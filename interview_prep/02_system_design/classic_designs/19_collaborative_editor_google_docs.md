# Collaborative Document Editor (Google Docs / Confluence)

> Appears at: Google (the canonical Docs/Realtime team question), Atlassian (Confluence — VERY relevant; their entire collaborative-editing platform is built on this, so expect a deep, pointed version of it here), Amazon L6. The interesting part is NOT the CRUD — it is the concurrency algorithm (OT vs CRDT). If you can explain why two concurrent edits at the same position converge, you have passed the hard part. Spend your depth budget there.

## 1. Requirements

**Functional:**
- Multiple users edit the same document simultaneously; everyone sees a consistent final state.
- Edits propagate in near-real-time (< 200ms perceived).
- Show presence (who is in the doc) and live cursors / selections per user.
- Version history — view and restore previous versions.
- Offline editing — edit while disconnected, reconcile on reconnect.
- Rich text (bold, headings, lists). We model the document as a sequence of characters with formatting; the concurrency problem is identical for plain text, so reason in plain text.

**Non-functional:**
- **Convergence (the core invariant):** given the same set of operations applied in any order, every replica reaches the *same* final document. This is the whole problem.
- **Intention preservation:** if I type "X" between "a" and "b", it stays between "a" and "b" even after a concurrent insert shifts positions.
- Low latency for the local editor — typing must feel instant (optimistic local apply).
- Availability over strong consistency — you keep typing even if the server is briefly slow.
- Scale: ~100 concurrent editors on a single hot doc (Confluence wiki page, big design doc); millions of docs total.

**Clarifying questions to ask:**
1. "How many concurrent editors per document?" → Design for ~50-100. This bounds the per-doc fan-out and lets one server own one doc.
2. "Do we need true offline + later merge, or just brief disconnects?" → Both; offline is the hard case and CRDTs shine there.
3. "Rich text or plain text?" → Model as plain text + formatting attributes; the transform logic is the same.
4. "Is server-authoritative ordering acceptable (Google Docs model) or fully peer-to-peer (no central server)?" → Server-authoritative — simpler, and what Docs/Confluence actually do.

## 2. Back-of-Envelope Estimation

```
Active docs concurrently edited:   1M docs with >=1 active editor
Editors per hot doc (peak):        100
Keystrokes per active user:        ~3 ops/sec while actively typing (debounced/batched)

Ops/sec on one hot doc:            100 editors * 3 ops/sec        = 300 ops/sec
Broadcast amplification:           each op fanned out to 100 peers
   => egress on one doc:           300 * 100                      = 30,000 msg/sec  (one server handles this fine)

Op size on the wire:               ~60 bytes (type, pos, char, rev, clientId)
Op log growth (busy doc, 1 day):   300 ops/sec * 8h editing ~= 8.6M ops/day
   raw op log:                     8.6M * 60B                     ~= 520 MB/day/doc  (=> must snapshot + compact)

Document snapshot size:            avg doc 50 KB; large doc up to 5 MB
Snapshot every:                    N ops (e.g. 1000) OR every 30s of quiescence

WebSocket connections (platform):  10M concurrent users / ~50k conns per edit server
   => edit servers:                ~200 servers (plus headroom)
```

Takeaway you should say out loud: **the op log grows without bound, so snapshotting + compaction is mandatory, not optional**, and **one document is small enough that a single server can own it** — that fact drives the whole routing design.

## 3. API Design

WebSocket for the live edit channel; plain REST for doc lifecycle. (Connection management mirrors the chat design — see [09_chat_messaging_whatsapp.md](./09_chat_messaging_whatsapp.md).)

```
# --- Lifecycle (REST) ---
POST   /api/v1/docs                       -> 201 { doc_id, title }
GET    /api/v1/docs/{doc_id}              -> { doc_id, snapshot, base_revision }   # bootstrap state
GET    /api/v1/docs/{doc_id}/history      -> [ { version, author, ts }, ... ]
POST   /api/v1/docs/{doc_id}/restore      Body: { version }  -> 200

# --- Realtime edit channel (WebSocket) ---
WS     /api/v1/docs/{doc_id}/connect
   <-  { type: "init", snapshot, base_revision }     # server sends on join

   ->  { type: "op",  client_id, base_rev: 42, op: { kind:"insert", pos:5, ch:"X" } }
   <-  { type: "ack", client_id, server_rev: 43 }    # this client's op committed
   <-  { type: "op",  origin_client, server_rev: 43, op: {...transformed...} }  # others' ops

   ->  { type: "cursor", client_id, pos: 12, sel_end: 18 }     # presence / live cursor
   <-  { type: "presence", users: [ {client_id, name, color, pos} ... ] }
```

Two contracts matter here: every op carries the **revision it was created against** (`base_rev`) so the server knows what to transform it past, and the server replies with a monotonically increasing **`server_rev`** that defines the single source-of-truth ordering.

## 4. High-Level Architecture

```
   Client A          Client B          Client C        (all editing doc 7)
      │  WS              │  WS             │  WS
      └────────┬─────────┴────────┬────────┘
               ▼                  ▼
        ┌──────────────────────────────┐
        │   Gateway / Load Balancer     │  routes by doc_id (sticky)  ──► see §7
        └───────────────┬──────────────┘
                        │  all editors of doc 7 land on the SAME server
                        ▼
        ┌──────────────────────────────┐
        │  Edit Server  (owns doc 7)    │
        │  ┌────────────────────────┐   │
        │  │ Document Session (7)    │   │  in-memory authority for this doc:
        │  │  - current revision     │   │   • serializes all incoming ops
        │  │  - tail of op log       │   │   • transforms (OT) / merges (CRDT)
        │  │  - connected clients    │   │   • assigns server_rev, broadcasts
        │  │  - presence/cursors     │   │
        │  └───────────┬────────────┘   │
        └──────────────┼────────────────┘
                       │ append ops (async, batched)
          ┌────────────┼───────────────────────┐
          ▼            ▼                         ▼
   ┌────────────┐ ┌──────────────┐      ┌──────────────────┐
   │ Op Log     │ │ Snapshot     │      │ Pub/Sub (Kafka /  │
   │ (append-   │ │ Store        │      │ Redis) — for      │
   │  only DB)  │ │ (S3 / blob)  │      │ cross-server +    │
   └────────────┘ └──────────────┘      │ failover handoff  │
                                        └──────────────────┘

Flow of one keystroke (client-side prediction + server authority):
  1. User types "X". Client applies it LOCALLY immediately (optimistic) — editor feels instant.
  2. Client sends op{insert, pos, base_rev} over WS; marks it "in flight".
  3. Edit Server's Document Session receives it. It TRANSFORMS the op against any ops
     committed since base_rev (ops the client hadn't seen yet), assigns server_rev, appends to log.
  4. Server ACKs the origin client (it can now discard the in-flight op) and BROADCASTS the
     transformed op to all other clients.
  5. Each other client TRANSFORMS the incoming op against its own in-flight ops, then applies it.
     => all clients converge to identical state.
```

## 5. Data Model

The document is never the source of truth at rest — the **ordered op log** is. A snapshot is just a cached fold of the log up to some revision.

```sql
-- Op log: append-only, the source of truth. Sharded by doc_id.
CREATE TABLE operations (
  doc_id        UUID        NOT NULL,
  server_rev    BIGINT      NOT NULL,        -- monotonic per doc; defines THE order
  client_id     UUID        NOT NULL,
  base_rev      BIGINT      NOT NULL,        -- revision the op was authored against
  op            JSONB       NOT NULL,        -- {kind:"insert"|"delete", pos, ch|len}
  author        UUID        NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (doc_id, server_rev)           -- clustered: read a doc's ops in order, fast
);

-- Snapshots: periodic materialized state for fast bootstrap + log compaction.
CREATE TABLE snapshots (
  doc_id        UUID        NOT NULL,
  at_rev        BIGINT      NOT NULL,        -- snapshot reflects log up to (and including) this rev
  blob_url      TEXT        NOT NULL,        -- content in S3/blob store (can be large)
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (doc_id, at_rev)
);

-- Doc metadata.
CREATE TABLE documents (
  doc_id        UUID PRIMARY KEY,
  title         TEXT,
  latest_rev    BIGINT,
  owner         UUID,
  updated_at    TIMESTAMPTZ
);
```

**Shard key: `doc_id`.** This is the most important schema decision. All ops for one doc live on one shard, are ordered by `server_rev`, and — critically — one edit server owns one `doc_id` at a time (§7). A doc is self-contained: you never need a cross-doc transaction.

For a CRDT design the row stores the CRDT operation (with its position identifier) instead of an integer `pos`; the rest is identical.

## 6. Deep Dives

### 6a. Concurrent editing: Operational Transformation (OT) vs CRDTs

This is the heart of the design. **The core problem:** two users edit the same position concurrently, against the same base state, and we must converge to one identical result on every replica — without a lock, because locking would make typing feel laggy.

**Concrete conflict.** Document is `"abc"` (revision 0). Concurrently:
- User A inserts `"X"` at position 1 → A's local state: `"aXbc"`.
- User B inserts `"Y"` at position 2 → B's local state: `"abYc"`.

Both send their op authored against `base_rev = 0`. If we naively apply the other person's op as-is, we diverge:

```
A receives B's op {insert "Y" at 2} and applies to "aXbc":  -> "aXYbc"   (Y landed after b... wrong)
B receives A's op {insert "X" at 1} and applies to "abYc":  -> "aXbYc"
   "aXYbc" != "aXbYc"   --> DIVERGENCE. Unacceptable.
```

The fix is to rewrite an incoming op so it accounts for changes it didn't see.

**Operational Transformation (OT) — what Google Docs uses.**
You define a `transform(op1, op2)` function: given two ops authored against the same state, return op1 adjusted to apply *after* op2. The classic insert/insert rule: if op2 inserted before (or at) op1's position, op1's position shifts right by op2's length.

```python
def transform_insert_insert(op1, op2):
    # op1 = (insert, pos1, ch1), op2 = (insert, pos2, ch2), both authored on same base
    if op2.pos < op1.pos or (op2.pos == op1.pos and op2.client_id < op1.client_id):
        # op2 lands at or before op1 -> op1 must shift right
        return Op("insert", op1.pos + len(op2.ch), op1.ch)
    return op1  # op2 is after op1 -> op1 unaffected

# Walk through the conflict above (tie broken consistently by position, then client_id):
#   A's view: transform A_op? no -> apply B_op transformed past A_op:
#       B_op was insert@2; A_op was insert@1 (before it) -> B_op shifts to @3 -> "aXbYc"
#   B's view: apply A_op transformed past B_op:
#       A_op insert@1; B_op insert@2 (after it) -> A_op unchanged @1 -> "aXbYc"
#   BOTH converge to "aXbYc".  Convergence achieved.
```

The server is the serialization point: it picks the canonical order (`server_rev`), transforms each arriving op against everything committed since the op's `base_rev`, and broadcasts the transformed op. Clients run the *same* transform against their in-flight ops.

- **OT pros:** compact ops (just integer positions), small memory, mature (Docs, Etherpad). The server's central ordering makes correctness tractable.
- **OT cons:** the transform function is notoriously hard to get right — you need a rule for every op-pair (ins/ins, ins/del, del/del) and they must satisfy the TP1/TP2 transform properties. Practically requires a central server to serialize; pure peer-to-peer OT is very hard.

**CRDTs (Conflict-free Replicated Data Types) — what many newer editors use (Figma-style, Yjs/Automerge, Apple Notes).**
Instead of transforming positions, give every inserted character a **globally unique, totally-ordered position identifier** that never changes. Then "merge" is just: union all characters and sort by identifier. There is no transform — convergence is structural.

```python
# Sequence CRDT (logoot/RGA-style). Each char gets a fractional/path position id
# that sorts BETWEEN its neighbors and is unique (tie-broken by site_id).
#
#   "abc" with positions:   a@[1]   b@[3]   c@[5]
#   A inserts X between a,b: pick id between [1] and [3] => X@[2, siteA]
#   B inserts Y between b,c: pick id between [3] and [5] => Y@[4, siteB]
#
#   Merge anywhere = sort all by position id:
#       a@[1], X@[2,A], b@[3], Y@[4,B], c@[5]  => "aXbYc"  on EVERY replica.
#
# If A and B both insert at the SAME gap, their ids differ by site_id => deterministic order, still converges.
def insert_between(left_id, right_id, site_id):
    new_id = midpoint(left_id, right_id)      # allocate an id strictly between
    return (new_id, site_id)                  # site_id breaks any tie deterministically
```

- **CRDT pros:** no central transform; merges commute and are idempotent, so they work **peer-to-peer and offline** beautifully — replay ops in any order, still converge. Great fit for the offline requirement.
- **CRDT cons:** per-character metadata (each char carries a position id + tombstone for deletes) bloats memory/storage; deleted chars become tombstones you must garbage-collect; large docs get heavy. Interleaving anomalies exist for concurrent inserts in some CRDTs.

**What to say in the interview:** "Google Docs uses OT with a central server as the serialization authority — it's compact and battle-tested. Newer systems (Yjs, Automerge, Figma) lean CRDT because the merge is structural and handles offline/P2P without a fragile transform function. For a server-authoritative product like Docs or Confluence, I'd default to OT with the edit server as the ordering point; if strong offline support is a first-class requirement, I'd pick a CRDT and accept the metadata cost (mitigated by tombstone GC and snapshotting)." See also CRDT/conflict ideas in the eventually-consistent store [02_distributed_cache.md](./02_distributed_cache.md).

### 6b. Real-time sync transport: WebSockets, the per-doc session, presence & reconciliation

**Transport.** Each editor holds a persistent **WebSocket** to an edit server (long-lived, bidirectional, low overhead per message — exactly the connection-management model from the chat design, [09_chat_messaging_whatsapp.md](./09_chat_messaging_whatsapp.md): heartbeats, reconnect with backoff, a connection registry).

**Per-document session.** Each hot doc has one in-memory **Document Session** object on its owning server. It is single-threaded per doc (or guarded by a per-doc lock / actor), which is what lets it *serialize* ops: receive op → transform/merge → assign `server_rev` → append to log → ack origin → broadcast to the other connected clients. Serializing on one session is why a single server must own a doc.

**Client-side prediction + server authority** (the UX trick):
- The client applies its own edit **locally and immediately** so typing feels instant, and marks that op "in flight."
- It keeps in-flight ops until the server `ack`s them.
- When the server broadcasts someone else's op, the client transforms it against its still-in-flight ops before applying — so the local optimistic state and the authoritative stream reconcile to the same place.
- If the client's prediction was wrong (server transformed the op differently), the ack carries the canonical position; client rebases its in-flight ops on top. The server's ordering always wins — this is "optimistic local, authoritative server."

**Presence & live cursors.** Cursor position and selection are *ephemeral* — broadcast over the same WS but **not** written to the op log (no point persisting where someone's cursor was). When a peer inserts text before your cursor, you transform your cursor position the same way you transform ops, so cursors don't drift. Presence (avatars, colors) is a lightweight pub/sub keyed by `doc_id`, expired by heartbeat timeout.

### 6c. Persistence & history: op log vs snapshots, compaction, offline replay

**Op log vs snapshot — store both.** The op log is the source of truth and gives you exact, fine-grained history ("who typed what, when"), but replaying millions of ops to open a doc is too slow. So you periodically **snapshot**: fold the log into a materialized document blob at revision R, store it in S3, and on bootstrap send `snapshot(R) + ops(>R)`. Opening a doc = load latest snapshot + replay only the small tail.

**Compaction.** Once a snapshot at revision R is durable, ops `<= R` are no longer needed for *bootstrap* (keep them if you want full keystroke history; archive/cold-store them otherwise). For CRDTs, compaction also means **garbage-collecting tombstones** of deleted characters once all replicas have acknowledged past that point. Snapshot cadence: every N ops (e.g. 1000) or after a quiescence window (e.g. 30s idle).

**Version history & restore.** "Versions" are named snapshots (or revision markers). Restore = create a *new* op that transforms current state into the chosen historical state (you don't rewrite the log — you append the inverse, preserving the immutable history). This keeps the log append-only and auditable, which is exactly what Confluence's page history needs.

**Offline edits replay.** While offline, the client buffers its ops locally (authored against the last `base_rev` it saw). On reconnect it streams them up; the server transforms each against everything committed in the meantime and broadcasts. This is where **CRDTs are genuinely easier** — because merges commute, an offline client's ops merge correctly regardless of order, with no transform chain to maintain. With OT you must transform the whole offline batch past the server's intervening ops (correct but more code).

## 7. Bottlenecks, Failure Modes & Trade-offs

**Routing all editors of one doc to the same server (the key constraint).** Because the Document Session serializes ops in memory, every editor of `doc_id` must hit the *same* edit server. Options:
- **Consistent-hash `doc_id` → server** at the gateway. Simple, but rebalances on scale events.
- **Coordination service (ZooKeeper/etcd) assigns doc ownership**; gateway looks up the owner. Survives rebalancing cleanly and supports clean failover handoff.
- The LB must be **sticky by `doc_id`**, not by client — two different users on the same doc must converge to one server even though they're different connections.

**Large-doc / hot-doc scaling.**
- A 5 MB doc with 100 editors: the *session* memory and broadcast fan-out (~30k msg/s, §2) sit comfortably on one server — the bottleneck is op-log write throughput and snapshot size, not CPU. Batch op-log appends; snapshot incrementally.
- If a single doc somehow exceeds one server (rare — a giant Confluence space being edited by hundreds), you can partition *within* the doc (e.g. per-section/sub-tree sessions) but this is genuinely hard and you should flag it as out of normal scope. The honest answer is "one doc is bounded by design; we scale by having millions of docs across many servers, not by splitting one doc."
- **Storage:** the op log grows ~520 MB/day on a busy doc (§2) — compaction + cold archival of pre-snapshot ops is mandatory.

**Failure modes:**
- **Edit server crashes:** the in-memory session is lost, but the op log + latest snapshot are durable. A new owner is assigned (via etcd), it rebuilds the session from `snapshot + tail ops`, and clients reconnect (WS reconnect with backoff). Clients replay any unacked in-flight ops — idempotency via `(client_id, base_rev)` dedup prevents double-apply.
- **Network partition / client offline:** client keeps editing optimistically, buffers ops, reconciles on reconnect (§6c). Availability over consistency — exactly the right CAP choice for an editor.
- **Op log write lag:** acks can be sent on in-memory commit, then logged async — but then a crash before flush loses the last few ops. Trade-off: ack-after-durable (safe, ~1 round-trip slower) vs ack-on-memory (fast, tiny loss window). For a doc editor, ack-on-memory with fast async batched flush is usually the right call.

**Key trade-offs to name:**
- OT (compact, central, mature, fragile transform) vs CRDT (structural merge, offline/P2P friendly, metadata-heavy).
- Optimistic local apply (instant typing, occasional rebase) vs wait-for-server (consistent but laggy — never do this for typing).
- One-server-per-doc (simple serialization) vs distributed-per-doc (scales a giant doc but very complex).

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: concurrent editors per doc (~100), offline support (yes), rich vs plain
           (model as plain text), server-authoritative (yes, like Docs). State the core
           invariant out loud: convergence + intention preservation.
3-6 min:   Estimation: 300 ops/sec/doc, 30k msg/s fan-out (one server is fine), op log
           ~520MB/day => snapshotting is mandatory. ~200 edit servers for WS connections.
6-12 min:  Architecture: WS to edit server, per-doc Document Session as the serialization
           authority, op log + snapshot store + pub/sub. Walk ONE keystroke end to end:
           optimistic local apply -> send with base_rev -> server transforms/orders/acks/broadcasts.
12-16 min: Data model: op log is source of truth (PK doc_id, server_rev), snapshots cache the
           fold, shard key = doc_id, one doc is self-contained.
16-30 min: DEEP DIVE (spend the most time here): the convergence problem. Draw "abc",
           two concurrent inserts, show naive divergence, then OT transform converging to
           "aXbYc". Contrast CRDT position-ids converging structurally. State who uses what
           (Docs = OT, Yjs/Automerge/Figma = CRDT) and your default (OT + central server;
           CRDT if offline is first-class).
30-36 min: Transport deep dive: client prediction + server authority, in-flight op rebase,
           presence/cursors as ephemeral (not logged), reconnect (ref chat design).
36-40 min: Persistence: op log vs snapshot, compaction/tombstone GC, version history as
           named snapshots, offline replay (and why CRDTs make it easier).
40-44 min: Bottlenecks: sticky routing by doc_id (etcd ownership), large-doc scaling honesty,
           server-crash recovery from snapshot+log, idempotent replay.
44-45 min: Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — system design](https://www.hellointerview.com)
- [ByteByteGo — collaborative editor / Google Docs system design](https://www.youtube.com/results?search_query=bytebytego+google+docs+system+design)
- [NeetCode — collaborative document editing system design](https://www.youtube.com/results?search_query=neetcode+collaborative+editor+system+design)
- [Operational Transformation vs CRDT explained](https://www.youtube.com/results?search_query=operational+transformation+vs+crdt+explained)

**Paid (optional):**
- "System Design Interview – Volume 2" by Alex Xu — Chapter: Google Docs (collaborative editing).
- [Grokking the System Design Interview — DesignGurus](https://www.designgurus.io)

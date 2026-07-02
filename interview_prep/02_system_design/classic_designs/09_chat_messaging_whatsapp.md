# Chat / Messaging System (WhatsApp / Messenger)

> Appears at: Amazon L6, Atlassian, Uber, Google L5. The connection-management question is what separates this from every other design — anyone can draw a message DB, but only you know how a server finds user X's live socket. Spend your depth budget on 6a and 6b; the storage choice (6c) is the "I've seen scale" signal.

## 1. Requirements

**Functional:**
- 1:1 messaging — send a message, deliver to the recipient in real time
- Group messaging — N members, fan-out to all (cap group size, e.g. 256)
- Delivery status — sent → delivered → read receipts
- Presence — online / last-seen
- Offline delivery — store the message, deliver on reconnect, push notification
- Message ordering — messages in a conversation appear in a consistent order
- Media (images/video) — out of scope for the core path (upload to blob store, send a link); mention it

**Non-functional:**
- 50M DAU, ~40 msgs/user/day — read-heavy on fan-out, low write latency
- Message delivery < 500ms p99 for online users
- Durable — a sent-and-acked message is never lost
- Ordered per-conversation (NOT global ordering — that's impossible and unneeded)
- Highly available — favor availability over strong consistency (AP); a slightly stale read beats a failed send
- At-least-once delivery with client-side dedup (exactly-once across a network is a fantasy)

**Clarifying questions:**
1. "Group size cap?" → 256 members. This is the line between fan-out-on-write (small groups) and a different strategy; with a 256 cap, fan-out-on-write is fine.
2. "Do we need end-to-end encryption?" → Treat it as a design constraint at the high level (server stores ciphertext, can't read content), but don't derive the Signal protocol — flag it and move on.
3. "Multi-device per user?" → Yes, assume up to ~4 devices. Each device is its own delivery target; messages fan out per-device, not per-user.

## 2. Back-of-Envelope Estimation

```
Users:                50M DAU
Messages/user/day:    40
Total messages/day:   50M × 40 = 2B messages/day
Avg send QPS:         2B / 86,400 ≈ 23,000 msgs/sec
Peak QPS (3x):        ~70,000 msgs/sec

Fan-out amplification: group msgs hit ~N recipients. Assume avg 5 recipients
                       per message (mix of 1:1 and groups).
Delivery QPS (peak):   70K × 5 ≈ 350,000 deliveries/sec

Connections (the real constraint — not QPS, but CONCURRENT sockets):
  50M DAU, assume 10M concurrent at peak (devices online)
  One box holds ~65K sockets comfortably (file-descriptor + memory bound)
  10M / 65K ≈ 155 connection servers (round up to ~250 for headroom + HA)

Message size:         ~200 bytes (text) + 100B metadata ≈ 300 bytes
Storage/day:          2B × 300B = 600 GB/day
Storage/year:         ~220 TB/year → wide-column store, not one RDBMS
Retention:            keep 1 year hot, archive older to cold storage (S3)

Presence writes:      each online user heartbeats every ~30s
                      10M concurrent / 30s ≈ 330K presence writes/sec → Redis, TTL-based
```

The headline: this is a **concurrent-connection** problem, not a QPS problem. 10M live sockets is the thing that breaks naive designs.

## 3. API Design

The transport is a **persistent WebSocket**, not REST request/response. REST is only for the side channels (history, group admin).

```
# Establish connection (WebSocket upgrade)
GET /ws  → 101 Switching Protocols
  Header: Authorization: Bearer <token>
  → server authenticates, registers (user_id, device_id) → this connection server in the session store

# Send a message (over the open WebSocket, framed as JSON)
→ { type: "SEND", client_msg_id: "uuid", conversation_id: "c123",
    content: "<ciphertext>", ts: 1718960000 }
← { type: "ACK", client_msg_id: "uuid", server_msg_id: 998877, seq: 42 }   # server assigns seq

# Receiving a message (server → client, pushed)
← { type: "MESSAGE", conversation_id: "c123", server_msg_id: 998877,
    seq: 42, sender_id: "u456", content: "<ciphertext>", ts: ... }

# Delivery / read receipts (client → server, over WS)
→ { type: "DELIVERED", server_msg_id: 998877 }
→ { type: "READ", conversation_id: "c123", up_to_seq: 42 }   # read up to a seq, not per-message

# REST side channels:
GET  /api/v1/conversations/{cid}/messages?before_seq=100&limit=50   # history / pagination
POST /api/v1/groups                  # create group
POST /api/v1/groups/{gid}/members    # add member
GET  /api/v1/presence?user_ids=...   # batch presence lookup
```

Receipts are sent **up_to_seq**, not per-message — one READ for "I've read through seq 42" collapses 42 acks into one.

## 4. High-Level Architecture

```
 Phone (WebSocket)                          Phone (WebSocket)
   │  persistent conn                           ▲  persistent conn
   ▼                                            │
┌─────────────┐                          ┌─────────────┐
│ Conn Server │  ... (250 of them) ...   │ Conn Server │
│   A (WS)    │                          │   B (WS)    │
└──────┬──────┘                          └──────▲──────┘
       │ 1. SEND                                │ 5. push MESSAGE
       ▼                                        │
┌────────────────────────────────────────────────────────┐
│              Message / Chat Service                      │
│  - assigns per-conversation seq (via Seq Generator)      │
│  - persists to message store                             │
│  - looks up recipient's conn server in Session Store     │
│  - routes the message to that conn server                │
└───┬──────────────┬───────────────┬──────────────┬───────┘
    │              │               │              │
    ▼              ▼               ▼              ▼
┌────────┐   ┌──────────┐   ┌────────────┐  ┌──────────────┐
│Session │   │ Message  │   │  Kafka /   │  │ Notification │
│Store   │   │ Store    │   │ msg queue  │  │  Service     │
│(Redis) │   │(Cassandra│   │(per-recip  │  │ (APNs/FCM    │
│ user→  │   │ wide col)│   │  inbox for │  │  push if     │
│ conn   │   │          │   │  offline)  │  │  offline)    │
│ server │   │          │   │            │  │              │
└────────┘   └──────────┘   └────────────┘  └──────────────┘
       │
       ▼
┌────────────┐
│ Presence    │  (Redis: user→last_heartbeat, TTL 60s)
│ Service     │
└────────────┘
```

**Request flow (1:1, recipient online):**
1. Alice sends `SEND` over her WebSocket to Conn Server A.
2. A forwards to the Message Service. Message Service asks the **Seq Generator** for the next `seq` in conversation `c123`, **persists** the message to Cassandra, and ACKs back to A → Alice's client marks "sent".
3. Message Service looks up Bob's `(user_id, device_id)` in the **Session Store** (Redis) → "Bob's device is on Conn Server B".
4. Message Service routes the message to Conn Server B (direct RPC or via a routing topic).
5. B pushes `MESSAGE` down Bob's WebSocket. Bob's client sends `DELIVERED` back → propagates to Alice ("delivered" tick).

**Recipient offline:** Step 3 finds no session in Redis → write the message to Bob's **per-recipient inbox** (a durable queue / Cassandra inbox partition) and fire a **push notification** via the Notification Service (APNs/FCM). On Bob's reconnect, his Conn Server drains the inbox in seq order.

## 5. Data Model

The message store is a **wide-column store (Cassandra/HBase)**, partitioned by `conversation_id`, clustered by `seq`. This is the single most important schema decision — it makes "fetch a conversation's messages in order" a single-partition sequential read.

```sql
-- MESSAGES (Cassandra). Partition key = conversation_id, clustering key = seq DESC.
-- All messages for one conversation live on one partition, sorted → cheap range scans.
CREATE TABLE messages (
  conversation_id   text,          -- PARTITION KEY (shard key)
  seq               bigint,        -- CLUSTERING KEY (per-conversation monotonic)
  server_msg_id     bigint,
  sender_id         text,
  content           blob,          -- ciphertext; server can't read it (E2EE)
  created_at        timestamp,
  PRIMARY KEY ((conversation_id), seq)
) WITH CLUSTERING ORDER BY (seq DESC);

-- PER-RECIPIENT INBOX for offline delivery (Cassandra). Partition = user_id+device.
-- Drained on reconnect; rows deleted (or TTL'd) once delivered+acked.
CREATE TABLE inbox (
  device_id     text,            -- PARTITION KEY  (user's device)
  msg_seq       bigint,
  conversation_id text,
  server_msg_id bigint,
  PRIMARY KEY ((device_id), msg_seq)
) WITH CLUSTERING ORDER BY (msg_seq ASC);

-- READ POSITION per (user, conversation): collapses per-message receipts.
CREATE TABLE read_cursors (
  conversation_id text,
  user_id         text,
  last_read_seq   bigint,
  PRIMARY KEY ((conversation_id), user_id)
);
```

```
# SESSION STORE (Redis) — the routing table. Where is user X's live socket?
HSET  session:{user_id}  {device_id}  "conn-server-B:9300"   # set on connect
HDEL  session:{user_id}  {device_id}                          # on disconnect
# TTL'd / heartbeat-refreshed so a crashed conn server's entries expire.

# PRESENCE (Redis)
SET   presence:{user_id}  "online"  EX 60     # refreshed by heartbeat; expiry → offline

# GROUP MEMBERSHIP (Postgres or Cassandra — read-heavy, rarely changes)
group_members(group_id, user_id, role, joined_at)   PK (group_id, user_id)
```

**Why partition by `conversation_id`, not `user_id`?** A conversation's messages must be ordered and co-located; reading a chat = one partition scan. Partitioning by user would scatter a conversation's messages across the sender's and recipient's partitions, breaking ordering and doubling writes. Hot-partition risk (a giant group) is real — mitigation in §7.

## 6. Deep Dives

### 6a. Connection Management — the service-discovery problem

**WebSocket vs long-polling.** Long-polling (client repeatedly asks "anything new?") works and is the fallback when WebSockets are blocked by a proxy, but it burns a request per poll and adds latency (you're offline between polls). **WebSocket** is the answer: one TCP connection, upgraded via HTTP `101`, stays open, and the server can push at any time. Bi-directional, low overhead per message after the handshake.

**Persistent connection servers.** A fleet of stateful "connection servers" each hold ~65K open sockets. They are stateful (unlike the URL shortener's stateless API tier), which changes everything — you can't just round-robin a load balancer and forget about it. The LB must do **sticky** routing, and on reconnect a user may land on a *different* conn server.

**The core problem: where is user X's socket?** When Alice sends to Bob, the Message Service must find which of 250 conn servers currently holds Bob's live socket. This is service discovery for ephemeral sessions:

```python
# On connect: register the session
def on_connect(user_id, device_id, this_server_addr):
    redis.hset(f"session:{user_id}", device_id, this_server_addr)
    redis.expire(f"session:{user_id}", 60)   # heartbeat refreshes this

# On message route: look up the recipient's conn server
def route(recipient_id, message):
    sessions = redis.hgetall(f"session:{recipient_id}")  # {device: server_addr}
    if not sessions:
        enqueue_inbox(recipient_id, message)   # offline → store + push
        send_push_notification(recipient_id, message)
        return
    for device_id, server_addr in sessions.items():
        rpc_push(server_addr, recipient_id, device_id, message)  # forward to that conn server
```

Two routing styles you should name:
- **Session store + direct RPC (above):** Redis holds `user → conn server`; Message Service does an RPC straight to that box. Lowest latency. The session store is the single source of truth for routing.
- **Pub/sub fan-out:** each conn server subscribes to a topic; Message Service publishes `route:{user_id}` to Kafka/Redis pub-sub and the owning server picks it up. Decouples sender from recipient's server location but adds a hop. WhatsApp-scale systems lean on the session-store approach for latency.

**Heartbeats.** The client pings every ~30s; the conn server refreshes the session/presence TTL. If a heartbeat is missed, the socket is assumed dead — the entry expires, presence flips to offline, and the user must reconnect. This is how you detect half-open TCP connections (the client vanished but the OS never sent a FIN). When a **conn server crashes**, all its session entries simply TTL-expire within 60s; clients reconnect (with backoff + jitter to avoid a thundering herd) and re-register on a new server.

### 6b. Message Delivery & Ordering

**Send path (durability first).** The message is **persisted before ACK** — the client only sees "sent" once Cassandra has it. This guarantees at-least-once: even if delivery to the recipient fails, the message is recoverable from the store and the inbox. The client supplies a `client_msg_id` (UUID) so retries are **idempotent** — the server dedups on it.

**Ordering — per-conversation sequence numbers.** You do NOT need global ordering (impossible at scale, and meaningless across unrelated chats). You need: within one conversation, everyone sees the same order. Achieve it with a **monotonic `seq` per `conversation_id`**, assigned by a single authority for that conversation:

```python
# Seq is assigned server-side, atomically, per conversation.
def assign_seq(conversation_id):
    return redis.incr(f"seq:{conversation_id}")   # atomic; or a sharded counter

# Clients sort by seq, not by wall-clock ts — clocks are unreliable and skewed.
# Late/out-of-order arrivals are reordered client-side using seq + a small buffer.
```

Server-assigned `seq` (not client timestamps) is the whole trick — clocks drift, but a single INCR per conversation gives a total order everyone agrees on. To avoid Redis being a per-conversation bottleneck, shard the counter or co-locate seq assignment with the conversation's partition.

**1:1 vs group fan-out.** For 1:1, route to one recipient. For groups (≤256), **fan-out-on-write**: on send, look up group membership, and for each member route to their conn server (online) or inbox (offline). With a 256 cap this is fine — at most 256 routing operations per group message. (For *huge* fan-out — millions of followers — you'd flip to fan-out-on-read, but that's the news-feed/Twitter problem, not chat. Name the trade-off, don't over-build it.)

**Delivery & read receipts.** Three states tracked client-to-client:
- **sent** — server persisted + ACKed (one tick).
- **delivered** — recipient's device received it and sent `DELIVERED` back (two ticks). Propagated to the sender.
- **read** — recipient opened the chat; client sends `READ up_to_seq=N`. Collapses many messages into one cursor update (the `read_cursors` table). Sender sees blue ticks.

**Offline users → store + push.** If the recipient has no session in Redis, the message goes to their durable **per-recipient inbox** (Cassandra partition keyed by device). A **push notification** is fired via the Notification Service → APNs (iOS) / FCM (Android). On reconnect, the conn server drains the inbox in `seq` order and the device acks each, after which inbox rows are deleted/TTL'd. (See the notification-system design for retry/dedup/provider-fanout details — reference it rather than re-deriving.)

### 6c. Message Storage — why a wide-column store, not one RDBMS

At 2B messages/day → ~220 TB/year, a single Postgres instance is a non-starter: you can't fit it, and the write rate (70K+/sec) saturates one primary. The access pattern is also peculiar — **write once, read a contiguous range** (the last N messages of a conversation, or paginate backward). That is exactly what a **wide-column store (Cassandra / HBase)** is built for:

- **Partition by `conversation_id`, cluster by `seq`** → all of a conversation's messages on one node's partition, physically sorted. "Load the last 50 messages" = one sequential partition read, no cross-node scatter-gather.
- **Write-optimized (LSM-tree):** Cassandra appends to a commit log + memtable, flushes to immutable SSTables. Sequential writes absorb the 70K/sec firehose far better than a B-tree RDBMS doing random page writes.
- **Horizontal scaling + tunable consistency:** add nodes to grow; pick `QUORUM` writes/reads for safety or `ONE` for latency. This is the **AP** posture — you accept that a read might momentarily miss the newest message rather than fail.
- **TTL & retention:** set a TTL on inbox rows (auto-delete after delivery) and on cold messages; archive >1-year messages to S3, keep 1 year hot.

**Why not one RDBMS:** no horizontal write scaling (single primary), random-write penalty under this load, and sharding Postgres by hand re-implements what Cassandra gives you for free. You *can* keep Postgres for low-volume relational data — users, group membership, billing — where joins and transactions matter and volume is small.

**Presence / last-seen** (cross-cutting): purely Redis with TTL. `SET presence:{uid} online EX 60`, refreshed by heartbeat; key expiry = offline; `last_seen` is a separate `SET presence:{uid}:last <ts>` written on disconnect/heartbeat. Don't persist presence to the message store — it's high-churn, low-value, fine to lose.

**End-to-end encryption** (high level): the server stores `content` as **ciphertext** and never holds plaintext or keys. Key exchange happens client-to-client (Signal-style double ratchet); the server is a dumb relay + key-bundle directory. Consequence for *this* design: the server **cannot** do server-side search, content moderation on plaintext, or smart notifications based on content — flag these trade-offs, don't implement the crypto.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x (500M DAU, 100M concurrent connections):**
- Conn servers: 100M / 65K ≈ 1,500+ boxes. The session store (Redis) now has 100M+ keys with constant churn → **Redis Cluster**, sharded by `user_id`. Heartbeat write rate (~3M/sec) becomes its own scaling problem — batch heartbeats, raise the interval.
- **Hot partition:** a 256-member very-active group hammers one Cassandra partition and one seq counter. Mitigations: cap group size; shard a hot conversation's partition by `(conversation_id, time_bucket)` so a month's messages spread across partitions; shard the seq counter.
- Fan-out: a flurry of group messages multiplies delivery QPS. Back-pressure via the per-recipient queue (Kafka) so a slow recipient can't stall the sender — see [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md).

**CAP / consistency choice:** This is an **AP** system. You favor availability — a send must succeed and be durable even during a partition; recipients converge slightly later. You do NOT need linearizable global ordering; per-conversation `seq` is the consistency boundary, and at-least-once + client dedup covers the rest. Strong consistency would cost you the latency and availability that messaging users actually care about.

**Failure modes & recovery:**
- **Conn server crash:** its sockets drop; session entries TTL-expire in ≤60s; clients reconnect (exponential backoff + jitter to avoid a reconnect storm) and re-register elsewhere. In-flight messages were already persisted before ACK, so nothing is lost — undelivered ones sit in the inbox.
- **Session store (Redis) down:** routing breaks → fall back to treating everyone as offline (write to inbox + push). Degraded (no real-time), but no data loss. Mitigation: Redis Cluster + replicas.
- **Message store node down:** Cassandra replication factor 3 + QUORUM → survives one node loss with no data loss and no downtime.
- **Notification provider (APNs/FCM) down:** offline users miss the push but the message is safe in the inbox and delivered on reconnect. Retry with backoff.
- **Duplicate delivery:** at-least-once means dupes happen (retry after a lost ACK). Client dedups on `server_msg_id` / `client_msg_id`. Never promise exactly-once over a network.

**Rate limiting** (spam / abuse): cap messages/sec per user at the conn server edge — see [01_rate_limiter.md](./01_rate_limiter.md).

## 8. Talk Track (40 min budget)

```
0-3 min:   Clarify: group size cap (256), E2EE (flag, don't derive), multi-device (yes, per-device targets),
           delivery semantics (at-least-once + client dedup).
3-6 min:   Estimation. Land the key insight FAST: this is a CONCURRENT-CONNECTION problem
           (10M live sockets → ~250 conn servers), not a QPS problem.
6-11 min:  Architecture. Draw conn servers (stateful!) + Message Service + Session Store + Cassandra
           + Notification. Walk the 1:1 online send path end-to-end.
11-20 min: DEEP DIVE 6a — connection management. WebSocket over long-poll. The service-discovery
           problem: how does the server find user X's socket? → Redis session store + RPC routing.
           Heartbeats, TTL expiry, crash recovery, reconnect storms.
20-28 min: DEEP DIVE 6b — delivery & ordering. Persist-before-ACK (durability). Per-conversation
           server-assigned seq for ordering (NOT clocks, NOT global order). 1:1 vs group fan-out-on-write.
           Offline → inbox + push. sent/delivered/read receipts (read = up_to_seq cursor).
28-34 min: DEEP DIVE 6c — storage. Wide-column (Cassandra), partition by conversation_id / cluster by seq,
           why not one RDBMS. Presence via Redis TTL. E2EE high level (server relays ciphertext).
34-38 min: Bottlenecks: hot partitions, AP/CAP choice, conn-server crash recovery, Redis Cluster at 10x.
38-40 min: Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — chat / WhatsApp system design](https://www.hellointerview.com)
- [ByteByteGo — design a chat system](https://www.youtube.com/results?search_query=bytebytego+design+a+chat+system)
- [NeetCode — WhatsApp / messaging system design](https://www.youtube.com/results?search_query=neetcode+whatsapp+messaging+system+design)

**Paid (optional):**
- "System Design Interview" by Alex Xu (Vol. 1) — Chapter 12: Design a Chat System
- [Grokking the System Design Interview](http
s://www.designgurus.io) — "Designing Facebook Messenger / WhatsApp"

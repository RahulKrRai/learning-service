# File Storage & Sync (Dropbox / Google Drive)

> Appears at: Google L5, Amazon L6, Atlassian (collaboration/Confluence-attachments angle). A meaty design — the interviewer wants to see content-addressable dedup, a sync protocol, and conflict resolution. Budget ~40 min and go deep on chunking + sync; that's where the signal is. Don't get lost designing the object store from scratch — reference it and move on.

## 1. Requirements

**Functional:**
- Upload a file from any device; it syncs to all the user's other devices.
- Download / open a file on any device.
- Edit a file locally while offline → changes sync when back online.
- Share a file or folder with another user (read or read-write).
- Version history (restore a previous version of a file).
- Keep bandwidth small: re-uploading a 1GB file after a 1-byte edit should NOT re-send 1GB.

**Non-functional:**
- Durability is sacred — a synced file must never be lost (11 nines, S3-class).
- Sync should feel near-real-time (a change on laptop appears on phone in seconds).
- Read:write heavily skewed to reads (downloads, opens) but writes are large (whole files).
- Scale: 500M users, ~100M daily active, files from a few KB to multi-GB.
- Consistency: read-your-writes on the same device; eventual across devices is fine.

**Clarifying questions:**
1. "Max file size?" → Support multi-GB; this forces chunking + resumable upload.
2. "Do we sync whole folders or selective?" → Selective sync (user picks which folders); affects metadata, not core design.
3. "Real-time collaborative editing (Google Docs style)?" → Out of scope. We sync *files as blobs*; we are not doing operational transforms on document contents. (Mention this — it scopes the problem hard.)
4. "Strong vs eventual consistency across devices?" → Eventual, with deterministic conflict resolution.

## 2. Back-of-Envelope Estimation

```
Users:                500M total, 100M DAU
Files per user:       ~200 avg               → 100B files total
Avg file size:        ~500 KB (long tail of large files)
Total logical bytes:  100B × 500KB ≈ 50 PB (before dedup)

Dedup savings: studies of consumer file storage show 30-50% of bytes are
duplicates (shared docs, OS files, re-saved copies). Assume 40%:
  Physical bytes after dedup ≈ 50 PB × 0.6 = 30 PB

Daily writes:         100M DAU × 5 file changes/day = 500M changes/day
                      = ~5,800 writes/sec avg, ~20,000/sec peak
With delta sync, each change uploads ~1 chunk (4MB) not the whole file:
  Upload bytes/day ≈ 500M × 4MB = 2 PB/day ingress  (vs ~25 PB without delta)

Metadata:
  per file: file_id, name, parent, version, chunk_list, size, mtime ≈ 1 KB
  100B files × 1KB = 100 TB metadata → must be sharded (Postgres/Spanner-style)

Notification fan-out:
  100M DAU each with ~3 devices long-polling = 300M open connections
  → notification servers must hold cheap idle connections (epoll), shard by user_id
```

The headline: **delta sync turns 25 PB/day of naive upload into ~2 PB/day, and dedup turns 50 PB stored into 30 PB.** Lead with this number.

## 3. API Design

```
# --- Block (chunk) store API ---
# Upload one content-addressed chunk. Idempotent: if hash exists, server skips the body.
PUT /api/v1/blocks/{sha256}
Body: <raw chunk bytes, up to 4MB>
→ 200 { stored: false }   # already existed (dedup hit — client didn't even need to send)
→ 201 { stored: true }    # newly stored

# Ask the server which chunks it already has BEFORE uploading (saves bandwidth)
POST /api/v1/blocks/check
Body: { hashes: ["sha256:aaa", "sha256:bbb", ...] }
→ 200 { missing: ["sha256:bbb"] }   # only upload these

# --- Metadata / commit API ---
# Commit a file as an ordered list of chunk hashes (the manifest)
POST /api/v1/files/commit
Body: { path: "/docs/report.pdf", chunks: ["sha256:aaa","sha256:bbb"],
        size: 8388608, base_version: 41 }   # base_version = version client edited from
→ 201 { file_id, version: 42 }
→ 409 Conflict { server_version: 43 }       # someone else committed first → resolve

# --- Sync / change detection ---
# Long-poll: "tell me what changed since cursor C" (server holds the request open)
GET /api/v1/changes?cursor={cursor}&timeout=30s
→ 200 { changes: [ {file_id, version, path, op:"upsert"} ... ], cursor: "new-cursor" }

# --- Download ---
GET /api/v1/files/{file_id}?version=42   → returns the manifest (chunk list)
GET /api/v1/blocks/{sha256}              → returns chunk bytes (served via CDN/presigned URL)

# --- Sharing ---
POST /api/v1/files/{file_id}/share
Body: { grantee_user_id, role: "viewer" | "editor" }
→ 201 { share_id }

# --- Resumable upload (large files) ---
POST /api/v1/uploads        → { upload_id }           # start a session
PUT  /api/v1/uploads/{id}/chunks/{index}              # upload each chunk; retry safe
POST /api/v1/uploads/{id}/complete                    # finalize → commit manifest
```

Note the two-phase pattern: **`check` → upload only missing blocks → `commit` manifest.** This is the heart of delta sync and is worth narrating.

## 4. High-Level Architecture

```
   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
   │ Laptop      │        │ Phone       │        │ Web browser │
   │ sync client │        │ sync client │        │             │
   └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
          │  chunk+hash locally  │                      │
          └──────────────┬───────┴──────────────────────┘
                         ▼
                ┌──────────────────┐
                │  Load Balancer   │
                └────────┬─────────┘
          ┌──────────────┼──────────────────┐
          ▼              ▼                   ▼
  ┌──────────────┐ ┌──────────────┐  ┌──────────────────┐
  │ Block Service│ │Metadata Svc  │  │ Notification Svc │
  │ (stateless)  │ │ (stateless)  │  │ (long-poll/push) │
  └──────┬───────┘ └──────┬───────┘  └────────┬─────────┘
         │                │                   │
         ▼                ▼                   │ pub/sub
  ┌──────────────┐ ┌──────────────┐    ┌──────────────┐
  │ Object Store │ │ Metadata DB  │───►│ Kafka / event│
  │ (S3-like)    │ │ (sharded SQL)│    │ bus          │
  │ chunks by    │ │ file tree,   │    └──────────────┘
  │ sha256       │ │ versions,    │
  │ + cold tier  │ │ chunk lists  │
  └──────────────┘ └──────────────┘
```

**Upload flow (delta sync):**
```
1. Client chunks the changed file, computes sha256 of each chunk.
2. POST /blocks/check with all hashes → server returns the `missing` set.
3. Client PUTs only the missing chunks to Block Service → Object Store.
4. Client POSTs /files/commit with base_version + ordered chunk list (the manifest).
5. Metadata Svc validates base_version (optimistic concurrency), writes new version row,
   emits a change event to Kafka.
6. Notification Svc, subscribed to the user's change stream, pushes/answers the
   long-poll of the user's OTHER devices → they pull the new manifest and any chunks
   they're missing.
```

The split is deliberate: **bytes flow through the Block Service / object store; tiny metadata flows through the Metadata Service.** They scale independently. (Same separation as a blob store fronted by a manifest DB.)

## 5. Data Model

```sql
-- Metadata DB (sharded relational — Postgres/Spanner/Vitess). Shard key: user_id
-- so all of one user's files + change feed live on one shard (single-user ops stay local).

CREATE TABLE files (
  file_id      UUID PRIMARY KEY,
  user_id      UUID NOT NULL,           -- shard key
  parent_id    UUID,                    -- folder tree (NULL = root)
  name         TEXT NOT NULL,
  is_dir       BOOLEAN NOT NULL,
  cur_version  BIGINT NOT NULL,         -- points at latest row in file_versions
  deleted      BOOLEAN DEFAULT FALSE,   -- soft delete (trash)
  updated_at   TIMESTAMPTZ
);
CREATE INDEX idx_files_parent ON files(user_id, parent_id);

CREATE TABLE file_versions (
  file_id      UUID NOT NULL,
  version      BIGINT NOT NULL,
  chunk_list   TEXT[] NOT NULL,         -- ordered sha256 hashes = the manifest
  size         BIGINT NOT NULL,
  device_id    UUID,                    -- who wrote it (for conflict UI)
  created_at   TIMESTAMPTZ,
  PRIMARY KEY (file_id, version)
);

-- Append-only change feed per user — drives the sync protocol (cursor = max seq seen)
CREATE TABLE changes (
  user_id      UUID NOT NULL,           -- shard key
  seq          BIGINT NOT NULL,         -- monotonic per user (cursor)
  file_id      UUID NOT NULL,
  version      BIGINT NOT NULL,
  op           TEXT,                    -- upsert | delete | move
  PRIMARY KEY (user_id, seq)
);

CREATE TABLE shares (
  file_id      UUID NOT NULL,
  grantee_id   UUID NOT NULL,
  role         TEXT NOT NULL,           -- viewer | editor
  PRIMARY KEY (file_id, grantee_id)
);
```

```
-- Block store (object storage, content-addressed). The KEY is the content hash,
-- which is WHY dedup is automatic: identical bytes → identical key → stored once.
   key:   blocks/{sha256}          value: <raw chunk bytes>
   ref-count (optional, in a KV store): blocks_refcount[sha256] = N
   -- GC: when refcount hits 0 AND no version references it, the chunk is collectable.
```

**Shard key choice:** `user_id` for metadata — keeps a user's file tree and change feed co-located, so listing a folder or computing "what changed for me" is a single-shard query. Blocks are sharded by `sha256` prefix across the object store, which spreads load evenly and is independent of users (shared chunks belong to no single user).

## 6. Deep Dives

### 6a. File Chunking + Content-Addressable Dedup

Split each file into chunks, hash each chunk with SHA-256, and treat the hash as the chunk's address. A file is then just an **ordered list of chunk hashes** (the manifest). Store each unique chunk exactly once.

```python
import hashlib

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB fixed-size chunks

def chunk_file(path):
    """Yield (sha256_hex, bytes) for each chunk."""
    manifest = []
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h = hashlib.sha256(chunk).hexdigest()
            manifest.append(h)
            yield h, chunk
    return manifest  # ordered list of hashes = the file's identity
```

**Delta sync** falls out for free: when a file changes, re-chunk it, and only the chunks whose hash changed need uploading. Edit page 2 of a 100MB PDF → only the 4MB chunk covering page 2 changes → upload 4MB, not 100MB. Client first calls `/blocks/check` so it skips chunks the server already has (from this user OR any user — global dedup).

**Fixed vs variable chunking — the nuance interviewers probe:**
- *Fixed-size* (above): simple. Problem — **insertion shifts everything.** Insert 1 byte at the start of a file and every subsequent chunk boundary shifts, so every chunk hash changes → you re-upload the whole file. Bad for delta sync on edited files.
- *Variable-size (content-defined chunking, CDC, e.g. Rabin fingerprint)*: pick boundaries based on content (cut where a rolling hash hits a pattern), not byte offset. Now inserting bytes only changes the one chunk around the insertion; boundaries downstream re-align. This is what real systems use for good delta sync. Mention it; you don't need to code Rabin live.

**Dedup math (say this out loud):**
```
Naive:  100B files × 500KB                       = 50 PB stored, 25 PB/day re-uploaded
With content-addressable dedup (~40% dup bytes)  = 30 PB stored
With delta sync (avg edit touches 1 of N chunks) = ~2 PB/day uploaded
→ ~12x less network than re-uploading whole files; ~40% less storage.
```

### 6b. Metadata Service + Sync Protocol + Conflict Resolution

The Metadata Service owns the file tree, versions, and the per-user **change feed** (the `changes` table — an append-only log with a monotonic `seq` per user). Sync is "replay the change feed from my cursor."

**Detecting remote changes — polling vs push:**
- *Naive polling:* every client asks "anything new?" every N seconds. Simple but either laggy (large N) or expensive (small N × 300M devices = a flood of empty responses).
- *Long-polling (recommended baseline):* client sends `GET /changes?cursor=C&timeout=30s`; the Notification Service **holds the connection open** until either a change for that user arrives (it's subscribed to the user's Kafka change stream) or the timeout fires. Near-real-time, but idle connections are cheap. Returns the new cursor; client advances and re-polls.
- *Server push (WebSocket):* lower latency still, persistent bidirectional. Heavier connection management. Many real clients use long-poll for change *signals* + a separate fast metadata pull.

```
Client A commits file F (version 42) ─► Metadata Svc writes changes(user, seq=901)
                                        and emits event to Kafka topic user.<id>
Notification Svc (holding A's other device's long-poll) sees seq 901
  ─► responds: { changes:[{F, v42}], cursor: 901 }
Device B pulls manifest for F v42, /blocks/check, downloads the 1 missing chunk. Done.
```

**Conflict resolution (two clients edit the same file offline):**
Both committed from `base_version = 41`. First commit wins → becomes version 42. The second client's commit also claims `base_version = 41`, but the server is now at 42:

```python
def commit(file_id, chunks, base_version, device_id):
    cur = db.get_current_version(file_id)
    if base_version == cur:                 # no conflict — fast path
        return db.append_version(file_id, chunks, base_version + 1)
    else:                                   # CONFLICT: someone committed since base
        # We do NOT silently overwrite and we do NOT merge file bytes.
        # Keep the winner; materialize the loser as a "conflicted copy".
        new_name = f"{name} (conflicted copy {device_id} {today})"
        return db.create_file(new_name, chunks)   # both versions survive; user decides
```

This is the Dropbox model: **last-writer-wins for the canonical file, but never lose data — the loser becomes a `conflicted copy`.** It's deterministic and simple. Contrast with Google Docs, which does operational transforms / CRDTs to *merge* concurrent edits — that's a different (out-of-scope) problem because it understands document structure; here we treat files as opaque blobs. Version history (the `file_versions` table) lets a user restore any prior version regardless.

### 6c. Storage Backend — Block Store on Object Storage

Chunks live in an S3-like object store keyed by `sha256`. Why object storage and not a DB: chunks are large, immutable, write-once-read-many blobs — exactly what object stores are built for, with built-in **durability via replication / erasure coding** (data split into k+m fragments across AZs; survives losing m fragments → ~11 nines durability). The Metadata DB stays small and fast because it only holds pointers, never bytes. (See [02_distributed_cache.md](02_distributed_cache.md) for the caching layer that fronts hot chunks.)

**Hot vs cold tiering:**
```
Hot  (standard tier):  recently accessed / actively synced chunks. CDN-fronted,
                       served via short-lived presigned URLs so bytes bypass our
                       servers entirely. Low latency.
Cold (archive tier):   chunks not touched in 90+ days (old versions, dormant files).
                       Cheaper $/GB, higher retrieval latency. A lifecycle policy
                       transitions objects hot→cold automatically.
```
Since chunks are content-addressed and immutable, tiering and caching are trivially safe — a hash always maps to the same bytes, so caches never go stale and there's no invalidation problem.

**Garbage collection:** dedup means a chunk may be referenced by many files/versions. Maintain a refcount (or run periodic mark-and-sweep over all manifests). Only delete a chunk when nothing references it. GC must be careful with the upload race: a chunk can be uploaded *before* its manifest commits, so don't collect "unreferenced" chunks younger than some grace window.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Large-file resumable upload:** A 5GB upload over flaky mobile must not restart from zero. Chunking already solves the mechanics: open an upload session (`upload_id`), PUT chunks by index, and each chunk PUT is **idempotent** (keyed by content hash, so a retried chunk is a no-op `200 {stored:false}`). On reconnect, the client calls `/blocks/check` to learn which chunks landed and resumes with the rest. `complete` commits the manifest. No partial-file corruption because the file only "exists" once its manifest is committed atomically.

**Sharing & permissions:** A share grants a `(file_id, grantee, role)` row. The tricky part is *folder* shares — granting a folder must apply to all descendants. Either (a) store the grant on the folder and resolve permissions by walking up the tree at access time (cheap writes, costlier reads), or (b) propagate grants down to children (costly on large trees, cheap reads). Real systems lean on (a) with caching. Access checks happen in the Metadata Service before returning any manifest; the object store itself only ever sees presigned, expiring URLs, so a leaked chunk hash isn't a capability.

**At 10x scale:**
- Metadata DB hot shards (a power user / shared team folder with millions of files): mitigate by sharding on `user_id` and treating huge shared folders as their own shard; cache folder listings.
- Notification fan-out (300M idle long-poll connections): horizontally scale Notification Svc, shard subscribers by `user_id`, use epoll-based servers that hold ~100k idle conns each.
- Object store write amplification from many tiny chunks: pack small files into a single chunk / coalesce; pick a chunk size (4MB) that balances dedup granularity vs object count.

**Failure modes:**
- *Block uploaded but commit fails:* orphan chunk → swept by GC after grace period. Safe (manifest is the source of truth).
- *Notification Svc down:* clients fall back to periodic polling — sync gets laggy, not broken. Graceful degradation.
- *Metadata DB shard down:* that user's writes fail (read-your-writes can't be guaranteed) but other shards unaffected; promote a replica.
- *Clock skew between devices:* never resolve conflicts by wall-clock time across devices — use the server's monotonic `version`/`seq`, not client timestamps.

**Key trade-offs to name:**
- Fixed chunks (simple, bad on inserts) vs content-defined chunks (complex, great delta sync).
- Long-poll (simple, near-real-time, fallback-friendly) vs WebSocket push (lowest latency, heavier ops).
- Last-writer-wins + conflicted copy (simple, never loses data, may annoy users) vs true merge/CRDT (great UX, only feasible when you understand the file format).
- Strong vs eventual cross-device consistency — we chose eventual + deterministic conflict handling for availability.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify. Max file size (multi-GB → chunking+resumable), selective sync,
           NO real-time co-editing (we sync blobs, not OT), eventual consistency OK.
3-6 min:   Estimation. 50PB logical, dedup→30PB, delta sync→2PB/day vs 25PB naive.
           Lead with the 12x bandwidth win — it motivates the whole design.
6-12 min:  Architecture. Draw the split: Block Service (bytes → object store) vs
           Metadata Service (pointers → sharded DB) vs Notification Service (sync).
           Walk the upload flow: chunk → check → upload missing → commit manifest.
12-22 min: DEEP DIVE 1 — chunking + content-addressable dedup. SHA-256 per chunk,
           file = ordered hash list, dedup is automatic from content addressing.
           Fixed vs content-defined chunking (the insertion problem). Dedup math.
22-32 min: DEEP DIVE 2 — sync protocol + conflict resolution. Per-user change feed +
           cursor. Polling vs long-poll vs push. base_version optimistic concurrency;
           last-writer-wins + conflicted copy; version history. Why not CRDT here.
32-38 min: DEEP DIVE 3 — storage backend. Object store, erasure-coded durability,
           hot/cold tiering, presigned URLs, GC of unreferenced chunks.
38-43 min: Bottlenecks — resumable large uploads (idempotent chunks), folder sharing
           permission model, notification fan-out at 300M connections, failure modes.
43-45 min: Questions.
```

Cross-references: change-feed delivery overlaps with [04_news_feed_fanout.md](04_news_feed_fanout.md); the event bus is the same primitive in [06_distributed_message_log_kafka.md](06_distributed_message_log_kafka.md); chunk caching builds on [02_distributed_cache.md](02_distributed_cache.md).

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — Dropbox / file storage design](https://www.hellointerview.com)
- [ByteByteGo — Design Dropbox / Google Drive](https://www.youtube.com/results?search_query=bytebytego+design+google+drive+dropbox)
- [NeetCode — Dropbox system design](https://www.youtube.com/results?search_query=neetcode+dropbox+system+design)

**Paid (optional):**
- "System Design Interview — Volume 2" by Alex Xu — Chapter: Design Google Drive
- [Grokking the System Design Interview (DesignGurus)](https://www.designgurus.io) — Designing Dropbox

# Object / Blob Store (Amazon S3)

> Appears at: **Amazon L6 (very relevant — this is the canonical S3-team question)**, Google L5. The "storage primitive" interview: the system that underpins half the other designs. If you can build this, you can build the storage layer for video streaming ([11_video_streaming_youtube.md](./11_video_streaming_youtube.md)) and file sync ([13_file_storage_dropbox.md](./13_file_storage_dropbox.md)). The signal interviewers want: do you understand durability math, the metadata/data split, and erasure coding? Spend your depth there.

## 1. Requirements

**Functional:**
- PUT an object (bytes + key) into a bucket → `PUT /bucket/key`
- GET an object by key → stream bytes back
- DELETE an object
- LIST objects in a bucket by prefix (pagination)
- Multipart upload for large objects (GB–TB range)
- Versioning (keep old versions of an overwritten key)
- Lifecycle / tiering (Standard → Infrequent Access → Glacier)

**Non-functional:**
- **Durability is the headline number: 11 nines (99.999999999%)** — lose at most 1 object per 100 billion per year.
- Availability: 99.99% (4 nines).
- Scale: exabytes of data, trillions of objects, flat keyspace.
- Read-after-write consistency for new objects (PUT then GET returns the new object).
- Throughput-oriented, not latency-oriented: first-byte latency ~10–100ms is fine; you optimize for GB/s aggregate.
- Object size: 1 byte up to 5 TB.

**Clarifying questions:**
1. "Mutable or immutable objects?" → Objects are **immutable**. An overwrite is a new version, not an in-place edit. This is the single most important simplifying assumption — it makes caching, replication, and consistency far easier.
2. "Strong or eventual consistency?" → Read-after-write for new keys; we'll discuss the overwrite/delete edge cases in the deep dive.
3. "Do we need a filesystem (directories, rename)?" → No. **Flat keyspace.** `photos/2026/a.jpg` is one key; the `/` is just a character. "Folders" are a UI illusion built from prefix listing.

## 2. Back-of-Envelope Estimation

```
Scale assumptions:
  Total stored:        100 PB usable (we'll size raw from this)
  Objects:             50 billion objects, avg 2 MB each
  Write throughput:    10 GB/s aggregate
  Read throughput:     50 GB/s aggregate (read-heavy, ~5:1)

Metadata sizing (the part people forget):
  Per-object metadata: key + bucket + size + version + location pointers + checksum
                       ≈ 1 KB per object
  Metadata total:      50B objects × 1 KB = 50 TB of METADATA alone
  → metadata does NOT fit on one node; it must be a sharded KV store.

Raw storage from durability scheme:
  Replication (3x):    100 PB usable × 3 = 300 PB raw  (200% overhead)
  Erasure code 10+4:   100 PB × (14/10) = 140 PB raw   (40% overhead)
  → erasure coding saves 160 PB of disk for the SAME durability. This is the
    money insight: at exabyte scale, 200% vs 40% overhead is billions of dollars.

Data nodes:
  Disk per node:       ~200 TB (HDD-dense storage server)
  Nodes for 140 PB:    140 PB / 200 TB ≈ 700 storage nodes (before headroom/AZ spread)

Durability intuition (11 nines):
  One disk AFR ≈ 2%/year. With 10+4 erasure coding you survive any 4 simultaneous
  losses out of 14. Probability all-5+ fail in the repair window is astronomically
  small → combined with fast background repair you reach ~10^-11 annual loss rate.
```

## 3. API Design

```
# Simple PUT (objects up to ~5 GB)
PUT /{bucket}/{key}
Headers: Content-Length, Content-MD5 (client checksum), x-amz-storage-class
Body: <raw bytes>
→ 200 { ETag: "<md5-or-multipart-hash>", VersionId: "v3" }

# GET (supports Range for partial / resumable reads)
GET /{bucket}/{key}
Headers: Range: bytes=0-1048575   (optional — fetch first 1 MB)
→ 200 <bytes>   |   206 Partial Content   |   404 NoSuchKey

DELETE /{bucket}/{key}          → 204 (with versioning: writes a delete marker)
GET    /{bucket}?prefix=photos/2026/&max-keys=1000&marker=...   (LIST, paginated)

# Multipart upload (the large-object protocol)
POST   /{bucket}/{key}?uploads                → 200 { UploadId }
PUT    /{bucket}/{key}?partNumber=N&uploadId=...   (upload one part, parallel)
       → 200 { ETag: "<part-md5>" }
POST   /{bucket}/{key}?uploadId=...            (complete: send list of {part, ETag})
       Body: [{1,"etag1"},{2,"etag2"},...]    → 200 { ETag, VersionId }
DELETE /{bucket}/{key}?uploadId=...            (abort — free orphaned parts)
```

**Why presigned URLs matter:** clients don't stream bytes through your API tier. The API issues a short-lived signed URL and the client PUT/GETs **directly against the data plane**, so your metadata/control servers never touch payload bytes. This is how one fleet serves 50 GB/s without melting.

## 4. High-Level Architecture

The defining decision: **separate the metadata plane from the data plane.** Metadata is small, hot, and needs a fast sharded KV store. Data is huge, cold-ish, and lives on dumb dense disk. They scale on completely different axes.

```
                         Client
                           │  PUT /bucket/key
                           ▼
                  ┌──────────────────┐
                  │  Load Balancer   │
                  └────────┬─────────┘
                           ▼
                  ┌──────────────────┐     auth, quota, routing.
                  │  API / Frontend  │     NEVER stores bytes long-term.
                  └───┬──────────┬───┘
            metadata  │          │  data (or hand back presigned URL)
                      ▼          ▼
          ┌───────────────────┐  ┌──────────────────────────────┐
          │  METADATA SERVICE │  │  PLACEMENT / DATA SERVICE     │
          │  bucket+key →     │  │  splits object into chunks,   │
          │  {chunk locations,│  │  erasure-codes, writes shards │
          │   version, size,  │  │  to data nodes across AZs     │
          │   checksum}       │  └───────────┬──────────────────┘
          │  (sharded KV)     │              │
          └─────────┬─────────┘    ┌─────────┼──────────┐
       shard by     │              ▼         ▼          ▼
    hash(bucket+key)│           ┌──────┐ ┌──────┐  ┌──────┐
        ┌───────┬───┴───┐       │ DN   │ │ DN   │  │ DN   │  ... 100s–1000s
        ▼       ▼       ▼       │ AZ-a │ │ AZ-b │  │ AZ-c │  of data nodes
     [meta]  [meta]  [meta]     └──────┘ └──────┘  └──────┘  (dumb dense disk)
     shard1  shard2  shard3       │
                                  └──► Background scrubber + repair workers
```

**PUT flow:**
1. API authenticates, checks bucket exists/quota.
2. Placement service splits the object into fixed-size chunks (e.g. 4–64 MB), erasure-codes each chunk into `k+m` shards (10+4), and writes the 14 shards to 14 data nodes spread across AZs.
3. On a write **quorum** of acks, it returns the chunk's locations.
4. Metadata service commits `bucket+key → [chunk locations], version, checksum, size` as one atomic record. **The object only "exists" once this metadata commit succeeds** — that's what makes read-after-write work.

**GET flow:**
1. API → metadata service: look up `bucket+key` → chunk list + locations + checksums.
2. For each chunk, read the data shards from data nodes (you only need `k`=10 of the 14 to reconstruct). Verify checksum.
3. Stream bytes back; if a shard is missing/corrupt, read a parity shard and reconstruct on the fly.

## 5. Data Model

```sql
-- METADATA SERVICE (sharded KV — modeled relationally for clarity).
-- Shard key = hash(bucket_id + key). Keeps one object's metadata on one shard;
-- prefix LISTs are served per-shard then merged.

CREATE TABLE objects (
  bucket_id     UUID        NOT NULL,
  object_key    TEXT        NOT NULL,       -- flat key: "photos/2026/a.jpg"
  version_id    TEXT        NOT NULL,       -- monotonic / UUID; "null" = unversioned
  size_bytes    BIGINT      NOT NULL,
  storage_class TEXT        NOT NULL,       -- STANDARD | IA | GLACIER
  full_checksum BYTEA       NOT NULL,       -- whole-object hash (for ETag / integrity)
  is_delete_marker BOOLEAN  DEFAULT FALSE,  -- versioned delete = a marker, not removal
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (bucket_id, object_key, version_id)
);

-- Each object → ordered list of chunks; each chunk → its erasure shards' locations.
CREATE TABLE chunks (
  bucket_id   UUID   NOT NULL,
  object_key  TEXT   NOT NULL,
  version_id  TEXT   NOT NULL,
  chunk_index INT    NOT NULL,             -- 0,1,2,... ordered for reassembly
  chunk_checksum BYTEA NOT NULL,
  shard_locations JSONB NOT NULL,          -- [{node_id, disk, shard_no}, ... 14 of them]
  PRIMARY KEY (bucket_id, object_key, version_id, chunk_index)
);

CREATE TABLE buckets (
  bucket_id    UUID PRIMARY KEY,
  name         TEXT UNIQUE NOT NULL,
  owner        UUID,
  versioning   BOOLEAN DEFAULT FALSE,
  lifecycle    JSONB                       -- e.g. {transition_IA_days:30, glacier:90}
);
```

```python
# DATA NODE: bytes on disk are keyed by an internal, location-agnostic shard id.
# The metadata service is the ONLY thing that maps user keys → these ids, so the
# data plane can move/rebalance shards freely without the user ever knowing.
#   /disk7/blobs/<chunk_uuid>.<shard_no>   +   /disk7/blobs/<chunk_uuid>.<shard_no>.crc
```

**Shard key choice — why `hash(bucket+key)` and not bucket alone:** sharding by bucket creates giant hot buckets. Hashing the full key spreads one bucket's objects across all metadata shards. The cost: a prefix LIST must scatter-gather across shards and merge-sort results (pagination cursors encode per-shard position).

## 6. Deep Dives

### 6a. Metadata/Data Separation, Routing & Partitioning

This is the architectural heart. **Metadata** (key → location map) is a few KB per object but must answer millions of lookups/sec with low latency → a horizontally **sharded KV store** (think a DynamoDB-class system, or sharded Postgres / FoundationDB). **Data** is the bytes themselves: huge, written once, read occasionally → dense commodity disk on data nodes that are deliberately "dumb."

```
Why split them?
  - They scale on different axes: metadata grows with OBJECT COUNT,
    data grows with TOTAL BYTES. A 1 KB object and a 5 TB object cost
    the same metadata but wildly different storage.
  - Data nodes can be rebalanced/replaced without touching the key->location
    contract, because only metadata knows where bytes physically live.
  - You can cache hot metadata aggressively (it's tiny); you can't cache PB of data.
```

**Partitioning the metadata** by `hash(bucket+key)` gives even load. The catch is LIST: `?prefix=photos/2026/` may touch every shard. You handle it by querying all shards in parallel, each returns its top-N for the prefix, and a coordinator merges them; the pagination `marker` is an opaque cursor encoding each shard's last-seen position. Range-sharding (lexicographic) would make LIST cheap but reintroduces hot shards on sequential keys (`log-2026-06-21-00001`, `...00002` all land on one shard) — the classic trade-off.

**Flat keyspace vs folders:** there are no directories. `a/b/c.txt` is a single opaque string key. A "folder view" is just `LIST prefix=a/b/ delimiter=/`, which returns common prefixes as pseudo-folders. This is why there's no atomic "rename folder" — it would be N copies + N deletes.

### 6b. Durability — Replication vs Erasure Coding, and "11 Nines"

Two ways to survive disk/node/AZ loss:

```
REPLICATION (N=3 across AZs):
  + simplest; a read is just "read any 1 of 3 copies"; fast repair (copy 1 disk)
  + great for small/hot objects (low latency)
  - 200% storage overhead (3x the disk)

ERASURE CODING (Reed-Solomon, k + m, e.g. 10 + 4):
  Split a chunk into k=10 data shards, compute m=4 parity shards → 14 total.
  Any 10 of the 14 reconstruct the original.
  + survives any 4 simultaneous shard losses
  + overhead = m/k = 4/10 = 40%  (vs 200% for 3x replication)
  - reconstruct-on-failure is CPU + network heavy (must read 10 shards & recompute)
  - small objects: 14 tiny shards = wasteful + many seeks → use replication for those
```

The real systems use **both**: replicate small/hot objects, erasure-code large/cold ones. Spread the 14 shards across AZs so losing an entire AZ still leaves ≥ `k` shards.

**Integrity — checksums + background scrubbing:** every shard is stored with a checksum (CRC32C). On every GET you verify; if a shard's checksum fails, treat it as lost and reconstruct from parity. A continuous **background scrubber** reads shards on a rolling schedule, re-verifies checksums, and triggers **repair** for any silent corruption (bit rot) or under-replicated chunk — *before* a second failure can cause data loss.

```python
# Repair worker (conceptual): detect under-durable chunk, rebuild missing shards.
def repair_chunk(chunk):
    healthy = [s for s in chunk.shards if verify_checksum(s)]      # need >= k
    if len(healthy) < chunk.k:
        raise DataLoss(chunk)                                      # the 10^-11 event
    if len(healthy) < chunk.k + chunk.m:                           # under-durable
        data = reed_solomon_decode(healthy, chunk.k)               # reconstruct object
        for missing in chunk.missing_shards():
            new_node = placement.pick_node(avoid_az=missing.az)    # keep AZ spread
            write_shard(new_node, reed_solomon_encode(data, missing.index))
            metadata.update_shard_location(chunk, missing.index, new_node)
```

**How you *claim* 11 nines:** it's a probability argument. Per-disk annual failure ~2%. With 10+4 you tolerate 4 concurrent losses, and the scrubber repairs a lost shard within minutes/hours (small repair window). The chance that ≥5 of a chunk's 14 shards die *within that same window*, faster than repair, is ~10⁻¹¹/year. AZ-spread eliminates correlated failures (power, network). You never claim 11 nines from one mechanism — it's erasure coding **×** fast repair **×** AZ isolation **×** checksum-driven scrubbing.

### 6c. Large Objects, Consistency, Versioning & Tiering

**Multipart upload** — how you PUT a 5 TB object reliably:
```
1. POST ?uploads            → server returns an UploadId; metadata holds a pending manifest.
2. Client splits the file into parts (e.g. 100 MB each) and PUTs them IN PARALLEL,
   each independently checksummed & erasure-coded. A failed part is retried alone —
   you never re-upload 5 TB because byte 4.9 TB flaked.
3. POST complete {part->ETag list}  → server validates every part's checksum,
   stitches the chunk list together in order, and commits ONE final metadata record.
   The object becomes visible atomically at this commit.
4. Orphaned parts from never-completed uploads are reaped by a lifecycle rule.
```

**Consistency model:** because metadata commit is the single atomic "object now exists" point, you get **read-after-write for new keys** for free — a GET either finds the committed metadata or doesn't. The hard cases are **overwrites** and **deletes**: a GET racing an overwrite may briefly see the old version. Modern S3 is strongly consistent here by making metadata the linearizable source of truth (a quorum/consensus write on the metadata record). Old garbage shards are cleaned by GC once no live version references them.

**Versioning:** with versioning on, an overwrite writes a **new** `version_id` rather than mutating; a DELETE inserts a `delete_marker` (so a GET returns 404, but the prior version is recoverable). Because objects are immutable, this is cheap — you're only ever appending version rows.

**Lifecycle / tiering:** a per-bucket policy migrates objects by age across **storage classes**: `STANDARD → IA (Infrequent Access, cheaper, retrieval fee) → GLACIER (archival, minutes-to-hours retrieval, cheapest)`. A background lifecycle engine scans metadata (`created_at` + policy), re-encodes/relocates the bytes to colder/denser media, and updates `storage_class`. The key↔metadata contract never changes, so the move is invisible to clients except for retrieval latency on Glacier.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Hot prefix / per-prefix throttling:** S3 historically partitioned by key prefix, so a workload writing `logs/2026-06-21/00001, 00002, ...` (sequential, same prefix) hammered one partition. Mitigations: (1) **hash/randomize the high-order key bytes** (`<hash>/logs/...`) to spread load; (2) request-rate auto-partitioning that splits a hot prefix's keyspace across more nodes as traffic climbs. Cross-reference the same hot-key problem in the URL shortener ([03_url_shortener.md](./03_url_shortener.md)).

**Quorum reads/writes:** to bound latency on the metadata record and tolerate node loss, use quorum: with N replicas of a metadata partition, require `W + R > N` (e.g. N=3, W=2, R=2) for strong consistency. On the data plane, a write returns success on a quorum of shard acks rather than all 14, so one slow/dead AZ doesn't stall the PUT; lagging shards are filled by repair.

**Failure modes:**
- *Single data node down:* GETs reconstruct from surviving shards (need only `k`); repair re-spreads shards. No client impact.
- *Whole AZ down:* because shards are AZ-spread, ≥`k` survive → reads still serve; PUTs route around the dead AZ.
- *Metadata shard down:* keys on that shard are unreadable until failover to a replica → this is why metadata needs quorum/consensus replication, not single-node.
- *Correlated bit rot:* the scrubber is your defense — without it, silent corruption accumulates and you eventually fail two shards on one read.

**Trade-offs to say out loud:**
- Erasure coding saves disk but costs CPU/network on repair and adds read amplification for small objects → replicate small/hot, EC large/cold.
- Strong consistency on overwrites costs a consensus round-trip on metadata → fine because metadata is tiny and not on the byte path.
- Flat keyspace makes LIST a scatter-gather and "rename" non-atomic — the price of infinite-scale partitioning.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: immutable objects, flat keyspace, 11 nines durability is THE goal,
           throughput- not latency-oriented, sizes 1B–5TB.
3-7 min:   Estimation: 50B objects → 50 TB of METADATA (can't fit one node → sharded KV).
           Raw storage: 3x replication = 200% overhead vs 10+4 EC = 40%. Plant the EC seed.
7-14 min:  Architecture. THE big idea: split metadata plane (key->location, sharded KV)
           from data plane (dumb dense disk). Walk a PUT and a GET. Mention presigned URLs
           keep bytes off the control tier.
14-19 min: Data model. objects + chunks + shard_locations. Shard key = hash(bucket+key),
           and the LIST scatter-gather cost that buys.
19-27 min: DEEP DIVE durability: replication vs Reed-Solomon erasure coding (10+4 math),
           checksums + background scrubber + repair, then DERIVE 11 nines as a product of
           EC × fast repair × AZ spread. This is the round-winner — spend the time here.
27-34 min: Large objects + consistency: multipart upload (parallel parts, atomic complete),
           read-after-write via atomic metadata commit, versioning (delete markers),
           lifecycle tiering Standard->IA->Glacier.
34-40 min: Bottlenecks: hot prefix throttling + key randomization; quorum W+R>N on metadata.
40-45 min: Trade-offs recap + questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — storage, replication, CAP sections
- [Hello Interview](https://www.hellointerview.com) — object store / S3 walkthroughs
- [ByteByteGo — how S3 / object storage works](https://www.youtube.com/results?search_query=bytebytego+s3+object+storage+system+design)
- [NeetCode — distributed file/object storage design](https://www.youtube.com/results?search_query=neetcode+distributed+object+storage+system+design)
- [ByteByteGo — erasure coding vs replication](https://www.youtube.com/results?search_query=bytebytego+erasure+coding+reed+solomon)

**Paid (optional):**
- "System Design Interview, Vol 2" by Alex Xu — Chapter: **Design S3-like Object Storage**
- [Grokking the Modern System Design Interview](https://www.designgurus.io) — distributed object storage / blob store module

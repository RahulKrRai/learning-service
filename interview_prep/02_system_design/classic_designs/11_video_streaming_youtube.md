# Video Streaming (YouTube / Netflix)

> Appears at: Google, Amazon (and any company with a media/CDN story). The "big iron" design — tests your grasp of blob storage, async pipelines, CDN economics, and read-heavy scale. The trap is spending the whole hour on transcoding; the real signal is the **delivery** path (CDN + adaptive bitrate). Budget your time so you reach 6b.

## 1. Requirements

**Functional:**
- Upload a video (creators); store it durably.
- Transcode the upload into multiple resolutions/codecs + generate thumbnails.
- Stream/playback a video to viewers with adaptive quality.
- Search and browse (metadata: title, description, channel, tags).
- View counts, likes, comments (focus this design on view counts).

**Non-functional:**
- ~1B users, read(playback)-heavy. Read:write skew is enormous — millions watch, thousands upload.
- YouTube scale: ~500 hrs of video uploaded **per minute**.
- Playback start time (time-to-first-frame) < 1-2s; smooth rebuffer-free playback is the core UX metric.
- Durability of the original upload is paramount (you can re-transcode, you cannot un-lose the source). 11 nines (S3-class).
- Global: a viewer in São Paulo and one in Berlin both get low-latency playback.
- Upload availability can be eventually consistent / async; playback availability must be high.

**Clarifying questions:**
1. "YouTube (UGC, anyone uploads) or Netflix (curated catalog)?" → **YouTube/UGC** — assume open uploads, so the transcoding pipeline must autoscale and be fully automated. (Netflix pre-transcodes a fixed catalog offline — simpler pipeline, same delivery.)
2. "Do we need live streaming?" → Out of scope; assume **VOD** (video-on-demand). Live is a different beast (low-latency HLS, sub-second chunks).
3. "Is the recommendation/feed ranking in scope?" → No. Assume metadata search + a basic browse. Cross-reference [04_news_feed_fanout.md](./04_news_feed_fanout.md) if asked about home-feed ranking.

## 2. Back-of-Envelope Estimation

```
UPLOADS
  500 hrs/min uploaded = 30,000 video-hrs/hr = 720,000 video-hrs/day
  Avg video length ~10 min → 720,000*60/10 = 4.32M videos/day = ~50 videos/sec
  Raw source bitrate (1080p H.264) ≈ 5 Mbps = 0.625 MB/s
    → 1 hr source ≈ 2.25 GB
    → 500 hrs/min * 2.25 GB = ~1.1 TB ingested per MINUTE of raw source

STORAGE (the killer number — multiple renditions blow this up)
  Per video you store original + ~5 renditions (240/360/480/720/1080) + codecs (H.264/VP9/AV1)
  Transcoded set ≈ 1.5-2x the source size.
  720,000 hr/day * 2.25 GB * ~2 (renditions) ≈ 3.2 PB/day of NEW encoded data
  Over a year → ~1.2 EB/yr. This is why storage tiering (hot/cold) is non-negotiable.

PLAYBACK (read path — the real load)
  Assume 1B users, 5 videos/day avg → 5B views/day = ~58,000 views/sec avg, ~250K/sec peak
  Streaming bitrate avg ~3 Mbps. Concurrent streams at peak ~ tens of millions.
  Egress: 5B views * 10 min * 3 Mbps = a staggering bandwidth bill.
  → 90%+ of bytes MUST be served from CDN edge, never from origin.

TRANSCODING COMPUTE
  50 videos/sec uploaded, each fans out to ~5 renditions * codecs.
  Transcoding is ~1-4x real-time per rendition → a worker pool of thousands of cores,
  autoscaled by queue depth.
```
Takeaways to say out loud: **storage (PB/EB) forces tiering**, **egress forces a CDN**, **bursty upload forces a queue-based autoscaling pool**.

## 3. API Design

```
# --- UPLOAD (resumable / chunked) ---
POST /api/v1/videos                      # create the video record, get an upload session
  Body: { title, description, channel_id, visibility }
  → 201 { video_id, upload_url, upload_id }

PUT  /api/v1/uploads/{upload_id}/chunks  # upload one chunk (resumable)
  Headers: Content-Range: bytes 0-8388607/52428800
  → 308 Resume Incomplete   (server tells client the next expected byte)
  → 200 when last chunk lands

POST /api/v1/uploads/{upload_id}/complete
  → 202 Accepted  { video_id, status: "PROCESSING" }   # transcoding kicked off async

# --- PLAYBACK ---
GET /api/v1/videos/{video_id}            # metadata (title, channel, status, view_count)
  → 200 { video_id, title, status: "READY", manifest_url, thumbnails:[...] }

GET /manifests/{video_id}/master.m3u8    # HLS master manifest (signed URL, served via CDN)
  → 200 (lists the bitrate variants; client's ABR engine picks one)

GET /segments/{video_id}/720p/seg_0042.ts  # a media segment (signed, CDN-cached)
  → 200 (binary)

# --- ENGAGEMENT ---
POST /api/v1/videos/{video_id}/view      # fire-and-forget view event
  → 202 Accepted
```
Notes: `/complete` returns **202** — transcoding is async, status moves `PROCESSING → READY → FAILED`. Playback URLs are **signed** (short-lived HMAC) so they can't be hot-linked or shared past expiry.

## 4. High-Level Architecture

```
                          UPLOAD PATH                              PLAYBACK PATH
 Creator                                              Viewer
   │ chunked PUT                                        │ GET master.m3u8 / segments
   ▼                                                    ▼
┌──────────────┐                              ┌────────────────────────┐
│ Upload Svc   │── multipart ──► [ Blob Store: ]│   CDN  (edge PoPs)     │ ◄─ 90%+ of bytes
│ (resumable)  │                 [ RAW originals]└───────────┬────────────┘
└──────┬───────┘                                            │ cache miss (cold/long-tail)
       │ "upload complete" event                            ▼
       ▼                                          ┌────────────────────┐
┌──────────────────┐                              │  Origin / Blob     │
│  Kafka topic     │  see 06_distributed_message  │  (transcoded HLS,  │
│  "transcode.jobs"│  _log_kafka.md               │   manifests, thumbs)│
└────────┬─────────┘                              └────────────────────┘
         │ consumed by
         ▼
┌────────────────────────────────────────────┐
│  Transcoding Orchestrator (DAG / workflow)  │
│   split → fan-out renditions → thumbnails    │
│        → package HLS/DASH → publish          │
└───────┬─────────────────────────────────────┘
        │ fans out tasks onto a queue
        ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │worker 1│ │worker 2│ │worker N│   autoscaled by queue depth (CPU/GPU pool)
   └────────┘ └────────┘ └────────┘
        │ outputs (segments+manifest) written to Blob Store
        ▼
   on success → update Metadata DB: status=READY, manifest_url
              → pre-warm CDN for popular channels

Metadata plane (both paths read it):
   API Servers ──► Metadata DB (video info)  ──► Redis (hot metadata cache)
               ──► View-count pipeline (Kafka → sharded counters → async rollup)
```

**Upload flow:** chunked upload → assembled in blob store → emit "complete" event to Kafka → orchestrator runs a DAG (split, transcode fan-out, thumbnail, package) → outputs to blob → flip metadata to `READY`.

**Playback flow:** client fetches metadata → gets signed manifest URL → CDN serves the manifest + segments; the client's ABR engine requests higher/lower bitrate variants based on measured bandwidth. Origin is touched only on a cold cache miss.

## 5. Data Model

```sql
-- Video metadata (relational: Postgres / Spanner / DynamoDB). Shard key: video_id.
CREATE TABLE videos (
  video_id     UUID PRIMARY KEY,         -- shard key (hash) → even distribution
  channel_id   UUID NOT NULL,
  title        TEXT,
  description  TEXT,
  status       VARCHAR(16),              -- PROCESSING | READY | FAILED
  duration_s   INT,
  visibility   VARCHAR(12),              -- public | unlisted | private
  manifest_url TEXT,                     -- HLS master once READY
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_videos_channel ON videos(channel_id, created_at DESC);  -- channel page

-- Renditions produced by transcoding (one row per resolution/codec)
CREATE TABLE renditions (
  video_id     UUID,
  codec        VARCHAR(8),               -- h264 | vp9 | av1
  resolution   VARCHAR(8),               -- 240p..1080p..4k
  bitrate_kbps INT,
  segment_path TEXT,                     -- prefix in blob store
  PRIMARY KEY (video_id, codec, resolution)
);

-- View counts: sharded counters (see deep dive 6c). NOT a single row.
CREATE TABLE view_counts_shard (
  video_id  UUID,
  shard_id  SMALLINT,                    -- 0..N-1
  count     BIGINT,
  PRIMARY KEY (video_id, shard_id)
);
```
```
# Blob store layout (S3/GCS) — the actual bytes, NOT in the DB:
#   raw/{video_id}/source.mp4                       (cold tier after transcode)
#   hls/{video_id}/master.m3u8
#   hls/{video_id}/{res}/segment_{n}.ts             (hot tier, CDN-fronted)
#   thumbs/{video_id}/{n}.jpg
```
**Why this split:** the DB holds small, queryable metadata; the blob store holds the heavy bytes. **Shard metadata by `video_id`** (hash) — playback and the API always know the `video_id`, so lookups are single-shard. A channel's video list is an index by `channel_id`.

## 6. Deep Dives

### 6a. Upload + Transcoding Pipeline

**Resumable, chunked upload.** A 2 GB upload over flaky mobile cannot be a single POST. The client splits the file into chunks (e.g. 8 MB) and `PUT`s each with a `Content-Range`. The server tracks received ranges; on a dropped connection the client asks "where were you?" and resumes from the next byte. This is exactly S3 multipart upload / GCS resumable upload — lean on the blob store's native support rather than reinventing it.

**Why a queue, not synchronous transcoding.** Transcoding a 1-hour video into 5 renditions is minutes of CPU. You cannot block the upload request. On `/complete`, the Upload Service writes the assembled source to the blob store and **publishes a job to Kafka** (`transcode.jobs`). See [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md) — Kafka gives you durable, replayable, partitioned job delivery, and the consumer group is your worker pool that scales independently. If a worker dies mid-job, the offset isn't committed and another worker re-processes (idempotently, keyed by `video_id + segment`).

**The pipeline is a DAG, not a single job.** An orchestrator (Temporal / Airflow / Step Functions style) drives:

```
            ┌──► transcode 240p ──┐
            ├──► transcode 360p ──┤
[source] ──►│──► transcode 720p  ──┤──► package HLS/DASH manifests ──► publish (status=READY)
   │        ├──► transcode 1080p ─┤        ▲
   │        └──► transcode + AV1 ─┘        │
   └──► extract thumbnails ────────────────┘
```

Splitting further: chop the source into **independent segments (e.g. 6s GOP-aligned chunks)** and transcode segments in parallel across many workers — a 1-hour video becomes 600 tiny jobs that finish in wall-clock seconds instead of minutes. Then stitch.

```python
# Orchestrator pseudo-DAG (conceptual)
def run_pipeline(video_id, source_path):
    segments = split_into_gop_chunks(source_path, seconds=6)        # fan-out unit
    ladder = [(240,400), (360,800), (480,1400), (720,2800), (1080,5000)]  # res, kbps
    tasks = []
    for res, kbps in ladder:
        for seg in segments:
            tasks.append(enqueue("transcode.jobs",                  # → Kafka
                {"video_id": video_id, "seg": seg.id, "res": res, "kbps": kbps}))
    enqueue("thumbnail.jobs", {"video_id": video_id, "source": source_path})
    wait_all(tasks)                                                 # barrier
    for res, _ in ladder:
        package_hls(video_id, res)        # concat segments → variant playlist
    write_master_manifest(video_id, ladder)                         # master.m3u8
    db.update(video_id, status="READY", manifest_url=...)
    cdn_prewarm_if_popular(video_id)
```

**Idempotency & failures:** each task is keyed; reprocessing overwrites the same `segment_path`. A poisoned job (corrupt source) goes to a **dead-letter topic** after N retries and flips `status=FAILED`. **Packaging into HLS/DASH:** the output is a *master manifest* listing variant playlists; each variant playlist lists segment URLs. The player downloads the master, then streams segments.

### 6b. Streaming & Delivery (the part that earns the offer)

**CDN is the architecture, not a footnote.** Origin egress at this scale is financially impossible. 90%+ of bytes are served from edge PoPs close to the viewer. Origin is hit only on a cold miss; the edge then caches the segment for the next viewer (and segments are immutable, so caching is trivial — infinite TTL, content-addressed paths).

**Adaptive Bitrate (ABR) — HLS/DASH.** The intelligence lives in the **client**, not the server. The player:
```
1. GET master.m3u8  → sees variants: [240p@400k, 480p@1.4M, 720p@2.8M, 1080p@5M]
2. Starts conservative (e.g. 480p) for fast time-to-first-frame.
3. Measures throughput of each downloaded segment + buffer occupancy.
4. If bandwidth is healthy and buffer is full → request the next segment at a HIGHER variant.
   If throughput drops / buffer drains → step DOWN a variant to avoid a rebuffer (stall).
```
Because every variant is cut into the **same 6s segment boundaries**, the player can switch quality at any segment edge seamlessly. This is why we GOP-align during transcode.

**Popularity-based pre-positioning.** You don't push every video to every edge — the long tail would blow edge storage. Instead:
- **Pull-through (default):** first viewer in a region triggers a cold miss; edge fetches and caches. Subsequent viewers hit cache.
- **Push/pre-warm (popular content):** for a video trending or a known big launch, proactively push segments to edges *before* the demand spike. Drive this off the view-count signal (6c) and channel size.

**Signed URLs.** Manifests and segments are served via short-lived signed URLs (HMAC of path + expiry + sometimes viewer IP). Stops hot-linking, enforces geo/entitlement (Netflix licensing, age gates), and bounds the blast radius of a leaked link. The signing happens at the API/edge auth layer; the CDN validates the signature.

### 6c. Metadata + View Counts at Massive Scale

**Metadata** is small and read-heavy: cache aggressively in Redis (cache-aside, keyed by `video_id`), front it with read replicas. A cache miss falls through to the sharded metadata DB. This is the easy part — name it and move on.

**View counts are the interesting scale problem.** A viral video gets millions of views/sec. A single `UPDATE videos SET views = views+1` is a hot-row write contention disaster (every increment serializes on one row). Three techniques, layered:

1. **Async ingestion (don't write on the hot path).** The `POST /view` endpoint emits an event to Kafka and returns 202 immediately. A consumer aggregates.
2. **Sharded counters.** Spread one logical counter across N rows/keys; increment a random shard; the displayed count is the SUM. Removes the hot-row bottleneck.
```python
N_SHARDS = 256
def record_view(video_id):
    shard = random.randint(0, N_SHARDS - 1)
    redis.incr(f"views:{video_id}:{shard}")          # contention spread 256-way

def get_view_count(video_id):
    return sum(int(redis.get(f"views:{video_id}:{s}") or 0)   # SUM of shards
               for s in range(N_SHARDS))                       # cache this result
```
3. **Approximate / batched rollup.** Exact-to-the-millisecond counts don't matter for display. Batch-aggregate the Kafka stream every few seconds (windowed) and write the rolled-up total back to the DB. For "unique viewers" rather than raw views, use **HyperLogLog** (Redis `PFADD`/`PFCOUNT`) — ~12 KB gives a count of billions within ~2% error, instead of storing every viewer ID.

**Eventual consistency is the deliberate trade-off:** the count you show may lag reality by seconds. That's fine — nobody refunds a view. You trade strict accuracy for write throughput and cost.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x (5,000 hrs/min uploaded, 50B views/day):**
- *Transcoding compute* becomes the cost center. Mitigate: GPU-accelerated encoding, segment-level parallelism (already in 6a), and a **priority queue** — transcode 360p/720p first so the video is playable in seconds, then backfill 1080p/4K and AV1 asynchronously.
- *Storage* hits exabytes. **Tiering is mandatory:** hot segments (recently/frequently watched) on SSD-backed object storage + CDN; the cold long tail and **raw originals** demoted to cheap cold storage (S3 Glacier / Coldline) via lifecycle policies. Re-promote on a sudden view spike. Most videos are watched in their first week, then go cold forever.
- *CDN egress* is the dominant bill. Multi-CDN (Akamai + CloudFront + own PoPs), peering agreements, and ISP-embedded caches (Netflix Open Connect appliances inside ISPs) cut transit cost.

**Global distribution:** metadata DB is multi-region with regional read replicas (reads local, writes routed to a home region — accept cross-region write latency for uploads, which are rare). Blob originals are replicated to a few regions; the CDN handles the last-mile globally. Choose the viewer's nearest healthy edge via anycast/GeoDNS.

**CAP:** the playback/metadata read path is **AP** — favor availability; a slightly stale title or view count is fine. The upload→READY transition is eventually consistent by design (202 + status polling). The only thing you protect with strong durability (not consistency) is the **raw source object**.

**Failure modes:**
- *CDN edge down:* clients fail over to another edge / origin; ABR may drop quality but playback survives. Origin must have headroom for the miss surge.
- *Transcoding worker crash:* Kafka offset uncommitted → job re-delivered → idempotent reprocess. No data loss.
- *Orchestrator stuck:* per-stage timeouts + DLQ; video sits in `PROCESSING` and is surfaced for retry, never silently lost.
- *Origin/blob outage:* CDN keeps serving cached (immutable) segments; only cold long-tail videos and new uploads are affected.
- *Thundering herd on a viral cold video:* request coalescing at the edge (collapse concurrent cold-misses into one origin fetch) + pre-warm on the trending signal.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: YouTube-UGC vs Netflix-catalog (pick UGC), VOD not live, recos out of scope.
3-7 min:   Estimation. Land the 3 punchlines: PB/EB storage → tiering; massive egress → CDN;
           bursty 500hr/min upload → queue + autoscaled worker pool.
7-12 min:  High-level arch. Draw TWO paths side by side: upload (write) and playback (read).
           Stress that they are decoupled by a queue and a blob store.
12-16 min: Data model. Metadata DB (shard by video_id) + renditions + the bytes live in blob store,
           not the DB. Mention signed manifest_url.
16-25 min: DEEP DIVE 6a — upload + transcoding. Resumable chunked upload → Kafka job
           (reference the Kafka design) → DAG → segment-level fan-out → HLS/DASH packaging →
           idempotency + DLQ. This is where you show pipeline maturity.
25-34 min: DEEP DIVE 6b — delivery. CDN as the core; ABR (client picks bitrate per segment);
           GOP-aligned segments enable seamless switching; pre-positioning popular content;
           signed URLs. SPEND TIME HERE — it's the strongest signal.
34-38 min: DEEP DIVE 6c — view counts: async via Kafka, sharded counters, HLL for uniques,
           eventual consistency trade-off.
38-43 min: Bottlenecks: storage tiering hot/cold, multi-CDN/egress cost, priority transcode,
           global distribution + CAP stance (AP reads, durable source).
43-45 min: Questions / extensions (live streaming, DRM, recommendations → point to 04_news_feed).
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — System Design](https://www.hellointerview.com)
- [ByteByteGo — design YouTube / video streaming](https://www.youtube.com/results?search_query=bytebytego+design+youtube+video+streaming)
- [NeetCode — YouTube system design](https://www.youtube.com/results?search_query=neetcode+youtube+system+design)
- Related siblings: [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md) (the transcode queue), [02_distributed_cache.md](./02_distributed_cache.md) (metadata cache + CDN ideas), [04_news_feed_fanout.md](./04_news_feed_fanout.md) (feed/recommendation extension).

**Paid (optional):**
- "System Design Interview — Volume 2" by Alex Xu — Chapter: Design YouTube.
- [Grokking the System Design Interview](https://www.designgurus.io) — Designing YouTube/Netflix module.

# Photo / Media Sharing (Instagram)

> Appears everywhere: Google L5 (Photos/YouTube media), Amazon L6 (Prime Photos, media pipelines), Uber (receipt/photo storage), Atlassian (media in Confluence/Jira), Confluent (you'd reframe the pipeline around Kafka). The defining trait vs a generic feed is that **media dominates** — petabytes of binaries, multi-resolution variants, and CDN delivery are the real problem. The feed fan-out itself is covered in [04_news_feed_fanout.md](./04_news_feed_fanout.md); don't re-derive it here. Spend your air time on the **upload → process → store → deliver** pipeline.

## 1. Requirements

**Functional:**
- Upload a photo/video with a caption; system stores it durably and makes it viewable.
- View a user's profile grid and individual posts (original + thumbnails at multiple resolutions).
- Home feed of posts from followed accounts (delegate the fan-out to [04](./04_news_feed_fanout.md)).
- Like / comment, with counts shown on every post.
- Follow / unfollow; follower & following counts.
- Stories: ephemeral media that auto-expires after 24h.

**Non-functional:**
- 500M DAU; ~95M media uploads/day; heavily **read-skewed** (read:write ≈ 100:1).
- Media must be durable (11 nines — never lose a user's photo) and globally fast (< 100ms to first byte from CDN).
- Feed/profile load < 200ms p95; upload feels instant to the client (durable accept in < 1s, processing async).
- Cost matters: at petabyte scale, egress/CDN bandwidth is the dominant bill.

**Clarifying questions:**
1. "Photos only, or video too?" → Both, but lead with photos; video adds transcoding (HLS/DASH) — mention, don't drown in it.
2. "Do we generate multiple resolutions?" → Yes — thumbnail, feed, full. This is the core of the design.
3. "Is the feed in scope or just the media pipeline?" → Focus media; reference the fan-out design for the feed.
4. "Edits/filters server-side?" → Client applies filters before upload; server stores what it receives.

## 2. Back-of-Envelope Estimation

```
DAU:                       500M
Uploads/day:               95M  ≈ 1,100/sec avg  ≈ 3,500/sec peak
Feed + media views/day:    ~10B image fetches ≈ 115,000/sec avg ≈ 350,000/sec peak

Per upload, store original + 3 variants (thumb / feed / full):
  original (avg):          2 MB
  full (1080w):            300 KB
  feed (640w):             100 KB
  thumb (150w):            15 KB
  total per post:          ≈ 2.4 MB

Blob storage growth:       95M × 2.4 MB ≈ 230 TB/day ≈ 84 PB/year  → object store (S3), not a DB
Metadata per post:         post_id, author, caption, variant keys, dims ≈ 1 KB
Metadata growth:           95M × 1 KB ≈ 95 GB/day ≈ 35 TB/year  → sharded Postgres / Cassandra

CDN bandwidth (the real cost):
  115K views/sec × ~150 KB avg served (mostly feed/thumb) ≈ 17 GB/sec egress
  → ~1.5 PB/day egress. CDN cache hit ratio of 90%+ is mandatory or the bill explodes.

Feed cache (post_ids only, NOT blobs):
  500M users × 20 items × 8 B = 80 GB → Redis Cluster   (see 04)
```

The headline number to say out loud: **84 PB/year of binaries** and **~17 GB/sec of egress**. That immediately forces "binaries live in an object store behind a CDN; the database only holds metadata and pointers."

## 3. API Design

```
# --- Upload: presigned / direct-to-blob, two-phase ---
POST /v1/media/upload-url
Body: { content_type: "image/jpeg", byte_size: 2097152 }
Auth: Bearer token
→ 200 { upload_id, upload_url: "https://blob.../uploads/ab12?X-Amz-Signature=...",
        expires_in: 900 }
        # client PUTs the bytes DIRECTLY to upload_url (object store), bypassing app servers

# --- Finalize: create the post once bytes are uploaded ---
POST /v1/posts
Body: { upload_id, caption: "...", location: "...", visibility: "public" }
→ 201 { post_id, status: "processing", created_at }
        # variants are generated async; post is viewable with thumb first

# --- Read a post (metadata + CDN URLs, never bytes through the app) ---
GET /v1/posts/{post_id}
→ { post_id, author_id, caption, created_at, like_count, comment_count,
    media: {
      thumb: "https://cdn.logw.rd/p/abc/thumb.webp",
      feed:  "https://cdn.logw.rd/p/abc/feed.webp",
      full:  "https://cdn.logw.rd/p/abc/full.webp"
    },
    status: "ready" }     # or "processing"

# --- Feed (delegates to fan-out service; returns media REFS, see 04) ---
GET /v1/feed?limit=20&cursor=<opaque>
→ { items: [{ post_id, author_id, author_name, caption, media:{...cdn urls...},
              like_count, comment_count, is_liked }], next_cursor, has_more }

# --- Interactions / graph ---
POST   /v1/posts/{post_id}/like     → 204
POST   /v1/users/{user_id}/follow   → 204
POST   /v1/stories                  → 201 { story_id, expires_at }   # TTL 24h
```

**Why presigned direct upload?** The 2 MB of bytes never touch your API servers — the client `PUT`s straight to S3 using a short-lived signed URL. Your app servers stay tiny and stateless; they only mint URLs and write metadata. This is the single most important API decision.

## 4. High-Level Architecture

```
                      ┌──────────────────────────────────────────┐
   Client             │  WRITE PATH (upload)                      │
     │                │                                           │
     │ 1. POST upload-url                                         │
     ├───────────────►│  Upload Service ── mints presigned URL    │
     │◄───────────────┤  (stateless API)                          │
     │ 2. PUT bytes    └──────────────┬───────────────────────────┘
     │   (direct)                     │
     ▼                                ▼
┌──────────────┐            ┌──────────────────┐
│ Object Store │◄───────────│  raw-uploads/     │  (S3, 11 nines durability)
│  (S3)        │            └────────┬──────────┘
└──────┬───────┘                     │  S3 event / Kafka: media.uploaded
       │                             ▼
       │                  ┌───────────────────────────┐
       │  3. POST /posts  │  Media Processing Workers  │
       │  (finalize)      │  - validate, strip EXIF    │
       │                  │  - generate thumb/feed/full│
       │                  │  - transcode video (HLS)   │
       │                  │  - write variants to S3     │
       │                  │  - update post.status=ready│
       │                  └────────┬──────────────────┘
       ▼                           │ Kafka: posts.created
┌──────────────┐                   ▼
│ Post Service │           ┌──────────────────────┐
│  writes      │           │ Fan-out Service       │  ── see 04_news_feed_fanout.md
│  metadata    │──────────►│ (hybrid push/pull)    │     (writes post_id refs to feeds)
└──────┬───────┘           └──────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Metadata stores                                              │
│   Posts DB (sharded by post_id)   Follows DB   Counters(Redis)│
└──────────────────────────────────────────────────────────────┘

                      ┌──────────────────────────────────────────┐
   Client             │  READ PATH (view)                         │
     │ GET /feed       │                                          │
     ├────────────────►│ Feed Svc → Redis feed (post_id refs)     │
     │◄────────────────┤        → Posts Cache (metadata + CDN urls)│
     │                 └──────────────────────────────────────────┘
     │ GET cdn.logw.rd/p/abc/feed.webp
     ▼
┌──────────────────────────────────────────────────────────────┐
│  CDN (CloudFront) ── 90%+ hit ratio ── origin = S3            │
└──────────────────────────────────────────────────────────────┘
```

**The mental model:** two completely separated planes.
- **Metadata plane** (small, structured, transactional): Postgres/Cassandra + Redis. Holds who-posted-what, captions, counts, and the *keys/URLs* of media variants.
- **Binary plane** (huge, immutable, cacheable): S3 + CDN. Holds the actual pixels. App servers never proxy bytes.

## 5. Data Model

```sql
-- Post metadata (sharded by post_id; Snowflake-style id so it's time-sortable)
CREATE TABLE posts (
  post_id       BIGINT PRIMARY KEY,        -- Snowflake: [ts][shard][seq], k-sortable
  author_id     BIGINT NOT NULL,
  caption       TEXT,
  location      TEXT,
  media_count   SMALLINT DEFAULT 1,        -- carousels hold multiple media
  status        SMALLINT NOT NULL,         -- 0=processing 1=ready 2=failed
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_posts_author_time ON posts(author_id, created_at DESC);  -- profile grid

-- Media variants: one row per (post, variant). Binary lives in S3; this is the pointer.
CREATE TABLE media_assets (
  asset_id      BIGINT PRIMARY KEY,
  post_id       BIGINT NOT NULL,
  variant       SMALLINT NOT NULL,         -- 0=orig 1=thumb 2=feed 3=full 4=video_hls
  s3_key        TEXT NOT NULL,             -- "p/ab/cd/abc123/feed.webp"
  cdn_url       TEXT NOT NULL,
  width         INT, height INT,
  byte_size     INT,
  codec         TEXT                       -- webp / avif / h264
);
CREATE INDEX idx_media_post ON media_assets(post_id);
```

```
# Follows graph (Postgres or Cassandra) — see 04 for the fan-out usage
follows(follower_id, followee_id, created_at)   PK(follower_id, followee_id)
  idx(followee_id)   -- "who follows celebrity X" for fan-out

# Counters (Redis, sharded — see 6c)
HINCRBY  count:{post_id}  likes 1
HINCRBY  count:{post_id}  comments 1

# Stories (TTL-native store)
story:{story_id}   →  { author_id, media_url, created_at }   EXPIRE 86400
story_set:{author_id}  → ZSET of story_ids, score=created_at  (auto-pruned)
```

**Shard key choices that matter:**
- `posts` and `media_assets` shard by **`post_id`** (Snowflake id) — writes spread evenly, and the embedded timestamp makes a post id roughly time-ordered so a profile grid sorts cheaply.
- `follows` shards by **`follower_id`** for "show me my following" and is also indexed by `followee_id` for fan-out (the two access patterns pull in opposite directions — this is the classic graph trade-off, expanded in 6c).
- **Never** shard by `author_id` for posts alone — a celebrity becomes a hot shard.

## 6. Deep Dives

### 6a. Media Upload & Storage Pipeline (the heart of this design)

This is where you win or lose the interview. Walk it as a pipeline.

**Step 1 — Presigned direct upload (keep bytes off your servers).**
```python
# Upload Service: mint a short-lived presigned PUT URL
def create_upload_url(user_id: int, content_type: str, byte_size: int) -> dict:
    assert content_type in {"image/jpeg", "image/png", "image/heic", "video/mp4"}
    assert byte_size <= MAX_UPLOAD_BYTES         # reject huge uploads up front
    upload_id = snowflake()
    key = f"raw-uploads/{user_id}/{upload_id}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": RAW_BUCKET, "Key": key,
                "ContentType": content_type, "ContentLength": byte_size},
        ExpiresIn=900,                            # 15 min window
    )
    return {"upload_id": upload_id, "upload_url": url, "s3_key": key}
```
The client PUTs the raw bytes directly to S3. Your API never sees 2 MB of pixels — it handles a few hundred bytes of JSON. This is what makes the upload path cheap and horizontally trivial.

**Step 2 — Event-driven async processing.** An S3 `ObjectCreated` event (or an explicit `media.uploaded` Kafka message on finalize) wakes a pool of **Media Processing Workers**. Processing is async because resizing/transcoding takes hundreds of ms to seconds — you must not block the user.

```python
# Media Processing Worker (consumes media.uploaded)
VARIANTS = [("thumb", 150), ("feed", 640), ("full", 1080)]

def process(msg):
    raw = s3.get_object(RAW_BUCKET, msg.s3_key)
    img = decode(raw)
    img = strip_exif(img)                         # privacy: drop GPS/EXIF
    if is_malicious(raw):                          # validate: real image, size sane
        mark_failed(msg.post_id); return
    for name, width in VARIANTS:
        variant = resize_keep_aspect(img, width)
        out = encode(variant, fmt="webp", quality=82)   # webp/avif = ~30% smaller
        key = f"p/{shard(msg.post_id)}/{msg.post_id}/{name}.webp"
        s3.put_object(MEDIA_BUCKET, key, out)
        record_asset(msg.post_id, name, key, cdn_url(key), variant.dims)
    set_status(msg.post_id, "ready")
    kafka.produce("posts.created", {"post_id": msg.post_id})   # NOW trigger fan-out
```

**Key decisions to defend:**
- **Why multiple variants?** A phone scrolling a feed should download a 100 KB `feed` image, not a 2 MB original — saves ~95% bandwidth (the dominant cost) and battery. The grid uses 15 KB thumbs. Only a tap-to-zoom fetches `full`.
- **Metadata vs binary separation.** The DB row is ~1 KB; the pixels are 2.4 MB in S3. The DB stays small and fast; S3 gives 11-nines durability and infinite scale. Reads of the post return *URLs*, and the client/CDN fetches binaries directly.
- **Idempotency / retries.** Processing is keyed by `post_id`; reprocessing overwrites the same S3 keys, so a redelivered Kafka message is harmless. Failed processing → `status=failed`, surfaced to the user as "upload failed, retry."
- **Video** is the same shape, heavier: transcode to **HLS/DASH** adaptive bitrate ladders (240p/480p/720p/1080p) via a fan-out of transcode jobs; store segments in S3; serve the `.m3u8` manifest through the CDN. Say this in one breath; don't rabbit-hole.
- **Optimization the panel likes:** generate the thumb *first* and flip `status=ready` early so the post appears almost instantly, then backfill larger variants. Perceived-instant uploads.

**Step 3 — CDN delivery.** Variants live under a CDN (CloudFront) with S3 as origin. URLs are immutable and content-addressed-ish (`/p/<shard>/<post_id>/feed.webp`), so they're cacheable forever (`Cache-Control: public, max-age=31536000, immutable`). A user in São Paulo fetches from a São Paulo edge; origin (S3) is hit only on a cache miss.

### 6b. Feed Generation — What's Media-Specific

The fan-out mechanics (push for normal users, pull for celebrities, the hybrid model, cursor pagination) are fully covered in [04_news_feed_fanout.md](./04_news_feed_fanout.md) — **say "I'd use the hybrid fan-out from my feed design" and move on.** Here, focus only on the media angles:

- **Feeds store references, never blobs.** The Redis feed is `feed:{user_id} → [post_id, post_id, ...]` (8 bytes each). On read you hydrate metadata (caption, counts, and the **CDN URLs** of variants) from the Posts Cache. The 80 GB feed cache in §2 is only possible because no pixels are in it.
- **The client gets URLs and fetches media itself.** Feed JSON returns `media.feed` / `media.thumb` CDN URLs; the device lazy-loads images as they scroll into view. Your servers serve JSON; the CDN serves bytes.
- **Variant selection is a feed-time decision.** Return the `feed` (640w) variant for the scroll view; the client requests `full` only on tap. On slow networks the client can pick a smaller variant (or you expose a `srcset`-style set).
- **Media-aware ranking signals.** On top of 04's freshness/engagement score, media adds signals: dwell time on a photo, video watch-completion %, whether the media was zoomed/saved, and image-quality/aspect-ratio fit. Mention these as ranking *inputs*; the ranking formula itself lives in 04.

### 6c. Follow Graph + Counters at Scale (the celebrity / hot-post problem)

**Follow graph storage.** `follows(follower_id, followee_id)` with two access patterns that fight each other:
- "Who do *I* follow?" → shard/index by `follower_id`.
- "Who follows celebrity X?" (needed for fan-out) → index by `followee_id`.

You maintain both — either two indexes in Postgres or two denormalized tables in Cassandra (`following_by_user`, `followers_by_user`). A celebrity's follower list is huge (100M rows) and is paginated, never loaded whole. For fan-out, the follower list is streamed in batches (see 04's celebrity handling).

**Like/comment counts — sharded counters.** A naive `UPDATE posts SET like_count = like_count + 1` row-locks; a post that goes viral gets thousands of likes/sec all contending on one row. Fixes, in order of sophistication:

```python
# 1) Redis atomic counter — absorbs the write storm, no DB lock
def like(post_id, user_id):
    if redis.sadd(f"liked:{post_id}", user_id):       # SADD returns 1 if newly added (dedupe)
        redis.hincrby(f"count:{post_id}", "likes", 1)  # O(1), atomic
    # periodically flush count:{post_id} → Postgres (every N sec or N likes)

# 2) For a HOT post, even one Redis key is a hot key → SHARD the counter
def like_hot(post_id, user_id):
    bucket = user_id % 16                              # spread across 16 keys
    redis.hincrby(f"count:{post_id}:{bucket}", "likes", 1)

def get_likes(post_id):                                # read = sum the shards
    return sum(int(redis.hget(f"count:{post_id}:{b}", "likes") or 0)
               for b in range(16))
```

- **Sharded counters** spread a single logical counter across N Redis keys (here keyed by `user_id % 16`) so the write load is divided by N. Reads sum the shards — slightly more expensive, but reads of an exact like count are rare and tolerant of being approximate.
- **Counts are eventually consistent.** Displaying "1,204,991 likes" off by a few for a second is fine; trading strict consistency for availability here is the right call (AP over CP for counters).
- **The celebrity/hot-post problem ties together:** a celebrity post is (1) skipped by fan-out-on-write and pulled on read (04), (2) its media variants are pre-warmed in the CDN because everyone will fetch them, and (3) its like counter is sharded because the whole world is liking it simultaneously. Naming all three when asked "what happens when a celebrity posts?" is the senior-level answer.

**Stories (ephemeral, briefly):** media uploaded the same way, but the metadata lives in a TTL-native store (Redis key with `EXPIRE 86400`, or a Cassandra table with TTL columns). After 24h the metadata auto-expires; a lazy/batch janitor reclaims the S3 binaries. Stories don't fan out into the durable feed — they're read by pulling the `story_set:{author}` of each followed account, which is cheap because they're few and short-lived.

## 7. Bottlenecks, Failure Modes & Trade-offs

**CDN cost & cache strategy (the dominant operational concern):**
- Egress is ~1.5 PB/day; CDN egress is billed per GB and dwarfs compute/storage. A **90%+ cache hit ratio is mandatory**, not a nice-to-have.
- Levers: long `max-age` immutable URLs (variants never mutate), serve `feed`/`thumb` (small) by default not `full`, use **WebP/AVIF** (~30% smaller than JPEG at equal quality), **tiered caching** (regional edge → origin shield → S3) so a popular photo hits S3 once globally, and **pre-warm** a celebrity's variants at publish time so the first million viewers all hit warm edges.
- Cold/long-tail media (old posts) will miss the CDN and hit S3 — that's fine and cheap; you don't pay edge storage for content nobody views.

**Storage tiering for cost:** move originals/old variants from S3 Standard → Infrequent-Access → Glacier as posts age. Keep the small feed/thumb variants hot (they're cheap and frequently re-viewed); cold-tier the rarely-fetched originals.

**Failure modes:**
- **Processing worker backlog/down:** uploads still land in S3 (durable); the queue buffers. Users see `status=processing` longer. Autoscale workers on queue depth. Nothing is lost.
- **CDN/edge outage in a region:** clients fail over to another edge or origin; latency rises but reads still serve from S3. The metadata plane is unaffected.
- **S3 partial outage:** binaries become temporarily unreadable for affected keys; cached media still serves from CDN. New uploads to that region fail — fail over the bucket to another region (cross-region replication for the metadata-critical buckets).
- **Redis counter loss:** if a counter shard is lost before flushing to Postgres, counts regress slightly; reconcile from the source-of-truth `likes` rows in a periodic batch job. Acceptable because counts are explicitly approximate.
- **Orphaned blobs:** a finalize that never arrives leaves a raw upload with no post. A janitor sweeps `raw-uploads/` older than the 15-min presign window.

**Trade-offs to state out loud:**
- **Async processing → eventual visibility.** A post isn't instantly viewable at full res; we trade strict immediacy for an instant, durable accept. Mitigated by thumb-first `status=ready`.
- **Metadata/binary separation → more moving parts** (an extra store + a CDN) but it's the only thing that scales to petabytes; a monolithic blob-in-DB design dies at this scale.
- **Multiple variants → more storage & processing** (~1.2× the original per post) but slashes the far-more-expensive egress bill — a clear win.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: photos+video, multi-resolution variants, feed in scope?,
           server-side filters? Land on "media pipeline is the focus; feed
           fan-out I'll reference from my news-feed design."
3-7 min:   Estimation. SAY THE BIG NUMBERS: 84 PB/year binaries, ~17 GB/sec
           egress. Conclude: binaries in object store + CDN, DB holds only
           metadata + pointers.
7-13 min:  Architecture. Draw the two planes (metadata vs binary) and the two
           paths (write=upload pipeline, read=feed/CDN). Emphasize presigned
           direct upload — bytes never hit app servers.
13-18 min: Data model. posts + media_assets (pointer rows), follows, Redis
           counters, stories with TTL. Justify post_id shard key.
18-30 min: DEEP DIVE 6a — upload pipeline. Presign → direct PUT → S3 event →
           async workers generate thumb/feed/full (webp), strip EXIF, write
           variants, flip status=ready (thumb-first), trigger fan-out.
           CDN delivery with immutable URLs. This is the crux — spend the time.
30-36 min: 6c — sharded counters for likes (Redis SADD dedupe + bucketed
           HINCRBY), follow-graph dual indexing, the celebrity trifecta
           (pull fan-out + CDN pre-warm + sharded counter).
36-40 min: 6b — feed holds CDN refs not blobs (why 80 GB cache fits);
           media-specific ranking signals. Reference 04 for fan-out.
40-43 min: Bottlenecks: CDN cache hit ratio is the bill; WebP/AVIF, tiered
           cache, storage tiering. Stories TTL. Failure modes.
43-45 min: Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — CDN, object storage, and caching sections
- [Hello Interview — design Instagram / media systems](https://www.hellointerview.com)
- [ByteByteGo — design Instagram](https://www.youtube.com/results?search_query=bytebytego+design+instagram+system+design)
- [NeetCode — Instagram system design](https://www.youtube.com/results?search_query=neetcode+instagram+system+design)
- Sibling designs: [04_news_feed_fanout.md](./04_news_feed_fanout.md) (feed fan-out, ranking, pagination), [03_url_shortener.md](./03_url_shortener.md) (CDN + cache-aside warm-up)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a News Feed System (fan-out) and the photo/CDN material in Vol. 2
- [Grokking the System Design Interview](https://www.designgurus.io) — "Designing Instagram"

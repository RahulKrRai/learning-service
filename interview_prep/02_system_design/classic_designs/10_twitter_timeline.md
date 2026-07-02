# Twitter / Home Timeline

> Appears at: Google L5, Uber, Amazon L6, Atlassian, and essentially every senior backend loop. The "design Twitter" canonical. The interviewer is testing whether you reach for **hybrid fan-out** under your own steam and can defend the **tweet object model, distributed ID generation, and the read-time merge**. The fan-out *mechanics* (push vs pull, celebrity problem) are covered in [04_news_feed_fanout.md](./04_news_feed_fanout.md) — don't re-derive them here; reference that file and spend your air time on what's Twitter-specific: the tweet object, Snowflake IDs, and the exact merge algorithm.

## 1. Requirements

**Functional:**
- Post a tweet (≤ 280 chars, optional media: images/video).
- Follow / unfollow users (asymmetric social graph — following ≠ followed-back).
- Home timeline: a blend of tweets from everyone you follow, reverse-chronological (with light ranking).
- User timeline: all tweets by a single user (their profile page).
- Retweet, reply, like (interactions on a tweet).
- Out of scope unless asked: DMs, search (point to [05_typeahead_autocomplete.md](./05_typeahead_autocomplete.md)), trending (covered lightly in 6c).

**Non-functional:**
- ~300M MAU; avg ~200 follows; power users follow 10K+, celebrities have 10M–100M followers.
- ~200M tweets/day; read:write ratio extremely high (~1000:1 — most of Twitter is reading).
- Home timeline read p99 < 200ms.
- Tweet visible to followers within a few seconds (eventual consistency is fine — no read-your-writes guarantee across other users).
- High availability over strong consistency: a slightly stale timeline beats an error page.

**Clarifying questions (with assumed answers):**
1. "Strictly chronological or ranked?" → Reverse-chron baseline with light ranking allowed; full ML ranking out of scope.
2. "Hard limit on follower / following counts?" → No limit. Must handle 100M-follower celebrities — this drives the whole design.
3. "Do tweet IDs need to be sortable / convey time order?" → Yes. We want roughly time-ordered, 64-bit, globally unique IDs (Snowflake) so timelines sort cheaply.

## 2. Back-of-Envelope Estimation

```
MAU:                    300M
Tweets/day:             200M  → 200M / 86,400 ≈ 2,300 tweets/sec avg
                                 peak ~ 3x avg ≈ 7,000 tweets/sec
Timeline reads:         300M users × ~10 timeline refreshes/day
                        = 3B reads/day ≈ 35,000 reads/sec avg, ~100K/sec peak
Read:write             35,000 / 2,300 ≈ 15:1 at the API; far higher counting
                        per-tweet object reads inside each timeline.

Fan-out writes (push):  2,300 tweets/sec × 200 avg followers
                        ≈ 460,000 timeline-cache writes/sec (the real cost — see 04).

Tweet object size:      id(8B) + author_id(8B) + text(280B) + media refs(~200B)
                        + counts(24B) + ts(8B) ≈ ~550B, round to ~1KB w/ overhead.
Tweet storage/day:      200M × 1KB = 200 GB/day ≈ 73 TB/year (before replication).

Timeline cache:         store only tweet IDs, not objects.
                        300M users × 800 IDs × 8B = ~1.9 TB  → Redis Cluster.
                        (Cap each cached timeline at ~800 IDs; older = served from DB.)

Media:                  Stored in blob store (S3) + CDN, never in the tweet row.
                        Tweet row holds only media keys/URLs.
```

The number to say out loud: **~460K fan-out writes/sec** is what forces the hybrid model. Reads are cheap (read a precomputed ID list); the asymmetry is the whole game.

## 3. API Design

```
# Post a tweet
POST /v1/tweets
Body: { text: "...", media_keys: ["s3://...mp4"], reply_to: <tweet_id|null>,
        quote_of: <tweet_id|null> }
Auth: Bearer
→ 201 { tweet_id: "1745...snowflake", author_id, created_at }

# Home timeline (cursor pagination — see 04 §6c, don't use OFFSET)
GET /v1/timeline/home?limit=20&cursor=<opaque>
→ { items: [{ tweet_id, author: {id,handle,name,avatar}, text, media,
              like_count, retweet_count, reply_count, retweeted_by?,
              created_at }],
    next_cursor, has_more }

# User timeline (a single author's tweets)
GET /v1/users/{user_id}/tweets?limit=20&cursor=<opaque>

# Interactions
POST   /v1/tweets/{id}/like        → 204
POST   /v1/tweets/{id}/retweet     → 201 { retweet_id }
POST   /v1/users/{id}/follow       → 204
DELETE /v1/users/{id}/follow       → 204

# Media: upload directly to blob store via pre-signed URL, then reference the key.
POST /v1/media:initUpload → { upload_url (pre-signed S3 PUT), media_key }
```

Cursor = base64 of the last tweet's Snowflake ID. Because Snowflake IDs are time-sortable, the cursor *is* a time cursor — `WHERE id < cursor ORDER BY id DESC` paginates with no separate timestamp column. That's a Twitter-specific win from the ID design.

## 4. High-Level Architecture

```
                    Client (web / mobile)
                          │
                    ┌─────┴─────┐
                    │  API GW   │  (auth, rate limit — see 01_rate_limiter.md)
                    └─────┬─────┘
        WRITE PATH        │           READ PATH
   ┌──────────────────────┴───────────────────────┐
   ▼                                               ▼
┌──────────────┐                          ┌───────────────────┐
│ Tweet Service│                          │ Timeline Service  │
│ 1. mint ID   │                          │ 1. read pushed IDs│
│   (Snowflake)│                          │    from Redis     │
│ 2. write row │                          │ 2. pull celeb IDs │
│ 3. emit Kafka│                          │ 3. MERGE + rank   │
└──────┬───────┘                          │ 4. hydrate objects│
       │ tweets.created                   └─────────┬─────────┘
       ▼                                            │
┌──────────────┐   follower list   ┌────────────────┴───────────┐
│ Fan-out      │◄──────────────────│ Social Graph Service       │
│ Workers      │   (Graph DB)      │ follows / followers lookup │
│ push to      │                   └────────────────────────────┘
│ Redis        │
│ timeline:{u} │      Stores:
└──────────────┘   ┌─ Tweet DB (sharded by tweet_id)   — source of truth
                   ├─ Graph DB (edges: follower→followee)
                   ├─ Redis Cluster: timeline:{user} (precomputed ID lists)
                   ├─ Tweet Cache (tweet_id → object, hot tweets)
                   └─ Blob store (S3) + CDN for media
```

**Write flow:** Tweet Service mints a Snowflake ID, writes the tweet row to the sharded Tweet DB, emits `tweets.created` to Kafka. Fan-out workers consume it, look up the author's followers in the Graph Service, and (for non-celebrities) LPUSH the tweet ID onto each follower's `timeline:{user}` Redis list. Celebrity tweets skip fan-out (see 04).

**Read flow:** Timeline Service reads the precomputed ID list from Redis, separately pulls recent tweet IDs from each celebrity the user follows, **merges** the two streams (§6b), hydrates the top N IDs into full objects from the Tweet Cache, and returns them.

## 5. Data Model

```sql
-- Tweets: source of truth. Sharded by tweet_id (Snowflake) so a shard owns a
-- contiguous-ish slice and writes spread across shards by sequence/worker bits.
CREATE TABLE tweets (
  tweet_id    BIGINT PRIMARY KEY,          -- Snowflake (see 6a), time-sortable
  author_id   BIGINT NOT NULL,
  text        VARCHAR(280) NOT NULL,
  media_keys  TEXT[],                       -- S3 keys; media never inline
  reply_to    BIGINT,                       -- parent tweet for replies
  quote_of    BIGINT,                       -- quoted tweet
  like_count  INT DEFAULT 0,                -- denormalized, approximate
  rt_count    INT DEFAULT 0,
  reply_count INT DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- User timeline query (profile page): all tweets by an author, newest first.
CREATE INDEX idx_tweets_author ON tweets(author_id, tweet_id DESC);

-- Social graph. Two access patterns → two indexes (or two tables / a graph DB).
CREATE TABLE follows (
  follower_id BIGINT NOT NULL,   -- I follow ...
  followee_id BIGINT NOT NULL,   -- ... this person
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (follower_id, followee_id)
);
-- "Who do I follow?"  (build my timeline / pull celebs):
--    sharded by follower_id (PK already covers it)
-- "Who follows celebrity X?" (fan-out target list):
CREATE INDEX idx_follows_followee ON follows(followee_id);

-- A retweet is a tweet that references another tweet (no text, or quote text).
-- Reuse the tweets table: rt_of column or quote_of for quote-tweets.
```

**NoSQL alternative (what Twitter actually uses):** tweets and timelines in a wide-column store (Cassandra/Manhattan). Timeline = a row keyed by `user_id` with tweet IDs as clustering columns sorted descending → range scan gives the timeline directly.

```
# Redis structures (the hot path)
timeline:{user_id}   → LIST of tweet_ids (capped ~800 via LTRIM). Push model output.
tweet:{tweet_id}     → HASH of the tweet object. TTL ~24h. Hydration cache.
celeb_tweets:{uid}   → ZSET (score = tweet_id ≈ time) of a celebrity's recent IDs,
                       short TTL. Read-side cache so every follower's merge is cheap.
```

**Shard keys to state explicitly:** Tweet DB sharded by `tweet_id`; Graph sharded by `follower_id` for the "who do I follow" path with a secondary index on `followee_id` for fan-out target lookup; Redis timelines sharded by `user_id`.

## 6. Deep Dives

### 6a. Tweet object model, media, and distributed IDs (Snowflake)

The tweet object is small and immutable-ish: text, author, timestamps, media references, and *denormalized* counters. Two Twitter-specific decisions:

**Media never lives in the tweet row.** The client uploads bytes to a blob store (S3) via a pre-signed URL and gets back a `media_key`. The tweet row stores only the key. Reads serve media from a CDN. This keeps the tweet row ~1KB and lets a 200M-row/day table stay scannable. Video gets a transcoding pipeline (Kafka → workers → multiple bitrates), but for the interview say "async transcode, store renditions in S3, reference the master key."

**Distributed unique IDs — Snowflake.** You need 64-bit, globally unique, *roughly time-ordered* IDs without a central counter (a single DB sequence can't do 7K writes/sec across regions). This is the same problem as the URL-shortener key generator — reference [03_url_shortener.md §6a](./03_url_shortener.md) for the counter-vs-hash discussion, then specialize to Snowflake:

```python
# Snowflake 64-bit layout:  [ 1 unused | 41 timestamp | 10 worker | 12 sequence ]
EPOCH_MS = 1_288_834_974_657          # custom epoch (Twitter's, 2010-11-04)

class Snowflake:
    def __init__(self, worker_id: int):
        assert 0 <= worker_id < 1024   # 10 bits = 1024 workers
        self.worker_id = worker_id
        self.seq = 0
        self.last_ms = -1

    def next_id(self) -> int:
        now = current_millis()
        if now == self.last_ms:                 # same ms → bump sequence
            self.seq = (self.seq + 1) & 0xFFF    # 12 bits = 4096 ids/ms/worker
            if self.seq == 0:                    # sequence exhausted this ms
                now = wait_next_millis(self.last_ms)
        else:
            self.seq = 0
        self.last_ms = now
        return ((now - EPOCH_MS) << 22) | (self.worker_id << 12) | self.seq
```

Why this matters for Twitter specifically: the 41 timestamp high-bits make IDs **monotonic by time**, so sorting a timeline = sorting integers, and pagination cursors are just `id < last_id`. No separate timestamp index needed. Worker IDs are handed out by ZooKeeper/etcd (or a config service) so no two machines collide. Capacity: 4096 ids/ms/worker × 1024 workers ≫ 7K/sec peak.

**Storage & sharding.** Shard the Tweet DB by `tweet_id`. Because Snowflake high bits are time, naive range-sharding by ID would hot-spot the newest shard; instead hash the ID (or use the worker/sequence low bits) to spread writes, while keeping per-author reads cheap via the `(author_id, tweet_id DESC)` index. A read of "user X's last 20 tweets" is a single-shard index scan.

### 6b. Home timeline generation — hybrid fan-out and the read-time merge

The push/pull trade-off and the celebrity problem are fully derived in [04_news_feed_fanout.md §6a](./04_news_feed_fanout.md). **Don't repeat it.** What's Twitter-specific and worth your air time is the **exact merge at read time** and the **cache structure**.

**Two sources feed one timeline:**
1. **Pushed (non-celebrity authors):** their tweet IDs were fan-out-on-write into `timeline:{me}` (a Redis LIST, capped at ~800 via `LTRIM` after each `LPUSH`). Reading is `LRANGE timeline:{me} 0 199` — O(1)-ish.
2. **Pulled (celebrity authors I follow):** never fanned out. At read time, for each celebrity I follow, fetch their recent IDs from `celeb_tweets:{uid}` (a Redis ZSET scored by tweet_id ≈ time). Most are cache hits; on miss, read `tweets WHERE author_id = ? ORDER BY tweet_id DESC LIMIT N` and backfill.

**The merge (this is what they want to see):**

```python
def home_timeline(me, limit=20, cursor=None):
    upper = cursor or MAX_ID                    # Snowflake IDs sort by time

    # 1. Pushed stream: precomputed, already time-ordered (descending).
    pushed = redis.lrange(f"timeline:{me}", 0, 400)        # tweet IDs
    pushed = [i for i in pushed if i < upper]

    # 2. Pulled stream: union of each followed celebrity's recent IDs.
    celebs = graph.celebrities_followed(me)                # small set (cached)
    pulled = []
    for c in celebs:
        ids = redis.zrevrangebyscore(f"celeb_tweets:{c}", upper - 1, 0, num=50)
        pulled.extend(ids)

    # 3. K-way merge two already-sorted streams by ID (= by time), desc.
    #    Because both streams are sorted, this is a heap merge, not a full sort.
    merged = heapq.merge(pushed, sorted(pulled, reverse=True), reverse=True)

    # 4. De-dup (a tweet could arrive via both paths during threshold flips),
    #    take top `limit`, then hydrate IDs → objects from tweet cache.
    top = dedup_take(merged, limit)
    tweets = mget_tweets(top)                              # Redis tweet:{id} HASH
    return {"items": tweets, "next_cursor": top[-1] if top else None}
```

Key points to narrate:
- The merge is a **k-way merge of pre-sorted ID streams**, not a sort of raw tweets — IDs are time-ordered so we merge integers, cheap.
- We **hydrate only the top `limit`** IDs into full objects. The expensive object fetch is bounded by page size, not by feed size.
- The celebrity set is tiny (you follow few celebrities relative to total follows), so the pull side stays small. The `celeb_tweets:{c}` ZSET is shared across *all* of that celebrity's followers — one cache entry amortized over millions of readers (vs. millions of pushed copies if we'd fanned out).

**Timeline cache structure & eviction:**
- `timeline:{user}` capped at ~800 IDs. Older history isn't cached — profile/deep-scroll reads fall through to the Tweet DB by author.
- **Evict cold users entirely:** don't keep timelines for users inactive > N days. On their return, lazily rebuild from the Graph + recent tweets (show a brief loading state). This is how 1.9 TB stays manageable — only active users occupy cache.
- Redis maxmemory policy `allkeys-lru` as a backstop; rebuild on miss is always possible because the Tweet DB + Graph are the source of truth.

**How this differs from the news-feed file's emphasis:** that file argues *when* to push vs pull. Here the focus is the **per-tweet object + Snowflake ID** that make the streams cheaply sortable, and the **concrete heap-merge + bounded hydration** at read time.

### 6c. Trending topics & search (high level)

**Trending = streaming heavy-hitters, not a SQL `GROUP BY COUNT`.** You can't count every hashtag exactly at 7K tweets/sec across a sliding window. Use approximate counting:

```
Kafka tweets.created
   → stream processor (Flink / Kafka Streams), windowed (e.g. 5-min sliding)
   → Count-Min Sketch per window to approximate per-hashtag counts in fixed memory
   → maintain a top-K heap (heavy hitters) of the highest-count terms
   → write top-K + score to Redis ZSET  trending:{region}
   → also weight by velocity (rate of change), not just volume, so genuinely
     "trending" (spiking) terms beat perennially-high ones.
```

Count-Min Sketch gives you per-term frequency in sub-linear memory with a bounded over-count — perfect when "approximately the top 20 hashtags" is the requirement. Partition by region/locale for localized trends.

**Full-text search of tweets is its own design** — inverted index, sharded by term, near-real-time indexing off the same Kafka stream. Don't build it here; point to [05_typeahead_autocomplete.md](./05_typeahead_autocomplete.md) for the prefix/autocomplete angle and say "tweet body search = Elasticsearch-style inverted index fed from `tweets.created`, out of scope for this session."

**Social graph storage & "who to fan out to":** the fan-out worker's hot lookup is "who follows author X" → the `idx_follows_followee` index (or graph DB). For celebrities this list is 10M–100M rows; you never materialize it for push (that's the whole reason they're pull). For normal users it's a few-hundred-row scan, cheap. The reverse lookup, "who do I follow" (sharded by `follower_id`), builds the pull side and is cached per active user.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x (2B tweets/day, 3B MAU):**
- Fan-out writes → ~4.6M/sec. Push must shard fan-out workers by follower hash, and the celebrity threshold must drop (more users become "pull") to cap write amplification.
- Timeline cache → ~19 TB. Aggressively evict inactive users; cap timeline depth tighter.
- Tweet DB → 730 TB/year. Time + hash sharding; cold tweets tier to cheaper storage; old shards become read-mostly.

**CAP stance:** Choose **AP**. Timelines are eventually consistent — a follower seeing a tweet 3 seconds late, or a like count off by a few, is acceptable. We never block a timeline read on a consistent write. The one place you tighten consistency is the author's *own* view (read-your-writes): serve their own new tweet from a local write-through so they don't think the post failed.

**Failure modes & recovery:**
- *Redis timeline shard down:* timelines on that shard are unavailable from cache → fall back to on-the-fly build from Graph + Tweet DB (slower, ~pull-for-everyone) until the shard recovers and rebuilds. Source of truth is intact.
- *Fan-out worker lag (Kafka backlog):* tweets land in the DB immediately (durable) but appear in followers' cached timelines late. The pull path still surfaces them for celebrities; for normal users, freshness degrades gracefully — no data loss, just latency. Scale out consumers; the Kafka log lets workers resume from offset.
- *Celebrity-post thundering herd on read:* millions hit `celeb_tweets:{c}` at once. The shared ZSET + short TTL + request coalescing (single-flight backfill on miss) prevents a DB stampede.
- *Hot tweet (viral) counter contention:* don't `UPDATE ... SET like_count = like_count+1` (row lock). Increment a Redis counter, flush to DB periodically — approximate counts, same pattern as [04 §7](./04_news_feed_fanout.md).

**Core trade-off to verbalize:** push optimizes the 1000:1 read side at the cost of write amplification; pull does the reverse. Twitter's follower distribution is so skewed (a handful of 50M+ accounts) that *neither alone works* — hybrid is forced by the data, not a preference.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: chronological-vs-ranked, no follower cap (celebrities!),
           IDs should be time-sortable. State AP > CP.
3-6 min:   Estimation. Land the two numbers: ~35K timeline reads/sec and the
           ~460K fan-out writes/sec — say "that asymmetry forces hybrid fan-out."
6-11 min:  Architecture: split write path (Tweet Svc → Kafka → fan-out) from
           read path (Timeline Svc: pushed + pulled + merge + hydrate).
11-16 min: Data model + shard keys: tweets by tweet_id, graph by follower_id
           with a followee_id index, Redis timeline:{user}. Media in S3.
16-22 min: DEEP DIVE 6a: tweet object, media-by-reference, Snowflake IDs
           (draw the 41/10/12 bit layout, explain time-sortability → cheap
           pagination). Reference 03 for the general key-gen discussion.
22-32 min: DEEP DIVE 6b: hybrid fan-out — reference 04 for push/pull theory,
           then WALK THE MERGE: pushed LIST + pulled ZSETs → heap-merge by ID →
           hydrate top 20. Cache cap + cold-user eviction. THIS is the crux.
32-37 min: 6c trending (count-min sketch + top-K + velocity); point to 05 for
           full-text search. Social-graph fan-out lookup.
37-42 min: Failure modes: Redis shard loss → rebuild from source; Kafka lag →
           graceful staleness; viral-tweet counter via Redis. CAP = AP.
42-45 min: 10x scaling + questions.
```

## Resources

**Free:**
- [System Design Primer — system design topics & social network](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — design Twitter / X](https://www.hellointerview.com)
- [ByteByteGo — design Twitter](https://www.youtube.com/results?search_query=bytebytego+design+twitter+system+design)
- [NeetCode — design Twitter system design](https://www.youtube.com/results?search_query=neetcode+design+twitter+system+design)
- [ByteByteGo — Snowflake unique ID generation](https://www.youtube.com/results?search_query=bytebytego+snowflake+unique+id+generator)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: *Design a News Feed System* (timeline fan-out) and *Design a Unique ID Generator in Distributed Systems* (Snowflake).
- [Grokking the Modern System Design Interview — DesignGurus](https://www.designgurus.io) — "Design Twitter" module.

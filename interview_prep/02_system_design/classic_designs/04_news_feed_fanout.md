# News Feed / Fan-out

> Appears at: Google L5 (social features on YouTube/Google+), Amazon L6 (notification/activity feeds), Uber (driver activity feeds). Tests fan-out trade-offs, feed ranking, pagination design.

## 1. Requirements

**Functional:**
- Users follow other users
- When a user posts, their followers see the post in their feed
- Feed is roughly chronological, with light ranking (freshness + relationship weight)
- Pagination: infinite scroll (load more)
- Basic interactions: like, comment count shown on feed items

**Non-functional:**
- 500M DAU; avg 200 followers per user; 1% of users are "celebrities" with > 1M followers
- Post creation: 5M posts/day = ~60/sec
- Feed load: 500M users × 5 feed loads/day = 2.5B loads/day = ~29,000 loads/sec
- Feed load latency: < 200ms p95
- Feed freshness: new posts appear within 5 seconds for most followers

**Clarifying questions:**
1. "How many users can one person follow? And max followers?" → No explicit limit; must handle celebrities with 1M+ followers.
2. "Is feed strictly chronological or ranked?" → Roughly chronological; light engagement-based ranking is fine.
3. "Do we handle media (videos/images) in the feed?" → Show URLs; actual media stored in CDN separately.

## 2. Back-of-Envelope Estimation

```
DAU:                       500M
Posts per day:             5M = 60 writes/sec
Feed loads per day:        2.5B = 29,000 reads/sec

Fan-out (avg):             1 post → 200 followers → 200 feed writes (fan-out on write)
Fan-out writes/sec:        60 posts/sec × 200 followers = 12,000 feed writes/sec
Celebrity fan-out:         1 post by celebrity (1M followers) = 1M feed writes → spike!

Feed cache storage:        500M users × 20 feed items × 1KB = 10TB
                           Store only post_ids in feed (not full post data) → 8 bytes each
                           500M × 20 × 8B = 80GB → fits in Redis Cluster

Post storage:              5M/day × 1KB = 5GB/day = 1.8TB/year
```

## 3. API Design

```
# Create post
POST /v1/posts
Body: { content: "...", media_urls: [], visibility: "public" }
Auth: Bearer token
→ 201 { post_id, created_at, author_id }

# Get feed (paginated)
GET /v1/feed?limit=20&cursor=<opaque_cursor>
→ {
    items: [{ post_id, author_id, author_name, content, media_urls,
              created_at, like_count, comment_count, is_liked_by_me }],
    next_cursor: "<opaque_cursor>",
    has_more: true
  }

# Like / Unlike
POST   /v1/posts/{post_id}/like    → 204
DELETE /v1/posts/{post_id}/like    → 204

# Get post detail
GET /v1/posts/{post_id}
→ { post, comments: [...], like_count }

# Follow / Unfollow
POST   /v1/users/{user_id}/follow    → 204
DELETE /v1/users/{user_id}/follow    → 204
```

## 4. High-Level Architecture

```
User
  │
  │ POST /posts
  ▼
┌────────────────────────────────────────────────────────┐
│  Post Service                                           │
│  1. Store post in Posts DB (PostgreSQL)                 │
│  2. Publish to Kafka: posts.created                     │
└───────────────────────────────────────────────────────┘
                          │
                Kafka: posts.created
                          │
                          ▼
              ┌───────────────────────────┐
              │  Fan-out Worker           │
              │  (regular users)          │
              │  1. Fetch follower list   │
              │  2. For each follower,    │
              │     LPUSH feed:{user_id}  │
              │     post_id to Redis      │
              │  3. Trim to 500 items     │
              └───────────────────────────┘

              ┌───────────────────────────┐
              │  Celebrity Handler        │
              │  (users with > 1M follow) │
              │  Skip fan-out on write    │
              │  → fetch on read instead  │
              └───────────────────────────┘

User
  │
  │ GET /feed
  ▼
┌────────────────────────────────────────────────────────┐
│  Feed Service                                           │
│  1. LRANGE feed:{user_id} 0 19 → [post_ids] (Redis)   │
│  2. Fetch post details from Posts Cache                 │
│  3. Merge celebrity posts (fan-out on read for them)   │
│  4. Sort by rank score, return top 20                   │
└────────────────────────────────────────────────────────┘

Infrastructure:
  Posts DB (PostgreSQL, sharded by post_id)
  Follows DB (PostgreSQL: follower_id, followee_id)
  Feed Cache (Redis Cluster: feed:{user_id} → sorted list of post_ids)
  Posts Cache (Redis: post:{post_id} → post data, 24h TTL)
```

## 5. Data Model

```sql
-- Posts
CREATE TABLE posts (
  post_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id    UUID NOT NULL,
  content      TEXT NOT NULL,
  media_urls   TEXT[],
  like_count   BIGINT DEFAULT 0,
  comment_count BIGINT DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_posts_author_time ON posts(author_id, created_at DESC);

-- Follows graph
CREATE TABLE follows (
  follower_id  UUID NOT NULL,
  followee_id  UUID NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (follower_id, followee_id)
);
CREATE INDEX idx_follows_followee ON follows(followee_id);  -- "who follows celebrity X"

-- Likes
CREATE TABLE likes (
  post_id    UUID NOT NULL,
  user_id    UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (post_id, user_id)
);

-- Feed in Redis:
-- Key: "feed:{user_id}"   Type: List (or Sorted Set for ranking)
-- Value: [post_id_1, post_id_2, ...] (max 500 items)
-- On write: LPUSH feed:{follower_id} {post_id}; LTRIM feed:{follower_id} 0 499

-- Post cache in Redis:
-- Key: "post:{post_id}"   Type: Hash
-- Fields: author_id, content, media_urls, like_count, comment_count, created_at
-- TTL: 86400 (24h)
```

## 6. Deep Dives

### 6a. Fan-out on Write vs Fan-out on Read

**Fan-out on write (push model):**
- On post creation, immediately write `post_id` to each follower's feed in Redis.
- Pros: Feed reads are O(1) — just read the pre-built list.
- Cons: For celebrities (1M+ followers), a single post triggers 1M Redis writes → spike, latency, failure cascade.
- Good for: users with < ~10K followers.

**Fan-out on read (pull model):**
- Don't pre-build feeds. On feed load, fetch posts from all followed users and merge.
- Pros: No fan-out cost on write. Simple.
- Cons: Feed load is O(number_of_following) — at 1,000 follows, must fetch 1,000 users' recent posts and sort. Very slow.
- Good for: celebrity accounts (they write rarely, millions read).

**Hybrid (the correct answer):**
```
On post creation:
  if author.follower_count < 10,000:
    → fan-out on write (push post_id to each follower's Redis feed)
  else (celebrity):
    → skip fan-out; just store the post in the celebrity's post history

On feed load:
  1. Load pre-built feed from Redis (post_ids from followed non-celebrities)
  2. For each celebrity the user follows: fetch their latest N posts from Posts DB
  3. Merge (sort by timestamp or rank score)
  4. Return top 20

Edge case: if a non-celebrity gains followers rapidly, threshold recalculation runs async.
```

### 6b. Feed Ranking

Simple ranking formula (no ML required in interviews):
```
rank_score = (1.0 / (age_in_hours + 2)^1.5) * engagement_weight * relationship_weight

where:
  age_in_hours     = now - post.created_at (in hours)
  engagement_weight = 1 + log(1 + like_count + comment_count * 2)
  relationship_weight = 1.5 if user interacted with author recently, else 1.0
```

In practice, compute this score when the feed is assembled. For a basic interview, "sort by timestamp and boost recent highly-liked posts" is sufficient.

### 6c. Pagination — Cursor-based (not offset)

**Why not offset?** `OFFSET 20` works today, but if 5 new posts are inserted while the user scrolls, the 21st post they see might be a duplicate (offset has shifted). Cursor-based avoids this.

**Cursor design:**
```
cursor = base64_encode({ post_id: "abc123", created_at: "2024-01-15T10:30:00Z" })

On next page load:
  GET /v1/feed?cursor=<encoded>
  → Decode cursor → SELECT ... WHERE created_at < cursor.created_at
                                  OR (created_at = cursor.created_at AND post_id < cursor.post_id)
                    ORDER BY created_at DESC, post_id DESC
                    LIMIT 20
```

The cursor is opaque to the client — they just pass it back to get the next page.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Celebrity fan-out spike:**
- A celebrity with 10M followers posts → 10M Redis writes in seconds → memory pressure + latency spike.
- Hybrid model (celebrity = fan-out on read) prevents this entirely.
- Even with hybrid: celebrity feed merging on read adds ~10-50ms per celebrity followed. Cache celebrity's recent posts separately (Redis sorted set keyed by celebrity_id, score = created_at timestamp, TTL 60s).

**Feed freshness for inactive users:**
- If a user hasn't opened the app in 30 days, their Redis feed is cold.
- On their first login: trigger async feed rebuild; show a "loading your feed" state.
- Alternatively, don't pre-build feeds for users inactive > 7 days (save Redis memory).

**Like count consistency:**
- Naive: `UPDATE posts SET like_count = like_count + 1` → row-level lock contention on popular posts.
- Better: accept approximate counts. Write likes to a Redis counter (`INCR like:{post_id}`), periodically sync to PostgreSQL (every minute or N likes).

**Trade-offs:**
- Fan-out on write: fast reads, slow writes for high-follower authors. Right for most users.
- Fan-out on read: slow reads, fast writes. Right for celebrities.
- Pre-computed feeds in Redis vs on-the-fly DB queries: Redis is 100x faster for feed load; the pre-computation cost is small (~12K writes/sec), worth it.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: DAU, follower limits, ranking, media.
3-6 min:  Estimation: 12K fan-out writes/sec, 29K feed reads/sec, 80GB feed cache.
6-12 min: Architecture. Two critical paths: post creation (fan-out) and feed read (Redis lookup + celebrity merge).
12-18 min: Data model. Posts, follows, likes, Redis list for feed cache.
18-28 min: DEEP DIVE: Fan-out on write vs read. Explain the celebrity problem. Walk the hybrid model. This is the crux of the design.
28-35 min: Cursor-based pagination. Why offset breaks on live feeds.
35-40 min: Feed ranking formula (brief). Like count approximate counting via Redis.
40-43 min: Failure modes: Redis eviction, celebrity spike.
43-45 min: Questions.
```

## Resources

**Free:**
- [System Design Primer — social network](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo — news feed design](https://www.youtube.com/results?search_query=bytebytego+news+feed+design+fan+out)
- [Hello Interview — social media feed](https://www.hellointerview.com)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a News Feed System
- [ByteByteGo](https://bytebytego.com)

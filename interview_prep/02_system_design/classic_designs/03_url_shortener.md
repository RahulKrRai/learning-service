# URL Shortener / Pastebin

> Appears at: Google L5, Amazon L6, Atlassian, banks (warm-up). Classic first design question — tests system thinking end-to-end without domain complexity. Do it confidently and fast (~30 min), leaving time for depth on key generation.

## 1. Requirements

**Functional:**
- Create a short URL for a long URL → `logw.rd/abc123`
- Redirect: GET short URL → 301/302 redirect to original URL
- Optional: custom aliases (`logw.rd/mylink`)
- Optional: expiry (short URL expires after N days)
- Optional: analytics (click count, geo, referrer)
- Optional: QR code generation

**Non-functional:**
- 100M URLs created per day (write heavy for creation period; very read-heavy after)
- Read:write ratio = 100:1 (most traffic is redirects, not new link creation)
- Redirects < 10ms p99 (critical UX)
- URL must remain valid for at least 5 years
- No collisions (two different long URLs must not get the same short code)

**Clarifying questions:**
1. "What's the max short code length?" → 7 characters (allows 62^7 = 3.5 trillion unique codes — more than enough).
2. "Are custom aliases required?" → Nice to have; keep in scope but don't over-engineer.
3. "Should we support analytics?" → Basic click count is fine; real-time geo/referrer is out of scope.

## 2. Back-of-Envelope Estimation

```
Writes (new URLs):    100M/day = 1,160/sec avg = ~3,500/sec peak
Reads (redirects):    10B/day = 115,700/sec avg = ~350,000/sec peak

URL record size:      short_code (7B) + long_url (2KB) + metadata (100B) ≈ 2.2 KB
Storage (5 years):    100M × 365 × 5 × 2.2KB ≈ 400TB

Short code space:     base62 (a-z A-Z 0-9): 62^7 = 3.5 trillion → ~7,000 years at 100M/day

Redirect latency:     Must be cached → in-memory cache hit < 1ms
Cache storage:        Top 20% of URLs handle 80% of traffic (Pareto)
                      20% × 100M active = 20M URLs × 2.2KB = 44GB → fits in Redis
```

## 3. API Design

```
# Create short URL
POST /api/v1/urls
Body: { long_url: "https://...", custom_alias: "mylink" (optional), expires_in_days: 30 (optional) }
Auth: API key in header
→ 201 { short_url: "https://logw.rd/abc123", short_code: "abc123", expires_at: "..." }

# Redirect (the primary read path)
GET /{short_code}
→ 301 Moved Permanently  (browser caches → fastest for static URLs)
   Location: https://long-url-here.com/...
   OR
→ 302 Found              (browser does NOT cache → needed if URL can change or for analytics)

# Delete
DELETE /api/v1/urls/{short_code}
→ 204 No Content

# Analytics (optional)
GET /api/v1/urls/{short_code}/stats
→ { short_code, clicks: 12345, created_at, expires_at }
```

**301 vs 302:**
- **301 Permanent:** Browser caches the redirect → subsequent requests go directly to the destination without hitting our servers. Good for CDN caching and reducing load. Bad if you want accurate click analytics (cached requests bypass our system).
- **302 Temporary:** Browser does not cache → every click goes through our system. Necessary for analytics. Use 302 if click counting matters.

## 4. High-Level Architecture

```
Browser
  │
  │ GET /abc123
  ▼
┌──────────────────────┐
│  CDN / Edge Cache    │  ← serves most redirects from cache (< 5ms globally)
│  (CloudFront, etc.)  │
└──────────┬───────────┘
           │ cache miss
           ▼
┌──────────────────────┐
│  Load Balancer       │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌────────┐  ...  API Servers (stateless, horizontally scaled)
│ API 1  │  │ API 2  │
└────┬───┘  └────────┘
     │
     ├──► Redis Cache (hot URL lookups: short_code → long_url)
     │
     └──► PostgreSQL (source of truth: all URL mappings)
              │
              └──► Analytics DB (ClickHouse/BigQuery)
                   (async write via Kafka on each redirect)

Key Generator Service (separate):
  - Pre-generates a pool of unique short codes
  - API servers claim codes from the pool (Redis SET)
  - Refills pool async to avoid blocking on creation
```

## 5. Data Model

```sql
-- URL mappings (PostgreSQL)
CREATE TABLE urls (
  short_code    VARCHAR(10) PRIMARY KEY,   -- e.g. "abc123X"
  long_url      TEXT NOT NULL,
  created_by    UUID,                       -- user/API key
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at    TIMESTAMPTZ,               -- NULL = never expires
  click_count   BIGINT DEFAULT 0           -- approximate (real counts in analytics DB)
);
CREATE INDEX idx_urls_long ON urls(MD5(long_url));  -- lookup by long URL to deduplicate

-- Pre-generated codes pool (Redis)
-- SET: "code_pool" → { "abc123X", "qwerty1", ... } (SRANDMEMBER to claim one)
-- SADD to replenish, SPOP to claim

-- Redirect analytics (Kafka → ClickHouse)
-- event: { short_code, timestamp, ip, user_agent, referrer, geo_country }
```

## 6. Deep Dives

### 6a. Key Generation — Counter+Base62 vs Hash

**Approach 1: Hash (MD5/SHA256 + first 7 chars):**
```python
import hashlib

def generate_code(long_url: str) -> str:
    hash_val = hashlib.md5(long_url.encode()).hexdigest()
    return hash_val[:7]  # take first 7 hex chars... wait, not base62

# Better: take first 7 chars of base62-encoded hash
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def to_base62(n: int) -> str:
    result = []
    while n:
        result.append(BASE62[n % 62])
        n //= 62
    return ''.join(reversed(result)).zfill(7)[:7]

def short_code_from_url(long_url: str) -> str:
    n = int(hashlib.md5(long_url.encode()).hexdigest(), 16)
    return to_base62(n)
```

Problems: collisions (different URLs → same first 7 chars of MD5), same URL always maps to same code (no per-user custom links), collision resolution requires retrying with a different hash or appending salt.

**Approach 2: Auto-increment counter + base62 (recommended):**
```python
# Global counter (in DB or a dedicated counter service like Snowflake ID)
# On each URL creation:
new_id = get_and_increment_global_counter()  # e.g. 12345678
short_code = to_base62(new_id)              # → "W7Xa2"

# No collisions (counters are unique by definition)
# Sequential → somewhat guessable, but not a security concern for URL shorteners
# Can use Snowflake IDs (distributed, monotonic) for multi-region
```

**Counter service (distributed):**
- Option A: DB sequence (`SERIAL` in PostgreSQL). Simple but single point of write.
- Option B: Pre-allocated ranges — each API server gets a range (e.g. server 1: IDs 1-1000; server 2: 1001-2000). No coordination needed within the range. Lose up to 999 IDs on crash (acceptable).
- Option C: Snowflake IDs — 64-bit: [timestamp][datacenter][worker][sequence]. Globally unique, no central counter.

**Pre-generation pool (the Interview favorite answer):**
A Key Generator Service pre-generates N codes, stores them in a Redis SET. On URL creation, an API server claims a code with `SPOP`. A background job refills the pool when it drops below threshold. Benefits: creation is O(1), no coordination, no collision.

### 6b. Collision Handling

With counter+base62: no collisions (counters are unique). This is why counter beats hash.

With hash: detect collision by checking DB (`SELECT * FROM urls WHERE short_code = ?`). If collision, append a random character and retry. Keep retrying until a unique code is found. Usually resolves in 1-2 retries.

### 6c. Read-Heavy Scaling

**Cache-aside with Redis:**
```
On redirect request for /abc123:
  1. Check Redis: GET "url:abc123"
     → cache hit: return 302 to cached long_url. Done.
     → cache miss: continue.
  2. SELECT long_url FROM urls WHERE short_code = 'abc123'
     → not found: return 404
     → found: SET "url:abc123" long_url EX 86400 (24h TTL)
              return 302 to long_url
```

**CDN caching:** For 301 (permanent redirect) responses, the CDN caches the redirect at edge locations globally. A user in Mumbai gets the redirect from a Mumbai edge node — no round trip to origin. Reduces origin load by 90%+ for popular URLs.

**Read replicas:** Write to PostgreSQL primary; read from N read replicas. Scales read QPS linearly.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x (1B URLs created/day):**
- PostgreSQL with 4TB of data — add read replicas + shard by `hash(short_code) % N`.
- Redis cache: 440GB needed → Redis Cluster.
- Key Generator: Snowflake IDs for distributed uniqueness.
- CDN: fronts 95% of redirect traffic.

**Expiry cleanup:** A scheduled job (daily cron) runs `DELETE FROM urls WHERE expires_at < NOW()`. For very large tables, use range partition by `created_at` and drop whole partitions.

**Custom alias collisions:** User requests alias "google" — already taken. Return 409 Conflict. Maintain a reserved-words list (admin, api, www, etc.) in application code.

**Failure modes:**
- Redis down: all requests fall through to PostgreSQL. Latency increases from ~1ms to ~10ms; manageable but DB load spikes. Mitigation: read replicas absorb load.
- DB down: reads fail. Mitigation: CDN-cached 301 redirects still work for popular URLs (cached at browser and CDN).
- Key Generator down: URL creation fails. Read path (redirects) unaffected. Pre-generated pool in Redis continues working until depleted.

## 8. Talk Track (30-35 min — this is a faster design)

```
0-2 min:  Clarify: short code length (7 chars), analytics scope, custom aliases, 301 vs 302.
2-4 min:  Estimation: 115K reads/sec, top 20% URLs → 44GB cache.
4-8 min:  Architecture. Two paths: write (create link) and read (redirect). CDN for read path.
8-12 min: Data model. Simple — short_code PK, long_url, expires_at.
12-20 min: DEEP DIVE: Key generation. Hash approach (explain problems) → counter+base62 → pre-generation pool (the clean answer).
20-25 min: Read scaling: Redis cache + CDN. 301 vs 302 trade-off.
25-30 min: Analytics: 302 + async Kafka event on each redirect. ClickHouse for aggregation.
30-33 min: Expiry, custom aliases, collision handling.
33-35 min: Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [NeetCode — URL Shortener system design](https://www.youtube.com/results?search_query=neetcode+url+shortener+system+design)
- [ByteByteGo — URL shortener](https://www.youtube.com/results?search_query=bytebytego+url+shortener)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a URL Shortening Service

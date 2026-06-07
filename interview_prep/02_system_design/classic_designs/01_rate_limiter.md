# Rate Limiter

> Appears at: Google L5, Amazon L6, Confluent, Uber. A canonical warm-up design. Tests: algorithm knowledge, distributed systems thinking, Redis fluency.

## 1. Requirements

**Functional:**
- Limit requests from a client to N requests per window (e.g. 100 req/min per user)
- Return HTTP 429 with `Retry-After` header when limit exceeded
- Support different limits per user tier (free: 60/min, pro: 1000/min, enterprise: 10000/min)
- Configurable per-endpoint (e.g. /login stricter than /feed)

**Non-functional:**
- Add < 5ms latency to each request
- Accurate to within ~1% (a few extra requests slipping through is acceptable)
- Handle 100,000 req/sec across 10M active users
- Distributed: same user hitting different API servers must share the same counter

**Clarifying questions:**
1. "Is this client-side, server-side (API gateway), or both?" → Server-side, at the API gateway layer.
2. "Hard limit (exactly N requests, no burst) or soft limit (allow bursts up to 2x for short periods)?" → Soft — token bucket is fine.
3. "What's the consistency requirement for the counter? Can a user occasionally send N+2 requests due to race conditions?" → Yes, a small overage is acceptable.

## 2. Back-of-Envelope Estimation

```
Active users:            10M (but only ~1M concurrent in peak hour)
Request rate:            100,000 req/sec
Redis counter ops:       1 per request → 100,000 Redis ops/sec
                         Redis single instance handles ~100K-1M ops/sec → fine

Counter storage per user: 16 bytes (user_id) + 8 bytes (count) + 8 bytes (TTL) ≈ 32 bytes
Total storage:           10M users × 32B = 320MB → trivial for Redis
```

## 3. API Design

```
# All requests pass through the rate limiter middleware — no explicit API.
# Rate limiter adds response headers:

200 OK (within limit):
  X-RateLimit-Limit:     1000
  X-RateLimit-Remaining: 742
  X-RateLimit-Reset:     1700000060  (Unix timestamp when window resets)

429 Too Many Requests:
  X-RateLimit-Limit:     1000
  X-RateLimit-Remaining: 0
  Retry-After:           42  (seconds until window resets)
  Body: { "error": "rate_limit_exceeded", "retry_after": 42 }
```

## 4. High-Level Architecture

```
Client
  │
  ▼
┌────────────────────────────────────────────┐
│  API Gateway                                │
│  ┌──────────────────────────────────────┐  │
│  │  Rate Limiter Middleware              │  │
│  │  1. Extract client key (user_id/IP)  │  │
│  │  2. Look up rate limit rule          │  │
│  │  3. CHECK + INCR counter in Redis    │  │
│  │  4. Allow or 429                     │  │
│  └──────────────────────────────────────┘  │
└────────────────────┬───────────────────────┘
                     │
              ┌──────▼──────┐
              │  Redis       │
              │  (counters)  │
              └─────────────┘
                     │
              ┌──────▼──────┐
              │  Rate Limit  │
              │  Rules Store │
              │  (Redis/DB)  │
              └─────────────┘

Multiple API servers all hit the SAME Redis instance → shared counter
```

## 5. Data Model

```
# Redis key design:
rate_limit:{algorithm}:{user_id}:{window_start}

# Fixed window:
Key: "rl:fw:{user_id}:{minute_bucket}"   e.g. "rl:fw:u123:28350420"
Value: integer count
TTL: 60s

# Sliding window counter:
Key: "rl:sw:{user_id}"
Value: hash { window_bucket: count }  (current and previous minute)
TTL: 120s

# Token bucket:
Key: "rl:tb:{user_id}"
Value: hash { tokens: float, last_refill: timestamp }
TTL: 3600s (or user session length)

# Rate limit rules (Redis hash or DB):
Key: "rl:rules:{tier}"   → { max_requests: 1000, window_seconds: 60 }
```

## 6. Deep Dives

### 6a. Algorithm Comparison

**Fixed Window Counter:**
```
On each request:
  key = "rl:{user}:{floor(now / window_size)}"
  count = INCR key
  if count == 1: EXPIRE key window_size
  return count <= limit
```
- Simple. But boundary problem: user can send 2×limit in 2 seconds (N at end of window + N at start of next).
- Best for: simple cases, low-precision requirements.

**Sliding Window Log:**
```
On each request:
  key = "rl:{user}:log"
  ZREMRANGEBYSCORE key 0 (now - window_size)   # remove old entries
  count = ZCARD key
  if count < limit:
    ZADD key now now_nanoseconds               # add current timestamp
    return ALLOW
  else:
    return DENY
```
- Perfectly accurate. Memory-intensive: stores every request timestamp. At 1,000 req/min per user, each entry is ~8 bytes → 8KB/user → 80GB for 10M users. Not scalable.
- Best for: low-volume APIs where accuracy is critical.

**Sliding Window Counter (recommended — best balance):**
```
On each request:
  current_window = floor(now / window_size)
  prev_window = current_window - 1
  elapsed_fraction = (now % window_size) / window_size

  current_count = GET "rl:{user}:{current_window}"
  prev_count = GET "rl:{user}:{prev_window}"
  estimated_count = prev_count * (1 - elapsed_fraction) + current_count

  if estimated_count >= limit: return DENY
  INCR "rl:{user}:{current_window}"
  EXPIRE "rl:{user}:{current_window}" window_size * 2
  return ALLOW
```
- Memory-efficient (only 2 counters per user). Approximates sliding window. Accurate to ~0.1%.
- Best for: production rate limiters (Cloudflare, Kong, Nginx use variants of this).

**Token Bucket:**
```
bucket has capacity C tokens, refills at rate R tokens/sec
On each request:
  tokens_to_add = (now - last_refill) * R
  current_tokens = min(C, stored_tokens + tokens_to_add)
  last_refill = now
  if current_tokens >= 1:
    current_tokens -= 1
    store and return ALLOW
  else:
    return DENY
```
- Allows bursts (up to bucket capacity). Smooth over time.
- Requires atomic read-modify-write → must use Lua script in Redis to avoid race conditions.
- Best for: APIs where short bursts are acceptable (API gateway).

### 6b. Distributed Rate Limiting with Redis

**Race condition problem:**
```
# NOT atomic — race condition between CHECK and INCR:
count = GET key
if count < limit:
    INCR key    # another request may have incremented between GET and INCR!
```

**Fix: Lua script (atomic in Redis):**
```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local count = redis.call('INCR', key)
if count == 1 then
    redis.call('EXPIRE', key, ttl)
end
if count > limit then
    return 0  -- denied
else
    return 1  -- allowed
end
```
`EVAL` executes this atomically on the Redis server — no race condition.

**Redis Cluster:** If one Redis instance can't handle the load, shard by `hash(user_id) % N` across a Redis Cluster. Same user always hits the same shard → counter accuracy maintained.

### 6c. Per-Tier and Per-Endpoint Limits

```python
def get_limit(user_id: str, endpoint: str) -> tuple[int, int]:
    """Returns (max_requests, window_seconds)"""
    tier = get_user_tier(user_id)  # cached locally
    endpoint_override = endpoint_limits.get(endpoint)  # e.g. /login → 5/min always
    if endpoint_override:
        return endpoint_override
    tier_limits = {
        "free": (60, 60),
        "pro": (1000, 60),
        "enterprise": (10000, 60),
    }
    return tier_limits.get(tier, (60, 60))
```

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x (1M req/sec):**
- Redis handles 100K-1M ops/sec per instance. At 1M req/sec → Redis Cluster with 5-10 shards.
- Minimize round trips: use Lua script to do INCR + EXPIRE in one RTT (< 1ms local DC).
- Local cache for rate limit rules (user tier), refreshed every 60s — avoids Redis lookup per request for the limit value.

**Redis down:**
- Option A: Fail open (allow all requests). Bad for DoS protection but good for availability.
- Option B: Fail closed (deny all requests). Good for security but breaks all API traffic.
- Option C: Fallback to in-process counter (approximate, no cross-instance sharing). Usually right choice.
- Always fail gracefully — choose your failure mode explicitly.

**Trade-offs:**
- Accuracy vs simplicity: sliding window counter is ~99.9% accurate and O(1) per request. Worth the complexity over fixed window.
- Hard vs soft limit: hard limit (exact) requires synchronous Redis + atomic operations; soft limit allows a small overage in exchange for lower latency (can check locally before Redis call).
- Single Redis vs per-region Redis: global rate limiting requires cross-region coordination (higher latency). Per-region limits are simpler but a user can exceed global limit by spreading requests across regions.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: client-side vs server-side? Hard vs soft limit? User-level vs IP-level?
3-5 min:  Estimation: 100K req/sec, Redis handles this easily. Storage: 320MB.
5-10 min: Architecture: API gateway middleware → Redis.
10-15 min: Walk through 4 algorithms: fixed window (simple, boundary problem) → log (accurate, memory problem) → sliding counter (best balance) → token bucket (burst-friendly).
15-25 min: DEEP DIVE: Sliding window counter implementation. Race condition → Lua script. Walk the exact Redis commands.
25-32 min: Distributed rate limiting with Redis Cluster. Per-tier rules. Per-endpoint overrides.
32-37 min: Failure modes: Redis down → fail open vs closed vs local fallback.
37-42 min: 10x scale: Redis Cluster, minimize round trips, local rule cache.
42-45 min: Open for questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo — rate limiting](https://www.youtube.com/results?search_query=bytebytego+rate+limiter+design)
- [Cloudflare blog — sliding window rate limiting](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Redis documentation — EVAL/Lua scripting](https://redis.io/docs/manual/programmability/eval-intro/)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a Rate Limiter
- [ByteByteGo](https://bytebytego.com)

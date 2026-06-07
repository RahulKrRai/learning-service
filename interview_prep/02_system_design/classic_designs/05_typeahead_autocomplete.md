# Typeahead / Search Autocomplete
> Appears at Google (Search, Maps), Amazon (product search), Uber (destination input). Often paired with "design Google Search" or given standalone as a 45-min deep dive.

## 1. Requirements

### Functional
- As a user types a query prefix, return the top-K (default K=5) ranked suggestions in <100 ms.
- Suggestions ranked by global popularity (search frequency) blended with personalization weight and recency.
- Support for multiple locales/languages.
- Near-real-time update for trending topics (e.g., a celebrity name spikes in the last 30 min).

### Non-Functional
- P99 suggestion latency < 100 ms end-to-end.
- Availability 99.99% (search box is revenue-critical).
- Read-heavy: suggestions read : index write ratio ≈ 10,000 : 1.
- Scale to ~10B prefix lookups/day (Google-scale) or ~1B/day (Amazon/Uber scale).

### Clarifying Questions to Ask
1. "Should suggestions be personalized per user, or purely global popularity?" — determines whether you need a per-user layer on top of the global trie.
2. "How fresh must trending topics be — seconds, minutes, or is a daily rebuild acceptable?" — drives batch vs streaming update architecture.
3. "Do we need to support prefix queries mid-word (substring match), or only leading-prefix?" — substring requires a different index (suffix tree or inverted index); leading-prefix = trie.

---

## 2. Back-of-Envelope Estimation

**Scale assumption:** 500 M DAU, average 5 searches/day, average query length 15 chars → user types ~8 chars before selecting → ~8 prefix requests per search.

```
QPS (reads):
  500M DAU × 5 searches/day × 8 keystrokes = 20B requests/day
  20B / 86,400 ≈ 230,000 RPS peak (assume 3x peak factor → ~700K RPS)

Trie size (in-memory):
  English: ~100K popular queries, avg length 20 chars
  Nodes: 100K queries × 20 chars = ~2M nodes
  Per node: 26 child pointers (8B each) + top-K list (5 × 20B) + frequency (8B) ≈ ~400B
  Total: 2M × 400B ≈ 800 MB per full trie replica — fits in RAM on a single host

Shard count (read path):
  ~700K RPS / 10K RPS per node = ~70 nodes for the read tier
  Trie fits in RAM → each shard holds a full or partial copy

Bandwidth:
  Each response: 5 suggestions × 50 bytes = 250 B
  700K RPS × 250 B ≈ 175 MB/s egress — trivial
```

---

## 3. API Design

### Suggestion endpoint (client-facing)
```
GET /v1/autocomplete?q=<prefix>&limit=5&locale=en-US&uid=<user_id>

Response 200 OK:
{
  "prefix": "star",
  "suggestions": [
    { "text": "starbucks near me",  "score": 9821.4 },
    { "text": "star wars",          "score": 8742.1 },
    { "text": "stardew valley",     "score": 7100.0 },
    { "text": "star trek",          "score": 6543.2 },
    { "text": "starlink",           "score": 4201.9 }
  ],
  "latency_ms": 12
}
```

### Aggregation ingestion (internal, write path)
```
POST /internal/v1/ingest-query
Body: { "query": "starbucks near me", "timestamp": 1700000000, "uid": "u123" }
```

### Index rebuild trigger (ops)
```
POST /internal/v1/rebuild-trie
Body: { "shard": 2, "snapshot_s3_uri": "s3://trie-snapshots/2024-01-15/shard-2.bin" }
```

---

## 4. High-Level Architecture

```
Client (browser/mobile)
       |
       | HTTPS (debounced, fires after 100ms idle)
       v
   [CDN / Edge Cache]  <-- popular prefixes cached at edge (Redis/Memcached at PoP)
       | cache miss
       v
   [API Gateway / Load Balancer]
       |
   +---+---+
   |       |
   v       v
[Suggestion Service cluster — stateless]
   |
   +---> [Trie Service cluster — stateful, sharded by first 2 chars]
   |           (in-memory trie per shard, top-K stored at each node)
   |
   +---> [Personalization Service] (optional, blends user history)
              |
              v
         [User Profile Store — Redis]

Write / Update path:
   Raw queries --> [Kafka topic: raw-queries]
                        |
              +---------+---------+
              |                   |
   [Batch aggregator]    [Streaming aggregator (Flink/Spark)]
   (runs daily,         (5-min tumbling window,
    full trie rebuild)   updates top-K for trending)
              |                   |
              v                   v
      [S3: trie snapshots]   [Delta updates API --> Trie Service]
              |
   [Trie loader: on startup or daily rebuild]
```

**Flow:** The client debounces keystrokes and fires a request to the nearest CDN PoP. Popular prefixes (top ~10K globally) are cached at the edge with a short TTL (1–5 min). Cache misses route to the stateless Suggestion Service, which fans out to the appropriate Trie Service shard, optionally blends personalization, and returns top-K in <20 ms from the trie.

---

## 5. Data Model

### Trie node (in-memory, per shard)
```
TrieNode {
  children:  map[char]→*TrieNode   // 26 slots or hashmap for unicode
  top_k:     []Suggestion          // top-K (K=10-20) pre-sorted by score
  is_end:    bool
}

Suggestion {
  text:       string
  global_freq: float64             // rolling 30-day count, log-scaled
  freshness:  float64              // exponential decay: e^(-λ·age_hours)
  score:      float64              // global_freq × freshness
}
```

### Persistent store (for rebuild and audit)
```sql
-- PostgreSQL / BigQuery
CREATE TABLE query_counts (
  query        TEXT        PRIMARY KEY,
  count_30d    BIGINT,
  count_7d     BIGINT,
  count_1d     BIGINT,
  last_seen_at TIMESTAMPTZ,
  updated_at   TIMESTAMPTZ
);
-- Partitioned by hash(query) for parallel rebuild jobs
```

### Trie snapshot (S3)
```
s3://trie-snapshots/YYYY-MM-DD/shard-{prefix_hash}.bin
Serialization: Protobuf (compact) or flatbuffers (zero-copy mmap on load)
Size: ~100 MB/shard compressed
```

**Partitioning key:** First 2 characters of the prefix determine the shard (26×26 = 676 buckets, mapped to N physical shards). This ensures all queries for a prefix land on the same shard — no scatter-gather for prefix lookups.

---

## 6. Deep Dives

### 6a. Trie at Scale — Why a Trie Beats a Sorted List

A **sorted list** of (query, score) pairs supports prefix queries via binary search in O(log N) time, but returning all matches requires a scan until the prefix no longer matches — O(K + matches) per lookup, and "matches" can be huge. A **trie** does it in O(|prefix|) to reach the prefix node, then O(1) to read the pre-computed top-K stored at that node — regardless of how many total queries share that prefix.

**Top-K per node — stored vs computed:**
- **Store top-K at every node:** On insert/update, propagate the new score up the ancestor chain, evicting the lowest scorer if the node's top-K list is full. Read is O(|prefix|). Write is O(|prefix| × K) — acceptable for batch builds, slightly costly for real-time updates.
- **Compute dynamically at query time:** DFS from the prefix node, heap-collect top-K. O(total nodes in subtree) — too slow for a trie with millions of nodes under a common prefix like "a".
- **Decision:** Store top-K at every node. Cap K at 10–20 internally; return 5 to the client. On batch rebuild, build bottom-up so child scores bubble up naturally.

**Sharding:**
- **By first 2 chars:** Deterministic, no hot-spot detection needed. "st" → shard 7. Downside: uneven distribution ("s", "a", "t" are much more common than "qx"). Mitigate by splitting hot shards ("st" → two shards).
- **By prefix length:** Puts very short prefixes (high fan-out) on dedicated nodes. Rarely used in practice.
- **Consistent hashing:** Flexible rebalancing but requires scatter-gather if a prefix could live on multiple nodes. Avoid for tries — use static first-2-char assignment.
- **Recommendation:** First-2-char sharding with manual hot-shard splitting. Each shard stores a full sub-trie for its key space.

**Serialization:** Use Protobuf or flatbuffers for snapshots. On node startup, mmap the snapshot file — zero-copy load in <1s for a 100 MB shard. The in-memory trie is pointer-linked; rebuild from snapshot into the live pointer structure takes ~5s, done in a background goroutine while the old trie serves traffic.

### 6b. Weighted Suggestions, Freshness, and Real-Time Updates

**Scoring formula:**
```
score(query, t) = log(global_count_30d + 1)
               × freshness_factor(t)
               × personalization_boost(uid, query)

freshness_factor(t) = α + (1-α) × e^(-λ × age_hours)
  α = 0.2 (floor so old queries don't disappear)
  λ = 0.1 (half-life ≈ 7 hours for trending decay)
```

**Real-time updates for trending:**
- Raw query events flow into Kafka (`raw-queries` topic, partitioned by `hash(query)`).
- A Flink job runs a 5-minute tumbling window, counts queries, and emits a delta update for any query whose count increased by >10× compared to its 30-day baseline.
- Delta updates are pushed to the Trie Service via a gRPC stream: `UpdateTopK(prefix, suggestion, new_score)`.
- The Trie Service re-evaluates the top-K list at each ancestor node affected by the update. With top-K stored at each node, this is O(|query| × K) per update.
- Full rebuild still runs nightly to recompute 30-day rolling counts from the data warehouse.

**CDN / Edge Cache Invalidation:**
- Popular prefixes (top 10K) are cached at CDN edge with TTL=60s.
- On a trending spike, push a cache purge for affected prefixes via CDN API (Cloudflare/Fastly instant purge).
- For less-critical freshness, simply let TTL expire — 60s staleness is acceptable for most prefixes.

---

## 7. Bottlenecks, Failure Modes & Trade-offs

| Concern | Risk | Mitigation |
|---|---|---|
| Single hot prefix ("a", "s") | One shard overwhelmed | Read replicas per shard; most-popular sub-prefixes cached at CDN |
| Trie shard restart / rebuild | Cold start takes 5–10s | Blue-green deployment: bring up new instance, warm it, then shift traffic |
| Trending query delays | Flink lag → stale suggestions | Reduce window to 1 min; accept slightly higher compute cost |
| Personalization latency | Adds ~10–20 ms round-trip | Async fetch; return global results immediately, patch with personalized if received within 50 ms |
| Trie memory growth | New queries added indefinitely | Cap trie at top-500K queries by 30d count; evict tail |
| Write amplification in trie | Every update touches O(|query|) nodes | Batch updates; coalesce delta updates per prefix before applying |
| Cache stampede on invalidation | Burst of misses after purge | Use probabilistic early expiry (jitter TTL ±10%); singleflight at suggestion service layer |

**Key trade-off:** Storing top-K at every node costs 10–20× more memory vs computing at query time, but eliminates O(subtree) fan-out at read time. At 700K RPS, memory is cheap; latency is not.

---

## 8. Talk Track (35–45 Min)

```
00:00–03:00  Clarify: global vs personalized? freshness SLA? prefix-only?
03:00–08:00  Estimation: 700K RPS read, 800 MB trie in RAM, shard count
08:00–14:00  High-level diagram: CDN → Suggestion Service → Trie Service (sharded)
             Write path: Kafka → Flink → delta updates + nightly rebuild
14:00–20:00  Deep dive 1 — Trie internals
             - Why trie > sorted list for prefix
             - Top-K stored at each node, bubble-up on insert
             - Sharding by first-2-chars, hot-shard splitting
             - Snapshot serialization (Protobuf), mmap load, blue-green swap
20:00–28:00  Deep dive 2 — Weighted scoring & real-time trending
             - Score formula (log frequency × freshness × personalization)
             - Flink 5-min window for delta updates
             - CDN cache for top-10K prefixes, instant purge on spike
28:00–34:00  Data model: TrieNode, query_counts table, S3 snapshot layout
34:00–40:00  Failure modes: hot shard, cold start, stampede
             Trade-offs: memory vs latency, batch vs streaming freshness
40:00–45:00  Extension: multi-language support (separate trie per locale),
             spell correction (BK-tree layered on top), CTR-based ranking
```

---

## Resources

### Free
- System Design Primer — https://github.com/donnemartin/system-design-primer (search "autocomplete")
- ByteByteGo YouTube — https://www.youtube.com/results?search_query=bytebytego+typeahead+autocomplete
- Hello Interview — https://www.hellointerview.com (search "typeahead")

### Paid
- ByteByteGo book/site — https://bytebytego.com (Chapter: "Design a Search Autocomplete System")
- DesignGurus — https://www.designgurus.io (Grokking the System Design Interview: "Typeahead Suggestion")

# Distributed Cache (Redis-like)

> Appears at: Google L5, Amazon L6, Uber. Foundational design that often comes up as a sub-component in larger designs. Tests: consistent hashing, eviction, replication, hot-key handling.

## 1. Requirements

**Functional:**
- Get(key) → value; Set(key, value, ttl); Delete(key)
- TTL-based expiry
- Support eviction when memory is full (LRU or LFU)
- Optional: pub/sub for cache invalidation notifications

**Non-functional:**
- < 1ms p99 read latency
- 99.99% availability
- Scale to 10TB total cached data across a cluster
- Handle 1M ops/sec read + 100K ops/sec write
- Survive node failures without data loss (replication)

**Clarifying questions:**
1. "Is this read-through (cache fetches from DB on miss) or cache-aside (app fetches on miss)?" → Cache-aside — the app handles misses.
2. "Do we need persistence (survive full cluster restart) or is in-memory-only fine?" → Persistence is optional; prioritize speed.
3. "Strong or eventual consistency across replicas?" → Eventual is fine for cache use cases.

## 2. Back-of-Envelope Estimation

```
Total data:           10 TB
Node memory:          256 GB per node
Nodes needed:         10TB / 256GB ≈ 40 nodes (+ replication factor 2 → 80 nodes)

Read QPS:             1M/sec total → 1M / 40 nodes = 25K reads/node/sec (Redis handles 100K+/node)
Write QPS:            100K/sec total

Average value size:   10KB
Average key size:     64 bytes
Keys stored:          10TB / 10KB = 1 billion keys

Network:              1M reads × 10KB = 10GB/sec outbound (big — need CDN for cacheable static data)
```

## 3. API Design

```
# Client SDK API (TCP or RESP protocol)

GET key                         → value | nil
SET key value [EX seconds]      → OK
MGET key1 key2 ... keyN         → [value1, value2, ..., valueN]  # batch read
MSET key1 val1 key2 val2        → OK                              # batch write
DEL key                         → integer (number deleted)
EXPIRE key seconds              → 1 (success) | 0 (key not found)
TTL key                         → seconds remaining | -1 (no TTL) | -2 (key not found)
INCR key                        → new integer value (atomic)

# Pub/sub for cache invalidation
PUBLISH channel message
SUBSCRIBE channel
```

## 4. High-Level Architecture

```
Clients
  │
  ▼
┌─────────────────────────────────────────────┐
│  Client Library (consistent hash router)     │
│  - Maps key → node using consistent hashing  │
│  - Handles retry on node failure             │
│  - Optional: local L1 cache (process-level)  │
└──────────┬──────────────────────────────────┘
           │  routes to specific node
           ▼
┌──────────┬──────────┬──────────┬──────────┐
│  Node 0  │  Node 1  │  Node 2  │  Node N  │   ← Cache Cluster
│  (leader)│  (leader)│  (leader)│          │
│  + replica│ + replica│ + replica│          │
└──────────┴──────────┴──────────┴──────────┘

Each node: in-memory hash map + eviction structure (LRU list or LFU freq buckets)
Replication: async leader→replica within each shard pair

Cluster Manager (separate service):
  - Tracks node health (heartbeat)
  - Updates ring on node join/leave
  - Handles failover promotion
```

## 5. Data Model

```
Internal data structure per node:
  hash_map: key → { value, ttl_expiry, last_access_time, access_count }
  lru_list: doubly-linked list (MRU at head, LRU at tail)
  lfu_freq_buckets: min-heap of {frequency, key} pairs

Key routing:
  consistent_hash_ring: sorted list of (virtual_node_token, server_id)
  virtual_nodes_per_server: 150 (reduces imbalance)

Replication:
  Primary: accepts reads + writes
  Replica: accepts reads (optional), async replication from primary
  Replication log: append-only command log (like Redis AOF)
```

## 6. Deep Dives

### 6a. Consistent Hashing

**Why not modular hashing?** With N nodes, `key % N` routes requests. If you add or remove a node, N changes and almost ALL keys map to different nodes → massive cache miss storm (thundering herd). Bad.

**Consistent hashing:** Place both nodes and keys on a hash ring (0 to 2^32). A key routes to the next node clockwise. Adding/removing a node only remaps the keys in one arc of the ring → only ~1/N keys are remapped. Cache miss storm is contained.

**Virtual nodes:** Each physical node is placed at 150 random positions on the ring (virtual nodes). This ensures even distribution even with heterogeneous node sizes and reduces the impact of adding/removing a single node.

```python
import hashlib
from sortedcontainers import SortedList

class ConsistentHashRing:
    def __init__(self, vnodes=150):
        self.vnodes = vnodes
        self.ring = SortedList()        # (hash_value, server_id)
        self.nodes = {}                 # hash_value → server_id

    def add_node(self, server_id: str):
        for i in range(self.vnodes):
            h = self._hash(f"{server_id}:{i}")
            self.ring.add((h, server_id))
            self.nodes[h] = server_id

    def remove_node(self, server_id: str):
        for i in range(self.vnodes):
            h = self._hash(f"{server_id}:{i}")
            self.ring.remove((h, server_id))
            del self.nodes[h]

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise Exception("Ring is empty")
        h = self._hash(key)
        idx = self.ring.bisect_left((h,))
        if idx == len(self.ring):
            idx = 0  # wrap around
        return self.ring[idx][1]

    def _hash(self, s: str) -> int:
        return int(hashlib.md5(s.encode()).hexdigest(), 16)
```

### 6b. LRU Eviction — O(1) Implementation

When memory is full, evict the least recently used key.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()  # key → value, maintains insertion order

    def get(self, key: str):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)  # mark as most recently used
        return self.cache[key]

    def put(self, key: str, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict LRU (first item)
```

Internally: `OrderedDict` is a doubly-linked list + hashmap → O(1) get, put, evict.

### 6c. Hot Keys / Celebrity Problem

A single key (e.g. Justin Bieber's profile, a viral tweet, a Black Friday product) receives millions of reads/sec — far exceeding a single node's capacity.

**Solutions:**
1. **Local L1 cache in the client:** Each app instance keeps an in-process LRU cache (e.g. 1000 entries, 1s TTL). Popular keys are served locally without hitting Redis at all.
2. **Read replicas for hot keys:** Detect hot keys by monitoring key access counts (node reports keys with > 10K hits/min). Route reads for those keys to N additional read replicas (temporary extra nodes). Trade-off: eventual consistency (< 1s lag).
3. **Request coalescing:** When a hot key expires, multiple app instances simultaneously try to regenerate it from the DB — thundering herd. Solution: one process acquires a lock and refreshes the cache; others wait and use a stale value or a short wait. Redis `SETNX` can implement the lock.
4. **Key splitting:** Append a random suffix `key:{rand(1,N)}` to spread hot key reads across N nodes. Writes go to all N shards; reads go to one random shard. Trade-off: write amplification.

### 6d. Cache Invalidation Strategies

| Strategy | How | Consistency | Complexity |
|----------|-----|-------------|------------|
| TTL | Set expiry on write | Eventual (stale up to TTL) | Simple |
| Write-through | On DB write, also update cache | Strong | Medium |
| Write-around | Write to DB only; cache on next read | Eventual | Simple |
| Write-back | Write to cache; async flush to DB | Risk of data loss | Complex |
| Event-driven | DB change → pub/sub → invalidate | Near-real-time | Medium |

**Event-driven invalidation with Redis pub/sub:**
```
DB write → service publishes "INVALIDATE:{key}" to Redis channel
→ all app instances subscribed to that channel call DEL(key)
→ next read → cache miss → fresh load from DB → re-cached
```

## 7. Bottlenecks, Failure Modes & Trade-offs

**Node failure:**
- Primary fails → Cluster Manager detects (heartbeat timeout ~5s) → promotes replica → updates ring.
- During 5s window: reads to the failed node fail or fall back to secondary.
- Async replication means replica may be slightly behind → RPO > 0 (acceptable for cache).

**Network partition:**
- If a node is partitioned from the ring but still reachable by some clients → stale reads.
- Cluster Manager uses quorum to determine if a node is truly dead before promoting replica.

**Memory pressure:**
- When a node is evicting heavily, consider: increasing node memory, adding nodes, tightening TTLs, or caching less.
- Alert on eviction rate > threshold — high eviction = low cache hit rate = DB pressure.

**Trade-offs:**
- Consistent hashing vs rendezvous hashing: both are good; consistent hashing is more widely understood in interviews.
- LRU vs LFU: LRU is simpler and usually better. LFU is better when some items are frequently accessed but not recently (e.g. a static reference dataset). Redis uses a probabilistic approximation of LRU (samples 5-10 keys and evicts the LRU among the sample).
- Async vs sync replication: async replication means potential data loss on primary crash; sync replication (wait for replica ACK) means higher write latency. For a cache, async is always the right choice — cache data can be rebuilt from the DB.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: read-through vs cache-aside? Persistence? Consistency model?
3-5 min:  Estimation: 40 nodes, 1M ops/sec easily handled.
5-10 min: Architecture: Client library with consistent hash ring → node cluster. Replication per node.
10-18 min: DEEP DIVE: Consistent hashing. Draw the ring. Explain virtual nodes. Walk the code.
18-25 min: Eviction: LRU (OrderedDict — O(1)). Compare LFU briefly.
25-32 min: Hot keys: L1 local cache, read replicas, request coalescing. This is where depth shows.
32-38 min: Cache invalidation: TTL vs event-driven. Trade-offs.
38-43 min: Failures: node down → replica promotion. Memory pressure → eviction monitoring.
43-45 min: Open for questions.
```

## Resources

**Free:**
- [System Design Primer — caching](https://github.com/donnemartin/system-design-primer#cache)
- [ByteByteGo — cache design](https://www.youtube.com/results?search_query=bytebytego+distributed+cache+design)
- [Redis documentation — data types and eviction](https://redis.io/docs/management/config/#maxmemory-policy)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a Key-Value Store
- [ByteByteGo](https://bytebytego.com)

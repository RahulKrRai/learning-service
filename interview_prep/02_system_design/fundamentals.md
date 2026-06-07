# System Design Fundamentals — Building Blocks Reference

---

## Load Balancing

**What:** Distribute incoming requests across multiple servers so no single server is a bottleneck.

**L4 (transport layer):** Routes based on IP/TCP — fast, doesn't inspect payload. Used for raw throughput (e.g. AWS NLB).

**L7 (application layer):** Routes based on HTTP headers, URL path, cookies — can do path-based routing, sticky sessions, SSL termination. Slightly more overhead. Used for most web services (e.g. AWS ALB, Nginx, HAProxy).

**Algorithms:** Round-robin (simple), least-connections (smart for variable request times), IP hash (sticky sessions without shared state), weighted round-robin (heterogeneous server fleet).

**Trade-off:** Sticky sessions enable stateful servers but create uneven load; stateless servers + shared session store (Redis) are preferred for horizontal scaling.

---

## Caching

**What:** Store frequently-read data closer to the reader to reduce latency and DB load.

### Cache Placement
- **Client-side cache:** Browser cache, mobile app cache. Low latency, but hard to invalidate.
- **CDN:** Edge cache for static assets and cacheable API responses. Reduces cross-region latency.
- **Application-level cache:** In-process (e.g. Python dict with TTL). Fast but not shared across instances.
- **Distributed cache:** Redis/Memcached. Shared across instances. Survives instance restarts (Redis with AOF).

### Write Strategies
- **Write-through:** Write to cache AND DB synchronously. High consistency, higher write latency.
- **Write-back (write-behind):** Write to cache, async flush to DB. Low write latency, risk of data loss.
- **Write-around:** Write directly to DB, skip cache. Cache populated on next read. Good for write-heavy, rarely-re-read data.

### Eviction Policies
- **LRU (Least Recently Used):** Evict the entry not accessed longest. Implemented with a doubly-linked list + hashmap. O(1) get/put.
- **LFU (Least Frequently Used):** Evict the entry accessed fewest times. Better for skewed access patterns. More complex.
- **TTL (Time-To-Live):** Expire entries after a fixed duration. Simplest for data that gets stale.

### Cache Invalidation
- **TTL:** Let it expire. Simple, accepts eventual consistency. Stale window = TTL.
- **Event-driven:** Publish a cache-invalidation event when the DB record changes. More complex but tighter consistency.
- **Cache-aside (lazy loading):** App reads cache; on miss, reads DB and populates cache. Simple and widely used.

**Hot keys / celebrity problem:** A single key (e.g. a viral post) gets overwhelming reads. Solutions: local replica in app memory, read replicas for that key, request coalescing (only one request hits the DB; others wait and share the result).

---

## Sharding / Partitioning

**What:** Split data across multiple DB nodes so no single node holds all data.

**Horizontal sharding (most common):** Split rows across nodes by a shard key (e.g. `user_id % N`).

**Vertical partitioning:** Split columns — put hot columns in one table, cold columns in another. Reduces row size on hot path.

**Shard key choice:** Aim for even distribution and co-locate related queries. `user_id` is often good (user's data stays on one shard). `timestamp` is bad (all new writes hit one shard — hotspot).

**Consistent hashing:** Map both nodes and keys onto a ring. A key routes to the next node clockwise. Adding/removing a node only remaps 1/N keys — far better than modular hashing which remaps all keys.

**Trade-offs:** Sharding complicates cross-shard queries (JOINs become fan-out + merge), cross-shard transactions (use sagas or two-phase commit), and re-sharding when you grow. Delay sharding as long as possible; start with read replicas and vertical scaling.

---

## Replication

**What:** Copy data to multiple nodes for durability and read scaling.

**Leader-follower (primary-replica):** Leader handles all writes; followers replicate asynchronously (or synchronously for sync replication). Reads can go to followers (eventually consistent) or leader (strong consistent).

**Sync vs async replication:**
- Sync: leader waits for follower ACK before returning to client. Durability guaranteed; higher write latency; leader blocked if follower is slow.
- Async: leader returns immediately; follower catches up eventually. Lower latency; risk of data loss on leader crash (RPO > 0).

**Multi-leader (active-active):** Multiple nodes accept writes. Good for multi-region writes. Conflict resolution is complex (last-write-wins, CRDTs, custom logic).

**Leaderless (e.g. Cassandra):** Client writes to a quorum of nodes. No single leader. High availability; tuneable consistency via quorum (R + W > N for strong consistency).

---

## SQL vs NoSQL

| | SQL (PostgreSQL, MySQL) | NoSQL |
|---|---|---|
| Schema | Rigid, enforced | Flexible, per-document |
| Transactions | ACID, multi-row | Often single-row atomic; multi-doc via 2PC or app logic |
| Joins | Native | Application-side or denormalized |
| Scaling | Vertical + read replicas; sharding is harder | Designed for horizontal scale |
| Consistency | Strong by default | Tunable (eventual to strong) |
| Use when | Complex queries, ACID required, relational data | High write throughput, flexible schema, horizontal scale |

**Default to PostgreSQL** unless you have a specific reason not to (schema flexibility, massive horizontal write scale, time-series, graph). PostgreSQL handles more than people think at scale.

---

## CAP Theorem & Consistency Models

**CAP:** A distributed system can guarantee at most two of: Consistency (every read sees the latest write), Availability (every request gets a response), Partition tolerance (the system works despite network splits). Since partition tolerance is non-negotiable in distributed systems, you choose between CA and CP.

**CP systems:** Sacrifice availability during a partition to ensure consistency (e.g. HBase, ZooKeeper). Used when stale data is unacceptable (financial ledgers, inventory counts).

**AP systems:** Sacrifice consistency during a partition to remain available (e.g. Cassandra, DynamoDB). Used when availability is critical and some staleness is acceptable (shopping carts, social feeds, DNS).

**PACELC:** Extends CAP — even without partitions, there's a latency vs consistency trade-off. Low-latency systems use async replication (accepting staleness); high-consistency systems use sync replication (accepting latency).

### Consistency Models (weakest to strongest)
- **Eventual consistency:** All replicas converge eventually. Read may be stale. (Cassandra default, DNS)
- **Monotonic read consistency:** Once you've seen a value, you won't see an older value. (Good for user sessions)
- **Read-your-writes:** You always see your own writes. (Critical for profile updates)
- **Causal consistency:** Related operations are seen in order. (Chat messages)
- **Strong consistency:** Every read sees the most recent write. (Financial transactions)

---

## Message Queues & Streaming (Kafka — your home turf)

### Core concepts

**Topic → Partition → Offset:** A topic has N partitions. Each partition is an ordered, immutable log. Each message has an offset. Consumers track their offset to resume after restart.

**Partitions = unit of parallelism AND ordering:** Messages within a partition are ordered. Messages across partitions are not. Partition count limits max consumer parallelism in a consumer group.

**Replication & ISR (In-Sync Replicas):** Each partition has a leader + N-1 followers. ISR = the set of replicas that are caught up to the leader. `acks=all` means the leader waits for all ISR replicas to acknowledge before returning success. `min.insync.replicas=2` means at least 2 replicas must be in ISR for writes to succeed (prevents data loss on leader crash).

**Consumer groups:** Consumers in the same group share partitions — each partition is consumed by exactly one consumer in the group. Different groups get independent copies of all messages (fan-out via multiple consumer groups).

**Offset commit:** Auto-commit (at-most-once or at-least-once depending on timing) vs manual commit after processing (at-least-once). Exactly-once requires the transactional API.

**Exactly-once semantics (EOS):**
1. Idempotent producer (`enable.idempotence=true`): deduplicates retries on the broker side (sequence numbers per partition).
2. Transactional producer: atomic write across multiple partitions. Combined with `read_committed` consumer isolation, gives end-to-end EOS.

**Log compaction:** For changelog topics (key-value stores). Instead of TTL-based retention, compaction retains only the latest message per key. Old values get garbage-collected. Used by Kafka Streams, KSQL, and the Schema Registry.

**Producer tuning:** `linger.ms` (wait before sending to batch more messages), `batch.size` (max bytes per batch), compression (`lz4` for throughput, `snappy` for balanced, `zstd` for best ratio). Higher linger = higher throughput, higher latency.

**Consumer lag:** `consumer_lag = latest_offset - committed_offset` per partition. Monitor this. If lag grows: scale consumers (up to partition count), increase processing throughput, increase partitions (requires rebalance), or add priority lanes.

**Schema Registry:** Avro/Protobuf schemas stored centrally. Producers serialize with a schema; consumers deserialize knowing the schema. Compatibility modes: BACKWARD (new schema can read old data), FORWARD (old schema can read new data), FULL (both). Prevents breaking changes from crashing consumers.

**When to use Kafka vs a simple queue (SQS/RabbitMQ):**
- Kafka: when you need replay, multiple independent consumers, event sourcing, stream processing, or high throughput (millions/sec).
- SQS/RabbitMQ: when you need simple work queue semantics, TTL-based messages, and don't need replay.

---

## Idempotency & Exactly-Once vs At-Least-Once

**Idempotency:** An operation that produces the same result whether applied once or N times. Critical for retries in distributed systems.

**At-least-once + idempotent consumer:** The simpler, preferred pattern. The sender retries on timeout/error; the receiver deduplicates using an idempotency key (e.g. `payment_id` in the DB with a UNIQUE constraint). If the second attempt arrives, the DB rejects the duplicate — outcome is correct.

**Exactly-once:** The sender and receiver coordinate to ensure exactly one delivery. Complex (requires distributed transactions or EOS in Kafka). Often not worth the complexity — prefer at-least-once + idempotency.

**Idempotency key design:** Use the business operation ID (e.g. `order_id`, `payment_request_id`), not a random UUID per attempt. Persist it in the DB. TTL the deduplication store after the retry window closes.

---

## Change Data Capture (CDC) & Outbox Pattern

**CDC:** Capture every row-level change in the DB (INSERT/UPDATE/DELETE) and stream them to consumers. Implemented via DB transaction log (Debezium reads PostgreSQL WAL). Use cases: cache invalidation, search index sync, event sourcing, audit log.

**Outbox pattern:** Instead of publishing to Kafka directly from your service (which can fail if Kafka is down after DB commit — dual-write problem), write the message to an `outbox` table in the same DB transaction as your business record. A CDC process (Debezium) reads the outbox table and publishes to Kafka. Guarantees exactly-once delivery from DB to Kafka.

```
Transaction:
  INSERT INTO orders (id, ...) VALUES (...)
  INSERT INTO outbox (event_type, payload) VALUES ('ORDER_CREATED', {...})
→ CDC reads outbox → publishes to Kafka → marks outbox row as published
```

---

## Rate Limiting

**Token bucket:** Tokens fill at a fixed rate; each request consumes a token. Allows bursts up to bucket size. Widely used.

**Leaky bucket:** Requests enter a queue and are processed at a fixed rate. Smooths bursts. Used for traffic shaping.

**Sliding window log:** Track timestamps of each request in the last window. Exact but memory-intensive.

**Sliding window counter:** Hybrid — count requests in current and previous window, weight by elapsed time fraction. Approximate but memory-efficient. Usually the right choice.

**Distributed rate limiting:** Store the counter in Redis. Use INCR + EXPIRE (not atomic — race condition possible) or a Lua script (atomic). Redis cluster requires careful key routing to avoid hotspots.

---

## Consensus: Raft & Paxos (high level)

Used for leader election and replicated state machines (e.g. ZooKeeper/etcd use Paxos/Raft).

**Raft (simpler, preferred):** Nodes elect a leader by requesting votes; a node wins if it gets majority votes. Leader handles all writes; followers replicate. On leader crash, a new election occurs. Used by etcd, CockroachDB, TiKV.

**Paxos:** Older, theoretically equivalent but harder to understand and implement correctly. Most modern systems prefer Raft.

**When you need it:** Distributed lock acquisition, leader election for distributed job scheduler, cluster membership management.

---

## CDNs

**What:** A network of geographically distributed servers that cache static and cacheable dynamic content close to users.

**Use cases:** Static assets (JS/CSS/images), large media files, API responses with high cache-hit rates, DDoS absorption.

**Push vs pull:** Pull CDN (most common) — CDN fetches from origin on first miss, caches until TTL. Push CDN — you upload assets to CDN proactively. Pull is simpler; push is better for large infrequently-changing files.

**Cache invalidation:** TTL + explicit invalidation API (expensive, use sparingly). Use content-addressed filenames (e.g. `app.abc123.js`) so new deploys naturally bypass cache.

---

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Confluent Kafka documentation](https://docs.confluent.io)
- [Designing Data-Intensive Applications (summary)](https://www.youtube.com/results?search_query=designing+data+intensive+applications+summary)

**Paid (optional):**
- "Designing Data-Intensive Applications" by Martin Kleppmann — the definitive reference
- [ByteByteGo](https://bytebytego.com)

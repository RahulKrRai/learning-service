# Framework & Estimation Cheat Sheet

## The 8-Step Interview Framework

```
1. CLARIFY (3 min)
   - "Before I dive in, let me make sure I understand the scope."
   - Ask: scale (users/QPS), consistency requirements, read vs write ratio,
     geographic distribution, mobile vs web, real-time vs batch.
   - State your assumptions out loud.

2. ESTIMATE (3 min)
   - QPS (read + write), storage (5 yr), bandwidth (inbound + outbound).
   - Say the arithmetic out loud. Round aggressively.
   - Flag if read-heavy (cache-first) or write-heavy (sharding-first).

3. API DESIGN (4 min)
   - Key endpoints only — not every field.
   - REST or RPC — state which and why briefly.
   - Request/response sketch is enough.

4. HIGH-LEVEL ARCHITECTURE (8 min)
   - Draw the boxes: clients → LB → API servers → DB/cache/queue.
   - Walk the request flow out loud for the primary use case.
   - Name your tech choices (PostgreSQL not "a database") and say why briefly.

5. DATA MODEL (5 min)
   - Key tables/collections, important columns, data types.
   - Partitioning key — say why (user_id for even distribution, not timestamp).
   - Indexes you'd add.

6. DEEP DIVES (15 min)
   - Pick 1-2 hardest components. Wait for the interviewer to guide if unsure.
   - This is where L5 candidates separate from L4: name the trade-off explicitly,
     not just the solution.

7. BOTTLENECKS & TRADE-OFFS (5 min)
   - What breaks at 10x load? Where is the first bottleneck?
   - Name your CAP choice: did you pick availability over consistency? Why?
   - Async vs sync, push vs pull, exactly-once vs at-least-once.

8. FAILURE MODES (2 min)
   - What fails? DB goes down, queue fills, a service crashes.
   - How do you detect it (metrics/alerts)? How do you recover (retry/circuit-breaker/fallback)?
```

---

## Powers of 2

| Unit | Bytes | Approx |
|------|-------|--------|
| 1 KB | 1,024 | ~10³ |
| 1 MB | 1,048,576 | ~10⁶ |
| 1 GB | 1,073,741,824 | ~10⁹ |
| 1 TB | ~10¹² | |
| 1 PB | ~10¹⁵ | |

---

## Latency Numbers Every Engineer Should Know

| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 25 ns |
| Main memory (RAM) reference | 100 ns |
| Compress 1KB with Snappy | 3,000 ns (3 µs) |
| Send 2KB over 1 Gbps network | 20,000 ns (20 µs) |
| SSD random read | 150,000 ns (150 µs) |
| Read 1MB sequentially from memory | 250,000 ns (250 µs) |
| Round trip within same datacenter | 500,000 ns (0.5 ms) |
| Read 1MB sequentially from SSD | 1,000,000 ns (1 ms) |
| HDD seek | 10,000,000 ns (10 ms) |
| Read 1MB sequentially from HDD | 20,000,000 ns (20 ms) |
| Send packet CA → Netherlands → CA | 150,000,000 ns (150 ms) |

**Key takeaways:**
- Memory is 200x faster than SSD; SSD is 80x faster than HDD.
- Cross-datacenter round trip = 150ms. Design with this in mind.
- Network within a datacenter = 0.5ms. Async calls within a DC are cheap.

---

## QPS / Storage / Bandwidth Formulas

### QPS from DAU

```
QPS = (DAU × requests_per_user_per_day) / 86,400
Peak QPS ≈ QPS × 2-3 (account for traffic spikes)

Example:
  50M DAU, 10 reads/day each
  → Read QPS = (50M × 10) / 86,400 = 5,787 ≈ 6,000/s
  → Peak read QPS ≈ 18,000/s
```

### Storage from write rate

```
Storage per year = writes_per_second × record_size × 86,400 × 365

Example:
  1,000 writes/sec, avg record = 1KB
  → 1,000 × 1KB × 86,400 × 365 = 31.5 TB/year
  → 5-year storage = ~160 TB
```

### Bandwidth

```
Inbound bandwidth = writes_per_second × avg_write_size
Outbound bandwidth = reads_per_second × avg_response_size

Example (Twitter-like):
  5,000 writes/s × 280 bytes = 1.4 MB/s inbound
  50,000 reads/s × 5KB (tweet + metadata) = 250 MB/s outbound
```

---

## Common Capacity Assumptions

| Item | Rough size |
|------|-----------|
| Tweet / short text | 280 bytes |
| User record (without photo) | 1 KB |
| Average webpage | 200 KB |
| Profile photo (compressed) | 200 KB |
| HD photo | 2-5 MB |
| 1-min compressed video | 6 MB |
| Average API response (JSON) | 1-10 KB |
| Kafka message | 1-100 KB |
| Redis key-value entry | ~100 bytes overhead + value |

---

## Design Checklist (use in every interview)

```
□ Stated the scale (QPS/storage) before drawing anything
□ Named my primary DB and why (SQL vs NoSQL; which specific one)
□ Chose a partitioning key and said why
□ Identified the read/write ratio and let it drive caching decisions
□ Named the consistency model (strong/eventual/causal) and why I chose it
□ Addressed idempotency for any write operation that can be retried
□ Mentioned how I'd handle a component going down
□ Named at least one explicit trade-off (CAP, push vs pull, async vs sync)
□ Said what I'd monitor (key metrics / SLOs)
□ Left time for the interviewer's deep-dive questions
```

---

## Resources

**Free:**
- [System Design Primer — capacity estimation](https://github.com/donnemartin/system-design-primer#system-design-topics-start-here)
- [ByteByteGo back-of-envelope estimation](https://www.youtube.com/results?search_query=bytebytego+back+of+envelope+estimation)

**Paid (optional):**
- "System Design Interview" by Alex Xu (ByteByteGo) — chapters 1-2 cover estimation and framework

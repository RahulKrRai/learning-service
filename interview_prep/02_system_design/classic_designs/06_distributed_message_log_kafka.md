# Distributed Message Log (Kafka-style)
> THE design for Confluent interviews. Also appears at Google (Pub/Sub internals), Amazon (Kinesis), Uber (real-time data pipelines), Atlassian. Rahul — this is your home turf. Be authoritative and go deep.

## 1. Requirements

### Functional
- Producers publish records to named topics; consumers read records in order.
- Topics are divided into partitions; each partition is an ordered, append-only log.
- Consumer groups: multiple consumers in a group cooperatively consume a topic (each partition assigned to exactly one consumer in the group).
- Records retained for a configurable duration (time-based or size-based) or compacted for changelog semantics.
- At-least-once delivery by default; exactly-once semantics (EOS) available via idempotent producer + transactions.
- Replication: each partition has one leader and N-1 followers; reads and writes go to the leader.

### Non-Functional
- Throughput: millions of messages/sec per broker (commodity hardware).
- Durability: no data loss on broker failure if `acks=all` and `min.insync.replicas ≥ 2`.
- Low latency: <5 ms p99 for produce (with `linger.ms=0`); consumer lag < 1s under normal conditions.
- Horizontal scalability: add brokers, reassign partitions, no downtime.
- Availability: 99.99% (partition leader failover in <30s).

### Clarifying Questions to Ask
1. "What delivery guarantee do producers need — fire-and-forget (`acks=0`), leader-ack (`acks=1`), or all-ISR-ack (`acks=all`)?" — determines durability vs latency trade-off.
2. "Do any consumers need exactly-once end-to-end semantics, or is at-least-once + idempotent consumers sufficient?" — EOS adds transactional overhead.
3. "What is the expected message size and retention period?" — drives storage tiering decisions and whether log compaction is needed.

---

## 2. Back-of-Envelope Estimation

**Scale assumption:** 10,000 producer clients, 1 M messages/sec ingestion, average message 1 KB, 7-day retention, replication factor 3.

```
Ingestion throughput:
  1M msg/sec × 1 KB = 1 GB/s raw write to leaders
  With RF=3: 3 GB/s total disk write across the cluster

Storage (7-day retention):
  1 GB/s × 86,400 s/day × 7 days = 604 TB raw
  With RF=3: ~1.8 PB total — use ~50 brokers × 36 TB NVMe each

Broker count (throughput):
  Assume 200 MB/s sustainable write per broker (sequential I/O)
  1 GB/s / 200 MB/s = 5 leader brokers minimum
  With RF=3 follower replication: ~15 brokers for replication traffic
  Add headroom: 30–50 brokers

Partitions:
  Rule of thumb: partitions = max(target_throughput / throughput_per_partition, consumer_parallelism)
  Throughput per partition: ~10 MB/s sequential write
  1 GB/s / 10 MB/s = 100 partitions minimum
  If you have 50 consumers: max(100, 50) = 100 partitions across the topic

Consumer lag budget:
  At 1M msg/sec, 1s of lag = 1M buffered messages = 1 GB in flight
```

---

## 3. API Design

### Producer API (Kafka client library — not HTTP)
```
// Produce a record
ProduceResult produce(
  topic:     string,
  key:       bytes,       // used for partition assignment: hash(key) % N
  value:     bytes,
  headers:   map[string]string,
  acks:      enum { 0, 1, ALL },
  timeout_ms: int
) -> { partition: int, offset: long, timestamp: long }

// Transactional produce (EOS)
beginTransaction()
produce(...)
produce(...)
commitTransaction()   // atomic across partitions
abortTransaction()
```

### Consumer API
```
// Subscribe and poll
subscribe(topics: []string, group_id: string)
records = poll(timeout_ms: int) -> []ConsumerRecord {
  topic, partition, offset, key, value, timestamp
}
commitSync()    // commit current offsets synchronously
commitAsync(callback)

// Manual partition assignment (no rebalance)
assign(partitions: []TopicPartition)
seek(partition: TopicPartition, offset: long)
```

### Admin API (internal / ops)
```
createTopic(name, num_partitions, replication_factor, configs)
deleteTopic(name)
alterPartitionCount(topic, new_count)   // can only increase
describeConsumerGroup(group_id) -> { lag_per_partition, member_assignments }
```

---

## 4. High-Level Architecture

```
Producers
  |  (batched, compressed records)
  v
+--------------------------------------------------+
|              Kafka Cluster                       |
|                                                  |
|  [Broker 1]        [Broker 2]        [Broker 3]  |
|  Partition 0-L     Partition 1-L     Partition 2-L|
|  Partition 1-F     Partition 2-F     Partition 0-F|
|  Partition 2-F     Partition 0-F     Partition 1-F|
|    (L=Leader, F=Follower)                        |
|                                                  |
|  Each partition = append-only segment files      |
|  on local disk (sequential I/O, page cache)      |
+--------------------------------------------------+
         |                    |
         | metadata / leader  | ZooKeeper (legacy)
         | election           | or KRaft controller quorum
         v                    v
  [Controller Broker]   [KRaft Quorum / ZooKeeper]
  (manages partition    (stores cluster metadata:
   leadership, ISR)      leader epochs, ISR lists)

Consumer Groups
  [Consumer A] [Consumer B] [Consumer C]
  Partition 0   Partition 1   Partition 2
  (each consumer owns ≥1 partition; commits offsets
   to __consumer_offsets internal topic)

Schema Registry (Confluent)
  [Schema Registry Service]
  - Stores Avro/Protobuf schemas
  - Producers/consumers look up schema by ID
  - Wire format: [magic byte][4-byte schema_id][payload]
```

**Flow:** Producers send batched, optionally compressed records to the partition leader broker. The leader appends to its local log, then replicates to follower brokers. Once all in-sync replicas (ISR) acknowledge (if `acks=all`), the produce request is confirmed. Consumers poll the leader (or follower with `fetch.from.replica` in KIP-392) and commit offsets to the `__consumer_offsets` topic. The Controller manages partition leadership using KRaft (or ZooKeeper in legacy deployments).

---

## 5. Data Model

### On-Disk Log Segment (per partition)
```
Partition directory: /kafka-logs/my-topic-0/
  00000000000000000000.log      // segment file: raw record batches
  00000000000000000000.index    // sparse offset index: offset→file_position
  00000000000000000000.timeindex// time→offset index (for time-based seek)
  00000000001234567890.log      // next segment (rolled after segment.bytes)

Record Batch (wire format):
  baseOffset          : int64
  batchLength         : int32
  magic               : int8   (2 = current)
  crc                 : int32
  attributes          : int16  (compression codec, timestamp type, EOS flags)
  lastOffsetDelta     : int32
  baseTimestamp       : int64
  maxTimestamp        : int64
  producerId          : int64  (idempotency)
  producerEpoch       : int16
  baseSequence        : int32
  records[]           : Record (key, value, headers, offset delta, timestamp delta)
```

### __consumer_offsets topic (internal)
```
Key:   GroupId + TopicPartition  (binary encoded)
Value: OffsetAndMetadata { committed_offset, metadata_string, commit_timestamp }
Compacted topic — only the latest offset per (group, partition) is retained.
```

### Cluster Metadata (KRaft — stored in __cluster_metadata topic)
```
Records:
  TopicRecord      { topic_id, name }
  PartitionRecord  { topic_id, partition_id, leader_id, isr[], leader_epoch }
  BrokerRecord     { broker_id, host, port, rack }
  ProducerIdsRecord{ next_producer_id_block }
```

**Partitioning key:** `hash(record.key) % num_partitions` — ensures all records with the same key land on the same partition, preserving per-key ordering. If key is null, round-robin (sticky partitioner in modern clients: fills a batch before switching).

---

## 6. Deep Dives

### 6a. Replication, ISR, and Durability Guarantees

**ISR (In-Sync Replicas):** A follower is "in-sync" if it has fetched up to the leader's log end offset within `replica.lag.time.max.ms` (default 30s). If a follower falls behind — due to slow disk, GC pause, or network hiccup — the controller removes it from the ISR. The leader tracks the **high-water mark (HWM)**: the highest offset that all ISR members have replicated. Consumers can only read up to the HWM — this is the committed/stable read boundary.

**`acks` settings:**
| acks | Durability | Latency |
|------|-----------|---------|
| 0 | Fire-and-forget; data loss on leader crash | ~0 ms |
| 1 | Leader written; loss if leader crashes before followers replicate | ~1–5 ms |
| all | All ISR members written; no loss if ≥1 ISR member survives | ~5–20 ms |

**`min.insync.replicas` (min.isr):** If `acks=all` and the number of ISR members drops below `min.isr`, the leader rejects produce requests with `NotEnoughReplicasException`. This is the safety brake: `min.isr=2` with RF=3 means you can lose one broker and still accept writes; you cannot lose two.

**Practical guidance:** Always set `acks=all`, `min.insync.replicas=2`, `replication.factor=3` for production topics. This gives you durability against single-broker failures with a small latency cost.

**What happens when a follower falls behind:**
1. Follower fetch lag exceeds `replica.lag.time.max.ms` → Controller removes it from ISR.
2. Leader continues accepting writes (ISR = remaining replicas).
3. Fallen follower catches up by fetching from the leader's log → Controller re-adds it to ISR once it reaches the HWM.
4. If the leader crashes while the follower is out of ISR, the follower becomes leader with a truncated log — records after its last fetched offset are lost (unless `acks=all` was used, in which case those records were never confirmed to the producer).

### 6b. Leader Election — ZooKeeper → KRaft

**Legacy (ZooKeeper):** Each broker registers an ephemeral znode. The **Controller** broker watches for broker failures and runs leader election for affected partitions. Controller itself is elected via ZooKeeper lock (`/controller` znode). Problems: ZooKeeper is a separate system to operate; controller has all metadata in memory (doesn't scale past ~200K partitions); failover of the controller requires a full metadata reload.

**KRaft (KIP-500, GA in Kafka 3.3+):** Eliminates ZooKeeper. A quorum of **controller nodes** (typically 3 or 5, separate from broker nodes or co-located) runs Raft consensus on the `__cluster_metadata` topic. The active controller is the Raft leader. Partition leadership changes are recorded as log records in `__cluster_metadata`, replicated via Raft. Brokers act as Raft followers for metadata only.

**Partition leader election flow (KRaft):**
1. Broker heartbeat timeout detected by the active KRaft controller.
2. Controller selects new leader from ISR (first in ISR list by convention, or preferred replica if in ISR).
3. Controller writes a `PartitionChangeRecord` to `__cluster_metadata` log.
4. New leader begins accepting produce/fetch requests.
5. Old leader (if it comes back) sees its epoch is stale → fences itself.

**Leader epoch:** Every leadership change increments the epoch. Clients attach the expected epoch to requests; a stale leader rejects requests with `NotLeaderOrFollower`, forcing the client to refresh metadata.

### 6c. Consumer Groups, Offsets, and Rebalancing

**Offset commit — auto vs manual:**
- `enable.auto.commit=true` (default): consumer library commits offsets every `auto.commit.interval.ms` (5s). Risk: a crash after poll but before processing commits the offset → **message loss** from the consumer's perspective (skipped messages).
- Manual `commitSync()` after processing: guarantees at-least-once (if you crash after processing but before commit, you reprocess on restart). This is correct for most workloads.
- Manual with `commitAsync()`: higher throughput (no blocking), but on failure the async callback must retry carefully to avoid committing a stale offset that skips later records.

**`__consumer_offsets` internals:** An internal Kafka topic with 50 partitions (default). Each consumer group maps to a partition via `hash(group_id) % 50`. The **Group Coordinator** broker (whichever broker owns that partition's leadership) manages the group. Offset commits are produce requests to this topic; the compaction policy ensures only the latest offset per (group, partition) is retained.

**Rebalance (consumer joins/leaves/crashes):**
1. Group Coordinator detects change (heartbeat timeout or JoinGroup request).
2. All consumers in the group are notified via heartbeat response.
3. Each consumer calls `JoinGroup` → Coordinator elects a **Group Leader** (first to join).
4. Group Leader runs the partition assignment strategy (range, round-robin, sticky).
5. Coordinator distributes assignment via `SyncGroup`.
6. **Stop-the-world rebalance:** all consumers stop consuming during rebalance. Mitigate with **Cooperative Sticky Assignor** (KIP-429): only partitions being moved are revoked; others continue consuming.

### 6d. Exactly-Once Semantics (EOS)

EOS in Kafka is achieved via two complementary mechanisms:

**1. Idempotent Producer (KIP-98):**
- Broker assigns a `producerId` + `epoch` to each producer on initialization.
- Each produce request carries a `sequence_number` (per partition, monotonically increasing).
- Broker deduplicates retries: if it receives a record with a sequence number it already applied, it silently drops the duplicate and returns success.
- Guarantees: **no duplicates on retry** within a single producer session. Does NOT survive producer restart (new producerId issued).

**2. Transactional API:**
- Producer calls `initTransactions()` with a `transactional.id` (stable across restarts).
- Producer fences previous zombie instances: if a new producer with the same `transactional.id` starts, the broker bumps the epoch, fencing old producers (any in-flight produce from old epoch is rejected).
- `commitTransaction()` writes a **transaction marker** (COMMIT or ABORT) to each partition that received records in the transaction. This is an atomic 2-phase commit coordinated by the **Transaction Coordinator** (a special broker role, backed by the `__transaction_state` topic).
- Consumers with `isolation.level=read_committed` skip records from aborted transactions and records without a COMMIT marker yet (they are "uncommitted").

**What EOS actually guarantees:**
- Produce side: each logical record appears **exactly once** in the log, even on producer retries and restarts.
- Consume-process-produce pattern (Kafka Streams): if consuming from topic A, processing, and producing to topic B, the entire operation is atomic — either both the offset commit and the produced record are committed, or neither is. This is the **consume-transform-produce** EOS pattern.
- EOS does NOT help if your consumer writes to an external system (e.g., a database) — that requires an idempotent external write or distributed transaction (2PC with the external system).

**EOS overhead:** ~3–5% throughput reduction due to transaction coordination. Acceptable for most use cases.

### 6e. Log Compaction

**Time-based retention:** Segments older than `retention.ms` are deleted. Simple, predictable storage use. All history is eventually lost.

**Size-based retention:** Delete oldest segments when total partition size exceeds `retention.bytes`. Good for bounding storage cost regardless of time.

**Log compaction (`cleanup.policy=compact`):** The cleaner thread periodically rewrites log segments, retaining only the **latest record per key**. Records with a null value (tombstones) are retained briefly then deleted — this is the delete mechanism for compacted topics.

**Use cases for compaction:**
- **Changelog topics** (Kafka Streams state store changelog): retain the latest value per key so a new consumer instance can reconstruct state by replaying only the compacted log.
- **Database CDC topics** (Debezium): retain the latest row state per primary key.
- **User preference topics**: retain the latest preference value per user ID.

**Compaction guarantees:** After compaction, the log contains at least the latest record for every key that was ever produced. Offsets are preserved (some offsets become "holes" — consumers skip them). The HWM and consumer offsets remain valid.

**Mixing retention and compaction:** `cleanup.policy=compact,delete` — compact and also time/size-based delete. Records older than `retention.ms` may be deleted even if they are the latest for their key.

### 6f. Producer Batching, Compression & Backpressure

**Batching (linger.ms + batch.size):**
- `batch.size` (default 16KB): producer accumulates records in a batch per partition until it reaches this size, then sends.
- `linger.ms` (default 0): if the batch isn't full, wait up to this long before sending anyway. `linger.ms=0` → lowest latency (send immediately). `linger.ms=5` → higher throughput (more records per batch, fewer requests).
- **Rule of thumb for throughput-sensitive producers:** `linger.ms=5–20`, `batch.size=64KB–512KB`.

**Compression:**
| Codec | CPU Cost | Compression Ratio | Latency Impact | Best For |
|-------|----------|------------------|----------------|----------|
| none | 0 | 1× | lowest | CPU-constrained producers |
| snappy | low | 1.5–2× | ~1 ms | General purpose, low latency |
| lz4 | very low | 1.5–2× | <1 ms | **Best latency+throughput balance** |
| zstd | medium | 2.5–4× | 2–5 ms | **Best compression ratio** (Kafka 2.1+) |
| gzip | high | 2–3× | 5–10 ms | Legacy; avoid for high-throughput |

Compression happens at the batch level — larger batches compress better. Broker stores compressed; consumers decompress. Broker CPU for re-compression if producer and topic compression differ — avoid by matching them.

**Backpressure and consumer lag:**
- **Lag** = leader's log end offset − consumer's committed offset (per partition).
- Monitoring: `kafka-consumer-groups.sh --describe` or JMX metric `records-lag-max`.
- **Lag growing → what to do:**
  1. **Scale consumers horizontally** (add instances to the consumer group) — only works up to `num_partitions` consumers (one partition per consumer).
  2. **Increase partition count** — enables more consumer parallelism. Can only increase, never decrease. Do it proactively.
  3. **Optimize consumer processing** — async processing, batching DB writes, parallel downstream calls.
  4. **Priority queues** — dedicate separate topics/partitions to high-priority traffic; have a dedicated consumer pool for them.
  5. **Increase `fetch.min.bytes` and `fetch.max.wait.ms`** — consumer fetches larger batches less frequently, reducing per-record processing overhead.

### 6g. Schema Registry — Schema Evolution

**Wire format:** `[0x00][4-byte schema_id][Avro/Protobuf payload]`. The magic byte `0x00` identifies a Schema Registry-encoded message. Consumers look up the schema by ID on the first occurrence (then cache locally).

**Compatibility modes:**
| Mode | Allows | Rejects |
|------|--------|---------|
| BACKWARD | New schema reads data written by old schema | Adding required fields without default |
| FORWARD | Old schema reads data written by new schema | Removing fields without default |
| FULL | Both directions | Any non-compatible change |
| NONE | Anything | Nothing |

**Practical schema evolution rules (Avro):**
- Adding a field: always provide a default value → BACKWARD and FORWARD compatible.
- Removing a field: only if old consumers don't rely on it → FORWARD compatible.
- Renaming a field: use `aliases` in Avro → transparent to old consumers.
- Changing a type: almost always breaking — avoid; use a union type instead.

**Schema Registry HA:** Deploy 2+ instances behind a load balancer; schemas stored in a Kafka topic (`_schemas`, compacted). Any instance can serve reads from local cache; writes go to the leader instance (elected via Kafka partition leadership for `_schemas`).

---

## 7. Bottlenecks, Failure Modes & Trade-offs

| Concern | Root Cause | Mitigation |
|---|---|---|
| Leader skew (hot partition) | All produce for a key goes to one partition | Use a synthetic key (`real_key + random_salt`) if ordering can be relaxed; or custom partitioner |
| ISR shrinks to 1, `min.isr=2` → produce rejected | Slow follower or network partition | Alert on ISR size < RF; tune `replica.lag.time.max.ms`; ensure brokers have sufficient I/O |
| Controller failover slow (ZooKeeper) | Controller re-elects, reloads all metadata | Migrate to KRaft; pre-warm standby controller |
| Consumer rebalance storm | Many consumers joining at once (e.g., deployment rollout) | Use Cooperative Sticky Assignor; rolling deploys with `session.timeout.ms` tuning |
| Offset commit lag → duplicate processing | Consumer crashes between process and commit | Accept at-least-once; make consumer idempotent (upsert by event ID) |
| Log compaction lag | Cleaner can't keep up with write rate | Increase `log.cleaner.threads`; reduce `log.cleaner.min.compaction.lag.ms` |
| `__consumer_offsets` partition hot | Many groups committing to same coordinator | Increase `offsets.topic.num.partitions` (only at cluster init); spread groups across coordinators |
| Schema Registry single point of failure | Registry down → producers/consumers can't resolve schemas | Cache schemas aggressively in clients; deploy Registry in HA mode; circuit-break to cached schema |
| Disk fill from retention lag | Topic grows faster than retention deletes | Set `retention.bytes` as a backstop; alert on disk usage >70% |

**Fundamental trade-offs:**
- **Throughput vs latency:** `linger.ms=0` for lowest latency; `linger.ms=20 + batch.size=512KB` for highest throughput. Choose based on producer SLA.
- **Durability vs availability:** `min.isr=2` is safer but causes producer errors if ISR shrinks; `min.isr=1` keeps writes going but risks data loss. For financial data: `min.isr=2` always.
- **EOS vs throughput:** Transactions add ~5% overhead. Use EOS only where exactly-once matters; use at-least-once + idempotent consumers everywhere else.
- **Partition count:** More partitions = more parallelism but more file handles, more ZooKeeper/KRaft state, longer leader election on broker restart. Rule: don't over-partition; you can always add later (within limits).

---

## 8. Talk Track (35–45 Min)

```
00:00–04:00  Clarify: delivery guarantee? EOS needed? message size + retention?
04:00–10:00  Estimation: 1 GB/s ingestion, RF=3 → 3 GB/s disk, 50 brokers,
             100 partitions, 1.8 PB storage
10:00–17:00  High-level architecture: brokers, partitions, Leader/Follower,
             KRaft controller, consumer groups, Schema Registry
             Walk the produce path: client → leader → ISR replication → HWM → consumer
17:00–25:00  Deep dive 1 — Replication & ISR
             - ISR definition, lag.time.max.ms, removal/re-addition
             - acks=all, min.isr, HWM, what consumers can read
             - Leader epoch, KRaft election flow
25:00–33:00  Deep dive 2 — EOS
             - Idempotent producer: producerId, epoch, sequence dedup
             - Transactional API: transactional.id, fencing, 2PC with Transaction Coordinator
             - read_committed isolation level
             - What EOS does NOT cover (external systems)
33:00–38:00  Consumer groups, offset commit strategies, rebalance,
             Cooperative Sticky Assignor
             Backpressure: lag monitoring, scale consumers, increase partitions
38:00–42:00  Failure modes table, trade-off discussion
             Schema Registry: wire format, compatibility modes
42:00–45:00  Extensions: tiered storage (KIP-405 — offload old segments to S3),
             multi-datacenter replication (MirrorMaker 2), compaction for CDC
```

---

## Resources

### Free
- System Design Primer — https://github.com/donnemartin/system-design-primer (search "message queue")
- ByteByteGo YouTube — https://www.youtube.com/results?search_query=bytebytego+kafka+distributed+message+queue
- Confluent Official Docs (free) — https://docs.confluent.io (Kafka internals, KRaft, EOS)
- Confluent Blog — https://www.confluent.io/blog (search "exactly once", "KRaft", "ISR")
- Hello Interview — https://www.hellointerview.com (search "Kafka" or "message queue")
- Apache Kafka KIPs (authoritative source): KIP-98 (EOS), KIP-500 (KRaft), KIP-429 (Cooperative Rebalance)

### Paid
- ByteByteGo — https://bytebytego.com (Chapter: "Design a Message Queue")
- DesignGurus — https://www.designgurus.io (Grokking System Design: "Kafka / Message Queue")
- Kafka: The Definitive Guide (O'Reilly) — free via Confluent: https://www.confluent.io/resources/kafka-the-definitive-guide/

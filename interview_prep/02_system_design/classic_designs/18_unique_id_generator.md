# Distributed Unique ID Generator

> Appears at: Confluent, Google L5, Uber, Amazon L6, Atlassian. Rarely a full 45-min question — most often a **sub-question** inside a bigger design ("how do you generate the tweet ID?", "what's the primary key for shipments?"). Both the [URL Shortener](./03_url_shortener.md) and the [Twitter Timeline](./10_twitter_timeline.md) designs need this. Know it cold so you can answer it in 5 minutes inside another design, or stretch it to ~30 min if asked standalone.

## 1. Requirements

**Functional:**
- Generate unique IDs across a distributed system (many machines, many regions).
- IDs must be **globally unique** — no two calls ever return the same value.
- IDs fit in **64 bits** (so they map to a `BIGINT` / Go `int64` / Java `long` — no 128-bit overhead in indexes and network payloads).
- IDs are **roughly time-sortable** — IDs generated later sort after earlier ones. Enables `ORDER BY id` as a cheap proxy for `ORDER BY created_at`, and keeps B-tree inserts append-mostly.

**Non-functional:**
- **High throughput** — 10K+ IDs/sec per node, millions/sec aggregate.
- **Low latency** — ID generation must be local/in-memory, sub-millisecond. No network round trip on the hot path.
- **No single point of failure** — a central DB sequence is the thing we are trying to kill.
- **Highly available** — if the ID service is down, callers cannot write. It is on the critical path of every insert.

**Clarifying questions:**
1. "Do IDs need to be *strictly* monotonic, or just roughly time-ordered?" → Roughly is almost always enough. Strict global ordering forces coordination (a single sequencer) and kills scalability.
2. "64-bit numeric, or is a 128-bit UUID acceptable?" → If they say UUID is fine, the whole problem collapses to one line (`uuid4()`). The interesting version is the 64-bit, sortable constraint.
3. "Is it OK if IDs leak volume?" → Sequential IDs reveal how many you've created (the classic `id=42` enumeration). Matters for public-facing IDs.

## 2. Back-of-Envelope Estimation

```
Throughput target:   1,000,000 IDs/sec aggregate across the fleet
Per-node target:     ~10,000 IDs/sec sustained

64-bit Snowflake budget:
  1  sign bit       (always 0 → keep IDs positive in signed int64)
  41 timestamp bits (milliseconds)
  10 machine bits
  12 sequence bits
  = 64 bits total

41-bit ms timestamp:
  2^41 ms = 2,199,023,255,552 ms
          = 2.199e12 / (1000*60*60*24*365) ≈ 69.7 years
  → with a custom epoch starting 2024, IDs last until ~2094.

10-bit machine id:
  2^10 = 1024 distinct workers (e.g. 32 datacenters x 32 machines, or flat 1024)

12-bit sequence (per machine, per millisecond):
  2^12 = 4096 IDs per millisecond per machine
  → 4096 * 1000 = 4,096,000 IDs/sec per machine (theoretical ceiling)
  → 1024 machines * 4.096M = ~4.2 billion IDs/sec fleet ceiling

So a single Snowflake node alone (4M/sec) blows past the 1M/sec target.
The bit layout is the design — almost no infra beyond worker-id assignment.
```

## 3. API Design

```
# In-process library (the common case — link the lib, no network call)
id = generator.next_id()    # returns int64, e.g. 1782939472638042113

# As a service (Snowflake-as-a-service, when you can't embed the lib)
GET /api/v1/id
  → 200 { "id": 1782939472638042113 }

# Batch fetch (amortize the network cost — get 1000 at once)
GET /api/v1/ids?count=1000
  → 200 { "ids": [ ...1000 monotonic ids... ] }

# Worker-id assignment (called once at boot, NOT per-id)
# Handled out-of-band via ZooKeeper/etcd registration, not a request API.
```

**Library vs service:** Prefer the **embedded library** — it generates IDs in-process with zero network hops, which is what makes it sub-microsecond. Expose it as a service only when callers can't embed it (polyglot fleet, untrusted clients). A batch endpoint hides the network latency by amortizing it over many IDs.

## 4. High-Level Architecture

```
   App Service A          App Service B          App Service C
  (machine_id=1)         (machine_id=2)         (machine_id=42)
        │                       │                       │
   ┌────▼─────┐            ┌────▼─────┐            ┌────▼─────┐
   │ Snowflake│            │ Snowflake│            │ Snowflake│   ← embedded lib,
   │  lib     │            │  lib     │            │  lib     │     in-process
   └────┬─────┘            └────┬─────┘            └────┬─────┘
        │  next_id()            │                       │
        │  (local, in-memory, no network)               │
        ▼                       ▼                       ▼
   1782...113              1782...229              1782...877
        └───────────────────────┴───────────────────────┘
                                 │
                                 ▼  written to DB as PK / used as event key
                          ┌─────────────┐
                          │  Postgres / │
                          │  Kafka / etc│
                          └─────────────┘

   Worker-ID coordination (boot-time only, off the hot path):
   ┌──────────────────────────────────────────────────┐
   │   ZooKeeper / etcd                                 │
   │   /workers/  → ephemeral sequential znodes         │
   │   each node claims a unique 0..1023 id on startup  │
   └──────────────────────────────────────────────────┘
```

**Flow:** At boot, each process registers with ZooKeeper/etcd and is handed a unique `machine_id` (0..1023). From then on every `next_id()` is a pure in-memory computation: read the wall clock, splice in the machine id, bump a per-ms sequence counter. **No coordination happens per ID** — that's the whole point. Coordination is paid once, at startup.

## 5. Data Model

There is barely a data model — IDs are computed, not stored. The only persistent state is **worker-id leases**.

```
# ZooKeeper / etcd layout for worker-id assignment
/snowflake/workers/                  (parent znode)
  worker-0000000001  → { host: "10.0.1.5",  leased_at: ... }   (ephemeral)
  worker-0000000002  → { host: "10.0.1.9",  leased_at: ... }   (ephemeral)
  ...
# Ephemeral nodes auto-release the worker-id when the session/host dies.
# Sequential znode suffix → derive machine_id = suffix % 1024.
```

```sql
-- How the generated ID is consumed downstream: it's just the PK.
CREATE TABLE tweets (
  id          BIGINT      PRIMARY KEY,   -- the Snowflake id, NOT a SERIAL
  author_id   BIGINT      NOT NULL,
  body        TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Because the id is time-prefixed, INSERTs append to the right edge of the
-- B-tree (hot, sequential, low fragmentation) instead of random insertions.
```

**Shard key:** Use the **high bits of the ID is a poor shard key** because they're all timestamp — every concurrent write lands in the same shard ("hot last shard"). Shard on a **hashed business key** (`author_id`, `tenant_id`) instead, and keep the time-sortable ID purely for ordering within a shard. This is the trade-off the next section drives home.

## 6. Deep Dives

### 6a. Approaches Compared

There are five families. Walk the interviewer through why each loses, ending on Snowflake.

**(1) UUID v4** — 128 random bits. `uuid4()`. Zero coordination, generate anywhere offline. But: 128-bit (2x storage, fatter indexes), **not sortable** (random → kills B-tree locality, causes index fragmentation), not numeric. Great when you don't need ordering and want zero infra (e.g. idempotency keys, request IDs).

**(2) DB auto-increment** — `SERIAL` / `AUTO_INCREMENT`. Perfectly sequential, trivial. But it's a **single point of failure** and a write bottleneck — every insert serializes on one sequence. Multi-master softens this with **offset + step**: master A emits 1,3,5,7…, master B emits 2,4,6,8… (offset 1/2, step 2). Works for 2-3 masters but doesn't scale — adding a 4th master means re-striding everyone, and a master crash burns its lane.

**(3) Flickr-style ticket server** — a dedicated MySQL box doing `REPLACE INTO Tickets64 ...; SELECT LAST_INSERT_ID();`. Run **two** ticket servers (one odd, one even via offset+step) for HA. Centralized but tiny and fast. Still two boxes on the critical path; a network hop per ID.

**(4) Range/segment allocation** — each node **leases a block** of IDs from a central store (e.g. "you own 1,000,000–1,001,000"). The node hands them out locally, only hitting the central store once per block to lease the next range. Amortizes coordination by ~1000x. Used by Twitter's later "segment" approach and Meituan Leaf-segment. Trade-off: IDs are sortable-ish but **gaps appear on crash** (unused tail of a leased range is lost) and ordering across nodes is loose.

**(5) Snowflake** — encode `[time | machine | sequence]` into 64 bits. No per-ID coordination, time-sortable, numeric, no SPOF. The standard answer.

| Approach | Coordination | Sortable | Bits | SPOF | Leaks volume | When to use |
|---|---|---|---|---|---|---|
| UUID v4 | none | no | 128 | no | no | offline / no ordering need |
| DB auto-increment | per-ID (central) | yes | 64 | **yes** | yes | tiny scale, single DB |
| Multi-master offset+step | per-ID | loosely | 64 | reduced | yes | 2-3 masters, legacy |
| Flickr ticket server | per-ID (1 hop) | yes | 64 | reduced (2 boxes) | yes | moderate scale |
| Range/segment lease | per-block (~1/1000) | loosely | 64 | reduced | partially | high write, gaps OK |
| **Snowflake** | **boot-time only** | **yes (ms)** | **64** | **no** | yes-ish | **the default** |

### 6b. Snowflake in Depth

**The 64-bit layout (most significant bit first):**

```
 63    62                                    22         12                0
 ┌─┬───────────────────────────────────────┬───────────┬────────────────┐
 │S│           timestamp (41 bits)          │ machine   │  sequence      │
 │ │       milliseconds since custom epoch  │ (10 bits) │  (12 bits)     │
 └─┴───────────────────────────────────────┴───────────┴────────────────┘
  1                  41                          10            12

  Sign bit = 0 always → ID stays positive in a signed 64-bit int.
  Timestamp FIRST (high bits) → numeric sort == time sort. This is what
  makes IDs "roughly time-sortable" — higher timestamp ⇒ larger number.
```

**Bit math:**
```
sequence:   2^12 = 4096 IDs per machine per millisecond
            → if you exhaust 4096 in one ms, BLOCK until the next ms.
machine:    2^10 = 1024 unique workers.
timestamp:  2^41 ms ≈ 69.7 years from the custom epoch.
            Use a custom epoch (e.g. 2024-01-01) NOT the Unix epoch (1970)
            to reclaim the ~54 years already elapsed → lifespan to ~2094.
```

**Worker-ID assignment** is the only coordination. On startup each process must claim a machine_id in 0..1023 that **no live process holds**:
- **ZooKeeper / etcd (recommended):** create an *ephemeral sequential* node under `/snowflake/workers/`; the sequence suffix `% 1024` is your machine_id. Ephemeral ⇒ on crash/disconnect the lease auto-releases and the id can be reused. No stale leases.
- **Static config:** bake machine_id into each host's config. Simple, but a copy-paste mistake → two hosts share an id → silent duplicate IDs. Avoid at scale.

**The clock-moving-backwards problem (the part interviewers probe):**
The timestamp is read from the wall clock. NTP corrections, leap-second smearing, or VM migration can make the clock **jump backwards**. If it does, you'll re-issue timestamps you already used → **duplicate IDs**. Snowflake's rule: track `last_timestamp`; if the current clock is *behind* it, you must NOT generate.
- Small skew (a few ms): **busy-wait** until the clock catches back up to `last_timestamp`, then proceed.
- Large skew: **refuse to generate** and raise an error / take the node out of rotation (return 503). Better to fail loud than emit dup IDs.

**Python implementation:**
```python
import time
import threading

class Snowflake:
    EPOCH_MS = 1704067200000          # custom epoch: 2024-01-01 00:00:00 UTC
    MACHINE_BITS = 10
    SEQUENCE_BITS = 12
    MAX_MACHINE_ID = (1 << MACHINE_BITS) - 1      # 1023
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1       # 4095
    MACHINE_SHIFT = SEQUENCE_BITS                 # 12
    TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_BITS  # 22

    def __init__(self, machine_id: int):
        if not 0 <= machine_id <= self.MAX_MACHINE_ID:
            raise ValueError("machine_id out of range 0..1023")
        self.machine_id = machine_id
        self.sequence = 0
        self.last_ts = -1
        self._lock = threading.Lock()   # next_id is called concurrently

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, last_ts: int) -> int:
        ts = self._now_ms()
        while ts <= last_ts:            # busy-wait for the clock to advance
            ts = self._now_ms()
        return ts

    def next_id(self) -> int:
        with self._lock:
            ts = self._now_ms()

            if ts < self.last_ts:
                # CLOCK MOVED BACKWARDS.
                drift = self.last_ts - ts
                if drift <= 5:           # tolerate small skew: wait it out
                    ts = self._wait_next_ms(self.last_ts)
                else:                    # large skew: refuse, don't dup
                    raise RuntimeError(f"clock moved back {drift}ms; refusing")

            if ts == self.last_ts:
                # same millisecond → bump sequence
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:   # 4096 used this ms → spill to next ms
                    ts = self._wait_next_ms(self.last_ts)
            else:
                self.sequence = 0        # new ms → reset sequence

            self.last_ts = ts
            return (((ts - self.EPOCH_MS) << self.TIMESTAMP_SHIFT)
                    | (self.machine_id << self.MACHINE_SHIFT)
                    | self.sequence)

# Decoding (handy for debugging — extract the timestamp back out)
def decode_ts(snowflake_id: int) -> int:
    return (snowflake_id >> Snowflake.TIMESTAMP_SHIFT) + Snowflake.EPOCH_MS
```

### 6c. Trade-offs — Sortability vs Coordination vs Leakage

Three forces pull against each other; pick based on which you actually need.

- **Sortability vs coordination.** Strict, gap-free, globally monotonic ordering requires a single sequencer (DB auto-increment, ticket server) — that reintroduces the SPOF/bottleneck you came to escape. Snowflake buys you *rough* (per-millisecond) ordering with *zero* per-ID coordination. Within one millisecond, IDs from different machines interleave arbitrarily — that's the price. If you truly need total order, you need consensus, and you should question the requirement.
- **Coordination vs throughput.** Range/segment leasing sits between auto-increment and Snowflake: it pays coordination once per block, not per ID. Choose it when you want *dense, mostly-sequential* numeric IDs (e.g. invoice numbers) but can't afford a central hop per ID. Accept gaps on crash.
- **ID leakage / security.** Any time-ordered or sequential ID **leaks volume and timing**: a competitor signing up and seeing `user_id=1,000,050` then `1,000,073` an hour later learns your signup rate; sequential resource IDs invite enumeration attacks (`/orders/124`, `/orders/125`). Mitigations: (a) use UUIDs for *externally exposed* IDs and keep Snowflake internal; (b) keep Snowflake as the DB PK but expose a separate opaque public id; (c) don't rely on obscurity — enforce authorization on every object regardless.

**When to pick which:**
- Need ordering + numeric + scale → **Snowflake**.
- Need zero infra / offline / no ordering → **UUID v4** (or UUID v7 if you want time-sortable 128-bit).
- Need dense sequential numbers (accounting) → **range/segment lease**.
- Tiny single-DB app → **auto-increment**, don't over-engineer.

## 7. Bottlenecks, Failure Modes & Trade-offs

- **Clock skew (the #1 issue):** covered above — track `last_timestamp`, busy-wait on small backward drift, refuse on large. Disable leap-second-induced jumps by running NTP in *slew* mode (gradual) not *step* mode (jump). VM live-migration is a sneaky cause — pin clock-sensitive nodes.
- **Sequence exhaustion:** >4096 IDs in one ms on one machine → block until next ms. At sustained 4M+/sec on a single node you'd hit this; in practice you spread load across machines long before. If one machine genuinely needs >4M/sec, steal bits from machine_id to grow the sequence field.
- **Worker-id collision:** two processes with the same machine_id silently emit duplicates — the most dangerous failure because it's *silent*. ZooKeeper/etcd ephemeral leases prevent it; static config invites it. Add a startup self-check that the leased id is unique.
- **ZooKeeper down at boot:** new nodes can't get a worker-id and won't start. Already-running nodes are unaffected (they only needed ZK at boot). Mitigation: cache the last leased id locally and reuse it if ZK is briefly unreachable, with a TTL guard.
- **Hot-shard from time-prefixed PKs:** if you shard *by the ID*, all current writes hit the same (latest) shard. Shard by a hashed business key instead; keep the Snowflake id for ordering only. (See [URL Shortener §7](./03_url_shortener.md) for the analogous sharding discussion.)
- **Not strictly monotonic:** two IDs in the same ms from different machines aren't globally ordered. Fine for "roughly time-sortable"; a dealbreaker only if you need a total order (then you need a sequencer + consensus).

## 8. Talk Track (25-35 min — note this is a SHORTER design, often a sub-question)

```
0-2 min:   Clarify: 64-bit numeric vs UUID OK? strictly monotonic or roughly?
           does the ID leak volume / is it public-facing? This scopes everything.
2-4 min:   Estimation: 1M/sec target. Show the 64-bit budget: 41 ts + 10 machine
           + 12 seq → 4096 ids/ms/machine = 4M/sec PER node. One node beats target.
4-9 min:   Walk the FIVE approaches: UUIDv4 (no sort, 128-bit) → DB auto-increment
           (SPOF) → multi-master offset+step → range/segment lease (amortized) →
           Snowflake. Put up the trade-off table. Land on Snowflake.
9-18 min:  DEEP DIVE Snowflake: draw the 64-bit layout. Do the bit math live
           (69.7 yrs, custom epoch, 4096/ms). Code next_id(). Explain why
           timestamp goes in the HIGH bits (sort == time).
18-24 min: Worker-id assignment via ZooKeeper/etcd ephemeral nodes. Then the
           CLOCK-BACKWARDS problem: track last_ts, busy-wait small skew, refuse
           large skew. This is the question they most want to hear answered.
24-29 min: Trade-offs: sortability vs coordination vs ID leakage. When to pick
           UUID vs segment vs Snowflake. Sharding caveat (don't shard by id).
29-33 min: Failure modes: silent worker-id collision, ZK-down-at-boot, sequence
           exhaustion. Tie back: "in the URL shortener / Twitter design, this is
           exactly how I'd mint the short code / tweet id."
33-35 min: Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — see the "Generating globally unique IDs" notes.
- [Hello Interview — system design](https://www.hellointerview.com) — distributed primitives incl. ID generation.
- [ByteByteGo — Snowflake / unique ID generator](https://www.youtube.com/results?search_query=bytebytego+unique+id+generator+snowflake)
- [NeetCode — distributed unique ID generation](https://www.youtube.com/results?search_query=neetcode+distributed+unique+id+generator)
- Twitter Snowflake source & Flickr "Ticket Servers" blog post (search: "flickr ticket servers sharding").

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a Unique ID Generator in Distributed Systems.
- [Grokking the System Design Interview](https://www.designgurus.io) — distributed unique ID section.

# Distributed Job Scheduler
> Appears at Google (Cloud Scheduler internals), Confluent (Kafka-based delayed processing), Atlassian (Jira automation, Bamboo CI), Amazon (Step Functions, EventBridge Scheduler). Common prompt: "Design a system that runs arbitrary tasks at a scheduled time, at scale."

## 1. Requirements

### Functional
- Schedule a job to run: (a) at a specific time, (b) after a delay, (c) on a recurring cron schedule.
- Each job has a handler type, input payload, and optional idempotency key.
- At-least-once execution guarantee; exactly-once available for workloads that provide an idempotency key.
- Monitor job status: pending, running, succeeded, failed, retrying, dead-lettered.
- Retry on failure up to N times with configurable backoff (linear, exponential).
- After N failures, move job to a Dead Letter Queue (DLQ) for manual inspection.
- Cancel a pending/running job.

### Non-Functional
- Scale: 10M scheduled jobs in flight; 10K job executions/sec at peak.
- Scheduling accuracy: jobs fire within ±5s of their scheduled time (not millisecond precision).
- Durability: no job is lost even if the scheduler crashes.
- High availability: 99.99%.
- Horizontal scalability: add scanner/worker nodes without downtime.

### Clarifying Questions to Ask
1. "What is the acceptable scheduling jitter — seconds or milliseconds?" — sub-second precision requires a different design (hardware timers, dedicated delay queues); seconds-precision allows a polling scanner.
2. "Are jobs short-running (seconds) or long-running (hours)?" — determines heartbeat interval and failure detection timeout.
3. "Do jobs need exactly-once semantics, or is at-least-once + idempotent worker acceptable?" — EOS requires distributed locking + worker coordination; at-least-once is simpler and usually sufficient.

---

## 2. Back-of-Envelope Estimation

```
Job volume:
  10M jobs in flight at any time
  10K executions/sec peak = 864M executions/day

Scanner throughput:
  Jobs become due at 10K/sec
  Scanner must identify and dispatch these within ±5s
  Polling interval: 1s per scanner shard
  Jobs due per poll: 10K/sec × 1s poll = 10K rows/scan
  With 10 scanner shards: 1K rows/shard/poll — lightweight DB query

Storage:
  Each job record: 1 KB (payload + metadata)
  10M active jobs × 1 KB = 10 GB — trivial for PostgreSQL
  Historical (completed) jobs: 864M/day × 1 KB = 864 GB/day → archive to S3

Worker throughput:
  10K executions/sec / 100 workers = 100 jobs/sec per worker
  Each worker runs 10 concurrent goroutines → 10 jobs/worker concurrently

Cron jobs:
  1M recurring cron jobs, each with a computed next_run_at
  On trigger: update next_run_at = compute_next(cron_expr, now) → insert next instance
```

---

## 3. API Design

### Job Management (HTTP / gRPC)
```
// Schedule a one-time job
POST /v1/jobs
Body: {
  handler:           string,          // "send-email", "resize-image", etc.
  payload:           object,          // arbitrary JSON, max 64 KB
  run_at:            ISO8601,         // "2024-01-20T14:30:00Z"
  idempotency_key:   string,          // optional; prevents duplicate scheduling
  max_retries:       int,             // default 3
  retry_backoff:     enum { LINEAR, EXPONENTIAL },
  timeout_seconds:   int              // default 300
}
Response 201 Created: { job_id: uuid, status: "PENDING", run_at: "..." }

// Schedule a recurring job (cron)
POST /v1/cron-jobs
Body: {
  name:     string,           // human-readable, unique per account
  handler:  string,
  payload:  object,
  schedule: string,           // cron expression: "0 * * * *" (hourly)
  timezone: string            // "America/New_York"
}
Response 201 Created: { cron_job_id: uuid, next_run_at: "..." }

// Get job status
GET /v1/jobs/{job_id}
Response: { job_id, status, run_at, started_at, completed_at, attempt, last_error }

// Cancel a job
DELETE /v1/jobs/{job_id}
Response: 204 No Content (only valid if status = PENDING)

// List DLQ jobs
GET /v1/jobs?status=DEAD_LETTERED&limit=50
```

### Internal (worker callback)
```
// Worker signals job completion (called by worker SDK, not exposed publicly)
POST /internal/v1/jobs/{job_id}/complete
Body: { status: enum { SUCCESS, FAILURE }, error_message: string, worker_id: string }
```

---

## 4. High-Level Architecture

```
API Clients
  |
  v
[API Service]  (stateless, horizontally scaled)
  |
  | INSERT job record with status=PENDING, due_at=run_at
  v
[PostgreSQL — Jobs DB]  (sharded by job_id hash)
  (schema: job_id, handler, payload, status, due_at, claimed_at, worker_id, attempt, ...)

  ^                          ^
  |                          |
[Scanner Service]       [etcd/ZooKeeper]
(one active scanner     (leader election;
 per shard via          only the elected
 leader election)        scanner per shard
  |                      polls the DB)
  |
  | SELECT jobs WHERE due_at <= NOW() AND status='PENDING' AND shard_id=N
  | UPDATE status='CLAIMED', claimed_at=NOW(), worker_id=...  [optimistic lock]
  v
[Job Queue — Kafka or Redis Queue]
  (one queue per handler type for isolation)
  |
  v
[Worker Pool]  (horizontally scaled; one consumer group per handler type)
  |        |
  |        | heartbeat every 10s to Jobs DB (UPDATE heartbeat_at=NOW())
  |        |
  | on success: UPDATE status='SUCCEEDED'
  | on failure: if attempt < max_retries: UPDATE status='PENDING', due_at=backoff_time
  |             if attempt >= max_retries: UPDATE status='DEAD_LETTERED'
  v
[Dead Letter Queue Service]
  (alert on DLQ size, manual retry UI)

[Cron Scheduler]  (separate service)
  - Reads cron_jobs table every 10s
  - For each job whose next_run_at <= NOW(): INSERT a one-time job into Jobs DB
  - UPDATE cron_jobs SET next_run_at = compute_next(schedule, NOW())
  - Uses same leader election as Scanner to avoid double-trigger
```

---

## 5. Data Model

### jobs table (PostgreSQL, sharded by hash(job_id) % N)
```sql
CREATE TABLE jobs (
  job_id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  shard_id        INT          GENERATED ALWAYS AS (('x'||substr(job_id::text,1,8))::bit(32)::int % 10) STORED,
  handler         VARCHAR(64)  NOT NULL,
  payload         JSONB        NOT NULL,
  idempotency_key VARCHAR(128) UNIQUE,  -- NULL if not provided
  status          VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, CLAIMED, RUNNING, SUCCEEDED, FAILED, DEAD_LETTERED, CANCELLED
  due_at          TIMESTAMPTZ  NOT NULL,
  claimed_at      TIMESTAMPTZ,
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  heartbeat_at    TIMESTAMPTZ,
  worker_id       VARCHAR(64),
  attempt         INT          NOT NULL DEFAULT 0,
  max_retries     INT          NOT NULL DEFAULT 3,
  retry_backoff   VARCHAR(12)  NOT NULL DEFAULT 'EXPONENTIAL',
  timeout_seconds INT          NOT NULL DEFAULT 300,
  last_error      TEXT,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  cron_job_id     UUID         REFERENCES cron_jobs(cron_job_id)
);

-- Critical index: scanner query
CREATE INDEX idx_jobs_scanner ON jobs (shard_id, status, due_at)
  WHERE status = 'PENDING';

-- Heartbeat timeout reclaim index
CREATE INDEX idx_jobs_stale ON jobs (status, heartbeat_at)
  WHERE status IN ('CLAIMED', 'RUNNING');
```

### cron_jobs table
```sql
CREATE TABLE cron_jobs (
  cron_job_id  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name         VARCHAR(128) NOT NULL UNIQUE,
  handler      VARCHAR(64) NOT NULL,
  payload      JSONB       NOT NULL,
  schedule     VARCHAR(64) NOT NULL,   -- cron expression
  timezone     VARCHAR(64) NOT NULL DEFAULT 'UTC',
  next_run_at  TIMESTAMPTZ NOT NULL,
  enabled      BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cron_due ON cron_jobs (next_run_at) WHERE enabled = TRUE;
```

### leader_locks table (DB-based leader election alternative to etcd)
```sql
CREATE TABLE leader_locks (
  lock_name    VARCHAR(64)  PRIMARY KEY,   -- e.g. "scanner-shard-3"
  owner_id     VARCHAR(64)  NOT NULL,      -- hostname:pid
  expires_at   TIMESTAMPTZ  NOT NULL,
  acquired_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
-- Leader: INSERT ON CONFLICT DO UPDATE SET owner_id=... WHERE expires_at < NOW()
-- Heartbeat: UPDATE leader_locks SET expires_at=NOW()+interval '30s' WHERE owner_id=me
```

**Partitioning key:** `shard_id` derived from `job_id` hash. Scanner service instance N polls only `shard_id = N`, distributing scanner load. Worker queues are partitioned by `handler` type for isolation.

---

## 6. Deep Dives

### 6a. Durable Scheduling — DB Polling vs Delayed Message Queue

**Approach 1 — DB polling (Scanner pattern):**
- Jobs stored in PostgreSQL with a `due_at` column.
- Scanner queries: `SELECT ... WHERE shard_id=N AND status='PENDING' AND due_at <= NOW() LIMIT 100`.
- Atomic claim: `UPDATE jobs SET status='CLAIMED', worker_id=me, claimed_at=NOW() WHERE job_id=? AND status='PENDING'` — only one scanner claims each job (optimistic lock via status check).
- **Pros:** durable (jobs survive restarts), trivially queryable (cancel, inspect, reorder), no separate queue infrastructure.
- **Cons:** DB polling can be heavy at scale; `due_at` index must stay efficient; can't easily do sub-second precision.
- **Scaling the scanner:** partition the `jobs` table by `shard_id` and run one scanner per shard. With 10 shards and 10K due jobs/sec: 1K jobs/shard/sec → a lightweight indexed query.

**Approach 2 — Delayed message queue:**
- Use SQS with `DelaySeconds` (max 15 min) or a purpose-built delay queue (Redis sorted set with score=due_at, poller reads items with score ≤ NOW()).
- **Pros:** no DB polling; queue inherently buffers load.
- **Cons:** SQS max delay is 15 min — can't schedule a job 6 months out without an intermediate "reschedule" step. Redis sorted set approach is custom infra.
- **Hybrid (production pattern):** Store all jobs in DB (durable, queryable). Scanner picks up jobs due in the next 5 minutes and pushes them into a short-lived queue (Kafka/SQS) for workers. DB is the source of truth; queue is the delivery mechanism.

**Decision in an interview:** Start with the DB polling approach (simple, durable, survives failures). Layer in a queue for worker dispatch. Mention the hybrid pattern as the production evolution.

### 6b. Exactly-Once Execution — The Hardest Problem

**Why it's hard:** A job is dispatched to a worker. The worker processes it, calls an external API, then crashes before marking it done. The scanner reclaims the job and re-dispatches it. The external API is called twice.

**Option 1 — At-least-once + idempotent worker (preferred):**
- Worker receives a job that includes an `idempotency_key` (provided by the caller or derived from `job_id`).
- Worker uses the idempotency key to make its external call safe to retry: e.g., upsert by `idempotency_key` in the DB, or call an external API that supports idempotency headers.
- The second execution of the job is a no-op at the business logic level.
- **This is the right answer for most workloads.** It's simpler, doesn't require distributed coordination, and scales well.

**Option 2 — Optimistic locking + claimed_at (prevents double-dispatch):**
- Before dispatching, scanner atomically sets `status=CLAIMED` using a conditional UPDATE: `WHERE status='PENDING'`. If two scanners race, only one succeeds (the other gets 0 rows affected).
- Worker heartbeats every 10s: `UPDATE jobs SET heartbeat_at=NOW() WHERE job_id=? AND worker_id=me`.
- Reclaim: `SELECT ... WHERE status IN ('CLAIMED','RUNNING') AND heartbeat_at < NOW() - interval '30s'`. Dead worker → reclaim → re-dispatch.
- **Gap:** Worker finishes, marks success, but the reclaim scanner also fires (race between heartbeat timeout and success mark). Use DB transaction: worker atomically marks `status=SUCCEEDED` AND checks that `worker_id=me` (no-op if reclaimed by another worker).
- This approach reduces duplicates to the reclaim window (30s), not zero.

**Option 3 — True exactly-once (rarely needed):**
- Use distributed transaction: worker atomically commits its business logic result AND marks the job as succeeded in the same transaction. Only possible if the worker writes to the same PostgreSQL instance as the jobs table. For external APIs, impossible without 2PC (avoid).
- For Kafka-based dispatch: idempotent producer + transactional offset commit (consume job record → process → commit offset atomically). Same caveats as Kafka EOS.

**Recommendation in the interview:** Recommend at-least-once + idempotent workers. State that true exactly-once is only achievable when the worker writes to the same DB, and even then, you should make workers idempotent anyway as a defense-in-depth measure.

### 6c. Leader Election — Preventing Double-Scan

**Problem:** If multiple scanner instances poll for due jobs simultaneously without coordination, the same job gets dispatched to multiple workers.

**Why the optimistic lock alone isn't enough:** Two scanners both `SELECT` the same 100 pending jobs, then race to `UPDATE status='CLAIMED'`. The second scanner's UPDATE is blocked/returns 0 rows — so the job is claimed exactly once. This works, but it's inefficient: wasted DB round-trips for the losing scanner.

**Better: only one scanner per shard scans at a time (leader lease):**

**Option A — etcd/ZooKeeper lease:**
- Scanner acquires a lease: `etcd.Grant(TTL=30s) → etcd.Put("scanner-shard-3", myID, LeaseID)`.
- Renew every 10s. If the leader dies, the lease expires after 30s and another scanner takes over.
- Clean, well-understood. Requires etcd/ZooKeeper as a dependency.

**Option B — PostgreSQL advisory lock:**
- `SELECT pg_try_advisory_lock(shard_id)` — returns true for exactly one session per shard_id.
- Lock held for the duration of the DB session. If the scanner process dies, the session closes and the lock is released automatically.
- **Pro:** no external dependency — uses the same PostgreSQL that stores jobs.
- **Con:** lock is tied to a DB connection; session must stay alive; doesn't work across DB connections.

**Option C — DB leader_locks table (shown in data model):**
- Atomic upsert: `INSERT INTO leader_locks ... ON CONFLICT DO UPDATE SET owner_id=me, expires_at=NOW()+30s WHERE expires_at < NOW()`.
- Leader renews every 10s. Non-leader attempts renewal on each poll; if leader is dead (expired), the non-leader wins the upsert and takes over.
- **Pro:** no external dependency; works with any DB client.
- **Con:** slightly more complex logic; clock skew between nodes can cause brief double-leadership (mitigate with a 2s grace period).

**Decision:** Use PostgreSQL advisory locks for simplicity in a co-located deployment. Use etcd for a multi-region or large-scale deployment where you want proper Raft consensus.

### 6d. Cron at Scale — Parsing, Pre-Computing, and DST

**Cron expression parsing:**
- Standard 5-field cron: `minute hour dom month dow` (e.g., `0 9 * * 1-5` = 9am Mon-Fri).
- Extended 6-field: add `second` prefix (e.g., `*/30 * * * * *` = every 30 seconds).
- Use a battle-tested library: `robfig/cron` (Go), `croniter` (Python), `node-cron` (Node.js).
- Pre-compute and store `next_run_at` in the `cron_jobs` table. Cron Scheduler reads `WHERE next_run_at <= NOW()` — simple indexed query.

**On trigger:** Insert a new one-time job into `jobs`, then update `next_run_at = croniter.next(schedule, now, tz)`. Do this in a single DB transaction to avoid inserting a job but failing to advance `next_run_at` (which would cause double-trigger on next scan).

**Daylight Saving Time (DST) edge cases:**
- **Spring-forward (gap):** `0 2 * * *` (2:00am daily) in a timezone that skips 2am on DST day. `croniter` will skip to 3am on that day — arguably correct.
- **Fall-back (ambiguous):** `0 1 * * *` (1:00am daily) runs twice on the day clocks fall back. Options: (a) accept double-trigger on that day, (b) track `last_run_at` and skip if already ran in the wall-clock hour.
- **Mitigation:** always store `next_run_at` in UTC. Convert to local time only for display. Compute `next_run_at` using the IANA timezone database which handles DST transitions correctly.

**Missed cron jobs (scheduler was down):**
- On startup, Cron Scheduler checks for cron jobs whose `next_run_at` is in the past.
- Policy choices: (a) fire the missed run immediately, then advance to the next future run; (b) skip missed runs and advance to next future run (simpler, usually correct for reporting/batch jobs).
- Make this configurable per cron job: `missed_run_policy: enum { FIRE_MISSED, SKIP_MISSED }`.

### 6e. Failure Recovery — Heartbeat, Reclaim, DLQ

**Heartbeat pattern:**
```
Worker loop:
  job = dequeue()
  jobs_db.update(job_id, status='RUNNING', worker_id=me, heartbeat_at=NOW())
  
  done_chan = spawn_goroutine(execute_job, job)
  
  while not done:
    select:
      case <-time.After(10s):
        jobs_db.update(job_id, heartbeat_at=NOW())  // heartbeat
      case result = <-done_chan:
        if result.success:
          jobs_db.update(job_id, status='SUCCEEDED', completed_at=NOW())
        else:
          schedule_retry(job, result.error)
        break
```

**Reclaim scanner (separate from dispatch scanner):**
```sql
-- Find stale jobs (worker died)
UPDATE jobs
SET    status = 'PENDING',
       due_at = NOW() + (attempt * 30s),  -- backoff
       attempt = attempt + 1,
       worker_id = NULL,
       claimed_at = NULL
WHERE  status IN ('CLAIMED', 'RUNNING')
  AND  heartbeat_at < NOW() - INTERVAL '30 seconds'
  AND  attempt < max_retries
RETURNING job_id;

-- DLQ: max retries exceeded
UPDATE jobs SET status = 'DEAD_LETTERED'
WHERE status IN ('CLAIMED','RUNNING')
  AND heartbeat_at < NOW() - INTERVAL '30 seconds'
  AND attempt >= max_retries;
```

**Retry backoff:**
- Linear: `due_at = NOW() + attempt × base_delay` (e.g., 30s, 60s, 90s).
- Exponential: `due_at = NOW() + base_delay × 2^attempt` (e.g., 30s, 60s, 120s, 240s).
- Add jitter: `due_at += random(0, due_at × 0.1)` to prevent retry storms.

**DLQ handling:**
- Jobs in `DEAD_LETTERED` state are never re-dispatched automatically.
- Ops can inspect payload, fix the handler, and manually requeue: `UPDATE jobs SET status='PENDING', attempt=0, due_at=NOW() WHERE job_id=?`.
- Alert: page on-call if DLQ size exceeds threshold (e.g., >100 jobs in 5 min).

---

## 7. Bottlenecks, Failure Modes & Trade-offs

| Concern | Risk | Mitigation |
|---|---|---|
| Scanner DB query slow at 10M rows | Full table scan if index degrades | Partial index on `(shard_id, due_at) WHERE status='PENDING'`; archive completed jobs to S3 after 7 days |
| Two scanners claim the same job | Double execution | Optimistic lock (conditional UPDATE); leader election per shard eliminates the race |
| Worker hangs indefinitely | Heartbeat keeps renewing; job never completes | Enforce `timeout_seconds` in worker: kill the goroutine after timeout, mark FAILED |
| Cron job double-trigger | Cron scheduler restarts, fires missed run AND next scheduled run | Idempotency key derived from `(cron_job_id, scheduled_run_at)`; duplicate insert blocked by UNIQUE constraint |
| etcd/ZooKeeper unavailable | No scanner can acquire leader lease | Scanner falls back to DB-level advisory lock as backup; or use DB-only leader_locks table (no external dep) |
| Clock skew between nodes | Reclaim scanner fires on a still-alive worker | Add 10s grace period to heartbeat timeout: reclaim only if `heartbeat_at < NOW() - (timeout + 10s)` |
| DLQ growth unmonitored | Silent job failures accumulate | Alert on DLQ size; Slack/PagerDuty integration; daily DLQ report |
| Hot handler type | One handler has 10K/sec jobs; others have 10/sec | Separate Kafka topics/partitions per handler type; scale worker pool independently per handler |

**Key trade-offs:**
- **Polling interval vs DB load:** 1s polling for 10K due jobs/sec across 10 shards = 10 queries/sec/shard, each returning ~1K rows. Fine for PostgreSQL. Lower to 100ms if scheduling precision must be tighter, but watch DB CPU.
- **At-least-once vs exactly-once:** exactly-once requires distributed coordination and limits throughput. At-least-once + idempotent workers is the right answer for 95% of workloads. State this clearly in the interview.
- **DB as queue vs dedicated queue:** DB-as-queue is simple and durable; dedicated queue (Kafka, SQS) scales better for dispatch but adds infra complexity. Hybrid (DB for durability, queue for dispatch) is the production-grade answer.
- **Cron job granularity:** second-level cron (e.g., every 30s) is hard to implement correctly at scale. Recommend minimum granularity of 1 minute for external APIs; use Kafka delayed processing for sub-minute needs.

---

## 8. Talk Track (35–45 Min)

```
00:00–04:00  Clarify: scheduling precision (seconds ok)? job duration (short vs long)?
             EOS or at-least-once+idempotent? cron support needed?
04:00–10:00  Estimation: 10M jobs in DB (10 GB), 10K executions/sec,
             10 shards × 1 scanner each, 100 workers
10:00–17:00  High-level diagram: API → Jobs DB → Scanner (leader-elected per shard)
             → Kafka → Worker Pool → heartbeat loop → DLQ
             Walk a full job lifecycle: schedule → scan → claim → dispatch → execute → complete
17:00–25:00  Deep dive 1 — Exactly-once execution
             - At-least-once + idempotent worker: the right default
             - Optimistic lock (conditional UPDATE) prevents double-claim
             - Heartbeat + reclaim for dead workers
             - True EOS only if worker writes to same DB (rarely needed)
25:00–33:00  Deep dive 2 — Leader election & sharded scanning
             - Why leader per shard: eliminates double-scan, reduces wasted DB ops
             - Three options: etcd lease, PostgreSQL advisory lock, leader_locks table
             - Trade-offs: external dep vs simplicity vs HA
33:00–38:00  Cron at scale: pre-compute next_run_at, croniter library, DST edge cases,
             missed-run policy (FIRE_MISSED vs SKIP_MISSED), idempotency key on cron trigger
38:00–42:00  Failure modes table; retry backoff with jitter; DLQ alerting
             DB polling vs delayed queue vs hybrid — when to use each
42:00–45:00  Extensions: priority queues (separate table/shard per priority level);
             workflow orchestration (multi-step jobs with DAG dependencies — Temporal/Airflow);
             multi-tenant isolation (separate shard per tenant)
```

---

## Resources

### Free
- System Design Primer — https://github.com/donnemartin/system-design-primer (search "job scheduler" / "task queue")
- ByteByteGo YouTube — https://www.youtube.com/results?search_query=bytebytego+distributed+job+scheduler
- Hello Interview — https://www.hellointerview.com (search "job scheduler" or "task scheduler")
- Temporal.io docs (free) — https://docs.temporal.io (production job orchestration reference)
- Amazon SQS delayed queues docs — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html

### Paid
- ByteByteGo — https://bytebytego.com (Chapter: "Design a Distributed Job Scheduler")
- DesignGurus — https://www.designgurus.io (Grokking System Design: "Task Scheduler")

# Recurring Payment / Autopay Scheduler

> Appears at: 56 AI / Razorpay Autopay (your actual system — -30% manual intervention). Strong design for Amazon (distributed scheduler), Google, Atlassian. Banks will ask variants of this. Also overlaps with "Design a distributed job scheduler."

## 1. Requirements

**Functional:**
- Register a NACH mandate for a customer (bank authorization for recurring debit)
- Schedule recurring charges on the mandate (monthly EMIs, subscriptions)
- Execute charges on their due dates, retry on failure with backoff
- Track mandate lifecycle: PENDING → REGISTERED → ACTIVE → CANCELLED/PAUSED
- Notify customers before each charge (D-2 reminder) and on success/failure
- Business can view payment history and mandate status

**Non-functional:**
- 100,000 active mandates; each mandates 1-12 charges/month → up to ~1.2M charges/month (~450/min peak)
- Charges must execute within a 15-minute window of their due_at time
- Exactly-once execution: a mandate must not be charged twice for the same period
- System must survive restarts and crashes without losing pending charges
- Retry on failure: up to 3 attempts over 7 days before marking mandate as PAUSED
- 99.5% uptime for the scheduler

**Clarifying questions:**
1. "Is this NACH mandate-based (bank debit) or card-based recurring?" → NACH mandate (India-specific), which means we submit to NPCI/bank and they handle the actual debit.
2. "What's the execution window tolerance? Exactly at 9 AM, or within a few hours?" → Within 15 min of due_at; business requirement (NPCI submission windows are time-bound).
3. "Who initiates retries — the business or the system?" → System-initiated, with configurable retry policy per mandate type.

## 2. Back-of-Envelope Estimation

```
Active mandates:        100,000
Charges per mandate/mo: avg 1 (monthly) → 100,000 charges/month
Peak charge window:     Most charges scheduled on 1st and 5th of month
                        → 40% of monthly volume in a 2-day window
                        → 40,000 charges in 2 days = ~14 charges/min avg
                        → peak: ~50 charges/min (burst window)

Scheduler overhead:     Scanner runs every 1 min, looks for charges due in next 2 min
                        → 50 rows scanned per run (trivial)

Mandate table:          100,000 rows × 2KB = 200MB (fits comfortably in PostgreSQL)
Charge history:         1.2M rows/month × 1KB = 1.2GB/month → 14GB/year

NPCI API:               Submit a charge file (batch) before 10 AM cut-off; result file arrives by EOD.
                        This is NOT real-time — it's a T+0 batch submission process (India NACH works this way).
```

## 3. API Design

```
# Mandate management
POST /v1/mandates
Body: { customer_id, bank_account, ifsc, max_amount_paise, purpose_code, start_date, end_date }
→ { mandate_id, status: "PENDING", umrn: null }

GET  /v1/mandates/{mandate_id}
→ { mandate_id, status, umrn, customer_id, next_charge_date, charge_history }

POST /v1/mandates/{mandate_id}/cancel
→ { mandate_id, status: "CANCELLED" }

# Schedule a charge
POST /v1/mandates/{mandate_id}/charges
Body: { amount_paise, due_at, description, idempotency_key }
→ { charge_id, status: "SCHEDULED", due_at }

# Get charges
GET /v1/mandates/{mandate_id}/charges?status=PENDING
→ [{ charge_id, due_at, amount_paise, status, attempts }]

# Internal scheduler API (not public)
POST /internal/charges/{charge_id}/execute   → triggers execution
POST /internal/charges/{charge_id}/result    → receives NPCI result callback
```

## 4. High-Level Architecture

```
Business API Client
       │
       │ POST /mandates, POST /charges
       ▼
┌──────────────────────────────┐
│     Mandate Service          │
│  (CRUD for mandates/charges) │
└──────────┬───────────────────┘
           │
           ▼
      PostgreSQL
      (mandates, scheduled_charges)
           │
           │ (Scanner reads this table every 1 min)
           ▼
┌──────────────────────────────┐
│      Scheduler (Scanner)     │
│  - Runs every 60s            │
│  - SELECT charges WHERE      │
│    due_at <= NOW() + 2min    │
│    AND status = 'SCHEDULED'  │
│    AND claimed_at IS NULL    │
│  - Claims rows (optimistic   │
│    lock: UPDATE + check)     │
│  - Publishes to Kafka        │
└──────────┬───────────────────┘
           │ Kafka: charges.due
           ▼
┌──────────────────────────────┐
│      Charge Worker           │
│  - Consumes charges.due      │
│  - Submits to NPCI/Razorpay  │
│  - Updates charge status     │
│  - Sends D-2 reminder        │
│  - Schedules retry if needed │
└──────────────────────────────┘
           │
           ▼
      NPCI / Razorpay Autopay API
      (result via webhook or polling)
           │
           ▼
┌──────────────────────────────┐
│      Result Processor        │
│  - Receives NPCI result      │
│  - Updates charge: CAPTURED  │
│    or FAILED                 │
│  - Schedules retry if needed │
│  - Notifies customer         │
└──────────────────────────────┘
```

## 5. Data Model

```sql
-- Mandates
CREATE TABLE mandates (
  mandate_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id     UUID NOT NULL,
  bank_account    TEXT NOT NULL,
  ifsc            TEXT NOT NULL,
  max_amount_paise BIGINT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING|REGISTERED|ACTIVE|PAUSED|CANCELLED
  umrn            TEXT UNIQUE,           -- NPCI's mandate reference number (set on registration)
  start_date      DATE NOT NULL,
  end_date        DATE,
  created_at      TIMESTAMPTZ NOT NULL,
  updated_at      TIMESTAMPTZ NOT NULL
);

-- Scheduled charges
CREATE TABLE scheduled_charges (
  charge_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mandate_id       UUID REFERENCES mandates NOT NULL,
  idempotency_key  TEXT UNIQUE NOT NULL,    -- business-provided, prevents duplicate scheduling
  amount_paise     BIGINT NOT NULL,
  due_at           TIMESTAMPTZ NOT NULL,    -- when to execute
  status           TEXT NOT NULL DEFAULT 'SCHEDULED',
                   -- SCHEDULED|CLAIMED|SUBMITTED|CAPTURED|FAILED|RETRYING|DLQ
  attempts         INT NOT NULL DEFAULT 0,
  claimed_at       TIMESTAMPTZ,            -- set when scheduler claims the row
  claimed_by       TEXT,                   -- scheduler instance ID
  last_attempt_at  TIMESTAMPTZ,
  next_retry_at    TIMESTAMPTZ,
  description      TEXT,
  npci_ref         TEXT                    -- NPCI transaction reference
);
CREATE INDEX idx_charges_due ON scheduled_charges(due_at, status)
  WHERE status IN ('SCHEDULED', 'RETRYING');  -- partial index: only actionable charges
```

## 6. Deep Dives

### 6a. Exactly-Once Execution Despite Retries and Crashes

**The problem:** The Scanner runs every minute. If it crashes after claiming a charge but before publishing to Kafka, the charge is in `CLAIMED` state but never processed. If the Scanner restarts, should it re-claim claimed charges?

**Solution: Optimistic locking + heartbeat + claim expiry**

```sql
-- Scanner claims a charge:
UPDATE scheduled_charges
SET status = 'CLAIMED',
    claimed_at = NOW(),
    claimed_by = 'scanner-instance-1'
WHERE charge_id = ?
  AND status IN ('SCHEDULED', 'RETRYING')
  AND (claimed_at IS NULL OR claimed_at < NOW() - INTERVAL '5 minutes')
RETURNING *;
-- The WHERE clause ensures:
--   1. No double-claim (status must be unclaimed)
--   2. Claim expiry: if a Scanner claimed it > 5 min ago and never progressed, it's safe to re-claim
```

If the Scanner crashes after claiming (row is CLAIMED) but before publishing to Kafka, the claim expires after 5 minutes. The next Scanner run re-claims it and tries again.

**Worker idempotency:** The Kafka message for each charge includes `charge_id`. The Charge Worker checks: `SELECT * FROM scheduled_charges WHERE charge_id = ? AND status = 'SUBMITTED'`. If already submitted, it skips (idempotent consumer). The NPCI submission also carries `idempotency_key` to prevent double-debit.

### 6b. Scheduler vs Worker Pool: The Critical Distinction

| | Scheduler (Scanner) | Worker |
|---|---|---|
| Responsibility | "What needs to run and when" | "Do the actual work" |
| State | Reads from DB; writes claimed_at | Reads from Kafka; submits to NPCI |
| Crash impact | Claim expires → another scanner picks up | Kafka offset not committed → reprocessed |
| Scale | Single instance (with leader election) OR sharded by mandate_id | Scale horizontally |

**Why not have the scanner do the work directly?** If the Scanner both scans AND submits to NPCI, a slow NPCI call blocks the scan loop, causing other charges to miss their window. Separation keeps the Scanner fast (DB query only).

### 6c. Clock Skew & UTC

All `due_at` timestamps stored in UTC. Scanner always compares `NOW()` in UTC. NTP drift is bounded to < 1s on cloud instances — well within the 15-min execution window. No special handling needed beyond "always use UTC."

Daylight saving time: India does not observe DST (UTC+5:30 always). But for future multi-region support: store `due_at` in UTC and convert to local time only for display.

### 6d. Retry Logic for Failed Charges

```
Attempt 1: due_at (original)
Attempt 2: due_at + 1 day  (e.g. bank was temporarily unavailable)
Attempt 3: due_at + 3 days (e.g. customer had insufficient funds)
After 3 failures: mandate → PAUSED, notify customer and business
                  business can manually re-activate

Skip retry if:
  - Mandate status = CANCELLED or PAUSED
  - charge.due_at + 7 days < NOW() (too stale to retry)
  - NPCI error = "MANDATE_CANCELLED" (hard failure — no point retrying)

Notify customer:
  - D-2 before each attempt (SMS/email)
  - On success: confirmation with transaction ref
  - On failure: reason + what to do next
```

### 6e. How -30% Manual Intervention Was Achieved

Before: Charges were manually submitted to NPCI by ops team via an Excel file each morning. Retry tracking was manual. Customer notifications were sent manually.

After: Automated scheduler submits to NPCI API. Result polling automated. Retry logic codified. D-2 reminders and result notifications automated. The 30% reduction came entirely from eliminating manual ops steps — not from a technical architectural change. The system simply did what ops were doing, reliably and at scale.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x scale (1M active mandates):**
- Scanner query: `SELECT WHERE due_at <= NOW() + 2min AND status IN ('SCHEDULED', 'RETRYING')` — partial index on `(due_at, status)` makes this fast even at 1M rows.
- At 1M mandates, peak could be 400K charges in 2 days = 140/min. Single scanner may bottleneck → shard by `hash(mandate_id) % N` across N scanner instances, each owns a range.
- NPCI API rate limits: batch submission (not per-charge API calls); build a batch aggregator.

**Failure modes:**
- NPCI API down: charges queue in `SUBMITTED` state; retry after recovery; NPCI has SLA for file submission windows.
- Scanner crashes: claim expiry (5 min) ensures no charge is permanently stuck.
- DB failover: primary PostgreSQL fails; read replica promoted → scanner restarts; at-most 5 min of claim expiry needed.
- Duplicate Kafka message: Charge Worker checks `status = 'SUBMITTED'` before re-submitting — idempotent.

**Trade-offs:**
- Polling DB every minute vs event-driven (immediate trigger when `due_at` is reached): polling is simpler, more reliable, and at this scale (50 charges/min) the overhead is negligible. Event-driven would use a sorted set in Redis (`ZADD due_charges due_at charge_id; ZRANGEBYSCORE ... 0 NOW()`), which is faster but adds complexity.
- Single scanner + claim expiry vs leader election: claim expiry is simpler than Zookeeper/etcd leader election. Good enough for this scale. At 10x, formal leader election would be worth it.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: NACH mandate or card-based? Execution window? Retry owner?
3-6 min:  Estimation: 100K mandates, 50 charges/min peak — not a high-QPS problem; this is an exactly-once correctness problem.
6-12 min: Architecture: Scanner → Kafka → Worker → NPCI. Emphasize separation of scheduler and worker.
12-18 min: Data model: mandates, scheduled_charges, partial index on (due_at, status).
18-28 min: DEEP DIVE: Exactly-once execution. Walk through the UPDATE SQL with claim expiry. Explain why this beats leader election for this scale.
28-35 min: Retry logic. Clock skew (UTC). NPCI result processing.
35-40 min: How -30% manual intervention was achieved (story).
40-43 min: 10x scale: sharded scanner, batch NPCI submission.
43-45 min: Open for questions.
```

**Authority hook:** *"I built this at 56 AI for Razorpay Autopay. The key insight was separating the scheduler (what and when) from the worker (do it), and using claim expiry instead of distributed locks for exactly-once execution. Here's how it worked in production."*

## Resources

**Free:**
- [System Design Primer — distributed systems](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo — distributed job scheduler](https://www.youtube.com/results?search_query=bytebytego+distributed+job+scheduler)
- [Razorpay Autopay NACH documentation](https://razorpay.com/docs/payments/recurring-payments/nach/)

**Paid (optional):**
- "Designing Data-Intensive Applications" — Chapter 10 (batch processing) and Chapter 11 (stream processing)

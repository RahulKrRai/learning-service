# Multi-Tenant Trigger & Notification Service

> Appears at: Logward (your actual system — you cut processing latency 60%). Strong design for Google L5 (event-driven platform), Confluent (Kafka fan-out), Amazon (notification service like SNS/SES), Uber (rule-based dispatch alerts).

## 1. Requirements

**Functional:**
- Enterprise tenants define triggers: "when container X enters port Y, send a webhook to endpoint Z"
- Triggers can be condition-based (event matches a rule) or threshold-based (delay exceeds N hours)
- Each trigger fires a notification: webhook, email, or internal event
- Tenants can create/update/delete their own triggers via a management API
- Triggers must fire reliably (at-least-once delivery) with retry and dead-letter handling
- Tenants can view delivery logs (fired at, status, response code)

**Non-functional:**
- Support 1,000 enterprise tenants; each with up to 10,000 trigger rules
- Event throughput: 5,000 events/sec (container events from the tracking platform)
- Trigger evaluation latency: < 500ms from event ingestion to notification dispatch (target < 200ms for 95th percentile)
- Notification delivery: at-least-once; webhook endpoint may be slow or temporarily down
- Per-tenant noisy-neighbor isolation: one tenant's spike must not degrade others
- 99.9% uptime for trigger evaluation

**Clarifying questions:**
1. "Are trigger rules static (predefined types) or fully dynamic (arbitrary expressions)?" → Semi-dynamic: a set of condition types (field equals, field contains, delay threshold) configurable by tenants, not arbitrary code execution.
2. "What's the acceptable notification latency — sub-second, or a few seconds?" → Sub-second preferred for urgent alerts; a few seconds acceptable for batch.
3. "Do tenants need exactly-once delivery or is at-least-once + idempotency key sufficient?" → At-least-once with an idempotency key in the webhook payload is sufficient.

## 2. Back-of-Envelope Estimation

```
Tenants:                1,000
Rules per tenant:       avg 1,000 (max 10,000) = 1M total rules
Events/sec:             5,000 (from container tracking Kafka topic)
Rules evaluated/sec:    worst case 5,000 events × 1,000 rules/event = 5M evaluations/sec
                        (in practice, rules are pre-indexed by container_id/event_type, so fan-out << 1M)

Fan-out (notifications per event): avg 2 triggers fire per event
Notification rate:      5,000 × 2 = 10,000 notifications/sec

Rule storage:           1M rules × 2KB avg = 2 GB (fits in memory with a hot-rule cache)
Delivery log storage:   10,000 deliveries/sec × 500B × 86,400 × 365 = ~158 TB/year
                        → cap retention at 90 days ≈ 39 TB
```

## 3. API Design

```
# Trigger management (tenant-scoped)
POST   /v1/triggers
Body:  { name, condition: { event_type, field, operator, value }, action: { type: "webhook", url, headers }, tenant_id (from JWT) }
→ { trigger_id }

GET    /v1/triggers                    → list of tenant's triggers
GET    /v1/triggers/{trigger_id}       → trigger detail
PUT    /v1/triggers/{trigger_id}       → update
DELETE /v1/triggers/{trigger_id}       → soft delete

# Delivery logs
GET    /v1/triggers/{trigger_id}/deliveries?from=ISO8601&to=ISO8601
→ [{ delivery_id, fired_at, status, response_code, response_time_ms, attempts }]

# Webhook payload (what the tenant receives)
POST {tenant_endpoint}
Headers: X-Logward-Signature: HMAC-SHA256(payload, tenant_secret)
Body: { trigger_id, event_id, idempotency_key, fired_at, event_data: {...} }
```

## 4. High-Level Architecture

```
Container Events (Kafka)
  topic: enriched.events
        │
        ▼
┌──────────────────────────────────────────┐
│  Trigger Evaluation Service              │
│  - Consumes enriched.events              │
│  - Loads matching rules from Rule Cache  │
│  - Evaluates conditions                  │
│  - Publishes matched triggers to         │
│    topic: trigger.firings                │
└──────────────┬───────────────────────────┘
               │
               ▼  (one partition per tenant for isolation)
        Kafka: trigger.firings
               │
               ▼
┌──────────────────────────────────────────┐
│  Notification Dispatcher Service         │
│  - Per-tenant consumer groups            │
│  - Rate limiting per tenant              │
│  - HTTP webhook delivery with retries    │
│  - DLQ on exhausted retries              │
└──────────┬───────────────────────────────┘
           │
           ├──► PostgreSQL (delivery log)
           └──► DLQ topic: trigger.firings.dlq
                    │
                    ▼
             Dead-Letter Processor (alert ops, manual requeue)

Rule Store:
  PostgreSQL (source of truth for rules)
  Redis (hot rule cache, keyed by event_type + container_id)
  Rule Cache Refresher (watches DB changes, updates Redis)
```

## 5. Data Model

```sql
-- Trigger rules
CREATE TABLE trigger_rules (
  trigger_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL,
  name          TEXT NOT NULL,
  event_type    TEXT NOT NULL,       -- index for fast lookup
  condition     JSONB NOT NULL,      -- { field, operator, value }
  action_type   TEXT NOT NULL,       -- 'webhook' | 'email'
  action_config JSONB NOT NULL,      -- { url, headers } or { email }
  secret        TEXT,                -- for HMAC signing
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL,
  updated_at    TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_rules_tenant_event ON trigger_rules(tenant_id, event_type) WHERE is_active;

-- Delivery log (partitioned by fired_at, 90-day retention)
CREATE TABLE deliveries (
  delivery_id     UUID PRIMARY KEY,
  trigger_id      UUID NOT NULL,
  tenant_id       UUID NOT NULL,
  event_id        UUID NOT NULL,
  idempotency_key TEXT NOT NULL UNIQUE,
  fired_at        TIMESTAMPTZ NOT NULL,  -- partition key
  status          TEXT NOT NULL,         -- PENDING | SUCCESS | FAILED | DLQ
  attempts        INT DEFAULT 0,
  last_attempt_at TIMESTAMPTZ,
  response_code   INT,
  response_time_ms INT
);

-- Redis hot cache: key = "rules:{event_type}" → [rule JSON]
-- Invalidated on rule create/update/delete (CDC or app-level pub/sub)
```

## 6. Deep Dives

### 6a. How the -60% Latency Improvement Was Achieved

**The bottleneck (before):** Trigger evaluation was synchronous — for every incoming container event, the service queried the DB for matching rules, evaluated conditions, and made the webhook HTTP call, all in series. This meant:
- DB query for rules: ~20-50ms per event
- Condition evaluation (in Python): ~5ms
- Webhook HTTP call: ~50-500ms (blocking the evaluation loop)
- Total per event: 75-550ms; at 5,000 events/sec this was a queue-building problem

**What changed:**
1. **Separated evaluation from dispatch:** Evaluation now just writes a `trigger.firings` message to Kafka (< 5ms). Dispatch is handled by a separate consumer service. The evaluation hot path is now < 10ms.
2. **Pre-loaded rule cache in Redis:** Instead of querying PostgreSQL per event, the Evaluation Service loads rules from Redis (keyed by `event_type`). Cache TTL = 30s; invalidated immediately on rule change via a CDC-triggered pub/sub. Eliminated the 20-50ms DB query from the hot path.
3. **Compiled conditions:** Condition expressions (e.g. `status == "AT_PORT" AND delay_hours > 24`) are pre-compiled at rule-load time into Python functions (using `eval` on a restricted AST). Evaluation per rule is now ~0.1ms instead of ~5ms.
4. **Result:** Evaluation latency dropped from ~75ms to ~12ms (p95). With async dispatch, the end-to-end notification delivery latency (event to webhook fired) dropped from ~600ms to ~250ms — a ~58% reduction.

### 6b. Per-Tenant Isolation & Noisy-Neighbor Prevention

**Problem:** Tenant A sends a bulk upload of 100K container events in 30 seconds. Without isolation, this floods the evaluation queue and delays notifications for all other tenants.

**Solutions:**
1. **Per-tenant Kafka partitions for `trigger.firings`:** Partition key = `tenant_id`. Each tenant's firing events are on their own partition(s). A slow dispatcher for tenant A (e.g. their webhook endpoint is slow) doesn't block tenant B.
2. **Per-tenant consumer groups for dispatch:** Each tenant (or tenant tier) has a separate consumer group for the Dispatcher. Tenant A's consumer group falling behind doesn't affect tenant B's consumer group.
3. **Token bucket rate limiting per tenant in the Dispatcher:** Even if tenant A fires 10,000 notifications in 10 seconds, the Dispatcher enforces `max_rps_per_tenant` (e.g. 100/sec for standard tier, 1,000/sec for enterprise). Excess requests are queued or back-pressured.
4. **Bulkhead pattern:** Separate thread pools in the Dispatcher per tenant tier (premium vs standard). Premium tenants get dedicated worker threads and are never blocked by standard tenants.

### 6c. Retry & Dead-Letter Queue

```
Attempt 1: immediate
Attempt 2: +30s (if 5xx or timeout)
Attempt 3: +5m
Attempt 4: +30m
Attempt 5: +2h
After 5 failures → move to DLQ topic
```

Tenants are alerted when a trigger enters DLQ. Ops team can inspect and manually requeue. Each attempt records `response_code` and `response_time_ms` in the delivery log — visible in the tenant dashboard.

**Idempotency:** Each webhook delivery carries `idempotency_key = SHA256(trigger_id + event_id)`. The tenant's endpoint can deduplicate retries using this key.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x scale (10,000 tenants, 50K events/sec):**
- Rule cache: 10M rules × 2KB = 20GB — exceeds single Redis instance. Shard by `hash(tenant_id) % N` across Redis cluster.
- Kafka: increase topic partitions from 100 to 1,000. Scale Evaluation Service consumers to 1,000.
- Dispatcher: add more consumer instances per tenant group; consider per-tenant queue service (Celery with Redis backend) for finer rate control.

**Failure modes:**
- Redis rule cache down: fall back to PostgreSQL (slower but correct); degraded latency for 30s until Redis recovers.
- Kafka partition leader election: ~10-30s downtime per partition; events queued at producer, no loss.
- Tenant webhook endpoint slow: only affects that tenant's dispatcher consumer group (per-tenant isolation); retries accumulate in Kafka.
- Condition evaluation bug crashes a worker: Kafka consumer fails to commit offset; events reprocessed on restart. Since deliveries are idempotent (unique `idempotency_key` in DB), duplicate firing is prevented.

**Trade-offs:**
- At-least-once delivery + idempotency key vs exactly-once: we chose at-least-once. EOS would require Kafka transactions across the evaluation and dispatch boundary — complex and slower. At-least-once + idempotency key in the webhook payload is sufficient for 99% of use cases.
- Synchronous rule evaluation (simple, consistent) vs async + cache (complex, faster): we chose async + cache after measuring the latency problem. The cache invalidation complexity is manageable with CDC.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: are rules dynamic or templated? Delivery latency SLA? Exactly-once or at-least-once?
3-6 min:  Estimation: 5M rule evaluations/sec worst-case → justify the need for a pre-indexed rule cache.
6-12 min: Draw the architecture. Key insight: separate evaluation (fast, in-memory, < 10ms) from dispatch (async, retries).
12-18 min: Data model. Trigger rules in Postgres + Redis. Delivery log with 90-day retention.
18-28 min: DEEP DIVE: How you achieved -60% latency (async dispatch + rule cache + compiled conditions). This is your authority story — tell it like a war story.
28-35 min: Per-tenant isolation: per-tenant Kafka partitions + consumer groups + token bucket. Bulkhead pattern.
35-40 min: Retry/DLQ. Failure modes.
40-43 min: 10x bottlenecks: Redis cluster sharding, more Kafka partitions.
43-45 min: Open for questions.
```

**Authority hook:** *"I built and own this service at Logward. The -60% latency came from a specific bottleneck I'll walk you through. Here's what the system looks like now vs. what we'd change at 10x the tenant count."*

## Resources

**Free:**
- [System Design Primer — message queues](https://github.com/donnemartin/system-design-primer)
- [Confluent blog — multi-tenancy with Kafka](https://www.confluent.io/blog/)
- [ByteByteGo — notification system design](https://www.youtube.com/results?search_query=bytebytego+notification+system+design)

**Paid (optional):**
- [ByteByteGo](https://bytebytego.com) — Chapter: Design a Notification System

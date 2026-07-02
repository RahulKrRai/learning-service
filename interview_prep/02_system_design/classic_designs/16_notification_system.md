# Notification System (Push / SMS / Email)

> Appears at: everyone — Confluent, Google L5, Uber, Amazon L6, Atlassian. A bread-and-butter design that tests fan-out, queueing, reliability, and product nuance (preferences, rate limits, templating). **Lead with your real experience:** you built a multi-tenant Trigger/notification service at Logward that cut latency ~60% — open by saying that, then design the general version. It buys instant credibility and lets you speak from scars, not slides.

## 1. Requirements

**Functional:**
- Send a notification to a user across one or more channels: push (iOS/Android/web), SMS, email.
- Channel-agnostic core: callers say "notify user X with template Y and params Z" — they don't pick providers.
- User preferences: opt-in/opt-out per channel, per notification category (marketing vs transactional), quiet hours.
- Templating: named templates with variable substitution + localization (per-locale copy).
- Scheduling: send now, send-at (future timestamp), recurring.
- Batching/digest: collapse many low-priority events into a single periodic notification.
- Analytics: delivery status, opens/clicks (see §7).

**Non-functional:**
- ~Hundreds of millions of notifications/day across channels (assume 500M/day).
- At-least-once delivery for transactional notifications; no silent drops.
- No duplicate sends (dedup) even under retries.
- Multi-tenant (your Logward angle): per-tenant isolation, quotas, rate limits.
- p99 enqueue-to-dispatch < 1s for transactional; marketing can lag minutes.
- Providers are unreliable and rate-limited — must failover and back-pressure.

**Clarifying questions:**
1. "Transactional, marketing, or both?" → Both, but priority differs. Transactional (OTP, password reset) is latency-critical and must not be dropped; marketing is bulk and best-effort.
2. "At-least-once or exactly-once?" → At-least-once delivery + idempotency/dedup keys. True exactly-once across third-party providers is impossible (you can't un-send an SMS).
3. "Do we own the channel transports?" → No. We integrate provider adapters (APNS/FCM, Twilio/SNS, SES/SendGrid). Our job is routing, reliability, preferences — not the wire protocol.
4. "Multi-tenant?" → Yes. Tenant is a first-class dimension on rate limits, templates, and analytics.

## 2. Back-of-Envelope Estimation

```
Total volume:        500M notifications/day
Avg rate:            500M / 86,400s ≈ 5,800/sec
Peak (10x bursty):   ~58,000/sec   (marketing blasts, product launches)

Channel mix (assume):
  push  70% → 350M/day → ~4,050/sec avg
  email 25% → 125M/day → ~1,450/sec avg
  sms    5% →  25M/day →   ~290/sec avg

Payload (event in queue):
  user_id + template_id + params (JSON) + metadata ≈ 1 KB
Daily queue throughput:  500M × 1KB = 500 GB/day flowing through Kafka

Device tokens (push):
  ~200M users × 2 devices × 256B token ≈ 100 GB → Postgres + Redis cache

Dedup window:
  Store dedup keys 24h. 500M keys/day × ~64B ≈ 32 GB in Redis (TTL'd).

Provider rate caps (real constraints, not ours):
  APNS:   high, but per-connection throttling
  FCM:    ~ generous, batch up to 500 tokens/multicast
  Twilio: ~1 msg/sec per number by default → need number pools
  SES:    starts at 14/sec, request increases; sandbox limits hurt
```

Takeaway you say out loud: "Provider limits, not our compute, are the real bottleneck. The design is mostly about absorbing bursts and respecting downstream caps."

## 3. API Design

```
# Send a notification (the one endpoint callers use)
POST /api/v1/notifications
Headers: X-Tenant-Id, Idempotency-Key: <uuid>
Body: {
  user_id:      "u_123",
  template_id:  "order_shipped",
  channels:     ["push","email"],         # optional; default = user prefs
  params:       { "order_id": "A-9", "eta": "Tue" },
  locale:       "de-DE",                   # optional; default from user profile
  priority:     "transactional",          # transactional | marketing
  send_at:      "2026-06-22T09:00:00Z"     # optional; omit = send now
}
→ 202 Accepted { notification_id: "n_abc", status: "queued" }
   (async — we acknowledge intake, not delivery)

# Delivery status (analytics path)
GET /api/v1/notifications/{notification_id}
→ { id, per_channel: [{channel:"push", status:"delivered", at:"..."},
                      {channel:"email", status:"bounced", reason:"..."}] }

# User preferences
GET  /api/v1/users/{user_id}/preferences
PUT  /api/v1/users/{user_id}/preferences
Body: { push: {enabled:true}, email:{enabled:true, marketing:false},
        sms:{enabled:false}, quiet_hours:{start:"22:00", end:"07:00", tz:"Europe/Berlin"} }

# Device registration (push)
POST /api/v1/users/{user_id}/devices
Body: { platform:"ios", token:"<apns-token>", app_version:"3.2.1" }

# Template management (admin)
POST /api/v1/templates
Body: { template_id, channel, locale, subject, body, version }
```

The `Idempotency-Key` is load-bearing — it's how a caller retrying a timed-out request avoids double-sending. See §6b.

## 4. High-Level Architecture

```
   Callers (services, cron, marketing tool)
        │  POST /notifications  (+Idempotency-Key)
        ▼
┌──────────────────────┐
│  Notification API    │  validate, resolve idempotency, write intake row
│  (stateless, scaled) │
└──────────┬───────────┘
           │ publish event
           ▼
   ┌───────────────────────────────┐
   │  Kafka: topic "notify.intake" │   ← durable buffer, absorbs bursts
   └───────────────┬───────────────┘     (see 06_distributed_message_log_kafka.md)
                   ▼
        ┌─────────────────────┐
        │  Routing / Core     │  per event:
        │  Workers            │   1. load user prefs + devices
        │ (consumer group)    │   2. apply opt-out / quiet-hours
        └─────────┬───────────┘   3. rate-limit check
                  │                4. render template (per channel+locale)
                  │                5. dedup check
                  │   fan-out one event → N per-channel messages
       ┌──────────┼───────────┐
       ▼          ▼           ▼
  ┌─────────┐┌─────────┐┌─────────┐   per-channel Kafka topics
  │notify.  ││notify.  ││notify.  │   (independent back-pressure & retry)
  │push     ││email    ││sms      │
  └────┬────┘└────┬────┘└────┬────┘
       ▼          ▼          ▼
  ┌─────────┐┌─────────┐┌─────────┐   Channel Senders
  │ Push    ││ Email   ││ SMS     │   (provider adapters + failover)
  │ Sender  ││ Sender  ││ Sender  │
  └──┬───┬──┘└──┬───┬──┘└──┬───┬──┘
     │   │      │   │      │   │
   APNS FCM   SES SendG  Twilio SNS    third-party providers
     │   │      │   │      │   │
     └───┴──────┴───┴──────┴───┘
            │ provider webhooks (delivered/bounced/clicked)
            ▼
   ┌───────────────────┐      ┌──────────────────┐
   │ Status/Analytics  │◄─────│ Kafka analytics   │
   │ (ClickHouse)      │      │ events            │
   └───────────────────┘      └──────────────────┘

Side services:
  - Scheduler (send_at / recurring) → see 08_distributed_job_scheduler.md
  - Template Service (versioned templates + localization, cached)
  - Preference Store (Postgres + Redis cache)
  - Rate Limiter (Redis) → see 01_rate_limiter.md
  - Dead Letter Queue per channel
```

**Flow in one breath:** API accepts → Kafka intake buffers → routing workers expand a logical notification into per-channel jobs (after prefs/rate-limit/template/dedup) → per-channel topics → channel senders talk to providers with retries/failover → provider webhooks feed status back into analytics.

## 5. Data Model

```sql
-- Postgres: source of truth for users, prefs, devices, intake records.

CREATE TABLE notification_intake (
  id              UUID PRIMARY KEY,
  tenant_id       UUID NOT NULL,
  user_id         UUID NOT NULL,
  idempotency_key TEXT NOT NULL,
  template_id     TEXT NOT NULL,
  params          JSONB NOT NULL,
  priority        TEXT NOT NULL,           -- transactional | marketing
  send_at         TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (tenant_id, idempotency_key)       -- dedup at intake (see 6b)
);

CREATE TABLE user_preferences (
  user_id     UUID PRIMARY KEY,
  push        BOOLEAN DEFAULT TRUE,
  email       BOOLEAN DEFAULT TRUE,
  sms         BOOLEAN DEFAULT FALSE,
  marketing   BOOLEAN DEFAULT TRUE,         -- transactional always allowed
  quiet_start TIME, quiet_end TIME, tz TEXT
);

CREATE TABLE devices (
  id          UUID PRIMARY KEY,
  user_id     UUID NOT NULL,
  platform    TEXT NOT NULL,                -- ios | android | web
  token       TEXT NOT NULL,
  valid       BOOLEAN DEFAULT TRUE,         -- flipped false on provider "unregistered"
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_devices_user ON devices(user_id) WHERE valid;

-- Per-delivery status (one row per channel attempt)
CREATE TABLE deliveries (
  id              UUID PRIMARY KEY,
  notification_id UUID NOT NULL,
  channel         TEXT NOT NULL,
  provider        TEXT,
  status          TEXT NOT NULL,           -- queued|sent|delivered|bounced|failed
  attempts        INT DEFAULT 0,
  provider_msg_id TEXT,                     -- to correlate webhooks
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

```nosql
# Redis (hot path, all TTL'd):
dedup:{tenant}:{dedup_key}   → "1"  EX 86400         # 6b dedup
rate:{user}:{channel}        → token bucket state    # 6c, see 01_rate_limiter.md
prefs:{user}                 → cached preference blob EX 300
devices:{user}               → cached valid tokens   EX 300

# ClickHouse (analytics, append-only, see §7):
events(notification_id, tenant_id, channel, event_type, ts, geo, metadata)
```

**Shard keys:**
- Kafka intake/per-channel topics: **partition by `user_id`** → preserves per-user ordering and keeps a user's rate-limit/dedup checks on one consumer (sticky, fewer cross-node races).
- Postgres `deliveries`/`intake`: shard by **`tenant_id`** (multi-tenant isolation; one noisy tenant doesn't bloat another's table).
- ClickHouse: partition by **`(tenant_id, toDate(ts))`** for cheap per-tenant per-day rollups.

## 6. Deep Dives

### 6a. Multi-Channel Fan-Out + Provider Abstraction

The core mistake juniors make is letting business logic know about APNS vs FCM. Don't. The core emits a **channel-agnostic dispatch intent**; an adapter layer translates per provider.

```python
# Channel-agnostic core: one logical notification → N channel jobs.
def route(event):
    prefs   = prefs_store.get(event.user_id)        # cached
    devices = device_store.get(event.user_id)
    for channel in resolve_channels(event, prefs):  # honors opt-out, see 6c
        if not allowed(event, channel, prefs):      # quiet hours, marketing flag
            continue
        if not rate_limiter.allow(event.user_id, channel):  # see 01_rate_limiter
            defer_or_drop(event, channel); continue
        rendered = template_svc.render(event.template_id, channel,
                                       event.locale, event.params)
        job = ChannelJob(event.notification_id, channel, rendered,
                         targets=targets_for(channel, devices, prefs))
        kafka.produce(f"notify.{channel}", key=event.user_id, value=job)

# Adapter interface — every provider implements the same contract.
class ProviderAdapter:
    def send(self, job) -> SendResult: ...        # returns provider_msg_id or error
    def healthy(self) -> bool: ...

# Channel sender picks an adapter, with failover:
class PushSender:
    def __init__(self):
        self.adapters = {"ios": [APNSAdapter()], "android": [FCMAdapter()]}
    def handle(self, job):
        for target in job.targets:
            adapter = self._pick_healthy(target.platform)
            try:
                res = adapter.send(job.for_target(target))
                deliveries.mark(job.id, "sent", res.provider_msg_id)
            except ProviderUnregistered:
                device_store.invalidate(target.token)   # stop sending to dead token
            except ProviderError as e:
                retry_or_dlq(job, target, e)             # see 6b
```

**Per-channel queues (why separate topics):** push, email, SMS have wildly different throughput, latency, and provider rate caps. A Twilio outage must not back up your push pipeline. Independent topics + consumer groups give each channel its own back-pressure, retry cadence, and scaling. This is exactly the durable-log pattern from [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md) — the log is your shock absorber.

**Provider failover & health:** Keep a health signal per adapter (rolling error rate / circuit breaker). On repeated failures, trip the breaker and route to a secondary (SES→SendGrid, Twilio→SNS). Half-open probes restore it. Crucial nuance: failover only for *transient* errors (5xx, timeouts). A hard bounce ("invalid number", "token unregistered") is terminal — don't retry, mark the target invalid.

### 6b. Reliability — At-Least-Once, Retries, Dedup, Ordering

**At-least-once = ack only after success.** A channel sender consumes a job, sends to the provider, and only commits its Kafka offset after the provider accepts (or after DLQ). Crash before commit → message redelivered → may send twice. We tolerate that and lean on dedup.

**Retries with exponential backoff + jitter:**
```python
def retry_or_dlq(job, target, err):
    if not err.transient:                 # hard bounce → terminal
        deliveries.mark(job.id, "failed", reason=err.reason); return
    job.attempts += 1
    if job.attempts > MAX_ATTEMPTS:       # e.g. 6
        dlq.produce(f"notify.{job.channel}.dlq", job)   # park for inspection
        deliveries.mark(job.id, "failed", reason="max_retries")
        return
    delay = min(BASE * 2 ** job.attempts, CAP) + random.uniform(0, JITTER)
    schedule_retry(job, after=delay)      # via delay topic or scheduler (08)
```
Backoff prevents hammering a struggling provider; jitter prevents a thundering-herd retry spike. The **DLQ** captures the poison messages so a human/automated job can replay them once the cause is fixed.

**Idempotency / dedup (two layers):**
1. *Intake dedup* — `UNIQUE(tenant_id, idempotency_key)` in Postgres. A caller retrying a timed-out POST with the same key gets the same `notification_id`, not a second notification.
2. *Send dedup* — before a sender hits the provider, `SET dedup:{tenant}:{key} 1 NX EX 86400`. If the key already exists, skip — this catches Kafka redelivery. Build the key from `(notification_id, channel, target)` so the same OTP isn't sent twice to the same device.

**Ordering where needed:** Mostly notifications are independent and order doesn't matter. Where it does (e.g. "order placed" must precede "order shipped"), partition the Kafka topic by `user_id` so a single consumer processes that user's events in order. Don't impose global ordering — it kills throughput. Order is a per-user, per-channel property at most.

### 6c. Rate Limiting, Preferences, Templating, Batching

**Per-user / per-channel rate limits.** Protects users from spam *and* you from provider caps. Token bucket in Redis, keyed `rate:{user}:{channel}` (and a separate `rate:{tenant}:{channel}` for tenant quotas). This is the same mechanism as [01_rate_limiter.md](./01_rate_limiter.md) — reuse it, don't reinvent. Transactional traffic gets a higher (or exempt) limit; marketing is throttled hard.

**Preferences & opt-out & quiet hours.** Checked in the routing worker before any provider call:
```python
def allowed(event, channel, prefs):
    if not prefs.channel_enabled(channel): return False
    if event.priority == "marketing" and not prefs.marketing: return False
    if in_quiet_hours(prefs, now_in(prefs.tz)):
        if event.priority == "transactional":
            return True                  # OTPs ignore quiet hours
        defer_until(quiet_end(prefs))    # marketing: hold, send after quiet window
        return False
    return True
```
Compliance matters: an unsubscribe (CAN-SPAM/GDPR) must be honored fast — cache prefs in Redis but invalidate on write.

**Template service + localization.** Templates are versioned and channel-specific (push has title+body+deep-link; email has subject+HTML; SMS is plain, 160-char aware). Render = pick `(template_id, channel, locale)`, substitute params, fall back to default locale if a translation is missing. Cache rendered shells; never store PII in the template cache. Versioning lets you roll back a bad copy change without a deploy.

**Batching / digest.** Low-priority events (e.g. "5 people liked your post") shouldn't be 5 pushes. Buffer per-user in a windowed store; a periodic job (hourly/daily, [08_distributed_job_scheduler.md](./08_distributed_job_scheduler.md)) collapses them into one digest using a digest template. This is also a huge provider-cost reducer.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Scheduling (send_at / recurring).** Future-dated and recurring notifications go to a scheduler, not the intake topic. Reuse the design from [08_distributed_job_scheduler.md](./08_distributed_job_scheduler.md): a time-bucketed store (Redis sorted set keyed by fire time, or a `jobs` table polled by a leader) emits the notification into `notify.intake` when due. Keep the scheduler dumb — it only decides *when*; routing/prefs/rate-limits still apply at fire time (a user may have opted out between scheduling and firing).

**Analytics & click-tracking.** Every lifecycle event (queued, sent, delivered, opened, clicked, bounced) is an append-only event into Kafka → ClickHouse. Opens use a tracking pixel (email) or SDK callback (push); clicks use a redirect/tracking link (the URL-shortener pattern — your own redirect that logs then 302s, see [03_url_shortener.md](./03_url_shortener.md)). Keep this **off the hot send path** — fire-and-forget; losing an analytics event is fine, losing a transactional send is not. Provider webhooks (Twilio/SES delivery receipts) reconcile final status asynchronously and correlate via `provider_msg_id`.

**Failure modes:**
- *One provider down* → circuit breaker trips, failover to secondary; if no secondary, jobs retry then DLQ. Other channels unaffected (per-channel queues).
- *Kafka lag spike* (marketing blast) → intake buffers it; transactional uses a separate high-priority topic/consumer group so OTPs aren't stuck behind a 10M-row campaign. **Priority isolation via separate topics is the key trick.**
- *Redis (rate-limit/dedup) down* → fail open for transactional (better a possible dup OTP than no OTP); fail closed for marketing (skip rather than risk spamming).
- *Duplicate sends* → bounded by dedup keys; worst case a user sees one extra push. Acceptable under at-least-once.
- *Dead device tokens* → providers return "unregistered"; mark device invalid so you stop wasting sends and hurting your sender reputation.

**Trade-offs you should name:**
- At-least-once + dedup over exactly-once: pragmatic; true exactly-once across third parties is impossible.
- Fan-out at routing time vs send time: routing-time fan-out (chosen) isolates channels and lets each scale independently, at the cost of more messages on the bus.
- Push tokens in cache: faster sends, but staleness risk → short TTL + invalidate-on-bounce.
- Sender reputation (email/SMS) is a real constraint: warm up IPs, honor bounces, or providers throttle you.

## 8. Talk Track (35-45 min)

```
0-2 min:   Lead with experience: "I built a multi-tenant notification/Trigger
           service at Logward — cut latency ~60%. Here's how I'd design the
           general version." Instant credibility.
2-5 min:   Clarify: transactional vs marketing, at-least-once + dedup (not
           exactly-once), we own routing not transports, multi-tenant.
5-9 min:   Estimation: 500M/day ≈ 5.8K/s avg, ~58K/s peak; channel mix;
           "provider rate caps are the real bottleneck, not our compute."
9-15 min:  Architecture: API → Kafka intake → routing workers (prefs, rate
           limit, template, dedup, fan-out) → per-channel topics → senders →
           providers; webhooks → analytics. Draw the per-channel split.
15-22 min: DEEP DIVE 6a: channel-agnostic core + provider adapter interface +
           failover/circuit breaker + per-channel queues (ref Kafka design).
22-30 min: DEEP DIVE 6b: at-least-once (ack after success), retries+backoff
           +jitter, DLQ, two-layer dedup (intake UNIQUE + Redis NX), ordering
           by user_id partition only where needed.
30-36 min: DEEP DIVE 6c: rate limits (ref rate limiter), prefs/opt-out/quiet
           hours, templating+localization+versioning, batching/digest.
36-41 min: Scheduling (ref job scheduler) + analytics/click-tracking off the
           hot path + priority isolation for transactional vs marketing.
41-45 min: Failure modes, fail-open-vs-closed for Redis, sender reputation,
           questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — system design](https://www.hellointerview.com)
- [ByteByteGo — notification system design](https://www.youtube.com/results?search_query=bytebytego+notification+system+design)
- [NeetCode — notification / messaging system design](https://www.youtube.com/results?search_query=neetcode+notification+system+design)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a Notification System
- [Grokking the Modern System Design Interview (DesignGurus)](https://www.designgurus.io)

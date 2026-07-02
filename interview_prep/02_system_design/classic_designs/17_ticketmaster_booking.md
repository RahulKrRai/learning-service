# Ticketmaster / Event Booking System

> Appears at: Amazon L6, Atlassian, banks (Goldman/JPM VP — strong fit: transactional integrity, no double-booking). Also Uber-adjacent (inventory + payment). This is THE concurrency-and-consistency design. The whole interview lives or dies on one sentence: **a seat must never be sold twice.** Lead with consistency, justify CP over AP loudly, and spend your depth on the hold/lock pattern. Get this one right and the bank panels love you.

## 1. Requirements

**Functional:**
- Browse events, venues, and seat maps (which seats exist, which are available)
- Reserve (hold) one or more specific seats for a short window while the user pays
- Pay → confirm booking → issue tickets
- Release abandoned holds automatically (user walked away, browser closed)
- Cancel / refund a booking
- Support general admission (no assigned seat, just a count) AND reserved seating (specific seat)

**Non-functional (the ones that matter):**
- **No double-booking.** Ever. A single seat maps to at most one confirmed booking. This is the hard requirement; everything else bends to it.
- **Strong consistency on inventory** — a "booked" seat must be visible as booked to all readers immediately. This pushes us to **CP** (see §7).
- Handle **hot events**: a stadium of 100k seats goes on sale at 10:00:00 and 2M people show up in the first minute (thundering herd).
- Booking confirmation latency < 2s; browse latency < 200ms (browse can be eventually consistent).
- Exactly-once payment: never charge a card twice for one booking.

**Clarifying questions to ask:**
1. "Assigned seats or general admission?" → Both, but assigned seating is where the concurrency lives. Focus there.
2. "Is it acceptable to show a seat as available that's actually held by someone mid-checkout?" → Briefly yes (optimistic display); on submit we validate authoritatively. Never confirm a held seat to two people.
3. "How long is a hold?" → Typically 5-10 minutes. Make it a tunable TTL.
4. "Global or regional?" → Events are inherently regional (a venue is in one place). We can shard inventory by venue/event and avoid cross-region consensus. Big simplification — say it out loud.

## 2. Back-of-Envelope Estimation

```
Catalog:
  Events:                    ~10k active events at a time
  Seats per large event:     ~100,000
  Total seat inventory:      10k events x avg 5k seats = 50M seat rows (small!)

Browse traffic (read-heavy, cacheable):
  Peak browse:               500,000 req/sec during a hot on-sale
  -> served from CDN + Redis seat-map cache, NOT the inventory DB

Booking traffic (the contended path):
  Hot event:                 100k seats, 2M users in first 60s
  Reserve attempts:          2,000,000 / 60s = ~33,000 reserve/sec arriving
  BUT only 100k can ever succeed -> 99.7% must be rejected or queued
  => the system's real job is ADMISSION CONTROL, not raw throughput

Inventory DB write load (after admission control):
  Admit ~ matches supply: let in ~2-3k users/sec to fight over 100k seats
  Each reserve = 1 short transaction (SELECT FOR UPDATE + UPDATE)
  -> ~3,000 write txns/sec on the hot event's shard. A single Postgres can do this.

Storage:
  Booking record ~500B; 100M bookings/year x 500B = 50GB/year. Trivial.
  The scaling problem here is CONTENTION, not volume or storage.
```

The punchline you say in the room: *"The data is tiny. The hard part is 33k people per second fighting over 100k seats with zero tolerance for double-selling. So this is a concurrency-control problem wearing a database costume."*

## 3. API Design

```
# Browse (eventually consistent, cached)
GET /api/v1/events/{event_id}/seatmap
  -> 200 { sections: [...], seats: [{ seat_id, section, row, num, status }] }
     status is a CACHED hint: AVAILABLE | UNAVAILABLE. Authoritative check happens on reserve.

# Reserve / hold seats (the contended write)
POST /api/v1/events/{event_id}/holds
Headers: Idempotency-Key: <uuid>          # client-generated, retry-safe
Body:    { seat_ids: ["A12","A13"], user_id }
  -> 201 { hold_id, seat_ids, expires_at }           # success: seats now HELD for you
  -> 409 Conflict { unavailable: ["A13"] }           # someone beat you to A13
  -> 429 Too Many Requests { retry_after, queue_token } # admission control rejected you

# Confirm booking (after payment authorized)
POST /api/v1/holds/{hold_id}/confirm
Headers: Idempotency-Key: <uuid>
Body:    { payment_token }                # token from payment provider, NOT raw card
  -> 200 { booking_id, ticket_ids[], seat_ids[] }
  -> 410 Gone                              # hold expired before you paid -> retry from reserve
  -> 402 Payment Required                  # payment declined; hold released

# Release a hold explicitly (user clicks "cancel")
DELETE /api/v1/holds/{hold_id}            -> 204

# Virtual waiting room (hot events)
GET /api/v1/events/{event_id}/queue       -> { position, queue_token, est_wait_s }
```

Note the two-phase shape: **hold then confirm.** Payment happens between them. The `Idempotency-Key` on both write endpoints is what makes retries safe (§6c).

## 4. High-Level Architecture

```
                        2M users at on-sale time
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  CDN (seat maps, static)│  browse served here, never hits inventory DB
                    └───────────┬─────────────┘
                                │ booking actions
                                ▼
                    ┌────────────────────────┐
                    │  VIRTUAL WAITING ROOM   │  admission control (Redis token queue)
                    │  (queue + rate limiter) │  lets in ~Nk/sec, holds the rest at a /queue page
                    └───────────┬─────────────┘   see [01_rate_limiter.md](./01_rate_limiter.md)
                                │ admitted requests only
                                ▼
                    ┌────────────────────────┐
                    │   Load Balancer         │
                    └───────────┬─────────────┘
                          ┌─────┴─────┐
                          ▼           ▼
                    ┌─────────┐ ┌─────────┐    Booking Service (stateless, horizontally scaled)
                    │ Book 1  │ │ Book 2  │ ...
                    └────┬────┘ └────┬────┘
                         │           │
        ┌────────────────┼───────────┼──────────────────┐
        ▼                ▼           ▼                  ▼
  ┌───────────┐   ┌──────────────────────┐      ┌──────────────┐
  │ Redis     │   │  Inventory DB         │      │  Payment      │
  │ (holds,   │   │  (Postgres, sharded   │      │  Service /    │
  │  TTLs,    │   │   by event_id) — the  │      │  Provider     │
  │  queue)   │   │   SOURCE OF TRUTH     │      │  (idempotent) │
  └───────────┘   └──────────┬───────────┘      └──────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │ Hold-Expiry Job         │  background sweeper releases stale HELD seats
                    │ (scheduler/worker)      │  see [08_distributed_job_scheduler.md](./08_distributed_job_scheduler.md)
                    └────────────────────────┘

Async (outbox -> Kafka): booking.confirmed -> ticketing, email, analytics, fraud
```

**Two flows, one rule:**
- **Browse flow:** CDN → cached seat map. Stale-but-fast. We tolerate showing a seat as "available" that's momentarily held — the authoritative check is on reserve.
- **Booking flow:** waiting room → booking service → **a single short ACID transaction on the inventory DB** is the only place the no-double-book invariant is enforced. Redis and caches are accelerators, never the arbiter of truth.

## 5. Data Model

```sql
-- Inventory: ONE row per physical seat. This row's state is the source of truth.
-- Shard key: event_id  (all seats of an event live on one shard -> no cross-shard txns)
CREATE TABLE seats (
  seat_id      VARCHAR(20),
  event_id     BIGINT NOT NULL,
  section      VARCHAR(16),
  row          VARCHAR(8),
  num          INT,
  status       VARCHAR(12) NOT NULL DEFAULT 'AVAILABLE', -- AVAILABLE|HELD|BOOKED
  held_by      UUID,                  -- user/hold owning the HELD state
  hold_id      UUID,
  hold_expires TIMESTAMPTZ,           -- when a HELD seat auto-releases
  version      BIGINT NOT NULL DEFAULT 0,  -- for optimistic concurrency control
  booking_id   UUID,
  PRIMARY KEY (event_id, seat_id)
);
CREATE INDEX idx_seats_expiry ON seats (hold_expires) WHERE status = 'HELD';
-- ^ lets the expiry sweeper find stale holds cheaply

CREATE TABLE bookings (
  booking_id   UUID PRIMARY KEY,
  event_id     BIGINT NOT NULL,
  user_id      UUID NOT NULL,
  seat_ids     TEXT[],                -- seats in this booking
  status       VARCHAR(12) NOT NULL,  -- PENDING|CONFIRMED|CANCELLED|REFUNDED
  amount_cents BIGINT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Idempotency ledger: dedupes retried writes (reserve / confirm)
CREATE TABLE idempotency_keys (
  key          VARCHAR(64) PRIMARY KEY,
  request_hash VARCHAR(64),           -- guards key reuse with a different body
  response     JSONB,                 -- cached prior response to replay
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Transactional outbox: written in the SAME txn as the booking,
-- relayed to Kafka so confirmed events are never lost. (exactly-once-ish)
CREATE TABLE outbox (
  id           BIGSERIAL PRIMARY KEY,
  topic        VARCHAR(64),
  payload      JSONB,
  published    BOOLEAN DEFAULT FALSE
);
```

```
Redis structures:
  hold:{hold_id}            -> { seat_ids, user_id }  EX 600   (TTL = the hold clock)
  queue:{event_id}         -> sorted set of waiting users (score = enqueue time)
  admit_token:{event_id}   -> rate-limited token bucket controlling admission
```

**Why shard by `event_id`:** all contention for a given event is on one shard, so the no-double-book transaction is **single-shard, single-node** — plain Postgres ACID, no distributed consensus, no 2PC. Different events scale out across shards independently. A 100k-seat mega-event still fits one node (it's only ~3k writes/sec). This is the most important design decision; say it explicitly.

## 6. Deep Dives

### 6a. Seat reservation under contention — the hold/lock pattern

This is the heart of the interview. Walk the **seat state machine** first:

```
                 reserve (within TTL)            confirm + payment OK
   AVAILABLE ───────────────────────► HELD(ttl) ──────────────────────► BOOKED
       ▲                                 │                                 │
       │   hold expires / user cancels   │                                 │ refund/cancel
       └─────────────────────────────────┘                                 │
       ▲                                                                    │
       └────────────────────────────────────────────────────────────────  ┘
```

The invariant: **a transition into HELD or BOOKED must be atomic and conditional on the seat's current state.** Three ways to enforce it — know all three and their trade-offs:

**Option A — Pessimistic row lock (`SELECT ... FOR UPDATE`).** Lock the row, check state, update. Simplest correct answer.

```sql
BEGIN;
-- Lock the exact seats; rows are locked until COMMIT.
SELECT seat_id, status FROM seats
  WHERE event_id = :eid AND seat_id = ANY(:seat_ids)
  FOR UPDATE;                      -- blocks concurrent FOR UPDATE on same rows

-- App-side: if any selected seat is NOT 'AVAILABLE' -> ROLLBACK, return 409.

UPDATE seats
  SET status='HELD', held_by=:uid, hold_id=:hid,
      hold_expires = NOW() + INTERVAL '10 minutes', version = version + 1
  WHERE event_id = :eid AND seat_id = ANY(:seat_ids) AND status = 'AVAILABLE';
COMMIT;
```
Two users hitting seat A13 simultaneously: the first acquires the row lock; the second blocks, then reads `status='HELD'` after the first commits, and gets a 409. **No double-book, guaranteed by the DB.** Cost: lock contention serializes writers on hot rows. Fine because hot rows drain fast (each seat is booked at most once). Always lock seats **in a deterministic order** (sort by seat_id) to avoid deadlocks on multi-seat holds.

**Option B — Optimistic concurrency (version column).** No lock held across the read; you bet nobody changed the row and verify on write.

```sql
-- Read (no lock):
SELECT version FROM seats WHERE event_id=:eid AND seat_id=:sid AND status='AVAILABLE';
-- Write conditioned on the version you read:
UPDATE seats SET status='HELD', held_by=:uid, hold_id=:hid,
       hold_expires=NOW()+INTERVAL '10 min', version=version+1
  WHERE event_id=:eid AND seat_id=:sid AND status='AVAILABLE' AND version=:v;
-- rows_affected == 0  -> someone else won the race -> retry or 409.
```
Better when contention is *low* (fewer locks held). Under a thundering herd you get a storm of failed updates and retries — which is exactly why we add admission control (§6b) to keep contention low enough that optimistic CAS mostly succeeds.

**Option C — Redis distributed lock (`SET key val NX PX ttl`).** Acquire a lock per seat in Redis before touching the DB. Fast, and the TTL doubles as the hold clock.

```python
# Acquire: NX = only if absent, PX = auto-expire (the hold TTL)
ok = redis.set(f"lock:seat:{event_id}:{seat_id}", hold_id, nx=True, px=600_000)
if not ok:
    raise SeatUnavailable()        # someone holds it
# ... now write HELD to Postgres ...
```
**Caveat — do not let Redis be your source of truth.** A single Redis can lose the lock on failover (the lock lived only on the primary that died). **Redlock** (lock a majority of N independent Redis nodes) reduces this but is still debated (Kleppmann's critique: GC pauses / clock skew can violate it). So: use Redis as a **fast first-line gate to shed contention**, but the **authoritative no-double-book check stays in the Postgres transaction** (Option A/B). Redis says "probably yours"; Postgres says "definitely yours." Belt and suspenders.

**My recommended answer in the room:** `SELECT ... FOR UPDATE` on the single event-sharded Postgres as the authority (simple, provably correct, single-shard), optionally fronted by a Redis NX lock to cheaply reject most losers before they reach the DB. State this clearly — interviewers want to hear you name the authority.

**Background expiry job (releasing abandoned holds).** A user holds 2 seats then closes the tab. Without cleanup, those seats are stuck in HELD forever. A sweeper reclaims them:

```sql
-- Runs every ~10s per shard, batched. Idempotent: only flips seats whose hold truly expired.
UPDATE seats
  SET status='AVAILABLE', held_by=NULL, hold_id=NULL, hold_expires=NULL, version=version+1
  WHERE status='HELD' AND hold_expires < NOW();   -- uses idx_seats_expiry
```
Run it as a leader-elected, sharded background worker — see [08_distributed_job_scheduler.md](./08_distributed_job_scheduler.md) for how to schedule it reliably and avoid two sweepers fighting. Belt-and-suspenders: the Redis hold key *also* has a native TTL, so even if the sweeper lags, the Redis gate frees up. The DB sweeper is the authority; Redis TTL is the accelerator. Crucially, the expiry update is conditional (`hold_expires < NOW()`), so it can never stomp a hold someone just confirmed in a race.

### 6b. Hot event / thundering herd — the virtual waiting room

When 2M users hit "buy" at 10:00:00, you cannot let 33k reserve/sec slam the inventory DB — lock contention collapses throughput and tail latency explodes. **Protect the inventory DB by admitting only as fast as it can serve.**

```
User clicks buy
      │
      ▼
Already have a valid admit_token?  ── yes ──► proceed to Booking Service
      │ no
      ▼
Enqueue in Redis sorted set queue:{event_id} (score = arrival time)
Return /queue page: { position: 48,213, est_wait_s: 240 }
      │
      ▼
Admission controller (token-bucket / leaky-bucket, see 01_rate_limiter.md)
   drips out N admit_tokens/sec, sized to the DB's safe write rate (~2-3k/s)
   pops the head of the queue, hands each a short-lived admit_token
      │
      ▼
Admitted user now allowed past the LB to reserve seats
```

Why this works and what it buys you:
- **Inventory protection:** the DB only ever sees a controlled trickle (≈ its capacity), so `SELECT FOR UPDATE` contention stays bounded and optimistic CAS mostly succeeds. The queue absorbs the 2M-person spike.
- **Fairness & UX:** FIFO-ish ordering beats a random thundering scramble; users see a position and an estimate instead of spinner-of-death timeouts.
- **Bot mitigation:** the queue is a natural choke point to apply CAPTCHA, per-user/IP rate limits, and account-age checks — reuse the rate-limiter machinery from [01_rate_limiter.md](./01_rate_limiter.md).
- **Backpressure, not failure:** excess load becomes a longer wait (429 + retry_after / queue position), never DB meltdown or double-bookings.

Sizing: admit rate ≈ DB safe write throughput ÷ avg attempts-per-success. If 100k seats and a 2x reserve-failure rate, admit ~the rate that lets the inventory drain in a few minutes. Once seats are gone, stop admitting and serve a "sold out" page straight from cache.

### 6c. Payment + idempotency — exactly-once booking, never a double charge

The dangerous window: **hold succeeds → user pays → something fails.** Walk the flow and every failure point.

```
1. RESERVE: seats -> HELD (TTL 10 min). Create booking row status=PENDING.
2. PAY:     client gets payment_token; calls confirm with an Idempotency-Key.
3. Booking Service calls Payment Provider with the SAME idempotency key
   -> provider guarantees: same key charged at most ONCE.
4. On payment AUTHORIZED, in ONE Postgres transaction:
     - flip held seats HELD -> BOOKED (conditioned on status='HELD' AND hold_id=:hid)
     - booking status PENDING -> CONFIRMED
     - write booking.confirmed to the OUTBOX table   (same txn = atomic)
   COMMIT.
5. Outbox relay publishes booking.confirmed to Kafka -> ticketing/email (async).
```

**Idempotency keys (the must-mention).** The client generates a UUID per logical attempt and sends it on both reserve and confirm. The server checks `idempotency_keys`: if the key exists, **replay the stored response** instead of re-executing. So a retry after a network blip (client never saw the 200) returns the same booking, not a second charge.

```python
def confirm(hold_id, idem_key, payment_token, request_hash):
    with db.transaction():
        prior = db.get_idempotency(idem_key)        # SELECT ... FOR UPDATE
        if prior:
            if prior.request_hash != request_hash:
                raise Conflict("key reused with different body")
            return prior.response                    # replay -> no double charge
        # provider is ALSO keyed on idem_key -> charged at most once even if we retry
        auth = payment.charge(payment_token, idempotency_key=idem_key)
        if not auth.ok:
            return Payment402()                      # hold left to expire (or release now)
        booking = mark_booked(hold_id)               # HELD->BOOKED, conditional
        write_outbox("booking.confirmed", booking)
        db.put_idempotency(idem_key, request_hash, response=booking)
        return booking
```

**Failure cases — say each one:**
- *Payment fails:* return 402; leave the hold to expire (seats auto-release via §6a) or release immediately. No charge, no booking. Clean.
- *Payment succeeds but our confirm txn crashes before commit:* the charge happened, the booking didn't. This is the saga gap. Recovery: a **reconciliation/compensation** job scans for authorized-but-unconfirmed payments and either completes the booking (re-run step 4 idempotently — seats still HELD by us) or **refunds** the charge if the hold already expired and the seats were resold. The idempotency key ties the orphan charge back to the hold.
- *Hold expired before the user paid (slow payment):* confirm returns 410 Gone; the user must reselect. Never confirm an expired hold — the `mark_booked` UPDATE is conditioned on `status='HELD' AND hold_id=:hid`, so if the sweeper already freed and resold the seat, `rows_affected==0` and we refuse + refund.
- *Two booking instances try to confirm the same hold (double-submit):* the idempotency ledger row lock serializes them; the second replays the first's response. Exactly-once.

This is a lightweight **saga**: reserve → pay → confirm, with compensation (release hold / refund) on any failed step. Because the booking write and the outbox write share one transaction, the confirmed event is never lost and never duplicated at the source.

## 7. Bottlenecks, Failure Modes & Trade-offs

**CP over AP — the central trade-off.** By CAP, on a partition you must choose. We choose **consistency**: if the inventory shard is unreachable, **reject the booking** (return 503 / keep the user queued) rather than risk selling a seat twice from a stale replica. Browse stays available and eventually-consistent (AP-ish, served from cache); **inventory is strictly CP.** Spell this out: *"I will return errors before I will double-sell a seat. Money and trust beat availability here — this is why banks like this design."*

**DB isolation levels.** The `SELECT FOR UPDATE` approach is correct at **READ COMMITTED** because the row lock plus the `status='AVAILABLE'` predicate in the UPDATE serializes contenders on each seat. If you instead do read-then-write without `FOR UPDATE`, you need **SERIALIZABLE** (or the optimistic `version` check) to prevent a write-skew / lost-update where two txns both read AVAILABLE and both write HELD. Trade-off: SERIALIZABLE adds abort-and-retry overhead; `FOR UPDATE` adds lock-wait. On a hot single seat both are fine because the seat is sold once and contention there ends instantly.

**Hot-row / hot-shard contention.** A single mega-event is one shard; thousands of users fight over the front-row seats. Mitigations: admission control caps the arrival rate (§6b); lock seats in deterministic order to avoid deadlocks; keep transactions tiny (lock → check → update → commit in milliseconds, no network calls — *never* call the payment provider while holding row locks).

**Failure modes:**
- *Redis (holds/queue) down:* lose the fast gate and the waiting room. Fall back to letting the Postgres `FOR UPDATE` path enforce correctness directly (slower, more contention) and degrade the waiting room to a simple rate limiter. **Correctness is never at risk** because Redis was never the authority.
- *Inventory DB primary down:* bookings for that shard pause; fail over to a **synchronous** replica (we accept higher write latency to preserve consistency — no async-replica reads for inventory). Other event shards unaffected.
- *Payment provider down/slow:* holds keep their TTL; if payment can't complete in the hold window, the hold expires, the seat returns to AVAILABLE — no orphaned booking. Reconciliation job mops up any authorized-but-unconfirmed charges.
- *Expiry sweeper down:* Redis hold-key TTLs still free seats; on sweeper restart it catches any DB rows the TTL didn't cover. Two layers, neither alone catastrophic.
- *Outbox relay lag:* confirmed bookings are valid (committed); downstream emails/tickets are merely delayed. Acceptable — the source of truth committed.

**Trade-offs to volunteer:** pessimistic locking (simple, correct, can serialize hot rows) vs optimistic (less locking, retry storms under contention) vs Redis lock (fast, but not an authority). Hold TTL length: short = seats recycle fast but users feel rushed; long = better UX but inventory looks unavailable longer. General admission can skip per-seat rows and use an atomic counter (`UPDATE events SET remaining=remaining-:n WHERE remaining>=:n`) — cheaper, same no-oversell guarantee via the conditional predicate.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: assigned vs GA seating; no-double-book is THE requirement; hold TTL;
           regional events -> shard by event_id (no cross-region consensus). Say "this is CP."
3-6 min:   Estimation. Data is tiny (50GB/yr). Real problem = 33k reserve/sec over 100k seats,
           99.7% must be rejected -> it's an admission-control + concurrency problem.
6-12 min:  Architecture. Two flows: browse (CDN/cache, eventually consistent) and
           booking (waiting room -> booking svc -> ONE ACID txn on event-sharded Postgres).
           Name the source of truth: the seat row. Redis is an accelerator, not authority.
12-16 min: Data model. seats table (status state machine, version, hold_expires),
           bookings, idempotency_keys, outbox. Shard key = event_id and WHY.
16-26 min: DEEP DIVE 6a — hold/lock. Draw AVAILABLE->HELD->BOOKED. Three options:
           SELECT FOR UPDATE (recommended authority), optimistic version, Redis NX+Redlock
           (with the Kleppmann caveat). Prove no double-book. Background expiry sweeper
           (-> 08_distributed_job_scheduler) + Redis TTL as second layer.
26-33 min: DEEP DIVE 6b — thundering herd. Virtual waiting room / token-bucket admission
           (-> 01_rate_limiter). Why: protect the inventory DB; backpressure not failure.
33-40 min: DEEP DIVE 6c — payment + idempotency. hold->pay->confirm saga, idempotency keys,
           outbox in same txn, compensation/reconciliation when payment succeeds but
           confirm fails or hold expired. Exactly-once booking, never double charge.
40-43 min: Bottlenecks: CP vs AP justification, isolation levels (READ COMMITTED + FOR UPDATE
           vs SERIALIZABLE), hot-row contention, failure modes.
43-45 min: Questions / extensions (GA counters, dynamic pricing, resale market).
```

If short on time, the non-negotiable core is **6a** (prove no double-booking) plus the sentence **"inventory is CP — I reject before I double-sell."** Everything else is garnish.

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — consistency, locking, CAP sections
- [Hello Interview — System Design](https://www.hellointerview.com) — has a Ticketmaster/event-booking walkthrough
- [ByteByteGo — Ticketmaster / booking system](https://www.youtube.com/results?search_query=bytebytego+ticketmaster+system+design)
- [NeetCode — design Ticketmaster](https://www.youtube.com/results?search_query=neetcode+ticketmaster+system+design)
- Martin Kleppmann — ["How to do distributed locking" / Redlock critique](https://www.youtube.com/results?search_query=martin+kleppmann+distributed+locking+redlock)

**Paid (optional):**
- "System Design Interview" by Alex Xu (Volume 2) — Chapter: Design a Ticketmaster / Hotel Reservation System (the reservation/inventory pattern is the same)
- [Grokking the Modern System Design Interview](https://www.designgurus.io) — ticket-booking / reservation module

---
Related siblings: [01_rate_limiter.md](./01_rate_limiter.md) · [03_url_shortener.md](./03_url_shortener.md) · [08_distributed_job_scheduler.md](./08_distributed_job_scheduler.md)

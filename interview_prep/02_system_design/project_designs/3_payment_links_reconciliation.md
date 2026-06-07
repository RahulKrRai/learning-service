# Payment Link + Reconciliation System

> Appears at: 56 AI / Razorpay (your actual system — -70% manual collection effort & fraud risk). Strong design for Amazon (financial transactions), Google (payments platform), Atlassian (billing). Banks will ask something close to this.

## 1. Requirements

**Functional:**
- Generate a shareable payment link for a customer (unique URL, pre-filled amount, expiry)
- Customer opens the link and pays via Razorpay (UPI, card, netbanking)
- Razorpay fires a webhook on payment success/failure
- Business receives real-time status updates
- Daily reconciliation: compare internal ledger against Razorpay settlement report
- Detect discrepancies: payments Razorpay shows as settled but not in our DB, and vice versa

**Non-functional:**
- 10,000 payment links created/day; 5,000 payments/day (50% conversion)
- Idempotent link generation (same business request = same link)
- Payment status must be consistent — no double charges, no lost payments
- Reconciliation job runs daily at 2 AM; must complete in < 30 min
- PCI: no card data touches our servers; all card flow goes through Razorpay
- Fraud detection: flag suspicious patterns (velocity, amount anomalies)

**Clarifying questions:**
1. "Is this for B2B invoicing (business creates a link, sends to their customer) or B2C e-commerce checkout?" → B2B invoicing.
2. "Do we need multi-currency or India-only (INR)?" → India-only for now.
3. "What's the expected QPS? Is this a high-throughput payment gateway or moderate B2B volume?" → Moderate — 10K links/day, 5K payments/day.

## 2. Back-of-Envelope Estimation

```
Links created:    10,000/day = ~0.12/sec avg (not write-intensive)
Payments:         5,000/day = ~0.06/sec
Webhook events:   5,000/day (success + failure + refund)

Link storage:     10,000 × 2KB = 20MB/day → 7GB/year (trivial)
Ledger entries:   2 entries per payment (debit + credit) = 10,000/day → ~730K/year

Reconciliation:   Razorpay exports up to 10,000 rows/day — single-threaded comparison in < 5 min
```

Not a high-QPS system. Design challenges are in **correctness, idempotency, and consistency** — not scale.

## 3. API Design

```
# Create payment link
POST /v1/payment-links
Body: { amount_paise, currency: "INR", description, customer_name, customer_email,
        expiry_seconds, idempotency_key, metadata: {} }
→ { link_id, short_url, qr_code_url, expires_at, status: "ACTIVE" }

# Get payment link status
GET /v1/payment-links/{link_id}
→ { link_id, status, amount_paise, payment_id, paid_at, attempts: [] }

# Webhook endpoint (called by Razorpay)
POST /v1/webhooks/razorpay
Headers: X-Razorpay-Signature: <HMAC-SHA256>
Body: { event: "payment.captured", payload: { payment: { id, order_id, amount, status } } }
→ 200 OK (must be fast — Razorpay retries if we return 5xx)

# Reconciliation status
GET /v1/reconciliation/reports/{date}
→ { date, matched: N, our_missing: [...], razorpay_missing: [...], discrepancies: [...] }
```

## 4. High-Level Architecture

```
Business (API client)          Customer (browser)
       │                              │
       │ POST /payment-links          │ opens short URL
       ▼                              ▼
┌─────────────────┐         ┌──────────────────┐
│  Link Service   │         │  Redirect Service │
│  (create/manage)│         │  (resolve short   │
└────────┬────────┘         │   URL → Razorpay) │
         │                  └──────────────────┘
         ▼
    PostgreSQL
    (payment_links,
     ledger_entries)
                             Razorpay
                               │
                               │ webhook
                               ▼
                     ┌──────────────────────┐
                     │  Webhook Handler     │
                     │  1. Verify signature │
                     │  2. Idempotency check│
                     │  3. Update link state│
                     │  4. Write to ledger  │
                     │  5. Fire events      │
                     └──────────────────────┘
                               │
                               ▼
                       Kafka: payment.events
                               │
                     ┌─────────┴──────────┐
                     ▼                    ▼
              Notification           Fraud Detection
              Service                Service
              (email/SMS)            (velocity checks)

Nightly (2 AM):
  ┌──────────────────────────────────────┐
  │  Reconciliation Job                  │
  │  1. Fetch Razorpay settlement report │
  │  2. Compare against internal ledger  │
  │  3. Write discrepancy report         │
  │  4. Alert on gaps                    │
  └──────────────────────────────────────┘
```

## 5. Data Model

```sql
-- Payment links
CREATE TABLE payment_links (
  link_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  idempotency_key  TEXT UNIQUE NOT NULL,   -- prevents duplicate link creation
  short_code       TEXT UNIQUE NOT NULL,   -- base62 short URL suffix
  amount_paise     BIGINT NOT NULL,        -- always store in smallest unit (paise)
  currency         TEXT NOT NULL DEFAULT 'INR',
  status           TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE|PAID|EXPIRED|CANCELLED
  customer_name    TEXT,
  customer_email   TEXT,
  expires_at       TIMESTAMPTZ NOT NULL,
  razorpay_link_id TEXT,                   -- Razorpay's ID for this link
  payment_id       UUID,                   -- FK to payments table on success
  metadata         JSONB,
  created_at       TIMESTAMPTZ NOT NULL
);

-- Payments (one row per successful payment)
CREATE TABLE payments (
  payment_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  link_id           UUID REFERENCES payment_links,
  razorpay_payment_id TEXT UNIQUE NOT NULL,  -- dedup key
  amount_paise      BIGINT NOT NULL,
  status            TEXT NOT NULL,   -- CAPTURED|FAILED|REFUNDED
  paid_at           TIMESTAMPTZ,
  webhook_received_at TIMESTAMPTZ,
  idempotency_key   TEXT UNIQUE NOT NULL,   -- prevent double processing of same webhook
  raw_webhook       JSONB                   -- store raw for audit
);

-- Double-entry ledger
CREATE TABLE ledger_entries (
  entry_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id    UUID NOT NULL,
  entry_type    TEXT NOT NULL,    -- 'DEBIT' | 'CREDIT'
  account       TEXT NOT NULL,    -- 'RECEIVABLE' | 'REVENUE' | 'FEE'
  amount_paise  BIGINT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL
);

-- Reconciliation reports
CREATE TABLE recon_reports (
  report_date    DATE PRIMARY KEY,
  status         TEXT,  -- RUNNING|COMPLETE|FAILED
  matched_count  INT,
  our_missing    JSONB,  -- payments in Razorpay but not our DB
  rz_missing     JSONB,  -- payments in our DB but not Razorpay
  discrepancies  JSONB,  -- amount mismatches
  run_at         TIMESTAMPTZ
);
```

## 6. Deep Dives

### 6a. Idempotency: Preventing Double Charges

**The problem:** Razorpay delivers webhooks at-least-once. If our webhook handler is slow (or crashes mid-processing), Razorpay retries the same event. Without idempotency, we'd mark the payment as successful twice and write two ledger entries.

**Solution:**
```
On webhook receipt:
  1. Parse and verify HMAC-SHA256 signature (X-Razorpay-Signature header)
     → reject if invalid (security: someone is spoofing webhooks)

  2. Check: SELECT * FROM payments WHERE razorpay_payment_id = ? AND idempotency_key = ?
     → if found: return 200 OK immediately (already processed)

  3. Begin transaction:
     INSERT INTO payments (..., idempotency_key) VALUES (...)
     ON CONFLICT (idempotency_key) DO NOTHING  -- DB-level dedup
     UPDATE payment_links SET status = 'PAID', payment_id = ? WHERE link_id = ?
     INSERT INTO ledger_entries (DEBIT, CREDIT pair) ...
     COMMIT

  4. Publish to Kafka: payment.events (for notifications, fraud check)
  5. Return 200 OK
```

The `ON CONFLICT DO NOTHING` on `idempotency_key` ensures that even if the webhook handler runs concurrently for the same event (race condition), exactly one payment row is created.

### 6b. Payment State Machine

```
ACTIVE ──payment initiated──► PROCESSING
PROCESSING ──webhook captured──► PAID
PROCESSING ──webhook failed──► FAILED (can retry)
ACTIVE ──TTL expired──► EXPIRED
PAID ──refund initiated──► REFUND_INITIATED ──► REFUNDED
```

State transitions are enforced in the application layer and the DB (`CHECK` constraint on `status`). Invalid transitions (e.g. EXPIRED → PAID) are rejected.

### 6c. Reconciliation

**Daily job (cron, 2 AM):**
1. Fetch Razorpay settlement report via API (paginated, up to 10K rows/day).
2. Load all our `payments` rows for that date.
3. Full outer join on `razorpay_payment_id`:
   - `in_razorpay AND in_our_db AND amount_matches` → MATCHED ✓
   - `in_razorpay AND NOT in_our_db` → our webhook handler missed it → flag for ops, manually credit ledger
   - `in_our_db AND NOT in_razorpay` → we recorded a payment Razorpay doesn't know about → fraud flag
   - `in_both AND amount_mismatch` → discrepancy → ops investigation
4. Write report to `recon_reports` table. Alert on-call if discrepancies > 0.

**Why this catches fraud:** Scenario — someone manipulates our webhook endpoint to mark a payment as PAID without actually paying. Our DB shows PAID; Razorpay shows no such payment. Reconciliation catches this every morning. This was a key insight in the 56 AI implementation that reduced fraud risk by 70%.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x scale (50K payments/day):**
- Still not a high-QPS system. PostgreSQL handles 5,000 writes/sec easily.
- Razorpay API rate limits reconciliation — use pagination + exponential backoff.
- Ledger table grows: partition by `created_at` (monthly partitions).

**Failure modes:**
- Webhook handler crashes after DB write but before publishing to Kafka: Kafka event is lost. Mitigation: use the **outbox pattern** — write the Kafka event to an `outbox` table in the same transaction, then a CDC process (Debezium) publishes it. Guarantees event is not lost.
- Razorpay is down during reconciliation: retry the next day; flag report as FAILED; alert ops.
- Double webhook (race condition): handled by `ON CONFLICT DO NOTHING` in the transaction.

**Trade-offs:**
- Razorpay-hosted payment page vs our own checkout: Razorpay-hosted keeps us out of PCI scope (card data never touches our servers). Trade-off: less control over UX. For B2B invoicing, this is the right call.
- Real-time reconciliation vs daily batch: daily batch is simpler and sufficient for B2B invoicing. Real-time would require webhooks from Razorpay for every settlement event — more complex, marginal benefit.

## 8. Talk Track (35-45 min)

```
0-3 min:  Clarify: B2B vs B2C? Multi-currency? QPS? → frame this as a correctness problem, not a scale problem.
3-6 min:  Estimation: 10K links/day — point out this is NOT a high-QPS challenge; it's about idempotency and consistency.
6-12 min: Architecture: Link Service → Razorpay link → webhook handler → ledger. Draw the state machine.
12-18 min: Data model: payment_links, payments, ledger_entries (double-entry), recon_reports.
18-28 min: DEEP DIVE: Webhook idempotency. Walk through the exact SQL transaction. This is where you show correctness thinking.
28-35 min: Reconciliation. Walk the full-outer-join logic. Explain how this caught fraud at 56 AI (-70% fraud risk).
35-40 min: Payment state machine. Failure modes. Outbox pattern for Kafka reliability.
40-43 min: PCI: Razorpay-hosted checkout, card data never touches our servers.
43-45 min: Open for questions.
```

**Authority hook:** *"I built this at 56 AI on top of Razorpay. The -70% fraud risk reduction came from the reconciliation job surfacing payments our system recorded but Razorpay didn't — catching manipulation of our webhook handler. Let me walk you through the design."*

## Resources

**Free:**
- [Stripe Engineering: Idempotency](https://stripe.com/blog/engineering) — search "idempotency" on their blog
- [System Design Primer — payment systems](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo — payment system design](https://www.youtube.com/results?search_query=bytebytego+payment+system+design)

**Paid (optional):**
- "Designing Data-Intensive Applications" — Chapter 9 (consistency and consensus)

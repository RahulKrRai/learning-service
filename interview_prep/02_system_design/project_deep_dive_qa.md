# Project Deep-Dive Q&A (Defend Your Decisions)
> One-line: a distinct senior-loop round where an engineer picks one project from your CV and *grills your real technical decisions* — "why this, not that", "what broke", "what would you change". Different from behavioral (that's about *you*) and from system design (that's a hypothetical). This is about proving the depth on your resume is real.

> **Why this exists:** Your [project_designs/](./project_designs/) present your work as clean architectures. This file is the adversarial companion — the questions an interviewer fires *at* those architectures. At L5/Senior/L6, "I built X" isn't enough; you must defend every fork in the road under follow-up pressure. This is your biggest edge (real distributed-systems work) — but only if you can defend it cold. Rehearse these out loud.

---

## How this round works & how to win it

- **Format:** "Tell me about a technically challenging project you owned." You pick (or they pick from your CV). Then 30-40 min of drilling: architecture → a specific decision → tradeoffs → failure modes → what you'd do differently.
- **What they're testing:** depth of ownership (did *you* decide, or ride along?), technical judgment (do you know the alternatives and why you rejected them?), and honesty (can you name what went wrong without spin?).
- **The four moves that win it:**
  1. **Lead with the constraint, not the tech.** "We had multi-tenant isolation + a 10M-row hot path, so..." Decisions make sense only against constraints. State them first.
  2. **Always name the alternative you rejected and why.** "I chose Kafka over SQS because we needed replay + ordered per-key consumption; SQS FIFO caps throughput and can't replay." This single habit reads as senior.
  3. **Quantify.** "-60% latency" needs a "from X ms to Y ms, measured at p99, under Z load." Numbers you can't break down read as fabricated.
  4. **Volunteer a failure.** "The first version deadlocked under concurrent tenant writes — here's how I found it and fixed it." Owning a mistake builds more trust than a flawless story.
- **The trap:** going wide (re-narrating the whole system) when they asked deep (one decision). Answer the question asked, then offer to go deeper.

---

## Universal drill questions (apply to ANY project — prep answers for all four)

1. What was the single hardest technical problem, and what made it hard?
2. What was the key architectural decision, and what did you *not* choose? Why?
3. Where's the bottleneck now? If traffic 10×'d tomorrow, what breaks first?
4. What's the failure mode? What happens on a node/DB/dependency outage mid-operation?
5. How did you guarantee correctness — idempotency, exactly-once, consistency? Prove it.
6. How did you test it, and how did you know it worked in production (metrics/SLOs)?
7. What broke in prod, and what did you learn? What's the RCA you're proudest of?
8. If you rebuilt it today, what would you change — and what would you keep?
9. What was the tradeoff you're least sure was right?
10. How did you roll it out safely (migration, canary, backfill) without downtime?

---

## Project 1 — Container Tracking Platform (Logward)
*10M+ records, multi-tenant, real-time.* Full design: [project_designs/1_container_tracking_platform.md](./project_designs/1_container_tracking_platform.md)

**Likely probes & how to defend:**
- **"How do you enforce tenant isolation at 10M rows?"** → Name your actual choice (shared DB + tenant_id row-level vs schema-per-tenant vs DB-per-tenant) and defend the tradeoff: shared-schema scales operationally but needs a tenant_id on every index + query guard (and the risk = a missing filter leaks data — how did you prevent it? middleware/row-level security). Have the answer ready.
- **"What's the read/write ratio, and how is the hot path indexed?"** → Give the shape (read-heavy tracking lookups), the composite indexes, and where you cache. If you denormalized, say why.
- **"A tracking event arrives out of order or twice — what happens?"** → Idempotency key / event dedup / last-write-wins by event timestamp. This is a classic follow-up; have a crisp answer.
- **"10× the tenants tomorrow — first thing to break?"** → Probably a shared hot table / connection pool / a per-tenant N+1. Name it and the mitigation (sharding key = tenant_id, read replicas, partitioning).
- **Failure you can volunteer:** a query missing the tenant filter, a slow migration on a big table, or a noisy-neighbour tenant — pick a real one and tell the RCA.

## Project 2 — Multi-Tenant Trigger Service (Logward, −60% latency)
*The one to know cold — best latency-win story.* Full design: [project_designs/2_multitenant_trigger_service.md](./project_designs/2_multitenant_trigger_service.md)

**Likely probes & how to defend:**
- **"−60% from what to what, measured how?"** → Have the before/after numbers, the percentile (p99 not avg), the load, and the measurement method. This *will* be probed; a vague answer sinks the story.
- **"What actually caused the 60%? Attribute it."** → Break it down: e.g. batching, async processing, removing a synchronous DB hop, a Kafka-backed queue replacing polling, caching. Know which change bought which slice.
- **"Why Kafka (or your queue) over alternatives?"** → Replay, ordered per-key, decoupling producer/consumer, backpressure. What you rejected (SQS/RabbitMQ/direct calls) and why.
- **"Exactly-once or at-least-once? How do you handle a duplicate trigger firing?"** → Almost certainly at-least-once + idempotent consumer (dedup key, idempotent side-effect). Explain the idempotency mechanism concretely.
- **"How do you stop one tenant's burst from starving others?"** → Per-tenant rate limiting / fair scheduling / partitioning. Ties to [classic_designs/16_notification_system.md](./classic_designs/16_notification_system.md).
- **Failure you can volunteer:** a thundering-herd on retry, a poison message stuck in the queue (→ DLQ), or a hot partition.

## Project 3 — Payment Links + Reconciliation (56 AI / Razorpay, −70% fraud/effort)
Full design: [project_designs/3_payment_links_reconciliation.md](./project_designs/3_payment_links_reconciliation.md)

**Likely probes & how to defend:**
- **"How do you guarantee no double-charge / exactly-once payment?"** → Idempotency keys on the payment intent, a state machine for the transaction, dedup on webhook delivery. Payments interviewers push hard here — be precise.
- **"Webhooks are unreliable — retried, out-of-order, duplicated. How do you reconcile?"** → Idempotent webhook handler + a reconciliation job that diffs your ledger against the PSP's source of truth on a schedule. Explain the ledger model.
- **"What does −70% fraud actually mean?"** → Baseline, what you measured (fraud rate / manual-review hours), what mechanism drove it (validation rules, reconciliation catching mismatches). Don't let it sound like a slogan.
- **"Consistency vs availability when the PSP is down?"** → You likely favored correctness (never lose/duplicate money): queue + retry + reconcile rather than fail-open. Defend it.
- **Failure you can volunteer:** a reconciliation mismatch you root-caused (clock skew, a missed webhook, a race between callback and poll).

## Project 4 — Autopay Recurring Scheduler (56 AI, −30% manual ops)
Full design: [project_designs/4_autopay_recurring_scheduler.md](./project_designs/4_autopay_recurring_scheduler.md)

**Likely probes & how to defend:**
- **"How does the scheduler guarantee each mandate fires exactly once at the right time?"** → Claim/lease pattern, idempotent execution, a job store with status transitions. Ties directly to [classic_designs/08_distributed_job_scheduler.md](./classic_designs/08_distributed_job_scheduler.md) — reuse that vocabulary.
- **"Two scheduler instances wake at the same time — double execution?"** → Leader election / distributed lock / atomic claim (SELECT ... FOR UPDATE SKIP LOCKED or a lease with expiry). Explain how a crashed worker's claim is reclaimed.
- **"Clock skew / missed window / server down at fire time — what happens?"** → Catch-up scan for overdue jobs, idempotent so a late run is safe, bounded lateness SLO.
- **"−30% manual ops — from what?"** → What ops task it eliminated (manual retries, reconciliation, failed-payment chasing) and how you measured hours saved.
- **Failure you can volunteer:** a retry storm, a mandate fired twice before you added the claim lock, or a timezone bug in the schedule.

---

## Cross-cutting themes interviewers love (have a crisp line for each)
- **Idempotency** — you touch it in 3 of 4 projects; have one clean definition + mechanism ready.
- **Exactly-once vs at-least-once** — know that true exactly-once = at-least-once delivery + idempotent processing. Say it that way.
- **Multi-tenancy isolation** — noisy neighbour, per-tenant limits, data isolation levels.
- **Consistency model chosen** — and *why* that CAP tradeoff fit the domain (payments = correctness; tracking = availability).
- **Observability** — how you *knew* it worked: the metric, the alert, the SLO. (Cross-ref [engineering_hygiene.md](./engineering_hygiene.md).)

## Rehearsal protocol
- [ ] For each of the 4 projects, I can give the **60-second summary** (problem → constraint → decision → result-with-number).
- [ ] For each, I can answer all 10 universal drill questions out loud without stalling.
- [ ] Every metric on my CV (−60%, −70%, −30%, 10M) breaks down into from → to → how-measured.
- [ ] For each project I have **one alternative-rejected** and **one failure-I-owned** ready.
- [ ] I can go deep on ONE decision for 10 min without re-narrating the whole system.
- [ ] I've said each of these answers out loud, timed — not just read them.

> Pair this with the [behavioral story_bank](../03_behavioral/story_bank.md): behavioral asks "tell me about a conflict/failure" (about you); this round asks "why did you choose X" (about the system). Same projects, different lens — don't blur them.

# Engineering Hygiene — 12-Factor App & Production-Readiness

> The deep-dive and bottleneck sections of a design interview reward *operational maturity*, not just box-drawing. When you say "I'd run this as a 12-factor service behind a rolling deploy with SLO-backed alerting," you signal you've actually operated software at scale — which is exactly the senior bar at Confluent/Google/Uber/Atlassian. You've done on-call at PharmEasy and shipped multi-tenant services at Logward; this file gives you the vocabulary to *name* what you already do.

This is a reference, not a design. Use it to (1) answer "how would you make this production-grade?", (2) score easy points in the bottlenecks/failure-modes steps, and (3) frame your own systems when an interviewer asks how you deployed and operated them.

---

## Part 1 — The 12-Factor App

Originated at Heroku (2011) as a methodology for building SaaS apps that are portable, scalable, and disposable. It predates Kubernetes but maps onto it almost perfectly — K8s is in many ways a 12-factor runtime. Know all twelve; interviewers (especially at infra-heavy companies) drop the term and expect you to keep up.

| # | Factor | One-line rule | What it buys you |
|---|--------|---------------|------------------|
| 1 | **Codebase** | One codebase tracked in version control, many deploys | A single repo maps to an app; dev/staging/prod are deploys of the same code, not forks |
| 2 | **Dependencies** | Explicitly declare and isolate dependencies | `requirements.txt`/`go.mod` + a clean container; never rely on system-wide packages |
| 3 | **Config** | Store config in the environment, not the code | Same artifact ships to every env; secrets never committed |
| 4 | **Backing services** | Treat backing services as attached resources | Swap a local Postgres for RDS by changing a URL — no code change |
| 5 | **Build, release, run** | Strictly separate the three stages | Immutable build → release (build + config) → run; any release is reproducible and rollback-able |
| 6 | **Processes** | Execute as one or more stateless, share-nothing processes | State lives in backing services (DB/Redis), never in process memory or local disk |
| 7 | **Port binding** | Export services via port binding | App is self-contained, binds its own port; no reliance on an injected webserver |
| 8 | **Concurrency** | Scale out via the process model | Scale horizontally by adding processes/pods, not by threading a single big box |
| 9 | **Disposability** | Maximize robustness with fast startup and graceful shutdown | Pods can be killed/rescheduled anytime; fast boot + clean SIGTERM handling = elastic and resilient |
| 10 | **Dev/prod parity** | Keep dev, staging, and prod as similar as possible | Containers + same backing-service types everywhere → "works on my machine" disappears |
| 11 | **Logs** | Treat logs as event streams | App writes to stdout; the platform aggregates/routes — app doesn't manage log files |
| 12 | **Admin processes** | Run admin/management tasks as one-off processes | Migrations, backfills, REPLs run in the same env/codebase as the app, not hand-run on a box |

### The factors worth a sentence of depth (these come up)

- **Factor 3 — Config in the environment.** The litmus test: *could you open-source the codebase right now without leaking any credentials?* If not, config is in the code. Env vars are the baseline; at scale you graduate to a secrets manager (AWS Secrets Manager, Vault, K8s Secrets) injected as env vars or mounted files. Never bake secrets into the image.
- **Factor 6 — Stateless processes.** This is the one that unlocks horizontal scaling. Any request must be serviceable by any instance. Session affinity is a smell; push session state to Redis. This is exactly why your Logward services scale — and why a "sticky session" load balancer is a trade-off you call out, not a default.
- **Factor 9 — Disposability.** Two halves: **fast startup** (so autoscaling and rescheduling are cheap) and **graceful shutdown** (on SIGTERM, stop accepting new work, drain in-flight requests, commit Kafka offsets, close DB connections, *then* exit). For a Kafka consumer this means finishing the current batch and committing before dying — directly relevant to your trigger service.
- **Factor 11 — Logs as streams.** The app does not know or care where logs go. Write structured JSON to stdout; let Fluent Bit / CloudWatch / Loki collect and route. Coupling the app to a log *destination* breaks dev/prod parity.

### Beyond 12-factor (the modern additions)

The original twelve are necessary but no longer sufficient. Senior interviewers expect you to extend them:

- **Telemetry / observability** — metrics, logs, and traces are first-class, not afterthoughts (see Part 3).
- **API as a contract** — versioned, backward-compatible APIs; schema governance (you already do this with the Kafka Schema Registry — BACKWARD compatibility so old consumers don't break).
- **Security as a baseline** — least-privilege IAM, secrets rotation, encryption in transit (TLS) and at rest, no long-lived credentials.
- **Authentication/authorization as a backing concern** — externalize authn/z (OIDC, mTLS between services) rather than hand-rolling per service.

---

## Part 2 — Deploy & Release Hygiene

| Concept | What it is | When you'd name it |
|---------|-----------|--------------------|
| **Immutable artifacts** | Build once, promote the *same* image dev→staging→prod | Guarantees what you tested is what you ship |
| **Rolling deploy** | Replace instances gradually, keeping the service up | Default for stateless services; zero-downtime |
| **Blue-green** | Stand up a full new env, flip traffic at the LB | Instant rollback by flipping back; needs 2x capacity briefly |
| **Canary** | Route 1%→5%→50%→100% to the new version, watch metrics | Catch regressions on real traffic before full rollout |
| **Feature flags** | Decouple *deploy* from *release*; toggle behavior at runtime | Ship dark, enable for 1% of tenants, kill instantly without a redeploy |
| **Backward-compatible migrations** | Expand → migrate → contract (never a breaking schema change in one shot) | Add nullable column → backfill → start writing → drop old column in a later deploy |
| **Idempotent deploys** | Re-running a deploy/migration is safe | Migrations guarded by versioning; no manual one-off SQL on prod |

**The expand/contract migration pattern** is worth memorizing — it's how you do zero-downtime schema changes when old and new code run simultaneously during a rolling deploy:
1. **Expand:** add the new column/table (nullable, non-breaking). Old code ignores it.
2. **Migrate:** backfill data; deploy code that writes to *both* old and new.
3. **Contract:** once all instances are on new code, switch reads to new, stop writing old, drop the old column in a later deploy.

---

## Part 3 — Observability (the three pillars)

If you can't observe it, you can't operate it. Name all three; most candidates only mention logs.

- **Metrics** — numeric time series, cheap to store, great for alerting and dashboards. The **RED method** for request-driven services: **R**ate, **E**rrors, **D**uration. The **USE method** for resources: **U**tilization, **S**aturation, **E**rrors. Push to Prometheus/CloudWatch; alert on SLO burn, not raw thresholds.
- **Logs** — discrete structured events (JSON, with a `trace_id`, `tenant_id`, `request_id`). High-cardinality, expensive at volume — sample aggressively in hot paths.
- **Traces** — the lifecycle of one request across services (OpenTelemetry → Jaeger/Tempo/X-Ray). Indispensable in microservices: shows you *which hop* added the latency. Propagate the trace context (`traceparent` header) across every service and into Kafka message headers.

**Correlate them:** a good incident flow is *alert (metric) → find the trace → pull the logs for that trace_id*. Mention the correlation, not just the three nouns.

---

## Part 4 — SRE Vocabulary (SLI / SLO / SLA / error budget)

These are senior signals. Get the distinction crisp:

- **SLI (Indicator)** — the *measurement*. E.g. "fraction of requests served < 200ms" or "successful requests / total."
- **SLO (Objective)** — the *internal target* for an SLI. E.g. "99.9% of requests < 200ms over 30 days." This is what you alert and engineer against.
- **SLA (Agreement)** — the *external, contractual* promise with consequences (refunds/credits). Always looser than your SLO — you keep headroom between them.
- **Error budget** — `1 − SLO`. At 99.9%, you have 0.1% (~43 min/month) of allowed failure. **The point:** the budget governs release velocity. Budget left → ship fast. Budget exhausted → freeze features, spend on reliability. It turns the dev-vs-ops tension into a number.

> **Availability cheat sheet:** 99.9% ≈ 43 min/month down. 99.99% ≈ 4.3 min/month. 99.999% ≈ 26 sec/month. Each extra nine is ~10x the cost — so the right answer is usually "what does the business actually need?", not "as high as possible."

Adjacent terms: **MTTR** (mean time to recovery — optimize for this over MTBF; failures are inevitable, fast recovery is the lever), **toil** (manual repetitive ops work; SRE goal is to automate it away), **graceful degradation** (shed non-critical features under load rather than fail wholesale — e.g. serve a stale cache instead of erroring).

---

## Part 5 — Resilience Patterns (failure-mode step)

Drop these in step 8 (failure modes) of the design framework:

- **Timeouts** — every network call has one. No timeout = a stuck dependency hangs your whole thread pool.
- **Retries with exponential backoff + jitter** — retry transient failures, but jitter to avoid synchronized retry storms (thundering herd). Cap total attempts.
- **Circuit breaker** — after N consecutive failures, "open" the circuit and fail fast for a cooldown, then half-open to test recovery. Stops cascading failures.
- **Bulkheads** — isolate resource pools (separate thread pools/connection pools per dependency) so one slow dependency can't drown the others.
- **Idempotency keys** — make retries safe (you already know this cold from the payments/reconciliation work).
- **Dead-letter queue (DLQ)** — messages that fail repeatedly go to a DLQ for inspection rather than blocking the partition or being lost.
- **Load shedding / backpressure** — reject or queue excess load early rather than collapsing; propagate backpressure upstream.

---

## Part 6 — Production-Readiness Checklist

A handy mental checklist for "is this service ready to ship?" — also a great thing to *say out loud* in an interview to show operational maturity:

- [ ] Stateless, horizontally scalable, behind a load balancer
- [ ] Config & secrets externalized (no secrets in code/image)
- [ ] Health checks: **liveness** (restart if dead) + **readiness** (don't route traffic until warm)
- [ ] Graceful shutdown on SIGTERM (drain, commit offsets, close connections)
- [ ] Structured logs to stdout with correlation IDs
- [ ] RED/USE metrics + dashboards + SLO-based alerts
- [ ] Distributed tracing with context propagation
- [ ] Timeouts, retries-with-backoff, circuit breakers on every dependency
- [ ] Resource requests/limits set (no noisy-neighbor OOM)
- [ ] Autoscaling policy (HPA on CPU/latency/queue-depth)
- [ ] Zero-downtime deploy (rolling/canary) + tested rollback
- [ ] Backward-compatible migrations (expand/contract)
- [ ] Runbook + on-call ownership defined
- [ ] Backups + tested restore; defined RPO/RTO

---

## How to Use This in Interviews

- **Don't volunteer all of it unprompted** — it'll eat your clock. Deploy 1-2 relevant points per design and go deep only if the interviewer pulls the thread.
- **Best entry points:** the bottlenecks/trade-offs step ("at 10x I'd add a circuit breaker here") and the failure-modes step ("on SIGTERM the consumer drains and commits offsets, so a pod kill never drops a message").
- **Tie to your prod experience.** "We ran the trigger service as stateless pods with readiness probes and SLO-backed alerts; error budget governed our release cadence" beats any textbook recital — it's a *story*, which is your edge.
- **The 12-factor name itself is a shibboleth.** If an interviewer says it, nod and reference 2-3 factors precisely (config in env, stateless processes, disposability). That alone reads as "this person has operated services."

---

## Resources

**Free:**
- [The Twelve-Factor App](https://12factor.net) — read it once, end to end; it's short
- [Google SRE Book](https://sre.google/books/) — free online; SLIs/SLOs/error budgets chapters are the gold
- [Beyond the Twelve-Factor App (Kevin Hoffman, free PDF)](https://www.oreilly.com/library/view/beyond-the-twelve-factor/9781492042631/) — the modern 15-factor extension
- [release-it / 12-factor on K8s](https://kubernetes.io/docs/concepts/) — map each factor onto a K8s primitive

**Paid (optional):**
- "Site Reliability Engineering" & "The SRE Workbook" — O'Reilly (also free online above)
- "Release It!" by Michael Nygard — the canonical resilience-patterns book (circuit breaker, bulkhead originate here)

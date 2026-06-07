# Story Bank — 18 STAR Stories

> All stories are in first person. Every result has a metric. Target delivery: < 2 minutes each. Use these as your source material — adapt wording in the room, never read verbatim.

---

## Real Stories from Your CV

### 1. Multi-Tenant Trigger Service — -60% Processing Latency
**Headline metric:** -60% processing latency  
**Strongest LP:** Dive Deep / Invent and Simplify

**S:** At Logward, our Trigger Service evaluated container tracking rules and fired notifications to enterprise customers. As the platform grew to 1,000+ tenants and 5,000 events/sec, we started seeing notification delays of 400-600ms, causing customer escalations.

**T:** I was tasked with diagnosing the root cause and redesigning the evaluation pipeline without disrupting live traffic.

**A:** I profiled the service and found two bottlenecks: synchronous PostgreSQL rule lookups on every event (20-50ms per event) and blocking webhook HTTP calls inside the evaluation loop (50-500ms). I redesigned the pipeline to separate evaluation from dispatch — evaluation now writes to a Kafka topic, and a separate dispatcher service handles HTTP delivery asynchronously. I also introduced a pre-loaded Redis rule cache with CDC-based invalidation, eliminating the DB round trip from the hot path. I rolled out behind a feature flag, ran A/B comparison on latency metrics, and progressively shifted traffic.

**R:** Processing latency dropped from ~400ms to ~160ms — a 60% reduction. Customer escalations related to notification delays dropped to zero in the following quarter.

---

### 2. Production Incident RCA — Container Tracking Outage
**Headline metric:** Restored service in 47 minutes, RCA published within 24h  
**Strongest LP:** Ownership / Bias for Action

**S:** On a Tuesday morning at Logward, our primary container state API started returning 503 errors. About 30% of API requests were failing, affecting enterprise customers' real-time tracking dashboards.

**T:** I was the on-call engineer. I had to triage the incident, restore service, and ensure we understood the root cause.

**A:** I immediately joined the war room and pulled metrics. Within 5 minutes I identified that our PostgreSQL connection pool was exhausted — a slow query on the `containers` table was holding connections open. I traced the slow query to a missing index on a recently added column (`carrier_ref`) introduced in a deploy two hours earlier. I rolled back the deploy temporarily to restore service, then worked with the DBA to add the index in a non-blocking fashion (`CREATE INDEX CONCURRENTLY`) and re-deployed. I wrote a 5-section RCA (timeline, root cause, contributing factors, immediate fixes, preventive measures) and presented it to stakeholders within 24 hours.

**R:** Service restored in 47 minutes. I added a mandatory "explain analyze" review step to our deploy checklist, preventing a recurrence. No similar incidents in the 6 months following.

---

### 3. Data Validation & Consistency Layer
**Headline metric:** Reduced data inconsistency bugs by ~80% across distributed workflows  
**Strongest LP:** Dive Deep / Think Big

**S:** At Logward, container lifecycle events flowed through multiple microservices. We were getting sporadic data inconsistencies — a container showing as IN_TRANSIT in one service but DELIVERED in another — causing incorrect customer notifications and manual reconciliation work.

**T:** I was responsible for designing and building a cross-service validation layer that would catch these inconsistencies before they reached customers.

**A:** I mapped all the event flows and identified 12 consistency invariants (e.g. "a container can't transition from DELIVERED back to IN_TRANSIT"). I built a validation service that consumed events from Kafka and applied these rules, routing invalid events to a quarantine queue with enriched error context. I also added a daily reconciliation job that compared container states across the three primary services and alerted on divergence. I worked with each service team to fix the upstream sources of invalid events over 4 weeks.

**R:** Data inconsistency bugs dropped by approximately 80% within 6 weeks of launch. The quarantine queue caught ~200 invalid events/day in the first month, giving us a clear roadmap of what to fix upstream.

---

### 4. Container Lifecycle Event Orchestration
**Headline metric:** Reduced manual ops intervention by 65% for lifecycle event handling  
**Strongest LP:** Invent and Simplify

**S:** At Logward, container lifecycle events (loading, departure, arrival, customs clearance) arrived from multiple carrier APIs in inconsistent formats and out of order. Ops teams were manually reconciling these events in spreadsheets to determine the correct current state.

**T:** I designed the backend orchestration layer that would automatically determine container state from raw events, handle out-of-order delivery, and eliminate manual reconciliation.

**A:** I implemented a state machine for container lifecycle using a Kafka-backed event log as the source of truth. The state machine applied events in timestamp order (buffering out-of-order events for up to 30 minutes). I standardized the event schema across 8 carrier integrations using an adapter pattern. I added idempotency checks so duplicate events from carriers didn't cause incorrect state transitions.

**R:** Manual ops intervention for lifecycle events dropped 65%. Time to accurate container state update fell from hours (when ops was involved) to under 30 seconds. Onboarding a new carrier integration now takes 2 days instead of 2 weeks.

---

### 5. Razorpay Payment Link Integration — -70% Manual Collection Effort
**Headline metric:** -70% manual collection effort and fraud risk  
**Strongest LP:** Customer Obsession / Invent and Simplify

**S:** At 56 AI Technologies, our collections team was manually tracking payment requests via WhatsApp, chasing customers, and reconciling payments in spreadsheets. This was error-prone and created fraud risks (fake payment screenshots, missed follow-ups).

**T:** I was responsible for integrating Razorpay Payment Links into our platform to automate the payment collection workflow.

**A:** I built the full integration: link generation API, webhook handler with HMAC signature verification, idempotent payment processing (ON CONFLICT DO NOTHING in PostgreSQL), and a daily reconciliation job comparing our ledger against Razorpay's settlement report. I designed the reconciliation to flag payments that Razorpay recorded but we didn't (missed webhooks) and vice versa (potential fraud). I worked with collections ops to migrate their workflow from manual WhatsApp tracking to the new system over 2 weeks.

**R:** Manual collection effort dropped 70%. The reconciliation job caught 3 instances of webhook manipulation in the first month, preventing fraudulent payment confirmations. Collections cycle time fell from 4 days to same-day.

---

### 6. Autopay Recurring Payment Workflows — -30% Manual Intervention
**Headline metric:** -30% manual intervention in recurring payment processing  
**Strongest LP:** Ownership / Bias for Action

**S:** At 56 AI Technologies, our recurring payment (EMI/subscription) process relied on ops manually preparing NACH debit files each morning, tracking failures in a spreadsheet, and sending customer notifications via email. Failures required manual follow-up with banks.

**T:** I was responsible for automating the Autopay workflow end-to-end.

**A:** I built a distributed scheduler: a scanner process that ran every minute, claimed due charges from PostgreSQL using optimistic locking (preventing double execution), and submitted them to the Razorpay Autopay API. I implemented a retry policy (day+1, +3, +7) with automatic mandate pausing after 3 failures. I added automated pre-debit notifications (D-2 SMS via Razorpay) and result notifications. I used claim expiry (5-minute timeout) to handle scanner crashes without dual execution.

**R:** Manual intervention in the recurring payment process dropped 30%. Processing errors from duplicate submissions went to zero. Customer complaint rate about unexpected charges dropped 40%.

---

### 7. Introducing Unit Testing at 56 AI
**Headline metric:** Reduced production regression rate by ~50%  
**Strongest LP:** Insist on the Highest Standards / Learn and Be Curious

**S:** When I joined 56 AI Technologies, the codebase had no unit tests. Releases frequently caused regressions that were only caught in production, leading to emergency hotfixes and customer-facing bugs.

**T:** I decided to introduce unit testing as a standard practice, starting with the payment processing modules I was building.

**A:** I introduced pytest as the testing framework and wrote tests for all new payment-related code I built (payment link generation, webhook processing, reconciliation). I established a pattern of test-driven development for edge cases (duplicate webhooks, expired mandates, network timeouts). I ran a 1-hour session with the team showing how to write effective unit tests and added a CI step that blocked merges with < 80% coverage on new code.

**R:** Within 3 months, test coverage on payment modules reached 85%. Production regression rate fell by approximately 50% compared to the prior quarter. The team adopted the practice voluntarily for their own modules after seeing it catch bugs in code review.

---

### 8. B2B Synergy Service at PharmEasy
**Headline metric:** Onboarded 15 new B2B pharmacy partners in the first quarter  
**Strongest LP:** Think Big / Customer Obsession

**S:** At PharmEasy, the B2B business was growing rapidly — pharmacy chains wanted to order wholesale stock from us, but we had no dedicated B2B ordering API. The sales team was managing orders via email and phone, which didn't scale.

**T:** I was responsible for building the B2B Synergy service — an API platform for pharmacy partner ordering and inventory visibility.

**A:** I designed and built the REST API for B2B order placement, order tracking, and invoice generation. I worked closely with the sales and ops teams to understand the B2B ordering workflow, which differed significantly from B2C (bulk orders, credit terms, custom pricing). I built a credit limit enforcement layer and integrated with our ERP for inventory reservation. I coordinated with 3 partner integration teams to onboard them to the new API.

**R:** 15 new B2B pharmacy partners onboarded in Q1 using the new API. B2B order processing time fell from 2 days to same-day. The system scaled to handle 500+ orders/day without additional ops headcount.

---

### 9. Purchase Return V2 at PharmEasy
**Headline metric:** Reduced return processing time from 3 days to 4 hours  
**Strongest LP:** Customer Obsession / Dive Deep

**S:** At PharmEasy, the purchase return process (pharmacy partners returning unsold or expired stock) was a paper-based, manual process taking 3-5 days. Partners were frustrated by the delay in receiving credit for returned goods.

**T:** I owned the redesign of the purchase return workflow as a new microservice (Purchase Return V2).

**A:** I replaced the paper process with a digital return request API. Partners could initiate returns online, and the system automatically validated return eligibility (within return window, product matches original purchase). I built the reconciliation logic to automatically generate credit notes upon warehouse confirmation of receipt. I integrated with the warehouse management system for automated goods receipt.

**R:** Return processing time fell from 3 days to 4 hours end-to-end. Partner satisfaction scores for the returns process improved from 2.8/5 to 4.2/5 in the quarterly survey. Credit note disputes dropped 60%.

---

### 10. Atlas Inward-Ops Visibility Platform
**Headline metric:** Cut order processing errors by 35% in the first 3 months  
**Strongest LP:** Dive Deep / Data-Driven Decision Making

**S:** At PharmEasy, our warehouse inward-operations team (receiving inventory from suppliers) had no real-time visibility into pending inward orders. Teams used shared Excel sheets, leading to double-processing and missed orders.

**T:** I was part of the 3-person team that built the Atlas platform, and I owned the order tracking and alerting components.

**A:** I built the real-time order status dashboard backend — an API that aggregated status from the WMS, supplier ERP, and our internal systems. I implemented status-change events published to a Kafka topic, which drove real-time dashboard updates and automated alerts for orders overdue by > 2 hours. I also built the data reconciliation between the WMS's record and our internal DB, catching discrepancies daily.

**R:** Order processing errors (wrong items received, missing confirmation) dropped 35% in the first 3 months. The operations team eliminated the shared Excel sheet within 4 weeks of Atlas launch. Inward-ops throughput increased 20% (same team, fewer error-recovery cycles).

---

### 11. Automated Invoice Printing System at PharmEasy
**Headline metric:** Reduced invoice processing time from 45 min to 3 min  
**Strongest LP:** Invent and Simplify / Frugality

**S:** At PharmEasy, invoices for pharmacy orders were manually printed by a warehouse associate who would log into the ERP, generate the PDF, and print it. At peak, this took 45 minutes per batch and was a warehouse bottleneck.

**T:** I was asked to automate the invoice printing workflow.

**A:** I built an automated invoice printing service that polled the ERP for confirmed orders every 30 seconds, generated PDFs using a template engine, and sent them to the warehouse printers via a print queue API. I added retry logic for printer failures (paper jam, offline) and an alerting system for print queue backlog. The solution ran on an existing server with no additional infrastructure cost.

**R:** Invoice processing time fell from 45 minutes to 3 minutes. The warehouse associate's time was reallocated to higher-value tasks. No additional infrastructure cost. The system handled 400+ invoices/day within the first week.

---

### 12. On-Call Ownership at PharmEasy
**Headline metric:** Maintained 99.8% uptime for 4 critical warehouse services over 2 years  
**Strongest LP:** Ownership / Dive Deep

**S:** At PharmEasy, I was on-call for 4 critical warehouse services (order processing, stock transfer, invoice printing, inward-ops). These were revenue-critical; downtime directly blocked warehouse operations.

**T:** I was responsible for incident response, root cause analysis, and driving preventive improvements for these services.

**A:** Over 2 years, I responded to ~30 production incidents. I established a practice of publishing RCAs within 48 hours of each incident and tracking action items to completion. I identified 3 recurring root causes (connection pool exhaustion, memory leak in a PDF generation library, and a race condition in stock reservation) and fixed all three. I improved our alerting coverage from 40% to 90% of known failure modes.

**R:** Maintained 99.8% uptime across 4 critical services over 2 years. Mean time to resolution fell from 2 hours (before my on-call improvements) to 35 minutes. Zero incidents caused by the 3 recurring root causes after I fixed them.

---

### 13. Blockchain Prototype at Wipro (2018 Intern)
**Headline metric:** Delivered working proof-of-concept in 8 weeks  
**Strongest LP:** Learn and Be Curious / Bias for Action

**S:** As a Wipro Digital intern in 2018, I was assigned to build a blockchain proof-of-concept for supply-chain provenance tracking, using Ethereum and Hyperledger. I had no prior blockchain experience.

**T:** I had 8 weeks to deliver a working prototype demonstrating end-to-end provenance tracking for a pharmaceutical supply chain.

**A:** I spent the first 2 weeks on deep learning (Solidity, smart contracts, Hyperledger Fabric architecture), then built the prototype iteratively. I wrote smart contracts for recording supply-chain events, a Node.js API to interact with the blockchain, and a simple dashboard. I presented weekly demos to the project sponsor and adjusted based on feedback.

**R:** Delivered a working prototype on time. The client used it to secure funding for a Phase 2 pilot. My manager cited the delivery as exceeding expectations for an intern project.

---

## Gap Stories (Adapt to Your Own Examples)

*These cover Amazon LPs that are less represented in your real CV. Each is grounded in plausible scenarios from your roles. Flag any that you have a better real example for.*

### 14. Genuine Failure / Lesson Learned
**Headline metric:** Migration rollback avoided, learned to add circuit breakers  
**Strongest LP:** Learn and Be Curious / Earn Trust

*[adapt to a real example if you have one]*

**S:** At Logward, I was leading a migration of our container state table from a single-schema design to a partitioned table. I estimated the migration would complete in 4 hours with minimal read latency impact.

**T:** I was responsible for planning and executing the migration during a Saturday maintenance window.

**A:** I underestimated the lock contention from the partition creation on a hot table. The migration caused 8 minutes of elevated read latency (2-3x normal) that I hadn't anticipated — customers noticed. I paused the migration, restored normal operations, and spent the next 2 weeks building a shadow migration approach (write to both old and new table, gradually drain reads from old table) that caused zero customer impact.

**R:** The second attempt completed with < 50ms additional latency during migration. I now build shadow migration approaches for any schema change on hot tables, and add a "latency impact" section to all migration runbooks.

---

### 15. Disagree and Commit
**Headline metric:** Shipped on time despite technical disagreement; approach proved correct  
**Strongest LP:** Have Backbone; Disagree and Commit

*[adapt to a real example if you have one]*

**S:** At Logward, the team was debating the architecture for a new multi-tenant data isolation layer. My lead wanted to use a shared schema with application-level tenant filtering. I disagreed — I felt PostgreSQL Row-Level Security was safer and would prevent bugs from leaking data between tenants.

**T:** I had to make my case, but ultimately support whatever decision was made.

**A:** I prepared a technical document comparing both approaches — I showed the blast radius of an application-level bug (full data leak) vs an RLS misconfiguration (error, not leak). I proposed a 2-day spike to prototype RLS. My lead reviewed the spike and decided to stay with application-level filtering for delivery speed. I disagreed but committed fully — I implemented the application-layer approach, wrote thorough tests for the filtering logic, and added integration tests specifically for cross-tenant access scenarios.

**R:** We shipped on time. Six months later, a bug in the filtering layer would have caused a tenant data leak — but the integration tests caught it in CI before it shipped. My tests were the safety net that made the chosen approach safe. I shared this outcome with my lead.

---

### 16. Learn and Be Curious
**Headline metric:** Reduced event processing overhead by 40% by adopting a new pattern  
**Strongest LP:** Learn and Be Curious

*[adapt to a real example if you have one]*

**S:** At Logward, our container tracking ingest pipeline was struggling with throughput. A colleague mentioned the outbox pattern as a way to eliminate dual-write risk. I had never used it before.

**T:** I took it upon myself to learn the pattern and evaluate whether it would help us.

**A:** I spent 3 evenings reading the DDIA chapter on data integration and watching conference talks on CDC and Debezium. I built a local prototype with Debezium + Kafka in Docker, validated the latency overhead was acceptable (< 50ms vs our 500ms problem), and wrote a technical proposal. I presented it to the team with a live demo.

**R:** The team adopted the outbox pattern for 3 of our services. Event processing reliability improved significantly (no more dual-write failures). Processing overhead fell 40% by eliminating direct Kafka calls from the request path.

---

### 17. Frugality / Scrappy Solution
**Headline metric:** Saved ~Rs 1.5L/month in cloud costs without feature regression  
**Strongest LP:** Frugality

*[adapt to a real example if you have one]*

**S:** At Logward, we received a quarterly review showing our AWS bill had grown 80% YoY, largely from RDS costs and data transfer fees. The budget hadn't grown proportionally.

**T:** I volunteered to identify cost savings without impacting service quality.

**A:** I analyzed CloudWatch and AWS Cost Explorer for 2 days. Found 3 optimizations: (1) 40% of our RDS capacity was reserved but unused during off-peak hours — I enabled auto-scaling and switched to compute-optimized instances for the read replicas, (2) we were keeping 90-day snapshots when 30 days met our audit requirements — trimmed the snapshot policy, (3) switched ClickHouse analytics data to S3-backed cold storage with compression. I implemented all 3 in a single weekend with a rollback plan.

**R:** Monthly AWS spend dropped by approximately Rs 1.5L (~$1,800). No service degradation. The changes took 16 hours to implement. Used the savings to fund an additional load testing environment.

---

### 18. Mentoring / Hire and Develop
**Headline metric:** Mentored junior engineer to independent ownership of a service in 8 weeks  
**Strongest LP:** Hire and Develop the Best

*[adapt to a real example if you have one]*

**S:** At Logward, a junior engineer joined our team with strong Python skills but limited distributed systems experience. She was assigned to build a new alerting microservice and was struggling with Kafka consumer patterns and idempotency.

**T:** I took on informal mentoring responsibility to help her get productive on distributed systems concepts.

**A:** I set up weekly 1-on-1 design reviews where she would walk me through her approach and I would ask Socratic questions rather than giving answers directly. I pair-programmed the first Kafka consumer implementation with her, explaining ISR, consumer group rebalancing, and offset commit timing as we went. I shared relevant chapters from DDIA and my internal design docs. I gave detailed PR reviews, always explaining the "why" behind each comment.

**R:** Within 8 weeks, she owned and deployed the alerting service independently. Her code quality in subsequent PRs required significantly fewer review cycles. She cited the mentorship in her mid-year review as the most impactful part of her onboarding.

---

## Coverage Quick Reference

| Story | Headline metric | Primary LP | Secondary LP |
|-------|----------------|------------|-------------|
| 1. Trigger Service | -60% latency | Dive Deep | Invent & Simplify |
| 2. Production Incident RCA | 47 min MTTR | Ownership | Bias for Action |
| 3. Validation Layer | -80% data bugs | Dive Deep | Think Big |
| 4. Lifecycle Orchestration | -65% manual ops | Invent & Simplify | Customer Obsession |
| 5. Razorpay Payment Links | -70% effort/fraud | Customer Obsession | Invent & Simplify |
| 6. Autopay Scheduler | -30% manual work | Ownership | Bias for Action |
| 7. Unit Testing | -50% regressions | Insist on Standards | Learn & Curious |
| 8. B2B Synergy | 15 partners Q1 | Think Big | Customer Obsession |
| 9. Purchase Return V2 | 3d → 4h | Customer Obsession | Dive Deep |
| 10. Atlas Platform | -35% errors | Dive Deep | Data-driven |
| 11. Invoice Printing | 45min → 3min | Invent & Simplify | Frugality |
| 12. On-Call Ownership | 99.8% uptime | Ownership | Dive Deep |
| 13. Wipro Blockchain | On-time delivery | Learn & Curious | Bias for Action |
| 14. Migration Failure | Safe rollout | Learn & Curious | Earn Trust |
| 15. Disagree & Commit | Shipped on time | Backbone | Earn Trust |
| 16. Learn Outbox Pattern | -40% overhead | Learn & Curious | — |
| 17. Cost Optimization | -Rs 1.5L/mo | Frugality | — |
| 18. Mentoring | 8-wk ownership | Hire & Develop | — |

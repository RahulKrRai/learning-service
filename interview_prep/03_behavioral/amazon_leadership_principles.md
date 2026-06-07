# Amazon Leadership Principles

> At Amazon, every answer is an LP answer. Every round has an LP question. The Bar Raiser will probe 3-4 levels deep. Know your LPs and know your stories.

**The golden rule:** When you open an LP answer, name the principle (briefly) and lead with the metric. "This is a story about diving deep — I found the root cause that others had missed, and it saved us 60% in processing latency."

---

## All 16 Leadership Principles

### 1. Customer Obsession
**One-line meaning:** Start with the customer and work backwards. Customer trust matters more than short-term profit.

**What Bar Raiser probes for:** Did you actually go talk to customers? Did you prioritize their need over an easier technical path? Can you give a specific customer impact metric?

**Primary story:** Story 5 — Razorpay Payment Links (-70% collection effort; customers got a better payment experience)
**Backup story:** Story 9 — Purchase Return V2 (partner satisfaction 2.8 → 4.2/5)

**Sample opening:** "When I built the Razorpay Payment Link integration at 56 AI, the driving force was a specific complaint from our largest customer — they had been burned by a fraudulent payment confirmation and had lost trust in the process. I traced the fraud risk to our lack of webhook signature verification and no reconciliation against Razorpay's ledger."

---

### 2. Ownership
**One-line meaning:** Think and act like an owner. Never say "that's not my job." Take responsibility for the outcome, not just the task.

**What Bar Raiser probes for:** Did you take action without being asked? Did you own the problem end-to-end, including things outside your stated scope? What did you do when things went wrong?

**Primary story:** Story 2 — Production Incident RCA (owned the incident from triage to RCA to prevention)
**Backup story:** Story 12 — On-call Ownership (99.8% uptime over 2 years)

**Sample opening:** "When our tracking API started failing at Logward, I was on-call. I didn't just restore service — I ran the RCA, presented it to stakeholders, and implemented a change to our deploy checklist that prevented recurrence."

---

### 3. Invent and Simplify
**One-line meaning:** Expect and require innovation. Find ways to simplify. Don't be constrained by "how things are done."

**What Bar Raiser probes for:** Was the solution genuinely novel, or just "we used a common pattern"? What specifically was simplified? What was discarded?

**Primary story:** Story 1 — Trigger Service redesign (separated evaluation from dispatch, added rule cache — genuinely simplified the hot path)
**Backup story:** Story 11 — Automated Invoice Printing (replaced a manual paper process with a polling service at zero infrastructure cost)

**Sample opening:** "The Trigger Service hot path was doing three things in series that should have been three separate concerns. I simplified it to a single responsibility per component and eliminated two external calls from the hot path."

---

### 4. Are Right, A Lot
**One-line meaning:** Have strong judgment and good instincts. Seek diverse perspectives. Be right more often than not.

**What Bar Raiser probes for:** How do you make decisions under uncertainty? Do you seek data, or trust your gut? When were you wrong, and how did you find out?

**Primary story:** Story 3 — Data Validation Layer (correctly identified that the problem was architectural, not per-service bugs; designed a cross-service solution)
**Backup story:** Story 15 — Disagree & Commit (had correct instinct about RLS; added integration tests that proved out the risk)

**Sample opening:** "When I saw repeated data inconsistency bugs across our tracking services, my instinct was that this was a systemic architecture problem, not individual service bugs. I dug into 20 recent incidents to confirm the pattern before proposing a solution."

---

### 5. Learn and Be Curious
**One-line meaning:** Never stop learning. Be curious about new possibilities. Explore broadly.

**What Bar Raiser probes for:** What have you learned recently that changed how you work? Have you gone outside your comfort zone? Do you apply learning proactively?

**Primary story:** Story 16 — Learned the outbox pattern independently and proposed it to the team
**Backup story:** Story 13 — Blockchain prototype (learned Solidity and Hyperledger from zero in 2 weeks)

**Sample opening:** "At Logward I noticed we had a dual-write risk in our event pipeline — a Kafka publish could fail after a DB commit. I hadn't solved this before, so I spent 3 evenings learning the outbox pattern and CDC. I built a prototype, validated it, and proposed it to the team."

---

### 6. Hire and Develop the Best
**One-line meaning:** Raise the performance bar with every hire. Develop others. Be a mentor.

**What Bar Raiser probes for:** Have you specifically developed someone's skills? Did you give hard feedback? Did you advocate for someone's growth?

**Primary story:** Story 18 — Mentored junior engineer to independent service ownership in 8 weeks
**Backup story:** Story 7 — Introduced unit testing culture at 56 AI (team adopted it voluntarily)

**Sample opening:** "When a junior engineer joined our team to build the alerting service, I saw she had strong coding skills but hadn't worked with distributed systems. I structured our 1-on-1s around Socratic questions — I'd ask her to defend design choices rather than giving answers."

---

### 7. Insist on the Highest Standards
**One-line meaning:** Leaders have relentlessly high standards. Don't let problems recur. Fix the root cause.

**What Bar Raiser probes for:** What standards did you raise? Did you push back when quality was insufficient? Did you prevent recurrence, not just fix the symptom?

**Primary story:** Story 7 — Introduced unit testing, CI coverage gates, and mandatory "explain analyze" in deploy checklist
**Backup story:** Story 2 — RCA practice (published RCA within 24h, tracked action items to completion)

**Sample opening:** "At 56 AI, the team shipped tests that worked but production kept breaking. I traced the root cause to a lack of testing standards — no coverage requirement, no test-driven practice. I introduced a concrete bar: 80% coverage on new payment code, enforced in CI."

---

### 8. Think Big
**One-line meaning:** Create and communicate a bold vision. Think at scale, not for today's problem.

**What Bar Raiser probes for:** What was the broader vision behind your work? How did you think about long-term scale, not just the immediate feature?

**Primary story:** Story 4 — Container Lifecycle Orchestration (designed for multi-carrier extensibility; onboarding a new carrier now takes 2 days, not 2 weeks)
**Backup story:** Story 8 — B2B Synergy (designed for 100+ partners, not just the initial 15)

**Sample opening:** "When I designed the container lifecycle orchestration layer, I didn't optimize for the 8 carriers we had. I designed the adapter pattern so the 9th, 10th, and 50th carrier could be onboarded without touching core logic."

---

### 9. Bias for Action
**One-line meaning:** Speed matters. Many decisions are reversible. Take calculated risks.

**What Bar Raiser probes for:** Did you act when others were waiting? Did you calculate the reversibility? Did you create an environment where action was safe?

**Primary story:** Story 2 — Production Incident (immediate triage, 47-min MTTR)
**Backup story:** Story 6 — Autopay Scheduler (built and shipped end-to-end in 3 weeks, reducing a multi-day manual process)

**Sample opening:** "During the Logward tracking API outage, I had incomplete information — I didn't know for certain the cause was the missing index. But I knew a rollback was fully reversible, so I didn't wait for certainty. I rolled back, confirmed the theory, and fixed it correctly."

---

### 10. Frugality
**One-line meaning:** Accomplish more with less. Resourcefulness is a virtue. Spending money is not a substitute for good engineering.

**What Bar Raiser probes for:** What did you avoid spending? Did you find a simple solution rather than buying one? Did you push back on unnecessary cost?

**Primary story:** Story 17 — AWS cost optimization (-Rs 1.5L/month with a weekend of engineering)
**Backup story:** Story 11 — Invoice Printing (automated a manual process with zero additional infrastructure cost)

**Sample opening:** "When I found that our AWS RDS bill had grown 80% YoY, I spent 2 days in Cost Explorer rather than requesting a budget increase. Three changes, a weekend of engineering, and we cut the monthly bill by Rs 1.5L."

---

### 11. Earn Trust
**One-line meaning:** Be radically candid. Acknowledge mistakes. Deliver on commitments.

**What Bar Raiser probes for:** Have you given bad news proactively? Have you admitted a mistake clearly? Do people trust your estimates?

**Primary story:** Story 14 — Migration Failure (acknowledged the mistake immediately, paused migration, communicated transparently)
**Backup story:** Story 2 — RCA (published a frank RCA including "I should have run EXPLAIN ANALYZE before the deploy")

**Sample opening:** "During the table migration at Logward, I realized mid-execution that I had misjudged the lock contention impact. I paused the migration immediately, informed stakeholders before they noticed the latency spike, and presented a revised plan within 2 hours."

---

### 12. Dive Deep
**One-line meaning:** Leaders operate at all levels. No detail is beneath you. Data and anecdotes both matter.

**What Bar Raiser probes for:** How deep did you go? Did you look at raw logs, metrics, the actual query plan? Did you find something others had missed?

**Primary story:** Story 1 — Trigger Service (profiled the service, found two bottlenecks at the code level — DB queries and HTTP call blocking)
**Backup story:** Story 3 — Validation Layer (analyzed 20 incidents to confirm the pattern before building the solution)

**Sample opening:** "When the Trigger Service latency spiked, I didn't trust the aggregate metrics. I added per-stage timing logs and replayed 1,000 real events. The DB query was taking 35ms on average — but I found it could spike to 200ms under load because of lock contention from our batch rule updates."

---

### 13. Have Backbone; Disagree and Commit
**One-line meaning:** Respectfully challenge decisions you disagree with. Once a decision is made, commit fully.

**What Bar Raiser probes for:** Did you push back? Was the pushback data-driven or emotional? Did you fully commit after the decision, or undermine it?

**Primary story:** Story 15 — Disagree on data isolation approach, committed fully, added safety tests
**Backup story:** *(thin — work on a second real example)*

**Sample opening:** "I disagreed with my lead about using application-level filtering vs Row-Level Security for tenant isolation. I prepared a technical doc quantifying the blast radius of each failure mode. He decided to go with application filtering for delivery speed. I committed fully — and I made sure to write the integration tests that would have caught the bug we later found."

---

### 14. Deliver Results
**One-line meaning:** Focus on the right inputs and deliver results with the right quality and in a timely fashion.

**What Bar Raiser probes for:** Did you actually ship? Did you handle obstacles? Are your results verifiable?

**Primary story:** Story 5 — Payment Links (shipped on time, -70% measurable outcome)
**Backup story:** Story 13 — Wipro prototype (on-time delivery despite learning from scratch)

**Sample opening:** "I shipped the Razorpay Payment Link integration in 6 weeks, including the reconciliation job that caught 3 fraud attempts in month one. The -70% reduction in manual effort was measured by comparing the collections team's logged time over the 30 days before and after launch."

---

### 15. Strive to Be Earth's Best Employer
**One-line meaning:** Leaders work every day to create a safer, more productive, more diverse, more just, and more fun work environment.

**What Bar Raiser probes for:** Have you created psychological safety? Have you advocated for a teammate? Have you removed a barrier for someone?

**Primary story:** Story 18 — Mentoring (created a safe environment for the junior engineer to ask "dumb questions"; used Socratic method rather than giving answers)
**Backup story:** Story 7 — Introduced testing (raised the whole team's quality bar, not just my own code)

**Sample opening:** "When I mentored the junior engineer on distributed systems, I made a deliberate choice to ask questions rather than give answers. I wanted her to build the mental model herself. I also explicitly told her there were no dumb questions in our 1-on-1s."

---

### 16. Success and Scale Bring Broad Responsibility
**One-line meaning:** As we grow, our decisions have a bigger impact on the world. Be a good steward.

**What Bar Raiser probes for:** Have you thought about the broader impact of your systems? Have you flagged risks beyond your immediate team?

**Primary story:** Story 3 — Data Validation Layer (a data leak between enterprise tenants would be a GDPR issue, not just a bug — I flagged this and designed with isolation in mind)
**Backup story:** Story 5 — Payment reconciliation (designed to catch fraud, not just process payments)

**Sample opening:** "When I designed the multi-tenant validation layer at Logward, I framed the data isolation requirement explicitly as a compliance risk — a bug that leaked tenant A's container data to tenant B would be a GDPR violation for our EU customers. I documented this and designed the defense-in-depth approach accordingly."

---

## Coverage Matrix

| LP | Primary Story | Backup Story | Coverage |
|----|--------------|-------------|----------|
| Customer Obsession | 5 — Razorpay | 9 — Returns | 🟢 Strong |
| Ownership | 2 — Incident RCA | 12 — On-Call | 🟢 Strong |
| Invent and Simplify | 1 — Trigger Service | 11 — Invoice | 🟢 Strong |
| Are Right, A Lot | 3 — Validation | 15 — Disagree | 🟡 OK |
| Learn and Be Curious | 16 — Outbox | 13 — Blockchain | 🟡 OK |
| Hire and Develop | 18 — Mentoring | 7 — Testing | 🟡 OK |
| Insist on Standards | 7 — Testing | 2 — RCA checklist | 🟢 Strong |
| Think Big | 4 — Orchestration | 8 — B2B | 🟡 OK |
| Bias for Action | 2 — Incident | 6 — Autopay | 🟢 Strong |
| Frugality | 17 — AWS costs | 11 — Invoice | 🟡 OK |
| Earn Trust | 14 — Migration | 2 — RCA | 🟡 OK |
| Dive Deep | 1 — Trigger | 3 — Validation | 🟢 Strong |
| Backbone/Disagree | 15 — Disagree | **THIN** | 🔴 Thin |
| Deliver Results | 5 — Razorpay | 13 — Wipro | 🟢 Strong |
| Best Employer | 18 — Mentoring | 7 — Testing | 🟡 OK |
| Broad Responsibility | 3 — Validation | 5 — Recon | 🔴 Thin |

**Action items for thin LPs:**
- **Have Backbone (🔴):** Find a second real example of pushing back on a decision. Even a small code review disagreement counts if it was data-driven.
- **Broad Responsibility (🔴):** Think about any time you flagged a security, privacy, or broader impact concern. This LP is rarely probed in tech loops but prepare one story.

---

## Resources

**Free:**
- [Amazon Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) — read every word
- [Dan Croitor on Amazon LPs](https://www.youtube.com/results?search_query=dan+croitor+amazon+leadership+principles)

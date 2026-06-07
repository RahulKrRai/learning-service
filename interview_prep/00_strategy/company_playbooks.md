# Company Playbooks

One section per target company. Read your target's section the week before the loop, and again the night before.

**How to use this file**
- **PRIMARY targets** (maximize comp + fit): Google L5, Confluent Senior, Uber Senior, Atlassian Senior, Amazon L6.
- **LEVERAGE / warm-up only** (early reps + competing offers): Goldman Sachs VP, JPMorgan VP. Accept only if >= ~Rs 75-80L.
- **Sequence**: banks first (cheap reps, HackerRank OAs) -> then cluster Tier-1 onsites into a 3-4 week window so offers land close together for negotiation leverage.
- **Comp data**: always cross-check offers and bands on [levels.fyi](https://www.levels.fyi). Filter by India / Bangalore. Glassdoor is noisier but useful for interview-experience write-ups.

**Your baseline (use this in every playbook below)**
- 7+ yrs, Senior Backend. Python primary for coding; also Go, Node/TS, Java, Kotlin.
- Distributed systems, event-driven, microservices, multi-tenant SaaS. AWS, K8s, Kafka, Redis, PostgreSQL, MongoDB.
- Logward headline stories: multi-tenant Trigger Service (-60% processing latency), distributed data validation/consistency layer, container-lifecycle orchestration, production incident RCA. 56 AI: Razorpay payment-link + Autopay. PharmEasy: warehouse/supply-chain at scale, on-call.
- Self-assessment: **DSA rusty (not weak)**; **system design is your strength**; **behavioral is make-or-break for Amazon**.

**2026 cross-company trend**: nearly every loop now has some flavor of an **AI-fluency / code-comprehension round** — read/debug unfamiliar code, reason about an AI-generated diff, or discuss how you use LLMs responsibly. Prep this once (see "AI-fluency prep" at the bottom) and reuse it everywhere. Note: AI assistants are *banned in live coding* at Google and Amazon — the AI round is a *separate, explicit* round, never an excuse to use AI in the algorithm round.

---

## Google — L5 (Senior Software Engineer)

**Target comp**: ~Rs 1.1Cr (India L5). Verify on [levels.fyi Google](https://www.levels.fyi/companies/google/salaries).

**Loop structure (4-5 rounds)**
- Recruiter screen -> sometimes 1 phone/online coding screen -> onsite ("virtual onsite") of ~4-5 rounds:
  - 2 coding rounds (DSA, 45 min each).
  - 1 system design round (expected at L5).
  - 1 "Googleyness & Leadership" (behavioral) round.
  - Occasionally a second design or a domain round depending on team.
- **Decoupled hiring**: you interview generically, then **Hiring Committee (HC)** reviews packet, then **team match**. You can pass the loop and still wait weeks for a team. Down-leveling to L4 is a real risk if coding is shaky — protect against it by being crisp.

**Coding environment quirks**
- **Plain Google Doc. No autocomplete, no syntax highlighting, no run/compile.** You cannot test code by running it.
- Consequence: you must **dry-run by hand**, track indentation manually, and write compilable-looking Python from memory (correct imports, no IDE crutches).
- Practice the last 3-4 weeks by solving in a bare text editor or Google Doc with a timer. No LeetCode "run".

**What they weight**
- **Algorithmic depth + clean communication.** They want optimal-ish solution, correct complexity analysis, and a clear narration of your thought process. Graphs, trees, DP, intervals, heaps, and "design a data structure" show up a lot.
- At L5 they expect you to **state the brute force, then optimize, state Big-O, and self-test** without prompting.
- System design at L5: scope, clarify, drive the conversation, discuss tradeoffs and failure modes.
- "Googleyness": collaboration, humility, dealing with ambiguity, bias to user impact.

**Known 2026 quirks**
- Code-comprehension / "reason about this code" probing is increasingly common; some teams add an AI-usage discussion in the behavioral round. **Do not use AI in the coding doc** — strictly prohibited.

**Referral strategy**
- A referral mainly speeds recruiter contact; it does not lower the bar. Get one from any current Googler (NIT Silchar alumni network on LinkedIn is your best channel) — ask them to refer "L5 SWE, India". Apply to a *specific* req before/at referral time.

**3-5 tips tailored to you**
1. **Weight DSA heaviest here** — Google is the most algorithm-pure of all your targets and the doc environment punishes rust. Drill graphs/DP/intervals/heaps until you can write them blind.
2. **Narrate constantly.** Your design instinct is strong; carry that "think out loud, state tradeoffs" habit into coding so HC reads you as L5, not L4.
3. **Hand-trace every solution** on a sample input before saying "done" — replaces the missing run button and catches off-by-one.
4. **Bring a real distributed-systems design story** (Trigger Service / consistency layer) to the design round; quantify the -60% latency and explain *why* it dropped.
5. **For team match**, push toward infra/data/event-driven teams where your Kafka + multi-tenant background is a differentiator.

**What good looks like at L5**: you independently drive ambiguous problems to a clean, optimal solution while narrating tradeoffs; design rounds show you own a non-trivial system end-to-end (scaling, failure, data model) without hand-holding; you behave like a force-multiplier on a team, not just a strong individual coder.

**Free resource**: [Google Engineering / Research blog](https://research.google/blog/) and the official [careers "how we hire"](https://www.google.com/about/careers/applications/how-we-hire). Interview-experience write-ups on [Glassdoor Google](https://www.glassdoor.co.in/Interview/Google-Interview-Questions-E9079.htm).

---

## Amazon — SDE III / L6 (insist on L6; never accept SDE II)

**Target comp**: ~Rs 1.25Cr at L6 (comp-max of your set, with a WLB tradeoff). Verify on [levels.fyi Amazon](https://www.levels.fyi/companies/amazon/salaries). **Hard rule: insist on L6 (SDE III). Do not let them slot you to SDE II/L5.**

**Loop structure**
- OA (online assessment: 1-2 coding problems + work-style/behavioral survey, sometimes a code-debugging segment) -> recruiter -> full loop (~5 rounds incl. **Bar Raiser**).
- Each loop round is ~60 min and is a **blend of coding/design + Leadership Principles**. Rounds are themed (e.g., "Deliver Results", "Dive Deep", "Are Right A Lot") and each interviewer owns 1-2 LPs.

**Coding environment**
- Live coding in a shared editor (e.g., shared IDE / collaborative pad). You can typically run code on some rounds, but treat it as if you can't.
- No AI assistants in live coding.

**What they weight (this is the differentiator)**
- **Leadership Principles in EVERY round.** Roughly half of each round can be behavioral. The **Bar Raiser** is an objective, cross-org interviewer with veto power whose job is to keep the bar high — they probe LPs hardest.
- At L6 they expect **scope and ambiguity ownership**: driving multi-team or org-level outcomes, mentoring, handling tradeoffs, "disagree and commit".
- System design (scaling, deep dives) plus solid coding.

**Known 2026 quirks**
- **GenAI-fluency round / questions** are now common — discuss how you'd apply or guard against GenAI, and reason about AI-generated code. (But again: no AI in the coding round.)
- Heavy "Dive Deep" follow-ups: expect to be pushed several layers down on metrics and decisions.

**Referral strategy**
- Referrals help routing only. More important: have a current Amazonian flag you as an **L6** candidate so you're not screened in at L5. Ask explicitly for the SDE III req.

**3-5 tips tailored to you (behavioral is make-or-break here)**
1. **Build 10-12 STAR stories now**, mapped to the 16 LPs, each with hard metrics. Your raw material is strong: Trigger Service (-60% latency = "Deliver Results" + "Invent and Simplify"), production incident RCA ("Dive Deep" + "Earn Trust"), data-consistency layer ("Insist on Highest Standards"), introducing unit testing at 56 AI ("Raise the Bar"). Write them out; rehearse aloud.
2. **Scope your stories to L6.** Reframe from "I built X" to "I drove X across teams / owned the outcome / influenced without authority". L5-sized stories get you L5-leveled.
3. **Quantify everything.** Amazon interviewers dive deep — know the numbers behind -60%, the record counts (10M+), incident MTTR, etc.
4. **Practice "disagree and commit" and a real failure story** with what you learned — these are almost always asked and you must not flinch.
5. **Prep the GenAI-fluency answers** with concrete examples from your work (where AI helps, where you keep a human in the loop, hallucination/cost guards).

**What good looks like at L6**: you own ambiguous, cross-team problems end-to-end and can show org-level impact with data; you mentor and raise the bar for others; every behavioral answer is a crisp STAR with metrics and a clear "what I'd do differently". Coding is competent but the bar is set by leadership + depth.

**Free resource**: [Amazon's 16 Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) (mandatory read) and [levels.fyi Amazon](https://www.levels.fyi/companies/amazon/salaries). Interview write-ups on [Glassdoor Amazon](https://www.glassdoor.co.in/Interview/Amazon-Interview-Questions-E6036.htm).

---

## Confluent — Senior Software Engineer

**Why this is your best stack fit**: Confluent *is* Kafka. Your event-driven / Kafka / distributed-systems background is directly on-target. Target comp up to ~Rs 1.21Cr. Verify on [levels.fyi Confluent](https://www.levels.fyi/companies/confluent/salaries).

**Loop structure**
- Recruiter screen -> technical phone screen (coding) -> onsite loop (~4-5 rounds): typically 1-2 coding, 1 system design (often distributed-systems / streaming flavored), 1 behavioral / values, sometimes a deep technical / domain round.

**Coding environment**
- Standard collaborative editor (CoderPad-style); you can usually run code. Still focus on correctness + clarity over relying on the runner.

**What they weight**
- **Distributed-systems and streaming depth.** Expect questions around partitioning, replication, consistency/ordering guarantees, exactly-once vs at-least-once, backpressure, consumer groups, idempotency, fault tolerance, and reasoning about throughput/latency tradeoffs.
- Strong coding still required, but the design + systems conversation is where you win or lose against other seniors.
- Ownership and on-call maturity for distributed services at scale.

**Known 2026 quirks**
- Code-comprehension / debugging-an-existing-system round is plausible; be ready to reason about an unfamiliar streaming pipeline. Possible AI-fluency discussion.

**Referral strategy**
- Strong fit means a referral is high-leverage. Find Confluent engineers via LinkedIn (search "Confluent" + Kafka community / Bangalore). Lead with your event-driven Trigger Service and Kafka production experience in the referral note.

**3-5 tips tailored to you**
1. **Lean hard into Kafka internals.** Be able to talk partitions, ISR/replication, leader election, offset management, rebalancing, and exactly-once semantics from real experience — this is your unfair advantage; make it obvious.
2. **Turn the Trigger Service into a streaming design story**: how events flow, ordering/idempotency guarantees, how you got -60% latency, how you'd scale it to multi-region.
3. **Don't neglect coding.** Stack fit gets you in the room; rusty DSA still sinks the loop. Keep up trees/graphs/heaps/two-pointer/sliding-window.
4. **Have on-call / incident stories ready** — they care about operating distributed systems, not just designing them. Your RCA leadership story fits perfectly.
5. **Prep design of a streaming / queueing system** (e.g., "design a distributed message queue", "design rate limiter / dedup at scale") — directly in their wheelhouse.

**What good looks like at Senior**: you reason fluently about consistency/ordering/fault-tolerance tradeoffs with real production grounding, design a scalable streaming system end-to-end, and demonstrate ownership + on-call maturity. Coding is clean and correct under time pressure.

**Free resource**: [Confluent Engineering blog](https://www.confluent.io/blog/) and the [Apache Kafka docs/design](https://kafka.apache.org/documentation/#design). Comp on [levels.fyi Confluent](https://www.levels.fyi/companies/confluent/salaries).

---

## Uber — Senior Software Engineer (L5)

**Target comp**: ~Rs 1.07-1.76Cr (wide band; depends on org/level). Verify on [levels.fyi Uber](https://www.levels.fyi/companies/uber/salaries).

**Loop structure**
- Recruiter screen -> technical phone screen (coding) -> onsite loop (~4-5 rounds): typically 2 coding, 1-2 system design (Uber leans heavily on design at senior), 1 behavioral / hiring-manager round.

**Coding environment**
- Collaborative editor (CoderPad-style); code can usually be run. Expect medium/hard LeetCode-style with a strong emphasis on optimal complexity and edge cases.

**What they weight**
- **System design at scale** — Uber's domain (real-time matching, geospatial, high-throughput, low-latency) means they value designing high-scale, fault-tolerant, event-driven systems. Distributed-systems and on-call maturity are highly valued.
- Solid coding with optimal solutions; they probe complexity and edge cases.
- Ownership: senior engineers are expected to drive ambiguous problems.

**Known 2026 quirks**
- Code-comprehension / debugging round and AI-fluency discussion increasingly likely.

**Referral strategy**
- Referral speeds the process. Many ex-PharmEasy / Indian product-company engineers are at Uber Bangalore/Hyderabad — tap that network. Highlight high-scale, real-time, event-driven experience.

**3-5 tips tailored to you**
1. **Practice high-scale real-time design**: think "design Uber-like dispatch", rate limiters, distributed locks, geospatial indexing, idempotent event processing. Your event-driven background transfers well.
2. **Bring throughput/latency numbers** from Logward (10M+ records, -60% latency) — Uber respects measurable scale impact.
3. **Tighten coding to optimal-first.** Uber interviewers push on complexity; don't settle on a brute force at senior level.
4. **On-call stories matter** — they run large production systems; your incident RCA leadership lands well.
5. **Drive the design round** — clarify scope, propose, defend tradeoffs, address failure/scale proactively (this is your strength; lead with it).

**What good looks like at Senior (L5)**: you design a high-scale, low-latency, fault-tolerant system end-to-end with clear tradeoffs; coding is optimal and clean; you show ownership and operational maturity. Behaviorally, you drive ambiguity and collaborate well.

**Free resource**: [Uber Engineering blog](https://www.uber.com/en-IN/blog/engineering/) (excellent for design prep) and [levels.fyi Uber](https://www.levels.fyi/companies/uber/salaries). Interview write-ups on [Glassdoor Uber](https://www.glassdoor.co.in/Interview/Uber-Interview-Questions-E575263.htm).

---

## Atlassian — Senior Software Engineer

**Why it's on the list**: good WLB (your #2 priority) plus competitive comp. Verify on [levels.fyi Atlassian](https://www.levels.fyi/companies/atlassian/salaries).

**Loop structure**
- Recruiter screen -> technical phone screen (coding) -> onsite loop (~4-5 rounds): typically 1-2 coding, 1 system design, and a notable **"Values" interview** (Atlassian-specific behavioral), plus sometimes a project / craft round.

**Coding environment**
- Standard collaborative editor; code can usually be run. Coding tends to be practical/medium rather than extreme-hard.

**What they weight**
- **Atlassian Values** get their own dedicated round ("Open company, no bullshit", "Build with heart and balance", "Don't #@!% the customer", "Play, as a team", "Be the change you seek"). This is real and scored — prepare for it like Amazon LPs, but lighter.
- Pragmatic engineering, collaboration, customer focus, craftsmanship.
- Solid coding + design; ownership of distributed services.

**Known 2026 quirks**
- Code-comprehension and AI-fluency themes possible. Atlassian ships AI features (Rovo/Intelligence) — being conversant in applying AI to product is a plus.

**Referral strategy**
- Referral helps routing. Lead with your collaboration/ownership stories and customer-impact framing (fits their values).

**3-5 tips tailored to you**
1. **Prep the Values round explicitly** — map 2-3 stories per value. Use your "introduced unit testing", "led incident RCA", and cross-team data-consistency work for "be the change", "build with heart and balance", "don't #@!% the customer".
2. **Frame impact around the customer/user**, not just tech metrics — Atlassian weighs customer empathy heavily.
3. **Coding: prioritize clean, readable, tested code** over flashy optimal tricks — craftsmanship is valued.
4. **WLB-fit signaling**: it's fine to ask about sustainable on-call and team practices; it aligns with their values and your priorities.
5. **System design**: bring a multi-tenant SaaS story (Logward) — Atlassian is multi-tenant SaaS at core, so it resonates.

**What good looks like at Senior**: pragmatic, customer-focused engineering; clean well-tested code; a solid end-to-end design; and authentic alignment with the values (collaboration, transparency, balance). You own services and collaborate without ego.

**Free resource**: [Atlassian Engineering blog](https://www.atlassian.com/engineering) and [Atlassian Values](https://www.atlassian.com/company/values). Comp on [levels.fyi Atlassian](https://www.levels.fyi/companies/atlassian/salaries).

---

## Goldman Sachs — VP (Engineering)

**Role in your strategy**: LEVERAGE / warm-up. Use for early reps and a competing offer. **Accept only if >= ~Rs 75-80L.** Verify on [levels.fyi Goldman Sachs](https://www.levels.fyi/companies/goldman-sachs/salaries).

**Loop structure**
- **HackerRank OA** (timed DSA, sometimes with debugging/MCQ sections) -> recruiter -> onsite loop: DSA coding + backend/system fundamentals + sometimes a design round + behavioral. VP loops often include a hiring-manager / leadership conversation.

**Coding environment**
- **HackerRank for the OA** (auto-graded, strict timer — practice the platform's quirks: custom input, partial scoring). Onsite coding in a shared editor or CoderPad.

**What they weight**
- **DSA fundamentals + CS basics** (data structures, complexity, sometimes concurrency, OOP design, SQL). Banks lean classic.
- Backend system fundamentals and reliability mindset (finance = correctness + risk).
- At **VP** level: ownership, mentoring, stakeholder management, and delivery — VP is a senior IC/lead title, not just code.

**Known 2026 quirks**
- Increasing code-comprehension / debugging segments in the OA. Possible AI-fluency discussion. Generally more conservative on AI than Big Tech.

**Referral strategy**
- Referrals route you faster past the OA pile. GS has a large Bangalore/Bengaluru engineering center; tap LinkedIn. Frame as VP-level backend.

**3-5 tips tailored to you**
1. **Use GS as your first rep** in the sequence — the HackerRank OA is the cheapest way to knock the rust off your DSA under real timed conditions before Tier-1 onsites.
2. **Practice on HackerRank specifically**, not just LeetCode — the editor, timer, and partial-scoring behave differently.
3. **Brush up CS fundamentals** banks love: concurrency/threading, OOP/SOLID design, SQL, and complexity analysis.
4. **Lead with correctness and risk awareness** in design/behavioral — finance values reliability and auditability; your data-consistency layer story is gold here.
5. **Don't over-invest** — this is leverage, not a primary target. Cap prep so it feeds (not competes with) your Google/Confluent/Uber prep, and only accept at >= ~Rs 75-80L.

**What good looks like at VP**: strong fundamentals executed reliably, plus evidence of ownership, mentoring, and stakeholder/delivery management. Correctness, risk-awareness, and clear communication outweigh exotic algorithms.

**Free resource**: [Goldman Sachs Engineering](https://www.goldmansachs.com/what-we-do/engineering/) and [levels.fyi Goldman Sachs](https://www.levels.fyi/companies/goldman-sachs/salaries). Interview write-ups on [Glassdoor Goldman Sachs](https://www.glassdoor.co.in/Interview/Goldman-Sachs-Interview-Questions-E2800.htm).

---

## JPMorgan — VP (Software Engineering)

**Role in your strategy**: LEVERAGE / warm-up, same as GS. **Accept only if >= ~Rs 75-80L.** Verify on [levels.fyi JPMorgan](https://www.levels.fyi/companies/jpmorgan-chase/salaries).

**Loop structure**
- **HackerRank OA** (timed DSA + sometimes MCQ/debugging) -> recruiter -> onsite loop: DSA coding + backend fundamentals + system design (for senior/VP) + behavioral. VP loops include a leadership/hiring-manager conversation.

**Coding environment**
- **HackerRank for the OA**; onsite in a shared editor / CoderPad. Same platform-practice advice as GS.

**What they weight**
- DSA + CS fundamentals; backend design; reliability and correctness (finance). System design appears at VP level.
- VP = senior lead expectations: ownership, mentoring, delivery, stakeholder management.

**Known 2026 quirks**
- Code-comprehension / debugging segments; possible AI-fluency discussion. Conservative on AI usage in interviews.

**Referral strategy**
- Large India presence (Bengaluru/Hyderabad/Mumbai); referral speeds routing past the OA. Frame as VP-level backend with distributed-systems depth.

**3-5 tips tailored to you**
1. **Run GS and JPM close together** as your warm-up cluster — same OA style means shared prep, and two bank offers stack for leverage against Tier-1.
2. **HackerRank-platform practice** + classic DSA (arrays, strings, trees, graphs, DP) is the bulk of the win here.
3. **CS fundamentals**: concurrency, OOP design, SQL, complexity — banks probe these more than Big Tech.
4. **Emphasize reliability/correctness** in design and behavioral; your data-consistency + incident-RCA stories map directly to finance's risk mindset.
5. **Time-box prep** — leverage target, not primary. Accept only at >= ~Rs 75-80L; otherwise use the offer to push Google/Confluent/Uber.

**What good looks like at VP**: reliable execution on fundamentals, sound backend/system design, and clear ownership/mentoring/delivery signal. Communication and risk-awareness matter as much as raw algorithm speed.

**Free resource**: [JPMorgan Engineering / Technology blog](https://www.jpmorgan.com/technology) and [levels.fyi JPMorgan](https://www.levels.fyi/companies/jpmorgan-chase/salaries). Interview write-ups on [Glassdoor JPMorgan](https://www.glassdoor.co.in/Interview/J-P-Morgan-Interview-Questions-E145.htm).

---

## AI-fluency prep (reusable across all companies)

The 2026 AI round is *separate* from the live-coding round. Prep these once:
- **Reading/debugging unfamiliar code**: practice explaining what a function does, spotting bugs, and reasoning about edge cases in code you didn't write.
- **Reasoning about an AI-generated diff**: be ready to review LLM output critically — where it's wrong, what you'd test, what you'd never ship blindly.
- **Responsible-use talking points**: have 2-3 concrete examples of where you use AI (boilerplate, test scaffolding, exploring an unfamiliar API) and where you keep a human in the loop (security, correctness-critical logic, cost/hallucination guards).
- **Hard rule**: AI assistants are banned in *live coding* at Google and Amazon. The AI round is its own thing — never blur the two.

## Quick reference table

| Company | Level | Target comp (verify on levels.fyi) | Role in strategy | Heaviest weight | Coding env quirk |
|---|---|---|---|---|---|
| Google | L5 | ~Rs 1.1Cr | PRIMARY | Algo depth + clear comms; HC + team match | **Plain doc, no autocomplete/run** |
| Amazon | SDE III / L6 | ~Rs 1.25Cr | PRIMARY (comp-max) | **LP in every round + Bar Raiser** | Shared editor; no AI |
| Confluent | Senior | up to ~Rs 1.21Cr | PRIMARY (best stack fit) | **Distributed-systems / Kafka depth** | CoderPad-style |
| Uber | Senior (L5) | ~Rs 1.07-1.76Cr | PRIMARY | **High-scale system design** | CoderPad-style |
| Atlassian | Senior | competitive (good WLB) | PRIMARY | **Values round** + craftsmanship | CoderPad-style |
| Goldman Sachs | VP | accept if >= ~Rs 75-80L | Leverage | DSA + CS fundamentals, reliability | **HackerRank OA** |
| JPMorgan | VP | accept if >= ~Rs 75-80L | Leverage | DSA + CS fundamentals, reliability | **HackerRank OA** |

_All comp figures are approximate and must be re-checked on [levels.fyi](https://www.levels.fyi) for India / Bangalore before any negotiation._

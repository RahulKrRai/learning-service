# Per-Company Behavioral Framing

> Same stories, different lens. Understand what each company optimizes for, then reframe your stories to speak their language.

---

## Google — Googleyness

**What Google values:**
- Intellectual humility (you changed your mind with data)
- Collaboration across functions
- Ambiguity tolerance (you drove clarity without needing all the answers)
- Community and good citizenship
- NOT: hero narratives ("I single-handedly saved the day")

**How to reframe your stories:**
- Emphasize the cross-functional work: "I partnered with the DBA team and ops to..." not "I alone designed and built..."
- Show intellectual humility: "My initial instinct was X, but after talking to the ops team I realized Y."
- Describe how you handled ambiguity: "The requirements were unclear, so I ran a spike to test two approaches before committing."
- Credit the team in the context while still clearly stating your individual contribution in Action.

**Red flags at Google:**
- Claiming sole credit for team efforts
- Being inflexible about technical choices
- Dismissive of others' ideas without trying them

**"Why Google?" — Rahul's draft:**
> "I've spent 7 years building systems at scale in logistics and payments, but I've hit the natural ceiling of what you can learn in a product-company environment. Google operates at a scale — in terms of traffic, reliability requirements, and engineering culture — that would fundamentally change how I think about distributed systems. Specifically, I'm drawn to how Google approaches reliability engineering and the intersection of infrastructure and product at L5. That's the growth trajectory I'm after."

**5 questions to ask a Google interviewer:**
1. "What does the transition from L4 to L5 look like on your team — what changes in expectation, not just scope?"
2. "How does your team balance shipping new features with maintaining reliability on your core systems?"
3. "What's the biggest technical challenge the team is working through right now?"
4. "How do teams at Google handle ambiguous requirements — where does clarity come from?"
5. "What do you wish you'd known about Google's engineering culture before joining?"

---

## Amazon — LP-Driven

**What Amazon values:**
- Every story is an LP story — know which LP you're demonstrating
- Quantified results — every Result must have a number
- Bar Raiser will probe 3-4 follow-up levels deep
- Ownership over scope ("I didn't wait to be asked")
- Frugality ("I did it with less")

**How to reframe your stories:**
- Open with the metric: "This is a story about Dive Deep — I found a root cause that was invisible in the aggregated metrics."
- Name the LP naturally, not robotically.
- Prepare your "why did you choose that?" follow-up for every story.
- Every result statement must have a number. "Improved" is not a result.

**Critical Amazon-specific prep:**
- Be ready for LP deep-dives on ANY story. They will ask: "What was the data behind that decision?" and "What would you do differently today?"
- The Bar Raiser is specifically looking for reasons to downvote. Don't give them one.
- LP coverage: you need at least one story per LP. See [amazon_leadership_principles.md](./amazon_leadership_principles.md).
- Never accept on the spot. Insist on SDE III/L6. If they offer SDE II, decline.

**Red flags at Amazon:**
- Vague results ("things improved")
- "We" without "I" — they're evaluating you
- Inconsistency when probed (your story changes under follow-up)
- LP mismatch (claiming Frugality for a story that isn't about doing more with less)

**"Why Amazon?" — Rahul's draft:**
> "Amazon operates at a scale and reliability requirement that very few companies match — and the bar for engineering rigor that comes with that is exactly where I want to grow. The Leadership Principles are something I genuinely identify with: Ownership and Dive Deep in particular map closely to how I've operated at Logward. At L6, I'd be working on systems where the cost of getting it wrong is high and the expectations on engineering judgment are correspondingly high. That's the environment I'm looking for."

**5 questions to ask an Amazon interviewer:**
1. "For an L6 engineer, what's the ratio of individual technical work to leadership/influence — how does that look on your team?"
2. "Which of the Leadership Principles is most actively live on your team right now?"
3. "How does your team handle disagreements between engineers about technical direction?"
4. "What's the biggest engineering challenge your team is facing in the next 12 months?"
5. "How does the Bar Raiser process work in practice — how long does the feedback loop take after the loop?"

---

## Confluent / Uber / Atlassian — Distributed Systems Ownership

**What these companies value:**
- Deep ownership of distributed systems at production scale
- On-call maturity (you've operated, not just built)
- Engineering culture: strong opinions, lightly held; RCA-driven learning
- Atlassian additionally values: collaboration tools mindset, remote-first culture fit
- Confluent additionally values: Kafka/streaming expertise (this is your edge)
- Uber additionally values: real-time systems, geospatial, reliability at extreme scale

**How to reframe your stories:**
- Lead with production impact: "This system handled 10M+ records in production — here's what broke and how I fixed it."
- Show on-call ownership: Story 2 (RCA) and Story 12 (on-call) are strong for these companies.
- For Confluent: go deep on Kafka. Your Trigger Service Kafka architecture is directly relevant. Mention ISR, consumer groups, exactly-once semantics naturally — not as a demo, but because you actually used them.
- For Uber: the container tracking platform (geospatial, real-time event processing) maps to their dispatch/matching systems.

**"Why Confluent?" — Rahul's draft:**
> "At Logward, the most technically interesting problems I solved were all Kafka-based — the Trigger Service fan-out, the container event pipeline, the CDC-based cache invalidation. I've developed a genuine depth in event-driven architecture. Confluent is building the platform that enables all of that at scale, and working there would let me go from a Kafka user to someone who helps define how Kafka is used at the ecosystem level. That's a rare opportunity."

**"Why Uber?" — Rahul's draft:**
> "The container tracking work I did at Logward is architecturally very similar to what Uber does — real-time location event processing, state management at scale, multi-tenant isolation. I've seen how hard those problems are in production. Uber operates at 10-100x the scale of what I've done, and I want to solve those problems at that scale. The dispatch and matching systems in particular are a natural extension of the real-time event processing work I've been doing."

**5 questions to ask a Confluent interviewer:**
1. "How does the team balance Kafka's core reliability work with building higher-level products like Flink-managed streaming?"
2. "What's the most interesting Kafka edge case you've run into at Confluent's own scale?"
3. "How do you approach exactly-once semantics for internal Confluent systems vs what you recommend to customers?"
4. "What does a 'senior' contribution look like at Confluent — is it primarily code, architecture, or customer-facing work?"
5. "What's the engineering culture around on-call and incident response?"

**5 questions to ask an Atlassian interviewer:**
1. "How does the remote-first culture affect how technical decisions get made — is async design review the norm?"
2. "What's the biggest reliability challenge on your team's services right now?"
3. "How does the engineering team at Atlassian approach technical debt — is there dedicated time, or is it woven into feature work?"
4. "What does growth from Senior to Staff look like at Atlassian?"
5. "How much autonomy do senior engineers have over technical architecture choices vs. top-down direction?"

---

## Banks (Goldman Sachs VP, JPMorgan VP)

**What banks value:**
- Stability and low-risk engineering (no cowboy deployments)
- Communication with non-technical stakeholders
- Understanding of financial risk and compliance requirements
- Production reliability and structured incident management
- Pragmatic engineering (not over-engineering)

**How to reframe your stories:**
- Emphasize structured processes: RCA documentation, runbooks, change management.
- Show financial risk awareness: story 5 (payment fraud, reconciliation) is ideal.
- Stress communication: "I presented the RCA to the business stakeholders within 24 hours" lands well.
- Downplay scrappiness/move-fast narratives. Banks like careful, methodical engineers.

**Note on offer strategy:** Use bank offers as leverage to anchor your floor at Rs 75-80L. Don't invest heavily in bank prep at the expense of Tier-1 prep. Do 1-2 rounds for reps and a competing offer, not to land a final offer unless comp beats the floor.

**5 questions to ask a bank interviewer:**
1. "How does engineering leadership at the bank balance velocity with the compliance and audit requirements?"
2. "What's the change management process for deploying to production — how many approvals, how long does a deploy take?"
3. "How does the bank approach incident management — is there a formal escalation path?"
4. "What's the mix of greenfield development vs. maintaining legacy systems on your team?"
5. "How is engineering career growth structured at VP level — is there a distinct Staff/Principal track above VP?"

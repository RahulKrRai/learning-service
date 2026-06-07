# AI Fluency Drills — 2026 Interview Prep

> A new round type is appearing at Google and Amazon in 2026: the AI-fluency / code-comprehension round. It tests how you USE AI tools as an engineering force-multiplier — and critically, how you VALIDATE their output. This is not about using AI to write code during the interview.

---

## What the Round Tests

The AI-fluency round is NOT asking you to let an AI write code for you. It tests:

1. **Code comprehension with AI assistance:** Can you use an AI to understand an unfamiliar module quickly, then verify its claims?
2. **AI-assisted debugging:** Can you use AI to locate a bug, diagnose it, and validate the diagnosis against the actual code?
3. **Precise prompting:** Can you give an AI a scoped, unambiguous instruction that produces useful output?
4. **Validation mindset:** Can you identify where an AI is confidently wrong, and articulate how you catch it?

**The Bar Raiser signal:** A senior engineer doesn't just use AI — they use AI as a tool while remaining the author and validator of every output. The moment you ship AI output without understanding it, you've abdicated engineering judgment. That's the failure mode they're testing for.

---

## The Critical Distinction

```
❌ "The AI said it works, so it works."
✅ "The AI suggested X. I verified it against the source code/docs/tests. Here's what it got right and what it got wrong."
```

AI is a first-draft tool. You own the output. You sign your name to it.

---

## 4 Self-Drills (Do These Weekly in Weeks 5-12)

### Drill 1: Explain an Unfamiliar OSS Repo

**Goal:** Build the skill of using AI to onboard to a codebase, then verifying the accuracy.

**Steps:**
1. Pick an OSS library you use but haven't read deeply — e.g., `confluent-kafka-python`, `celery`, `tenacity`, or `pydantic`.
2. Point an AI (Claude, Copilot, or GPT-4) at a module: paste the source code and ask: *"Explain the retry logic in this module. What are the edge cases?"*
3. Read the AI's explanation carefully.
4. Go read the actual source code. Compare.
5. Log: What did the AI get right? What did it confidently get wrong or oversimplify?

**What you're building:** The habit of treating AI output as a hypothesis, not a fact.

**Interview framing:** *"When I'm onboarding to a new codebase, I'll ask Claude to explain the architecture of a module, then I'll read the actual code and verify the major claims. It usually gets 80% right and misses edge cases in error handling. I use it to get oriented, then read deeply for the parts that matter."*

---

### Drill 2: Introduce a Bug, Then Validate the AI's Diagnosis

**Goal:** Build confidence in evaluating AI debugging output.

**Steps:**
1. Take a function you know well — e.g., your Kafka consumer offset commit logic or your LRU cache implementation.
2. Introduce a subtle bug: an off-by-one error, a missing `None` check, a wrong condition (`>=` vs `>`).
3. Paste the buggy code to an AI and ask: *"Find any bugs in this function."*
4. Evaluate the AI's response: Did it find the bug? Did it describe the right root cause? Did it suggest false positives?
5. Log: How confident was the AI in its wrong answers?

**What you're building:** The ability to recognize when an AI is plausible-but-wrong — the "Confident Idiot" failure mode.

**Interview framing:** *"I've found that AI is excellent at spotting certain classes of bugs — null pointer issues, off-by-ones in boundary conditions. But it sometimes misses semantic bugs or proposes fixes that introduce new issues. I always trace through the proposed fix manually before applying it."*

---

### Drill 3: Scope-Limited Prompting Practice

**Goal:** Learn to give precise, scoped instructions that produce focused, useful output.

**Bad prompt:** *"Explain this file."*  
**Good prompt:** *"Explain only the retry logic in the `consume_messages` function. Ignore the connection setup and the metrics code. What are the failure modes and how does the function handle each one?"*

**Steps:**
1. Take any moderately complex function (150+ lines).
2. First: ask the broad question. Note how much of the output is irrelevant.
3. Second: ask 3 scoped questions about specific behaviors. Note the signal-to-noise improvement.
4. Practice until your first prompt is almost always scoped.

**What you're building:** The discipline to treat AI like a tool with a specific scope, not a general oracle.

**Interview framing:** *"I've learned to scope my AI prompts tightly. If I ask 'explain this file,' I get a 500-word summary of things I could have read myself. If I ask 'explain the backpressure handling in the consume loop,' I get something immediately useful that I can verify in 2 minutes."*

---

### Drill 4: Catch Confidently-Wrong Output

**Goal:** Train yourself to spot hallucination in AI output.

**Steps:**
1. Ask an AI about a well-known library API you know deeply — e.g., *"How does `consumer.poll(timeout_ms)` work in confluent-kafka-python? What happens if the timeout expires?"*
2. Compare the response to the actual confluent-kafka-python documentation.
3. Identify: Did the AI invent method signatures that don't exist? Did it mix up parameters? Did it describe behavior from a different Kafka client library (e.g., Java)?
4. Log the specific wrong claim. This is your "hallucination case library."

**What you're building:** A calibrated skepticism toward AI output on specific technical claims. You can cite real examples in an interview.

**Interview framing:** *"I once asked an AI about Kafka consumer group rebalancing behavior and it described the Java client's behavior, not the Python client's. The difference was significant — the error handling is different. I caught it because I knew the Python client well. That's the validation layer you always need."*

---

## "How I Validate AI Output" — Interview Talking Points

When an interviewer asks *"How do you use AI tools in your workflow?"*, this is the answer:

```
1. Cross-check against official docs / source code
   "I treat AI output as a starting point, not a final answer. For any API claim,
   I check the official docs or read the source."

2. Mental trace
   "I read the suggested code or explanation and trace through it mentally for the
   happy path and at least one edge case. If it doesn't make sense at this level,
   I don't trust it."

3. Ask for reasoning
   "If the AI makes a claim I'm uncertain about, I ask: 'Why does that work? Walk
   me through the reasoning.' Incoherent reasoning is a strong signal that the
   output is hallucinated or borrowed from a related-but-different context."

4. Look for hallucinated symbols
   "I grep for method names the AI suggests. If they don't exist in the codebase
   or library, the AI made them up. This happens more than people expect."

5. Own the output
   "I never ship something I couldn't explain line by line. If I can't explain
   why a piece of AI-suggested code is correct, I rewrite it from scratch."
```

---

## The Live Coding Round Caveat

**Do NOT use AI during live monitored coding rounds.**

Amazon, Google, and most companies explicitly flag this:
- Amazon: their coding rounds use an internal platform with no AI access, and they explicitly state no AI tools.
- Google: plain-text Google Doc with no autocomplete, no AI.
- Confluent/Uber: CoderPad, typically no AI.

The AI-fluency round is about **talking about** how you use AI in your day-to-day work — not using it in the interview itself. Confusing these two is a quick way to get disqualified.

---

## Resources

**Free:**
- [GitHub Copilot documentation](https://docs.github.com/en/copilot)
- [Anthropic prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Google's guidance on using AI in software engineering](https://www.youtube.com/results?search_query=google+ai+coding+assistant+software+engineering+2024)

**Paid (optional):**
- [Claude Pro](https://claude.ai) — for drill 1 and 2 (more capable for code understanding)
- [GitHub Copilot](https://github.com/features/copilot) — for drill 3 (IDE-integrated prompting)

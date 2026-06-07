# Behavioral Question Bank

> ~40 common behavioral questions, categorized. For the highest-frequency ones, a story pointer is included. End of file: "Tell me about yourself" script and "Why are you leaving Logward?" answer.

---

## Leadership & Ownership

1. Tell me about a time you took ownership of a problem that wasn't technically your responsibility. → **Story 2 (Production Incident RCA)**
2. Describe a time when you led a project without formal authority.
3. Tell me about a time you set a high standard for your team and held them to it. → **Story 7 (Unit Testing)**
4. Tell me about a time you delivered a project with a tight deadline despite obstacles.
5. Describe a situation where you saw a problem and fixed it proactively, before being asked.
6. Tell me about a time you made a decision with incomplete information.
7. Tell me about a time you had to rally your team around a difficult goal.

---

## Conflict & Disagreement

8. Tell me about a time you disagreed with a technical decision made by your manager or team. → **Story 15 (Disagree & Commit)**
9. Tell me about a time you had to push back on a deadline or scope cut that you felt was too aggressive.
10. Describe a situation where two team members had conflicting approaches. How did you resolve it?
11. Tell me about a time you received critical feedback that was hard to hear. How did you respond?
12. Tell me about a time you had to change someone's mind. What was your approach?

---

## Failure & Learning

13. Tell me about a time you failed. What did you do? → **Story 14 (Migration Failure)**
14. Tell me about a project that didn't go as planned. What would you do differently?
15. Describe a time you made a mistake that impacted production or customers. → **Story 2 (Incident) or Story 14 (Migration)**
16. Tell me about a time you had to pivot your approach mid-project because your original plan wasn't working.

---

## Dealing with Ambiguity

17. Tell me about a time you had to make progress with unclear or incomplete requirements.
18. Describe a situation where the priorities kept changing. How did you manage it?
19. Tell me about a project where you had to define the problem before you could solve it. → **Story 3 (Validation Layer — had to map all event flows first)**
20. Tell me about a time you had to make a technical decision with conflicting data.

---

## Prioritization & Trade-offs

21. Tell me about a time you had to make a trade-off between quality and speed. → **Story 15 (Disagree on RLS vs app filtering — chose speed, added safety net)**
22. Tell me about a time you had to say no to a feature request or stakeholder demand.
23. Describe a situation where you had multiple competing priorities. How did you decide what to work on first?
24. Tell me about a time you had to kill a project or feature you had invested in.

---

## Influence Without Authority

25. Tell me about a time you influenced a decision without being the final decision-maker. → **Story 15 (Disagree & Commit)**
26. Describe a situation where you had to get buy-in from stakeholders who weren't initially supportive.
27. Tell me about a time you drove adoption of a new practice or tool across a team. → **Story 7 (Unit Testing adoption)**
28. Tell me about a time you worked with a difficult colleague to reach a shared goal.

---

## Mentoring & Team Development

29. Tell me about a time you mentored someone. What was the outcome? → **Story 18 (Junior engineer → independent ownership in 8 weeks)**
30. Describe a time you gave difficult feedback to a colleague or report.
31. Tell me about a time you helped someone on your team grow technically.

---

## Dealing with Difficult Stakeholders

32. Tell me about a time you had to manage expectations with a customer or stakeholder who was frustrated.
33. Describe a situation where a stakeholder changed requirements late in the project. How did you handle it?
34. Tell me about a time you had to deliver bad news to a customer or business partner.

---

## Tell Me About Yourself & Why Leave

35. Tell me about yourself. → **(See script below)**
36. Why are you looking to leave Logward? → **(See script below)**
37. What are you looking for in your next role?
38. Where do you see yourself in 3-5 years?
39. Why are you interested in [this company]? → **(See per_company_framing.md for company-specific answers)**
40. What's your biggest strength? Biggest area for growth?

---

## Story Pointers for Highest-Frequency Questions

| Question | Best story |
|----------|-----------|
| "Tell me about a time you failed." | Story 14 — Migration Failure |
| "Tell me about a time you disagreed with your manager." | Story 15 — Disagree & Commit |
| "Tell me about your biggest achievement." | Story 1 — Trigger Service (-60%) or Story 5 — Razorpay (-70%) |
| "Tell me about a time you took ownership." | Story 2 — Production Incident RCA |
| "Tell me about a time you improved a process." | Story 6 — Autopay (-30%) or Story 11 — Invoice Printing |
| "Tell me about a time you mentored someone." | Story 18 — Junior engineer |
| "Tell me about a time you had to learn something new quickly." | Story 13 — Blockchain or Story 16 — Outbox Pattern |
| "Tell me about a time you set a high standard." | Story 7 — Unit Testing |

---

## "Tell Me About Yourself" — 75-Second Script

> Deliver this in a warm, confident tone. No memorization — internalize the arc.

*"I'm a backend engineer with 7 years of experience, currently at Logward where I build distributed systems for container tracking — we're tracking 10 million-plus records for enterprise logistics customers globally.*

*Before Logward, I spent 2 years at a fintech building payment infrastructure on top of Razorpay — I shipped a payment link system and an Autopay recurring-payment platform that meaningfully reduced both manual ops effort and fraud risk.*

*And before that, 3+ years at PharmEasy on their warehouse operations platform — order processing, supply chain, on-call reliability for critical services.*

*Across all three, the pattern is the same: building reliable, event-driven systems at scale. My stack is Python and Go primarily, with a lot of Kafka, Redis, and PostgreSQL.*

*I'm here because I'm ready for the scale and engineering depth of [this company] — specifically the [Kafka expertise at Confluent / real-time geospatial challenges at Uber / the reliability bar at Google]. I've built the foundation at smaller scale; I want to apply it at 10x."*

---

## "Why Are You Leaving Logward?" — Draft Answer

> Positive, growth-framed, no badmouthing. Always future-focused.

*"I've genuinely loved building at Logward — I came in as a senior engineer and grew into owning some of the most technically interesting parts of the platform. The Trigger Service architecture, the data validation layer, our multi-tenant design — those were hard, high-stakes problems and I'm proud of what we built.*

*But I've hit a natural ceiling in terms of what I can learn in this environment. The team is small, the scale is what it is, and I've found myself wanting to work with engineers who have solved these problems at 10x or 100x the scale I've operated at.*

*The timing is right. I'm in a strong position — I know distributed systems well, I've operated production systems at scale, and I want to bring that to a company like [X] where the engineering bar is higher and the problems are correspondingly harder."*

**Key rules:**
- Never say anything negative about Logward, your manager, or teammates.
- Never frame it as "I need more money" (even if that's true — let the comp negotiation be separate).
- Always end with a pull factor (what you're moving toward), not a push factor (what you're moving away from).

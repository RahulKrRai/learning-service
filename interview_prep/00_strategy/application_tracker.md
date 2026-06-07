# Application Tracker

> Your single source of truth for every conversation in flight. Update it the same day anything moves.
> Strategy reminder: **banks first** (Goldman/JPM as warm-up reps + competing-offer leverage), then **cluster the Tier-1 onsites (Google / Confluent / Uber / Atlassian / Amazon) into one 3-4 week window** so you can play offers against each other. Floor Rs 70L, target Rs 95L-1.3Cr. India only.

---

## 1. Application Table

Update **Stage** and **Next step** every time something changes. Keep "Next step" to one concrete action with an owner and a date ("Me: nudge recruiter Fri" / "Them: scheduling onsite").

Stage values (pick one): `Researching` -> `Referral sent` -> `Applied` -> `Recruiter screen` -> `OA / HackerRank` -> `Phone screen` -> `Onsite/Loop scheduled` -> `Onsite/Loop done` -> `Team match / HC` -> `Offer` -> `Negotiating` -> `Accepted` / `Rejected` / `On hold` / `Withdrawn`.

| Company | Role / Level | Applied date | Referral? | Recruiter (name / contact) | Stage | Next step (owner + date) | Notes |
|---|---|---|---|---|---|---|---|
| Goldman Sachs | VP, Backend | | | | | | Warm-up rep. Accept only if >= ~Rs 75-80L. HackerRank OA first. |
| JPMorgan | VP, Backend | | | | | | Warm-up rep + competing-offer leverage. Accept only if >= ~Rs 75-80L. |
| Confluent | Senior SWE | | | | | | **Best stack fit** (Kafka / event-driven). Up to ~Rs 1.21Cr. Highest-priority Tier-1. |
| Uber | Senior SWE | | | | | | ~Rs 1.07-1.76Cr. Distributed systems at scale + on-call maturity. |
| Google | L5 SWE | | | | | | ~Rs 1.1Cr. Coding in plain doc, no autocomplete/run. HC + team match. |
| Atlassian | Senior SWE | | | | | | Good WLB. Strong coding + design. |
| Amazon | SDE III / **L6** | | | | | | ~Rs 1.25Cr. **Insist on L6, never SDE II.** LPs in every round + Bar Raiser. |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

---

## 2. Referral Outreach Drafts

How to use these:
- Send to a 1st- or 2nd-degree connection who actually works there (LinkedIn, ex-colleagues, NIT Silchar alumni). A referral from someone who'll vouch beats a cold one.
- Personalize the **[bracketed]** bits before sending. Keep it short - they're busy.
- Attach your resume and the exact job-req link/ID so they can submit in one click.
- Track each send as a `Referral sent` row above with the date and the person's name in Notes.

### Confluent (lead with the Kafka / event-driven fit)

> Hi [Name], hope you're doing well! I've been following Confluent's work on [Flink / Kora / Tableflow - pick one you genuinely find interesting] and I'd love to throw my hat in for a Senior SWE role on the [data streaming / connect / cloud] side.
>
> Quick context on why I think it's a strong fit: I'm a backend engineer with 7+ years building event-driven, distributed systems - currently at Logward where I architected a multi-tenant Trigger Service (cut processing latency ~60%) and run Kafka-backed orchestration for container-lifecycle events across a 10M+ record platform. Confluent is genuinely the stack I reach for, so this is the role I'm most excited about.
>
> Would you be open to referring me, or pointing me to the right person? Happy to send my resume and the exact req. Thanks a ton either way!

### Uber (lead with scale + on-call ownership)

> Hi [Name], hope all's well at Uber! I'm exploring Senior SWE roles and Uber's [Marketplace / Fulfillment / Maps / Payments - pick a team] org is high on my list - the scale and ownership culture are exactly what I'm after.
>
> Background: 7+ years in backend / distributed systems. At Logward I designed the backend orchestration for container-lifecycle events on a multi-tenant platform (10M+ records), led production incident resolution and RCAs for critical tracking services, and built the data-validation/consistency layer across distributed workflows. Before that, payments at 56 AI and warehouse/supply-chain systems at PharmEasy - so I've carried real on-call for systems that can't go down.
>
> Would you be willing to refer me, or connect me with a recruiter on [team]? I'll send my resume and the req ID right over. Really appreciate it!

### Google (warm, humble, specifics over buzzwords)

> Hi [Name], hope you're doing great! I'm starting to interview for L5 SWE roles and would love to be considered at Google - reaching out because a referral from someone inside makes a real difference, and I'd value the chance.
>
> Short version of my background: 7+ years as a backend engineer working on distributed, event-driven systems. At Logward I architected a multi-tenant Trigger Service (~60% lower processing latency), built a cross-workflow data-consistency layer, and owned RCA for critical production incidents on a 10M+ record container-tracking platform. NIT Silchar CS grad, primarily Python/Go.
>
> If you're comfortable referring me I'd be grateful - I can send my resume and target a specific team/req if that helps, or leave it to general SWE. Thank you so much!

---

## 3. Loop Retro (fill in within an hour of each real interview)

Copy this block per interview while it's fresh. Brutal honesty here is what converts the next loop.

```
### [Company] - [Round type] - [Date]
1. What rusted (the thing that slowed you / you blanked on):
2. What landed (what clearly went well - keep doing it):
3. Question(s) asked (topic + difficulty, enough to recreate later):
4. Interviewer signal (tone, follow-ups, hints, where they pushed):
5. One fix before the next round (a single concrete drill or story tweak):
```

> After 2-3 retros, scan the "What rusted" lines together - the repeat offender is your next week's heaviest practice topic.

---

## 4. Pre-Loop Checklist (run the night before + morning of)

**Night before**
- [ ] Sleep target locked - in bed for 7.5-8 hrs; no new/hard problems after dinner (you'll only spook yourself).
- [ ] Logistics confirmed: time zone, video link tested, ID ready, backup internet (hotspot), water on desk.
- [ ] Re-read this company's row + Notes (level you're holding out for, comp floor, any prior-round retro).

**Morning of (60-90 min before)**
- [ ] One easy warm-up problem solved end-to-end (a known two-pointer / hashmap - rebuild confidence, don't learn).
- [ ] Story refresh: skim 3-4 STAR stories you'll likely use (Trigger Service latency win, data-consistency layer, a production RCA, a conflict/disagreement). For **Amazon**, map each to a Leadership Principle - LPs land in every round and behavioral is make-or-break there.
- [ ] Format reality-check: **Google** = plain doc, no autocomplete/run, so talk through compile/edge cases out loud. **Amazon** = do NOT use AI in live coding even if a GenAI-fluency round comes up separately.
- [ ] Voice + framing primer: say your "tell me about yourself" once out loud; have 2 smart questions ready for the interviewer.
- [ ] Light movement + protein; arrive at the link 5 min early, calm.

> Reminder: these loops are reps, not verdicts. DSA is rusty, not weak - the warm-up is there to remind your hands they know this. System design is your strength; lean on it.

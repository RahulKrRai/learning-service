# Strategy & Targets — Your North Star

> Last anchored: 2026-06-07 (Sunday). 12-week plan starts Week 1 = week of Mon Jun 8, 2026.
> Read this first, every time you doubt whether an offer or a process is worth your energy. Everything below is written for you, Rahul.

---

## 0. The One Insight That Frames Everything

You are at **54 LPA** as a Senior Backend Engineer with 7+ years. That number matters because it redefines what counts as a "win."

**At your current comp, an Amazon SDE II offer or a generic bank "VP" title is a lateral move, not an upgrade.** Amazon SDE II in India typically lands in the ~50-75 LPA range — i.e. roughly where you already are, sometimes a hair below. A bank VP title sounds senior, but the comp band frequently overlaps your floor too. Taking either of those at face value would be running a 12-week gauntlet just to stand still.

The **real jump** — the only thing that justifies the prep, the interviews, the disruption — is the **senior big-tech / top-product tier**: Google L5, Amazon **L6 (never II)**, Uber Senior, Confluent, Atlassian. That tier is where 95L-1.3Cr lives. That is the target. Banks are *reps and leverage*, not the destination (unless they overpay — see decision rules).

Internalize this: **title inflation is a trap; total comp at the right level is the signal.** You insist on the level that matches your 7 years and your actual scope (multi-tenant systems, distributed orchestration, production incident ownership). You do not let a recruiter "down-level" you into a lateral move dressed up as a promotion.

---

## 1. Target Table

| Company | Level | Est. comp range (INR / yr) | Why it fits you | Priority tier | Stack-fit notes |
|---|---|---|---|---|---|
| **Confluent** | Senior SWE | up to ~1.21 Cr | **Best stack fit by far.** Your Kafka, event-driven, distributed-systems background is exactly their product. You can speak their language natively in both coding and design. | **PRIMARY** | Kafka, event streaming, exactly-once semantics, distributed consensus. Your Trigger Service + event orchestration work is on-topic. |
| **Google** | L5 (Senior SWE) | ~1.1 Cr | Comp + brand + learning. L5 matches your 7 yrs and scope. Strong on system design (your strength). | **PRIMARY** | Coding in a plain doc, no autocomplete/run — practice cold. Hiring committee + team match; design is differentiator. |
| **Uber** | Senior SWE | ~1.07-1.76 Cr | High comp ceiling; distributed systems at massive scale; on-call maturity rewarded. Your incident/RCA track record is a direct match. | **PRIMARY** | Microservices at scale, real-time event pipelines, geo/marketplace systems. Strong coding + design both required. |
| **Amazon** | **L6 / SDE III** | ~1.25 Cr | Comp-max play. **Insist on L6.** WLB tradeoff accepted only because comp is top-tier. Behavioral is make-or-break here. | **PRIMARY** | LP in EVERY round, Bar Raiser, LP deep-dives, GenAI-fluency round. Do NOT use AI in live coding. **Never accept SDE II.** |
| **Atlassian** | Senior SWE | ~90L-1.2Cr (band) | Best **WLB** of the primary set; strong eng culture; good comp. Aligns with priority #2 (stability/WLB). | **PRIMARY** | Distributed systems, ownership, on-call maturity. Solid coding + design. |
| **Goldman Sachs** | VP | accept only if >= ~75-80L | Early reps + a real competing offer to pressure the Tier-1 cluster. Not a destination unless they overpay. | **LEVERAGE** | HackerRank OA -> DSA + backend + sometimes design + behavioral. Treat as warm-up. |
| **JPMorgan** | VP | accept only if >= ~75-80L | Same role as GS: warm-up reps and a leverage offer in hand. | **LEVERAGE** | HackerRank OA -> DSA + backend + behavioral. Treat as warm-up. |

*Note: comp ranges are estimates for India-based roles and vary with level calibration, sign-on, and stock price at grant. Verify against your own actual numbers — see the comp math below.*

---

## 2. Comp Math — How to Read an Offer

**Your numbers:**
- **Floor: Rs 70L.** Below this, do not move. (54 LPA today + the disruption cost of switching means a sub-70L offer is not worth it.)
- **Target band: Rs 95L - 1.3 Cr.** This is where the PRIMARY tier lands. Aim here; negotiate toward the top.

**How to actually read a big-tech / product offer.** Total comp is *not* base salary. It is the sum of four components, and recruiters quote whichever number flatters the offer:

1. **Base** — fixed cash, paid monthly. The only fully guaranteed, non-volatile piece.
2. **RSU (stock) grant** — the biggest swing factor at senior levels. Quoted as a total grant value vesting over (usually) **4 years**. **Always compute the per-year average**, and ask the **vesting schedule** — it is rarely a flat 25/25/25/25:
   - Amazon historically back-loads: **5 / 15 / 40 / 40**. Years 1-2 are thin; the big money is years 3-4. This is why Amazon pairs it with a large **sign-on bonus** to fill the early gap.
   - Google / Confluent / Uber / Atlassian are closer to flat or front-loaded — easier to compare year-on-year.
3. **Sign-on bonus** — one-time (or split across years 1-2) cash to bridge the RSU ramp and buy out unvested stock you're leaving behind. **It is not recurring.** Never average a sign-on over 4 years to inflate the headline.
4. **Annual bonus / target bonus** — a % of base, performance-dependent. Treat the *expected* (not max) value.

**The rule: compare on a steady-state per-year basis AND a true 4-year average.**
- **4-year average** = (4 x base) + (total RSU grant) + (total sign-on) + (4 x expected bonus), all divided by 4. Good for comparing offers head-to-head.
- **Steady-state year** (typically year 2-3, sign-on gone, RSUs ramped) = base + (one year's vesting tranche) + expected bonus. This is what you'll *actually* earn once the sign-on washes out — the more honest long-run number.
- Watch the **year-1 trough vs. cliff in year 5**: a fat sign-on can make year 1 look great and year 5 (when you need a refresher grant) look like a pay cut. Ask about **refresh/refresher grant** policy.

When a recruiter says "1.2 crore," ask: *"Is that the 4-year average including sign-on, or steady-state? What's the base, the grant value, the vest schedule, and the sign-on split?"* Make them break it into the four buckets. Then you do the per-year math yourself.

---

## 3. The Sequence — Banks First, Then Cluster the Tier-1 Onsites

The order is deliberate. Do not freelance it.

1. **Banks first (GS / JPM) as warm-up reps.** Their HackerRank OA -> DSA loop is the lowest-stakes way to knock the rust off (your DSA is rusty, not weak). You get live-interview reps under pressure *before* it matters, and — critically — you aim to walk away with a **real offer in hand**.
2. **A bank offer becomes leverage.** A concrete competing number (even one at/near your floor) is the single best negotiation tool for the PRIMARY tier. It sets a deadline and a floor that recruiters at Google/Uber/Confluent/Amazon/Atlassian will move to beat.
3. **Cluster the Tier-1 onsites into a tight 3-4 week window.** Do not let them spread across months. When the PRIMARY offers (or final loops) land close together, you can:
   - play them against each other for comp,
   - run parallel negotiations with live deadlines,
   - and avoid the trap of accepting the first offer because you're afraid nothing else will come.
   Multiple offers arriving in the same window is where the 95L-1.3Cr band actually gets unlocked.

**Timing implication:** front-load bank applications/OAs in the early weeks so their loops resolve *before* the Tier-1 cluster. Schedule the Tier-1 onsites to converge late, after you've had your reps and (ideally) have a bank offer in your pocket.

---

## 4. Priorities, Ranked — and What They Imply

Your stated ranking:

1. **Maximize comp** (highest)
2. **Stability / WLB**
3. **Learning / tech depth**
4. **Fast switch** (lowest)

What this ranking *implies* for decisions:

- **Comp #1** -> Push every offer to the top of its band; use the bank-leverage sequence; don't take a lateral move (the core insight in §0). Be willing to wait for the right number.
- **Stability/WLB #2** -> This is a real tiebreaker, not a footnote. Between two comparable comp offers, weight **Atlassian** (best WLB of the set) up and weight **Amazon** down (you accept Amazon's WLB tradeoff *only* because its comp is top-tier — if Amazon is not clearly the comp leader, its WLB cost isn't worth it).
- **Learning/tech depth #3** -> Favors **Confluent** (you'd go deep on the exact distributed-systems/streaming problems you already love) and **Google/Uber** (scale). A nice-to-have, not a reason to take less money.
- **Fast switch #4 (lowest)** -> You are **not** in a hurry. This is permission to run the full sequence, cluster onsites properly, and **walk away from any offer below floor**. Do not let urgency talk you into a lateral move. Time is on your side; use it.

Because fast-switch is dead last, the dominant failure mode to guard against is *impatience* — accepting early/lateral out of fear. The whole strategy is built to remove that fear by generating leverage.

---

## 5. Decision Rules (the box)

```
+---------------------------------------------------------------------------+
|  DECISION RULES — non-negotiable. Re-read before responding to any offer. |
+---------------------------------------------------------------------------+
|                                                                           |
|  1. NEVER accept Amazon SDE II. Insist on L6 / SDE III. SDE II is a       |
|     lateral move at 54 LPA, not an upgrade. Walk if they down-level you.  |
|                                                                           |
|  2. NEVER accept anything below the Rs 70L FLOOR. Period.                 |
|                                                                           |
|  3. A BANK (GS/JPM) VP offer is acceptable ONLY if >= ~Rs 75-80L.         |
|     Otherwise it is leverage/reps only — extract the offer, then leverage |
|     it; do not sign it.                                                   |
|                                                                           |
|  4. NEVER accept on the call. Always say "thank you, I need to review     |
|     the full breakdown and I'll get back to you by <date>." Get every     |
|     offer in WRITING, broken into base / RSU grant + vest schedule /      |
|     sign-on / bonus, before you react.                                    |
|                                                                           |
|  5. Compare offers on STEADY-STATE per-year comp AND true 4-year average  |
|     — never on the recruiter's headline number.                          |
|                                                                           |
|  6. Keep the SEQUENCE: banks first for reps + leverage, then cluster the  |
|     Tier-1 onsites in a 3-4 week window. Don't accept early and break the |
|     cluster — fast switch is your LOWEST priority.                        |
|                                                                           |
|  7. TARGET the top of the band (95L-1.3Cr). Use competing offers + a hard |
|     deadline to push there. Don't anchor to the first number quoted.      |
|                                                                           |
+---------------------------------------------------------------------------+
```

---

*This file is the north star. The 12-week prep plan (DSA-heaviest, system design as your strength, behavioral as the Amazon make-or-break) executes against these targets. When in doubt, optimize for comp at the right level — and never, ever take a lateral move dressed up as a promotion.*

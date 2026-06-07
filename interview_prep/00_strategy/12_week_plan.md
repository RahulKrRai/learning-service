# The 12-Week Master Plan — Rahul Kumar Rai

> Senior Backend Engineer, 7+ yrs (Logward / 56 AI / PharmEasy). Targeting Google L5, Confluent, Uber Senior, Atlassian, Amazon L6, with Goldman/JPMorgan VP as warm-up reps.
> Anchored to a real calendar: **Week 1 = Mon Jun 8, 2026**. Runs through **Sun Aug 30, 2026** (12 weeks).

---

## How to read this plan

Every week has **three parallel tracks** plus two milestone columns:

| Track | What it is | Weekly budget (of ~12-15 hrs) |
|---|---|---|
| **Code** | DSA pattern recond + LeetCode reps. **Weighted heaviest — your DSA is rusty, not weak.** | ~7-9 hrs |
| **Design** | System design framework + the 4 project deep-dives + classic designs. **This is your strength — keep it sharp, don't over-invest early.** | ~3-4 hrs |
| **Behavioral** | Story bank (STAR), Amazon Leadership Principles, Googleyness. **Make-or-break for Amazon.** | ~2-3 hrs |
| **Mock** | Timed, recorded, with a human or peer. Starts Week 5. | (inside the budget) |
| **Apply** | When to hit "submit." Banks first, then a tight Tier-1 cluster. | — |

### Time budget & compression
- **Baseline: 12-15 hrs/week** across the full 12 weeks (this document's default).
- **If you can sustain 20+ hrs/week**, fold the phases: do Phase 1 in ~3 weeks and Phase 2 in ~3, compressing the whole thing to **~8 weeks** (loops landing late July instead of late Aug). The *sequence* below never changes — only the calendar does.
- **Non-negotiable**: never let the Code track slip. If a week is short, cut Design first (it's your strength), then Behavioral, never Code.

### Strategy reminders baked into the timeline
- **Banks before Tier-1.** Goldman/JPMorgan OAs are your live-fire reps; do them while DSA is warming up, and only accept if >= ~Rs 75-80L. They also create a competing-offer clock.
- **Cluster the Tier-1 onsites** into a 3-4 week window (Weeks 9-11) so offers land close together for leverage.
- **Comp targets:** floor Rs 70L, target Rs 95L-1.3Cr. India-only, no relocation.
- **Amazon:** insist on **L6 / SDE III** — never accept SDE II. LP prep is not optional.

---

# PHASE 1 — Reconditioning (Weeks 1-4)
*Goal: knock the rust off DSA fundamentals, install one repeatable SD framework, and draft the raw story bank. End the phase by applying to the banks.*

---

## Week 1 — Mon Jun 8 → Sun Jun 14
**Theme: Arrays, Hashing, Two Pointers — wake the muscle up.**

- **Code** (heaviest):
  - [Arrays & Hashing](../01_dsa/patterns/01_arrays_hashing.md) — frequency maps, prefix sums, in-place tricks.
  - [Two Pointers](../01_dsa/patterns/02_two_pointers.md) — sorted-array convergence, fast/slow.
  - Reps: [Two Sum](https://leetcode.com/problems/two-sum/) (FREE), [3Sum](https://leetcode.com/problems/3sum/) (FREE), [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) (FREE), [Group Anagrams](https://leetcode.com/problems/group-anagrams/) (FREE).
  - Free video: [NeetCode — Arrays & Hashing](https://neetcode.io/roadmap) and search [takeUforward arrays playlist](https://www.youtube.com/results?search_query=takeuforward+arrays+playlist).
  - **Target: 12-15 problems this week** (easy/medium, re-grooving syntax). Hand-write in a plain doc once — Google bans autocomplete.
- **Design:**
  - [SD Interview Framework](../02_system_design/00_framework.md) — the 6-step loop (requirements → estimates → API → data model → high-level → deep-dive/bottlenecks). Read [System Design Primer](https://github.com/donnemartin/system-design-primer) intro + [Hello Interview delivery framework](https://www.hellointerview.com).
- **Behavioral:**
  - [Story Bank](../03_behavioral/01_story_bank.md) — brain-dump every project from the last 7 yrs into raw bullets (don't polish yet). Aim for 12-15 candidate stories.
- **Mock:** none.
- **Apply:** none — but **create/refresh your LeetCode, build a tracking sheet** for applications.

---

## Week 2 — Mon Jun 15 → Sun Jun 21
**Theme: Sliding Window, Stack, Binary Search.**

- **Code:**
  - [Sliding Window](../01_dsa/patterns/03_sliding_window.md), [Stack](../01_dsa/patterns/04_stack.md), [Binary Search](../01_dsa/patterns/05_binary_search.md).
  - Reps: [Best Time to Buy/Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) (FREE), [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) (FREE), [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) (FREE), [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) (FREE), [Min Stack](https://leetcode.com/problems/min-stack/) (FREE).
  - Free video: [NeetCode practice list](https://neetcode.io/practice).
  - **Target: 12-15 problems.**
- **Design:**
  - [SD Building Blocks](../02_system_design/01_building_blocks.md) — load balancers, caching, DB replication/sharding, CAP. Free: [ByteByteGo YouTube](https://www.youtube.com/results?search_query=bytebytego+system+design).
- **Behavioral:**
  - [Amazon Leadership Principles](../03_behavioral/02_amazon_leadership_principles.md) — map 2-3 of your raw stories to each of the 16 LPs (Ownership, Bias for Action, Dive Deep, Deliver Results first).
- **Mock:** none.
- **Apply:** none — start tailoring the resume for backend/distributed-systems roles.

---

## Week 3 — Mon Jun 22 → Sun Jun 28
**Theme: Linked Lists, Trees, Heaps + estimation math.**

- **Code:**
  - [Linked List](../01_dsa/patterns/06_linked_list.md), [Trees / BST](../01_dsa/patterns/07_trees.md), [Heap / Priority Queue](../01_dsa/patterns/08_heap_priority_queue.md).
  - Reps: [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) (FREE), [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) (FREE), [LRU Cache](https://leetcode.com/problems/lru-cache/) (FREE), [Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) (FREE), [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) (FREE), [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) (FREE).
  - **Target: 12-15 problems.**
- **Design:**
  - [Back-of-Envelope Estimation](../02_system_design/02_estimation.md) — QPS, storage, bandwidth napkin math. Free: System Design Primer "appendix — powers of two / latency numbers."
- **Behavioral:**
  - [STAR Template](../03_behavioral/03_star_template.md) — convert your **top 6 stories** into tight STAR form (Situation 1 line, Task 1 line, Action 60%, Result quantified).
- **Mock:** none.
- **Apply:** none — finalize the bank-targeted resume; line up referrals for Confluent/Uber/Google.

---

## Week 4 — Mon Jun 29 → Sun Jul 5
**Theme: Backtracking + Intervals; close out the fundamentals; APPLY TO BANKS.**

- **Code:**
  - [Backtracking](../01_dsa/patterns/09_backtracking.md), [Intervals](../01_dsa/patterns/10_intervals.md).
  - Reps: [Subsets](https://leetcode.com/problems/subsets/) (FREE), [Combination Sum](https://leetcode.com/problems/combination-sum/) (FREE), [Permutations](https://leetcode.com/problems/permutations/) (FREE), [Merge Intervals](https://leetcode.com/problems/merge-intervals/) (FREE), [Insert Interval](https://leetcode.com/problems/insert-interval/) (FREE).
  - **Light Phase-1 retro:** re-attempt any Week 1-3 problem you couldn't finish under time.
- **Design:**
  - [Classic Design: URL Shortener / Pastebin](../02_system_design/classic_designs/url_shortener.md) — your first end-to-end rep using the framework. Hash/key-gen, read-heavy caching, DB choice.
- **Behavioral:**
  - Polish remaining stories; draft your **2-minute "Tell me about yourself"** in [Story Bank](../03_behavioral/01_story_bank.md).
- **Mock:** none (light self-timed problem under 35 min to test readiness).
- **Apply:** **🎯 MILESTONE — Apply to Goldman Sachs VP & JPMorgan VP now.** These trigger HackerRank OAs (DSA-heavy) — perfect live-fire reps while you're sharp on fundamentals. Treat the OAs as graded mocks. Accept only if >= ~Rs 75-80L; primarily for leverage.

---

# PHASE 2 — Depth + Designs + Mocks (Weeks 5-8)
*Goal: graduate to hard DSA (DP, graphs, tries), build the 4 project designs that anchor your SD/behavioral story, and start real mocks. Fire the Tier-1 applications mid-phase so loops land in Phase 3.*

---

## Week 5 — Mon Jul 6 → Sun Jul 12
**Theme: Graphs (BFS/DFS) — the highest-leverage hard topic. Mocks begin.**

- **Code** (heaviest):
  - [Graphs — BFS/DFS](../01_dsa/patterns/11_graphs.md) — adjacency repr, grid traversal, connected components, cycle detection.
  - Reps: [Number of Islands](https://leetcode.com/problems/number-of-islands/) (FREE), [Clone Graph](https://leetcode.com/problems/clone-graph/) (FREE), [Course Schedule](https://leetcode.com/problems/course-schedule/) (FREE), [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) (FREE).
  - Free video: [NeetCode — Graphs](https://neetcode.io/roadmap).
- **Design:**
  - [Project Design 1 — Multi-Tenant Trigger Service](../02_system_design/project_designs/01_trigger_service.md) — your Logward flagship. Event-driven, tenant isolation, the -60% latency story. This doubles as a behavioral anchor.
- **Behavioral:**
  - [Googleyness & Leadership](../03_behavioral/04_googleyness.md) — collaboration, ambiguity, user-focus framing of your stories.
- **Mock:** **🎤 Mock #1 — one timed coding round** (45 min, recorded). Use [Pramp / interviewing.io free peer mocks](https://www.interviewing.io) or a peer. Topic: arrays/graphs.
- **Apply:** none — chase referrals; prep for the Tier-1 push next week.

---

## Week 6 — Mon Jul 13 → Sun Jul 19
**Theme: Advanced Graphs (topo sort, Dijkstra, union-find). FIRST Tier-1 apps.**

- **Code:**
  - [Advanced Graphs](../01_dsa/patterns/12_advanced_graphs.md) — topological sort, Dijkstra, Union-Find, MST.
  - Reps: [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) (FREE), [Network Delay Time](https://leetcode.com/problems/network-delay-time/) (FREE), [Number of Connected Components](https://leetcode.com/problems/graph-valid-tree/) *(Premium — free alt: [NeetCode Graph Valid Tree](https://neetcode.io/problems/valid-tree))*, [Redundant Connection](https://leetcode.com/problems/redundant-connection/) (FREE).
- **Design:**
  - [Project Design 2 — Data Validation & Consistency Layer](../02_system_design/project_designs/02_validation_layer.md) — cross-workflow consistency across distributed services; idempotency, exactly-once-ish semantics, reconciliation.
- **Behavioral:**
  - Rehearse LP deep-dives out loud; record yourself. Tighten "Dive Deep" + "Deliver Results."
- **Mock:** **🎤 Mock #2 — coding** (graphs/heap).
- **Apply:** **🎯 MILESTONE — Apply to Confluent (best stack fit) & Uber Senior.** Submit via referral if possible. These have longer pipelines, so start them now to land loops in Weeks 9-11.

---

## Week 7 — Mon Jul 20 → Sun Jul 26
**Theme: Dynamic Programming (1-D). Remaining Tier-1 apps.**

- **Code:**
  - [Dynamic Programming — 1-D](../01_dsa/patterns/13_dp_1d.md) — you already have local reps (knapsack, coin change, rod cutting, LCS in `DP/`); convert them to interview speed.
  - Reps: [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) (FREE), [House Robber](https://leetcode.com/problems/house-robber/) (FREE), [Coin Change](https://leetcode.com/problems/coin-change/) (FREE), [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) (FREE), [Word Break](https://leetcode.com/problems/word-break/) (FREE).
  - Free video: [takeUforward DP playlist](https://www.youtube.com/results?search_query=takeuforward+dynamic+programming+playlist), [Aditya Verma DP](https://www.youtube.com/results?search_query=aditya+verma+dynamic+programming).
- **Design:**
  - [Project Design 3 — Container Lifecycle Orchestration](../02_system_design/project_designs/03_lifecycle_orchestration.md) — backend orchestration for container lifecycle events; state machines, workflow durability.
- **Behavioral:**
  - Map each project design above to its STAR story so the design round and behavioral round reinforce each other.
- **Mock:** **🎤 Mock #3 — system design** (use a project design or [URL shortener](../02_system_design/classic_designs/url_shortener.md)). Free SD mocks via [Hello Interview](https://www.hellointerview.com) / interviewing.io.
- **Apply:** **🎯 MILESTONE — Apply to Google (L5), Amazon (insist L6), Atlassian.** Time it so OAs and recruiter screens schedule the onsite loops into Weeks 9-11.

---

## Week 8 — Mon Jul 27 → Sun Aug 2
**Theme: DP (2-D) + Tries; close out the design set.**

- **Code:**
  - [Dynamic Programming — 2-D](../01_dsa/patterns/14_dp_2d.md), [Tries](../01_dsa/patterns/15_tries.md).
  - Reps: [Unique Paths](https://leetcode.com/problems/unique-paths/) (FREE), [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) (FREE), [Edit Distance](https://leetcode.com/problems/edit-distance/) (FREE), [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) (FREE), [Word Search II](https://leetcode.com/problems/word-search-ii/) (FREE).
- **Design:**
  - [Project Design 4 — Production Incident RCA / Tracking Reliability](../02_system_design/project_designs/04_incident_rca.md) — your on-call/RCA leadership story rendered as a reliability/observability design (alerting, dashboards, runbooks, blast-radius). Plus skim [Classic: Rate Limiter](../02_system_design/classic_designs/rate_limiter.md).
- **Behavioral:**
  - Full LP dry-run with a friend: 6 LPs, 2 min each, no notes.
- **Mock:** **🎤 Mock #4 — coding** (DP, the topic most likely to ambush you).
- **Apply:** Respond to/schedule all OAs and recruiter screens; **lock onsite loop dates into the Week 9-11 window.**

---

# PHASE 3 — Loops, Intensive Mocks, Negotiation (Weeks 9-12)
*Goal: peak performance during a tight cluster of onsite loops, simulate the real thing relentlessly, then negotiate from a position of stacked offers.*

---

## Week 9 — Mon Aug 3 → Sun Aug 9
**Theme: First loops + full-mock intensity. AI-fluency round prep.**

- **Code:**
  - Spaced-repetition over your weak patterns (DP, advanced graphs, intervals). Daily 2-problem warm-up before any real interview. Re-read [Graphs](../01_dsa/patterns/11_graphs.md) + [DP 1-D](../01_dsa/patterns/13_dp_1d.md).
- **Design:**
  - Rapid review of all 4 project designs + the [SD Framework](../02_system_design/00_framework.md). Be able to whiteboard any of them in 35 min.
- **Behavioral:**
  - [AI-Fluency / Code-Comprehension](../04_ai_fluency/01_ai_fluency.md) — the 2026 cross-board round. Be fluent discussing LLM-assisted dev, but remember: **do NOT use AI in live coding** (esp. Amazon).
- **Mock:** **🎤 Full mock loop #1** — 1 coding + 1 design + 1 behavioral back-to-back, simulating a real onsite day.
- **Apply:** **🎯 First onsite loops likely begin** (banks + earliest Tier-1). Front-load the banks here as final warm-up reps.

---

## Week 10 — Mon Aug 10 → Sun Aug 16
**Theme: Peak loop week — Tier-1 cluster center.**

- **Code:**
  - Maintenance only: daily warm-up, review missed problems from live loops same-day while fresh.
- **Design:**
  - Targeted prep per company: Confluent → lean on event-driven/Kafka ([Trigger Service](../02_system_design/project_designs/01_trigger_service.md)); Uber → scale/geo; Google → fundamentals depth.
- **Behavioral:**
  - Company-specific: Amazon LPs every round + Bar Raiser; Google Googleyness. Review [Amazon LPs](../03_behavioral/02_amazon_leadership_principles.md) the night before each loop.
- **Mock:** **🎤 Full mock loop #2** (or live loop debrief if you're mid-cluster).
- **Apply:** **🎯 Core Tier-1 onsites (Google / Confluent / Uber / Atlassian / Amazon).** Keep them packed tight for offer-timing leverage.

---

## Week 11 — Mon Aug 17 → Sun Aug 23
**Theme: Final loops + closing the cluster.**

- **Code:**
  - Light daily warm-up; rest the brain between loops — recovery is performance.
- **Design:**
  - Just-in-time refresh of the relevant project design before each remaining loop.
- **Behavioral:**
  - Refine answers using feedback patterns you've noticed across loops. Prep thoughtful questions for each panel (signals seniority).
- **Mock:** As needed for any company you haven't yet faced live.
- **Apply:** **🎯 Remaining onsites wrap.** Begin signaling timelines to recruiters so offers converge. Ask each recruiter for their decision timeline.

---

## Week 12 — Mon Aug 24 → Sun Aug 30
**Theme: NEGOTIATION & decision.**

- **Code:** Maintenance warm-ups only (in case of a straggler round or a re-loop request).
- **Design:** None.
- **Behavioral:** None.
- **Mock:** **🎤 Negotiation role-play** — rehearse with a friend playing recruiter.
- **Apply / Close:** **🎯 MILESTONE — Negotiate.** Use [Negotiation Playbook](../00_strategy/negotiation_playbook.md).
  - Get **everything in writing**; never give a number first; **stack competing offers** (this is why you clustered the loops).
  - **Floor Rs 70L. Push toward Rs 95L-1.3Cr.** Walk away below floor.
  - **Amazon: confirm the level is L6/SDE III in writing** before deep negotiation — never SDE II.
  - Weigh against your priorities: (1) comp, (2) stability/WLB, (3) learning/depth, (4) speed. Confluent = best stack fit; Atlassian = best WLB; Amazon = comp-max with WLB tradeoff.

---

## Phase summary

| Phase | Weeks | Dates | Focus | Apply milestone |
|---|---|---|---|---|
| **1 — Recondition** | 1-4 | Jun 8 – Jul 5 | DSA fundamentals recond, SD framework, draft story bank | Banks (GS/JPM VP) in Wk 4 |
| **2 — Depth** | 5-8 | Jul 6 – Aug 2 | Hard DSA (graphs/DP/tries), 4 project designs, mocks begin | Confluent/Uber Wk 6; Google/Amazon/Atlassian Wk 7 |
| **3 — Loops** | 9-12 | Aug 3 – Aug 30 | Cluster onsite loops, intensive full mocks, negotiate | Loops Wk 9-11; negotiate Wk 12 |

## Weekly discipline checklist
- [ ] Hit the **Code** target (don't let it slip — it's the rusty track and weighted heaviest).
- [ ] One **Design** rep using the 6-step framework, out loud or on a whiteboard.
- [ ] At least one **Behavioral** story rehearsed aloud / recorded.
- [ ] Log every problem missed → re-attempt within the same week.
- [ ] From Week 5: at least one **timed, recorded mock**.

> **Compression note again:** at 20+ hrs/week, run Phases 1-2 at ~1.5x speed and you'll be loop-ready by ~Week 8 (early Aug). The order of operations is fixed; only the calendar compresses.

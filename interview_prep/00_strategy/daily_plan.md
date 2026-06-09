# Daily Study Plan — 12-Week Interview Prep

**You:** Rahul Kumar Rai, Senior Backend Engineer (7+ yrs), Bangalore. Targeting Google L5, Confluent, Uber Senior, Atlassian, Amazon L6, with GS/JPM VP as warm-up reps.

**Anchor:** Today is Sun Jun 7, 2026. **Week 1 starts Mon Jun 8, 2026.** Phase 1 (skill rebuild) runs Weeks 1-4 (Jun 8 - Jul 5). Phase 2 (mocks + onsite clustering) starts Week 5.

**Time budget (realistic, full-time job):**
- Weekdays: ~2-2.5 hrs (one ~75-90 min code block + ~15 min behavioral/design micro-task + ~20 min review).
- Saturday: ~4-5 hrs (deep work + system design).
- Sunday: ~2-3 hrs (review, spaced repetition, light reading) — protect this for WLB; it is a half-rest day.

**How to use this file:**
- Pattern files live in [`../01_dsa/patterns/`](../01_dsa/patterns/). Each day links the file to read *before* you code.
- "Solve" means: 20 min attempt cold -> if stuck, read the pattern hint, not the full solution -> implement -> re-implement from blank the next review touch.
- Google L5 reminder: practice coding in a **plain doc with no autocomplete and no run button** at least once a week (marked DOC DRILL).
- Track every problem in a simple sheet: `problem | date | cold-solve? (Y/N) | revisit date`. Spaced-repetition (SR) days below pull from your "N" pile first.

---

## Legend

- **Read:** the pattern file to study first (links into `../01_dsa/patterns/`).
- **Solve:** count + named problems (LeetCode slug links are free unless marked Premium; free video on the matching NeetCode page).
- **Micro-task:** ~15 min behavioral or design rep (links into `../03_behavioral/` and `../02_system_design/`).
- All LeetCode links: `https://leetcode.com/problems/<slug>/`. Free video walkthrough: `https://neetcode.io/problems/<slug>`.

---

# PHASE 1 — Weeks 1-4 (Mon Jun 8 - Sun Jul 5)

Rebuild DSA muscle (you are rusty, not weak) while keeping design sharp and seeding your Amazon LP story bank.

## Week 1 — Arrays, Hashing, Two Pointers (Jun 8-14)

### Mon Jun 8 — Arrays & Hashing
- **Read:** [`../01_dsa/patterns/02_hashing_frequency.md`](../01_dsa/patterns/02_hashing_frequency.md)
- **Solve (3):** [two-sum](https://leetcode.com/problems/two-sum/), [contains-duplicate](https://leetcode.com/problems/contains-duplicate/), [valid-anagram](https://leetcode.com/problems/valid-anagram/)
- **Micro-task (behavioral):** In [`../03_behavioral/story_bank.md`](../03_behavioral/story_bank.md), draft the headline + situation for your **Trigger Service re-architecture** story (the -60% latency one). One paragraph, STAR skeleton only.

### Tue Jun 9 — Arrays & Hashing (group/encode)
- **Read:** [`../01_dsa/patterns/02_hashing_frequency.md`](../01_dsa/patterns/02_hashing_frequency.md) (re-skim grouping section)
- **Solve (3):** [group-anagrams](https://leetcode.com/problems/group-anagrams/), [top-k-frequent-elements](https://leetcode.com/problems/top-k-frequent-elements/), [product-of-array-except-self](https://leetcode.com/problems/product-of-array-except-self/)
- **Micro-task (design):** Read the intro of the [System Design Primer](https://github.com/donnemartin/system-design-primer) and jot a 5-line glossary (latency vs throughput, vertical vs horizontal scaling) in [`../02_system_design/notes.md`](../02_system_design/notes.md).

### Wed Jun 10 — Two Pointers
- **Read:** [`../01_dsa/patterns/01_two_pointers_sliding_window.md`](../01_dsa/patterns/01_two_pointers_sliding_window.md)
- **Solve (3):** [valid-palindrome](https://leetcode.com/problems/valid-palindrome/), [two-sum-ii-input-array-is-sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/), [3sum](https://leetcode.com/problems/3sum/)
- **Micro-task (behavioral):** Finish the STAR for the Trigger Service story — write the **Action** bullets (what *you* specifically did). Map it to Amazon LPs: *Ownership*, *Dive Deep*.

### Thu Jun 11 — Two Pointers / Sliding Window bridge
- **Read:** [`../01_dsa/patterns/01_two_pointers_sliding_window.md`](../01_dsa/patterns/01_two_pointers_sliding_window.md) (container/trapping section)
- **Solve (2):** [container-with-most-water](https://leetcode.com/problems/container-with-most-water/), [trapping-rain-water](https://leetcode.com/problems/trapping-rain-water/) (hard — timebox 35 min, then read hint)
- **Micro-task (design):** Watch ~10 min of [ByteByteGo on YouTube](https://www.youtube.com/results?search_query=bytebytego+system+design+basics) on load balancing; one-line note.

### Fri Jun 12 — Sliding Window
- **Read:** [`../01_dsa/patterns/01_two_pointers_sliding_window.md`](../01_dsa/patterns/01_two_pointers_sliding_window.md)
- **Solve (3):** [best-time-to-buy-and-sell-stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/), [longest-substring-without-repeating-characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/), [longest-repeating-character-replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)
- **Micro-task (behavioral):** Finish Trigger Service story — write **Result** with hard numbers and the *Learn and Be Curious* angle. This is now a complete, reusable story.

### Sat Jun 13 — Deep work + Design kickoff (~4-5 hrs)
- **Read:** [`../01_dsa/patterns/01_two_pointers_sliding_window.md`](../01_dsa/patterns/01_two_pointers_sliding_window.md) (hard variants)
- **Solve (3):** [permutation-in-string](https://leetcode.com/problems/permutation-in-string/), [minimum-window-substring](https://leetcode.com/problems/minimum-window-substring/) (hard), [sliding-window-maximum](https://leetcode.com/problems/sliding-window-maximum/) (hard, uses deque)
- **Design (60-90 min):** Read the [Hello Interview](https://www.hellointerview.com) system-design delivery framework. Write your own 7-step template (requirements -> estimates -> API -> data model -> high-level -> deep dive -> bottlenecks) into [`../02_system_design/framework.md`](../02_system_design/framework.md). This template is your safety net for every design round.

### Sun Jun 14 — SR Review + light reading (~2 hrs)
- **SR Review:** Re-solve from blank any 3 problems you marked "N" (didn't cold-solve) this week. Arrays/two-pointers focus.
- **Micro-task (AI fluency):** Skim [`../04_ai_fluency/`](../04_ai_fluency/) plan; note one way you'd explain "how would you use an LLM to help debug a distributed trace" (Amazon GenAI-fluency round prep). 5 lines.
- **Rest the afternoon.**

---

## Week 2 — Stack, Binary Search, Linked List (Jun 15-21)

### Mon Jun 15 — Stack
- **Read:** [`../01_dsa/patterns/04_stack_monotonic.md`](../01_dsa/patterns/04_stack_monotonic.md)
- **Solve (3):** [valid-parentheses](https://leetcode.com/problems/valid-parentheses/), [min-stack](https://leetcode.com/problems/min-stack/), [evaluate-reverse-polish-notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/)
- **Micro-task (behavioral):** Draft headline + situation for your **production incident RCA** story (Logward critical tracking services). Map to *Customer Obsession*, *Bias for Action*.

### Tue Jun 16 — Stack (monotonic)
- **Read:** [`../01_dsa/patterns/04_stack_monotonic.md`](../01_dsa/patterns/04_stack_monotonic.md) (monotonic stack section)
- **Solve (3):** [daily-temperatures](https://leetcode.com/problems/daily-temperatures/), [car-fleet](https://leetcode.com/problems/car-fleet/), [largest-rectangle-in-histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) (hard — timebox 35 min)
- **Micro-task (design):** Note in [`../02_system_design/notes.md`](../02_system_design/notes.md): caching strategies (write-through vs write-back, eviction). Tie to your real Redis usage at Logward.

### Wed Jun 17 — Binary Search
- **Read:** [`../01_dsa/patterns/03_binary_search.md`](../01_dsa/patterns/03_binary_search.md)
- **Solve (3):** [binary-search](https://leetcode.com/problems/binary-search/), [search-a-2d-matrix](https://leetcode.com/problems/search-a-2d-matrix/), [koko-eating-bananas](https://leetcode.com/problems/koko-eating-bananas/)
- **Micro-task (behavioral):** Finish RCA story Action + Result. Practice saying it out loud once, under 2 minutes.

### Thu Jun 18 — Binary Search (on rotated / answer space)
- **Read:** [`../01_dsa/patterns/03_binary_search.md`](../01_dsa/patterns/03_binary_search.md) (rotated array section)
- **Solve (3):** [find-minimum-in-rotated-sorted-array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/), [search-in-rotated-sorted-array](https://leetcode.com/problems/search-in-rotated-sorted-array/), [median-of-two-sorted-arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) (hard — read pattern first)
- **Micro-task (design):** 10 min of [Hussein Nasser on YouTube](https://www.youtube.com/results?search_query=hussein+nasser+database+indexing) on DB indexing; one-line note.

### Fri Jun 19 — Linked List
- **Read:** [`../01_dsa/patterns/05_linked_list.md`](../01_dsa/patterns/05_linked_list.md)
- **Solve (3):** [reverse-linked-list](https://leetcode.com/problems/reverse-linked-list/), [merge-two-sorted-lists](https://leetcode.com/problems/merge-two-sorted-lists/), [linked-list-cycle](https://leetcode.com/problems/linked-list-cycle/)
- **Micro-task (behavioral):** Draft your **"tell me about yourself"** 90-second pitch in [`../03_behavioral/story_bank.md`](../03_behavioral/story_bank.md). Lead with Logward distributed-systems ownership.

### Sat Jun 20 — Deep work + Design (~4-5 hrs)  | **DOC DRILL**
- **Read:** [`../01_dsa/patterns/05_linked_list.md`](../01_dsa/patterns/05_linked_list.md) (advanced section)
- **Solve (3, in a plain Google Doc — no IDE, no run):** [reorder-list](https://leetcode.com/problems/reorder-list/), [remove-nth-node-from-end-of-list](https://leetcode.com/problems/remove-nth-node-from-end-of-list/), [lru-cache](https://leetcode.com/problems/lru-cache/)
- **Design (60-90 min):** Design a **URL shortener / TinyURL** using your framework. Free ref: [System Design Primer](https://github.com/donnemartin/system-design-primer). Write the full pass into [`../02_system_design/practiced/url-shortener.md`](../02_system_design/practiced/url-shortener.md).

### Sun Jun 21 — SR Review (~2 hrs)
- **SR Review:** Re-solve from blank 3 "N"-pile problems (Week 1-2). Include [lru-cache](https://leetcode.com/problems/lru-cache/) again — it shows up everywhere.
- **Micro-task (behavioral):** Read the [Amazon Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) list; tag which 2 of your 3 stories so far cover which LPs. Find your gaps.
- **Rest the afternoon.**

---

## Week 3 — Trees, Tries, Heaps (Jun 22-28)

### Mon Jun 22 — Binary Trees (traversal)
- **Read:** [`../01_dsa/patterns/06_trees_bst.md`](../01_dsa/patterns/06_trees_bst.md)
- **Solve (3):** [invert-binary-tree](https://leetcode.com/problems/invert-binary-tree/), [maximum-depth-of-binary-tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/), [diameter-of-binary-tree](https://leetcode.com/problems/diameter-of-binary-tree/)
- **Micro-task (behavioral):** Draft **conflict / disagreement** story (e.g. pushing back on a design at 56 AI or Logward). Map to *Have Backbone; Disagree and Commit*.

### Tue Jun 23 — Binary Trees (BFS / BST)
- **Read:** [`../01_dsa/patterns/06_trees_bst.md`](../01_dsa/patterns/06_trees_bst.md) (level-order + BST section)
- **Solve (3):** [binary-tree-level-order-traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/), [validate-binary-search-tree](https://leetcode.com/problems/validate-binary-search-tree/), [kth-smallest-element-in-a-bst](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)
- **Micro-task (design):** Note: SQL vs NoSQL decision criteria. Tie to your PostgreSQL + MongoDB real usage.

### Wed Jun 24 — Trees (construct / LCA)
- **Read:** [`../01_dsa/patterns/06_trees_bst.md`](../01_dsa/patterns/06_trees_bst.md) (recursion-with-return-value section)
- **Solve (3):** [lowest-common-ancestor-of-a-binary-search-tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/), [construct-binary-tree-from-preorder-and-inorder-traversal](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/), [binary-tree-maximum-path-sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) (hard)
- **Micro-task (behavioral):** Finish conflict story Action + Result. Say it out loud once.

### Thu Jun 25 — Tries
- **Read:** [`../01_dsa/patterns/07_trie.md`](../01_dsa/patterns/07_trie.md)
- **Solve (3):** [implement-trie-prefix-tree](https://leetcode.com/problems/implement-trie-prefix-tree/), [design-add-and-search-words-data-structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/), [word-search-ii](https://leetcode.com/problems/word-search-ii/) (hard — trie + backtracking)
- **Micro-task (design):** 10 min of [ByteByteGo on YouTube](https://www.youtube.com/results?search_query=bytebytego+message+queue+kafka) on message queues. This is your Confluent home turf — note one Kafka-specific insight.

### Fri Jun 26 — Heaps / Priority Queue
- **Read:** [`../01_dsa/patterns/08_heap_topk_mergek.md`](../01_dsa/patterns/08_heap_topk_mergek.md)
- **Solve (3):** [kth-largest-element-in-a-stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/), [last-stone-weight](https://leetcode.com/problems/last-stone-weight/), [k-closest-points-to-origin](https://leetcode.com/problems/k-closest-points-to-origin/)
- **Micro-task (behavioral):** Draft **"biggest failure / mistake"** story. Map to *Earn Trust*, *Learn and Be Curious*. Be honest; show the lesson.

### Sat Jun 27 — Deep work + Design (~4-5 hrs)
- **Read:** [`../01_dsa/patterns/08_heap_topk_mergek.md`](../01_dsa/patterns/08_heap_topk_mergek.md) (two-heaps + merge section)
- **Solve (3):** [task-scheduler](https://leetcode.com/problems/task-scheduler/), [merge-k-sorted-lists](https://leetcode.com/problems/merge-k-sorted-lists/) (hard), [find-median-from-data-stream](https://leetcode.com/problems/find-median-from-data-stream/) (hard, two heaps)
- **Design (60-90 min):** Design a **distributed message queue / Kafka-like system**. This is your strongest, most strategic design (Confluent). Free refs: [Confluent/Kafka docs blog](https://www.confluent.io/blog/) + [ByteByteGo YouTube](https://www.youtube.com/results?search_query=bytebytego+design+kafka). Write into [`../02_system_design/practiced/distributed-queue.md`](../02_system_design/practiced/distributed-queue.md).

### Sun Jun 28 — SR Review (~2-3 hrs)
- **SR Review:** Re-solve 4 "N"-pile problems (trees + heaps weighted). Trees are the most common rust point — over-index here.
- **Micro-task (behavioral):** You now have 5 stories. Build a **story-to-LP coverage grid** in [`../03_behavioral/story_bank.md`](../03_behavioral/story_bank.md). Every Amazon LP should map to at least one story; flag the uncovered ones.
- **Rest the afternoon.**

---

## Week 4 — Backtracking, Graphs, + Phase-1 consolidation (Jun 29 - Jul 5)

### Mon Jun 29 — Backtracking
- **Read:** [`../01_dsa/patterns/13_backtracking.md`](../01_dsa/patterns/13_backtracking.md)
- **Solve (3):** [subsets](https://leetcode.com/problems/subsets/), [combination-sum](https://leetcode.com/problems/combination-sum/), [permutations](https://leetcode.com/problems/permutations/)
- **Micro-task (behavioral):** Draft **"delivered under tight deadline / ambiguity"** story (Razorpay Payment Link or Autopay at 56 AI). Map to *Deliver Results*, *Invent and Simplify*.

### Tue Jun 30 — Backtracking (grid / pruning)
- **Read:** [`../01_dsa/patterns/13_backtracking.md`](../01_dsa/patterns/13_backtracking.md) (pruning section)
- **Solve (3):** [word-search](https://leetcode.com/problems/word-search/), [palindrome-partitioning](https://leetcode.com/problems/palindrome-partitioning/), [combination-sum-ii](https://leetcode.com/problems/combination-sum-ii/)
- **Micro-task (design):** Note: idempotency + exactly-once vs at-least-once delivery. You lived this at Logward (data consistency layer) and 56 AI (payments) — write 4 lines you can speak to.

### Wed Jul 1 — Graphs (BFS/DFS)
- **Read:** [`../01_dsa/patterns/09_graph_bfs_dfs.md`](../01_dsa/patterns/09_graph_bfs_dfs.md)
- **Solve (3):** [number-of-islands](https://leetcode.com/problems/number-of-islands/), [clone-graph](https://leetcode.com/problems/clone-graph/), [pacific-atlantic-water-flow](https://leetcode.com/problems/pacific-atlantic-water-flow/)
- **Micro-task (behavioral):** Finish deadline story. Say it out loud once.

### Thu Jul 2 — Graphs (topological sort)
- **Read:** [`../01_dsa/patterns/09_graph_bfs_dfs.md`](../01_dsa/patterns/09_graph_bfs_dfs.md) (topo-sort + cycle detection)
- **Solve (3):** [course-schedule](https://leetcode.com/problems/course-schedule/), [course-schedule-ii](https://leetcode.com/problems/course-schedule-ii/), [graph-valid-tree](https://leetcode.com/problems/graph-valid-tree/) (LeetCode Premium — free alt: [LintCode 178](https://www.lintcode.com/problem/178/) or [NeetCode graph-valid-tree](https://neetcode.io/problems/valid-tree))
- **Micro-task (design):** 10 min of [Gaurav Sen on YouTube](https://www.youtube.com/results?search_query=gaurav+sen+consistent+hashing) on consistent hashing; one-line note.

### Fri Jul 3 — Graphs (Dijkstra / union-find) | **DOC DRILL**
- **Read:** [`../01_dsa/patterns/09_graph_bfs_dfs.md`](../01_dsa/patterns/09_graph_bfs_dfs.md) (weighted + union-find)
- **Solve (3, in a plain doc — no IDE):** [network-delay-time](https://leetcode.com/problems/network-delay-time/), [number-of-connected-components-in-an-undirected-graph](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) (Premium — free alt: [NeetCode](https://neetcode.io/problems/count-connected-components)), [redundant-connection](https://leetcode.com/problems/redundant-connection/)
- **Micro-task (behavioral):** Draft **"mentored / influenced without authority"** story (you led incident RCA, introduced unit testing). Map to *Hire and Develop the Best*.

### Sat Jul 4 — Phase-1 capstone + Design (~4-5 hrs)
- **Mixed set (4), timed 30 min each, random topics** to simulate not knowing what's coming: pick one each from arrays, trees, graphs, heaps off your "N" pile.
- **Design (60-90 min):** Design a **rate limiter** (token bucket vs sliding window). Free ref: [System Design Primer](https://github.com/donnemartin/system-design-primer). Write into [`../02_system_design/practiced/rate-limiter.md`](../02_system_design/practiced/rate-limiter.md).
- **Review:** Skim all pattern files in [`../01_dsa/patterns/`](../01_dsa/patterns/) — you should now recognize every pattern name on sight.

### Sun Jul 5 — Phase-1 retro + SR (~2-3 hrs)
- **SR Review:** Re-solve 4 hardest "N"-pile problems from the whole phase.
- **Retro:** In [`../00_strategy/`](../00_strategy/), write 10 lines: which patterns are solid, which still scare you. **Weeks 5-12 weekly rhythm should over-weight your weak 2-3 patterns.**
- **Behavioral:** Confirm story bank has 6-7 complete STAR stories with full LP coverage. If a Google "Googleyness" or Confluent/Uber ownership angle is thin, note it.
- **Rest. You have rebuilt the foundation.**

---

# PHASE 2+ — Weeks 5-12 (Jul 6 - ~Aug 30): Sustainable Weekly Rhythm

By now DSA recognition is back. The job shifts from *learning* to *performing under pressure*: mocks, timed sets, and clustering your Tier-1 onsites into a 3-4 week leverage window. **Front-load the bank OAs (GS/JPM) as warm-up reps in Weeks 5-6.**

**Strategic sequencing reminder:**
- **Weeks 5-6:** Banks first (GS/JPM HackerRank OAs) — low-stakes reps + a possible early competing offer (accept only if >= ~Rs 75-80L).
- **Weeks 7-10:** Cluster Google L5, Confluent, Uber Senior, Atlassian, Amazon L6 onsites into a tight window so offers land together for negotiation leverage. **Amazon: insist on L6, never SDE II.**
- **Weeks 11-12:** Buffer for re-loops, negotiation, and rest.

## The Sustainable Weekly Template (repeat each week, Weeks 5-12)

A realistic full-time-job week = **6 sessions**:

| Slot | When (suggested) | Activity |
|---|---|---|
| **Code Session 1** | Mon ~90 min | 2-3 problems from this week's focus pattern. Re-read the matching [`../01_dsa/patterns/`](../01_dsa/patterns/) file first. |
| **Code Session 2** | Wed ~90 min | 2-3 problems, **mixed topics, timed 25-30 min each** (simulate the unknown). DOC DRILL every 2nd week for the Google plain-doc format. |
| **Code Session 3** | Fri ~75 min | 1 hard problem + re-solve 2 SR "N"-pile problems from blank. |
| **Design Session** | Sat ~90 min | One full mock design from your framework. Rotate: queue/Kafka (Confluent), ride-matching/geo (Uber), notification system, news feed, distributed cache, multi-tenant SaaS (your Logward edge). Write each into [`../02_system_design/practiced/`](../02_system_design/practiced/). |
| **Behavioral Rehearsal** | Sat ~20 min | Pick 2 stories from [`../03_behavioral/story_bank.md`](../03_behavioral/story_bank.md), say them out loud, record once, cut to under 2.5 min. Rotate so every story gets rehearsed monthly. Amazon weeks: drill LP deep-dive follow-ups ("what would you do differently?"). |
| **Mock Interview** | Sun ~60-75 min | **From Phase 2 on, one full mock every week.** Alternate coding mock and design mock. Use [Pramp / interviewing.io](https://interviewing.io) or a peer. Treat it as the real thing: webcam on, think aloud, no pausing. Debrief in [`../00_strategy/`](../00_strategy/). |

**Plus the daily ~15-min micro-task** (weekdays): rotate behavioral story polish, one design concept note, or one [`../04_ai_fluency/`](../04_ai_fluency/) rep (code-comprehension / "how would you use an LLM here" — the new 2026 round across all targets; never actually use AI in live coding).

**Spaced repetition stays on:** every Friday session and every Sunday mock debrief, pull from the oldest "N"-pile entries first. A problem isn't "done" until you've cold-solved it from blank twice on separate days.

**Weekly weak-spot rule:** each week's Code Session 1 focus pattern = your weakest remaining pattern from the Jul 5 retro, until those are no longer weak. Then rotate evenly.

**Guardrails (priority #2 is stability/WLB):**
- Hard stop on weeknights — never let a session bleed past ~2.5 hrs. Sleep > one extra problem.
- One full rest evening per week (your pick). Sunday afternoons stay light.
- The week before any confirmed onsite: **cut volume by half**, switch to light review + sleep. Peak fresh, not fried.

---

## Quick reference — pattern files

All in [`../01_dsa/patterns/`](../01_dsa/patterns/): `arrays-hashing.md`, `two-pointers.md`, `sliding-window.md`, `stack.md`, `binary-search.md`, `linked-list.md`, `trees.md`, `tries.md`, `heap.md`, `backtracking.md`, `graphs.md`, `dynamic-programming.md` (DP gets its own dedicated rotation in the Weeks 5-12 weak-spot slots — you already have a head start from patterns 15-17 (DP / knapsack)).

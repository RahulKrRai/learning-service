# Practice Log & Spaced-Repetition Tracker
> Your single source of truth for *what you've actually done*. The [application_tracker](./application_tracker.md) tracks conversations with companies; this tracks reps with the material. **Update it the same day you solve anything — it's a 60-second habit that kills the "I feel lost" feeling.**

> **Why this exists:** "I don't know where I am" is a tracking problem, not a knowledge problem. You can't feel on-track without a visible board of what's done, what's weak, and what's due for review. Progress you can see is progress you'll continue. This turns vague guilt into three numbers you can check in 10 seconds.

---

## How to use this (read once)

1. **Every problem you solve, add one row** to the DSA log below — even an easy one, even a re-solve. Takes 60 seconds.
2. **Rate it honestly** with the traffic light: 🔴 couldn't do it / needed the solution · 🟡 solved with hints or slowly · 🟢 solved clean, would pass live.
3. **Set a Revisit date** using spaced repetition (below). Anything 🔴/🟡 comes back fast; 🟢 comes back slow.
4. **Once a week (Sunday), scan three things:** the Pattern Heatmap (where are the reds?), the Revisit queue (what's due?), and the Mistakes Log (what keeps biting me?). That scan *is* your planning session — it tells you what to do next week without you having to decide.

### Spaced-repetition schedule (when to revisit)
| Last rating | Next revisit |
|---|---|
| 🔴 couldn't do it | **+2 days** |
| 🟡 hints / slow | **+4 days**, then +1 week |
| 🟢 clean | **+1 week**, then +3 weeks, then retire |

> A problem is "owned" after **two consecutive 🟢** on separate days. Then stop revisiting it and trust it.

---

## 1. DSA Problem Log

Add newest at the top. Keep "Notes" to the one thing you'd tell yourself next time.

| Date | # / Problem | Pattern (file) | Difficulty | Rating | Time | Revisit on | Notes (the one takeaway) |
|---|---|---|---|---|---|---|---|
| | | | | 🔴🟡🟢 | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

---

## 2. Pattern Heatmap (your at-a-glance map)

Update the status after each session. This is the single most useful view — it shows the holes. Status: ⬜ not started · 🔴 shaky · 🟡 getting there · 🟢 solid. Target = enough reps to hit 🟢.

| # | Pattern | Reps done | Status | Priority for your targets |
|---|---|---|---|---|
| 01 | Two Pointers & Sliding Window | | ⬜ | Core — everyone |
| 02 | Hashing & Frequency | | ⬜ | Core — everyone |
| 03 | Binary Search (+ answer space) | | ⬜ | Core — everyone |
| 04 | Stack & Monotonic | | ⬜ | Core |
| 05 | Linked List | | ⬜ | Core |
| 06 | Trees & BST | | ⬜ | Core — everyone |
| 07 | Trie | | ⬜ | Google, autocomplete |
| 08 | Heap / Top-K / Merge-K | | ⬜ | Core — everyone |
| 09 | Graphs BFS/DFS | | ⬜ | 🔥 Core — everyone |
| 10 | Topological Sort | | ⬜ | Google, Uber |
| 11 | Union-Find | | ⬜ | Google, Uber |
| 12 | Shortest Path & MST | | ⬜ | Google, Uber |
| 13 | Backtracking | | ⬜ | Core |
| 14 | Intervals & Sweep Line | | ⬜ | 🔥 Core — everyone |
| 15 | DP 1D | | ⬜ | 🔥 Core |
| 16 | DP 2D & Grid | | ⬜ | Google, Amazon |
| 17 | Knapsack & Subset DP | | ⬜ | Amazon |
| 18 | Greedy | | ⬜ | Core |
| 19 | Bit Manipulation | | ⬜ | Occasional |
| 20 | Matrix & Grid | | ⬜ | 🔥 Google, Amazon |
| 21 | Math & Geometry | | ⬜ | Google |
| 22 | OOD / LLD (coding) | | ⬜ | 🔥 Atlassian, Amazon, Uber |
| 23 | Advanced DP | | ⬜ | Google-hard |
| 24 | Advanced Strings (KMP/RK) | | ⬜ | Google-hard |
| 25 | Range Queries (Fenwick/segtree) | | ⬜ | Google/Uber-hard |
| 26 | Divide & Conquer / Sorting | | ⬜ | Everyone |
| 27 | Concurrency & Multithreading | | ⬜ | 🔥 Uber, Atlassian |

---

## 3. System Design Log

Rate each design on whether you can **draw it from memory in 40 min** and defend the deep dives.

| Date | Design (file) | From memory? | Rating | The deep-dive I fumbled |
|---|---|---|---|---|
| | | ☐ | 🔴🟡🟢 | |
| | | ☐ | | |
| | | ☐ | | |
| | | ☐ | | |

**Priority order for your loops:** Kafka log ([06](../02_system_design/classic_designs/06_distributed_message_log_kafka.md), Confluent) → your 4 [project_designs](../02_system_design/project_designs/) (defend cold) → ride dispatch ([07](../02_system_design/classic_designs/07_ride_dispatch_matching.md), Uber) → the rest.

---

## 4. Mistakes Log (the highest-value section)

Every time you get something wrong, add a line. **Recurring lines here are your real weaknesses** — worth more than any new problem. Review before every mock and every loop.

| Date | What I got wrong | Root cause (why) | The fix / rule to remember |
|---|---|---|---|
| | e.g. off-by-one in binary search | used `<=` vs `<` wrong on shrinking window | write the invariant as a comment first |
| | | | |
| | | | |
| | | | |
| | | | |

---

## 5. Weekly Scoreboard (fill Sunday — 5 min)

Three numbers + one decision. That's the whole review.

| Week of | Problems solved | Patterns at 🟢 | Designs from-memory | Next week's #1 focus (from the reds above) |
|---|---|---|---|---|
| | | / 27 | / ~15 | |
| | | / 27 | | |
| | | / 27 | | |
| | | / 27 | | |
| | | / 27 | | |
| | | / 27 | | |

> **The only rule that matters:** did I log a rep today? If the answer is yes most days, you are on track — regardless of what the calendar plan says. Streak > schedule.

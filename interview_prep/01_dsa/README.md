# 01 — DSA Hub

Your home base for the coding-interview prep. DSA is **rusty, not weak** — so the whole point of this section is to rebuild *pattern-recall speed*, not to grind volume. You've solved most of this before; you need the "oh, this is a monotonic-stack problem" reflex back.

---

## How this section is organised

```
01_dsa/
├── README.md            ← you are here (the hub)
└── patterns/
    ├── 01_two_pointers_sliding_window.md
    ├── 02_hashing_frequency.md
    ├── ...
    ├── 19_bit_manipulation.md       ← end of the CORE 19
    └── 20–27 (advanced add-ons)     ← matrix · math · OOD/LLD · advanced DP · strings · range queries · D&C · concurrency
```

- **One file per pattern: 19 core + 8 advanced = 27 total**, under `patterns/`.
- **Naming:** `NN_<snake_case_name>.md` where `NN` is a zero-padded two-digit index (`01`–`27`). The index is just a stable ordering for the tables below — it is *not* a difficulty or study order. **01–19 are the core spine**; **20–27 are advanced / company-specific add-ons** (see the second table).
- Each pattern file follows the same internal shape: *when to reach for it → the core template (Python) → 6–10 representative problems (easy→hard, with company tags) → the 2–3 "gotcha" variants interviewers use to see if you actually understand it → recall drill.*
- Keep solutions in your own words. A pattern file is "done" when you can reproduce the template from a blank page in under 3 minutes.

---

## The core pattern checklist (01–19)

Update the **Confidence** column honestly as you go. The goal is to turn everything 🟢 by the time onsites cluster (late July / August).

- 🔴 = rusty / can't reproduce the template cold
- 🟡 = can do it with a hint or after one warm-up problem
- 🟢 = reflexive — I recognise it on sight and code the template from memory

| # | Pattern | Confidence | File |
|---|---------|:----------:|------|
| 01 | Two pointers / sliding window | 🔴 | [patterns/01_two_pointers_sliding_window.md](patterns/01_two_pointers_sliding_window.md) |
| 02 | Hashing / frequency maps | 🔴 | [patterns/02_hashing_frequency.md](patterns/02_hashing_frequency.md) |
| 03 | Binary search (on answer too) | 🔴 | [patterns/03_binary_search.md](patterns/03_binary_search.md) |
| 04 | Stack / monotonic stack | 🔴 | [patterns/04_stack_monotonic.md](patterns/04_stack_monotonic.md) |
| 05 | Linked list (fast/slow, reversal) | 🔴 | [patterns/05_linked_list.md](patterns/05_linked_list.md) |
| 06 | Trees / BST | 🔴 | [patterns/06_trees_bst.md](patterns/06_trees_bst.md) |
| 07 | Trie | 🔴 | [patterns/07_trie.md](patterns/07_trie.md) |
| 08 | Heap / top-K / merge-K | 🔴 | [patterns/08_heap_topk_mergek.md](patterns/08_heap_topk_mergek.md) |
| 09 | Graph BFS / DFS | 🔴 | [patterns/09_graph_bfs_dfs.md](patterns/09_graph_bfs_dfs.md) |
| 10 | Topological sort | 🔴 | [patterns/10_topological_sort.md](patterns/10_topological_sort.md) |
| 11 | Union-find (DSU) | 🔴 | [patterns/11_union_find.md](patterns/11_union_find.md) |
| 12 | Shortest path (Dijkstra/Bellman-Ford) | 🔴 | [patterns/12_shortest_path.md](patterns/12_shortest_path.md) |
| 13 | Backtracking | 🔴 | [patterns/13_backtracking.md](patterns/13_backtracking.md) |
| 14 | Intervals / sweep line | 🔴 | [patterns/14_intervals_sweep_line.md](patterns/14_intervals_sweep_line.md) |
| 15 | DP — 1D | 🔴 | [patterns/15_dp_1d.md](patterns/15_dp_1d.md) |
| 16 | DP — 2D / grid | 🔴 | [patterns/16_dp_2d_grid.md](patterns/16_dp_2d_grid.md) |
| 17 | Knapsack / subset | 🟡 | [patterns/17_knapsack_subset.md](patterns/17_knapsack_subset.md) |
| 18 | Greedy | 🔴 | [patterns/18_greedy.md](patterns/18_greedy.md) |
| 19 | Bit manipulation | 🔴 | [patterns/19_bit_manipulation.md](patterns/19_bit_manipulation.md) |

> Knapsack starts at 🟡 because you've already worked 0/1-knapsack, unbounded, and subset variants. Lean on that — re-derive it once, then promote to 🟢.

### Advanced / company-specific add-ons (20–26)

These cover the ~15% the core 19 don't fully reach. Study them **after** the core spine is mostly 🟡/🟢, and prioritise by your target loops (frequency tags below).

| # | Pattern | Frequency / who asks | Confidence | File |
|---|---------|----------------------|:----------:|------|
| 20 | Matrix & grid manipulation | 🔥 High — everyone (esp. Google/Amazon) | 🔴 | [patterns/20_matrix_grid.md](patterns/20_matrix_grid.md) |
| 21 | Math, number theory & randomized | 🔥 High — Google + bank OAs (GS/JPM) | 🔴 | [patterns/21_math_geometry.md](patterns/21_math_geometry.md) |
| 22 | Object-oriented / low-level design (coding) | 🔥 High — **Atlassian**, Amazon, Uber | 🔴 | [patterns/22_object_oriented_design.md](patterns/22_object_oriented_design.md) |
| 23 | Advanced DP (state-machine / interval / bitmask / tree) | ⚡ Google-hard | 🔴 | [patterns/23_advanced_dp.md](patterns/23_advanced_dp.md) |
| 24 | Advanced strings (KMP / Rabin-Karp) | ⚡ Google-hard, lower freq | 🔴 | [patterns/24_advanced_strings.md](patterns/24_advanced_strings.md) |
| 25 | Prefix/difference arrays & range queries (Fenwick / segment tree) | 🔸 Medium core + Google/Uber-hard | 🔴 | [patterns/25_range_queries.md](patterns/25_range_queries.md) |
| 26 | Divide & conquer, sorting & quickselect | 🔸 Medium-high — everyone | 🔴 | [patterns/26_divide_conquer_sorting.md](patterns/26_divide_conquer_sorting.md) |
| 27 | Concurrency & multithreading (locks / conditions / semaphores / deadlock) | 🔥 High — **Uber, Atlassian**; Google/Amazon | 🔴 | [patterns/27_concurrency_multithreading.md](patterns/27_concurrency_multithreading.md) |

**Where to spend first, by target:** **Atlassian** → 22 (OOD) + 27 (concurrency) are non-negotiable; also see [machine coding round](../02_system_design/machine_coding_round.md). **Google L5** → 20, 21, 23. **Banks (GS/JPM OA)** → 21, 26. **Amazon / Uber** → 20, 22, 26, 27. **Confluent** leans on systems/**concurrency** over exotic algorithms, so the core 19 + 22 + 26 + 27 cover it.

---

## Volume target: ~150–200 problems, quality of recall > count

- **Aim for ~150–200 solved**, not 500. A solved problem you can't reproduce a week later is worth zero.
- **Bias toward company-tagged MEDIUMs.** Easies are warm-ups (do a handful per pattern to recover the template); the interview signal lives in mediums. Hards only where a target company is known to ask them (Google, Uber).
- **Per pattern:** roughly 1–2 easy, 5–8 medium, 1–2 hard. That lands you around 8–10 problems × 19 core patterns ≈ 160 (plus a lighter, prioritised pass over the 20–26 add-ons).
- **The recall rule:** a problem only counts when you can, on a blank editor, re-derive the approach and code it cleanly **without looking**. Re-solve anything you needed a hint on after 3–4 days (spaced repetition). Track this in each pattern file's recall drill.
- **Use company tags** (LeetCode → problem → "Companies", free for the target list) to pull the actual asked-mediums for Google / Amazon / Uber / Confluent / Atlassian / Goldman / JPMorgan and prioritise those.

---

## The universal 6-step interview framework

Run **every** problem through these six steps, out loud. Interviewers score your *process* as much as your answer — and in a Google plain-doc or Amazon no-AI setting, narrating the process is most of the signal. Budget assumes a ~35–40 min coding slot.

| # | Step | What you actually do | Time budget |
|---|------|----------------------|:-----------:|
| 1 | **Understand** | Restate the problem in your words. Clarify input types, ranges, duplicates, empty/negative cases, what "best" means, expected output shape. Confirm constraints (n size → hints at target complexity). | 2–4 min |
| 2 | **Examples** | Walk one normal example by hand. Then write down edge cases: empty, single element, all-same, sorted/reverse, overflow, cycles. Get interviewer to confirm expected outputs. | 2–3 min |
| 3 | **Brute force** | State the obvious solution and its complexity *out loud* — even if O(n²) or exponential. Establishes a baseline and shows you can always produce *something*. Don't code it. | 2–3 min |
| 4 | **Optimize** | Name the pattern. "The repeated work is X; a hash map / monotonic stack / two pointers removes it." State the new time/space before coding. Get a nod from the interviewer. | 4–6 min |
| 5 | **Code** | Write the clean version. Talk while you type. Use real variable names, factor helpers, handle the edge cases you already listed. Don't go silent. | 12–18 min |
| 6 | **Test** | Dry-run your code on step-2 examples line by line. Hit the edge cases. Find and fix bugs *before* the interviewer points them out. State final time/space complexity. | 4–6 min |

**Rahul-specific timing note:** because the bottleneck is recall, not problem-solving, steps 1–4 are where you'll feel slow at first. Drilling the pattern files compresses 1–4 from ~12 minutes down to ~5, which is exactly the speed-up that turns a "couldn't finish" into a "finished with time to spare."

---

## Complexity cheat-sheet

### Common data structures — average-case operations

| Structure | Access | Search | Insert | Delete | Space | Notes |
|-----------|:------:|:------:|:------:|:------:|:-----:|-------|
| Array / Python `list` | O(1) | O(n) | O(n) | O(n) | O(n) | append amortised O(1); insert/delete at end O(1) |
| Dynamic array (amortised) | O(1) | O(n) | O(1)* | O(n) | O(n) | *amortised append; mid-insert is O(n) |
| Hash map / `dict`, `set` | — | O(1) | O(1) | O(1) | O(n) | worst case O(n) on collisions; unordered |
| Stack / Queue / `deque` | O(n) | O(n) | O(1) | O(1) | O(n) | push/pop/popleft/append all O(1) |
| Singly linked list | O(n) | O(n) | O(1) | O(1) | O(n) | O(1) insert/delete *given the node*; access is O(n) |
| Binary heap (`heapq`) | O(1) peek | O(n) | O(log n) | O(log n) | O(n) | min-heap by default; heapify is O(n) |
| Balanced BST | O(log n) | O(log n) | O(log n) | O(log n) | O(n) | Python has no built-in; use `sortedcontainers` |
| Trie | — | O(L) | O(L) | O(L) | O(Σ·N·L) | L = key length, Σ = alphabet size |
| Union-find (DSU) | — | ~O(α(n)) | — | — | O(n) | with path compression + union by rank; α ≈ constant |

### Sorting & search

| Algorithm | Time (avg) | Time (worst) | Space | Stable? |
|-----------|:----------:|:------------:|:-----:|:-------:|
| Binary search | O(log n) | O(log n) | O(1) | — |
| Merge sort | O(n log n) | O(n log n) | O(n) | yes |
| Quick sort | O(n log n) | O(n²) | O(log n) | no |
| Heap sort | O(n log n) | O(n log n) | O(1) | no |
| Timsort (Python `sorted`) | O(n log n) | O(n log n) | O(n) | yes |
| Counting / radix sort | O(n + k) | O(n + k) | O(n + k) | yes |

### Big-O sanity ladder (rough "will it pass" by input size n)

| n up to | Acceptable complexity |
|---------|-----------------------|
| ~10–12 | O(n!) / O(2ⁿ) (backtracking, permutations) |
| ~20–25 | O(2ⁿ) with memo |
| ~500 | O(n³) |
| ~5,000 | O(n²) |
| ~10⁶ | O(n log n) |
| ~10⁷–10⁸ | O(n) / O(log n) |

---

## Resources

Every topic below has a **free** option first. Paid tools are accelerators, not requirements.

### Free
- **NeetCode 150** — the spine of this prep. Roadmap: <https://neetcode.io/roadmap> · Practice list: <https://neetcode.io/practice> · Each problem page (e.g. <https://neetcode.io/problems/two-sum>) has a free video walkthrough.
- **Blind 75** — the leaner core list if time is tight; covered inside the NeetCode roadmap.
- **LeetCode company tags** — free for the target list. Open a problem → "Companies" tab to see who asks it. Pull the asked-mediums for Google / Amazon / Uber / Confluent / Atlassian / GS / JPM.
- **YouTube channels** (search-link, pick your favourite explainer): NeetCode, takeUforward/striver, Abdul Bari, Tushar Roy, Back To Back SWE. e.g. <https://www.youtube.com/results?search_query=neetcode+sliding+window>
- **LeetCode problems themselves** are free to read and solve: <https://leetcode.com/problemset/>

### Paid (optional accelerators)
- **AlgoMonster** — <https://algo.monster> — fast pattern-first refresher; good fit for "rusty not weak" because it's organised by pattern, exactly like this section.
- **Grokking the Coding Interview (DesignGurus)** — <https://www.designgurus.io> — the canonical pattern-based course; the 19 patterns here map closely to it.
- **LeetCode Premium** — <https://leetcode.com/subscribe/> — unlocks full company-tag frequency/recency data and Premium-only problems.

---

## Suggested flow

1. Pick a 🔴 pattern. Read its file's template; reproduce it on a blank page until clean.
2. Do the easy warm-up(s), then the mediums, narrating all 6 steps.
3. Promote the pattern's confidence only when you can code the template cold.
4. Re-solve any hinted problem 3–4 days later (spaced repetition).
5. Once a cluster of patterns is 🟢, do **mixed sets** (random problem, unknown pattern) — that's the real interview condition and the truest test of recall speed.

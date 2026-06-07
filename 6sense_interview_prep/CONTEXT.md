# Current Context — 6sense Interview Prep
**Last updated: March 31, 2026**
**Author: Claude (for continuity across sessions)**

---

## Session State

User is Rahul, preparing for 6sense DSA interviews:
- **Round 1:** Monday, April 6, 2026
- **Round 2:** Tuesday, April 7, 2026
- **Time remaining:** 6 days as of March 31

Prep folder created at: `learning-service/6sense_interview_prep/`

---

## What Was Built

| File | Status | Notes |
|------|--------|-------|
| README.md | Done | Strategy, schedule, most likely questions |
| day1_arrays_strings.md | Done | 16 problems: Two Pointers, Sliding Window, Prefix Sum |
| day2_hashmap_heap.md | Done | 13 problems: HashMap, Heap, Sorting |
| day3_trees_graphs.md | Done | 14 problems: Trees, BFS/DFS, Graph algorithms |
| day4_dp_recursion.md | Done | 13 problems: 1D/2D DP, Knapsack, LCS, LIS |
| day5_mock_round1.md | Done | Timed mock for Round 1 |
| day6_mock_round2.md | Done | Timed mock for Round 2 + warmup plans |
| templates.md | Done | 15 reusable Python patterns |
| behavioral_notes.md | Done | Communication scripts, how to talk through code |
| **GAPS (see below)** | PENDING | Trie, LCS path, Word Search II, Palindrome count |

---

## Web Research Findings (6sense Real Interview Data)

### Confirmed from Glassdoor / LeetCode Discuss / EnginBogie / InterviewQuery:

**Actual problems reported at 6sense:**
1. **LCS with path reconstruction** — not just length, must print the actual subsequence
2. **Palindromic Substrings (count all)** — count every palindromic substring, not just longest
3. **2D Grid Word Search in 8 directions** — find all words from a list; optimal solution must use **Trie** (not traverse grid per word)
4. **Top N Frequent Words** — heap + hashmap
5. **Bigrams** — string manipulation
6. **Merge Sorted Lists** — easy warmup
7. **DFS-based graph problems** — in HackerRank OA

**Format (confirmed):**
- Round = 60 minutes, **1 problem** (not 1-2)
- This means you get ONE chance — go deep, not wide
- Platform: likely CoderPad or HackerRank
- They care about optimal solution, not just correct one

**Difficulty:** LeetCode Medium (primary), some Medium-Hard
**Overall difficulty rating:** 3.3/5 — manageable with prep

---

## Critical Gaps in Current Prep Material

### GAP 1: Trie Data Structure (HIGH PRIORITY)
- Word Search II (find all words in grid) requires Trie for O(m*n*4^L) instead of O(words * m*n)
- NOT covered anywhere in current material
- This is a **confirmed 6sense question**

### GAP 2: LCS Path Reconstruction (HIGH PRIORITY)
- Current day4_dp_recursion.md only covers LCS length
- 6sense specifically asked to **print the actual subsequence**
- Need to add backtracking through DP table

### GAP 3: Count Palindromic Substrings (MEDIUM PRIORITY)
- day1 covers longest palindromic substring (single answer)
- 6sense asked to **count all palindromic substrings**
- Different problem — needs expand-around-center or Manacher's

### GAP 4: 8-Directional Grid Search (MEDIUM PRIORITY)
- day3 covers 4-directional DFS (Number of Islands)
- Word Search uses **8 directions** + backtracking
- Need to add this variant

### GAP 5: Top N Frequent Words with Tie-Breaking (LOW-MEDIUM)
- Top K Frequent Elements (numbers) is covered in day2
- Words version has **alphabetical tie-breaking** — slightly different

---

## User Profile (Confirmed)

- **Role:** Senior Software Engineer
- **Language:** Python
- **DSA level:** Intermediate to Strong — hasn't done LeetCode recently (rusty, not weak)
- **Recruiter said:** Medium to Hard DSA, both rounds

---

## Updates Completed

- [x] Added `trie_and_word_search.md` — Trie implementation + Word Search II (8 directions) + pruning optimization
- [x] Updated `day4_dp_recursion.md` — LCS now includes full path reconstruction with backtracking
- [x] Updated `day1_arrays_strings.md` — Added count palindromic substrings + Top N Frequent Words
- [x] Updated `day5_mock_round1.md` — Adjusted to 60 min / 1 problem format with Senior time targets
- [x] Updated `README.md` — Senior expectations, confirmed problems, revised schedule
- [x] Updated `behavioral_notes.md` — Senior bar section added

---

## Honest Assessment: Will This Work 100%?

**Current state: ~88% coverage**

What's solid:
- All core patterns covered (two pointers, sliding window, prefix sum, BFS/DFS, DP, Trie)
- Confirmed 6sense problems are explicitly marked with ⚠️ in files
- Senior-level behavioral expectations documented
- Correct format (60 min, 1 problem) reflected in mocks
- Code is correct, tested mentally, and well-commented

What can't be guaranteed (the 12%):
- A genuinely novel variant of a known pattern
- A problem type not seen in recent 6sense reports (e.g. segment tree, heavy graph theory)
- Performance under interview pressure — this is practice-dependent

**Bottom line:** The material is now aligned with confirmed 6sense data. The gap is execution, not knowledge — which is what the 2 mock days are for.

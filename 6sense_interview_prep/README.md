# 6sense DSA Interview Prep
**Round 1: Monday April 6, 2026 | Round 2: Tuesday April 7, 2026**

---

## What's in This Folder

| File | Content |
|------|---------|
| `README.md` | This file — strategy, schedule, and topic guide |
| `day1_arrays_strings.md` | Arrays, Strings, Two Pointers, Sliding Window |
| `day2_hashmap_heap.md` | HashMaps, Sets, Heaps, Top-K problems |
| `day3_trees_graphs.md` | Binary Trees, BFS/DFS, Graphs |
| `day4_dp_recursion.md` | Dynamic Programming + Recursion patterns |
| `day5_mock_and_review.md` | Mock problems + Round 1 prep |
| `day6_mock_and_review.md` | Mock problems + Round 2 prep |
| `templates.md` | Reusable Python templates for common patterns |
| `behavioral_notes.md` | Quick notes on how to talk through code in interviews |

---

## 6sense Interview Profile (Verified from Real Interviews)

6sense is a B2B revenue AI platform (Series E, ~$5B valuation).

**Confirmed format (from Glassdoor / LeetCode Discuss):**
- Each round = **60 minutes, 1 problem** (not 1-2)
- Difficulty: **Medium to Hard** (recruiter confirmed)
- Platform: CoderPad or HackerRank

**For Senior SWE specifically, they expect:**
1. You discard brute force quickly — don't dwell on it
2. You reach the **optimal solution**, not just a correct one
3. You can discuss trade-offs between approaches unprompted
4. Clean, production-quality code on first attempt
5. Strong complexity analysis — you should know *why* it's O(n log n), not just state it

**Confirmed actual problems asked (from real interviews):**
- LCS with path reconstruction (print the actual subsequence)
- Count all palindromic substrings
- 2D Grid Word Search in 8 directions using Trie
- Top N Frequent Words with alphabetical tie-breaking
- DFS graph problems (HackerRank OA)

---

## 6-Day Schedule (March 31 – April 5)

> **Senior-specific note:** Since you're rusty, Day 1 is a warm-up day. Go fast — you'll recognise most of it. Days 2–4 are where to invest heavily.

| Day | Date | Focus | Priority File |
|-----|------|-------|--------------|
| Day 1 | Tue Mar 31 | **Rust removal** — Arrays, Two Pointers, Sliding Window, Strings | `day1_arrays_strings.md` |
| Day 2 | Wed Apr 1 | HashMap + Heap + **Trie** (confirmed 6sense topic) | `day2_hashmap_heap.md` + `trie_and_word_search.md` |
| Day 3 | Thu Apr 2 | Trees + BFS/DFS + Graphs | `day3_trees_graphs.md` |
| Day 4 | Fri Apr 3 | **DP deep dive** — LCS path, Palindromes, Knapsack variants | `day4_dp_recursion.md` |
| Day 5 | Sat Apr 4 | **Timed mock Round 1** (60 min, 1 medium-hard problem) | `day5_mock_round1.md` |
| Day 6 | Sun Apr 5 | **Timed mock Round 2** (60 min, 1 medium-hard problem) + review | `day6_mock_round2.md` |

**Daily time commitment: 3–4 hours**

**Most important files given confirmed problems:** `trie_and_word_search.md` and `day4_dp_recursion.md` (LCS section)

---

## Most Likely Questions by Round

### Round 1 — High Probability

| Problem | Pattern | Difficulty |
|---------|---------|-----------|
| Two Sum / Three Sum | HashMap | Easy–Medium |
| Longest Substring Without Repeating Characters | Sliding Window | Medium |
| Valid Anagram / Group Anagrams | HashMap | Easy–Medium |
| Container With Most Water | Two Pointers | Medium |
| Product of Array Except Self | Prefix Product | Medium |
| Merge Intervals | Sorting + Sweep | Medium |
| Best Time to Buy/Sell Stock | Greedy / DP | Easy |
| Move Zeroes / Rotate Array | In-place Array | Easy |
| Subarray Sum Equals K | Prefix Sum + HashMap | Medium |
| Find All Duplicates in Array | Cycle / Index trick | Medium |

### Round 2 — High Probability

| Problem | Pattern | Difficulty |
|---------|---------|-----------|
| Binary Tree Level Order Traversal | BFS | Medium |
| Lowest Common Ancestor | DFS / Recursion | Medium |
| Validate Binary Search Tree | DFS + bounds | Medium |
| Number of Islands | BFS/DFS on Grid | Medium |
| Course Schedule (Cycle in DAG) | Topological Sort | Medium |
| Word Break | DP / BFS | Medium |
| Coin Change | DP (Unbounded Knapsack) | Medium |
| Top K Frequent Elements | Heap + HashMap | Medium |
| Serialize / Deserialize Binary Tree | DFS + String | Hard |
| Clone Graph | BFS + HashMap | Medium |

---

## Complexity Cheat Sheet

| Structure | Access | Search | Insert | Delete |
|-----------|--------|--------|--------|--------|
| Array | O(1) | O(n) | O(n) | O(n) |
| HashMap | O(1) avg | O(1) avg | O(1) avg | O(1) avg |
| BST | O(log n) | O(log n) | O(log n) | O(log n) |
| Heap | O(1) top | O(n) | O(log n) | O(log n) |
| Graph BFS/DFS | — | O(V+E) | — | — |

---

## How to Approach a Problem in the Interview

```
1. UNDERSTAND (2 min)
   - Repeat the problem back in your own words
   - Ask: input size? sorted? duplicates allowed? what to return?

2. EXAMPLES (2 min)
   - Walk through 1–2 examples including edge cases (empty, single element, all same)

3. BRUTE FORCE (1 min)
   - Say it out loud, state the complexity — don't code it

4. OPTIMIZE (3–5 min)
   - Think: what's repeated work? → HashMap/cache
   - Think: sorted input? → Binary Search / Two Pointers
   - Think: subarray/substring? → Sliding Window / Prefix Sum
   - Think: tree/graph traversal? → BFS for level, DFS for path

5. CODE (15–20 min)
   - Write clean, readable code
   - Use helper variables with clear names

6. TEST (5 min)
   - Trace through your example
   - Check edge cases
   - State time and space complexity
```

---

## Key Patterns Reference

### Two Pointers
Used when: sorted array, find pair/triplet, palindrome, merge
```python
left, right = 0, len(arr) - 1
while left < right:
    if condition: left += 1
    else: right -= 1
```

### Sliding Window
Used when: subarray/substring with constraint
```python
left = 0
window = {}
for right in range(len(s)):
    # expand window: add s[right]
    while invalid_condition:
        # shrink window: remove s[left]
        left += 1
    # update answer
```

### Prefix Sum
Used when: subarray sum queries
```python
prefix = [0] * (len(arr) + 1)
for i, v in enumerate(arr):
    prefix[i+1] = prefix[i] + v
# sum from l to r = prefix[r+1] - prefix[l]
```

### BFS (Tree Level Order / Graph)
```python
from collections import deque
queue = deque([root])
while queue:
    node = queue.popleft()
    for child in node.children:
        queue.append(child)
```

### DFS (Tree / Graph)
```python
visited = set()
def dfs(node):
    if node in visited: return
    visited.add(node)
    for neighbor in graph[node]:
        dfs(neighbor)
```

### Top-K with Heap
```python
import heapq
heap = []
for num in nums:
    heapq.heappush(heap, num)
    if len(heap) > k:
        heapq.heappop(heap)
# heap now contains top K largest
```

---

## What NOT to Do

- Don't jump into coding without discussing approach
- Don't go silent — narrate your thinking even if stuck
- Don't optimize prematurely — mention brute force first
- Don't forget edge cases: empty input, single element, all negatives, duplicates
- Don't use complex variable names (`x`, `tmp`) — use `left`, `right`, `freq`, `seen`

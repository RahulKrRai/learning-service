# 18 - Greedy
> When at every step a locally optimal choice provably leads to a global optimum, so you sweep once and never look back.

## When to use it (recognition triggers)
- The problem asks for an optimal value (max/min count, max reach, can-you-do-it yes/no) and you suspect you don't need to explore all combinations.
- You can make a decision based only on what you've seen so far, never needing to revise it (no backtracking).
- There's an obvious "best next move" — take the largest, the earliest-finishing, the closest reachable — and intuition says doing that repeatedly works.
- Phrases like "maximum reach", "minimum number of jumps/intervals", "can you complete the circuit", "partition so that...".
- A DP solution exists but is O(n²)/O(2ⁿ) and you sense an O(n) one-pass exists.
- Each element belongs to exactly one group/range and you only care about boundaries (last occurrence, running max).

## Mental model
- Greedy commits to the choice that looks best *right now* and proves (via an exchange argument) that this choice is never worse than any alternative. The whole algorithm is usually one linear scan maintaining a couple of running aggregates: a running max, a current reach, a balance counter, or a frequency map.
- The hard part is never the code — it's *proving* the greedy choice is safe. If you can argue "any optimal solution can be transformed into one that makes my greedy choice without getting worse," greedy is correct.
- Contrast with DP: DP keeps *all* sub-results because it can't tell which choice is best until later; greedy throws away alternatives immediately because it *can* tell. When in doubt, a greedy that fails a small counterexample means you actually need DP.
- Many greedy problems reduce to tracking an "envelope": the farthest you can reach, the running balance of `(` vs `)`, the rightmost index a label appears. You extend the envelope and react when you hit its edge.

## Reusable template(s)
```python
# Template A: one-pass running aggregate (Kadane / max-reach style)
def greedy_scan(nums):
    best = running = nums[0]          # seed with first element
    for x in nums[1:]:
        running = max(x, running + x) # local optimal: extend or restart
        best = max(best, running)     # global answer tracks the best local
    return best

# Template B: reach / interval-edge sweep (Jump Game, Partition Labels)
def reach_sweep(nums):
    farthest = 0
    for i, gain in enumerate(nums):
        if i > farthest:              # current position unreachable -> fail
            return False
        farthest = max(farthest, i + gain)
    return True

# Template C: greedy with a sorted structure / frequency map (Hand of Straights)
from collections import Counter
def consume_in_order(items, group):
    cnt = Counter(items)
    for start in sorted(cnt):         # always start a group at the smallest leftover
        c = cnt[start]
        if c > 0:
            for k in range(start, start + group):
                if cnt[k] < c: return False
                cnt[k] -= c
    return True
```

## Complexity profile
- Typical: **O(n)** time (single scan) or **O(n log n)** when a sort/heap is needed, **O(1)–O(n)** space. You're usually beating an O(n²) DP, O(2ⁿ) brute-force enumeration, or O(n·k) BFS.

## Curated problems (easy -> hard)

### 1. Maximum Subarray (Kadane)  -  Medium
- **Problem:** Given an integer array, find the contiguous subarray with the largest sum and return that sum.
- **Practice (free):** https://leetcode.com/problems/maximum-subarray/
- **Video (free):** https://neetcode.io/problems/maximum-subarray
- **Idea:** At each index decide greedily whether to extend the current subarray or start fresh — start fresh whenever the running sum has gone negative, because a negative prefix can only hurt what follows.
```python
from typing import List

def maxSubArray(nums: List[int]) -> int:
    best = running = nums[0]
    for x in nums[1:]:
        running = max(x, running + x)  # drop a negative prefix by restarting at x
        best = max(best, running)
    return best
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Seed `best` with `nums[0]`, not `0` — an all-negative array (e.g. `[-3,-1,-2]`) must return the largest single element, and seeding with 0 would wrongly return 0.
- **Follow-up:** "Return the indices of the subarray." Track a `start` pointer that you reset whenever you restart (`running == x`), and capture `(start, i)` whenever `best` updates.

### 2. Jump Game  -  Medium
- **Problem:** Each element is the max jump length from that index; starting at index 0, determine whether you can reach the last index.
- **Practice (free):** https://leetcode.com/problems/jump-game/
- **Video (free):** https://neetcode.io/problems/jump-game
- **Idea:** Sweep left to right tracking the farthest index reachable so far; if you ever stand on an index beyond that reach, you're stuck.
```python
from typing import List

def canJump(nums: List[int]) -> bool:
    farthest = 0
    for i, gain in enumerate(nums):
        if i > farthest:               # this index was never reachable
            return False
        farthest = max(farthest, i + gain)
    return True
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** You don't need to know *how* you reached an index, only *that* you could; a single running `farthest` captures it. An equivalent backward greedy shrinks a "goal" pointer toward 0.
- **Follow-up:** "What if jumps could be backward too?" Reachability becomes a graph/BFS problem; the simple monotone greedy no longer holds.

### 3. Jump Game II  -  Medium
- **Problem:** Same setup as Jump Game, but you're guaranteed you can reach the end — return the *minimum* number of jumps.
- **Practice (free):** https://leetcode.com/problems/jump-game-ii/
- **Video (free):** https://neetcode.io/problems/jump-game-ii
- **Idea:** Greedy BFS by levels: treat the current jump's reachable range as one "level"; when you reach its right edge, you must spend a jump and the new edge becomes the farthest seen within the old level.
```python
from typing import List

def jump(nums: List[int]) -> int:
    jumps = 0
    cur_end = 0        # right edge of the range reachable with `jumps` jumps
    farthest = 0       # farthest reachable with one more jump
    for i in range(len(nums) - 1):     # no need to jump from the last index
        farthest = max(farthest, i + nums[i])
        if i == cur_end:               # consumed current level -> jump
            jumps += 1
            cur_end = farthest
    return jumps
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Loop to `len(nums) - 1`, not the end — otherwise you'd count one extra jump when `i` lands exactly on the last index. The greedy works because within a level you delay committing the jump until forced, always picking the stride that maximizes the next reach.
- **Follow-up:** "Reconstruct the actual indices jumped to." At each level boundary, record the index in `[prev_end+1, cur_end]` that produced `farthest`.

### 4. Gas Station  -  Medium
- **Problem:** Around a circular route, `gas[i]` is fuel at station i and `cost[i]` is fuel to reach the next; find the starting index from which you can complete the loop, or -1.
- **Practice (free):** https://leetcode.com/problems/gas-station/
- **Video (free):** https://neetcode.io/problems/gas-station
- **Idea:** If total gas ≥ total cost a unique answer exists. Track a running tank from a candidate start; the moment it goes negative, no station in that span can be the start, so reset the candidate to the next station.
```python
from typing import List

def canCompleteCircuit(gas: List[int], cost: List[int]) -> int:
    if sum(gas) < sum(cost):
        return -1                      # globally impossible
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                   # can't reach i+1 from current start
            start = i + 1              # every station up to i is also disqualified
            tank = 0
    return start
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** The exchange argument: if you run dry going from `start` to `i`, then *any* station between them also fails (each had a non-negative prefix into the failing stretch), so you can safely skip the whole range and resume at `i+1`. The global `sum` check guarantees the surviving candidate works.
- **Follow-up:** "Return all valid starts." Only possible when total gas == total cost and the tank never dips below zero anywhere; otherwise the start is unique.

### 5. Hand of Straights  -  Medium
- **Problem:** Given a multiset of card values and a group size, decide whether the hand can be rearranged into groups of `groupSize` consecutive values.
- **Practice (free):** https://leetcode.com/problems/hand-of-straights/
- **Video (free):** https://neetcode.io/problems/hand-of-straights
- **Idea:** The smallest remaining card *must* be the start of some group, so greedily form a consecutive run of length `groupSize` from it, decrementing counts; if any needed value is missing, fail.
```python
from typing import List
from collections import Counter

def isNStraightHand(hand: List[int], groupSize: int) -> bool:
    if len(hand) % groupSize != 0:
        return False
    cnt = Counter(hand)
    for start in sorted(cnt):          # smallest leftover card forces a group start
        need = cnt[start]
        if need > 0:
            for v in range(start, start + groupSize):
                if cnt[v] < need:
                    return False       # not enough cards to extend the run
                cnt[v] -= need
    return True
```
- **Complexity:** Time O(n log n), Space O(n)
- **Key insight / gotcha:** Forming groups from the smallest value outward is forced — nothing smaller can ever join later, so the smallest must anchor a group now. Decrement by `need` (its full count) at once instead of one card at a time to keep it efficient. (Identical to LeetCode 1296 "Divide Array in Sets of K Consecutive Numbers".)
- **Follow-up:** "Use a heap instead of a sorted dict." A min-heap of distinct values supports streaming input and lazy deletion of zeroed counts.

### 6. Partition Labels  -  Medium
- **Problem:** Partition a string into as many parts as possible so that each letter appears in at most one part; return the sizes of the parts.
- **Practice (free):** https://leetcode.com/problems/partition-labels/
- **Video (free):** https://neetcode.io/problems/partition-labels
- **Idea:** Precompute each character's last index. Sweep, extending the current partition's right edge to the max last-index of any char seen; close the partition when the scan pointer reaches that edge.
```python
from typing import List

def partitionLabels(s: str) -> List[int]:
    last = {c: i for i, c in enumerate(s)}   # last occurrence of each char
    result = []
    start = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])              # partition must include this char's tail
        if i == end:                         # no pending char reaches beyond i
            result.append(i - start + 1)
            start = i + 1
    return result
```
- **Complexity:** Time O(n), Space O(1) (the map holds at most 26 entries)
- **Key insight / gotcha:** This is an interval-merge in disguise: each char defines an interval `[first, last]`; a partition closes only when the scan index equals the running max of all `last` indices seen so far. Greedy gives the *maximum* number of partitions automatically.
- **Follow-up:** "Return the actual substrings, not sizes." Slice `s[start:i+1]` at each close instead of appending the length.

### 7. Merge Triplets to Form Target Triplet  -  Medium
- **Problem:** Given triplets and a target triplet, you may repeatedly replace two triplets with their element-wise max; decide whether `target` is obtainable.
- **Practice (free):** https://leetcode.com/problems/merge-triplets-to-form-target-triplet/
- **Video (free):** https://neetcode.io/problems/merge-triplets-to-form-target-triplet
- **Idea:** Only triplets that never exceed the target in *any* position are usable (one over-large value would poison the running max). Among usable triplets, check that each target position is hit exactly by at least one of them.
```python
from typing import List

def mergeTriplets(triplets: List[List[int]], target: List[int]) -> bool:
    matched = set()
    for a, b, c in triplets:
        if a <= target[0] and b <= target[1] and c <= target[2]:  # safe to merge
            for idx, val in enumerate((a, b, c)):
                if val == target[idx]:
                    matched.add(idx)        # this triplet supplies that coordinate
    return len(matched) == 3
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Filtering out any triplet with a value strictly greater than the target in some coordinate is the crux — merging is element-wise max, so a single overshoot can never be undone. Once filtered, merging *all* survivors is harmless, so you just need each coordinate matched exactly once.
- **Follow-up:** "What if the op were element-wise min?" The whole logic inverts — keep triplets that never go *below* target and check each coordinate is reachable from above.

### 8. Valid Parenthesis String  -  Medium
- **Problem:** A string of `(`, `)`, and `*` (where `*` is `(`, `)`, or empty) is valid if parentheses balance; decide validity.
- **Practice (free):** https://leetcode.com/problems/valid-parenthesis-string/
- **Video (free):** https://neetcode.io/problems/valid-parenthesis-string
- **Idea:** Track the *range* `[low, high]` of possible open-paren counts. `(` bumps both; `)` drops both; `*` widens the range (`low-1, high+1`). Clamp `low` at 0; if `high` ever goes negative there are too many `)`. Valid iff `low` can reach 0 at the end.
```python
def checkValidString(s: str) -> bool:
    low = high = 0          # min / max possible number of unmatched '('
    for ch in s:
        if ch == '(':
            low += 1; high += 1
        elif ch == ')':
            low -= 1; high -= 1
        else:               # '*' could be '(', ')', or empty
            low -= 1; high += 1
        if high < 0:        # even treating every '*' as '(' can't cover the ')'
            return False
        low = max(low, 0)   # extra ')'/'*' just stay as empty, never go below 0
    return low == 0         # some assignment of '*' balances everything
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** You don't decide what each `*` is — you carry the *interval* of feasible open counts and prune greedily. Clamping `low` at 0 matters: a `)` or `*` with no open paren to match is simply treated as empty, not a negative balance. The two-stack/DP solutions are O(n²); this interval trick is the O(1)-space optimum.
- **Follow-up:** "Solve with a single forward pass *and* prove correctness." The forward `high` check rejects excess `)`; a symmetric reasoning on `low` (it can always be pushed down to 0 by `*` as empty) handles excess `(`, so `low == 0` at the end is both necessary and sufficient.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the template from memory (Kadane / reach-sweep / freq-map)
- [ ] I can state an exchange-argument proof for at least Gas Station and Jump Game II
- [ ] Maximum Subarray (Kadane) — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Jump Game — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Jump Game II — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Gas Station — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Hand of Straights — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Partition Labels — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Merge Triplets to Form Target Triplet — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Valid Parenthesis String — 🔴 rusty / 🟡 ok / 🟢 fast

## Resources
- **Free:** NeetCode Greedy roadmap section — https://neetcode.io/roadmap (the "Greedy" group lists exactly these problems with free videos). LeetCode tag/study list — https://leetcode.com/tag/greedy/ . takeUforward/Striver greedy playlist via search — https://www.youtube.com/results?search_query=striver+greedy+algorithm+playlist .
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" greedy module — https://www.designgurus.io (free alternative: the NeetCode roadmap above covers the same patterns with videos). AlgoMonster greedy track — https://algo.monster (free alternative: LeetCode greedy tag list above).

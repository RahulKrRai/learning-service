# 03 - Binary Search (incl. on answer space)

> One-line: when your data is sorted (or the *answer* lives in a monotonic range), halve the search space each step instead of scanning it.

## When to use it (recognition triggers)
- The input array is **sorted**, or you can sort it cheaply, and you need to find a value / boundary / insertion point.
- The array is **rotated sorted** or has a single "peak/valley" — one half is always still sorted.
- You need an answer in `O(log n)` where a linear scan would be `O(n)`, or you must beat an obvious `O(n)`/`O(n log n)`.
- "**Minimum/maximum X such that** condition(X) holds" — the condition flips from False→True exactly once over a numeric range (monotonic predicate). This is *binary search on the answer space*.
- You're choosing a **rate / capacity / size / time** (speed, weight, days, length) and a `check(candidate)` is feasible-or-not and monotone.
- Two sorted arrays and you need a **k-th / median** element fast.

## Mental model
- Maintain a half-open or closed interval `[lo, hi]` that is *guaranteed to contain the answer*; each step discards the half that cannot.
- The whole game is the **loop invariant + how you shrink**. Pick one convention and never mix: I use `lo <= hi` with `mid = lo + (hi-lo)//2` and move `lo = mid+1` / `hi = mid-1`. For boundary ("leftmost true") searches I use `lo < hi`, `hi = mid` / `lo = mid+1`, answer = `lo`.
- "Binary search on the answer" reframes an optimization into a decision problem: define `feasible(x)` that is monotone (once true, stays true), then find the boundary. The array you search is the *conceptual range of answers*, not the input.
- `mid = lo + (hi-lo)//2` avoids overflow (irrelevant in Python but a habit interviewers like) and biases toward `lo`; use `hi - (hi-lo)//2` to bias toward `hi` when you set `lo = mid` to avoid infinite loops.
- Off-by-one bugs come from inconsistent interval semantics. Decide up front whether `hi` is inclusive (`len-1`) or exclusive (`len`) and keep the comparisons matching.

## Reusable template(s)
```python
# 1) Classic exact-match binary search (closed interval, hi inclusive)
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:                  # interval [lo, hi] is non-empty
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1             # answer is strictly right
        else:
            hi = mid - 1             # answer is strictly left
    return -1                        # not found; lo == insertion point

# 2) Leftmost-true boundary (find smallest x in [lo, hi] with pred(x) True)
def lower_bound(lo, hi, pred):
    # REQUIRES: pred is monotone False...False True...True over [lo, hi]
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if pred(mid):
            hi = mid                 # mid might be the answer, keep it
        else:
            lo = mid + 1             # mid is too small, discard it
    return lo                        # first index/value where pred is True

# 3) Binary search on the answer space (minimize x s.t. feasible(x))
def min_feasible(low, high, feasible):
    while low < high:
        mid = low + (high - low) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1
    return low
```

## Complexity profile
- Time `O(log n)` for a search over `n` elements; for answer-space search it's `O(log(range) * cost_of_check)` where `cost_of_check` is often `O(n)` → `O(n log(range))`.
- Space `O(1)` iterative (preferred). Recursive is `O(log n)` stack.
- You're beating a linear `O(n)` scan, or an `O(n)` / `O(n^2)` brute force over candidate answers.

## Curated problems (easy -> hard)

### 1. Binary Search  -  Easy
- **Problem:** Given a sorted ascending array of distinct ints and a target, return its index, or -1 if absent, in `O(log n)`.
- **Practice (free):** https://leetcode.com/problems/binary-search/
- **Video (free):** https://neetcode.io/problems/binary-search
- **Idea:** Textbook closed-interval search; maintain `[lo, hi]`, compare to `mid`, discard the impossible half.
```python
from typing import List

def search(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```
- **Complexity:** Time O(log n), Space O(1)
- **Key insight / gotcha:** Use `lo <= hi` (not `<`) so the single-element interval is actually checked; and `mid +/- 1` so you never re-test `mid`.
- **Follow-up:** "What if duplicates exist and you want the first occurrence?" → switch to the `lower_bound` template with `pred = nums[mid] >= target`.

### 2. Search Insert Position  -  Easy
- **Problem:** In a sorted array of distinct ints, return the index of `target`, or the index where it should be inserted to keep it sorted.
- **Practice (free):** https://leetcode.com/problems/search-insert-position/
- **Video (free):** https://neetcode.io/problems/search-insert-position
- **Idea:** This is exactly `lower_bound`: the first index whose value is `>= target`. After a failed exact search, `lo` already holds that index.
```python
from typing import List

def searchInsert(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums)            # hi exclusive: insertion can be at len
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1             # target must go to the right
        else:
            hi = mid                 # mid is a candidate insertion point
    return lo
```
- **Complexity:** Time O(log n), Space O(1)
- **Key insight / gotcha:** Use the half-open interval `[0, len]` so an insertion past the end (`return len`) falls out naturally; `hi = mid` (not `mid-1`) keeps the candidate.
- **Follow-up:** "Return the last position it could be inserted (upper bound)?" → use `pred = nums[mid] <= target` and the same boundary loop.

### 3. Find Minimum in Rotated Sorted Array  -  Medium
- **Problem:** A sorted ascending array of distinct ints was rotated at an unknown pivot; return the minimum element in `O(log n)`.
- **Practice (free):** https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/
- **Video (free):** https://neetcode.io/problems/find-minimum-in-rotated-sorted-array
- **Idea:** Compare `nums[mid]` to `nums[hi]`. If `nums[mid] > nums[hi]`, the min is strictly right of `mid`; otherwise it's at `mid` or left. The minimum is the rotation point.
```python
from typing import List

def findMin(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1             # min is in the right (unsorted) half
        else:
            hi = mid                 # min is mid or to its left
    return nums[lo]
```
- **Complexity:** Time O(log n), Space O(1)
- **Key insight / gotcha:** Compare against `nums[hi]`, not `nums[lo]`. Comparing to `lo` fails on a fully non-rotated array because `nums[mid] > nums[lo]` is true even when the min is at index 0.
- **Follow-up:** "With duplicates (LC 154)?" → when `nums[mid] == nums[hi]` you can't tell which half; safely shrink with `hi -= 1`. Worst case degrades to O(n).

### 4. Search in Rotated Sorted Array  -  Medium
- **Problem:** Search a target in a rotated sorted array of distinct ints; return its index or -1, in `O(log n)`.
- **Practice (free):** https://leetcode.com/problems/search-in-rotated-sorted-array/
- **Video (free):** https://neetcode.io/problems/search-in-rotated-sorted-array
- **Idea:** At each `mid`, exactly one side `[lo,mid]` or `[mid,hi]` is sorted. Detect which, then check whether `target` lies inside that sorted side; recurse into the appropriate half.
```python
from typing import List

def search(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:            # left half [lo, mid] is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                # right half [mid, hi] is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```
- **Complexity:** Time O(log n), Space O(1)
- **Key insight / gotcha:** Use `nums[lo] <= nums[mid]` (with `<=`) to decide the sorted half — equality matters when `lo == mid`. Then use *closed* bounds in the membership test that match the sorted side (`<=` on the endpoint that's the array element, `<` toward `mid`).
- **Follow-up:** "Allow duplicates (LC 81)?" → when `nums[lo] == nums[mid] == nums[hi]` you can't pick a half, so do `lo += 1; hi -= 1`; worst case O(n).

### 5. Search a 2D Matrix  -  Medium
- **Problem:** In an `m x n` matrix where each row is sorted and each row's first element exceeds the previous row's last, determine whether `target` exists, in `O(log(m*n))`.
- **Practice (free):** https://leetcode.com/problems/search-a-2d-matrix/
- **Video (free):** https://neetcode.io/problems/search-a-2d-matrix
- **Idea:** The matrix read row-major is one fully sorted array of length `m*n`. Binary search index `i`, mapping it to `(i // n, i % n)`.
```python
from typing import List

def searchMatrix(matrix: List[List[int]], target: int) -> bool:
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        val = matrix[mid // n][mid % n]      # flatten index -> (row, col)
        if val == target:
            return True
        elif val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
```
- **Complexity:** Time O(log(m*n)), Space O(1)
- **Key insight / gotcha:** The `divmod` mapping `(mid // n, mid % n)` uses the column count `n`, not `m`. A common bug is swapping them.
- **Follow-up:** "What about LC 240 where rows AND columns are sorted but rows don't chain?" → that's *not* one sorted array; use the staircase walk from top-right (O(m+n)), not binary search.

### 6. Koko Eating Bananas  -  Medium
- **Problem:** Given piles of bananas and `h` hours, find the minimum integer eating speed `k` (bananas/hour) so Koko finishes all piles within `h` hours (a partial pile still consumes a full hour).
- **Practice (free):** https://leetcode.com/problems/koko-eating-bananas/
- **Video (free):** https://neetcode.io/problems/koko-eating-bananas
- **Idea:** Binary search on the answer `k` in `[1, max(piles)]`. `feasible(k)` = total hours `sum(ceil(p/k)) <= h` is monotone (faster speed → fewer hours). Find the leftmost feasible `k`.
```python
from typing import List
from math import ceil

def minEatingSpeed(piles: List[int], h: int) -> int:
    def hours(k: int) -> int:
        return sum(ceil(p / k) for p in piles)   # or (p + k - 1) // k

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if hours(mid) <= h:          # feasible -> try slower (smaller k)
            hi = mid
        else:
            lo = mid + 1             # too slow -> need faster
    return lo
```
- **Complexity:** Time O(n log(max(piles))), Space O(1)
- **Key insight / gotcha:** Use integer ceil `(p + k - 1) // k` to avoid float rounding error in `hours`. The predicate must be monotone — confirm "faster ⇒ never more hours" before trusting the boundary search.
- **Follow-up:** "Prove `h >= len(piles)` always has a solution." → at `k = max(piles)` each pile takes 1 hour, so `hours = len(piles) <= h` is feasible; the upper bound is valid.

### 7. Capacity To Ship Packages Within D Days  -  Medium
- **Problem:** Given package weights that must ship in given order, find the minimum ship capacity so all packages ship within `days` days (each day loads packages in sequence without exceeding capacity).
- **Practice (free):** https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/
- **Video (free):** https://neetcode.io/problems/capacity-to-ship-packages-within-d-days
- **Idea:** Binary search capacity in `[max(weights), sum(weights)]`. `feasible(cap)` greedily counts days needed; it's monotone (bigger capacity → fewer days). Return the smallest feasible capacity.
```python
from typing import List

def shipWithinDays(weights: List[int], days: int) -> int:
    def days_needed(cap: int) -> int:
        d, load = 1, 0
        for w in weights:
            if load + w > cap:       # can't fit -> start a new day
                d += 1
                load = 0
            load += w
        return d

    lo, hi = max(weights), sum(weights)   # lo: must carry heaviest pkg
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if days_needed(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
```
- **Complexity:** Time O(n log(sum - max)), Space O(1)
- **Key insight / gotcha:** Lower bound is `max(weights)` (a single package can't be split), not 1. Starting at 1 makes `feasible` infinite-loop / never terminate for the heaviest package.
- **Follow-up:** "This is the same shape as 'Split Array Largest Sum' (LC 410) — show the mapping." → identical: minimize the largest subarray sum given `k` splits; `feasible(x)` = subarrays needed with cap `x` is `<= k`.

### 8. Time Based Key-Value Store  -  Medium
- **Problem:** Implement `set(key, value, timestamp)` and `get(key, timestamp)` returning the value with the largest stored timestamp `<= timestamp` (or "" if none); timestamps for a key are strictly increasing across `set` calls.
- **Practice (free):** https://leetcode.com/problems/time-based-key-value-store/
- **Video (free):** https://neetcode.io/problems/time-based-key-value-store
- **Idea:** Per key, append `(timestamp, value)` to a list (already sorted since timestamps increase). `get` binary-searches for the rightmost timestamp `<= query` — an upper-bound search minus one.
```python
from collections import defaultdict
from typing import List, Tuple

class TimeMap:
    def __init__(self):
        self.store: dict[str, List[Tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))   # appended in sorted order

    def get(self, key: str, timestamp: int) -> str:
        arr = self.store.get(key, [])
        lo, hi = 0, len(arr)             # find first index with ts > timestamp
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if arr[mid][0] <= timestamp:
                lo = mid + 1
            else:
                hi = mid
        return arr[lo - 1][1] if lo > 0 else ""   # one left = largest ts <= q
```
- **Complexity:** Time: `set` O(1), `get` O(log n); Space O(total entries)
- **Key insight / gotcha:** The list stays sorted *for free* because timestamps are strictly increasing per key — no need to insort. `get` is upper_bound then step back one; guard `lo > 0` for "no valid timestamp."
- **Follow-up:** "What if `set` calls could arrive out of timestamp order?" → use `bisect.insort` on `set` (O(n) shift) keeping the list sorted, or buffer and sort lazily on first `get`.

### 9. Median of Two Sorted Arrays  -  Hard
- **Problem:** Given two sorted arrays of sizes `m` and `n`, return the median of the combined array in `O(log(min(m,n)))`.
- **Practice (free):** https://leetcode.com/problems/median-of-two-sorted-arrays/
- **Video (free):** https://neetcode.io/problems/median-of-two-sorted-arrays
- **Idea:** Binary search a partition of the smaller array. Choose `i` elements from `A` and `j = half - i` from `B` for the left half; adjust `i` until `maxLeftA <= minRightB` and `maxLeftB <= minRightA`. The median is read off the four boundary values.
```python
from typing import List

def findMedianSortedArrays(A: List[int], B: List[int]) -> float:
    if len(A) > len(B):                  # always binary-search the smaller
        A, B = B, A
    m, n = len(A), len(B)
    half = (m + n + 1) // 2              # size of the left partition
    lo, hi = 0, m
    INF = float('inf')
    while lo <= hi:
        i = lo + (hi - lo) // 2          # take i from A
        j = half - i                     # take j from B
        Aleft  = A[i - 1] if i > 0 else -INF
        Aright = A[i]     if i < m else  INF
        Bleft  = B[j - 1] if j > 0 else -INF
        Bright = B[j]     if j < n else  INF
        if Aleft <= Bright and Bleft <= Aright:        # correct partition
            if (m + n) % 2:                            # odd total
                return float(max(Aleft, Bleft))
            return (max(Aleft, Bleft) + min(Aright, Bright)) / 2.0
        elif Aleft > Bright:
            hi = i - 1                   # took too many from A
        else:
            lo = i + 1                   # took too few from A
    return 0.0                            # unreachable for valid input
```
- **Complexity:** Time O(log(min(m,n))), Space O(1)
- **Key insight / gotcha:** Always partition the *smaller* array so `j = half - i` stays in range. Use `+/-inf` sentinels for empty partition sides so the comparisons work without special-casing `i==0`/`i==m`. `half = (m+n+1)//2` makes the formula work for both odd and even totals.
- **Follow-up:** "Generalize to the k-th smallest of two sorted arrays?" → there's a cleaner O(log k) recursion that drops `k/2` elements from one array each step; mention you can also merge in O(m+n) if log isn't required.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (sorted input, rotated array, or "min/max X such that …")
- [ ] I can write the classic + leftmost-boundary + answer-space templates from memory
- [ ] Binary Search 🔴/🟡/🟢
- [ ] Search Insert Position 🔴/🟡/🟢
- [ ] Find Minimum in Rotated Sorted Array 🔴/🟡/🟢
- [ ] Search in Rotated Sorted Array 🔴/🟡/🟢
- [ ] Search a 2D Matrix 🔴/🟡/🟢
- [ ] Koko Eating Bananas 🔴/🟡/🟢
- [ ] Capacity To Ship Packages Within D Days 🔴/🟡/🟢
- [ ] Time Based Key-Value Store 🔴/🟡/🟢
- [ ] Median of Two Sorted Arrays 🔴/🟡/🟢

## Resources
- **Free:** NeetCode Binary Search roadmap section — https://neetcode.io/roadmap ; LeetCode Binary Search study plan — https://leetcode.com/studyplan/binary-search/ ; takeUforward "Binary Search on Answers" video — https://www.youtube.com/results?search_query=takeuforward+binary+search+on+answers
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Modified Binary Search pattern) — https://www.designgurus.io (free alternative: the NeetCode roadmap section above); AlgoMonster binary search module — https://algo.monster (free alternative: LeetCode study plan above).

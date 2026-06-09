# 26 - Divide & Conquer, Sorting & Quickselect
> One-line: when an answer falls out of *ordering* the data, or from splitting an array in half, solving each half, and combining — custom comparators, quickselect for the k-th element, and merge-sort that counts work while it merges.

> **Frequency: MEDIUM-HIGH.** Custom sorting and quickselect show up everywhere (k-th largest, top-k, "sort by rule X"). Merge-sort-for-inversions (Count Smaller After Self / Reverse Pairs) is a classic Google/Uber medium-hard — interviewers love it because the naive O(n^2) is obvious and the O(n log n) requires the insight that a merge step can *count* while it merges.

## When to use it (recognition triggers)
- You need the **k-th smallest/largest** or the **top-k** and you do *not* need them sorted — that's **Quickselect** (average O(n)), or a heap (O(n log k)); cross-ref `12_heap.md`.
- The problem is "sort by a non-trivial rule" — concatenation order, frequency then value, custom tie-breaks — reach for a **comparator** via `functools.cmp_to_key` (or a `key=` tuple when the rule is expressible as a sort key).
- You must **count pairs** (inversions, `i<j and a[i]>a[j]`, `a[i] > 2*a[j]`) — naive is O(n^2); a **merge sort** counts the qualifying pairs during the merge for O(n log n).
- The answer over a range equals "best in left half" vs "best in right half" vs "best crossing the midpoint" — a **divide & conquer recurrence** (Maximum Subarray, closest pair, etc.).
- "Two sorted arrays, find the median / k-th in O(log(m+n))" — **binary-search partition**, a D&C cousin; cross-ref `09_binary_search.md`.
- In-place rearrangement into a few buckets (0/1/2, negatives/zeros/positives) — **3-way partition** (Dutch national flag) in one O(n) pass.

## Mental model
- **Divide & conquer** = split into independent subproblems, solve recursively, **combine**. The combine step is where the real algorithm lives (merge in merge sort, the cross-sum in max-subarray, the inversion count in the merge). Recurrence `T(n)=2T(n/2)+O(n)` => O(n log n) by the Master Theorem.
- **Sorting as a primitive:** many problems collapse once data is ordered. Decide whether the rule is a **key** (map each element to a comparable surrogate, `sorted(a, key=...)`) or a true **comparator** (the relationship between two elements isn't a per-element key — e.g. "does `xy` beat `yx`"). Comparators need `functools.cmp_to_key`.
- **Quickselect** is quicksort that only recurses into the side containing the target rank. Average O(n) because the work halves each step (n + n/2 + n/4 + ... = 2n); **worst case O(n^2)** on an adversarial/sorted input with a bad pivot. **Random pivot** (or median-of-three) makes the worst case astronomically unlikely.
- **Partitioning** is the shared engine: **Lomuto** (one pointer, pivot at end — simplest to memorize) and **Hoare** (two pointers converging — fewer swaps, trickier boundaries). **3-way / Dutch flag** splits into `<pivot`, `==pivot`, `>pivot` and is the right tool when there are many duplicate keys.
- **Counting in a merge:** when the left and right halves are each sorted, every element still in the right half that you emit "early" tells you something about the lefts it jumped over (Reverse Pairs) or vice versa (Count Smaller After Self). The sorted-halves invariant is what lets you count a *block* of pairs in O(1) instead of one at a time.

## Reusable template(s)
```python
import random
from functools import cmp_to_key

# ---- Merge sort (stable, O(n log n)); returns a new sorted list ----
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    return merge(left, right)

def merge(left, right):
    res, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:        # '<=' keeps it STABLE
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:]); res.extend(right[j:])
    return res

# ---- Lomuto partition (pivot = last element) ----
def lomuto(a, lo, hi):                  # returns final index of the pivot
    pivot = a[hi]
    i = lo                              # boundary: a[lo..i-1] are < pivot
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]           # drop pivot into place
    return i

# ---- Quickselect: k-th SMALLEST (0-indexed), average O(n), random pivot ----
def quickselect(a, k):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        p = random.randint(lo, hi)               # random pivot => avoid O(n^2)
        a[p], a[hi] = a[hi], a[p]
        idx = lomuto(a, lo, hi)
        if idx == k:   return a[idx]
        if idx < k:    lo = idx + 1              # recurse RIGHT side only
        else:          hi = idx - 1              # recurse LEFT side only

# ---- 3-way partition (Dutch national flag) around a value `pivot` ----
def three_way(a, pivot):
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if   a[mid] < pivot: a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
        elif a[mid] > pivot: a[mid], a[hi] = a[hi], a[mid]; hi -= 1   # don't advance mid
        else:                mid += 1

# ---- Custom comparator: return <0 if x before y, >0 if after, 0 if equal ----
def sort_with_comparator(items):
    def cmp(x, y):
        if x + y > y + x: return -1   # x should come first
        if x + y < y + x: return 1
        return 0
    return sorted(items, key=cmp_to_key(cmp))
```

## Complexity profile
- **Merge sort:** O(n log n) time always (no bad-input case), O(n) extra space, **stable**.
- **Quicksort:** O(n log n) average, **O(n^2) worst** (sorted input + naive pivot), O(log n) stack with the smaller-side-first trick; in-place, **not stable**.
- **Quickselect:** **average O(n)**, worst O(n^2); random pivot reduces expected comparisons and makes worst case practically unreachable. Median-of-medians gives a guaranteed O(n) but with a large constant — rarely worth it in interviews.
- **Heap alternative for top-k:** O(n log k) time, O(k) space — beats quickselect when k is small, when you want them *sorted*, or for a **streaming** input where you can't hold/partition the whole array.
- **Inversion counting via merge sort:** O(n log n), O(n) space — the only way to beat the obvious O(n^2).
- **3-way partition / Dutch flag:** O(n) time, O(1) space, single pass.

## Curated problems (easy -> hard)

### 1. Sort Colors (Dutch National Flag)  -  Medium
- **Problem:** Sort an array of 0s, 1s, and 2s in-place, in a single pass, without using a library sort.
- **Practice (free):** https://leetcode.com/problems/sort-colors/
- **Video (free):** https://neetcode.io/problems/sort-colors
- **Idea:** Three pointers — `lo` (next slot for 0), `hi` (next slot for 2), `mid` (scanner). Swap 0s to the front, 2s to the back; only `mid` advances on a 1 or after sending a 0 forward.
```python
def sortColors(nums):
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]; lo += 1; mid += 1
        elif nums[mid] == 2:
            nums[mid], nums[hi] = nums[hi], nums[mid]; hi -= 1   # do NOT advance mid
        else:                                                    # == 1
            mid += 1
```
- **Complexity:** Time O(n), Space O(1) — single pass.
- **Key insight / gotcha:** After swapping with `hi` you must **not** advance `mid` — the value swapped in from the back is unexamined and could itself be a 0 or 2. After swapping with `lo` you *can* advance both, because `lo <= mid` means the value pulled from `lo` was already scanned (it was a 1).
- **Follow-up:** "Generalize to k colors / a counting sort." Count occurrences then overwrite — O(n) but two passes; Dutch flag is the one-pass, in-place, 3-bucket special case.

### 2. Kth Largest Element in an Array (Quickselect)  -  Medium
- **Problem:** Return the k-th largest element in an unsorted array (the k-th largest in sorted order, not the k-th distinct).
- **Practice (free):** https://leetcode.com/problems/kth-largest-element-in-an-array/
- **Video (free):** https://neetcode.io/problems/kth-largest-element-in-an-array
- **Idea:** k-th largest = the element at index `n-k` in ascending order. Quickselect: partition around a random pivot and recurse only into the side that contains index `n-k`. Average O(n).
```python
import random

def findKthLargest(nums, k):
    target = len(nums) - k                       # index in ascending order
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        p = random.randint(lo, hi)               # random pivot avoids O(n^2)
        nums[p], nums[hi] = nums[hi], nums[p]
        pivot, i = nums[hi], lo
        for j in range(lo, hi):                  # Lomuto partition
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]; i += 1
        nums[i], nums[hi] = nums[hi], nums[i]
        if   i == target: return nums[i]
        elif i < target:  lo = i + 1             # answer is to the right
        else:             hi = i - 1             # answer is to the left
```
- **Complexity:** Time O(n) average, **O(n^2) worst**; Space O(1) (iterative, in-place).
- **Key insight / gotcha:** Quickselect recurses into **one** side only — that's what turns the O(n log n) of a full sort into expected O(n). The **random pivot** is mandatory: on already-sorted input a fixed (last) pivot degrades every partition to size 1 and you hit O(n^2).
- **Heap alternative (cross-ref `12_heap.md`):** keep a min-heap of size k — `heapq.heappush`/`heappop` each new element, the root is the answer. O(n log k) time, O(k) space. **Prefer the heap when k is small, when the data streams, or when you must return all top-k sorted.** Prefer quickselect when you just need the single k-th value and can mutate the array.
- **Follow-up:** "Guaranteed O(n)?" Median-of-medians picks a provably good pivot for worst-case O(n), but the constant is large; in practice random pivot is what's expected.

### 3. Largest Number (Custom Comparator)  -  Medium
- **Problem:** Given a list of non-negative integers, arrange them to form the largest possible number; return it as a string.
- **Practice (free):** https://leetcode.com/problems/largest-number/
- **Video (free):** https://neetcode.io/problems/largest-number
- **Idea:** Order two numbers `x, y` by comparing the concatenations `xy` vs `yx` as strings — whichever pairing is larger wins. This is a genuine **comparator** (not a per-element key), so use `functools.cmp_to_key`.
```python
from functools import cmp_to_key

def largestNumber(nums):
    strs = list(map(str, nums))
    def cmp(x, y):
        if x + y > y + x: return -1      # x before y => larger number
        if x + y < y + x: return 1
        return 0
    strs.sort(key=cmp_to_key(cmp))
    res = ''.join(strs)
    return '0' if res[0] == '0' else res   # handle all-zeros -> "00..0" -> "0"
```
- **Complexity:** Time O(n log n · L) (L = max digits, paid per comparison), Space O(n).
- **Key insight / gotcha:** You **cannot** sort by numeric value or by string length — `"3"` must beat `"30"` because `"330" > "303"`. Comparing `x+y` vs `y+x` is the only consistent rule, and it *is* a valid total order (it's transitive). Don't forget the all-zeros edge case: `[0,0]` would otherwise return `"00"`.
- **Follow-up:** "Why a comparator and not a `key=`?" There's no function of a single element that captures the pairwise concat rule, so it must be a comparator. (You *can* abuse a key via repeating the string, but that's fragile.)

### 4. Sort an Array (Merge Sort + Quicksort)  -  Medium
- **Problem:** Sort an integer array in ascending order without using built-in sort; expected O(n log n).
- **Practice (free):** https://leetcode.com/problems/sort-an-array/
- **Video (free):** https://neetcode.io/problems/sort-an-array
- **Idea:** Show you can implement both. **Merge sort** = split, recurse, merge (stable, guaranteed O(n log n)). **Quicksort** = partition around a random pivot, recurse both sides (in-place, average O(n log n)).
```python
import random

def sortArray(nums):
    # --- Merge sort (guaranteed O(n log n), O(n) space, stable) ---
    def merge_sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
        out.extend(left[i:]); out.extend(right[j:])
        return out
    return merge_sort(nums)

def sortArrayQuick(nums):
    # --- Quicksort (in-place, average O(n log n), random pivot) ---
    def quicksort(lo, hi):
        if lo >= hi:
            return
        p = random.randint(lo, hi)
        nums[p], nums[hi] = nums[hi], nums[p]
        pivot, i = nums[hi], lo
        for j in range(lo, hi):
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]; i += 1
        nums[i], nums[hi] = nums[hi], nums[i]
        quicksort(lo, i - 1)
        quicksort(i + 1, hi)
    quicksort(0, len(nums) - 1)
    return nums
```
- **Complexity:** Merge sort O(n log n) time / O(n) space / stable. Quicksort O(n log n) average / O(log n) stack / in-place / **not stable**; O(n^2) worst without a random pivot.
- **Key insight / gotcha:** LeetCode's test set includes a sorted/anti-sorted array specifically to TLE a fixed-pivot quicksort — **the random pivot is required to pass.** Use `<=` in the merge to keep it stable. To bound quicksort's stack to O(log n), recurse into the smaller partition first (or recurse the smaller side and loop on the larger).
- **Follow-up:** "Heapsort?" O(n log n) worst case, in-place, not stable — build a heap then pop. Good when you need worst-case guarantees *and* O(1) extra space.

### 5. Count of Smaller Numbers After Self (Merge Sort Counting)  -  Hard
- **Problem:** For each `nums[i]`, count how many elements to its right are smaller; return that count array.
- **Practice (free):** https://leetcode.com/problems/count-of-smaller-numbers-after-self/
- **Video (free):** https://neetcode.io/problems/count-of-smaller-numbers-after-self
- **Idea:** Merge sort the **indices** (so we can attribute counts to original positions). During the merge, when we pick an element from the **right** half before the current **left** element, every right element already emitted is smaller-and-after the lefts that remain — so add the right-emitted count to each remaining left index.
```python
def countSmaller(nums):
    n = len(nums)
    counts = [0] * n
    idx = list(range(n))                          # sort indices, not values

    def merge_sort(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        merge_sort(lo, mid); merge_sort(mid, hi)
        merged, i, j, right_smaller = [], lo, mid, 0
        while i < mid and j < hi:
            if nums[idx[j]] < nums[idx[i]]:       # right element is smaller
                right_smaller += 1                # it sits after, counts for later lefts
                merged.append(idx[j]); j += 1
            else:
                counts[idx[i]] += right_smaller   # all rights emitted so far are smaller+after
                merged.append(idx[i]); i += 1
        while i < mid:
            counts[idx[i]] += right_smaller; merged.append(idx[i]); i += 1
        while j < hi:
            merged.append(idx[j]); j += 1
        idx[lo:hi] = merged

    merge_sort(0, n)
    return counts
```
- **Complexity:** Time O(n log n), Space O(n).
- **Key insight / gotcha:** Sort **indices**, not values, so each count lands in the right output slot. The counting happens when we take a **left** element: `right_smaller` already holds how many right-half (hence after, since right indices > left indices originally) elements were smaller. A BIT/Fenwick tree over compressed values is an alternative O(n log n).
- **Follow-up:** "Count *greater* after self, or count for *Reverse Pairs* (`a[i] > 2*a[j]`)?" Same merge-sort skeleton; only the comparison and where you accumulate the count change — see next problem.

### 6. Reverse Pairs (Merge Sort Counting)  -  Hard
- **Problem:** Count pairs `(i, j)` with `i < j` and `nums[i] > 2 * nums[j]`.
- **Practice (free):** https://leetcode.com/problems/reverse-pairs/
- **Video (free):** https://neetcode.io/problems/reverse-pairs
- **Idea:** Merge sort. **Before** merging the two sorted halves, count pairs where a left element exceeds twice a right element — both halves are sorted, so a single forward sweep with a moving pointer counts a whole block at once. Then merge normally.
```python
def reversePairs(nums):
    def merge_sort(lo, hi):                       # sorts nums[lo:hi], returns pair count
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        count = merge_sort(lo, mid) + merge_sort(mid, hi)
        # count cross pairs: nums[i] > 2*nums[j], i in left, j in right (both sorted)
        j = mid
        for i in range(lo, mid):
            while j < hi and nums[i] > 2 * nums[j]:
                j += 1
            count += j - mid                      # all rights mid..j-1 pair with this i
        nums[lo:hi] = sorted(nums[lo:hi])         # merge (sorted() ok; explicit merge also fine)
        return count
    return merge_sort(0, len(nums))
```
- **Complexity:** Time O(n log n), Space O(n).
- **Key insight / gotcha:** **Count first, merge second.** Because both halves are sorted, the pointer `j` only moves forward across the whole left sweep (monotonic) — that keeps counting at O(n) per level, not O(n^2). If you merge before counting you destroy the "all lefts have smaller original index than all rights" structure. (Using an explicit two-pointer merge instead of `sorted()` keeps it a clean O(n) merge.)
- **Follow-up:** "Plain inversion count (`a[i] > a[j]`)?" Identical, but do the counting *inside* the merge step (when you take a right element, it inverts with every remaining left) — that's the textbook inversions algorithm.

### 7. Median of Two Sorted Arrays (Binary-Search Partition)  -  Hard
- **Problem:** Given two sorted arrays, return the median of their combined elements in O(log(m+n)).
- **Practice (free):** https://leetcode.com/problems/median-of-two-sorted-arrays/
- **Video (free):** https://neetcode.io/problems/median-of-two-sorted-arrays
- **Idea:** Binary search the **partition** of the smaller array. Choose how many elements of A go in the left half; the rest of the left half comes from B. A valid partition has `maxLeftA <= minRightB` and `maxLeftB <= minRightA`; then the median is read from the four boundary elements. Cross-ref `09_binary_search.md`.
```python
def findMedianSortedArrays(A, B):
    if len(A) > len(B):
        A, B = B, A                               # binary search the smaller array
    m, n = len(A), len(B)
    half = (m + n + 1) // 2                        # size of the combined left half
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2                         # take i from A
        j = half - i                               # take j from B
        Aleft  = A[i - 1] if i > 0 else float('-inf')
        Aright = A[i]     if i < m else float('inf')
        Bleft  = B[j - 1] if j > 0 else float('-inf')
        Bright = B[j]     if j < n else float('inf')
        if Aleft <= Bright and Bleft <= Aright:    # correct partition
            if (m + n) % 2:
                return max(Aleft, Bleft)           # odd total
            return (max(Aleft, Bleft) + min(Aright, Bright)) / 2
        elif Aleft > Bright:
            hi = i - 1                             # took too many from A
        else:
            lo = i + 1                             # took too few from A
    raise ValueError("inputs not sorted")
```
- **Complexity:** Time O(log(min(m, n))), Space O(1).
- **Key insight / gotcha:** You binary-search the **partition point**, never the values. Always search the **smaller** array so `j = half - i` stays in range. The `±inf` sentinels handle the edges where one side contributes nothing — without them the boundary checks need messy special-casing.
- **Follow-up:** "k-th element of two sorted arrays?" Same partition idea, or a simpler O(log k) recursion that discards `k/2` elements from one array each step.

### 8. Maximum Subarray (Divide & Conquer variant)  -  Medium
- **Problem:** Find the contiguous subarray with the largest sum and return that sum.
- **Practice (free):** https://leetcode.com/problems/maximum-subarray/
- **Video (free):** https://neetcode.io/problems/maximum-subarray
- **Idea (D&C):** The best subarray is entirely in the left half, entirely in the right half, or **crosses the midpoint**. Solve the two halves recursively; compute the best crossing sum by extending greedily left and right from the middle; return the max of the three.
```python
def maxSubArray(nums):
    def dc(lo, hi):
        if lo == hi:
            return nums[lo]
        mid = (lo + hi) // 2
        left  = dc(lo, mid)                        # best fully in left
        right = dc(mid + 1, hi)                    # best fully in right
        # best crossing the midpoint:
        s, best_left = 0, float('-inf')
        for k in range(mid, lo - 1, -1):
            s += nums[k]; best_left = max(best_left, s)
        s, best_right = 0, float('-inf')
        for k in range(mid + 1, hi + 1):
            s += nums[k]; best_right = max(best_right, s)
        return max(left, right, best_left + best_right)
    return dc(0, len(nums) - 1)
```
- **Complexity:** Time O(n log n), Space O(log n) recursion.
- **Key insight / gotcha:** The cross sum must **include the midpoint** and extend outward independently on each side, then add — that's the only piece the two recursive calls can't see. **Kadane's algorithm is simpler and strictly better here: O(n), O(1)** (`cur = max(x, cur + x); best = max(best, cur)`) — cross-ref `07_greedy.md`. Bring up D&C only when asked for it or for "max subarray sum in a 2D / segment-tree-able setting."
- **Follow-up:** "Return the indices, or handle queries on subranges." D&C generalizes into a segment tree storing (total, prefix-best, suffix-best, best) per node, answering range-max-subarray queries in O(log n) — the D&C combine *is* the segment-tree merge.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (k-th / top-k / sort-by-rule / count-pairs / split-in-half)
- [ ] I can write the merge-sort template from memory (and know why `<=` keeps it stable)
- [ ] I can write Lomuto partition + quickselect from memory and explain the random-pivot need
- [ ] I can write the Dutch-flag 3-way partition from memory
- [ ] I can state when to pick quickselect vs a heap for top-k
- [ ] I can explain why the merge step can count inversions in O(1) per block
- [ ] Sort Colors — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Kth Largest (Quickselect) — 🔴 / 🟡 / 🟢
- [ ] Largest Number (comparator) — 🔴 / 🟡 / 🟢
- [ ] Sort an Array (merge + quicksort) — 🔴 / 🟡 / 🟢
- [ ] Count of Smaller Numbers After Self — 🔴 / 🟡 / 🟢
- [ ] Reverse Pairs — 🔴 / 🟡 / 🟢
- [ ] Median of Two Sorted Arrays — 🔴 / 🟡 / 🟢
- [ ] Maximum Subarray (D&C + Kadane) — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (Sorting / Divide & Conquer problems are spread across the Arrays, Heap, and Advanced sections) — https://neetcode.io/roadmap ; CLRS chapters on Quicksort & Medians/Order Statistics (the canonical quickselect + median-of-medians treatment) ; takeUforward/Striver merge-sort & quickselect videos — https://www.youtube.com/results?search_query=striver+merge+sort+count+inversions ; Python docs on sorting + `functools.cmp_to_key` — https://docs.python.org/3/howto/sorting.html
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Modified Binary Search & K-way merge patterns) — https://www.designgurus.io (free alternative: the NeetCode roadmap above plus the Python sorting HOWTO cover the same comparator/merge/quickselect ground with examples).

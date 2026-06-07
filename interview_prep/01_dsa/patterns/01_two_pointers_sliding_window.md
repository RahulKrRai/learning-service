# 01 - Two Pointers & Sliding Window
> One-line: reach for this when you're scanning a linear structure (array/string) and a brute-force pair/subarray loop is O(n^2) but the data has monotonic structure (sorted, or a window invariant) you can exploit to drop a dimension.

## When to use it (recognition triggers)
- The input is a **sorted array** and you need a pair/triple meeting a sum/closeness condition -> opposing pointers.
- You need the **longest / shortest / count of contiguous subarray or substring** satisfying a constraint (sum, distinct chars, at-most-k, frequency) -> sliding window.
- Phrases like "**at most K**", "**without repeating**", "**contains all of**", "**maximum/minimum window**".
- You're comparing a string from **both ends** (palindrome) or merging from both ends.
- Brute force is O(n^2)/O(n^3) over pairs/substrings and you suspect each element should be visited a **small constant number of times**.
- A monotonic quantity (a running sum, a frequency count, a max) lets you **shrink one side** when the window becomes invalid.

## Mental model
- **Two pointers (opposing):** start `l=0`, `r=n-1` on a *sorted* array. The sortedness means moving `l` right strictly increases a sum and moving `r` left strictly decreases it, so you can decide which pointer to move and never revisit a discarded candidate. This collapses an O(n^2) pair search to O(n).
- **Sliding window:** maintain a window `[l, r]` and a running summary (count map, sum, distinct count). Expand `r` to include new elements; when the window violates the constraint, advance `l` to restore it. Each index enters and leaves the window once, so the whole scan is O(n) amortized even though there are two nested-looking loops.
- The hard part is choosing the **window invariant** and what to do at the moment it breaks: for "longest valid" you shrink only enough to become valid again; for "shortest valid" you shrink greedily while still valid, recording the best.
- A **fixed-size window** (e.g. permutation match, sliding-window max) just slides by one each step; the trick is updating the summary in O(1) on add/remove rather than recomputing.

## Reusable template(s)
```python
# --- Opposing two pointers on a SORTED array ---
def two_pointer_sorted(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return (l, r)
        elif s < target:
            l += 1          # need a bigger sum
        else:
            r -= 1          # need a smaller sum
    return None

# --- Variable-size sliding window (longest valid) ---
def longest_window(s):
    from collections import defaultdict
    count = defaultdict(int)
    l = best = 0
    for r, ch in enumerate(s):
        count[ch] += 1
        while window_invalid(count):   # shrink until valid again
            count[s[l]] -= 1
            if count[s[l]] == 0:
                del count[s[l]]
            l += 1
        best = max(best, r - l + 1)
    return best

# --- Variable-size sliding window (shortest valid covering a need) ---
def shortest_window(s, need):
    from collections import Counter
    need = Counter(need)
    missing = len(need)               # distinct chars still unmet
    l = 0
    best = (float('inf'), 0, 0)
    for r, ch in enumerate(s):
        if ch in need:
            need[ch] -= 1
            if need[ch] == 0:
                missing -= 1
        while missing == 0:           # valid -> try to shrink
            if r - l + 1 < best[0]:
                best = (r - l + 1, l, r)
            left = s[l]
            if left in need:
                need[left] += 1
                if need[left] == 1:
                    missing += 1
            l += 1
    return best
```

## Complexity profile
- **Two pointers (sorted):** O(n) time, O(1) extra space — beats the O(n^2) nested-loop pair search. (3Sum is O(n^2) overall: one fixed element times an O(n) two-pointer scan, beating O(n^3).)
- **Sliding window:** O(n) time (each index added/removed once), O(k) space for the window summary (k = alphabet size or distinct elements) — beats the O(n^2)/O(n^3) substring enumeration.
- **Sliding-window maximum** with a monotonic deque: O(n) time, O(k) space — beats O(n*k) recomputation.

## Curated problems (easy -> hard)

### 1. Two Sum II - Input Array Is Sorted  -  Easy
- **Problem:** Given a 1-indexed array sorted in non-decreasing order, return the 1-based indices of the two numbers that add up to a given target (exactly one solution exists).
- **Practice (free):** https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/
- **Video (free):** https://neetcode.io/problems/two-integer-sum-ii
- **Idea:** Opposing pointers; sortedness lets you move `l` right to grow the sum or `r` left to shrink it, discarding the other end with certainty.
```python
from typing import List

def twoSum(numbers: List[int], target: int) -> List[int]:
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]      # 1-indexed
        elif s < target:
            l += 1
        else:
            r -= 1
    return []  # guaranteed unreachable per constraints
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Works *only because the array is sorted*. If `s < target`, no pair using the current `r` and any smaller-or-equal left index can ever reach target, so advancing `l` loses nothing.
- **Follow-up:** "Unsorted input?" -> use a hash map (classic Two Sum, O(n) time / O(n) space), or sort first while tracking original indices if you need indices and can afford O(n log n).

### 2. Valid Palindrome  -  Easy
- **Problem:** Given a string, return true if it reads the same forwards and backwards considering only alphanumeric characters and ignoring case.
- **Practice (free):** https://leetcode.com/problems/valid-palindrome/
- **Video (free):** https://neetcode.io/problems/is-palindrome
- **Idea:** Two pointers from both ends, skipping non-alphanumeric characters, comparing case-folded characters.
```python
def isPalindrome(s: str) -> bool:
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum():
            l += 1
        while l < r and not s[r].isalnum():
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1
        r -= 1
    return True
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Keep the inner skip loops guarded by `l < r` so you don't walk past each other on an all-symbol string. `isalnum()` and `lower()` handle the filtering without building a new string.
- **Follow-up:** "Valid Palindrome II — allow deleting at most one char?" -> on the first mismatch, check whether `s[l+1..r]` or `s[l..r-1]` is a palindrome (one helper, still O(n)).

### 3. 3Sum  -  Medium
- **Problem:** Find all unique triplets in the array that sum to zero (no duplicate triplets in the output).
- **Practice (free):** https://leetcode.com/problems/3sum/
- **Video (free):** https://neetcode.io/problems/three-integer-sum
- **Idea:** Sort, fix each index `i`, then run a two-pointer scan on the suffix for the pair summing to `-nums[i]`; skip duplicates at every level.
```python
from typing import List

def threeSum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if nums[i] > 0:                      # smallest is positive -> no zero sum possible
            break
        if i > 0 and nums[i] == nums[i - 1]: # skip duplicate anchors
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:  # skip dup left
                    l += 1
                while l < r and nums[r] == nums[r + 1]:  # skip dup right
                    r -= 1
    return res
```
- **Complexity:** Time O(n^2), Space O(1) extra (ignoring the output and sort's stack)
- **Key insight / gotcha:** Dedup at three places — the anchor `i`, and both pointers *after* recording a hit. Skipping the anchor dup must compare to `nums[i-1]` (the already-processed value), not `nums[i+1]`.
- **Follow-up:** "3Sum Closest?" -> same fixed-anchor + two-pointer scan, but track the triplet whose sum has minimum `abs(sum - target)` instead of testing equality.

### 4. Container With Most Water  -  Medium
- **Problem:** Given heights of vertical lines, pick two lines that with the x-axis form a container holding the most water; return that maximum area.
- **Practice (free):** https://leetcode.com/problems/container-with-most-water/
- **Video (free):** https://neetcode.io/problems/max-water-container
- **Idea:** Start with the widest container (both ends); area is limited by the shorter wall, so move the shorter pointer inward — that's the only move that can possibly increase area.
```python
from typing import List

def maxArea(height: List[int]) -> int:
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1                  # shorter wall caps the area; widening won't help it
        else:
            r -= 1
    return best
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Moving the *taller* wall can never improve the area (width shrinks, height still capped by the shorter wall), so always move the shorter one. On ties, moving either is fine.
- **Follow-up:** "Why is the greedy move correct?" -> because the current pair already maximizes width for that shorter wall; any other pairing with that shorter wall has less width, so you can safely discard it.

### 5. Trapping Rain Water  -  Hard
- **Problem:** Given an elevation map (bar heights of unit width), compute how much rainwater is trapped between the bars after raining.
- **Practice (free):** https://leetcode.com/problems/trapping-rain-water/
- **Video (free):** https://neetcode.io/problems/trapping-rain-water
- **Idea:** Water above each bar = min(max-to-left, max-to-right) - height. Two pointers carrying `left_max`/`right_max` resolve this in one O(1)-space pass: process the side whose running max is smaller, because that side's water is fully determined.
```python
from typing import List

def trap(height: List[int]) -> int:
    if not height:
        return 0
    l, r = 0, len(height) - 1
    left_max, right_max = height[l], height[r]
    water = 0
    while l < r:
        if left_max < right_max:
            l += 1
            left_max = max(left_max, height[l])
            water += left_max - height[l]   # bounded by the smaller (left) max
        else:
            r -= 1
            right_max = max(right_max, height[r])
            water += right_max - height[r]
    return water
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** When `left_max < right_max`, the water on the left index is bounded solely by `left_max` — you don't need the exact right max, only that *some* taller wall exists on the right, which `right_max` guarantees. That's why advancing the smaller side is always safe.
- **Follow-up:** "Explain the prefix/suffix-max DP alternative." -> precompute `left_max[]` and `right_max[]` arrays, then sum `min(left_max[i], right_max[i]) - height[i]`; same O(n) time but O(n) space. The two-pointer version trades those arrays for two scalars.

### 6. Longest Substring Without Repeating Characters  -  Medium
- **Problem:** Find the length of the longest substring of a string that contains no repeated characters.
- **Practice (free):** https://leetcode.com/problems/longest-substring-without-repeating-characters/
- **Video (free):** https://neetcode.io/problems/longest-substring-without-duplicates
- **Idea:** Variable window; keep the last-seen index of each char and when a repeat appears inside the window, jump `l` to just past the previous occurrence.
```python
def lengthOfLongestSubstring(s: str) -> int:
    last = {}          # char -> most recent index seen
    l = best = 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1      # jump left past the duplicate
        last[ch] = r
        best = max(best, r - l + 1)
    return best
```
- **Complexity:** Time O(n), Space O(min(n, alphabet))
- **Key insight / gotcha:** The guard `last[ch] >= l` matters — a stale index from *before* the current window must not drag `l` backwards. The jump version moves `l` in one step instead of shrinking char-by-char.
- **Follow-up:** "Longest substring with at most K distinct characters?" -> same skeleton but shrink while `len(count_map) > k`; record the longest valid window.

### 7. Longest Repeating Character Replacement  -  Medium
- **Problem:** Given a string of uppercase letters and an integer k, find the longest substring you can make all-identical by replacing at most k characters.
- **Practice (free):** https://leetcode.com/problems/longest-repeating-character-replacement/
- **Video (free):** https://neetcode.io/problems/longest-repeating-substring-with-replacement
- **Idea:** A window is valid when `window_len - count_of_most_frequent_char <= k` (the non-majority chars are what you'd replace). Expand `r`; when invalid, slide `l` forward by one.
```python
from collections import defaultdict

def characterReplacement(s: str, k: int) -> int:
    count = defaultdict(int)
    l = best = max_freq = 0
    for r, ch in enumerate(s):
        count[ch] += 1
        max_freq = max(max_freq, count[ch])
        # replacements needed = window size - most frequent count
        if (r - l + 1) - max_freq > k:
            count[s[l]] -= 1
            l += 1
        best = max(best, r - l + 1)
    return best
```
- **Complexity:** Time O(n), Space O(1) (26 letters)
- **Key insight / gotcha:** `max_freq` is intentionally never decreased. The window only ever shrinks by one and grows by one, so `best` can't increase unless a *new* `max_freq` is reached; a slightly stale `max_freq` therefore never produces a wrong larger answer. This is the subtle part most people get wrong.
- **Follow-up:** "Does keeping a stale `max_freq` ever overcount?" -> no: the window never shrinks below its previous max length, so any reported length was genuinely achievable with the true frequency at that point.

### 8. Permutation in String  -  Medium
- **Problem:** Given strings s1 and s2, return true if s2 contains any permutation of s1 as a contiguous substring.
- **Practice (free):** https://leetcode.com/problems/permutation-in-string/
- **Video (free):** https://neetcode.io/problems/permutation-string
- **Idea:** Fixed-size window of length `len(s1)` over s2; maintain a frequency count and a `matches` counter of how many of the 26 letters have exactly the right frequency. Slide and update both ends in O(1).
```python
def checkInclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    s1c = [0] * 26
    win = [0] * 26
    for ch in s1:
        s1c[ord(ch) - 97] += 1
    idx = lambda c: ord(c) - 97
    matches = sum(1 for i in range(26) if s1c[i] == win[i])  # = 26 initially (all zero counts)

    l = 0
    for r in range(len(s2)):
        i = idx(s2[r])
        win[i] += 1
        matches += 1 if win[i] == s1c[i] else (-1 if win[i] == s1c[i] + 1 else 0)
        if r - l + 1 > len(s1):          # window too big -> drop leftmost
            j = idx(s2[l])
            win[j] -= 1
            matches += 1 if win[j] == s1c[j] else (-1 if win[j] == s1c[j] - 1 else 0)
            l += 1
        if matches == 26:
            return True
    return False
```
- **Complexity:** Time O(n) where n = len(s2), Space O(1) (two size-26 arrays)
- **Key insight / gotcha:** The `matches == 26` trick avoids re-comparing all 26 counts on every slide — update `matches` only for the single letter whose count changed, checking if it just *became* equal (+1) or just *left* equality (-1). Simpler-but-slower alternative: compare the two count arrays each step (O(26n)).
- **Follow-up:** "Find All Anagrams in a String?" -> identical window; instead of returning early, append `l` to a result list every time `matches == 26`.

### 9. Minimum Window Substring  -  Hard
- **Problem:** Given strings s and t, return the smallest substring of s containing every character of t (with multiplicity); empty string if none.
- **Practice (free):** https://leetcode.com/problems/minimum-window-substring/
- **Video (free):** https://neetcode.io/problems/minimum-window-with-characters
- **Idea:** Expand `r` to satisfy the requirement (track how many required chars are still missing); once satisfied, greedily shrink `l` while still valid, recording the smallest window seen.
```python
from collections import Counter

def minWindow(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)                 # total required chars (with multiplicity) still needed
    l = 0
    best_len, best_l = float('inf'), 0
    for r, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1             # this char counted toward a real requirement
        need[ch] -= 1                # may go negative for surplus chars
        while missing == 0:          # window valid -> shrink
            if r - l + 1 < best_len:
                best_len, best_l = r - l + 1, l
            need[s[l]] += 1
            if need[s[l]] > 0:       # we just removed a *required* char -> window breaks
                missing += 1
            l += 1
    return "" if best_len == float('inf') else s[best_l:best_l + best_len]
```
- **Complexity:** Time O(|s| + |t|), Space O(|t|) (alphabet of t)
- **Key insight / gotcha:** Let `need` go negative to track surplus chars cheaply. A char is "required" exactly when its `need` value is `> 0` *before* you decrement it (on entry) or *after* you increment it (on exit). Conflating surplus with requirement is the classic bug.
- **Follow-up:** "Constant-factor speedup for sparse alphabets?" -> filter `s` down to only the indices whose char is in `t` and slide over that reduced list; helps when relevant chars are rare in a long `s`.

### 10. Sliding Window Maximum  -  Hard
- **Problem:** Given an array and window size k, return the maximum of each contiguous window of size k as it slides left to right.
- **Practice (free):** https://leetcode.com/problems/sliding-window-maximum/
- **Video (free):** https://neetcode.io/problems/sliding-window-maximum
- **Idea:** Maintain a **monotonic decreasing deque of indices**: before adding a new index, pop smaller-or-equal values from the back (they can never be the max while the newcomer lives); the front is always the current window's max. Pop the front when it slides out of range.
```python
from collections import deque
from typing import List

def maxSlidingWindow(nums: List[int], k: int) -> List[int]:
    dq = deque()       # indices, values strictly decreasing front -> back
    res = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:   # newcomer dominates smaller tails
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:                # front index fell out of the window
            dq.popleft()
        if i >= k - 1:                    # first full window reached
            res.append(nums[dq[0]])
    return res
```
- **Complexity:** Time O(n) (each index pushed and popped at most once), Space O(k)
- **Key insight / gotcha:** Store **indices, not values**, so you can detect when the front expires (`dq[0] <= i - k`). Popping `<=` (not just `<`) keeps the deque smaller and is correct because for the max we don't need to retain equal stale values.
- **Follow-up:** "What about sliding-window *minimum* or both at once?" -> mirror the comparison (pop `>= x` for a min-deque); for both, run two deques in parallel. A max-heap also works at O(n log k) but lazy deletion makes it messier than the deque.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (sorted-pair vs longest-window vs shortest-window vs fixed-window vs monotonic-deque)
- [ ] I can write the opposing-pointer template from memory
- [ ] I can write the variable-window (longest) and (shortest) templates from memory
- [ ] Two Sum II  -  🔴/🟡/🟢
- [ ] Valid Palindrome  -  🔴/🟡/🟢
- [ ] 3Sum (all three dedup spots)  -  🔴/🟡/🟢
- [ ] Container With Most Water (why move the shorter wall)  -  🔴/🟡/🟢
- [ ] Trapping Rain Water (why advance the smaller max)  -  🔴/🟡/🟢
- [ ] Longest Substring Without Repeating Chars (the `>= l` guard)  -  🔴/🟡/🟢
- [ ] Longest Repeating Character Replacement (stale `max_freq` is OK)  -  🔴/🟡/🟢
- [ ] Permutation in String (`matches == 26` trick)  -  🔴/🟡/🟢
- [ ] Minimum Window Substring (surplus vs required via negative counts)  -  🔴/🟡/🟢
- [ ] Sliding Window Maximum (monotonic deque of indices)  -  🔴/🟡/🟢

## Resources
- **Free:** NeetCode roadmap (Arrays & Hashing -> Two Pointers -> Sliding Window): https://neetcode.io/roadmap  |  NeetCode practice list (filter by Two Pointers / Sliding Window): https://neetcode.io/practice  |  takeUforward/striver sliding-window & two-pointer playlist (search): https://www.youtube.com/results?search_query=striver+sliding+window+and+two+pointer
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" — the original *Sliding Window* and *Two Pointers* pattern chapters: https://www.designgurus.io  (free alternative: the NeetCode roadmap sections above cover the same patterns with videos). AlgoMonster two-pointer/window track: https://algo.monster (free alternative: NeetCode practice list).

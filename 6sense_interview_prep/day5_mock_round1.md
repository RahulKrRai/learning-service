# Day 5 — Mock Round 1 (Timed Practice)
**Date: April 4 | Simulate Round 1 conditions**

---

## How to Use This File

**Format: 60 minutes, 1 problem** (confirmed 6sense format)

1. Set a **60-minute timer**.
2. Pick **one** problem from the list below — the hardest one you're not confident about.
3. Open a blank editor — no autocomplete, no hints, no referring to notes.
4. Talk out loud as you code (practice this — it matters for Senior bar).
5. At 60 min stop, then compare with solution.

**Senior time targets:**
- Pattern identified: < 3 min
- Approach agreed + brute force dismissed: < 6 min
- Coding started: < 8 min
- Working solution: < 40 min
- Edge cases + complexity stated: < 50 min
- Remaining 10 min: optimize, discuss follow-ups

---

## Mock Set A — Arrays / Strings / HashMap

### A1: Longest Subarray with Sum ≤ K
Given array of positive integers, find length of longest subarray with sum ≤ k.

**Your approach first (write it before looking at solution):**
```
Think: sliding window — expand right, shrink left when sum > k
```

```python
def longest_subarray_sum_k(nums, k):
    left = 0
    current_sum = 0
    max_len = 0
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum > k and left <= right:
            current_sum -= nums[left]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
# Time: O(n), Space: O(1)
```

---

### A2: Find All Anagram Substrings
Given string s and pattern p, find all start indices in s where an anagram of p begins.

```python
from collections import Counter

def find_anagrams(s, p):
    if len(p) > len(s): return []
    p_count = Counter(p)
    window = Counter(s[:len(p)])
    result = []
    if window == p_count:
        result.append(0)
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        left_char = s[i - len(p)]
        window[left_char] -= 1
        if window[left_char] == 0:
            del window[left_char]
        if window == p_count:
            result.append(i - len(p) + 1)
    return result
# Time: O(n), Space: O(1) since at most 26 chars
```

---

### A3: Spiral Matrix
Return all elements of matrix in spiral order.

```python
def spiral_order(matrix):
    result = []
    if not matrix: return result
    top, bottom, left, right = 0, len(matrix)-1, 0, len(matrix[0])-1

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1
    return result
```

---

### A4: Minimum Size Subarray Sum ≥ Target
```python
def min_subarray_len(target, nums):
    left = 0
    current_sum = 0
    min_len = float('inf')
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return min_len if min_len != float('inf') else 0
# Time: O(n), Space: O(1)
```

---

## Mock Set B — Two Pointers / Prefix Sum

### B1: Trapping Rain Water
```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water
# Time: O(n), Space: O(1)
# Key insight: water at position i = min(max_left, max_right) - height[i]
```

---

### B2: Jump Game II (Minimum Jumps to End)
```python
def jump(nums):
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps
# Time: O(n), Space: O(1)
# Key insight: BFS levels — each jump is one level
```

---

### B3: Next Permutation
```python
def next_permutation(nums):
    n = len(nums)
    i = n - 2
    # Find rightmost ascending pair
    while i >= 0 and nums[i] >= nums[i+1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    # Reverse from i+1 to end
    left, right = i + 1, n - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
```

---

## Post-Mock Review Checklist

After each mock session:
- [ ] Did I state my approach before coding?
- [ ] Did I get the right time/space complexity?
- [ ] Did I handle edge cases (empty input, single element, all equal)?
- [ ] Did I finish within 35–40 min per problem?
- [ ] Which problem type felt hardest? → revisit that topic

---

## Round 1 Day-Of Reminders

- Warm up with 1 easy problem 30 min before the interview
- Use Python (faster to write, less boilerplate)
- Always import at the top: `from collections import Counter, defaultdict, deque`
- If stuck for 5 min: ask for a hint ("Can I get a hint on the approach?") — it's better than silence
- Explain tradeoffs: "I can do this in O(n log n) with a sort, or O(n) with a hashmap — which would you prefer?"

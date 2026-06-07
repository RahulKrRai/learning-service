# Day 1 — Arrays, Strings, Two Pointers, Sliding Window
**Target: 3–4 hours | Date: March 31**

---

## Part 1: Two Pointers (1 hour)

### Problem 1: Two Sum (Sorted Input)
Given a sorted array, find two numbers that add up to target.

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left + 1, right + 1]  # 1-indexed
        elif total < target:
            left += 1
        else:
            right -= 1
    return []
# Time: O(n), Space: O(1)
```

### Problem 2: Three Sum
Find all unique triplets that sum to zero.

```python
def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:  # skip duplicates
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]: left += 1
                while left < right and nums[right] == nums[right-1]: right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return result
# Time: O(n^2), Space: O(1) excluding output
```

### Problem 3: Container With Most Water
```python
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        water = min(height[left], height[right]) * (right - left)
        max_water = max(max_water, water)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water
# Time: O(n), Space: O(1)
# Key insight: always move the shorter wall — moving the taller wall can only decrease area
```

### Problem 4: Valid Palindrome
```python
def is_palindrome(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
# Time: O(n), Space: O(n) for cleaned string
```

---

## Part 2: Sliding Window (1 hour)

### Problem 5: Longest Substring Without Repeating Characters
```python
def length_of_longest_substring(s):
    seen = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            left = seen[char] + 1  # jump left past the duplicate
        seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
# Time: O(n), Space: O(min(n, charset))
# Key insight: store index, not just presence — lets you jump left pointer
```

### Problem 6: Minimum Window Substring
Find smallest window in s that contains all chars of t.

```python
from collections import Counter

def min_window(s, t):
    need = Counter(t)
    have = {}
    formed = 0
    required = len(need)
    left = 0
    min_len = float('inf')
    result = ""

    for right, char in enumerate(s):
        have[char] = have.get(char, 0) + 1
        if char in need and have[char] == need[char]:
            formed += 1

        while formed == required:
            window_len = right - left + 1
            if window_len < min_len:
                min_len = window_len
                result = s[left:right+1]
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1

    return result
# Time: O(|s| + |t|), Space: O(|s| + |t|)
```

### Problem 7: Maximum Sum Subarray of Size K
```python
def max_sum_subarray(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # slide: add new, remove old
        max_sum = max(max_sum, window_sum)
    return max_sum
# Time: O(n), Space: O(1)
```

### Problem 8: Fruits Into Baskets (At Most 2 Distinct)
```python
def total_fruit(fruits):
    basket = {}
    left = 0
    max_count = 0
    for right, fruit in enumerate(fruits):
        basket[fruit] = basket.get(fruit, 0) + 1
        while len(basket) > 2:
            left_fruit = fruits[left]
            basket[left_fruit] -= 1
            if basket[left_fruit] == 0:
                del basket[left_fruit]
            left += 1
        max_count = max(max_count, right - left + 1)
    return max_count
# Generalizes to: longest subarray with at most K distinct elements
```

---

## Part 3: Arrays — Prefix Sum & Tricks (1 hour)

### Problem 9: Product of Array Except Self
```python
def product_except_self(nums):
    n = len(nums)
    result = [1] * n

    # left pass: result[i] = product of all elements to left of i
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]

    # right pass: multiply by product of all elements to right of i
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]

    return result
# Time: O(n), Space: O(1) extra (output array doesn't count)
# Key insight: no division needed — build prefix and suffix products separately
```

### Problem 10: Subarray Sum Equals K
```python
def subarray_sum(nums, k):
    count = 0
    prefix_sum = 0
    freq = {0: 1}  # prefix sum 0 appears once (empty subarray)
    for num in nums:
        prefix_sum += num
        # if prefix_sum - k exists, those subarrays sum to k
        count += freq.get(prefix_sum - k, 0)
        freq[prefix_sum] = freq.get(prefix_sum, 0) + 1
    return count
# Time: O(n), Space: O(n)
# Key insight: subarray[i..j] sum = prefix[j] - prefix[i-1]
#              so we need prefix[j] - k = prefix[i-1]
```

### Problem 11: Merge Intervals
```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:  # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
# Time: O(n log n), Space: O(n)
```

### Problem 12: Best Time to Buy and Sell Stock
```python
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
# Time: O(n), Space: O(1)
```

### Problem 13: Find All Duplicates in Array (nums in [1,n])
```python
def find_duplicates(nums):
    result = []
    for num in nums:
        idx = abs(num) - 1
        if nums[idx] < 0:
            result.append(abs(num))  # seen before
        else:
            nums[idx] = -nums[idx]  # mark as seen
    return result
# Time: O(n), Space: O(1)
# Key insight: use index as hash, negate to mark visited
```

---

## Part 4: Strings (30 min)

### Problem 14: Valid Anagram
```python
from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)
# Or without Counter:
def is_anagram_v2(s, t):
    if len(s) != len(t): return False
    count = {}
    for c in s: count[c] = count.get(c, 0) + 1
    for c in t:
        if c not in count or count[c] == 0: return False
        count[c] -= 1
    return True
# Time: O(n), Space: O(1) since only 26 letters
```

### Problem 15: Group Anagrams
```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))  # canonical form
        groups[key].append(s)
    return list(groups.values())
# Time: O(n * k log k) where k = max string length
# Optimization: use count tuple as key instead of sorted string → O(n*k)
```

### Problem 16: Longest Palindromic Substring
```python
def longest_palindrome(s):
    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left+1:right]

    result = ""
    for i in range(len(s)):
        odd = expand(i, i)      # odd length palindromes
        even = expand(i, i+1)   # even length palindromes
        if len(odd) > len(result): result = odd
        if len(even) > len(result): result = even
    return result
# Time: O(n^2), Space: O(1)
```

### Problem 17: Count All Palindromic Substrings
**⚠️ CONFIRMED 6SENSE QUESTION — different from above (count, not find longest)**

```python
def count_substrings(s):
    count = 0

    def expand_and_count(left, right):
        nonlocal count
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1       # every valid expansion is a palindrome
            left -= 1
            right += 1

    for i in range(len(s)):
        expand_and_count(i, i)      # odd-length palindromes centered at i
        expand_and_count(i, i + 1)  # even-length palindromes centered between i and i+1

    return count

# Example: s = "abc" → "a","b","c" → 3
# Example: s = "aaa" → "a","a","a","aa","aa","aaa" → 6
# Time: O(n^2), Space: O(1)

# KEY DIFFERENCE from "longest palindrome":
#   - longest: track max length string, return it
#   - count: increment counter on every valid palindrome found
# Same expand-around-center technique, different bookkeeping
```

### Problem 18: Top N Frequent Words (with alphabetical tie-breaking)
**⚠️ CONFIRMED 6SENSE QUESTION**

```python
import heapq
from collections import Counter

def top_k_frequent_words(words, k):
    freq = Counter(words)

    # Min-heap: store (-count, word) so that:
    #   - higher count = higher priority (negated)
    #   - same count → alphabetically smaller word stays (natural string comparison)
    heap = []
    for word, count in freq.items():
        heapq.heappush(heap, (-count, word))

    return [heapq.heappop(heap)[1] for _ in range(k)]

# Example: words=["i","love","leetcode","i","love","coding"], k=2
# → ["i","love"] (i:2, love:2 tied → alphabetical order)
# Time: O(n log n), Space: O(n)

# Why (-count, word) works for tie-breaking:
#   heapq compares tuples lexicographically
#   same -count → compare word strings → smaller string wins (correct for alphabetical)
```

---

## Day 1 Checklist
- [ ] Two Pointers: Two Sum, Three Sum, Container With Most Water
- [ ] Sliding Window: Longest Substring, Min Window Substring
- [ ] Prefix Sum: Product Except Self, Subarray Sum = K
- [ ] Arrays: Merge Intervals, Buy/Sell Stock
- [ ] Strings: Anagram, Group Anagrams
- [ ] **Palindrome Count** (confirmed 6sense)
- [ ] **Top N Frequent Words** (confirmed 6sense)

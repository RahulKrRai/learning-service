# Day 4 — Dynamic Programming & Recursion
**Target: 3–4 hours | Date: April 3**

---

## DP Framework

Ask these 4 questions for every DP problem:

1. **What is the subproblem?** Define `dp[i]` or `dp[i][j]` precisely.
2. **What is the recurrence?** How does dp[i] depend on smaller subproblems?
3. **Base case?** What is the smallest valid input?
4. **Answer?** Where in dp is the final answer?

---

## Part 1: 1D DP (1 hour)

### Problem 1: Climbing Stairs (Fibonacci DP)
How many ways to climb n stairs taking 1 or 2 steps?

```python
def climb_stairs(n):
    if n <= 2: return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
# dp[i] = dp[i-1] + dp[i-2]
# Time: O(n), Space: O(1)
```

### Problem 2: House Robber
Can't rob adjacent houses. Max money.

```python
def rob(nums):
    if not nums: return 0
    if len(nums) == 1: return nums[0]
    prev2, prev1 = 0, 0
    for num in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + num)
    return prev1
# dp[i] = max(dp[i-1], dp[i-2] + nums[i])
# Time: O(n), Space: O(1)
```

### Problem 3: Word Break
Can s be segmented using words from wordDict?

```python
def word_break(s, word_dict):
    word_set = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # empty string
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[n]
# dp[i] = True if s[:i] can be segmented
# Time: O(n^2 * m) where m = avg word length, Space: O(n)
```

### Problem 4: Decode Ways
Count ways to decode a numeric string (1→A, 2→B, ..., 26→Z)

```python
def num_decodings(s):
    if not s or s[0] == '0': return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1  # empty string: 1 way
    dp[1] = 1  # first char (not '0')

    for i in range(2, n + 1):
        one_digit = int(s[i-1])
        two_digit = int(s[i-2:i])
        if one_digit >= 1:
            dp[i] += dp[i-1]
        if 10 <= two_digit <= 26:
            dp[i] += dp[i-2]
    return dp[n]
# Time: O(n), Space: O(n) → can optimize to O(1)
```

---

## Part 2: Knapsack / Choice DP (1 hour)

### Problem 5: 0/1 Knapsack
```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]
            # Take item i-1 (if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])
    return dp[n][capacity]
# Time: O(n * capacity), Space: O(n * capacity) → optimize to O(capacity)
```

### Problem 6: Coin Change (Min Coins)
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
# dp[i] = min coins to make amount i
# Time: O(amount * len(coins)), Space: O(amount)
```

### Problem 7: Coin Change II (Number of Ways)
```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1  # 1 way to make 0
    for coin in coins:          # outer loop on coins → avoids counting permutations
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]
    return dp[amount]
# Time: O(amount * len(coins)), Space: O(amount)
# Key: outer loop on coins ensures each coin used in combination order
```

### Problem 8: Target Sum (Count ways to assign +/-)
```python
def find_target_sum_ways(nums, target):
    # Reduce to: find subset with sum = (total + target) / 2
    total = sum(nums)
    if (total + target) % 2 != 0 or abs(target) > total:
        return 0
    s = (total + target) // 2

    dp = [0] * (s + 1)
    dp[0] = 1
    for num in nums:
        for j in range(s, num - 1, -1):  # reverse to avoid reuse
            dp[j] += dp[j - num]
    return dp[s]
# Time: O(n * s), Space: O(s)
```

---

## Part 3: String DP (1 hour)

### Problem 9: Longest Common Subsequence (LCS)
**⚠️ CONFIRMED 6SENSE QUESTION — they asked to PRINT the actual subsequence, not just the length**

```python
def lcs_length(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
# Time: O(m*n), Space: O(m*n)

# *** CRITICAL: Reconstruct the actual LCS string by backtracking through dp table ***
def lcs_with_path(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Step 1: Fill DP table (same as above)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Step 2: Backtrack from dp[m][n] to reconstruct the path
    result = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            result.append(text1[i-1])  # this char is part of LCS
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1  # came from above
        else:
            j -= 1  # came from left

    return ''.join(reversed(result))  # built backwards, so reverse

# Example:
# text1 = "ABCBDAB", text2 = "BDCAB"
# lcs_with_path → "BCAB" or "BDAB" (length 4)
# Time: O(m*n), Space: O(m*n)

# Mental model for backtracking:
# At dp[i][j]:
#   - if chars match → this char is in LCS, go diagonal (i-1, j-1)
#   - else → go in direction of larger neighbor (up or left)
#   - keep going until i=0 or j=0
```

### Problem 10: Edit Distance (Levenshtein)
```python
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i  # delete all chars
    for j in range(n + 1): dp[0][j] = j  # insert all chars

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # delete from word1
                    dp[i][j-1],    # insert into word1
                    dp[i-1][j-1]   # replace
                )
    return dp[m][n]
```

### Problem 11: Palindrome Partitioning II (Min Cuts)
```python
def min_cut(s):
    n = len(s)
    # is_palindrome[i][j] = True if s[i..j] is palindrome
    is_palindrome = [[False] * n for _ in range(n)]
    for i in range(n):
        is_palindrome[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                is_palindrome[i][j] = (length == 2) or is_palindrome[i+1][j-1]

    dp = list(range(n))  # dp[i] = min cuts for s[:i+1]
    for i in range(1, n):
        if is_palindrome[0][i]:
            dp[i] = 0
            continue
        for j in range(1, i + 1):
            if is_palindrome[j][i]:
                dp[i] = min(dp[i], dp[j-1] + 1)
    return dp[n-1]
```

---

## Part 4: Interval / Grid DP (30 min)

### Problem 12: Unique Paths (Grid)
```python
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]
# Time: O(m*n), Space: O(m*n) → optimize to O(n)
```

### Problem 13: Longest Increasing Subsequence (LIS)
```python
def length_of_lis(nums):
    n = len(nums)
    dp = [1] * n  # each element is a subsequence of length 1
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
# Time: O(n^2), Space: O(n)

# O(n log n) with patience sorting:
import bisect
def length_of_lis_fast(nums):
    tails = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

---

## DP Pattern Summary

| Problem Type | State | Transition |
|-------------|-------|-----------|
| 1D linear | dp[i] | dp[i] = f(dp[i-1], dp[i-2]) |
| Knapsack | dp[i][w] | take/skip item |
| String match | dp[i][j] | match/mismatch chars |
| Grid | dp[i][j] | come from top or left |
| LIS | dp[i] | max over all j < i |

---

## Day 4 Checklist
- [ ] 1D DP: Climbing Stairs, House Robber, Word Break, Decode Ways
- [ ] Knapsack: 0/1 Knapsack, Coin Change, Coin Change II, Target Sum
- [ ] String DP: LCS, Edit Distance
- [ ] Misc: Unique Paths, LIS (both O(n^2) and O(n log n))

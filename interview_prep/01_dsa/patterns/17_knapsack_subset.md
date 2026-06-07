# 17 - Knapsack & Subset DP
> When you must choose a subset of items under a numeric budget/target and ask "max value / can I hit it / how many ways" — reach for knapsack.

## When to use it (recognition triggers)
- You have a list of numbers (weights, values, coins, stones) and a **single integer constraint** (capacity, target sum, amount).
- The question is one of: **maximize/minimize** a value, **can a subset reach** an exact sum (feasibility), or **count the ways** to reach a sum.
- Each item is either **taken or skipped** (0/1 knapsack) or can be **reused unlimited times** (unbounded knapsack / coins).
- Brute force is "try every subset" = `O(2^n)` and the target/capacity is a bounded integer — that bound becomes a DP dimension.
- Phrases like "partition into two equal halves", "assign +/- signs", "fewest coins", "number of combinations".

## Mental model
- State is `dp[i][c]` = the best/feasible/count answer using the first `i` items with budget `c`. For each item you branch: **skip it** (`dp[i-1][c]`) or **take it** (`dp[i-1][c-w]` for 0/1, or `dp[i][c-w]` for unbounded since you may reuse).
- **0/1 vs unbounded** is entirely about which row you read when "taking": 0/1 reads the *previous* item's row (each item once); unbounded reads the *current* row (reuse allowed). In 1-D this is the difference between iterating capacity **descending** (0/1) vs **ascending** (unbounded).
- **Feasibility/count vs optimization**: same recurrence, you just swap the combine operator — `or` for "can we?", `+` for "how many ways", `max`/`min` for value. The skeleton never changes.
- Many problems are knapsack in disguise: "partition equal subset" is "subset summing to total/2", "target sum +/-" is "subset summing to (total+target)/2", "last stone weight" is "split into two subsets with minimal difference".
- The 1-D rolling array works because each `dp[c]` only depends on smaller-or-equal `c` from the prior state; choosing the loop direction preserves exactly the row you need.

## Reusable template(s)
```python
# ---- 0/1 Knapsack: maximize value, capacity W, each item used at most once ----
def knapsack_01(weights, values, W):
    dp = [0] * (W + 1)                 # dp[c] = best value with capacity c
    for i in range(len(weights)):
        w, v = weights[i], values[i]
        for c in range(W, w - 1, -1):  # DESCENDING -> each item used once
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[W]

# ---- Subset feasibility: can any subset sum to exactly `target`? ----
def subset_sum_possible(nums, target):
    dp = [False] * (target + 1)
    dp[0] = True                       # empty subset reaches 0
    for x in nums:
        for c in range(target, x - 1, -1):   # 0/1: descending
            dp[c] = dp[c] or dp[c - x]
    return dp[target]

# ---- Unbounded knapsack / coins: items reusable -> ASCENDING capacity ----
def coin_min(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for c in range(1, amount + 1):
        for coin in coins:
            if coin <= c:
                dp[c] = min(dp[c], dp[c - coin] + 1)
    return dp[amount] if dp[amount] != INF else -1
```

## Complexity profile
- Time `O(n * C)`, space `O(C)` with the rolling 1-D array (`O(n*C)` for the 2-D table), where `n` = number of items and `C` = capacity/target/amount.
- This is **pseudo-polynomial**: linear in the *value* of `C`, not its bit-length. You're beating the brute-force `O(2^n)` subset enumeration (and `O(k^n)` for unbounded "try every sequence").

## Curated problems (easy -> hard)

### 1. 0/1 Knapsack (concept)  -  Medium
- **Problem:** Given item weights and values and a capacity `W`, pick a subset (each item at most once) maximizing total value without exceeding `W`.
- **Practice (free):** https://leetcode.com/problems/partition-equal-subset-sum/ (closest free LeetCode proxy; the pure 0/1 knapsack lives on GeeksforGeeks)
- **Video (free):** https://www.youtube.com/results?search_query=takeuforward+0+1+knapsack
- **Idea:** For each item branch take/skip; in 1-D iterate capacity **descending** so each item is counted at most once.
```python
def knapsack_01(weights, values, W):
    # dp[c] = max value achievable with capacity exactly <= c
    dp = [0] * (W + 1)
    for i in range(len(weights)):
        w, v = weights[i], values[i]
        for c in range(W, w - 1, -1):      # descending => item used at most once
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[W]

if __name__ == '__main__':
    print(knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], 7))  # 9 (items w=3,4 -> v=4+5)
```
- **Complexity:** Time O(n*W), Space O(W)
- **Key insight / gotcha:** The descending capacity loop is the whole trick. Iterating **ascending** silently turns this into *unbounded* knapsack (item reused), a classic bug.
- **Follow-up:** "Reconstruct which items were chosen." Keep the 2-D table and backtrack: at `dp[i][c]`, if `dp[i][c] != dp[i-1][c]` item `i` was taken, move to `dp[i-1][c-w]`, else `dp[i-1][c]`.

### 2. Partition Equal Subset Sum  -  Medium
- **Problem:** Given an array of positive integers, decide whether it can be split into two subsets with equal sum.
- **Practice (free):** https://leetcode.com/problems/partition-equal-subset-sum/
- **Video (free):** https://neetcode.io/problems/partition-equal-subset-sum
- **Idea:** Total must be even; then it reduces to "is there a subset summing to total/2" — a 0/1 subset-feasibility knapsack.
```python
from typing import List

def canPartition(nums: List[int]) -> bool:
    total = sum(nums)
    if total % 2:                      # odd total can't split evenly
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True                       # empty subset hits sum 0
    for x in nums:
        for c in range(target, x - 1, -1):   # 0/1 => descending
            dp[c] = dp[c] or dp[c - x]
        if dp[target]:                 # early exit once reachable
            return True
    return dp[target]

if __name__ == '__main__':
    print(canPartition([1, 5, 11, 5]))  # True  -> {1,5,5} and {11}
    print(canPartition([1, 2, 3, 5]))   # False
```
- **Complexity:** Time O(n*total), Space O(total)
- **Key insight / gotcha:** Reframing "two equal halves" as "one subset == total/2" is the unlock. Don't forget the odd-total short-circuit, and skip work once `dp[target]` is True.
- **Follow-up:** "What if numbers can be negative or zero?" Then total/2 framing breaks; shift to an offset-based dp over the achievable-sum range, or handle zeros (they don't change reachability but inflate count problems).

### 3. Target Sum  -  Medium
- **Problem:** Assign a `+` or `-` to each number so the signed total equals `target`; count the number of such assignments.
- **Practice (free):** https://leetcode.com/problems/target-sum/
- **Video (free):** https://neetcode.io/problems/target-sum
- **Idea:** Let `P` = sum of `+` items. Then `P - (total - P) = target` => `P = (total + target) / 2`. Count subsets summing to `P` — a 0/1 **counting** knapsack.
```python
from typing import List

def findTargetSumWays(nums: List[int], target: int) -> int:
    total = sum(nums)
    # P must be a non-negative integer: (total + target) even and in range
    if (total + target) % 2 or abs(target) > total:
        return 0
    P = (total + target) // 2
    dp = [0] * (P + 1)
    dp[0] = 1                          # one way to make sum 0: take nothing
    for x in nums:
        for c in range(P, x - 1, -1):  # 0/1 counting => descending
            dp[c] += dp[c - x]
    return dp[P]

if __name__ == '__main__':
    print(findTargetSumWays([1, 1, 1, 1, 1], 3))  # 5
    print(findTargetSumWays([1], 1))              # 1
```
- **Complexity:** Time O(n*P), Space O(P)
- **Key insight / gotcha:** The `+`/`-` framing collapses into one subset-sum count via `P = (total+target)/2`. Guard the parity and range, and note **zeros** double the count (each zero can be + or -) — the dp handles this naturally because `dp[c] += dp[c]` when `x == 0`.
- **Follow-up:** "Return the actual assignments, not the count." That's exponential in the worst case; switch to DFS with memo on `(index, runningSum)` and backtrack to emit each valid sign vector.

### 4. Coin Change (unbounded min coins)  -  Medium
- **Problem:** Given coin denominations (each usable unlimited times) and an amount, return the fewest coins that sum to the amount, or `-1` if impossible.
- **Practice (free):** https://leetcode.com/problems/coin-change/
- **Video (free):** https://neetcode.io/problems/coin-change
- **Idea:** Unbounded knapsack minimizing count: `dp[c] = min over coins of dp[c-coin] + 1`. Iterate amount ascending so a coin can be reused.
```python
from typing import List

def coinChange(coins: List[int], amount: int) -> int:
    INF = amount + 1                   # sentinel larger than any real answer
    dp = [0] + [INF] * amount          # dp[c] = min coins to make c
    for c in range(1, amount + 1):
        for coin in coins:
            if coin <= c:
                dp[c] = min(dp[c], dp[c - coin] + 1)
    return dp[amount] if dp[amount] != INF else -1

if __name__ == '__main__':
    print(coinChange([1, 2, 5], 11))  # 3  -> 5+5+1
    print(coinChange([2], 3))         # -1
```
- **Complexity:** Time O(amount * #coins), Space O(amount)
- **Key insight / gotcha:** This is a min-optimization, so greedy (always take the biggest coin) is **wrong** in general — e.g. coins `[1,3,4]`, amount `6` is `3+3` (2 coins), greedy gives `4+1+1` (3). Use the sentinel `amount+1` so `dp[c-coin]+1` never falsely "wins".
- **Follow-up:** "Reconstruct the coin set used." Store a `parent[c]` = chosen coin when `dp[c]` improves, then walk `c -> c - parent[c]` until 0.

### 5. Coin Change II (number of ways)  -  Medium
- **Problem:** Count the number of distinct **combinations** of coins (order doesn't matter) that sum to the amount; each coin is usable unlimited times.
- **Practice (free):** https://leetcode.com/problems/coin-change-ii/
- **Video (free):** https://neetcode.io/problems/coin-change-ii
- **Idea:** Unbounded counting knapsack. Put the **coin loop outside** and amount loop inside so each combination is counted once (order ignored).
```python
from typing import List

def change(amount: int, coins: List[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1                          # one way to make 0: use no coins
    for coin in coins:                 # OUTER loop over coins => combinations
        for c in range(coin, amount + 1):   # ascending => coin reusable
            dp[c] += dp[c - coin]
    return dp[amount]

if __name__ == '__main__':
    print(change(5, [1, 2, 5]))  # 4  -> {5},{2,2,1},{2,1,1,1},{1x5}
    print(change(3, [2]))        # 0
```
- **Complexity:** Time O(amount * #coins), Space O(amount)
- **Key insight / gotcha:** **Loop order decides combinations vs permutations.** Coins outer = combinations (this problem). Amount outer = permutations (next problem). Swapping them is the single most common mistake on these two.
- **Follow-up:** "What if you also cap how many of each coin you may use?" That's bounded knapsack — handle each coin with a count loop, or binary-split the count into powers of two and run it as 0/1.

### 6. Combination Sum IV  -  Medium
- **Problem:** Count the number of ordered sequences (permutations count separately) of numbers from the array that sum to `target`; numbers reusable.
- **Practice (free):** https://leetcode.com/problems/combination-sum-iv/
- **Video (free):** https://neetcode.io/problems/combination-target-sum
- **Idea:** Counting knapsack but **target loop outside, numbers inside** — so `(1,3)` and `(3,1)` are counted as two distinct sequences (permutations).
```python
from typing import List

def combinationSum4(nums: List[int], target: int) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1                          # empty sequence sums to 0
    for c in range(1, target + 1):     # OUTER loop over target => permutations
        for x in nums:
            if x <= c:
                dp[c] += dp[c - x]
    return dp[target]

if __name__ == '__main__':
    print(combinationSum4([1, 2, 3], 4))  # 7 (order matters)
    print(combinationSum4([9], 3))        # 0
```
- **Complexity:** Time O(target * len(nums)), Space O(target)
- **Key insight / gotcha:** Despite the name "Combination", it counts **permutations** — that's exactly why the target loop is outer (mirror image of Coin Change II). Contrast the two side by side until the loop-order rule is reflex.
- **Follow-up:** "What if negative numbers are allowed and reuse is unlimited?" Then the count can be infinite (a +k and -k cycle), so the problem must bound sequence length; the unbounded dp no longer terminates without that cap.

### 7. Last Stone Weight II  -  Medium
- **Problem:** Each stone has a weight; repeatedly smash two stones (the difference remains). Return the smallest possible weight of the last remaining stone.
- **Practice (free):** https://leetcode.com/problems/last-stone-weight-ii/
- **Video (free):** https://neetcode.io/problems/last-stone-weight-ii
- **Idea:** Assigning each stone `+`/`-` and minimizing `|sum|` = partition stones into two groups with **minimal difference**. Find the largest subset sum `s <= total/2`; answer is `total - 2*s`.
```python
from typing import List

def lastStoneWeightII(stones: List[int]) -> int:
    total = sum(stones)
    half = total // 2
    dp = [False] * (half + 1)          # dp[s] = subset summing to s is reachable
    dp[0] = True
    for w in stones:
        for s in range(half, w - 1, -1):    # 0/1 feasibility => descending
            dp[s] = dp[s] or dp[s - w]
    best = max(s for s in range(half + 1) if dp[s])   # closest sum to total/2
    return total - 2 * best

if __name__ == '__main__':
    print(lastStoneWeightII([2, 7, 4, 1, 8, 1]))  # 1
    print(lastStoneWeightII([31, 26, 33, 21, 40]))  # 5
```
- **Complexity:** Time O(n * total), Space O(total)
- **Key insight / gotcha:** Smashing stones is equivalent to choosing signs, and minimizing `|S+ - S-|` means making one subset as close to `total/2` as possible. The answer is `total - 2*best`, never negative because `best <= total/2`.
- **Follow-up:** "Prove the smashing process can always realize the optimal partition." Inductively, any +/- sign assignment is achievable by a sequence of pairwise differences — you can always reproduce a target signed sum via the smash operations.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the 0/1 template (descending) and unbounded template (ascending) from memory
- [ ] 0/1 Knapsack concept (take/skip + descending loop) 🔴🟡🟢
- [ ] Partition Equal Subset Sum (reduce to subset == total/2) 🔴🟡🟢
- [ ] Target Sum (P = (total+target)/2, counting dp) 🔴🟡🟢
- [ ] Coin Change min (unbounded, ascending, sentinel) 🔴🟡🟢
- [ ] Coin Change II (coins outer = combinations) 🔴🟡🟢
- [ ] Combination Sum IV (target outer = permutations) 🔴🟡🟢
- [ ] Last Stone Weight II (min partition diff = total - 2*best) 🔴🟡🟢
- [ ] I never mix up combinations-vs-permutations loop order

## Resources
- **Free:** NeetCode roadmap 1-D DP section https://neetcode.io/roadmap ; takeUforward DP playlist (knapsack series) https://www.youtube.com/results?search_query=takeuforward+dp+knapsack+playlist ; LeetCode Dynamic Programming study plan https://leetcode.com/studyplan/dynamic-programming/
- **Paid (optional):** DesignGurus "Grokking Dynamic Programming for Coding Interviews" https://www.designgurus.io (free alternative: the NeetCode roadmap DP section above, which covers every problem in this file).

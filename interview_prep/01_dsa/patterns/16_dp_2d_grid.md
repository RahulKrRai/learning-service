# 16 - Dynamic Programming - 2D & Grid
> One-line: reach for this when the optimal answer over two sequences (or a 2D grid) is built from answers to smaller (i, j) prefixes/suffixes.

## When to use it (recognition triggers)
- The problem has **two strings/arrays** and you compare/align/transform one into the other (LCS, edit distance, subsequence counting, interleaving, regex/wildcard matching).
- You move through a **grid** with restricted moves (right/down, or 4-directional) and ask for count of paths, min/max path cost, or largest square/region.
- A brute-force recursion has **two indices** that shrink, and the same `(i, j)` pair recurs -> memoize into a 2D table.
- The answer at `dp[i][j]` depends only on a **constant number of neighbors** (`dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]`), which screams 2D DP and usually allows **rolling-array** space optimization.
- You're asked for an "is it possible" boolean, a "how many ways" count, or a "min/max cost" over a 2D state space.

## Mental model
- Define a 2D state `dp[i][j]` = the answer for the first `i` characters of A and first `j` characters of B (or for the subgrid ending at cell `(i, j)`). The art is picking what `(i, j)` means so the recurrence is local.
- The transition asks "what happens at the boundary cell?" In string DP that's "do A[i-1] and B[j-1] match?"; matching lets you consume both and add `dp[i-1][j-1]`, mismatch forces you to pay a cost or branch.
- Base cases live on **row 0 and column 0** (empty prefix of one string, or the grid edge) — get these right and the interior fills mechanically.
- Iteration order must respect dependencies: if `dp[i][j]` needs smaller `i` and `j`, fill rows top-to-bottom, columns left-to-right. Grid problems with 4-directional moves (Longest Increasing Path) break this ordering, so use memoized DFS instead of bottom-up.
- Most 2D DP that only looks one row back collapses to **O(width) space** with a rolling 1D array (sometimes two variables for the diagonal).

## Reusable template(s)
```python
# Generic 2D string DP skeleton (LCS-style).
# dp[i][j] = answer for a[:i] vs b[:j]; rows/cols 0 = empty prefixes.
def two_string_dp(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Base cases: fill dp[0][*] and dp[*][0] here if non-zero.

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1          # consume both on match
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # branch on mismatch
    return dp[n][m]


# Generic grid DP with memoized DFS (use when moves aren't monotonic).
from functools import lru_cache
def grid_dfs(grid):
    R, C = len(grid), len(grid[0])

    @lru_cache(maxsize=None)
    def best(r, c):
        ans = 1  # base contribution of this cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] > grid[r][c]:
                ans = max(ans, 1 + best(nr, nc))
        return ans

    return max(best(r, c) for r in range(R) for c in range(C))
```

## Complexity profile
- **Time:** almost always `O(n * m)` (fill every cell once with O(1)/O(neighbors) work). Grid DFS variants are `O(R * C)` with memoization vs exponential without.
- **Space:** `O(n * m)` for the full table; usually reducible to `O(min(n, m))` with a rolling row, or `O(1)` extra for some grid problems by mutating in place.
- **Brute force you're beating:** naive recursion branches into both "skip A" and "skip B" at every step -> `O(2^(n+m))`. Memoization on the `(i, j)` pair is the whole win.

## Curated problems (easy -> hard)

### 1. Unique Paths  -  Medium
- **Problem:** Count the distinct paths a robot can take from the top-left to the bottom-right of an `m x n` grid moving only right or down.
- **Practice (free):** https://leetcode.com/problems/unique-paths/
- **Video (free):** https://neetcode.io/problems/count-paths
- **Idea:** Ways to reach a cell = ways from the cell above + ways from the cell to the left; edges have exactly one way.
```python
def uniquePaths(m: int, n: int) -> int:
    # row[j] = number of ways to reach cell (i, j) for the current row i.
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]  # ways from above (old row[j]) + from left (row[j-1])
    return row[n - 1]
```
- **Complexity:** Time O(m*n), Space O(n)
- **Key insight / gotcha:** The closed form is the binomial `C(m+n-2, m-1)`, but the rolling-array DP is what they want you to derive; initialize the first row/column to 1, not 0.
- **Follow-up:** "Now there are obstacles" (Unique Paths II) — set `dp[j] = 0` whenever the cell is blocked, keeping the same rolling sweep.

### 2. Minimum Path Sum  -  Medium
- **Problem:** Given a grid of non-negative numbers, find the minimum sum of values along a path from top-left to bottom-right moving only right or down.
- **Practice (free):** https://leetcode.com/problems/minimum-path-sum/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+minimum+path+sum
- **Idea:** Min cost to reach a cell = its own value plus the cheaper of the cell above or to the left.
```python
def minPathSum(grid: list[list[int]]) -> int:
    R, C = len(grid), len(grid[0])
    dp = grid[0][:]  # first row: only reachable from the left
    for c in range(1, C):
        dp[c] += dp[c - 1]
    for r in range(1, R):
        dp[0] += grid[r][0]  # first column: only from above
        for c in range(1, C):
            dp[c] = grid[r][c] + min(dp[c], dp[c - 1])  # dp[c] is "above", dp[c-1] is "left"
    return dp[C - 1]
```
- **Complexity:** Time O(R*C), Space O(C)
- **Key insight / gotcha:** Handle the first row and first column separately — they have only one predecessor, and reading a non-existent neighbor as 0 silently corrupts the answer.
- **Follow-up:** "Reconstruct the actual path" — store choices or backtrack from `(R-1, C-1)` choosing the smaller predecessor; this needs the full 2D table, so drop the rolling-array trick.

### 3. Longest Common Subsequence (with path reconstruction)  -  Medium
- **Problem:** Find the length of the longest subsequence present in both strings (characters in order but not necessarily contiguous).
- **Practice (free):** https://leetcode.com/problems/longest-common-subsequence/
- **Video (free):** https://neetcode.io/problems/longest-common-subsequence
- **Idea:** On a character match, both prefixes shrink and length increases by 1; on a mismatch, take the better of dropping one character from either string.
```python
def longestCommonSubsequence(a: str, b: str) -> int:
    n, m = len(a), len(b)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[m]


def lcs_string(a: str, b: str) -> str:
    # Full table needed to walk back and rebuild the actual subsequence.
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] \
                else max(dp[i - 1][j], dp[i][j - 1])
    i, j, out = n, m, []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1]); i -= 1; j -= 1   # this char is in the LCS
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1                                  # move toward the larger neighbor
        else:
            j -= 1
    return ''.join(reversed(out))
```
- **Complexity:** Time O(n*m), Space O(m) for the length, O(n*m) if you must reconstruct.
- **Key insight / gotcha:** This is the parent of Edit Distance and Distinct Subsequences. **Path reconstruction note:** you cannot reconstruct from a rolling 1D array — keep the full table and backtrack from `dp[n][m]`, stepping diagonally on matches and toward the larger neighbor on mismatches.
- **Follow-up:** "Shortest Common Supersequence" — its length is `n + m - LCS(a, b)`, and you interleave using the same backtracking walk.

### 4. Edit Distance  -  Hard
- **Problem:** Find the minimum number of single-character insertions, deletions, or substitutions to convert string `word1` into `word2`.
- **Practice (free):** https://leetcode.com/problems/edit-distance/
- **Video (free):** https://neetcode.io/problems/edit-distance
- **Idea:** If the last characters match, no cost — recurse on both prefixes; otherwise pay 1 plus the cheapest of insert (`dp[i][j-1]`), delete (`dp[i-1][j]`), or replace (`dp[i-1][j-1]`).
```python
def minDistance(w1: str, w2: str) -> int:
    n, m = len(w1), len(w2)
    prev = list(range(m + 1))  # dp[0][j] = j insertions to build w2[:j] from empty
    for i in range(1, n + 1):
        cur = [i] + [0] * m    # dp[i][0] = i deletions
        for j in range(1, m + 1):
            if w1[i - 1] == w2[j - 1]:
                cur[j] = prev[j - 1]               # free match
            else:
                cur[j] = 1 + min(prev[j],          # delete from w1
                                 cur[j - 1],       # insert into w1
                                 prev[j - 1])      # replace
        prev = cur
    return prev[m]
```
- **Complexity:** Time O(n*m), Space O(m)
- **Key insight / gotcha:** The base row/column are **not** zeros — `dp[i][0] = i` and `dp[0][j] = j` because turning a length-`i` string into the empty string costs `i` deletions. Forgetting this is the classic bug.
- **Follow-up:** "Operations have different costs (e.g., replace costs 2)" — just swap the literal `1` for the per-operation cost in the `min`, the structure is unchanged.

### 5. Distinct Subsequences  -  Hard
- **Problem:** Count how many distinct subsequences of string `s` equal string `t`.
- **Practice (free):** https://leetcode.com/problems/distinct-subsequences/
- **Video (free):** https://neetcode.io/problems/distinct-subsequences
- **Idea:** `dp[i][j]` = ways to form `t[:j]` from `s[:i]`. Always include the option of skipping `s[i-1]`; if `s[i-1] == t[j-1]` you may also match it, adding `dp[i-1][j-1]`.
```python
def numDistinct(s: str, t: str) -> int:
    n, m = len(s), len(t)
    if m > n:
        return 0
    # dp[j] = ways to form t[:j]; empty t has exactly one matching (the empty pick).
    dp = [1] + [0] * m
    for i in range(1, n + 1):
        # iterate j downward so dp[j-1] still refers to the previous row
        for j in range(min(i, m), 0, -1):
            if s[i - 1] == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[m]
```
- **Complexity:** Time O(n*m), Space O(m)
- **Key insight / gotcha:** When rolling to 1D you **must iterate `j` from high to low**, exactly like 0/1 knapsack, so `dp[j-1]` is the value from the previous outer iteration (the old row), not one you just overwrote.
- **Follow-up:** "What if you only need it modulo 1e9+7 because counts overflow?" — In Python integers are unbounded, but mention you'd take the mod after each `+=` in languages with fixed-width ints.

### 6. Interleaving String  -  Medium
- **Problem:** Decide whether `s3` can be formed by interleaving `s1` and `s2` while preserving the relative order of characters in each.
- **Practice (free):** https://leetcode.com/problems/interleaving-string/
- **Video (free):** https://neetcode.io/problems/interleaving-string
- **Idea:** `dp[i][j]` = can `s1[:i]` and `s2[:j]` interleave to `s3[:i+j]`? You reach it if the matching previous state holds AND the next `s3` char equals the consumed `s1` or `s2` char.
```python
def isInterleave(s1: str, s2: str, s3: str) -> bool:
    n, m = len(s1), len(s2)
    if n + m != len(s3):
        return False
    dp = [False] * (m + 1)
    dp[0] = True
    for j in range(1, m + 1):                      # first row: use only s2
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
    for i in range(1, n + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]   # first column: use only s1
        for j in range(1, m + 1):
            from_s1 = dp[j] and s1[i - 1] == s3[i + j - 1]       # dp[j] is the "above" cell
            from_s2 = dp[j - 1] and s2[j - 1] == s3[i + j - 1]   # dp[j-1] is the "left" cell
            dp[j] = from_s1 or from_s2
    return dp[m]
```
- **Complexity:** Time O(n*m), Space O(m)
- **Key insight / gotcha:** The early length check `n + m == len(s3)` is mandatory; without it the `s3` index `i + j - 1` goes out of range. A greedy two-pointer is wrong (e.g., `s1="aa", s2="ab", s3="aaba"`) — you genuinely need the 2D state.
- **Follow-up:** "Recover the actual interleaving" — backtrack from `dp[n][m]`, at each step checking which predecessor was True and emitting an L/R move.

### 7. Best Time to Buy and Sell Stock with Cooldown  -  Medium
- **Problem:** Maximize profit from unlimited buy/sell transactions on a price array, but you must skip one day (cooldown) after every sell.
- **Practice (free):** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/
- **Video (free):** https://neetcode.io/problems/buy-and-sell-crypto-with-cooldown
- **Idea:** A small **state-machine DP**: track best profit in three states each day — `hold` (own a share), `sold` (just sold, must cool down), `rest` (idle and free to buy). It's 2D in spirit (day x state) but collapses to a few rolling variables.
```python
def maxProfit(prices: list[int]) -> int:
    hold = float('-inf')   # best profit while currently holding a share
    sold = 0               # best profit on a day we just sold (forces cooldown next)
    rest = 0               # best profit while idle and allowed to buy
    for p in prices:
        prev_sold = sold
        sold = hold + p                 # sell what we held today
        hold = max(hold, rest - p)      # keep holding, or buy today (only from rest)
        rest = max(rest, prev_sold)     # stay idle, or arrive here after a sale
    return max(sold, rest)              # never end while still holding
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** You can only **buy from `rest`**, never directly after a sell — that single edge enforces the cooldown. Capture `prev_sold` before overwriting `sold`, since `rest` depends on yesterday's `sold`.
- **Follow-up:** "Add a fixed transaction fee per trade" — subtract the fee inside the `sold = hold + p - fee` transition; the cooldown variant and fee variant share this exact 3-state skeleton.

### 8. Maximal Square  -  Medium
- **Problem:** In a binary matrix, find the area of the largest square composed entirely of 1s.
- **Practice (free):** https://leetcode.com/problems/maximal-square/
- **Video (free):** https://neetcode.io/problems/maximal-square
- **Idea:** `dp[i][j]` = side length of the largest all-1 square whose **bottom-right corner** is `(i, j)`. If the cell is 1, it's `1 + min` of the three squares above, left, and diagonal.
```python
def maximalSquare(matrix: list[list[str]]) -> int:
    R, C = len(matrix), len(matrix[0])
    dp = [0] * (C + 1)   # rolling row, padded so j-1 / above are always valid
    best = 0
    for i in range(1, R + 1):
        diag = 0         # dp[i-1][j-1] from the previous row, before overwrite
        for j in range(1, C + 1):
            up = dp[j]                    # dp[i-1][j]
            if matrix[i - 1][j - 1] == '1':
                dp[j] = 1 + min(dp[j - 1], up, diag)  # left, above, diagonal
                best = max(best, dp[j])
            else:
                dp[j] = 0
            diag = up                     # this row's "up" is next column's diagonal
    return best * best
```
- **Complexity:** Time O(R*C), Space O(C)
- **Key insight / gotcha:** The square is bounded by its **weakest** of the three neighbors, hence `min` (not `max`); a single 0 in any of them caps the side. Return area = side², not the side.
- **Follow-up:** "Largest rectangle of 1s instead of square" — that's a different technique (per-row histogram + largest-rectangle-in-histogram via monotonic stack), not this `min`-of-neighbors recurrence.

### 9. Longest Increasing Path in a Matrix  -  Hard
- **Problem:** Find the length of the longest strictly increasing path in a matrix, moving in the four cardinal directions.
- **Practice (free):** https://leetcode.com/problems/longest-increasing-path-in-a-matrix/
- **Video (free):** https://neetcode.io/problems/longest-increasing-path-in-matrix
- **Idea:** Because strictly increasing moves can never revisit a cell, the grid is a DAG. Memoized DFS from each cell caches the longest increasing path starting there.
```python
from functools import lru_cache
def longestIncreasingPath(matrix: list[list[int]]) -> int:
    R, C = len(matrix), len(matrix[0])

    @lru_cache(maxsize=None)
    def dfs(r, c):
        best = 1  # the cell itself
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + dfs(nr, nc))
        return best

    return max(dfs(r, c) for r in range(R) for c in range(C))
```
- **Complexity:** Time O(R*C) (each cell computed once, O(4) work), Space O(R*C) for the memo and recursion stack.
- **Key insight / gotcha:** Moves are not monotone (you can go any direction), so bottom-up row-by-row ordering doesn't apply — memoized DFS is the natural fit. **Strictly** increasing guarantees no cycles, so you don't need a visited set within one DFS.
- **Follow-up:** "Avoid recursion depth limits / interviewer bans recursion" — topologically process cells by increasing value, or peel cells in increasing-value order (a Kahn's-style longest-path-on-DAG), giving the same O(R*C).

### 10. Regular Expression Matching  -  Hard
- **Problem:** Implement regex matching for `.` (any single char) and `*` (zero or more of the preceding element) so that the pattern must match the entire input string.
- **Practice (free):** https://leetcode.com/problems/regular-expression-matching/
- **Video (free):** https://neetcode.io/problems/regular-expression-matching
- **Idea:** `dp[i][j]` = does `s[:i]` match `p[:j]`? A `*` means "zero occurrences" (`dp[i][j-2]`) OR "one more occurrence" if the char before `*` matches `s[i-1]` (`dp[i-1][j]`). A normal/`.` char consumes one from each.
```python
def isMatch(s: str, p: str) -> bool:
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    # empty string can match patterns like a*, a*b*, .* (each star kills its pair)
    for j in range(2, m + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == '*':
                # zero of the preceding element
                dp[i][j] = dp[i][j - 2]
                # one more of it, if the preceding pattern char matches s[i-1]
                if p[j - 2] == s[i - 1] or p[j - 2] == '.':
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            elif p[j - 1] == s[i - 1] or p[j - 1] == '.':
                dp[i][j] = dp[i - 1][j - 1]
    return dp[n][m]
```
- **Complexity:** Time O(n*m), Space O(n*m) (reducible to O(m) with two rows).
- **Key insight / gotcha:** A `*` always refers to the **pair** `p[j-2]p[j-1]`, so its "zero" branch is `dp[i][j-2]` (skip both chars). The empty-string initialization of the first row (`a*`, `.*` etc.) is the most-missed base case and breaks half of submissions.
- **Follow-up:** "Wildcard Matching where `*` matches any sequence and `?` matches any single char (LeetCode 44)" — simpler recurrence (`*` -> `dp[i-1][j] or dp[i][j-1]`); note the `*` semantics differ from regex and many people conflate the two.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the template from memory
- [ ] Unique Paths — rolling array + obstacle variant 🔴/🟡/🟢
- [ ] Minimum Path Sum — edge handling + path reconstruction 🔴/🟡/🟢
- [ ] Longest Common Subsequence — length AND backtracking the string 🔴/🟡/🟢
- [ ] Edit Distance — non-zero base row/column 🔴/🟡/🟢
- [ ] Distinct Subsequences — 1D rolling with reverse-j sweep 🔴/🟡/🟢
- [ ] Interleaving String — why greedy fails, length guard 🔴/🟡/🟢
- [ ] Stock with Cooldown — 3-state machine, buy only from rest 🔴/🟡/🟢
- [ ] Maximal Square — min-of-three neighbors, area = side² 🔴/🟡/🟢
- [ ] Longest Increasing Path — memoized DFS on a DAG 🔴/🟡/🟢
- [ ] Regular Expression Matching — `*` pairs + empty-row base case 🔴/🟡/🟢

## Resources
- **Free:** NeetCode 2-D DP roadmap section — https://neetcode.io/roadmap (the "2-D Dynamic Programming" group covers Unique Paths, LCS, Edit Distance, Distinct Subsequences, Interleaving String, Regex Matching).
- **Free:** LeetCode Dynamic Programming Study Plan (explore card) — https://leetcode.com/study-plan/dynamic-programming/
- **Free:** takeUforward / Striver "DP on Grids" and "DP on Strings" playlists — https://www.youtube.com/results?search_query=striver+dp+on+strings+lcs
- **Paid (optional):** DesignGurus "Grokking Dynamic Programming for Coding Interviews" — https://www.designgurus.io (free alternative: the NeetCode 2-D DP roadmap section above, which covers the same problem set with video walkthroughs).

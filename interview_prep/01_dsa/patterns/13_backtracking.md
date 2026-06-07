# 13 - Backtracking
> One-line: when you must enumerate/construct all valid combinations, permutations, or arrangements by making a choice, recursing, then undoing it.

## When to use it (recognition triggers)
- The problem asks for **all** subsets / combinations / permutations / partitions / arrangements (not just a count or a single answer).
- You build a candidate **incrementally** and can **prune** the moment a partial candidate becomes invalid ("if it can't lead to a solution, stop").
- The output size itself is exponential/factorial (2^n subsets, n! permutations) — you're expected to enumerate, not optimize away the explosion.
- Phrases like "find all ways", "generate every valid ...", "place N pieces so that no two conflict", "split the string so each piece satisfies P".
- A grid/board search where you explore neighbors and must **mark and unmark** visited cells.

## Mental model
- Backtracking is DFS over a **decision tree**. At each node you pick one of several choices, recurse into a smaller subproblem, then **undo** the choice (pop/unmark) so the next branch starts clean. The "undo" is what makes one shared mutable `path` correct.
- The skeleton is always the same three parts: a **base case** (record a finished candidate), a **loop over choices**, and a **choose / recurse / un-choose** body.
- **Pruning** is the whole game: skip choices that violate a constraint, sort then break early when remaining options can't help, and skip duplicates so you don't generate the same answer twice.
- Two recurring shapes: **combinations/subsets** pass a `start` index so each element is only considered once and order doesn't matter; **permutations** use a `used[]` flag (or swap) because order matters and every position can draw from the whole set.
- To skip duplicates from a multiset: **sort first**, then within one recursion level skip an element equal to its predecessor (`nums[i] == nums[i-1]`) unless the predecessor was just used on the current path.

## Reusable template(s)
```python
# ---- Subsets / Combinations: 'start' index, order doesn't matter ----
def combinations(nums):
    res, path = [], []
    def backtrack(start):
        res.append(path[:])                 # record current subset (or guard with a base case)
        for i in range(start, len(nums)):   # only look forward => no reorderings
            # if duplicates: if i > start and nums[i] == nums[i-1]: continue
            path.append(nums[i])            # choose
            backtrack(i + 1)                # recurse (i, not i+1, if reuse allowed)
            path.pop()                      # un-choose (backtrack)
    backtrack(0)
    return res

# ---- Permutations: 'used[]' flag, order matters ----
def permutations(nums):
    res, path = [], []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            res.append(path[:]); return
        for i in range(len(nums)):
            if used[i]:
                continue
            # if duplicates: if i > 0 and nums[i]==nums[i-1] and not used[i-1]: continue
            used[i] = True; path.append(nums[i])   # choose
            backtrack()                             # recurse
            path.pop(); used[i] = False             # un-choose
    backtrack()
    return res
```

## Complexity profile
- **Subsets:** O(n · 2^n) time (2^n subsets, O(n) to copy each), O(n) extra space for the path.
- **Permutations:** O(n · n!) time, O(n) recursion depth.
- **Combination Sum family:** worst case O(2^t) or O(n^(t/min)) shaped by target/candidates; sorting + pruning dramatically cuts the constant.
- You are **not** beating brute force here — the answer set is exponential. Backtracking *is* the efficient enumeration; the win is pruning dead branches early instead of generating-then-filtering.

## Curated problems (easy -> hard)

### 1. Subsets  -  Medium
- **Problem:** Given an array of distinct integers, return all possible subsets (the power set), without duplicate subsets.
- **Practice (free):** https://leetcode.com/problems/subsets/
- **Video (free):** https://neetcode.io/problems/subsets
- **Idea:** DFS with a `start` index; at every node append a copy of the current path (every prefix is itself a valid subset), then extend by each later element.
```python
def subsets(nums):
    res, path = [], []
    def backtrack(start):
        res.append(path[:])                # every node is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])           # include nums[i]
            backtrack(i + 1)               # move forward
            path.pop()                     # exclude it again
    backtrack(0)
    return res
```
- **Complexity:** Time O(n · 2^n), Space O(n) recursion (plus output).
- **Key insight / gotcha:** Append `path[:]` (a copy) — appending `path` itself stores a reference that you later mutate, so every entry would end up empty.
- **Follow-up:** "Do it iteratively." Start with `[[]]` and for each num, append num to every existing subset: `res += [s + [num] for s in res]`.

### 2. Subsets II  -  Medium
- **Problem:** Given an array that may contain duplicates, return all possible subsets with no duplicate subsets in the result.
- **Practice (free):** https://leetcode.com/problems/subsets-ii/
- **Video (free):** https://neetcode.io/problems/subsets-ii
- **Idea:** Sort so equal values are adjacent; within a single recursion level, skip a value equal to its predecessor so each distinct multiset prefix is generated once.
```python
def subsetsWithDup(nums):
    nums.sort()
    res, path = [], []
    def backtrack(start):
        res.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:   # skip dup at this level
                continue
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return res
```
- **Complexity:** Time O(n · 2^n), Space O(n) recursion.
- **Key insight / gotcha:** The skip condition is `i > start`, not `i > 0` — you must allow the first occurrence at each level; you only suppress repeats that start a fresh branch with the same value.
- **Follow-up:** "Why sort?" Without sorting, equal elements aren't adjacent, so the `nums[i]==nums[i-1]` test can't reliably detect duplicates at a level.

### 3. Combination Sum  -  Medium
- **Problem:** Given distinct candidates and a target, return all unique combinations where the chosen numbers sum to target; the same number may be used unlimited times.
- **Practice (free):** https://leetcode.com/problems/combination-sum/
- **Video (free):** https://neetcode.io/problems/combination-target-sum
- **Idea:** DFS with a `start` index but recurse on `i` (not `i+1`) to allow reuse; sort and break when a candidate already exceeds the remaining target.
```python
def combinationSum(candidates, target):
    candidates.sort()
    res, path = [], []
    def backtrack(start, remain):
        if remain == 0:
            res.append(path[:]); return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:     # sorted => all later are too big
                break
            path.append(candidates[i])
            backtrack(i, remain - candidates[i])   # i, not i+1 => reuse allowed
            path.pop()
    backtrack(0, target)
    return res
```
- **Complexity:** Time O(n^(target/min)) worst case, Space O(target/min) depth.
- **Key insight / gotcha:** Passing `i` (not `i+1`) permits reusing the same element; passing `start` (so we never look backward) prevents permutations of the same combination.
- **Follow-up:** "Each number at most once?" Recurse on `i+1` and that's exactly Combination Sum II (minus the duplicate handling).

### 4. Combination Sum II  -  Medium
- **Problem:** Given candidates (may contain duplicates) and a target, return all unique combinations summing to target where each number is used at most once.
- **Practice (free):** https://leetcode.com/problems/combination-sum-ii/
- **Video (free):** https://neetcode.io/problems/combination-target-sum-ii
- **Idea:** Sort; recurse on `i+1` (no reuse); skip duplicates at the same level with the `i > start` guard, and break early when the value exceeds the remaining target.
```python
def combinationSum2(candidates, target):
    candidates.sort()
    res, path = [], []
    def backtrack(start, remain):
        if remain == 0:
            res.append(path[:]); return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:   # skip dup at level
                continue
            if candidates[i] > remain:     # prune the rest (sorted)
                break
            path.append(candidates[i])
            backtrack(i + 1, remain - candidates[i])   # no reuse
            path.pop()
    backtrack(0, target)
    return res
```
- **Complexity:** Time O(2^n) worst case, Space O(n) depth.
- **Key insight / gotcha:** Two distinct mechanisms combine here: `i+1` enforces "use each index once", and the `i > start` skip enforces "don't emit duplicate combinations from equal values".
- **Follow-up:** "What if target can be negative or candidates zero?" Constraints exclude zeros/negatives; with zeros the unlimited-reuse variants would loop forever, which is why the `>` prune assumes positive values.

### 5. Permutations  -  Medium
- **Problem:** Given an array of distinct integers, return all possible orderings (permutations).
- **Practice (free):** https://leetcode.com/problems/permutations/
- **Video (free):** https://neetcode.io/problems/permutations
- **Idea:** Track a `used[]` flag; at each position try every unused element, recurse, then unmark — order matters so we always scan from index 0.
```python
def permute(nums):
    res, path = [], []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            res.append(path[:]); return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True; path.append(nums[i])
            backtrack()
            path.pop(); used[i] = False
    backtrack()
    return res
```
- **Complexity:** Time O(n · n!), Space O(n) depth.
- **Key insight / gotcha:** Permutations differ from subsets/combinations by scanning from `0` every level (with `used[]`) instead of from a `start` index — that's what reintroduces ordering.
- **Follow-up:** "Avoid the `used[]` array." Swap-in-place: for `i` from `start..n-1`, swap `nums[start], nums[i]`, recurse on `start+1`, swap back — O(1) extra space.

### 6. Permutations II  -  Medium
- **Problem:** Given a collection that may contain duplicates, return all unique permutations.
- **Practice (free):** https://leetcode.com/problems/permutations-ii/
- **Video (free):** https://neetcode.io/problems/permutations-ii
- **Idea:** Sort; use `used[]`; skip an element equal to its predecessor when the predecessor is **not** currently used — that forces equal values to be picked in left-to-right order, killing duplicate orderings.
```python
def permuteUnique(nums):
    nums.sort()
    res, path = [], []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            res.append(path[:]); return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                   # predecessor free => this is a duplicate branch
            used[i] = True; path.append(nums[i])
            backtrack()
            path.pop(); used[i] = False
    backtrack()
    return res
```
- **Complexity:** Time O(n · n!) worst case (far less with duplicates), Space O(n) depth.
- **Key insight / gotcha:** The condition is `not used[i-1]`. If the previous equal element *is* used, we're deeper in a valid branch; only when it's *free* would picking `nums[i]` first produce a mirror duplicate.
- **Follow-up:** "Why does `not used[i-1]` work and `used[i-1]` doesn't?" Both deduplicate, but `not used[i-1]` is the canonical convention that's easier to reason about; either is acceptable if applied consistently.

### 7. Letter Combinations of a Phone Number  -  Medium
- **Problem:** Given a string of digits 2-9, return all letter combinations the number could spell on a phone keypad.
- **Practice (free):** https://leetcode.com/problems/letter-combinations-of-a-phone-number/
- **Video (free):** https://neetcode.io/problems/combinations-of-a-phone-number
- **Idea:** One recursion level per digit; iterate that digit's letters, append, recurse to the next index, pop.
```python
def letterCombinations(digits):
    if not digits:
        return []
    keys = {'2':'abc','3':'def','4':'ghi','5':'jkl',
            '6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    res, path = [], []
    def backtrack(idx):
        if idx == len(digits):
            res.append(''.join(path)); return
        for ch in keys[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1)
            path.pop()
    backtrack(0)
    return res
```
- **Complexity:** Time O(4^n · n) (n = #digits), Space O(n) depth.
- **Key insight / gotcha:** Guard the empty input up front — `""` should return `[]`, not `[""]`, which a naive base case would produce.
- **Follow-up:** "Iterative?" BFS/product: start with `[""]` and for each digit replace the frontier with `[prefix + ch ...]`; or just `itertools.product(*[keys[d] for d in digits])`.

### 8. Generate Parentheses  -  Medium
- **Problem:** Given n pairs of parentheses, generate all combinations of well-formed parentheses.
- **Practice (free):** https://leetcode.com/problems/generate-parentheses/
- **Video (free):** https://neetcode.io/problems/generate-parentheses
- **Idea:** Track counts of open and close used; you may add `(` while `open < n`, and `)` only while `close < open` (keeps the prefix valid by construction).
```python
def generateParenthesis(n):
    res, path = [], []
    def backtrack(open_c, close_c):
        if len(path) == 2 * n:
            res.append(''.join(path)); return
        if open_c < n:                     # can still open
            path.append('('); backtrack(open_c + 1, close_c); path.pop()
        if close_c < open_c:               # can close only if an open is unmatched
            path.append(')'); backtrack(open_c, close_c + 1); path.pop()
    backtrack(0, 0)
    return res
```
- **Complexity:** Time O(4^n / sqrt(n)) (the nth Catalan number), Space O(n) depth.
- **Key insight / gotcha:** The constraint `close_c < open_c` is the entire pruning strategy — it guarantees every prefix is valid, so you never generate-then-filter.
- **Follow-up:** "How many results for n?" The Catalan number C(n) = (2n)! / ((n+1)! n!); useful for sanity-checking output size.

### 9. Palindrome Partitioning  -  Medium
- **Problem:** Given a string, partition it so every substring is a palindrome, and return all such partitionings.
- **Practice (free):** https://leetcode.com/problems/palindrome-partitioning/
- **Video (free):** https://neetcode.io/problems/palindrome-partitioning
- **Idea:** At index `start`, try every cut `start..end`; if `s[start:end+1]` is a palindrome, take it and recurse from `end+1` — `start` advancing is the decision variable.
```python
def partition(s):
    res, path = [], []
    def is_pal(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1; r -= 1
        return True
    def backtrack(start):
        if start == len(s):
            res.append(path[:]); return
        for end in range(start, len(s)):
            if is_pal(start, end):         # prune: only recurse on valid palindromic prefixes
                path.append(s[start:end + 1])
                backtrack(end + 1)
                path.pop()
    backtrack(0)
    return res
```
- **Complexity:** Time O(n · 2^n) (2^n cut sets, O(n) palindrome check/copy), Space O(n) depth.
- **Key insight / gotcha:** The pruning is checking the palindrome *before* recursing — that's what prevents exploring invalid partitions; without it you'd enumerate all 2^(n-1) cut sets.
- **Follow-up:** "Speed up the checks." Precompute a DP table `pal[i][j]` of palindrome-ness in O(n^2) so each `is_pal` lookup is O(1).

### 10. Word Search  -  Medium
- **Problem:** Given an m×n grid of characters and a word, return true if the word exists via sequentially adjacent (horizontally/vertically) cells, each used at most once.
- **Practice (free):** https://leetcode.com/problems/word-search/
- **Video (free):** https://neetcode.io/problems/word-search
- **Idea:** DFS from every cell; match characters one by one, mark the cell visited (mutate the board), explore 4 neighbors, then restore — backtracking on a grid.
```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def dfs(r, c, k):
        if k == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[k]:
            return False
        tmp, board[r][c] = board[r][c], '#'     # mark visited
        found = (dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1) or
                 dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1))
        board[r][c] = tmp                        # restore (backtrack)
        return found
    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False
```
- **Complexity:** Time O(m·n·4^L) (L = word length), Space O(L) recursion.
- **Key insight / gotcha:** Mark-and-restore in place avoids a separate `visited` set; just remember to restore on **every** return path or you'll corrupt the board for the next start cell.
- **Follow-up:** "Many words to search (Word Search II)." Build a Trie of all words and DFS once per cell against the Trie, pruning whole branches that no word follows.

### 11. N-Queens  -  Hard
- **Problem:** Place n queens on an n×n board so no two attack each other (no shared row, column, or diagonal); return all distinct solutions.
- **Practice (free):** https://leetcode.com/problems/n-queens/
- **Video (free):** https://neetcode.io/problems/n-queens
- **Idea:** Place one queen per row; track occupied columns and both diagonals (`r-c` and `r+c`) in sets for O(1) conflict checks; recurse row by row, undoing on backtrack.
```python
def solveNQueens(n):
    res = []
    cols, diag1, diag2 = set(), set(), set()   # diag1: r-c, diag2: r+c
    board = [['.'] * n for _ in range(n)]
    def backtrack(r):
        if r == n:
            res.append([''.join(row) for row in board]); return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue                       # prune attacked squares
            cols.add(c); diag1.add(r - c); diag2.add(r + c); board[r][c] = 'Q'
            backtrack(r + 1)
            cols.remove(c); diag1.remove(r - c); diag2.remove(r + c); board[r][c] = '.'
    backtrack(0)
    return res
```
- **Complexity:** Time O(n!) (bounded by valid placements, far below n^n), Space O(n) for the sets + board.
- **Key insight / gotcha:** Each cell on a "/" diagonal shares the same `r+c`, and each "\" diagonal shares the same `r-c` — those two identities turn diagonal checks into O(1) set lookups.
- **Follow-up:** "Just count solutions (N-Queens II)." Same recursion, increment a counter instead of building boards; bitmasks for `cols/diag1/diag2` make it noticeably faster.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the subsets template (start index) from memory
- [ ] I can write the permutations template (used[]) from memory
- [ ] I can state the duplicate-skip rule for combinations vs permutations
- [ ] Subsets — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Subsets II — 🔴 / 🟡 / 🟢
- [ ] Combination Sum — 🔴 / 🟡 / 🟢
- [ ] Combination Sum II — 🔴 / 🟡 / 🟢
- [ ] Permutations — 🔴 / 🟡 / 🟢
- [ ] Permutations II — 🔴 / 🟡 / 🟢
- [ ] Letter Combinations — 🔴 / 🟡 / 🟢
- [ ] Generate Parentheses — 🔴 / 🟡 / 🟢
- [ ] Palindrome Partitioning — 🔴 / 🟡 / 🟢
- [ ] Word Search — 🔴 / 🟡 / 🟢
- [ ] N-Queens — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap, Backtracking section — https://neetcode.io/roadmap ; LeetCode "Recursion II" explore card — https://leetcode.com/explore/learn/card/recursion-ii/ ; takeUforward/Striver recursion + backtracking series — https://www.youtube.com/results?search_query=striver+backtracking+playlist
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Subsets & Backtracking patterns) — https://www.designgurus.io (free alternative: the NeetCode roadmap section above covers the same patterns with video).

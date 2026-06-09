# 20 - Matrix & Grid Manipulation
> One-line: when the input is a 2D array and the task is to traverse, transform, rotate, or query it — usually in-place — by reasoning about indices, layers, direction vectors, and prefix sums.

> **HIGH-FREQUENCY pattern.** Asked everywhere, especially Google and Amazon. Spiral Matrix, Rotate Image, and Set Matrix Zeroes are perennial phone-screen / onsite staples. The hard part is rarely the algorithm — it's index bookkeeping done cleanly under pressure and the "do it in O(1) space / in place" follow-up that every interviewer will push.

## When to use it (recognition triggers)
- Input is a **grid / 2D matrix** and you're asked to **transform it in place** (rotate, set zeroes, evolve cells) — the follow-up will almost always demand **O(1) extra space**.
- You must **traverse in a non-row-major order**: spiral, diagonal, layer-by-layer, or boundary-first.
- You're asked to **search** a matrix with sorted structure (rows and/or columns sorted) — think staircase / elimination, not a flat binary search.
- Repeated **rectangle/region sum queries** over a static matrix — that's a 2D prefix sum (cumulative sum) problem.
- "Modify the matrix as if all updates happen simultaneously" (Game of Life) — you need to encode old + new state in the same cell.
- Phrases like "in place", "without using extra space", "in spiral order", "rotate 90 degrees", "the next state", "sum of a submatrix".

## Mental model
- A grid is just indices `(r, c)` with `0 <= r < rows`, `0 <= c < cols`. Most bugs are off-by-one boundary errors, so name `rows, cols` once and reuse them — never recompute `len(...)` inline.
- **Direction vectors** turn "move to neighbors" into a loop. The 4-neighborhood is `[(0,1),(1,0),(0,-1),(-1,0)]`; iterating it in **clockwise order** (right, down, left, up) is exactly the spiral order, so a single rotating direction index drives Spiral Matrix.
- **In-place marking**: when you need O(1) space but must remember state, encode it inside the matrix itself. Two flavors: (a) use the **first row/column as flag storage** (Set Matrix Zeroes), and (b) **bit-pack** the next state alongside the current state so one pass reads old bits and a second pass shifts to new (Game of Life).
- **Layer-by-layer** thinking: a square matrix is concentric rings. Rotation and spiral both peel rings from outside in, processing 4 sides per ring with symmetric index arithmetic.
- **2D prefix sums**: `P[i][j]` = sum of the rectangle from `(0,0)` to `(i-1,j-1)`. Inclusion-exclusion (`P = top + left - corner + cell`) builds it; the reverse inclusion-exclusion answers any rectangle query in O(1).
- The diagonal identities you reuse everywhere: cells on the same **"/" anti-diagonal** share `r + c`; cells on the same **"\" main diagonal** share `r - c`.

## Reusable template(s)
```python
# ---- Direction vectors: iterate 4 (or 8) neighbors ----
DIRS4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]          # R, D, L, U (clockwise)
DIRS8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
for dr, dc in DIRS4:
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols:           # bounds check, always
        ...                                          # use (nr, nc)

# ---- Layer-by-layer boundary walk (shrinking window) ----
top, bottom, left, right = 0, rows - 1, 0, cols - 1
while top <= bottom and left <= right:
    for c in range(left, right + 1): ...   # top row  L->R
    for r in range(top + 1, bottom + 1): ...   # right col T->B
    if top < bottom and left < right:          # guard single row/col
        for c in range(right - 1, left - 1, -1): ...   # bottom R->L
        for r in range(bottom - 1, top, -1): ...       # left col B->T
    top += 1; bottom -= 1; left += 1; right -= 1

# ---- 2D prefix sum: build O(mn), query O(1) ----
P = [[0]*(cols+1) for _ in range(rows+1)]            # 1-indexed padding row/col
for i in range(1, rows+1):
    for j in range(1, cols+1):
        P[i][j] = matrix[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]
# rectangle (r1,c1)..(r2,c2) inclusive, 0-indexed:
def region(r1, c1, r2, c2):
    return P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

## Complexity profile
- **Full traversal / transform** (spiral, rotate, set zeroes, diagonal, Game of Life): **O(m·n)** time — you touch every cell a constant number of times. Space is the whole game: naive O(m·n), but the expected in-place answer is **O(1)** extra.
- **Search a 2D Matrix II (staircase):** **O(m + n)** — each step eliminates a full row or column; far better than O(m·n) and not reducible to a single O(log mn) binary search because only the per-row/per-col order is guaranteed.
- **Range Sum Query 2D:** **O(m·n)** preprocessing, **O(1)** per query, O(m·n) space for the prefix table.
- **Maximal Square:** **O(m·n)** time, O(n) space with a rolling DP row.
- The interview signal here is **constant-factor cleanliness and the in-place trick**, not big-O reductions — most of these are already linear in the input.

## Curated problems (easy -> hard)

### 1. Set Matrix Zeroes  -  Medium
- **Problem:** Given an m×n matrix, if an element is 0, set its entire row and column to 0 — do it in place.
- **Practice (free):** https://leetcode.com/problems/set-matrix-zeroes/
- **Video (free):** https://neetcode.io/problems/set-zeroes-in-matrix
- **Idea:** Use the **first row and first column as flag storage**. First record whether row 0 / col 0 themselves contain a zero (two booleans), then for every interior zero stamp a flag into `matrix[r][0]` and `matrix[0][c]`. Apply flags inward-out, and finally zero the first row/col if their booleans were set. O(1) extra space.
```python
def setZeroes(matrix):
    rows, cols = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][c] == 0 for c in range(cols))
    first_col_zero = any(matrix[r][0] == 0 for r in range(rows))
    # stamp flags into row 0 / col 0 for interior zeros
    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0
    # zero interior cells based on flags
    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0
    # finally handle the flag row/col themselves
    if first_row_zero:
        for c in range(cols):
            matrix[0][c] = 0
    if first_col_zero:
        for r in range(rows):
            matrix[r][0] = 0
```
- **Complexity:** Time O(m·n), Space O(1) extra.
- **Key insight / gotcha:** You must capture `first_row_zero` / `first_col_zero` **before** writing any flags, and apply them **last** — otherwise the flags you store in row 0 / col 0 are indistinguishable from genuine original zeros and you cascade-clobber.
- **Follow-up:** "O(m+n) space version?" Keep two sets/boolean arrays of zero-rows and zero-cols — simpler, accepted, but the first-row/col trick is what they want when they say O(1).

### 2. Spiral Matrix  -  Medium
- **Problem:** Given an m×n matrix, return all elements in spiral order (clockwise from the top-left).
- **Practice (free):** https://leetcode.com/problems/spiral-matrix/
- **Video (free):** https://neetcode.io/problems/spiral-matrix
- **Idea:** Maintain four shrinking boundaries `top, bottom, left, right`. Walk the top row L→R, right col T→B, then (guarded) bottom row R→L and left col B→T; shrink all four and repeat until they cross.
```python
def spiralOrder(matrix):
    if not matrix or not matrix[0]:
        return []
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):       # top row  L->R
            res.append(matrix[top][c])
        for r in range(top + 1, bottom + 1):   # right col T->B
            res.append(matrix[r][right])
        if top < bottom and left < right:      # avoid re-walking a lone row/col
            for c in range(right - 1, left - 1, -1):   # bottom row R->L
                res.append(matrix[bottom][c])
            for r in range(bottom - 1, top, -1):       # left col B->T
                res.append(matrix[r][left])
        top += 1; bottom -= 1; left += 1; right -= 1
    return res
```
- **Complexity:** Time O(m·n), Space O(1) extra (output excluded).
- **Key insight / gotcha:** The `if top < bottom and left < right` guard is essential — without it, a final single remaining row or column gets traversed twice (forward then backward), duplicating elements.
- **Follow-up:** "Direction-vector version?" Iterate `DIRS4` clockwise, mark visited (or sentinel), and turn right whenever the next cell is out of bounds or already seen — same O(m·n), no explicit boundaries.

### 3. Rotate Image  -  Medium
- **Problem:** Rotate an n×n matrix 90° clockwise, in place.
- **Practice (free):** https://leetcode.com/problems/rotate-image/
- **Video (free):** https://neetcode.io/problems/rotate-matrix
- **Idea:** **Transpose then reverse each row.** Transposing swaps `(r,c)` with `(c,r)` (reflect over the main diagonal); reversing each row then flips horizontally — the composition is exactly a 90° clockwise rotation. Both steps are in place.
```python
def rotate(matrix):
    n = len(matrix)
    # transpose: swap across the main diagonal
    for r in range(n):
        for c in range(r + 1, n):          # c starts at r+1 => each pair once
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    # reverse each row
    for r in range(n):
        matrix[r].reverse()
```
- **Complexity:** Time O(n²), Space O(1) extra.
- **Key insight / gotcha:** In the transpose loop `c` must start at `r + 1`, not `0` — starting at `0` swaps every pair twice and lands you back at the original matrix. For **counter-clockwise**, reverse the rows' order first (or transpose then reverse each column).
- **Follow-up:** "Do it as a 4-way layer rotation." Process concentric rings; for each ring rotate four cells at a time (`top→right→bottom→left`) — same O(n²), avoids the two-pass transpose but is fiddlier to index.

### 4. Diagonal Traverse  -  Medium
- **Problem:** Given an m×n matrix, return all elements traversed in a zig-zag diagonal order (alternating up-right and down-left).
- **Practice (free):** https://leetcode.com/problems/diagonal-traverse/
- **Video (free):** https://www.youtube.com/results?search_query=diagonal+traverse+leetcode+498
- **Idea:** Cells on the same anti-diagonal share `r + c`. Group by that key (there are `m + n - 1` diagonals), then **reverse every other diagonal** so the walk zig-zags: even diagonals go up-right, odd go down-left.
```python
def findDiagonalOrder(mat):
    if not mat or not mat[0]:
        return []
    rows, cols = len(mat), len(mat[0])
    diagonals = {}                      # key = r + c
    for r in range(rows):
        for c in range(cols):
            diagonals.setdefault(r + c, []).append(mat[r][c])
    res = []
    for d in range(rows + cols - 1):
        cells = diagonals[d]
        if d % 2 == 0:                  # even diagonal => bottom-up (up-right)
            res.extend(reversed(cells))
        else:                           # odd diagonal => top-down (down-left)
            res.extend(cells)
    return res
```
- **Complexity:** Time O(m·n), Space O(m·n) for the grouping (or O(1) extra with a pure index walk).
- **Key insight / gotcha:** Because we appended in increasing `r` order, the natural list is top-down; the **even** diagonals (including the first, `d=0`) must be reversed to go up-right. Off-by-one on which parity reverses is the classic bug — anchor it on `d=0` being a single cell that's trivially correct either way, then check `d=1`.
- **Follow-up:** "O(1) extra space?" Walk with a single `(r,c)` and a direction flag; on stepping out of bounds, snap back onto the grid edge and flip direction — no dictionary, just careful boundary handling.

### 5. Game of Life  -  Medium
- **Problem:** Given an m×n board of 0/1 cells, compute the next state per Conway's rules, updating all cells simultaneously, in place.
- **Practice (free):** https://leetcode.com/problems/game-of-life/
- **Video (free):** https://neetcode.io/problems/game-of-life
- **Idea:** **Bit-pack** the next state into the 2nd bit while leaving the current state in the low bit. Read neighbors with `& 1` (still the old state), write the new state into bit 1 (`|= 2` when the next state is alive). A final pass shifts everything right by one (`>>= 1`). O(1) extra space.
```python
def gameOfLife(board):
    rows, cols = len(board), len(board[0])
    DIRS8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for r in range(rows):
        for c in range(cols):
            live = 0
            for dr, dc in DIRS8:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    live += board[nr][nc] & 1     # read OLD state (low bit)
            cur = board[r][c] & 1
            # next alive iff (alive and 2-3 neighbors) or (dead and exactly 3)
            if (cur and 2 <= live <= 3) or (not cur and live == 3):
                board[r][c] |= 2                  # set bit 1 = next state alive
    for r in range(rows):
        for c in range(cols):
            board[r][c] >>= 1                     # shift next state into place
```
- **Complexity:** Time O(m·n) (8 neighbor reads each), Space O(1) extra.
- **Key insight / gotcha:** Every neighbor read **must** mask with `& 1` so you see the original state — if you read the raw cell after some have been `|= 2`'d, you've contaminated the "simultaneous" update. The two-bit encoding is what makes simultaneity possible without a copy.
- **Follow-up:** "Infinite board?" You can't allocate it — store only the set of live-cell coordinates and tally neighbor counts in a dict over live cells and their neighbors.

### 6. Search a 2D Matrix II  -  Medium
- **Problem:** Search a target in an m×n matrix where each row is sorted left-to-right and each column is sorted top-to-bottom.
- **Practice (free):** https://leetcode.com/problems/search-a-2d-matrix-ii/
- **Video (free):** https://neetcode.io/problems/search-in-a-sorted-matrix
- **Idea:** **Staircase search** from the top-right corner. That cell is the largest in its row and smallest in its column, so each comparison eliminates an entire row or column: if it's bigger than target move left, if smaller move down.
```python
def searchMatrix(matrix, target):
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    r, c = 0, cols - 1                  # start top-right
    while r < rows and c >= 0:
        if matrix[r][c] == target:
            return True
        elif matrix[r][c] > target:
            c -= 1                      # whole column too big => drop it
        else:
            r += 1                      # whole row too small => drop it
    return False
```
- **Complexity:** Time O(m + n), Space O(1).
- **Key insight / gotcha:** Start from a corner where one direction increases and the other decreases (top-right or bottom-left) — **not** top-left or bottom-right, where both neighbors move the same way and you can't decide which to eliminate. This matrix is *not* fully sorted, so you cannot flatten and binary-search it (that's the easier LC 74 with the stronger row-continuation guarantee).
- **Follow-up:** "Stronger guarantee — last of each row < first of next (LC 74)?" Then treat it as one sorted array of length m·n and binary search in O(log(m·n)) via `idx -> (idx // cols, idx % cols)`.

### 7. Range Sum Query 2D - Immutable  -  Medium
- **Problem:** Given a static matrix, answer many queries for the sum of any rectangular submatrix `(r1,c1)..(r2,c2)`.
- **Practice (free):** https://leetcode.com/problems/range-sum-query-2d-immutable/
- **Video (free):** https://neetcode.io/problems/range-sum-query-2d-immutable
- **Idea:** Precompute a **2D prefix-sum table** `P` with a padding row/column so `P[i][j]` = sum of all cells above-and-left of `(i-1,j-1)`. Each query is one inclusion-exclusion: `full - top - left + corner` in O(1).
```python
class NumMatrix:
    def __init__(self, matrix):
        rows, cols = len(matrix), len(matrix[0])
        # P is (rows+1) x (cols+1), zero-padded first row/col
        self.P = [[0] * (cols + 1) for _ in range(rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                self.P[i][j] = (matrix[i-1][j-1]
                                + self.P[i-1][j]
                                + self.P[i][j-1]
                                - self.P[i-1][j-1])

    def sumRegion(self, r1, c1, r2, c2):
        P = self.P
        return (P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1])
```
- **Complexity:** Build O(m·n); each `sumRegion` query O(1); Space O(m·n).
- **Key insight / gotcha:** The `+ P[r1][c1]` term adds back the top-left corner subtracted twice — drop it and every query is wrong. The padding row/column removes all the `if r1 == 0` boundary special-cases; that's why we 1-index `P`.
- **Follow-up:** "Mutable (LC 308, updates allowed)?" A static prefix sum costs O(m·n) per update — switch to a **2D Binary Indexed Tree (Fenwick)** for O(log m · log n) update and query.

### 8. Maximal Square  -  Medium (cross-ref: DP)
- **Problem:** Given a binary matrix, find the area of the largest square containing only 1s.
- **Practice (free):** https://leetcode.com/problems/maximal-square/
- **Video (free):** https://neetcode.io/problems/maximal-square
- **Idea:** DP on the grid: `dp[r][c]` = side length of the largest all-1 square whose **bottom-right corner** is `(r,c)`. If the cell is 1, it extends the smallest of its top, left, and top-left neighbors by one: `dp = 1 + min(up, left, up_left)`. Track the global max side; answer is side². (See the DP pattern file for the general "square/rectangle from neighbors" recurrence.)
```python
def maximalSquare(matrix):
    if not matrix or not matrix[0]:
        return 0
    rows, cols = len(matrix), len(matrix[0])
    prev = [0] * (cols + 1)            # rolling DP row (1-indexed padding)
    best = 0
    for r in range(rows):
        curr = [0] * (cols + 1)
        for c in range(1, cols + 1):
            if matrix[r][c-1] == '1':
                curr[c] = 1 + min(prev[c], curr[c-1], prev[c-1])
                best = max(best, curr[c])
        prev = curr
    return best * best
```
- **Complexity:** Time O(m·n), Space O(n) with the rolling row (O(m·n) for a full table).
- **Key insight / gotcha:** It's **min**, not max — a square's side is limited by its weakest of the three neighboring squares; one short neighbor caps the whole expansion. Note the input here is characters `'1'`/`'0'` (LeetCode quirk), so compare against the string.
- **Follow-up:** "Maximal *Rectangle* (LC 85, Hard)?" Reduce each row to a histogram of consecutive 1s and run "Largest Rectangle in Histogram" per row with a monotonic stack — different, harder reduction.

### 9. Spiral Matrix II  -  Medium
- **Problem:** Generate an n×n matrix filled with 1..n² in spiral (clockwise) order.
- **Practice (free):** https://leetcode.com/problems/spiral-matrix-ii/
- **Video (free):** https://neetcode.io/problems/spiral-matrix-ii
- **Idea:** Same four-boundary spiral walk as Spiral Matrix I, but **writing** an incrementing counter instead of reading. Walk top→right→bottom→left, shrink the boundaries, and stop after placing n² values.
```python
def generateMatrix(n):
    mat = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    val = 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):       # top row  L->R
            mat[top][c] = val; val += 1
        for r in range(top + 1, bottom + 1):   # right col T->B
            mat[r][right] = val; val += 1
        if top < bottom and left < right:
            for c in range(right - 1, left - 1, -1):   # bottom R->L
                mat[bottom][c] = val; val += 1
            for r in range(bottom - 1, top, -1):       # left col B->T
                mat[r][left] = val; val += 1
        top += 1; bottom -= 1; left += 1; right -= 1
    return mat
```
- **Complexity:** Time O(n²), Space O(1) extra (output excluded).
- **Key insight / gotcha:** Same single-row/col guard as Spiral I — for odd `n` the center cell is filled by the top-row pass of the innermost ring, and the guard prevents the bottom/left passes from overwriting it. The writing direction is identical to the reading direction; only the operation differs.
- **Follow-up:** "Spiral Matrix III (LC 885)?" Start from an arbitrary cell and spiral outward with step lengths 1,1,2,2,3,3,…, collecting only in-bounds cells — direction-vector driven rather than boundary driven.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the four-boundary spiral walk (with the single-row/col guard) from memory
- [ ] I can derive rotate-90 from transpose + row-reverse without hesitating
- [ ] I can state the 2D prefix-sum query formula (inclusion-exclusion) from memory
- [ ] I can explain why staircase search starts top-right, not top-left
- [ ] Set Matrix Zeroes — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Spiral Matrix — 🔴 / 🟡 / 🟢
- [ ] Rotate Image — 🔴 / 🟡 / 🟢
- [ ] Diagonal Traverse — 🔴 / 🟡 / 🟢
- [ ] Game of Life — 🔴 / 🟡 / 🟢
- [ ] Search a 2D Matrix II — 🔴 / 🟡 / 🟢
- [ ] Range Sum Query 2D - Immutable — 🔴 / 🟡 / 🟢
- [ ] Maximal Square — 🔴 / 🟡 / 🟢
- [ ] Spiral Matrix II — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (Arrays & Hashing / 2-D problems are scattered through the Arrays and DP sections) — https://neetcode.io/roadmap ; LeetCode "Array and String" explore card (covers spiral, rotate, prefix-sum intuition) — https://leetcode.com/explore/learn/card/array-and-string/ ; takeUforward/Striver matrix problems series — https://www.youtube.com/results?search_query=striver+matrix+problems+playlist
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (the 2D/matrix and prefix-sum patterns) — https://www.designgurus.io (free alternative: the NeetCode roadmap and LeetCode Array & String explore card above cover the same material with worked examples).

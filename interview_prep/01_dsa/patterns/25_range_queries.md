# 25 - Prefix Sums, Difference Arrays & Range-Query Structures (Fenwick / Segment Tree)
> One-line: answer "what's the aggregate over range [l, r]?" — fast — by precomputing cumulative structure instead of re-scanning the range every query.

> **Frequency / signal:** Prefix sums and difference arrays are **MEDIUM-HIGH frequency** — they show up everywhere (subarray sums, 2D regions, interval stamping) and are table stakes. Fenwick trees (BIT) and segment trees are **GOOGLE / UBER-hard**: lower raw frequency, but knowing them cleanly is exactly what separates an L5 / Senior signal from a down-level one. Reach for the heavy structure only when updates **and** queries are both interleaved; otherwise a prefix/difference array wins on simplicity.

## When to use it (recognition triggers)
- "**Range sum / min / max / xor** over `[l, r]`" asked **many times** on an array that **doesn't change** -> 1D/2D prefix sum, O(1) per query after O(n) build.
- "Subarray summing to k", "count subarrays with sum divisible by k", "max-size subarray sum = k" -> prefix sum + hash map of seen prefixes.
- "Add `val` to **every element in a range** `[l, r]`", many such updates, **then** read the final array once -> **difference array** (O(1) per range update, O(n) to materialize).
- "Booking / interval stamping / sweep" — flights between stations, passengers picked up/dropped, +1 at start / -1 at end -> difference array (a.k.a. the imbalance/delta trick).
- "Range query **and** point update, **interleaved**" (read [l,r], then change index i, then read again) -> **Fenwick tree (BIT)** for sum/prefix-aggregates, **segment tree** for anything associative (min/max/gcd/sum).
- "Count of smaller/greater elements to the right", "count inversions", "number of range sums" -> BIT or merge-sort over **coordinate-compressed** values.
- "Range **update** and range **query** both online" -> segment tree with **lazy propagation**.

## Mental model
- **Prefix sum** turns a range aggregate into a difference of two precomputed values: `sum(l..r) = P[r+1] - P[l]`. You pay O(n) once, then every query is O(1). The whole trick is "cumulative array, then subtract."
- **Difference array** is the *inverse*: instead of storing values you store **deltas** `d[i] = a[i] - a[i-1]`. A range add `+v on [l, r]` becomes two point pokes: `d[l] += v`, `d[r+1] -= v`. Take a prefix sum of `d` at the end to recover the array. Range-update / single-read -> O(1) per update.
- Prefix sum and difference array are duals: prefix sum reads ranges cheaply but updates expensively; difference array updates ranges cheaply but reads expensively. Use whichever side of the trade matches the workload.
- **Fenwick tree (BIT)** is a clever array where index `i` stores the sum of a block of size `i & (-i)` (its lowest set bit). Walking *down* by stripping the lowest bit gives a prefix sum in O(log n); walking *up* by adding the lowest bit updates all blocks covering an index in O(log n). It only handles **invertible** aggregates well (sum, xor) because range = prefix(r) - prefix(l-1).
- **Segment tree** is a binary tree over array segments: each node holds the aggregate of its half. Query/update split into O(log n) canonical nodes. It handles **any associative** op (min, max, gcd, sum) and supports **range updates** via *lazy propagation* (defer pushing an update to children until you actually descend).
- Decision order: **no updates** -> prefix/difference array. **point update + range query, op is sum/xor** -> BIT (smaller, faster, less code). **point update + range query, op is min/max/gcd** or **range update + range query** -> segment tree.

## Reusable template(s)
```python
# ---- 1D prefix sum: immutable range sum, O(1) query ----
class PrefixSum1D:
    def __init__(self, nums):
        self.P = [0] * (len(nums) + 1)          # P[i] = sum(nums[:i])
        for i, x in enumerate(nums):
            self.P[i + 1] = self.P[i] + x
    def range_sum(self, l, r):                  # inclusive [l, r]
        return self.P[r + 1] - self.P[l]

# ---- Difference array: O(1) range add, O(n) materialize ----
class DiffArray:
    def __init__(self, n):
        self.d = [0] * (n + 1)                  # one extra slot for r+1
    def add(self, l, r, v):                     # +v on inclusive [l, r]
        self.d[l] += v
        self.d[r + 1] -= v
    def build(self):                            # prefix sum -> final array
        out, run = [], 0
        for i in range(len(self.d) - 1):
            run += self.d[i]
            out.append(run)
        return out

# ---- Fenwick / Binary Indexed Tree: point update + prefix/range sum, O(log n) ----
class BIT:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)               # 1-indexed
    def update(self, i, delta):                 # add delta at 1-indexed i
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)                       # move to next responsible block
    def prefix(self, i):                        # sum of [1..i]
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)                        # strip lowest set bit
        return s
    def range_sum(self, l, r):                  # 1-indexed inclusive
        return self.prefix(r) - self.prefix(l - 1)

# ---- Segment tree: point update + range query, any associative op ----
class SegTree:
    def __init__(self, nums, func=min, identity=float('inf')):
        self.n = len(nums)
        self.func = func
        self.identity = identity
        self.t = [identity] * (2 * self.n)       # iterative, size 2n
        for i in range(self.n):                  # leaves at [n .. 2n)
            self.t[self.n + i] = nums[i]
        for i in range(self.n - 1, 0, -1):       # build internal nodes
            self.t[i] = func(self.t[2 * i], self.t[2 * i + 1])
    def update(self, i, val):                    # point set index i = val
        i += self.n
        self.t[i] = val
        while i > 1:
            i //= 2
            self.t[i] = self.func(self.t[2 * i], self.t[2 * i + 1])
    def query(self, l, r):                        # inclusive [l, r]
        res = self.identity
        l += self.n
        r += self.n + 1                           # half-open [l, r)
        while l < r:
            if l & 1:
                res = self.func(res, self.t[l]); l += 1
            if r & 1:
                r -= 1; res = self.func(res, self.t[r])
            l //= 2; r //= 2
        return res
```

## Complexity profile
- **Prefix sum (1D/2D):** build O(n) / O(mn), query O(1), space O(n) / O(mn). No updates allowed (rebuild is O(n)).
- **Difference array:** each range update O(1), final materialize O(n), space O(n). One bulk read at the end.
- **Fenwick / BIT:** build O(n) (or O(n log n) naively), update O(log n), prefix/range query O(log n), space O(n). Smallest constant of the log-structures; sum/xor only.
- **Segment tree (point update):** build O(n), update O(log n), query O(log n), space O(2n) iterative / O(4n) recursive. Any associative op.
- **Segment tree + lazy (range update):** range update O(log n), range query O(log n), space O(4n). The only structure here that does range-update *and* range-query both online.
- Rule of thumb: if there are **no updates**, never reach past a prefix/difference array — a BIT or segment tree is wasted code and slower constants.

## Curated problems (easy -> hard)

### 1. Range Sum Query - Immutable  -  Easy
- **Problem:** Given an integer array, answer many `sumRange(l, r)` queries (inclusive). The array never changes.
- **Practice (free):** https://leetcode.com/problems/range-sum-query-immutable/
- **Video (free):** https://neetcode.io/problems/range-sum-query-immutable
- **Idea:** Precompute a prefix array `P` where `P[i] = sum of first i elements`; then `sumRange(l, r) = P[r+1] - P[l]` in O(1).
```python
class NumArray:
    def __init__(self, nums):
        self.P = [0] * (len(nums) + 1)
        for i, x in enumerate(nums):
            self.P[i + 1] = self.P[i] + x      # P[i+1] = sum(nums[:i+1])
    def sumRange(self, l, r):
        return self.P[r + 1] - self.P[l]       # subtract the two cumulative endpoints
```
- **Complexity:** Build O(n), query O(1), space O(n).
- **Key insight / gotcha:** Use a **size n+1** prefix array with `P[0] = 0` so `l = 0` needs no special case (`P[r+1] - P[0]`). Off-by-one on the upper index (`r+1`, not `r`) is the classic bug.
- **Follow-up:** "What if the array can be updated?" That's the mutable version — switch to a BIT or segment tree (problem #5/#7).

### 2. Range Sum Query 2D - Immutable  -  Medium
- **Problem:** Given an immutable matrix, answer many `sumRegion(r1, c1, r2, c2)` queries for the rectangle sum.
- **Practice (free):** https://leetcode.com/problems/range-sum-query-2d-immutable/
- **Video (free):** https://neetcode.io/problems/range-sum-query-2d-immutable
- **Idea:** 2D prefix sum: `P[i][j] = sum of all cells in rectangle (0,0)..(i-1,j-1)`. A region is recovered by inclusion-exclusion: full - top - left + top-left-overlap.
```python
class NumMatrix:
    def __init__(self, matrix):
        m, n = len(matrix), len(matrix[0])
        self.P = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                self.P[i + 1][j + 1] = (matrix[i][j]
                                        + self.P[i][j + 1]   # add row above
                                        + self.P[i + 1][j]   # add col left
                                        - self.P[i][j])      # remove double-counted corner
    def sumRegion(self, r1, c1, r2, c2):
        return (self.P[r2 + 1][c2 + 1] - self.P[r1][c2 + 1]
                - self.P[r2 + 1][c1] + self.P[r1][c1])
```
- **Complexity:** Build O(mn), query O(1), space O(mn).
- **Key insight / gotcha:** Inclusion-exclusion needs the `+ P[r1][c1]` term: subtracting the top strip and the left strip removes the top-left overlap **twice**, so you add it back once. The `+1` padding again kills boundary special-casing.
- **Follow-up:** "Mutable 2D with point updates?" Use a **2D BIT** (a Fenwick tree of Fenwick trees), update and query both O(log m · log n).

### 3. Corporate Flight Bookings  -  Medium
- **Problem:** Given `n` flights (1..n) and bookings `[first, last, seats]` meaning `seats` were booked on every flight in `[first, last]`, return the total seats booked per flight.
- **Practice (free):** https://leetcode.com/problems/corporate-flight-bookings/
- **Video (free):** https://www.youtube.com/results?search_query=corporate+flight+bookings+difference+array
- **Idea:** Difference array. For each booking add `seats` at `first` and subtract it after `last`; a single prefix sum at the end materializes every flight's total — O(n + bookings) instead of O(n · bookings).
```python
def corpFlightBookings(bookings, n):
    diff = [0] * (n + 1)                       # 1-indexed flights, extra slot
    for first, last, seats in bookings:
        diff[first - 1] += seats               # 0-indexed start
        diff[last] -= seats                    # cancel right after 'last'
    res, run = [], 0
    for i in range(n):
        run += diff[i]                          # prefix sum recovers the value
        res.append(run)
    return res
```
- **Complexity:** O(n + k) time (k = #bookings), O(n) space.
- **Key insight / gotcha:** A range add becomes **two point updates** on the diff array; you only pay O(range) once, at the final prefix-sum pass. Watch the `-1` for 1-indexed flights and that `diff[last]` (not `last+1`) is correct because flights are 1-indexed but `diff` is 0-indexed.
- **Follow-up:** "Queries interleaved with reads?" The diff trick assumes all updates happen before the single read — if reads interleave, use a BIT.

### 4. Car Pooling  -  Medium
- **Problem:** A car has `capacity` seats. Given trips `[numPassengers, from, to]`, return whether you can pick up and drop off everyone without ever exceeding capacity.
- **Practice (free):** https://leetcode.com/problems/car-pooling/
- **Video (free):** https://neetcode.io/problems/car-pooling
- **Idea:** Difference array over locations (a sweep): `+passengers` at `from`, `-passengers` at `to`; prefix-sum the deltas and check the running occupancy never exceeds capacity.
```python
def carPooling(trips, capacity):
    diff = [0] * 1001                          # locations 0..1000 per constraints
    for p, frm, to in trips:
        diff[frm] += p                          # board at 'frm'
        diff[to] -= p                           # alight at 'to' (seat freed here)
    cur = 0
    for delta in diff:
        cur += delta                            # occupancy after this location
        if cur > capacity:
            return False
    return True
```
- **Complexity:** O(n + maxLoc) time, O(maxLoc) space (or O(n log n) with sorted event sweep).
- **Key insight / gotcha:** Passengers alight **at** `to` (`-p` goes at `to`, not `to+1`) — they free the seat exactly when they get off, so the segment occupied is `[from, to)`. Getting that boundary wrong double-books the drop-off station.
- **Follow-up:** "Coordinates up to 1e9?" Drop the fixed array; sort `(location, delta)` events and sweep — coordinate-compression / event-sweep handles sparse coordinates.

### 5. Range Sum Query - Mutable (Fenwick / BIT)  -  Medium
- **Problem:** Support `update(i, val)` (set element i to val) and `sumRange(l, r)` interleaved arbitrarily.
- **Practice (free):** https://leetcode.com/problems/range-sum-query-mutable/
- **Video (free):** https://neetcode.io/problems/range-sum-query-mutable
- **Idea:** Fenwick tree (BIT) over the array. `update` adds the **delta** (new - old) along the responsible blocks; `sumRange(l, r) = prefix(r) - prefix(l-1)`. Both O(log n).
```python
class NumArray:
    def __init__(self, nums):
        self.n = len(nums)
        self.nums = [0] * self.n
        self.tree = [0] * (self.n + 1)          # 1-indexed BIT
        for i, x in enumerate(nums):
            self.update(i, x)                   # builds via repeated point-add
    def _add(self, i, delta):                   # i is 1-indexed here
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)                       # next block covering i
    def _prefix(self, i):                       # sum of [1..i]
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)                        # strip lowest set bit
        return s
    def update(self, index, val):
        delta = val - self.nums[index]          # BIT stores deltas, so diff first
        self.nums[index] = val
        self._add(index + 1, delta)             # +1 for 1-indexing
    def sumRange(self, left, right):
        return self._prefix(right + 1) - self._prefix(left)
```
- **Complexity:** Build O(n log n) (or O(n) with a smarter build), update O(log n), query O(log n), space O(n).
- **Key insight / gotcha:** A BIT stores **deltas**, not values, so `update` must add `val - old`, not `val`. `i & (-i)` isolates the lowest set bit — that's the block size; add it to climb (update), subtract it to descend (prefix). The whole tree is **1-indexed**; index 0 would loop forever (`0 & -0 == 0`).
- **Follow-up:** "Range update + point query?" Build the BIT over the **difference array**: range-add becomes two point updates, and a point query is a prefix sum. "Range update + range query?" Two BITs, or jump to a lazy segment tree.

### 6. Count of Smaller Numbers After Self  -  Hard
- **Problem:** For each `nums[i]`, count how many elements to its right are strictly smaller.
- **Practice (free):** https://leetcode.com/problems/count-of-smaller-numbers-after-self/
- **Video (free):** https://neetcode.io/problems/count-of-smaller-numbers-after-self
- **Idea:** Sweep **right to left** and keep a BIT indexed by **rank** (coordinate-compressed value). For each element, query the prefix count of all strictly-smaller ranks already inserted, then insert the current element.
```python
def countSmaller(nums):
    sorted_vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(sorted_vals)}   # 1-indexed ranks
    n = len(sorted_vals)
    tree = [0] * (n + 1)
    def add(i):
        while i <= n:
            tree[i] += 1
            i += i & (-i)
    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & (-i)
        return s
    res = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):       # right to left
        r = rank[nums[i]]
        res[i] = prefix(r - 1)                     # how many already-seen ranks < this
        add(r)                                     # now register this element
    return res
```
- **Complexity:** O(n log n) time (compression + n BIT ops), O(n) space.
- **Key insight / gotcha:** **Coordinate-compress** values to ranks `1..n` so the BIT is sized by *distinct values*, not value magnitude (values can be huge/negative). Query `prefix(r-1)` for *strictly* smaller; `prefix(r)` would wrongly include equal values. Processing right-to-left means "already inserted" == "to the right."
- **Follow-up:** "Count of larger after self / count inversions." Same skeleton: query the suffix (`total_inserted - prefix(r)`) for larger, or count inversions with a left-to-right sweep — all reducible to BIT-on-ranks or merge sort.

### 7. Range Sum Query - Mutable (Segment Tree)  -  Medium
- **Problem:** Same as #5 (interleaved `update` and `sumRange`), solved with a segment tree — the template that generalizes to min/max/gcd, not just sum.
- **Practice (free):** https://leetcode.com/problems/range-sum-query-mutable/
- **Video (free):** https://neetcode.io/problems/range-sum-query-mutable
- **Idea:** Build a binary tree where each node holds the sum of its segment; leaves are array cells. Point update walks leaf->root re-aggregating; range query splits `[l, r]` into O(log n) covering nodes. Swap `+` for `min`/`max`/`gcd` to reuse verbatim.
```python
class NumArray:
    def __init__(self, nums):
        self.n = len(nums)
        self.t = [0] * (2 * self.n)             # iterative seg tree, leaves at [n..2n)
        for i in range(self.n):
            self.t[self.n + i] = nums[i]
        for i in range(self.n - 1, 0, -1):       # build internal: parent = sum of kids
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]
    def update(self, index, val):
        i = index + self.n
        self.t[i] = val                          # set the leaf
        while i > 1:                             # propagate up to the root
            i //= 2
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]
    def sumRange(self, left, right):
        res = 0
        l, r = left + self.n, right + self.n + 1  # half-open [l, r)
        while l < r:
            if l & 1:                            # l is a right child -> include, step right
                res += self.t[l]; l += 1
            if r & 1:                            # r is a right child -> include the one left of it
                r -= 1; res += self.t[r]
            l //= 2; r //= 2                      # climb a level
        return res
```
- **Complexity:** Build O(n), update O(log n), query O(log n), space O(2n).
- **Key insight / gotcha:** The iterative array layout puts leaves at indices `[n, 2n)` and each parent at `i//2`. The bit-trick `if l & 1` / `if r & 1` is how you collect exactly the canonical boundary nodes without recursion. For min/max set the identity correctly (`+inf` / `-inf`) — `0` as identity only works for sum/xor.
- **Follow-up:** "BIT vs segment tree here?" For pure sum, BIT is smaller and faster (#5). Use the segment tree when the op is **non-invertible** (min/max/gcd) — a BIT can't do those because `range = prefix(r) - prefix(l-1)` needs subtraction.

### 8. Range Update + Range Query (Lazy Propagation note)  -  Hard
- **Problem:** Support `update(l, r, val)` (add `val` to **every** element in `[l, r]`) **and** `query(l, r)` (range sum), both online and interleaved. (Practice on "Range Module" / SPOJ HORRIBLE / Codeforces; LeetCode "My Calendar III" and "Range Module" exercise the same idea.)
- **Practice (free):** https://leetcode.com/problems/range-module/  (range add/query flavor); classic drill: https://www.spoj.com/problems/HORRIBLE/
- **Video (free):** https://www.youtube.com/results?search_query=segment+tree+lazy+propagation
- **Idea:** A plain segment tree can't do **range updates** cheaply because touching every leaf in `[l, r]` is O(range). **Lazy propagation** fixes this: when an update fully covers a node, apply it to that node's aggregate and stash a pending `lazy` value there instead of descending. Only when you later need to go *into* that node do you "push down" the lazy value to its children. Both range update and range query stay O(log n).
```python
class LazySegTree:
    def __init__(self, nums):
        self.n = len(nums)
        self.t = [0] * (4 * self.n)             # node sums
        self.lazy = [0] * (4 * self.n)          # pending add for each node
        self._build(nums, 1, 0, self.n - 1)
    def _build(self, a, node, lo, hi):
        if lo == hi:
            self.t[node] = a[lo]; return
        mid = (lo + hi) // 2
        self._build(a, 2 * node, lo, mid)
        self._build(a, 2 * node + 1, mid + 1, hi)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]
    def _push_down(self, node, lo, hi):
        if self.lazy[node]:
            mid = (lo + hi) // 2
            for child, clo, chi in ((2 * node, lo, mid),
                                    (2 * node + 1, mid + 1, hi)):
                self.lazy[child] += self.lazy[node]
                self.t[child] += self.lazy[node] * (chi - clo + 1)   # add * count
            self.lazy[node] = 0
    def update(self, l, r, val, node=1, lo=0, hi=None):
        if hi is None: hi = self.n - 1
        if r < lo or hi < l:                     # no overlap
            return
        if l <= lo and hi <= r:                  # full cover -> stamp lazily
            self.t[node] += val * (hi - lo + 1)
            self.lazy[node] += val
            return
        self._push_down(node, lo, hi)            # partial -> must descend, push first
        mid = (lo + hi) // 2
        self.update(l, r, val, 2 * node, lo, mid)
        self.update(l, r, val, 2 * node + 1, mid + 1, hi)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]
    def query(self, l, r, node=1, lo=0, hi=None):
        if hi is None: hi = self.n - 1
        if r < lo or hi < l:                     # no overlap
            return 0
        if l <= lo and hi <= r:                  # full cover
            return self.t[node]
        self._push_down(node, lo, hi)            # partial -> push pending down first
        mid = (lo + hi) // 2
        return (self.query(l, r, 2 * node, lo, mid)
                + self.query(l, r, 2 * node + 1, mid + 1, hi))
```
- **Complexity:** Build O(n), range update O(log n), range query O(log n), space O(4n).
- **Key insight / gotcha:** A lazy "add" updates a node's aggregate by `val * (segment length)` for sums (not just `val`) — forgetting the length factor is the #1 bug. Always `_push_down` **before** descending into a partially-covered node, so children see pending updates; on a **full cover** you stamp and return without pushing. Use the recursive `4n` layout for lazy trees — the iterative `2n` form doesn't support lazy cleanly.
- **Follow-up:** "Range **assign** (set, not add) instead of add?" Lazy value becomes a "pending assignment" with a has-value flag; pushdown overwrites children. "Min/max with range-add?" The aggregate add becomes just `+val` (no length factor) since min/max of a shifted segment shifts by `val`.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (does the array change? are queries and updates interleaved?)
- [ ] I can write the 1D and 2D prefix-sum build + query from memory (incl. the +1 padding)
- [ ] I can derive the difference-array range-add trick and the inclusion-exclusion 2D query
- [ ] I can write the BIT `update` / `prefix` with the `i & (-i)` lowest-bit move from memory
- [ ] I can write the iterative segment tree (point update + range query) from memory
- [ ] I can explain when to pick prefix sum vs difference array vs BIT vs segment tree
- [ ] I can explain lazy propagation (push-down, full-cover stamp, length factor)
- [ ] Range Sum Query - Immutable (1D) — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Range Sum Query 2D - Immutable — 🔴 / 🟡 / 🟢
- [ ] Corporate Flight Bookings — 🔴 / 🟡 / 🟢
- [ ] Car Pooling — 🔴 / 🟡 / 🟢
- [ ] Range Sum Query - Mutable (BIT) — 🔴 / 🟡 / 🟢
- [ ] Count of Smaller Numbers After Self — 🔴 / 🟡 / 🟢
- [ ] Range Sum Query - Mutable (Segment Tree) — 🔴 / 🟡 / 🟢
- [ ] Range Update + Range Query (lazy) — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (Advanced / "Math & Geometry" and array prefix sections) — https://neetcode.io/roadmap ; cp-algorithms Fenwick tree — https://cp-algorithms.com/data_structures/fenwick.html ; cp-algorithms Segment tree (incl. lazy) — https://cp-algorithms.com/data_structures/segment_tree.html ; USACO Guide "Prefix Sums" + "Point Update Range Sum" — https://usaco.guide/silver/prefix-sums ; takeUforward/Striver segment tree + BIT — https://www.youtube.com/results?search_query=striver+segment+tree+fenwick+tree
- **Paid (optional):** DesignGurus "Grokking" merged-interval / prefix patterns — https://www.designgurus.io (free alternative: the cp-algorithms + USACO Guide links above cover prefix sums, BIT, and lazy segment trees with full derivations).

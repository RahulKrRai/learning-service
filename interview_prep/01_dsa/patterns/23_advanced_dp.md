# 23 - Advanced DP - state machines, intervals, bitmask, tree DP

> One-line: the four "second-tier" DP shapes that show up once the answer can't be a 1D prefix or a 2D `(i, j)` table — a fixed set of *states* per step, a *range* `[i, j]` whose answer needs a split point, a *set of visited things* packed into an integer, or a recurrence over the *children of a tree node*.

> **Priority: GOOGLE-HARD.** These are the patterns most likely to surface in Google L5 hard rounds and occasionally Atlassian/Uber. They appear far less often at Amazon/Confluent than the 1D/grid/knapsack DP in files 15-17 — drill those to reflex first, then layer these on. If you see a clean interval-split or bitmask-over-`n<=20` problem in a Google loop, this file is the unlock.

## When to use it (recognition triggers)
- **State-machine DP:** the entity moves between a small fixed set of modes (holding/idle/cooling, or "k transactions used so far") and the transition out of each mode is constrained. Cue words: "at most k transactions", "cooldown", "fee per trade", "you may be in one of these situations".
- **Interval DP:** the answer for a range `[i, j]` is built by choosing a **split point / last action** `k` inside the range, gluing together `[i, k]` and `[k, j]`. Cue: "burst/remove/merge elements and the cost depends on neighbors", "the order you process matters", "combine adjacent pieces". Archetype = **Matrix Chain Multiplication**.
- **Bitmask DP:** `n` is tiny (**n <= ~20-22**) and the state is "which subset of items have I used/visited", which packs into an `int` bitmask. Cue: "visit all nodes", "partition into k groups", "assign tasks to people", "n <= 20" in the constraints is itself the tell.
- **Tree DP:** the input is a binary tree / general tree and the answer at a node is a function of the answers at its **children**, often with a per-node choice (take this node or not) that forbids the adjacent choice. Cue: "rob the tree", "cover/cameras", "max path through a node".

## Mental model
- All four are still just "define a state, write a recurrence over strictly smaller states, memoize". What changes is the *shape* of the state, not the discipline.
- **State machine** = `dp[i][state]`. Enumerate the legal `state -> state'` edges once on paper; the transition is just "best way to arrive in each state today given each state yesterday". Almost always collapses to a few rolling scalars.
- **Interval** = `dp[i][j]` filled by **increasing range length** (so the sub-ranges are already done), with an inner loop over the split/last-action `k`. The defining trick is choosing `k` to be "the *last* element acted on in `[i, j]`" so its neighbors are the fixed boundaries `i-1` and `j+1`.
- **Bitmask** = `dp[mask]` (sometimes `dp[mask][i]` for "...ending at node i"). `mask` enumerates subsets; iterate masks in increasing integer order so subsets are processed before supersets. Standard bit ops: test `mask >> b & 1`, set `mask | 1 << b`, iterate set bits.
- **Tree DP** = post-order DFS returning a small tuple per node (e.g. `(best_if_robbed, best_if_not)`); the parent combines its children's tuples. No explicit table — the recursion stack *is* the DP order.

## Reusable template(s)
```python
# ---- State-machine DP (rolling scalars; here a generic k-state day loop) ----
def state_machine(prices):
    # one variable per state; init to the legal starting value (often -inf or 0)
    s_hold, s_idle = float('-inf'), 0
    for p in prices:
        new_hold = max(s_hold, s_idle - p)     # stay holding, or buy today
        new_idle = max(s_idle, s_hold + p)     # stay idle,   or sell today
        s_hold, s_idle = new_hold, new_idle    # commit simultaneously
    return s_idle

# ---- Interval DP (fill by increasing length, inner loop over split k) ----
def interval_dp(a):
    n = len(a)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):             # range length, smallest first
        for i in range(n - length + 1):
            j = i + length - 1
            best = float('inf')                # or -inf for max problems
            for k in range(i, j):              # k = split / last-action point
                best = min(best, dp[i][k] + dp[k + 1][j] + cost(i, k, j))
            dp[i][j] = best
    return dp[0][n - 1]

# ---- Bitmask DP (iterate masks ascending; supersets after subsets) ----
def bitmask_dp(n, cost):
    FULL = (1 << n) - 1
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        for b in range(n):                     # try adding an unused element b
            if not (mask >> b & 1):
                nxt = mask | (1 << b)
                dp[nxt] = min(dp[nxt], dp[mask] + cost(mask, b))
    return dp[FULL]

# ---- Tree DP (post-order DFS returning a per-node tuple) ----
def tree_dp(root):
    def dfs(node):
        if not node:
            return (0, 0)                      # (take_node, skip_node)
        l = dfs(node.left)
        r = dfs(node.right)
        take = node.val + l[1] + r[1]          # if we take node, children must be skipped
        skip = max(l) + max(r)                 # if we skip node, children free to choose best
        return (take, skip)
    return max(dfs(root))
```

## Complexity profile
- **State machine:** `O(n * states)` time, `O(states)` space (rolling) — `states` is a tiny constant (3 for cooldown) or `O(k)` for k-transaction problems, giving `O(n*k)`.
- **Interval:** `O(n^3)` time (n² ranges × O(n) split scan), `O(n^2)` space. The cubic is expected and fine for `n` up to a few hundred.
- **Bitmask:** `O(2^n * n)` or `O(2^n * n^2)` time, `O(2^n)` or `O(2^n * n)` space. The `2^n` is why `n <= ~20` is mandatory; at n=20 that's ~1M masks × 20 = ~20M ops.
- **Tree DP:** `O(V)` time (each node visited once), `O(h)` stack space (`h` = tree height, `O(n)` worst case for a skewed tree).

---

# Group 1 - State-machine DP

**Recognition cue:** the actor is always in exactly one of a *small fixed set of modes* and each day/step you move between modes under rules ("can't buy right after selling", "pay a fee on each sale", "you've used j of k transactions"). Model it as `dp[i][state]`, enumerate the legal mode transitions once, then roll. The giveaway phrases are **"at most k transactions"**, **"cooldown"**, and **"transaction fee"**.

> Note: the *cooldown* variant also appears in file 16 (2D & grid) framed as a 3-state machine. It's repeated here because it's the cleanest entry point to the family, and the **fee** and **k-transaction** variants below are the genuinely advanced members you should own.

### 1. Best Time to Buy and Sell Stock with Cooldown  -  Medium
- **Problem:** Maximize profit from unlimited transactions on a price array, but after you sell you must sit out one day (cooldown) before buying again.
- **Practice (free):** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/
- **Video (free):** https://neetcode.io/problems/buy-and-sell-crypto-with-cooldown
- **Idea:** Three states per day — `hold` (own a share), `sold` (sold *today*, so tomorrow is forced idle), `rest` (idle and free to buy). You may only buy *from* `rest`, which is exactly what enforces the cooldown.
```python
from typing import List

def maxProfit(prices: List[int]) -> int:
    hold = float('-inf')   # best profit while currently holding a share
    sold = 0               # best profit on a day we sold today (cooldown tomorrow)
    rest = 0               # best profit while idle and allowed to buy
    for p in prices:
        prev_sold = sold
        sold = hold + p                 # sell what we held
        hold = max(hold, rest - p)      # keep holding, or buy (only from rest)
        rest = max(rest, prev_sold)     # stay resting, or arrive after yesterday's sale
    return max(sold, rest)              # never optimal to end while holding

if __name__ == '__main__':
    print(maxProfit([1, 2, 3, 0, 2]))   # 3  -> buy1 sell3, cooldown, buy0 sell2
    print(maxProfit([1]))               # 0
```
- **Complexity:** Time O(n), Space O(1).
- **Key insight / gotcha:** Capture `prev_sold` *before* overwriting `sold`, because `rest` depends on yesterday's `sold`. The single edge "buy only from `rest`, never directly after a sell" is the entire cooldown rule.
- **Follow-up:** "Cooldown of `c` days instead of 1?" Keep a small ring buffer / track `sold` from `c` days ago; the transition into `rest` reads the older sold value.

### 2. Best Time to Buy and Sell Stock with Transaction Fee  -  Medium
- **Problem:** Maximize profit from unlimited transactions, paying a fixed `fee` on every completed transaction (charge it once, conventionally on sell).
- **Practice (free):** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/
- **Video (free):** https://neetcode.io/problems/buy-and-sell-crypto-with-fee — also https://www.youtube.com/results?search_query=neetcode+best+time+to+buy+and+sell+stock+with+transaction+fee
- **Idea:** Two states — `hold` (own a share) and `cash` (no share). Selling pays the fee. No cooldown, so you may buy directly from `cash` the same step you could have rested.
```python
from typing import List

def maxProfit(prices: List[int], fee: int) -> int:
    hold = float('-inf')   # best profit while holding a share
    cash = 0               # best profit while holding no share
    for p in prices:
        cash = max(cash, hold + p - fee)   # sell today (pay the fee once, here)
        hold = max(hold, cash - p)         # buy today from current cash
    return cash

if __name__ == '__main__':
    print(maxProfit([1, 3, 2, 8, 4, 9], 2))  # 8
    print(maxProfit([1, 3, 7, 5, 10, 3], 3)) # 6
```
- **Complexity:** Time O(n), Space O(1).
- **Key insight / gotcha:** Charge the fee in exactly one transition (here on `sell`); charging on both buy and sell double-counts it. Note `hold` is updated *after* `cash` using the new `cash` — buying same step is allowed (no cooldown), unlike the previous problem.
- **Follow-up:** "Fee on buy instead?" Move the `- fee` into the `hold` transition; the optimum is identical, just where you book the cost differs.

### 3. Best Time to Buy and Sell Stock IV (at most k transactions)  -  Hard
- **Problem:** Maximize profit with **at most `k`** complete buy-sell transactions on a price array.
- **Practice (free):** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/
- **Video (free):** https://neetcode.io/problems/buy-and-sell-stock-iv — also https://www.youtube.com/results?search_query=neetcode+best+time+to+buy+and+sell+stock+iv
- **Idea:** State = `dp[t][hold?]` = best profit having used `t` transactions and currently holding (or not). For each price, for each transaction count, you may sell (closing a transaction) or buy. Big shortcut: if `k >= n//2` you can transact as often as you like — fall back to the greedy "sum every positive delta".
```python
from typing import List

def maxProfit(k: int, prices: List[int]) -> int:
    n = len(prices)
    if n == 0 or k == 0:
        return 0
    if k >= n // 2:                       # unlimited transactions regime
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, n))

    # buy[t] = best profit after opening the t-th transaction (currently holding)
    # sell[t] = best profit after closing the t-th transaction (not holding)
    buy = [float('-inf')] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)   # open t-th trade from t-1 sells
            sell[t] = max(sell[t], buy[t] + p)      # close t-th trade
    return sell[k]

if __name__ == '__main__':
    print(maxProfit(2, [3, 2, 6, 5, 0, 3]))  # 7  -> (2->6) + (0->3)
    print(maxProfit(2, [2, 4, 1]))           # 2
```
- **Complexity:** Time O(n*k), Space O(k).
- **Key insight / gotcha:** Process `buy[t]` then `sell[t]` left-to-right within a day so a transaction can open and close on the same iteration's chain (a length-1 hold). The `k >= n//2` shortcut is what keeps huge `k` from blowing up the table — without it the intended O(n*k) is fine but the unlimited regime is cleaner and avoids overflow of an oversized `k`.
- **Follow-up:** "Exactly k transactions (not 'at most')?" Drop the unlimited shortcut and initialize so unused transactions are illegal; or compute at-most-k and at-most-(k-1) and difference, depending on the exact phrasing. **Stock III** is just this with `k = 2`.

---

# Group 2 - Interval DP

**Recognition cue:** you process a 1D array by repeatedly **removing / merging / cutting** elements, and the cost of an action depends on the elements *adjacent* to it at the time you act. Brute force is "try every order" (factorial). The fix: define `dp[i][j]` over a sub-range and choose `k` = the **last** thing you act on in `[i, j]`, so that when you act on `k` its left/right neighbors are the fixed range boundaries (`i-1`, `j+1`). Fill by increasing range length. Archetype = **Matrix Chain Multiplication** (`dp[i][j]` = min scalar multiplications to multiply matrices `i..j`, split at `k`).

### 1. Burst Balloons  -  Hard
- **Problem:** Each balloon `i` has a value; bursting it yields `nums[i-1] * nums[i] * nums[i+1]` (out-of-range neighbors count as 1), and the burst removes it so neighbors become adjacent. Maximize total coins.
- **Practice (free):** https://leetcode.com/problems/burst-balloons/
- **Video (free):** https://neetcode.io/problems/burst-balloons
- **Idea:** Don't think "which to burst first" — think **"which balloon `k` is burst *last* in the open range `(i, j)`"**. When `k` is last, its neighbors are exactly the padded boundaries `i` and `j`, so its gain is `nums[i]*nums[k]*nums[j]` plus the two independent sub-ranges.
```python
from typing import List

def maxCoins(nums: List[int]) -> int:
    vals = [1] + nums + [1]               # pad both ends with virtual 1s
    n = len(vals)
    # dp[i][j] = max coins from bursting all balloons strictly between i and j
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):            # distance between the open boundaries
        for i in range(n - length):
            j = i + length
            for k in range(i + 1, j):     # k = last balloon burst in (i, j)
                gain = vals[i] * vals[k] * vals[j]
                dp[i][j] = max(dp[i][j], dp[i][k] + gain + dp[k][j])
    return dp[0][n - 1]

if __name__ == '__main__':
    print(maxCoins([3, 1, 5, 8]))  # 167
    print(maxCoins([1, 5]))        # 10
```
- **Complexity:** Time O(n^3), Space O(n^2).
- **Key insight / gotcha:** The whole problem hinges on "**last** to burst", not "first". Picking first makes the subproblems overlap (the removed balloon changes both halves' neighbors); picking last keeps the two halves independent because `k`'s neighbors are frozen at `i` and `j`. Pad with `1`s so edge balloons have well-defined neighbors.
- **Follow-up:** "Why not greedy / why is order-of-burst exponential naively?" There are `n!` burst orders; the interval DP collapses them because every order's value decomposes by its last-burst element recursively.

### 2. Minimum Cost to Cut a Stick  -  Hard
- **Problem:** A stick of length `n` has cut positions `cuts`. Cutting a segment costs its current length; you may cut in any order. Minimize total cost.
- **Practice (free):** https://leetcode.com/problems/minimum-cost-to-cut-a-stick/
- **Video (free):** https://www.youtube.com/results?search_query=takeuforward+minimum+cost+to+cut+a+stick — also https://www.youtube.com/results?search_query=neetcode+minimum+cost+to+cut+a+stick
- **Idea:** Sort the cut positions and pad with the stick's two ends `0` and `n`. `dp[i][j]` = min cost to make all cuts strictly between sorted positions `i` and `j`. Choose `k` = the **first** cut made in that segment; its cost is the segment length `pos[j] - pos[i]`, then recurse on the two halves.
```python
from typing import List

def minCost(n: int, cuts: List[int]) -> int:
    pos = sorted(cuts) + [0, n]
    pos.sort()                            # boundaries 0 and n included
    m = len(pos)
    # dp[i][j] = min cost to perform every cut strictly between pos[i] and pos[j]
    dp = [[0] * m for _ in range(m)]
    for length in range(2, m):            # gap between boundary indices
        for i in range(m - length):
            j = i + length
            best = float('inf')
            for k in range(i + 1, j):     # k = a cut made first in this segment
                best = min(best, dp[i][k] + dp[k][j] + (pos[j] - pos[i]))
            dp[i][j] = best
    return dp[0][m - 1]

if __name__ == '__main__':
    print(minCost(7, [1, 3, 4, 5]))   # 16
    print(minCost(9, [5, 6, 1, 4, 2]))  # 22
```
- **Complexity:** Time O(m^3) where `m = len(cuts)`, Space O(m^2).
- **Key insight / gotcha:** Sorting the cuts is mandatory — the cost of cutting a segment is the distance between its *current* end boundaries, which only makes sense once cuts are ordered. The cost `pos[j]-pos[i]` is the same regardless of which `k` you pick (it's the segment being cut), so only the recursive halves differ.
- **Follow-up:** "First vs last cut — does it matter which you fix?" Here the segment-length cost is independent of `k`, so fixing "first cut = k" is natural; in Burst Balloons the per-action gain *depends* on `k`'s neighbors, which is why "last" is forced. Recognizing which to fix is the interval-DP skill.

### 3. Matrix Chain Multiplication (the archetype)  -  Hard
- **Problem:** Given matrix dimensions `dims` (matrix `i` is `dims[i] x dims[i+1]`), parenthesize the chain to minimize scalar multiplications.
- **Practice:** No exact LeetCode problem; closest free practice is the interval-DP family above plus GeeksforGeeks "Matrix Chain Multiplication". (LeetCode 1039 *Minimum Score Triangulation of a Polygon* is the same recurrence and **free**: https://leetcode.com/problems/minimum-score-triangulation-of-a-polygon/ )
- **Video (free):** https://www.youtube.com/results?search_query=abdul+bari+matrix+chain+multiplication — also https://www.youtube.com/results?search_query=takeuforward+matrix+chain+multiplication
- **Idea:** `dp[i][j]` = min cost to multiply matrices `i..j`. Split at `k`: the cost is the two sub-products plus the cost of multiplying the two resulting matrices, `dims[i]*dims[k+1]*dims[j+1]`.
```python
from typing import List

def matrix_chain_order(dims: List[int]) -> int:
    # dims has len = (#matrices + 1); matrix m spans dims[m]..dims[m+1]
    n = len(dims) - 1                     # number of matrices
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):        # chain length (#matrices in the range)
        for i in range(n - length + 1):
            j = i + length - 1
            best = float('inf')
            for k in range(i, j):         # split: (i..k)(k+1..j)
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                best = min(best, cost)
            dp[i][j] = best
    return dp[0][n - 1]

if __name__ == '__main__':
    print(matrix_chain_order([40, 20, 30, 10, 30]))  # 26000
    print(matrix_chain_order([10, 20, 30]))          # 6000
```
- **Complexity:** Time O(n^3), Space O(n^2).
- **Key insight / gotcha:** The split point `k` here is "where the *outermost* multiplication happens" — the last multiply combines the `(i..k)` block with the `(k+1..j)` block. This "split into two independent halves glued by a boundary cost" is the canonical interval-DP move that Burst Balloons and Cut-a-Stick both reuse.
- **Follow-up:** "Reconstruct the optimal parenthesization." Store the winning `k` in a `split[i][j]` table and recursively print `( ... )` around the split point.

---

# Group 3 - Bitmask DP

**Recognition cue:** **`n` is tiny (n <= ~20)** and the natural state is "which subset of the `n` items have I already used/visited/assigned". That subset is an integer bitmask. You're effectively doing DP over the `2^n` subsets, often combined with a second small dimension ("...and I'm currently at node `i`"). If the constraints scream `n <= 20` and the problem is about covering/visiting/partitioning a set, reach for a bitmask before anything else.

### 1. Partition to K Equal Sum Subsets  -  Medium (hard in practice)
- **Problem:** Given `nums` and integer `k`, decide whether you can partition all elements into `k` non-empty subsets of equal sum.
- **Practice (free):** https://leetcode.com/problems/partition-to-k-equal-sum-subsets/
- **Video (free):** https://neetcode.io/problems/partition-to-k-equal-sum-subsets
- **Idea:** Target per subset = `total / k`. `dp[mask]` = the remaining sum *modulo target* of the current (partially filled) bucket after using exactly the elements in `mask` (or `-1` if `mask` is unreachable). Add one unused element at a time; only add it if it fits in the current bucket's remaining room.
```python
from typing import List

def canPartitionKSubsets(nums: List[int], k: int) -> bool:
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    n = len(nums)
    if any(x > target for x in nums):
        return False
    nums.sort(reverse=True)               # fail fast / pruning
    full = (1 << n) - 1
    # dp[mask] = used-sum mod target for elements in mask; -1 if mask unreachable
    dp = [-1] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] == -1:
            continue
        for b in range(n):
            if mask >> b & 1:
                continue                  # b already used
            if dp[mask] + nums[b] > target:
                continue                  # doesn't fit the current bucket
            nxt = mask | (1 << b)
            if dp[nxt] == -1:
                dp[nxt] = (dp[mask] + nums[b]) % target
    return dp[full] == 0

if __name__ == '__main__':
    print(canPartitionKSubsets([4, 3, 2, 3, 5, 2, 1], 4))  # True
    print(canPartitionKSubsets([1, 2, 3, 4], 3))           # False
```
- **Complexity:** Time O(2^n * n), Space O(2^n).
- **Key insight / gotcha:** Storing the bucket fill as `(used_sum) % target` is the trick that lets a single `dp[mask]` represent "we've completed some whole buckets and are partway through the next". When a partial sum hits exactly `target` it wraps to `0`, transparently starting a fresh bucket. Reaching `dp[full] == 0` means the last bucket closed cleanly. Sorting descending + the per-element fit check prune hard.
- **Follow-up:** "Backtracking instead?" A DFS that greedily fills one bucket at a time with sorting + skip-duplicate-failures pruning is also standard and sometimes faster for small `k`; the bitmask DP is the cleaner *worst-case* bound.

### 2. Shortest Path Visiting All Nodes  -  Hard
- **Problem:** Given an undirected connected graph (`n <= 12`), find the length of the shortest walk that visits *every* node; you may start/end anywhere and revisit nodes and edges.
- **Practice (free):** https://leetcode.com/problems/shortest-path-visiting-all-nodes/
- **Video (free):** https://www.youtube.com/results?search_query=shortest+path+visiting+all+nodes+bitmask+bfs
- **Idea:** State = `(node, mask)` where `mask` is the set of visited nodes. **BFS** over these states finds the shortest path because every edge has weight 1. Start by seeding the queue with `(i, 1<<i)` for every node simultaneously (any start is allowed); the answer is the first time any state reaches `mask == full`.
```python
from collections import deque
from typing import List

def shortestPathLength(graph: List[List[int]]) -> int:
    n = len(graph)
    if n == 1:
        return 0
    full = (1 << n) - 1
    # multi-source BFS: every node is a valid starting point
    queue = deque((i, 1 << i, 0) for i in range(n))   # (node, visited_mask, dist)
    seen = {(i, 1 << i) for i in range(n)}
    while queue:
        node, mask, dist = queue.popleft()
        if mask == full:
            return dist
        for nxt in graph[node]:
            nmask = mask | (1 << nxt)
            if (nxt, nmask) not in seen:
                seen.add((nxt, nmask))
                queue.append((nxt, nmask, dist + 1))
    return 0  # graph is connected, so this is unreachable

if __name__ == '__main__':
    print(shortestPathLength([[1, 2, 3], [0], [0], [0]]))  # 4
    print(shortestPathLength([[1], [0, 2, 4], [1, 3], [2], [1]]))  # 5
```
- **Complexity:** Time O(2^n * n^2) (states = `n * 2^n`, each expands to <= n neighbors), Space O(2^n * n).
- **Key insight / gotcha:** This is **bitmask + BFS**, not pure tabular DP — because edges are unit-weight, the *first* arrival at a `(node, full)` state is optimal, and revisiting nodes is allowed (so a plain visited-set over *nodes* is wrong; you must key `seen` on `(node, mask)`). Seeding all `n` start states at once handles "start anywhere".
- **Follow-up:** "Weighted edges?" BFS no longer suffices — use Dijkstra over `(node, mask)` states, or Held-Karp DP (`dp[mask][i]`) for the full TSP, which is the next problem's territory.

### 3. Traveling Salesman / Held-Karp (the bitmask archetype)  -  Hard
- **Problem:** Given a cost matrix between `n` cities (`n <= ~16`), find the min-cost tour that starts at city 0, visits every city once, and returns to 0.
- **Practice:** No standard LeetCode problem (TSP); the bitmask technique is the same one **Partition to K Equal Sum Subsets** and **Shortest Path Visiting All Nodes** above test. Closest free LeetCode is 943 *Find the Shortest Superstring* (Premium-adjacent but free) — same `dp[mask][i]` shape.
- **Video (free):** https://www.youtube.com/results?search_query=held+karp+tsp+bitmask+dp
- **Idea:** `dp[mask][i]` = min cost of a path that starts at 0, visits exactly the set `mask`, and ends at city `i`. Extend by moving to an unvisited `j`. Answer adds the return edge `i -> 0`.
```python
from typing import List

def tsp(cost: List[List[int]]) -> int:
    n = len(cost)
    full = (1 << n) - 1
    INF = float('inf')
    # dp[mask][i] = min cost path visiting `mask`, starting at 0, ending at i
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                          # only city 0 visited, sitting at 0
    for mask in range(1 << n):
        for i in range(n):
            if dp[mask][i] == INF or not (mask >> i & 1):
                continue
            for j in range(n):
                if mask >> j & 1:
                    continue              # j already visited
                nmask = mask | (1 << j)
                if dp[mask][i] + cost[i][j] < dp[nmask][j]:
                    dp[nmask][j] = dp[mask][i] + cost[i][j]
    return min(dp[full][i] + cost[i][0] for i in range(n))

if __name__ == '__main__':
    grid = [[0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]]
    print(tsp(grid))  # 80
```
- **Complexity:** Time O(2^n * n^2), Space O(2^n * n).
- **Key insight / gotcha:** The second state dimension "...ending at node `i`" is what distinguishes Held-Karp from a plain `dp[mask]` — you need to know *where* the path currently is to extend it. Iterating `mask` in ascending integer order guarantees every subset is finalized before its supersets read it.
- **Follow-up:** "n up to 20?" `2^20 * 20^2 ~= 400M` is borderline; prune with branch-and-bound or accept that exact TSP beyond ~20 needs heuristics. This is why bitmask DP lives and dies by the `n <= 20` constraint.

---

# Group 4 - Tree DP

**Recognition cue:** the input is a **binary tree or general tree** and the answer at a node is computed from the answers at its **children**, usually with a per-node *choice* whose effect propagates one level up (taking a node forbids/affects the choice at its parent or children). Implement as a **post-order DFS returning a small tuple** per node; the parent merges its children's tuples. No table, no explicit ordering — recursion handles it.

> Also included here: **Longest Arithmetic Subsequence**, which is *not* tree DP but a hashmap-keyed DP `dp[i][diff]`. It's grouped at the end as a "state shape that doesn't fit a flat array" companion to round out the advanced-DP toolkit.

### 1. House Robber III  -  Medium
- **Problem:** Houses form a binary tree; you can't rob two directly-connected (parent-child) houses. Maximize the loot.
- **Practice (free):** https://leetcode.com/problems/house-robber-iii/
- **Video (free):** https://neetcode.io/problems/house-robber-iii
- **Idea:** Post-order DFS returning `(rob, skip)` per node: `rob` = node's value plus *skip* of both children (can't rob children); `skip` = best (rob-or-skip) of each child independently. Answer = `max` of the root's pair.
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def rob(root: TreeNode) -> int:
    def dfs(node):
        if not node:
            return (0, 0)                 # (rob_this, skip_this)
        l_rob, l_skip = dfs(node.left)
        r_rob, r_skip = dfs(node.right)
        rob_this = node.val + l_skip + r_skip      # take node => children skipped
        skip_this = max(l_rob, l_skip) + max(r_rob, r_skip)  # children free
        return (rob_this, skip_this)
    return max(dfs(root))

if __name__ == '__main__':
    #     3
    #    / \
    #   2   3
    #    \   \
    #     3   1
    root = TreeNode(3, TreeNode(2, None, TreeNode(3)), TreeNode(3, None, TreeNode(1)))
    print(rob(root))  # 7  -> 3 (root) + 3 + 1
```
- **Complexity:** Time O(n), Space O(h) recursion (h = tree height).
- **Key insight / gotcha:** Returning a *pair* per node is what avoids the exponential naive recursion that recomputes grandchildren. The classic bug is returning a single number — you then can't tell the parent "what's the best where you *didn't* rob me", which it needs to decide its own choice.
- **Follow-up:** "Linear House Robber (file 15) vs this?" Same take/skip logic; the tree version just merges two children instead of one linear predecessor. The pair-of-states trick generalizes any "adjacent-exclusion" DP onto a tree.

### 2. Binary Tree Cameras  -  Hard
- **Problem:** Place cameras on tree nodes; a camera covers its own node, its parent, and its immediate children. Find the minimum number of cameras to cover every node.
- **Practice (free):** https://leetcode.com/problems/binary-tree-cameras/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+binary+tree+cameras
- **Idea:** Greedy post-order DFS with three node states bubbling up: `0` = node is **uncovered** (needs a parent camera), `1` = node is **covered but has no camera**, `2` = node **has a camera**. Put a camera only when a child reports uncovered (`0`); install as high as possible (let leaves stay uncovered and force their parents to hold cameras).
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def minCameraCover(root: TreeNode) -> int:
    NEED, OK, CAM = 0, 1, 2                # uncovered / covered / has-camera
    cameras = 0
    def dfs(node):
        nonlocal cameras
        if not node:
            return OK                      # null children are considered covered
        l, r = dfs(node.left), dfs(node.right)
        if l == NEED or r == NEED:         # a child is uncovered => must place here
            cameras += 1
            return CAM
        if l == CAM or r == CAM:           # a child covers this node
            return OK
        return NEED                        # both children covered but neither has a cam
    # if the root ends up uncovered, it needs one more camera
    return cameras + (1 if dfs(root) == NEED else 0)

if __name__ == '__main__':
    #       a(root)    cameras bubble up from the leaves: d covers f+d+b's line,
    #      / \         b covers e, root covers c -> 3 total
    #     b   c
    #    / \
    #   d   e
    #  /
    # f
    f = TreeNode(0)
    d = TreeNode(0, f, None)
    e = TreeNode(0)
    b = TreeNode(0, d, e)
    c = TreeNode(0)
    root = TreeNode(0, b, c)
    print(minCameraCover(root))  # 3
```
- **Complexity:** Time O(n), Space O(h) recursion.
- **Key insight / gotcha:** The "greedy" is provably optimal here: never put a camera on a leaf (wasteful) — push coverage upward so each camera covers a parent + up to two children. Treat `None` as `OK` (covered), or leaves would wrongly demand cameras on themselves. Don't forget the final root-uncovered check after the DFS.
- **Follow-up:** "Express as pure min-DP instead of greedy states?" You can use `dp[node][state]` with three states (has-camera / covered-no-camera / not-covered) and minimize, which is more mechanical but equivalent; the greedy three-state return is the slick interview version.

### 3. Longest Arithmetic Subsequence (hashmap DP)  -  Medium
- **Problem:** Find the length of the longest subsequence of `nums` that forms an arithmetic progression (constant common difference).
- **Practice (free):** https://leetcode.com/problems/longest-arithmetic-subsequence/
- **Video (free):** https://www.youtube.com/results?search_query=longest+arithmetic+subsequence+dp
- **Idea:** `dp[i]` is a **dict** mapping a common difference `d` to the length of the longest arithmetic subsequence ending at index `i` with that difference. For each pair `(j, i)` with `j < i`, the difference is `d = nums[i] - nums[j]`, and `dp[i][d] = dp[j].get(d, 1) + 1`.
```python
from typing import List

def longestArithSeqLength(nums: List[int]) -> int:
    n = len(nums)
    dp = [dict() for _ in range(n)]       # dp[i][d] = best length ending at i, step d
    best = 1
    for i in range(n):
        for j in range(i):
            d = nums[i] - nums[j]
            dp[i][d] = dp[j].get(d, 1) + 1   # extend j's run, or start a length-2 run
            best = max(best, dp[i][d])
    return best

if __name__ == '__main__':
    print(longestArithSeqLength([3, 6, 9, 12]))  # 4
    print(longestArithSeqLength([9, 4, 7, 2, 10]))  # 3  -> 4,7,10
    print(longestArithSeqLength([20, 1, 15, 3, 10, 5, 8]))  # 4 -> 20,15,10,5
```
- **Complexity:** Time O(n^2), Space O(n^2) (each `dp[i]` can hold up to `i` differences).
- **Key insight / gotcha:** The state needs the *difference* in its key, which can't index a flat array (differences can be negative / large), so a per-index hashmap is the natural structure. `dp[j].get(d, 1) + 1` defaults to 1 because `nums[j]` alone is a length-1 run that `nums[i]` extends to 2. This "DP keyed by a value, not an index" is a recurring advanced shape (e.g. also in Longest Arithmetic Subsequence of Given Difference, which is O(n) with one global dict).
- **Follow-up:** "Common difference is *fixed* / given?" Then a single global `dict` mapping value -> best length suffices: `best[x] = best.get(x - d, 0) + 1`, giving O(n) time.

## Self-rating checklist
- [ ] I can recognise which of the four sub-patterns applies in <30s (state vs interval vs bitmask vs tree)
- [ ] I can write the interval-DP template (increasing length + inner split `k`) from memory
- [ ] I can write the bitmask-DP template (ascending masks, bit ops) from memory
- [ ] I can write the tree-DP post-order tuple template from memory
- [ ] State machine — Cooldown (3 states, buy only from rest) 🔴/🟡/🟢
- [ ] State machine — Transaction Fee (charge fee once) 🔴/🟡/🟢
- [ ] State machine — Stock IV / k transactions (buy[t]/sell[t], k>=n/2 shortcut) 🔴/🟡/🟢
- [ ] Interval — Burst Balloons (pick LAST to burst, pad with 1s) 🔴/🟡/🟢
- [ ] Interval — Min Cost to Cut a Stick (sort cuts, pad with 0/n) 🔴/🟡/🟢
- [ ] Interval — Matrix Chain Multiplication (the archetype split) 🔴/🟡/🟢
- [ ] Bitmask — Partition to K Equal Sum Subsets (dp[mask] = sum % target) 🔴/🟡/🟢
- [ ] Bitmask — Shortest Path Visiting All Nodes (bitmask + BFS, key on (node,mask)) 🔴/🟡/🟢
- [ ] Bitmask — TSP / Held-Karp (dp[mask][i], the archetype) 🔴/🟡/🟢
- [ ] Tree — House Robber III (return (rob, skip) pair) 🔴/🟡/🟢
- [ ] Tree — Binary Tree Cameras (3-state greedy bubble-up) 🔴/🟡/🟢
- [ ] Hashmap DP — Longest Arithmetic Subsequence (dp[i][d]) 🔴/🟡/🟢

## Resources
- **Free:** NeetCode roadmap, advanced DP problems are spread across the 1-D and 2-D DP groups — https://neetcode.io/roadmap ; takeUforward/Striver "DP on Stocks", "Partition DP / MCM" and "DP on Trees" playlists — https://www.youtube.com/results?search_query=striver+partition+dp+mcm and https://www.youtube.com/results?search_query=striver+dp+on+stocks
- **Free:** CP-Algorithms "Bitmask DP" / "SOS DP" reference — https://cp-algorithms.com/ ; Errichto bitmask DP video — https://www.youtube.com/results?search_query=errichto+bitmask+dp
- **Free (interval DP):** abdul bari Matrix Chain Multiplication (the cleanest MCM derivation) — https://www.youtube.com/results?search_query=abdul+bari+matrix+chain+multiplication
- **Paid (optional):** DesignGurus "Grokking Dynamic Programming for Coding Interviews" (advanced patterns module) — https://www.designgurus.io (free alternative: the NeetCode roadmap + Striver playlists above cover every problem in this file with video walkthroughs).

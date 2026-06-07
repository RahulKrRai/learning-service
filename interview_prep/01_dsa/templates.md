# DSA Templates Library (Python 3)

Your memorize-once reference. Each template is correct, copy-pasteable, and zero-indexed. Drill these until you can reproduce any of them in under 60 seconds on a blank Google Doc (no autocomplete, no run button).

How to use this page:
- **Internalize the shape**, not the variable names. The control flow is the asset.
- For every template there is a **"Use when"** trigger. Pattern-match the problem to the trigger first, then pour in the details.
- Watch the invariant comments — those are the lines you will fumble under pressure.

---

## 1. Two Pointers (opposite ends)

**Use when:** array/string is **sorted** (or you can sort it) and you need a pair/triple satisfying a relation, or you're comparing from both ends (palindrome, container with most water, reverse in place).

```python
def two_sum_sorted(nums, target):
    # nums is sorted ascending. Returns 0-based indices of a pair summing to target.
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo, hi]
        elif s < target:
            lo += 1          # need a bigger sum -> move left pointer right
        else:
            hi -= 1          # need a smaller sum -> move right pointer left
    return [-1, -1]
```

---

## 2. Sliding Window (variable size)

**Use when:** longest/shortest **contiguous** subarray/substring meeting a constraint (at most K distinct, sum >= target, no repeating chars). Window grows on the right, shrinks from the left when the constraint breaks.

```python
def longest_substring_k_distinct(s, k):
    from collections import defaultdict
    count = defaultdict(int)
    left = 0
    best = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        # shrink until the window is valid again
        while len(count) > k:
            count[s[left]] -= 1
            if count[s[left]] == 0:
                del count[s[left]]
            left += 1
        best = max(best, right - left + 1)   # window [left, right] is valid here
    return best
```

---

## 3. Sliding Window (fixed size K)

**Use when:** max/min/average over **every window of fixed length K** (max sum of size-K subarray, count anagrams). Add the entering element, drop the leaving element.

```python
def max_sum_window(nums, k):
    if len(nums) < k:
        return None
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]   # slide: add new, remove old
        best = max(best, window)
    return best
```

---

## 4. Prefix Sum (+ subarray-sum-equals-K)

**Use when:** many range-sum queries, or counting subarrays whose sum equals K. `prefix[i+1] - prefix[i] = sum(nums[i:j])`; a hashmap of seen prefix sums turns "subarray sum == K" into O(n).

```python
def subarray_sum_equals_k(nums, k):
    from collections import defaultdict
    seen = defaultdict(int)
    seen[0] = 1            # empty prefix; lets a prefix itself equal k
    running = 0
    count = 0
    for x in nums:
        running += x
        count += seen[running - k]   # how many earlier prefixes make a k-sum window
        seen[running] += 1
    return count
```

---

## 5. Binary Search — lower / upper bound

**Use when:** searching a **sorted** array; you need the first index >= target (lower) or first index > target (upper). These two cover "exists?", "insertion point", "count of value", and dedup.

```python
def lower_bound(nums, target):
    # first index i with nums[i] >= target; len(nums) if none.
    lo, hi = 0, len(nums)          # half-open [lo, hi)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(nums, target):
    # first index i with nums[i] > target; len(nums) if none.
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
# Python stdlib: from bisect import bisect_left (lower), bisect_right (upper).
```

---

## 6. Binary Search on the Answer Space

**Use when:** the answer is a number in a range and there's a **monotonic** feasibility check `ok(x)` (false...false, true...true). Min capacity to ship in D days, Koko eating bananas, split array largest sum, min days to make bouquets.

```python
def min_feasible(lo, hi, ok):
    # ok(x) is monotonic: once True it stays True. Returns smallest x with ok(x) True.
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid           # mid works; try to do better (smaller)
        else:
            lo = mid + 1       # mid too small; need larger
    return lo                  # lo == hi == smallest feasible answer
```

---

## 7. Monotonic Stack (next greater element)

**Use when:** for each element you need the **next/previous greater or smaller** element, or you're spanning ranges (daily temperatures, stock span, largest rectangle in histogram, trapping rain water).

```python
def next_greater(nums):
    # res[i] = index of the next element to the right strictly greater than nums[i], else -1.
    n = len(nums)
    res = [-1] * n
    stack = []                 # holds indices; values are decreasing from bottom to top
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = i   # x is the next-greater for everything we pop
        stack.append(i)
    return res
```

---

## 8. Fast / Slow Pointers (Floyd's cycle detection)

**Use when:** linked-list cycle detection, finding cycle start, middle of a list, happy number. Slow moves 1, fast moves 2; they meet inside any cycle.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:               # met inside the cycle
            ptr = head
            while ptr is not slow:     # reset one pointer to head, advance both by 1
                ptr, slow = ptr.next, slow.next
            return ptr                 # node where the cycle begins
    return None
```

---

## 9. Reverse a Linked List (iterative)

**Use when:** reversing a list or a sublist (reverse-K-group, palindrome list, reorder list). Memorize the three-line pointer dance cold.

```python
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next     # save next
        curr.next = prev    # flip the link
        prev = curr         # advance prev
        curr = nxt          # advance curr
    return prev             # new head
```

---

## 10. BFS on a Grid

**Use when:** shortest path / flood fill on a 2D matrix with uniform edge cost (number of islands, rotting oranges, shortest path in binary matrix, walls and gates).

```python
def bfs_grid(grid, start):
    from collections import deque
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    q = deque([(sr, sc)])
    seen = {(sr, sc)}
    dist = 0
    while q:
        for _ in range(len(q)):        # process one "ring" -> dist is layer count
            r, c = q.popleft()
            # ... use (r, c) ...
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen \
                        and grid[nr][nc] != '#':       # adjust your blocked test
                    seen.add((nr, nc))
                    q.append((nr, nc))
        dist += 1
    return dist
```

---

## 11. BFS on a Graph (adjacency list)

**Use when:** shortest hops in an unweighted graph, level/distance from a source, bipartite check, word ladder.

```python
def bfs_graph(adj, src):
    # adj: dict node -> list of neighbors. Returns dist from src to each reachable node.
    from collections import deque
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:          # first time we see v = shortest hop count
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

---

## 12. BFS — Tree Level Order

**Use when:** process a binary tree level by level (level-order, right-side view, zigzag, max width, level averages).

```python
def level_order(root):
    from collections import deque
    if not root:
        return []
    levels = []
    q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):        # exactly the nodes on this level
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        levels.append(level)
    return levels
```

---

## 13. DFS — Recursive and Iterative (graph)

**Use when:** connectivity, path existence, full traversal, cycle detection. Recursion is cleaner; keep the iterative version for "recursion depth" follow-ups.

```python
def dfs_recursive(adj, src):
    seen = set()
    def go(u):
        seen.add(u)
        for v in adj[u]:
            if v not in seen:
                go(v)
    go(src)
    return seen

def dfs_iterative(adj, src):
    seen = set()
    stack = [src]
    while stack:
        u = stack.pop()
        if u in seen:                  # guard: a node can be pushed multiple times
            continue
        seen.add(u)
        for v in adj[u]:
            if v not in seen:
                stack.append(v)
    return seen
```

---

## 14. Topological Sort — Kahn's (BFS) and DFS

**Use when:** ordering a DAG with prerequisites (course schedule I/II, build order, alien dictionary). Kahn's also detects cycles (output length < N means a cycle).

```python
def topo_kahn(adj, n):
    # nodes 0..n-1; adj[u] -> nodes that depend on u (edge u -> v). Returns [] if cyclic.
    from collections import deque
    indeg = [0] * n
    for u in range(n):
        for v in adj[u]:
            indeg[v] += 1
    q = deque(u for u in range(n) if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []   # [] => cycle

def topo_dfs(adj, n):
    seen = [0] * n          # 0=unvisited, 1=in-progress, 2=done
    order = []
    cyclic = False
    def go(u):
        nonlocal cyclic
        seen[u] = 1
        for v in adj[u]:
            if seen[v] == 1:        # back edge -> cycle
                cyclic = True
            elif seen[v] == 0:
                go(v)
        seen[u] = 2
        order.append(u)             # post-order
    for u in range(n):
        if seen[u] == 0:
            go(u)
    return [] if cyclic else order[::-1]   # reverse post-order
```

---

## 15. Union-Find (path compression + union by rank)

**Use when:** connectivity / grouping under merges (number of provinces, redundant connection, accounts merge, Kruskal's MST, detect cycle in undirected graph). Near-O(1) amortized per op.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n              # number of disjoint components

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression (halving)
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False            # already connected (e.g. cycle edge)
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra         # attach smaller tree under larger
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True
```

---

## 16. Dijkstra (min-heap)

**Use when:** shortest path with **non-negative** weights (network delay time, cheapest flights within K stops, path with min effort). For negative edges use Bellman-Ford instead.

```python
def dijkstra(adj, src, n):
    # adj: dict u -> list of (v, weight). Returns dist[] with inf for unreachable.
    import heapq
    dist = [float('inf')] * n
    dist[src] = 0
    pq = [(0, src)]                 # (distance, node)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:             # stale entry -> skip
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist
```

---

## 17. Backtracking Skeleton

**Use when:** enumerate all valid combinations / permutations / subsets / placements (subsets, combination sum, permutations, N-queens, word search, palindrome partitioning). Choose -> recurse -> undo.

```python
def backtrack_subsets(nums):
    res = []
    path = []
    def go(start):
        res.append(path[:])         # record the current choice (copy!)
        for i in range(start, len(nums)):
            # to skip duplicates on a sorted input:
            # if i > start and nums[i] == nums[i-1]: continue
            path.append(nums[i])    # choose
            go(i + 1)               # explore (use i to allow reuse, i+1 to move on)
            path.pop()              # un-choose (backtrack)
    go(0)
    return res
```

---

## 18. Trie (node + insert + search)

**Use when:** prefix queries, autocomplete, word dictionaries, word search II, replace-words, maximum XOR (bit trie variant).

```python
class TrieNode:
    def __init__(self):
        self.children = {}          # char -> TrieNode
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

---

## 19. Heap — Top K

**Use when:** K largest/smallest, K most frequent, K closest points, merge K sorted lists. A min-heap of size K keeps the K largest in O(n log K).

```python
def top_k_largest(nums, k):
    import heapq
    heap = []                       # min-heap of size <= k
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)     # evict the smallest -> heap holds k largest
    return heap                     # the k largest, smallest of them at heap[0]

def top_k_frequent(nums, k):
    import heapq
    from collections import Counter
    freq = Counter(nums)
    return heapq.nlargest(k, freq.keys(), key=freq.get)
```

---

## 20. 1D DP Skeleton

**Use when:** linear sequence decisions (climbing stairs, house robber, coin change, longest increasing subsequence, decode ways). Define dp[i] precisely, set base cases, then fill left to right.

```python
def climb_stairs(n):
    # dp[i] = number of distinct ways to reach step i.
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2             # base cases
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]   # transition
    return dp[n]
    # space-optimized: keep only the last two values (a, b = b, a + b)
```

---

## 21. 2D DP Skeleton

**Use when:** two interacting sequences or a grid (edit distance, LCS, unique paths, knapsack, min path sum). dp[i][j] is the answer for the first i of one input and first j of the other.

```python
def longest_common_subsequence(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # dp[i][j] = LCS of a[:i], b[:j]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1          # match: extend diagonal
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # skip one char
    return dp[m][n]
```

---

## 22. Interval Merge

**Use when:** overlapping intervals (merge intervals, insert interval, meeting rooms, employee free time). Sort by start, then sweep and merge when the next start <= current end.

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])   # sort by start
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:   # overlaps the last merged interval
            merged[-1][1] = max(merged[-1][1], end)   # extend it
        else:
            merged.append([start, end])     # disjoint -> start a new interval
    return merged
```

---

### Quick trigger -> template index

| Signal in the prompt | Template |
|---|---|
| sorted array, find a pair | 1 two pointers |
| longest/shortest substring with constraint | 2 variable window |
| every window of size K | 3 fixed window |
| count subarrays summing to K | 4 prefix sum |
| sorted, "first/last position", "insert at" | 5 lower/upper bound |
| "minimum X such that feasible", monotonic check | 6 binary search on answer |
| next/previous greater/smaller | 7 monotonic stack |
| linked-list cycle / middle | 8 fast-slow |
| reverse linked list/sublist | 9 reverse list |
| shortest path in grid, uniform cost | 10 BFS grid |
| fewest hops unweighted graph | 11 BFS graph |
| tree per-level processing | 12 level order |
| connectivity / full traversal | 13 DFS |
| prerequisites / ordering a DAG | 14 topo sort |
| dynamic connectivity / grouping | 15 union-find |
| shortest path, weighted, non-negative | 16 Dijkstra |
| all combinations/permutations/subsets | 17 backtracking |
| prefix / autocomplete / word dictionary | 18 trie |
| K largest / K frequent / K closest | 19 heap top-k |
| linear sequence decision | 20 1D DP |
| two sequences / grid DP | 21 2D DP |
| overlapping intervals | 22 interval merge |

# Day 6 — Mock Round 2 + Final Review
**Date: April 5 | Simulate Round 2 conditions**

---

## Mock Set — Trees / Graphs / DP

Pick 2 problems. Set a 75-minute timer. No hints.

---

### Problem 1: Binary Tree Maximum Path Sum
Path doesn't have to go through root. Find max sum path.

```python
def max_path_sum(root):
    max_sum = [float('-inf')]

    def dfs(node):
        if not node: return 0
        left = max(dfs(node.left), 0)   # ignore negative paths
        right = max(dfs(node.right), 0)
        # Path through current node
        max_sum[0] = max(max_sum[0], node.val + left + right)
        # Return max single-branch path (can only extend in one direction)
        return node.val + max(left, right)

    dfs(root)
    return max_sum[0]
# Time: O(n), Space: O(h)
```

---

### Problem 2: Rotting Oranges (Multi-source BFS)
Grid of 0 (empty), 1 (fresh), 2 (rotten). Each minute, rotten spreads to adjacent fresh. Min time for all to rot.

```python
from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))  # (row, col, time)
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0: return 0
    max_time = 0
    while queue:
        r, c, time = queue.popleft()
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                max_time = max(max_time, time + 1)
                queue.append((nr, nc, time + 1))

    return max_time if fresh == 0 else -1
# Time: O(m*n), Space: O(m*n)
# Key insight: multi-source BFS — start from ALL rotten oranges simultaneously
```

---

### Problem 3: Network Delay Time (Dijkstra)
Weighted graph, find time for signal to reach all nodes from source k.

```python
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float('inf') for i in range(1, n+1)}
    dist[k] = 0
    heap = [(0, k)]  # (distance, node)

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]: continue  # stale entry
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    max_dist = max(dist.values())
    return max_dist if max_dist != float('inf') else -1
# Time: O((V + E) log V), Space: O(V + E)
```

---

### Problem 4: Partition Equal Subset Sum
Can array be split into two subsets with equal sum?

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0: return False
    target = total // 2

    dp = {0}  # set of achievable sums
    for num in nums:
        dp = {s + num for s in dp} | dp
        if target in dp: return True
    return target in dp

# Classic DP approach:
def can_partition_dp(nums):
    total = sum(nums)
    if total % 2 != 0: return False
    target = total // 2

    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for j in range(target, num - 1, -1):  # reverse to avoid reuse
            dp[j] = dp[j] or dp[j - num]
    return dp[target]
# Time: O(n * target), Space: O(target)
```

---

### Problem 5: Alien Dictionary (Topological Sort)
Given list of words in alien language order, find character order.

```python
from collections import defaultdict, deque

def alien_order(words):
    # Build graph
    adj = defaultdict(set)
    in_degree = {c: 0 for word in words for c in word}

    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        min_len = min(len(w1), len(w2))
        # Check invalid: longer word is prefix of shorter
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in adj[w1[j]]:
                    adj[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break

    # BFS topological sort
    queue = deque([c for c in in_degree if in_degree[c] == 0])
    result = []
    while queue:
        c = queue.popleft()
        result.append(c)
        for neighbor in adj[c]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return "".join(result) if len(result) == len(in_degree) else ""
```

---

### Problem 6: Burst Balloons (Interval DP — Hard)
Burst balloons to maximize coins. Bursting balloon i gives nums[i-1]*nums[i]*nums[i+1].

```python
def max_coins(nums):
    nums = [1] + nums + [1]  # add boundary balloons
    n = len(nums)
    dp = [[0] * n for _ in range(n)]

    # dp[left][right] = max coins from bursting all balloons between left and right (exclusive)
    for length in range(2, n):
        for left in range(0, n - length):
            right = left + length
            for k in range(left + 1, right):  # k is the LAST balloon to burst in range
                dp[left][right] = max(
                    dp[left][right],
                    nums[left] * nums[k] * nums[right] + dp[left][k] + dp[k][right]
                )
    return dp[0][n-1]
# Time: O(n^3), Space: O(n^2)
# Key insight: think of k as the LAST balloon burst (not first) — boundary balloons are still there
```

---

## Final Review — Weak Areas

Use this section on the morning of each interview (April 6 & 7).

### 30-Minute Morning Warmup (April 6 — Round 1)
Solve 1 problem from each:
1. Two Pointers: Container With Most Water
2. Sliding Window: Longest Substring Without Repeating Chars
3. HashMap: Subarray Sum = K

### 30-Minute Morning Warmup (April 7 — Round 2)
Solve 1 problem from each:
1. Tree: Level Order Traversal
2. Graph: Number of Islands
3. DP: Coin Change

---

## Complexity Quick-Check Before Submitting

Always state before submitting:
```
"Time complexity is O(__) because ___."
"Space complexity is O(__) because ___."
"Edge cases I handled: empty input, single element, ___."
```

---

## Possible Follow-Up Questions from Interviewer

- "Can you optimize space further?" → rolling array, two variables
- "What if input is very large?" → streaming approach, external sort
- "What if numbers can be negative?" → can't use sliding window for sum problems
- "Can you do it iteratively instead of recursively?" → use explicit stack
- "What's the difference between BFS and DFS here?" → BFS for shortest path, DFS for all paths/existence

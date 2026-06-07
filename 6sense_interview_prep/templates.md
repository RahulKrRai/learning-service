# Python Templates — Reusable Interview Patterns

Copy-paste ready. Memorize these structures.

---

## Imports (Always Add at Top)
```python
from collections import Counter, defaultdict, deque
import heapq
from typing import List, Optional
```

---

## Two Pointers
```python
left, right = 0, len(arr) - 1
while left < right:
    if condition_met:
        # record result
        left += 1
        right -= 1
    elif need_larger:
        left += 1
    else:
        right -= 1
```

## Sliding Window (Variable Size)
```python
left = 0
window = defaultdict(int)
result = 0
for right in range(len(s)):
    window[s[right]] += 1          # expand
    while invalid(window):         # shrink until valid
        window[s[left]] -= 1
        if window[s[left]] == 0:
            del window[s[left]]
        left += 1
    result = max(result, right - left + 1)
```

## Prefix Sum
```python
prefix = [0] * (len(arr) + 1)
for i, v in enumerate(arr):
    prefix[i+1] = prefix[i] + v
# query: sum(l, r) = prefix[r+1] - prefix[l]

# With HashMap for subarray sum = k:
freq = {0: 1}
running = 0
count = 0
for num in arr:
    running += num
    count += freq.get(running - k, 0)
    freq[running] = freq.get(running, 0) + 1
```

## Binary Search
```python
# Standard
lo, hi = 0, len(arr) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if arr[mid] == target: return mid
    elif arr[mid] < target: lo = mid + 1
    else: hi = mid - 1
return -1

# Find leftmost position satisfying condition
lo, hi = 0, len(arr)
while lo < hi:
    mid = (lo + hi) // 2
    if condition(mid): hi = mid
    else: lo = mid + 1
return lo
```

## BFS (Graph / Grid)
```python
from collections import deque
queue = deque([start])
visited = {start}
steps = 0
while queue:
    for _ in range(len(queue)):   # process level by level
        node = queue.popleft()
        if node == target: return steps
        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    steps += 1
```

## DFS (Graph)
```python
visited = set()
def dfs(node):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor)

# Iterative DFS
stack = [start]
visited = {start}
while stack:
    node = stack.pop()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            stack.append(neighbor)
```

## Tree DFS (Recursive)
```python
def dfs(node):
    if not node: return base_value
    left = dfs(node.left)
    right = dfs(node.right)
    return combine(node.val, left, right)
```

## Tree BFS (Level Order)
```python
result = []
queue = deque([root]) if root else deque()
while queue:
    level = []
    for _ in range(len(queue)):
        node = queue.popleft()
        level.append(node.val)
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)
    result.append(level)
```

## Top-K Heap
```python
import heapq
heap = []
for item in collection:
    heapq.heappush(heap, (priority(item), item))
    if len(heap) > k:
        heapq.heappop(heap)
# heap contains top-k items by priority
```

## 1D DP Template
```python
dp = [initial] * (n + 1)
dp[0] = base_case
for i in range(1, n + 1):
    dp[i] = f(dp[i-1], dp[i-2], ...)  # recurrence
return dp[n]
```

## 2D DP Template (String / Grid)
```python
dp = [[0] * (n + 1) for _ in range(m + 1)]
# Fill base cases: dp[i][0] and dp[0][j]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if match_condition:
            dp[i][j] = dp[i-1][j-1] + 1
        else:
            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
return dp[m][n]
```

## Knapsack (0/1 — Space Optimized)
```python
dp = [0] * (capacity + 1)
for weight, value in items:
    for j in range(capacity, weight - 1, -1):  # REVERSE to avoid reuse
        dp[j] = max(dp[j], dp[j - weight] + value)
```

## Knapsack (Unbounded)
```python
dp = [0] * (capacity + 1)
for weight, value in items:
    for j in range(weight, capacity + 1):  # FORWARD allows reuse
        dp[j] = max(dp[j], dp[j - weight] + value)
```

## Backtracking
```python
result = []
def backtrack(start, current):
    if is_valid_solution(current):
        result.append(list(current))
        return  # or don't return if want all extensions
    for i in range(start, len(nums)):
        if can_prune(i, current): continue
        current.append(nums[i])
        backtrack(i + 1, current)  # i+1 for combinations, i for reuse
        current.pop()  # undo choice
backtrack(0, [])
```

## Monotonic Stack (Next Greater Element)
```python
result = [-1] * len(nums)
stack = []  # stores indices
for i in range(len(nums)):
    while stack and nums[stack[-1]] < nums[i]:
        idx = stack.pop()
        result[idx] = nums[i]  # nums[i] is next greater for idx
    stack.append(i)
```

## Union-Find (Disjoint Set)
```python
parent = list(range(n))
rank = [0] * n

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  # path compression
    return parent[x]

def union(x, y):
    px, py = find(x), find(y)
    if px == py: return False  # already connected
    if rank[px] < rank[py]: px, py = py, px
    parent[py] = px
    if rank[px] == rank[py]: rank[px] += 1
    return True
```

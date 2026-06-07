# 12 - Shortest Path & MST
> When you have a weighted graph and need the cheapest way to reach a node, traverse all edges, or connect everything — reach for Dijkstra, Bellman-Ford, or an MST algorithm.

## When to use it (recognition triggers)
- The graph has **weighted edges** and you want the minimum-cost path from a source (or to all nodes) — and **all weights are non-negative** → **Dijkstra** (lazy, with a min-heap).
- Same, but there's a **hop/edge-count constraint** ("at most K stops"), or weights can be negative, or you must do a fixed number of relaxation rounds → **Bellman-Ford** (relax all edges `V-1` times, or `K+1` times when stops are bounded).
- The "cost" of a path isn't the *sum* of edges but the **max single edge** (min of maximums: minimum effort, swim in rising water, max capacity path) → Dijkstra-style where you `max(running, edge)` instead of `running + edge`. Equivalently binary search + BFS, or Union-Find by sorted edge weight.
- You must **connect every node** with minimum total edge weight (no path/source asked, just "connect all") → **Minimum Spanning Tree**: Prim (grow one tree with a heap) or Kruskal (sort edges + Union-Find).
- Points on a plane with "cost = distance to connect them" → MST on a complete graph (Manhattan/Euclidean weights).
- You must use **every edge exactly once** and return the trail (itinerary, "use all tickets") → **Eulerian path via Hierholzer's algorithm**, not shortest path at all.

## Mental model
- **Dijkstra** is BFS that respects weights: instead of a FIFO queue it pops the globally cheapest unsettled node from a min-heap. The first time you pop a node, its distance is final (greedy invariant — only valid because no edge is negative). Lazy Dijkstra leaves stale entries in the heap and skips them on pop.
- **Bellman-Ford** drops the greedy assumption. It just relaxes every edge repeatedly: after `i` rounds, `dist[v]` is the shortest path using ≤ `i` edges. So bounding rounds to `K+1` directly answers "shortest path with at most K stops" — and you must relax from a **snapshot** of last round's distances so one round can't chain multiple new edges.
- **Min-max path** problems replace `+` with `max`: the cost of a path is its single worst edge, so you greedily expand the frontier by smallest "worst edge so far". Dijkstra's machinery works verbatim with that relaxation.
- **MST** picks `V-1` edges forming a tree of minimum total weight. **Prim** grows one connected blob, always adding the cheapest edge leaving it (Dijkstra-like heap). **Kruskal** sorts all edges globally and adds each one unless it forms a cycle (Union-Find detects cycles). Prim wins on dense graphs, Kruskal on sparse/edge-list graphs.
- **Hierholzer** finds a path/circuit using every edge once: walk forward consuming edges until stuck, and whenever stuck, pop that dead-end node onto the answer and back up. Reversing the popped order yields the Eulerian trail.

## Reusable template(s)
```python
import heapq
from collections import defaultdict
from typing import List, Dict

# --- Dijkstra (lazy, min-heap): single-source shortest paths, weights >= 0 ---
def dijkstra(graph: Dict[int, List[tuple]], src: int, n: int) -> List[float]:
    dist = [float('inf')] * n
    dist[src] = 0
    pq = [(0, src)]                       # (distance_so_far, node)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:                   # stale entry — already settled cheaper
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:              # relax: '+' for sum, 'max(d, w)' for min-max paths
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

# --- Bellman-Ford with a hop limit: shortest path using at most `limit` edges ---
def bellman_ford_k(n: int, edges: List[tuple], src: int, limit: int) -> List[float]:
    dist = [float('inf')] * n
    dist[src] = 0
    for _ in range(limit):                # `limit` = max number of edges allowed
        snap = dist[:]                    # snapshot: relax from last round only
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < snap[v]:
                snap[v] = dist[u] + w
        dist = snap
    return dist

# --- Union-Find: backbone of Kruskal's MST and cycle detection ---
class DSU:
    def __init__(self, n):
        self.par = list(range(n))
        self.rank = [0] * n
    def find(self, x):
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]   # path compression
            x = self.par[x]
        return x
    def union(self, a, b) -> bool:        # returns False if already connected (cycle)
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.par[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

# --- Hierholzer: Eulerian path using every edge exactly once ---
def hierholzer(graph: Dict[str, List[str]], start: str) -> List[str]:
    route, stack = [], [start]
    while stack:
        while graph[stack[-1]]:
            stack.append(graph[stack[-1]].pop())  # consume an edge, go deeper
        route.append(stack.pop())                 # dead end -> commit to answer
    return route[::-1]
```

## Complexity profile
- **Dijkstra (binary heap):** `O(E log V)` time, `O(V + E)` space. Beats the `O(V·E)` you'd get from naive repeated relaxation.
- **Bellman-Ford:** `O(V·E)` (or `O(K·E)` with a hop limit). Slower than Dijkstra but handles negative weights and edge-count constraints Dijkstra cannot.
- **Min-max path (Dijkstra-style):** `O(E log V)` = `O(R·C·log(R·C))` on a grid; binary-search + BFS variant is `O(R·C·log(maxVal))`.
- **MST — Prim (heap):** `O(E log V)`; on a dense `V×V` graph the `O(V²)` array version is better. **Kruskal:** `O(E log E)` dominated by the sort, plus near-`O(E·α(V))` for Union-Find.
- **Hierholzer:** `O(E log E)` if you sort edges for lexicographic order, else `O(E)`; space `O(E)`.

## Curated problems (easy -> hard)

### 1. Network Delay Time  -  Medium
- **Problem:** Given directed edges `times[i] = (u, v, w)` (signal travel time), find the minimum time for a signal sent from node `k` to reach **all** `n` nodes, or `-1` if some node is unreachable.
- **Practice (free):** https://leetcode.com/problems/network-delay-time/
- **Video (free):** https://neetcode.io/problems/network-delay-time
- **Idea:** This is single-source shortest path with non-negative weights, then take the max settled distance (the slowest-to-arrive node is when "all" have received it).
```python
import heapq
from collections import defaultdict
from typing import List

def networkDelayTime(times: List[List[int]], n: int, k: int) -> int:
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {}                              # node -> finalized shortest time
    pq = [(0, k)]                          # (time_so_far, node)
    while pq:
        d, node = heapq.heappop(pq)
        if node in dist:                   # already settled with a smaller time
            continue
        dist[node] = d
        for nei, w in graph[node]:
            if nei not in dist:
                heapq.heappush(pq, (d + w, nei))
    return max(dist.values()) if len(dist) == n else -1
```
- **Complexity:** Time O(E log V), Space O(V + E)
- **Key insight / gotcha:** The answer is the **maximum** of the shortest distances (the last node to get the signal), not the sum. Settle a node only once — the first pop is final.
- **Follow-up:** "What if some weights were negative?" Dijkstra's greedy pop-is-final invariant breaks; switch to Bellman-Ford (`O(V·E)`) and optionally detect negative cycles with one extra relaxation round.

### 2. Min Cost to Connect All Points  -  Medium
- **Problem:** Given `points` on a 2D plane, cost to connect two points is their Manhattan distance; return the minimum total cost to connect **all** points so every pair is reachable.
- **Practice (free):** https://leetcode.com/problems/min-cost-to-connect-all-points/
- **Video (free):** https://neetcode.io/problems/min-cost-to-connect-points
- **Idea:** "Connect all with minimum total weight" = Minimum Spanning Tree on the complete graph of points. Prim's algorithm grows the tree by repeatedly pulling the cheapest edge to an unattached point.
```python
import heapq
from typing import List

def minCostConnectPoints(points: List[List[int]]) -> int:
    n = len(points)
    in_mst = [False] * n
    pq = [(0, 0)]                          # (edge_cost, point_index); start at point 0
    total, count = 0, 0
    while pq and count < n:
        cost, u = heapq.heappop(pq)
        if in_mst[u]:                      # already attached — stale edge
            continue
        in_mst[u] = True
        total += cost
        count += 1
        for v in range(n):                 # complete graph: every other point is a candidate
            if not in_mst[v]:
                w = abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1])
                heapq.heappush(pq, (w, v))
    return total
```
- **Complexity:** Time O(V² log V) (dense complete graph), Space O(V)
- **Key insight / gotcha:** It's a complete graph, so don't precompute all `V²` edges into a list for Kruskal unless V is small — Prim adds candidate edges lazily. Guard with `in_mst` to skip stale heap entries.
- **Follow-up:** "Prim vs Kruskal here?" The graph is dense (`E ≈ V²`), so Prim with an array/heap is natural; Kruskal would sort `~V²` edges (`O(V² log V)`) — comparable, but Prim avoids materializing every edge.

### 3. Cheapest Flights Within K Stops  -  Medium
- **Problem:** Given flights `(u, v, price)`, find the cheapest fare from `src` to `dst` using **at most K stops** (i.e. ≤ K+1 flights), or `-1` if impossible.
- **Practice (free):** https://leetcode.com/problems/cheapest-flights-within-k-stops/
- **Video (free):** https://neetcode.io/problems/cheapest-flights-within-k-stops
- **Idea:** The hop limit breaks plain Dijkstra (the cheapest path might use too many stops). Bellman-Ford fits perfectly: relax all edges exactly `K+1` times — after `i` rounds `dist[v]` is the cheapest path using ≤ `i` edges.
```python
from typing import List

def findCheapestPrice(n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):                 # K stops => at most K+1 edges
        snap = dist[:]                     # relax from PREVIOUS round only
        for u, v, w in flights:
            if dist[u] != INF and dist[u] + w < snap[v]:
                snap[v] = dist[u] + w
        dist = snap
    return dist[dst] if dist[dst] != INF else -1
```
- **Complexity:** Time O(K·E), Space O(V)
- **Key insight / gotcha:** You **must** relax from a snapshot of the prior round's `dist`, not the array you're mutating — otherwise a single round could chain several flights and violate the stop limit. The `K+1` (not `K`) round count trips people up.
- **Follow-up:** "Can Dijkstra solve this?" Only if you augment the state to `(cost, node, stops)` and allow revisiting a node with fewer stops — a strictly more complex variant; Bellman-Ford is the cleaner default for bounded-hop shortest paths.

### 4. Path With Minimum Effort  -  Medium
- **Problem:** On a grid of heights, a path's *effort* is the maximum absolute height difference between consecutive cells; find the minimum possible effort from top-left to bottom-right (moves in 4 directions).
- **Practice (free):** https://leetcode.com/problems/path-with-minimum-effort/
- **Video (free):** https://neetcode.io/problems/path-with-minimum-effort
- **Idea:** Cost is the *max edge on the path*, not a sum. Run Dijkstra but relax with `max(effort_so_far, |height diff|)`; the first time you pop the destination, that's the minimum effort.
```python
import heapq
from typing import List

def minimumEffortPath(heights: List[List[int]]) -> int:
    rows, cols = len(heights), len(heights[0])
    effort = [[float('inf')] * cols for _ in range(rows)]
    effort[0][0] = 0
    pq = [(0, 0, 0)]                       # (effort_so_far, row, col)
    while pq:
        e, r, c = heapq.heappop(pq)
        if r == rows - 1 and c == cols - 1:
            return e                       # first pop of target is the answer
        if e > effort[r][c]:               # stale
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                ne = max(e, abs(heights[nr][nc] - heights[r][c]))  # min-max relaxation
                if ne < effort[nr][nc]:
                    effort[nr][nc] = ne
                    heapq.heappush(pq, (ne, nr, nc))
    return 0
```
- **Complexity:** Time O(R·C·log(R·C)), Space O(R·C)
- **Key insight / gotcha:** The relaxation uses `max(...)` not `+`. The whole Dijkstra correctness argument still holds because we always expand the smallest-known worst-edge frontier first.
- **Follow-up:** "Solve without Dijkstra." Binary search the answer `mid` and BFS/DFS using only edges with `|diff| <= mid` to test reachability — `O(R·C·log(maxHeight))`; or sort cells by height and Union-Find until source and target connect.

### 5. Swim in Rising Water  -  Hard
- **Problem:** Grid `grid[r][c]` is the elevation; water rises so at time `t` you can stand on any cell with elevation ≤ `t`. Starting at `(0,0)`, find the least time to reach `(n-1,n-1)` (4-directional moves, swimming is instant).
- **Practice (free):** https://leetcode.com/problems/swim-in-rising-water/
- **Video (free):** https://neetcode.io/problems/swim-in-rising-water
- **Idea:** The time to traverse a path is the **maximum elevation** on it; you want the path minimizing that max. Identical min-max Dijkstra to Path With Minimum Effort — relax with `max(time_so_far, neighbor_elevation)`.
```python
import heapq
from typing import List

def swimInWater(grid: List[List[int]]) -> int:
    n = len(grid)
    visited = [[False] * n for _ in range(n)]
    pq = [(grid[0][0], 0, 0)]              # (max_elevation_so_far, row, col)
    visited[0][0] = True
    while pq:
        t, r, c = heapq.heappop(pq)
        if r == n - 1 and c == n - 1:
            return t
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc]:
                visited[nr][nc] = True
                heapq.heappush(pq, (max(t, grid[nr][nc]), nr, nc))
    return -1
```
- **Complexity:** Time O(n²·log n), Space O(n²)
- **Key insight / gotcha:** Mark visited **on push** (and rely on the heap ordering) so you never re-expand a cell — since the first time you settle a cell it already has the minimal "worst elevation" needed to reach it.
- **Follow-up:** "Alternative approach?" Union-Find: process cells in increasing elevation order, union each with already-active neighbors, and return the elevation at which `(0,0)` and `(n-1,n-1)` first connect — `O(n²·α(n²))` after sorting.

### 6. Reconstruct Itinerary  -  Hard
- **Problem:** Given airline `tickets[i] = [from, to]`, reconstruct an itinerary using **all** tickets exactly once, starting from `"JFK"`; if multiple valid itineraries exist, return the lexicographically smallest.
- **Practice (free):** https://leetcode.com/problems/reconstruct-itinerary/
- **Video (free):** https://neetcode.io/problems/reconstruct-itinerary
- **Idea:** "Use every edge exactly once" = Eulerian path. Hierholzer's algorithm: sort each node's destinations descending so popping the last gives smallest-first, walk greedily until stuck, then unwind dead-ends onto the route and reverse.
```python
from collections import defaultdict
from typing import List

def findItinerary(tickets: List[List[str]]) -> List[str]:
    graph = defaultdict(list)
    for src, dst in sorted(tickets, reverse=True):   # reverse-sorted so .pop() yields lexicographic order
        graph[src].append(dst)
    route, stack = [], ["JFK"]
    while stack:
        while graph[stack[-1]]:
            stack.append(graph[stack[-1]].pop())     # fly the smallest available destination
        route.append(stack.pop())                    # stuck: this airport ends a sub-trail
    return route[::-1]
```
- **Complexity:** Time O(E log E) (sorting destinations), Space O(E)
- **Key insight / gotcha:** A naive greedy DFS can paint itself into a corner (fly into a dead-end before using other tickets). Hierholzer fixes this: dead-ends are pushed to the route last and end up at the *front* after reversal, so they're visited last. Don't try to "fix" greedy with backtracking — it's `O(E!)`.
- **Follow-up:** "Why does reversing work?" The first node that gets stuck is the true end of the Eulerian trail; appending stuck nodes and reversing places that end node last and JFK first, correctly stitching detours back in.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the lazy-Dijkstra template from memory
- [ ] I can write Bellman-Ford with a hop limit (and remember the snapshot)
- [ ] I can write Prim's MST and Kruskal+DSU from memory
- [ ] Network Delay Time ... 🔴 rusty
- [ ] Min Cost to Connect All Points ... 🔴 rusty
- [ ] Cheapest Flights Within K Stops ... 🔴 rusty
- [ ] Path With Minimum Effort ... 🔴 rusty
- [ ] Swim in Rising Water ... 🔴 rusty
- [ ] Reconstruct Itinerary (Hierholzer) ... 🔴 rusty

## Resources
- **Free:** NeetCode Advanced Graphs roadmap section — https://neetcode.io/roadmap (Dijkstra, Prim, Kruskal, Bellman-Ford, Eulerian) ; LeetCode Graph Theory study plan — https://leetcode.com/studyplan/graph-theory/ ; takeUforward/Striver Graph series (Dijkstra, Bellman-Ford, MST) — https://www.youtube.com/results?search_query=striver+dijkstra+algorithm
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" graph patterns — https://www.designgurus.io (free alternative: the NeetCode Advanced Graphs roadmap above) ; AlgoMonster graph/shortest-path module — https://algo.monster (free alternative: System Design Primer's graph references and the NeetCode videos).

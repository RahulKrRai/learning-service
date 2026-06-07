# 09 - Graphs - BFS / DFS
> One-line: when you need to explore everything reachable from a node, find connected regions, or compute shortest paths in an unweighted graph/grid.

## When to use it (recognition triggers)
- Input is a **2D grid** and you must count regions, flood-fill, or measure area ("islands", "regions", "zones").
- Problem says **"shortest number of steps / minimum moves"** in an unweighted graph or grid -> BFS (level-order) is the reflex.
- You need to know what is **reachable** from a source, or whether two nodes are **connected**.
- Words like **"connected components"**, **"clone/copy a graph"**, **"is this a valid tree"**, **"propagate / spread over time"** (multi-source BFS).
- Adjacency given as a grid, an edge list, or an adjacency map — and there are no edge weights (or all weights equal 1).

## Mental model
- **DFS** dives deep along one path, backtracks, and is natural for "fill this whole region" or "explore everything" — implement recursively (call stack) or with an explicit stack. Use it when you don't care about distance, only reachability/coverage.
- **BFS** expands in concentric rings (level by level) from the source using a queue, so the first time you reach a node you've reached it by the **fewest edges** — that's why BFS gives shortest paths in unweighted graphs.
- **Multi-source BFS** seeds the queue with *all* starting cells at once (rotten oranges, gates); every node is then discovered at its true minimum distance to the nearest source.
- The universal trick is a **visited set/marker** so you never process a node twice; on grids you can often mark in place (flip the cell) to save memory.
- Connectivity questions (valid tree, connected components) are just "run a traversal from each unvisited node and count how many traversals you needed" — or use Union-Find as an alternative.

## Reusable template(s)
```python
from collections import deque

# ---- Grid DFS (recursive flood fill) ----
def grid_dfs(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != '1':
        return
    grid[r][c] = '#'                      # mark visited in place
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grid_dfs(grid, r + dr, c + dc)

# ---- Grid BFS (shortest path / multi-source) ----
def grid_bfs(grid, sources):
    rows, cols = len(grid), len(grid[0])
    q = deque(sources)                    # each source = (r, c, dist) or just (r, c)
    seen = {(r, c) for r, c, *_ in sources}
    while q:
        r, c, *rest = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append((nr, nc))        # process / record distance here

# ---- Generic graph BFS over an adjacency map ----
def graph_bfs(adj, start):
    seen = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nei in adj[node]:
            if nei not in seen:
                seen.add(nei)
                q.append(nei)
    return seen
```

## Complexity profile
- Grid traversal: **Time O(R·C)**, **Space O(R·C)** worst case (recursion/queue). You touch every cell a constant number of times.
- Graph traversal: **Time O(V + E)**, **Space O(V)**. You beat the naive "re-explore from scratch" approaches that revisit nodes (exponential blowups) by using a visited set.

## Curated problems (easy -> hard)

### 1. Number of Islands  -  Medium
- **Problem:** Given a grid of `'1'` (land) and `'0'` (water), count the number of islands, where an island is land connected 4-directionally.
- **Practice (free):** https://leetcode.com/problems/number-of-islands/
- **Video (free):** https://neetcode.io/problems/count-number-of-islands
- **Idea:** Scan every cell; each time you hit unvisited land, increment the count and flood-fill (DFS/BFS) the whole island to mark it visited.
```python
def numIslands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'                  # sink the land so we don't revisit
        dfs(r + 1, c); dfs(r - 1, c)
        dfs(r, c + 1); dfs(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```
- **Complexity:** Time O(R·C), Space O(R·C) worst-case recursion depth.
- **Key insight / gotcha:** Marking the cell *before* recursing prevents infinite loops; don't forget to count the island once and then erase all of it.
- **Follow-up:** "What if the grid is too large for the recursion stack?" Switch to an iterative BFS/DFS with an explicit deque/stack to avoid stack overflow.

### 2. Max Area of Island  -  Medium
- **Problem:** Given a binary grid, return the area (number of `1` cells) of the largest 4-directionally connected island, or 0 if none.
- **Practice (free):** https://leetcode.com/problems/max-area-of-island/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+max+area+of+island
- **Idea:** Same flood fill as Number of Islands, but DFS returns the size of the region it filled; track the maximum.
```python
def maxAreaOfIsland(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c) -> int:
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != 1:
            return 0
        grid[r][c] = 0                    # mark visited
        return 1 + dfs(r + 1, c) + dfs(r - 1, c) + dfs(r, c + 1) + dfs(r, c - 1)

    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                best = max(best, dfs(r, c))
    return best
```
- **Complexity:** Time O(R·C), Space O(R·C).
- **Key insight / gotcha:** The DFS must *return* the accumulated area (1 + children); a common bug is using a global counter that you forget to reset per island.
- **Follow-up:** "Count islands of a specific shape / distinct shapes?" Normalize each island's cell coordinates relative to its top-left and hash the shape set.

### 3. Number of Connected Components in an Undirected Graph  -  Medium
- **Problem:** Given `n` nodes labeled `0..n-1` and an edge list, return how many connected components the graph has.
- **Practice (free):** https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/ (LeetCode Premium) — free alternative: https://neetcode.io/problems/count-connected-components
- **Video (free):** https://neetcode.io/problems/count-connected-components
- **Idea:** Build an adjacency list, then run DFS/BFS from each unvisited node; each fresh traversal you start is exactly one component.
```python
def countComponents(n: int, edges: list[list[int]]) -> int:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    seen = [False] * n

    def dfs(node):
        seen[node] = True
        for nei in adj[node]:
            if not seen[nei]:
                dfs(nei)

    components = 0
    for node in range(n):
        if not seen[node]:
            components += 1
            dfs(node)
    return components
```
- **Complexity:** Time O(V + E), Space O(V + E).
- **Key insight / gotcha:** Isolated nodes (no edges) each count as their own component — looping over all `n` nodes handles this automatically.
- **Follow-up:** "Edges arrive as a stream / you also get union queries?" Use Union-Find (disjoint set) with path compression for near-O(1) amortized merges and component counting.

### 4. Graph Valid Tree  -  Medium
- **Problem:** Given `n` nodes and an undirected edge list, decide whether they form a valid tree (fully connected and acyclic).
- **Practice (free):** https://leetcode.com/problems/graph-valid-tree/ (LeetCode Premium) — free alternative: https://neetcode.io/problems/valid-tree
- **Video (free):** https://neetcode.io/problems/valid-tree
- **Idea:** A tree on `n` nodes has exactly `n-1` edges and is connected. Check the edge count first, then confirm a single traversal reaches all `n` nodes.
```python
def validTree(n: int, edges: list[list[int]]) -> bool:
    if len(edges) != n - 1:               # necessary: tree has exactly n-1 edges
        return False
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    seen = set()
    stack = [0]
    seen.add(0)
    while stack:
        node = stack.pop()
        for nei in adj[node]:
            if nei not in seen:
                seen.add(nei)
                stack.append(nei)

    return len(seen) == n                 # connected <=> reached every node
```
- **Complexity:** Time O(V + E), Space O(V + E).
- **Key insight / gotcha:** Once you know edges == n-1, you only need to verify *connectivity* — that combination forbids cycles automatically, so you don't need explicit cycle detection.
- **Follow-up:** "Do it without the edge-count shortcut." Run DFS tracking each node's parent; if you reach an already-visited node that isn't the parent, there's a cycle -> not a tree.

### 5. Rotting Oranges  -  Medium
- **Problem:** In a grid of empty (`0`), fresh (`1`), and rotten (`2`) oranges, each minute every fresh orange adjacent to a rotten one rots; return the minutes until none are fresh, or -1 if impossible.
- **Practice (free):** https://leetcode.com/problems/rotting-oranges/
- **Video (free):** https://neetcode.io/problems/rotting-fruit
- **Idea:** Multi-source BFS: seed the queue with all initially rotten oranges, then expand level by level; the number of levels is the elapsed minutes.
```python
from collections import deque

def orangesRotting(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    while q and fresh > 0:
        minutes += 1
        for _ in range(len(q)):           # process one full minute (level)
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))

    return minutes if fresh == 0 else -1
```
- **Complexity:** Time O(R·C), Space O(R·C).
- **Key insight / gotcha:** The `for _ in range(len(q))` snapshot is what separates minutes into discrete levels; counting `fresh` lets you return -1 when some orange is unreachable.
- **Follow-up:** "Return which oranges never rot." Those are the fresh cells still equal to `1` after the BFS completes.

### 6. Walls and Gates  -  Medium
- **Problem:** Fill each empty room (`INF`) in a grid with its distance to the nearest gate (`0`); walls are `-1`. Rooms unreachable from any gate stay `INF`.
- **Practice (free):** https://leetcode.com/problems/walls-and-gates/ (LeetCode Premium) — free alternative: https://neetcode.io/problems/islands-and-treasure
- **Video (free):** https://neetcode.io/problems/islands-and-treasure
- **Idea:** Multi-source BFS from all gates simultaneously; the first time BFS touches a room, it's at the minimum distance to the nearest gate.
```python
from collections import deque

def wallsAndGates(rooms: list[list[int]]) -> None:
    INF = 2 ** 31 - 1
    rows, cols = len(rooms), len(rooms[0])
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if rooms[r][c] == 0:          # seed every gate
                q.append((r, c))

    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and rooms[nr][nc] == INF:
                rooms[nr][nc] = rooms[r][c] + 1
                q.append((nr, nc))
```
- **Complexity:** Time O(R·C), Space O(R·C).
- **Key insight / gotcha:** Seeding *all* gates at once is the whole trick — a separate BFS per gate would be O((R·C)²). The `== INF` check doubles as the visited marker since any filled room is no longer INF.
- **Follow-up:** "Single gate, but huge grid, find distance to one target room." Plain single-source BFS with early exit when you pop the target.

### 7. Surrounded Regions  -  Medium
- **Problem:** In a board of `'X'` and `'O'`, capture (flip to `'X'`) every region of `'O'`s that is fully surrounded — i.e., not connected to the border.
- **Practice (free):** https://leetcode.com/problems/surrounded-regions/
- **Video (free):** https://neetcode.io/problems/surrounded-regions
- **Idea:** Invert the logic: `'O'`s connected to the border are *safe*. DFS from every border `'O'` to mark safe cells, then flip everything still `'O'` (truly surrounded) and restore the safe ones.
```python
def solve(board: list[list[str]]) -> None:
    if not board:
        return
    rows, cols = len(board), len(board[0])

    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or board[r][c] != 'O':
            return
        board[r][c] = 'S'                 # mark border-connected as Safe
        dfs(r + 1, c); dfs(r - 1, c)
        dfs(r, c + 1); dfs(r, c - 1)

    for r in range(rows):                 # only border cells launch DFS
        for c in range(cols):
            if (r in (0, rows - 1) or c in (0, cols - 1)) and board[r][c] == 'O':
                dfs(r, c)

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                board[r][c] = 'X'         # surrounded -> capture
            elif board[r][c] == 'S':
                board[r][c] = 'O'         # restore safe
```
- **Complexity:** Time O(R·C), Space O(R·C).
- **Key insight / gotcha:** Don't try to detect "surrounded" directly — flood-filling inward from the border and capturing the leftovers is far simpler and avoids ambiguous edge cases.
- **Follow-up:** "Memory-tight, can't recurse." Use an explicit stack/queue from the border cells; the algorithm is identical.

### 8. Pacific Atlantic Water Flow  -  Medium
- **Problem:** Given a height grid, find all cells from which water can flow to *both* the Pacific (top/left edges) and Atlantic (bottom/right edges), flowing only to equal-or-lower neighbors.
- **Practice (free):** https://leetcode.com/problems/pacific-atlantic-water-flow/
- **Video (free):** https://neetcode.io/problems/pacific-atlantic-water-flow
- **Idea:** Reverse the flow: from each ocean's border cells, DFS *uphill* (to neighbors with height >= current) to find all cells that can reach that ocean. The answer is the intersection of the two reachable sets.
```python
def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    if not heights:
        return []
    rows, cols = len(heights), len(heights[0])
    pac, atl = set(), set()

    def dfs(r, c, visited, prev_height):
        if (r < 0 or c < 0 or r >= rows or c >= cols
                or (r, c) in visited or heights[r][c] < prev_height):
            return
        visited.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc, visited, heights[r][c])

    for c in range(cols):
        dfs(0, c, pac, heights[0][c])           # top edge -> Pacific
        dfs(rows - 1, c, atl, heights[rows - 1][c])  # bottom edge -> Atlantic
    for r in range(rows):
        dfs(r, 0, pac, heights[r][0])           # left edge -> Pacific
        dfs(r, cols - 1, atl, heights[r][cols - 1])  # right edge -> Atlantic

    return [[r, c] for r in range(rows) for c in range(cols)
            if (r, c) in pac and (r, c) in atl]
```
- **Complexity:** Time O(R·C), Space O(R·C).
- **Key insight / gotcha:** Flowing *forward* (downhill from every cell) is O((R·C)²); reversing to flow *uphill from the oceans* makes it O(R·C). The condition is `>=` so equal-height plateaus still propagate.
- **Follow-up:** "Diagonal flow allowed too." Add the four diagonal offsets to the direction list — the rest is unchanged.

### 9. Clone Graph  -  Medium
- **Problem:** Given a reference to a node in a connected undirected graph, return a deep copy (clone all nodes and their neighbor lists).
- **Practice (free):** https://leetcode.com/problems/clone-graph/
- **Video (free):** https://neetcode.io/problems/clone-graph
- **Idea:** Traverse (DFS/BFS) while maintaining a map from original node -> its clone; create each clone once on first visit, then wire up cloned neighbors.
```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node: 'Node') -> 'Node':
    if not node:
        return None
    old_to_new = {}

    def dfs(cur):
        if cur in old_to_new:
            return old_to_new[cur]
        copy = Node(cur.val)
        old_to_new[cur] = copy            # record BEFORE recursing (handles cycles)
        for nei in cur.neighbors:
            copy.neighbors.append(dfs(nei))
        return copy

    return dfs(node)
```
- **Complexity:** Time O(V + E), Space O(V).
- **Key insight / gotcha:** Insert the clone into the map *before* recursing into neighbors; otherwise cycles cause infinite recursion and you'd create duplicate nodes.
- **Follow-up:** "Convert to iterative." BFS with a queue, clone a node when first seen, and append cloned neighbors — same hash map, no recursion limit risk.

### 10. Word Ladder  -  Hard
- **Problem:** Given `beginWord`, `endWord`, and a word list, return the length of the shortest transformation sequence changing one letter at a time, where every intermediate word is in the list (0 if impossible).
- **Practice (free):** https://leetcode.com/problems/word-ladder/
- **Video (free):** https://neetcode.io/problems/word-ladder
- **Idea:** Model words as graph nodes with edges between words differing by one letter; BFS from `beginWord` gives the shortest path length. Use wildcard patterns (e.g. `h*t`) to find neighbors in O(L) instead of comparing all word pairs.
```python
from collections import deque, defaultdict

def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    words = set(wordList)
    if endWord not in words:
        return 0

    # bucket words by each "wildcard" pattern: hot -> *ot, h*t, ho*
    patterns = defaultdict(list)
    for word in words | {beginWord}:
        for i in range(len(word)):
            patterns[word[:i] + '*' + word[i + 1:]].append(word)

    q = deque([(beginWord, 1)])           # (word, sequence length so far)
    seen = {beginWord}
    while q:
        word, steps = q.popleft()
        if word == endWord:
            return steps
        for i in range(len(word)):
            key = word[:i] + '*' + word[i + 1:]
            for nei in patterns[key]:
                if nei not in seen:
                    seen.add(nei)
                    q.append((nei, steps + 1))
    return 0
```
- **Complexity:** Time O(N·L²) where N = words, L = word length (L patterns per word, each O(L) to build), Space O(N·L²).
- **Key insight / gotcha:** Building neighbors by comparing every pair of words is O(N²·L) and times out; the wildcard-bucket adjacency is the standard fix. BFS (not DFS) is mandatory because we want the *shortest* sequence.
- **Follow-up:** "Make it faster for large dictionaries." Use bidirectional BFS — search from both ends and stop when the frontiers meet, cutting the explored branching factor dramatically.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the grid-DFS and grid-BFS templates from memory
- [ ] I know when to reach for multi-source BFS vs single-source vs DFS
- [ ] Number of Islands ... 🔴/🟡/🟢
- [ ] Max Area of Island ... 🔴/🟡/🟢
- [ ] Number of Connected Components ... 🔴/🟡/🟢
- [ ] Graph Valid Tree ... 🔴/🟡/🟢
- [ ] Rotting Oranges ... 🔴/🟡/🟢
- [ ] Walls and Gates ... 🔴/🟡/🟢
- [ ] Surrounded Regions ... 🔴/🟡/🟢
- [ ] Pacific Atlantic Water Flow ... 🔴/🟡/🟢
- [ ] Clone Graph ... 🔴/🟡/🟢
- [ ] Word Ladder ... 🔴/🟡/🟢

## Resources
- **Free:** NeetCode Graphs roadmap section — https://neetcode.io/roadmap ; LeetCode Graph Explore card — https://leetcode.com/explore/learn/card/graph/ ; takeUforward/Striver graph series (search) — https://www.youtube.com/results?search_query=striver+graph+series+bfs+dfs
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" graph patterns — https://www.designgurus.io (free alternative: the NeetCode roadmap + problem videos above cover the same patterns).

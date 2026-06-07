# 10 - Topological Sort
> Reach for this when you must order things under "X must come before Y" constraints over a directed graph (DAG).

## When to use it (recognition triggers)
- The problem gives you **dependencies / prerequisites / ordering rules** ("a before b", "to do X you first need Y").
- You're asked for a **valid ordering**, whether a valid ordering **exists** (cycle detection), or **how many** orderings exist.
- Input is a **directed graph** (often disguised as pairs, words, course lists) and the answer must respect edge direction.
- You see phrases like "build order", "compile order", "task scheduling", "course schedule", "alien/unknown alphabet order".
- You need to **peel off** nodes layer by layer (e.g. leaves of a tree, zero-dependency tasks first).

## Mental model
- A topological order lists every node so that for every directed edge `u -> v`, `u` appears before `v`. It exists **iff the graph is a DAG** (no cycle).
- **Kahn's algorithm (BFS)** is the workhorse: compute every node's in-degree, push all in-degree-0 nodes into a queue, repeatedly pop one (it has no remaining unmet dependency), append to the order, and decrement its neighbors' in-degrees, enqueuing any that hit 0.
- If you process **fewer nodes than exist**, the leftovers are stuck in a cycle -> no valid order. This is how Kahn doubles as cycle detection.
- **DFS** gives the same result by pushing a node onto a stack **after** fully exploring its descendants, then reversing. DFS also detects cycles via a 3-color (white/gray/black) state.
- Use a **min-heap instead of a plain queue** when you need the lexicographically smallest order. Use Kahn and check the queue has **exactly one** candidate at each step when you need to verify the order is **unique** (Sequence Reconstruction).

## Reusable template(s)
```python
from collections import deque

def topo_sort_kahn(n, edges):
    """n nodes labeled 0..n-1. edges: list of (u, v) meaning u must come before v.
    Returns a valid topological order, or [] if a cycle exists."""
    graph = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        graph[u].append(v)
        indeg[v] += 1

    # Start from every node that has no incoming edge (no dependency).
    queue = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for w in graph[u]:
            indeg[w] -= 1          # one dependency of w is now satisfied
            if indeg[w] == 0:
                queue.append(w)

    return order if len(order) == n else []   # short order => cycle


def topo_sort_dfs(n, edges):
    """DFS variant with 3-color cycle detection. Returns order or [] on cycle."""
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    order = []
    has_cycle = False

    def dfs(u):
        nonlocal has_cycle
        color[u] = GRAY                # currently on the recursion stack
        for w in graph[u]:
            if color[w] == GRAY:       # back-edge -> cycle
                has_cycle = True
                return
            if color[w] == WHITE:
                dfs(w)
        color[u] = BLACK
        order.append(u)                # finished: append post-order

    for i in range(n):
        if color[i] == WHITE:
            dfs(i)
        if has_cycle:
            return []
    return order[::-1]                 # reverse post-order = topo order
```

## Complexity profile
- **Time O(V + E)**, **Space O(V + E)** for both Kahn and DFS (graph adjacency + queue/recursion).
- You're beating the brute force of trying all `V!` permutations and checking each against the constraints (`O(V! * E)`).
- Lexicographic-smallest variant costs `O(E + V log V)` because of the heap.

## Curated problems (easy -> hard)

### 1. Course Schedule  -  Medium
- **Problem:** Given `numCourses` and prerequisite pairs `[a, b]` (take `b` before `a`), return whether you can finish all courses.
- **Practice (free):** https://leetcode.com/problems/course-schedule/
- **Video (free):** https://neetcode.io/problems/course-schedule
- **Idea:** This is pure cycle detection on a DAG. Run Kahn; if you can process all `numCourses` nodes, there's no cycle and you can finish.
```python
from collections import deque
from typing import List

def canFinish(numCourses: int, prerequisites: List[List[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:      # must take b before a  =>  edge b -> a
        graph[b].append(a)
        indeg[a] += 1

    queue = deque(i for i in range(numCourses) if indeg[i] == 0)
    taken = 0
    while queue:
        u = queue.popleft()
        taken += 1
        for w in graph[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    return taken == numCourses       # all taken => acyclic
```
- **Complexity:** Time O(V + E), Space O(V + E)
- **Key insight / gotcha:** Get the edge direction right: `[a, b]` means `b -> a`. Flipping it silently passes some tests and fails others.
- **Follow-up:** "Return the actual order, not just a bool." -> That's the next problem; collect the popped nodes into a list.

### 2. Course Schedule II  -  Medium
- **Problem:** Same setup, but return **a valid order** to finish all courses, or an empty array if impossible.
- **Practice (free):** https://leetcode.com/problems/course-schedule-ii/
- **Video (free):** https://neetcode.io/problems/course-schedule-ii
- **Idea:** Identical Kahn traversal; record each popped node. If the recorded order has length `numCourses`, return it, else return `[]`.
```python
from collections import deque
from typing import List

def findOrder(numCourses: int, prerequisites: List[List[int]]) -> List[int]:
    graph = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:      # edge b -> a
        graph[b].append(a)
        indeg[a] += 1

    queue = deque(i for i in range(numCourses) if indeg[i] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for w in graph[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    return order if len(order) == numCourses else []
```
- **Complexity:** Time O(V + E), Space O(V + E)
- **Key insight / gotcha:** Any valid topo order is accepted; don't over-engineer for a "canonical" one unless asked. The cycle check (`len(order) == numCourses`) is mandatory before returning.
- **Follow-up:** "Return the lexicographically smallest valid order." -> Swap the `deque` for a `heapq` min-heap so you always expand the smallest available course.

### 3. Minimum Height Trees  -  Medium
- **Problem:** Given an undirected tree of `n` nodes, return all root labels that minimize the resulting tree's height.
- **Practice (free):** https://leetcode.com/problems/minimum-height-trees/
- **Video (free):** https://neetcode.io/problems/minimum-height-trees
- **Idea:** The answer is the 1 or 2 **centroids** of the tree. Use a Kahn-style "peel the leaves" BFS: repeatedly remove all current leaves (degree 1) layer by layer; the last 1-2 nodes remaining are the centroids.
```python
from collections import deque
from typing import List

def findMinHeightTrees(n: int, edges: List[List[int]]) -> List[int]:
    if n == 1:
        return [0]
    graph = [set() for _ in range(n)]
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    leaves = deque(i for i in range(n) if len(graph[i]) == 1)
    remaining = n
    while remaining > 2:
        size = len(leaves)
        remaining -= size
        for _ in range(size):               # strip one full layer of leaves
            leaf = leaves.popleft()
            nxt = graph[leaf].pop()          # leaf has exactly one neighbor
            graph[nxt].discard(leaf)
            if len(graph[nxt]) == 1:         # neighbor just became a leaf
                leaves.append(nxt)
    return list(leaves)                      # 1 or 2 centroids
```
- **Complexity:** Time O(V + E), Space O(V + E)
- **Key insight / gotcha:** It's topological-sort flavored (in-degree -> degree, peel zero/one-degree nodes), but on an **undirected** tree, and you must stop at `remaining <= 2`, not drain to empty. Handle `n == 1` (and `n == 2`) explicitly.
- **Follow-up:** "Why never more than 2 answers?" -> A tree's center is at most an edge's two endpoints; a longest path (diameter) has its middle at 1 node (odd length) or 2 nodes (even length).

### 4. Alien Dictionary  -  Hard
- **Problem:** Given words sorted lexicographically by an unknown alphabet, return any valid ordering of that alphabet's letters, or `""` if none is consistent.
- **Practice (free):** https://leetcode.com/problems/alien-dictionary/ (LeetCode Premium) — free alternative: https://neetcode.io/problems/foreign-dictionary
- **Video (free):** https://neetcode.io/problems/foreign-dictionary
- **Idea:** Compare each adjacent word pair; the first differing character gives one ordering edge `c1 -> c2`. Topologically sort the graph of letters. Watch the invalid-prefix case.
```python
from collections import deque
from typing import List

def alienOrder(words: List[str]) -> str:
    graph = {c: set() for w in words for c in w}     # every seen letter is a node
    indeg = {c: 0 for c in graph}

    for a, b in zip(words, words[1:]):
        # If b is a prefix of a but shorter, ordering is impossible.
        if len(a) > len(b) and a.startswith(b):
            return ""
        for x, y in zip(a, b):
            if x != y:
                if y not in graph[x]:
                    graph[x].add(y)
                    indeg[y] += 1
                break                                # only the FIRST diff matters

    queue = deque(c for c in indeg if indeg[c] == 0)
    order = []
    while queue:
        c = queue.popleft()
        order.append(c)
        for nxt in graph[c]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    return "".join(order) if len(order) == len(indeg) else ""   # cycle => ""
```
- **Complexity:** Time O(C) where C is total characters across all words, Space O(1) (alphabet bounded by 26)
- **Key insight / gotcha:** Two traps: (1) only the **first** differing char yields an edge — break after it; (2) the invalid case where a longer word precedes its own prefix (`["abc", "ab"]`) must return `""`. Add a guard against duplicate edges so in-degree isn't double-counted.
- **Follow-up:** "What if multiple valid orders exist?" -> Any is accepted; if asked for uniqueness, require the queue to hold exactly one node at every step.

### 5. Sequence Reconstruction  -  Medium
- **Problem:** Given a permutation `nums` of `1..n` and a list of subsequences `seqs`, determine if `nums` is the **only** sequence that can be reconstructed from `seqs` (i.e. the unique topological order).
- **Practice (free):** https://leetcode.com/problems/sequence-reconstruction/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/605/
- **Video (free):** https://www.youtube.com/results?search_query=sequence+reconstruction+topological+sort
- **Idea:** Build the dependency graph from consecutive pairs in each `seq`. The order is unique iff at every Kahn step there is **exactly one** node with in-degree 0, and the resulting order equals `nums`.
```python
from collections import deque, defaultdict
from typing import List

def sequenceReconstruction(nums: List[int], seqs: List[List[int]]) -> bool:
    graph = defaultdict(set)
    indeg = {}
    for seq in seqs:
        for x in seq:
            indeg.setdefault(x, 0)            # register every value as a node
        for a, b in zip(seq, seq[1:]):
            if b not in graph[a]:
                graph[a].add(b)
                indeg[b] += 1

    # Every value in nums must appear; no extra/out-of-range value allowed.
    if set(indeg) != set(nums):
        return False

    queue = deque(x for x in indeg if indeg[x] == 0)
    order = []
    while queue:
        if len(queue) > 1:                    # ambiguous => not a unique order
            return False
        u = queue.popleft()
        order.append(u)
        for w in graph[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)

    return order == nums                      # unique AND matches nums
```
- **Complexity:** Time O(V + E), Space O(V + E)
- **Key insight / gotcha:** The whole problem hinges on the **`len(queue) > 1`** check — that's what distinguishes "a valid order exists" from "exactly one order exists." Also validate the node set matches `nums` (catches missing values and out-of-range entries like `[2]` for `n=1`).
- **Follow-up:** "Just return whether *any* valid reconstruction exists." -> Drop the uniqueness check and the `order == nums` equality; only verify it's a DAG covering all values.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the Kahn template from memory
- [ ] I can write the DFS + 3-color cycle-detection template from memory
- [ ] Course Schedule  🔴 / 🟡 / 🟢
- [ ] Course Schedule II  🔴 / 🟡 / 🟢
- [ ] Minimum Height Trees  🔴 / 🟡 / 🟢
- [ ] Alien Dictionary  🔴 / 🟡 / 🟢
- [ ] Sequence Reconstruction  🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (Graphs section): https://neetcode.io/roadmap | System Design Primer's DAG/scheduling notes & general graph refresher: https://github.com/donnemartin/system-design-primer | LeetCode Graph study plan: https://leetcode.com/studyplan/graph-theory/
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Topological Sort module): https://www.designgurus.io — free alternative is the NeetCode Graphs roadmap above; AlgoMonster topological-sort track: https://algo.monster — free alternative is the NeetCode problem pages linked per-problem.

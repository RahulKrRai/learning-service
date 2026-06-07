# 11 - Union-Find (Disjoint Set)
> One-line: when you need to repeatedly merge groups and ask "are these two things in the same group?" — fast.

## When to use it (recognition triggers)
- You're tracking **connected components** in a graph and edges arrive incrementally (online / streaming).
- The question is membership: "are a and b connected?", "how many components?", "does adding this edge create a cycle?"
- You need to **merge** disjoint sets and the only queries are union + find (no path/shortest-distance needs).
- "Group / cluster / merge accounts / friend circles / provinces / islands" plus a near-equivalence relation.
- A grid where you add land/edges one at a time and must report component count *after each step* (a BFS/DFS rerun would be too slow).

## Mental model
- Each element starts as its own one-node tree pointing at itself (its "parent"). A set is identified by its **root** (the representative).
- `find(x)` walks parent pointers up to the root; `union(a, b)` links one root under the other, merging two trees.
- Two optimizations make it near-O(1) amortized: **path compression** (on `find`, re-point nodes directly at the root) and **union by rank/size** (always attach the smaller tree under the larger so trees stay shallow).
- Together these give the inverse-Ackermann bound α(n), which is ≤ 4 for any input you'll ever see — effectively constant.
- It's a one-way structure: great for "add edges and ask connectivity," but it can't efficiently *delete* edges or answer path queries. If you need deletions, process them offline in reverse (union instead of cut).

## Reusable template(s)
```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))   # each node is its own root initially
        self.rank = [0] * n            # tree height upper bound (for union by rank)
        self.size = [1] * n            # component size (handy for many problems)
        self.count = n                 # number of disjoint components

    def find(self, x):
        # iterative path compression: every node on the path points to the root
        root = x
        while root != self.parent[root]:
            root = self.parent[root]
        while x != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False               # already connected -> would form a cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra            # ensure ra is the taller/heavier root
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True                    # a real merge happened

    def connected(self, a, b):
        return self.find(a) == self.find(b)
```

For string / arbitrary keys, wrap a dict-based version:
```python
class DSUDict:
    def __init__(self):
        self.parent = {}
    def find(self, x):
        self.parent.setdefault(x, x)
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x
    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)
```

## Complexity profile
- `find` / `union`: **O(α(n))** amortized ≈ O(1) with both optimizations; O(log n) with only one; O(n) with neither.
- m operations on n elements: **O(m · α(n))** ≈ O(m). Space **O(n)**.
- You're beating a per-query BFS/DFS (O(V+E) each) or rebuilding components from scratch after every edge.

## Curated problems (easy -> hard)

### 1. Number of Connected Components in an Undirected Graph  -  Medium
- **Problem:** Given `n` nodes labeled `0..n-1` and a list of undirected edges, return how many connected components the graph has.
- **Practice (free):** https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/3651/
- **Video (free):** https://neetcode.io/problems/count-connected-components
- **Idea:** Start with `n` components; each edge that successfully unions two *different* roots reduces the count by one.
```python
from typing import List

def countComponents(n: int, edges: List[List[int]]) -> int:
    parent = list(range(n))
    rank = [0] * n
    count = n

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]   # path halving
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            continue                        # edge inside an existing component
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        count -= 1                          # one fewer component
    return count
```
- **Complexity:** Time O(n + E·α(n)), Space O(n)
- **Key insight / gotcha:** Don't double-count: only decrement `count` when the two endpoints had *different* roots. An edge within a component is a no-op.
- **Follow-up:** "Now also support adding edges live and querying the count." That's already what DSU gives you — just expose `union` and read `count` after each call (vs. DFS which would rescan every time).

### 2. Graph Valid Tree  -  Medium
- **Problem:** Given `n` nodes and a list of undirected edges, determine whether they form a valid tree (fully connected and acyclic).
- **Practice (free):** https://leetcode.com/problems/graph-valid-tree/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/178/
- **Video (free):** https://neetcode.io/problems/valid-tree
- **Idea:** A tree on `n` nodes has exactly `n-1` edges and no cycle. Check edge count first, then use DSU: if any `union` finds both endpoints already connected, there's a cycle.
```python
from typing import List

def validTree(n: int, edges: List[List[int]]) -> bool:
    if len(edges) != n - 1:                 # tree must have exactly n-1 edges
        return False
    parent = list(range(n))

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:                        # endpoints already linked -> cycle
            return False
        parent[ra] = rb
    return True                             # n-1 edges + no cycle => connected & acyclic
```
- **Complexity:** Time O(n + E·α(n)), Space O(n)
- **Key insight / gotcha:** The `len(edges) == n-1` check is what lets you skip a separate connectivity pass: with exactly `n-1` edges and no cycle, the graph *must* be a single component. Skip that check and you'd also need to verify `count == 1`.
- **Follow-up:** "What if edges can be duplicated?" A duplicate edge is itself a cycle (both endpoints share a root on the second pass), so DSU still catches it correctly.

### 3. Redundant Connection  -  Medium
- **Problem:** A tree had one extra edge added, creating exactly one cycle. Given the edges (1-indexed), return the edge that can be removed — the last one in input order that closes a cycle.
- **Practice (free):** https://leetcode.com/problems/redundant-connection/
- **Video (free):** https://neetcode.io/problems/redundant-connection
- **Idea:** Union edges in input order; the first edge whose two endpoints are *already* connected is the redundant one. Because exactly one cycle exists, the first failure to union is the answer.
```python
from typing import List

def findRedundantConnection(edges: List[List[int]]) -> List[int]:
    n = len(edges)
    parent = list(range(n + 1))             # nodes are 1..n, index 0 unused
    rank = [0] * (n + 1)

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                    # cycle: a and b already connected
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    for a, b in edges:
        if not union(a, b):                 # first edge that closes a cycle
            return [a, b]
    return []                               # unreachable per problem guarantee
```
- **Complexity:** Time O(n·α(n)), Space O(n)
- **Key insight / gotcha:** Return the *first* edge that fails to union — that is the last edge in input order completing the cycle, which the problem asks for. Watch the 1-indexing: size the arrays `n+1`.
- **Follow-up:** "Redundant Connection II" (directed graph) is the real hard variant: a node may have two parents OR there's a cycle. Detect the two-parent case first, then run DSU once skipping the suspect edge — the logic branches on which configuration holds.

### 4. Accounts Merge  -  Medium
- **Problem:** Given accounts as `[name, email1, email2, ...]`, merge any accounts that share at least one email (transitively). Return merged accounts with name + sorted unique emails.
- **Practice (free):** https://leetcode.com/problems/accounts-merge/
- **Video (free):** https://neetcode.io/problems/accounts-merge
- **Idea:** Treat each account index as a DSU node. For each email, remember which account first owned it; if a later account reuses that email, union the two account indices. Then group emails by root.
```python
from typing import List
from collections import defaultdict

def accountsMerge(accounts: List[List[str]]) -> List[List[str]]:
    n = len(accounts)
    parent = list(range(n))

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    email_owner = {}                        # email -> first account index seen
    for i, acct in enumerate(accounts):
        for email in acct[1:]:
            if email in email_owner:
                union(i, email_owner[email])  # same email -> merge accounts
            else:
                email_owner[email] = i

    # gather emails under each component root
    groups = defaultdict(set)
    for email, owner in email_owner.items():
        groups[find(owner)].add(email)

    result = []
    for root, emails in groups.items():
        name = accounts[root][0]
        result.append([name] + sorted(emails))
    return result
```
- **Complexity:** Time O(N·K·logK·α) where N=accounts, K=emails/account (sort dominates), Space O(N·K)
- **Key insight / gotcha:** Union the **account indices**, not the email strings — that keeps the DSU small and avoids re-deriving names. Final emails must be **sorted**, and the name comes from any account in the component (they all share it).
- **Follow-up:** "Two accounts with the same name but no shared email — should they merge?" No. Name is not an identity key here; only shared emails connect accounts. Merging by name would be a bug.

### 5. Number of Islands II  -  Hard
- **Problem:** On an initially all-water `m x n` grid, you add land one cell at a time via a list of `positions`. After each addition, report the current number of islands.
- **Practice (free):** https://leetcode.com/problems/number-of-islands-ii/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/677/
- **Video (free):** https://www.youtube.com/results?search_query=number+of+islands+II+union+find
- **Idea:** Flatten each cell to id `r*n + c`. Adding land increments island count by 1, then union with any already-land 4-neighbor; each successful union decrements the count. Append the count after every position.
```python
from typing import List

def numIslands2(m: int, n: int, positions: List[List[int]]) -> List[int]:
    parent = {}
    count = 0
    res = []

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r, c in positions:
        idx = r * n + c
        if idx in parent:                   # duplicate add -> island count unchanged
            res.append(count)
            continue
        parent[idx] = idx                   # new land = its own island for now
        count += 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            nidx = nr * n + nc
            if 0 <= nr < m and 0 <= nc < n and nidx in parent:
                if find(idx) != find(nidx): # merge two distinct islands
                    parent[find(idx)] = find(nidx)
                    count -= 1
        res.append(count)
    return res
```
- **Complexity:** Time O(L·α(L)) where L=len(positions), Space O(L)
- **Key insight / gotcha:** Two traps: (1) handle **duplicate positions** — re-adding existing land must not bump the count; (2) only `parent`-register and union with neighbors that are *already land*. Add 1 first, then subtract for each genuine merge.
- **Follow-up:** "Why not BFS/DFS after each add?" Each rescan is O(m·n), giving O(L·m·n) — far worse. DSU is the canonical reason this problem is "Hard": it's the only structure that keeps the running count cheap under incremental updates.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the DSU template (find + union by rank + path compression) from memory
- [ ] Number of Connected Components  🔴🟡🟢
- [ ] Graph Valid Tree  🔴🟡🟢
- [ ] Redundant Connection  🔴🟡🟢
- [ ] Accounts Merge  🔴🟡🟢
- [ ] Number of Islands II  🔴🟡🟢

## Resources
- **Free:** NeetCode Graphs roadmap section — https://neetcode.io/roadmap ; CP-Algorithms DSU writeup (proofs + optimizations) — https://cp-algorithms.com/data_structures/disjoint_set_union.html ; takeUforward/striver DSU explainer — https://www.youtube.com/results?search_query=striver+disjoint+set+union+by+rank+path+compression
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" union-find module — https://www.designgurus.io (free alternative: the CP-Algorithms link above covers the same material with proofs).

# Day 3 — Binary Trees, BFS/DFS, Graphs
**Target: 3–4 hours | Date: April 2**

---

## Tree Definitions

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## Part 1: Tree Traversals (30 min)

```python
# Inorder: Left → Root → Right (gives sorted order for BST)
def inorder(root):
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# Preorder: Root → Left → Right (good for serialization)
def preorder(root):
    if not root: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

# Postorder: Left → Right → Root (good for deletion, bottom-up)
def postorder(root):
    if not root: return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# Level Order (BFS)
from collections import deque
def level_order(root):
    if not root: return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):  # process entire level
            node = queue.popleft()
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

---

## Part 2: Classic Tree Problems (1.5 hours)

### Problem 1: Maximum Depth of Binary Tree
```python
def max_depth(root):
    if not root: return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
# Time: O(n), Space: O(h) call stack where h = height
```

### Problem 2: Validate Binary Search Tree
```python
def is_valid_bst(root):
    def validate(node, min_val, max_val):
        if not node: return True
        if node.val <= min_val or node.val >= max_val:
            return False
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))
    return validate(root, float('-inf'), float('inf'))
# Time: O(n), Space: O(h)
# Key insight: pass down valid range, not just check children
```

### Problem 3: Lowest Common Ancestor of BST
```python
def lca_bst(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root  # split point is the LCA
# Time: O(h), Space: O(1)
```

### Problem 4: Lowest Common Ancestor of Binary Tree (not BST)
```python
def lca_tree(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lca_tree(root.left, p, q)
    right = lca_tree(root.right, p, q)
    if left and right:
        return root  # p and q are in different subtrees
    return left or right  # both in same subtree
# Time: O(n), Space: O(h)
```

### Problem 5: Binary Tree Right Side View
```python
def right_side_view(root):
    if not root: return []
    result = []
    queue = deque([root])
    while queue:
        for i in range(len(queue)):
            node = queue.popleft()
            if i == len(queue):  # last node in level (already decremented)
                result.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
    # Simpler: just take last element of each BFS level
    return result

def right_side_view_clean(root):
    result = []
    queue = deque([root]) if root else deque()
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:
                result.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
    return result
```

### Problem 6: Path Sum II (All root-to-leaf paths with target sum)
```python
def path_sum(root, target):
    result = []
    def dfs(node, remaining, path):
        if not node: return
        path.append(node.val)
        if not node.left and not node.right and remaining == node.val:
            result.append(list(path))  # copy the path
        dfs(node.left, remaining - node.val, path)
        dfs(node.right, remaining - node.val, path)
        path.pop()  # backtrack
    dfs(root, target, [])
    return result
# Time: O(n^2) worst case (copy paths), Space: O(h)
```

### Problem 7: Diameter of Binary Tree
```python
def diameter_of_binary_tree(root):
    max_diameter = [0]
    def depth(node):
        if not node: return 0
        left = depth(node.left)
        right = depth(node.right)
        max_diameter[0] = max(max_diameter[0], left + right)
        return 1 + max(left, right)
    depth(root)
    return max_diameter[0]
# Time: O(n), Space: O(h)
# Key: diameter at each node = left_depth + right_depth
```

### Problem 8: Serialize and Deserialize Binary Tree
```python
class Codec:
    def serialize(self, root):
        result = []
        def preorder(node):
            if not node:
                result.append('null')
                return
            result.append(str(node.val))
            preorder(node.left)
            preorder(node.right)
        preorder(root)
        return ','.join(result)

    def deserialize(self, data):
        tokens = iter(data.split(','))
        def build():
            val = next(tokens)
            if val == 'null':
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node
        return build()
# Time: O(n), Space: O(n)
```

---

## Part 3: Graph Problems (1.5 hours)

### Graph Setup

```python
# Adjacency list (most common in interviews)
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0],
    3: [1]
}

# Grid graph — 4-directional neighbors
directions = [(0,1),(0,-1),(1,0),(-1,0)]
```

### Problem 9: Number of Islands
```python
def num_islands(grid):
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'  # mark visited by sinking the island
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count
# Time: O(m*n), Space: O(m*n) recursive stack
```

### Problem 10: Clone Graph
```python
def clone_graph(node):
    if not node: return None
    cloned = {}  # original node -> cloned node

    def dfs(n):
        if n in cloned: return cloned[n]
        clone = Node(n.val)
        cloned[n] = clone
        for neighbor in n.neighbors:
            clone.neighbors.append(dfs(neighbor))
        return clone

    return dfs(node)
# Time: O(V+E), Space: O(V)
```

### Problem 11: Course Schedule (Cycle Detection in DAG)
```python
def can_finish(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    # 0 = unvisited, 1 = visiting (in current path), 2 = done
    state = [0] * num_courses

    def has_cycle(node):
        if state[node] == 1: return True   # cycle detected
        if state[node] == 2: return False  # already processed

        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor): return True
        state[node] = 2
        return False

    return not any(has_cycle(i) for i in range(num_courses))
# Time: O(V+E), Space: O(V)
```

### Problem 12: Topological Sort (Course Schedule II)
```python
def find_order(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    order = []
    state = [0] * num_courses

    def dfs(node):
        if state[node] == 1: return False  # cycle
        if state[node] == 2: return True   # done

        state[node] = 1
        for neighbor in graph[node]:
            if not dfs(neighbor): return False
        state[node] = 2
        order.append(node)  # add after processing all dependencies
        return True

    for i in range(num_courses):
        if not dfs(i): return []

    return order[::-1]  # reverse gives topological order
```

### Problem 13: Word Ladder (BFS — Shortest Path)
```python
from collections import deque

def ladder_length(begin_word, end_word, word_list):
    word_set = set(word_list)
    if end_word not in word_set: return 0

    queue = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, steps = queue.popleft()
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]
                if new_word == end_word: return steps + 1
                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, steps + 1))
    return 0
# Time: O(M^2 * N) where M = word length, N = num words
```

### Problem 14: Pacific Atlantic Water Flow
```python
def pacific_atlantic(heights):
    rows, cols = len(heights), len(heights[0])
    pacific = set()  # cells that can reach Pacific
    atlantic = set()  # cells that can reach Atlantic

    def dfs(r, c, visited, prev_height):
        if (r, c) in visited or r < 0 or r >= rows or c < 0 or c >= cols:
            return
        if heights[r][c] < prev_height:  # water can't flow uphill
            return
        visited.add((r, c))
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            dfs(r+dr, c+dc, visited, heights[r][c])

    # Start from ocean borders and flow INWARD (reverse the flow)
    for r in range(rows):
        dfs(r, 0, pacific, heights[r][0])
        dfs(r, cols-1, atlantic, heights[r][cols-1])
    for c in range(cols):
        dfs(0, c, pacific, heights[0][c])
        dfs(rows-1, c, atlantic, heights[rows-1][c])

    return [[r, c] for r in range(rows) for c in range(cols)
            if (r,c) in pacific and (r,c) in atlantic]
# Time: O(m*n), Space: O(m*n)
```

---

## Day 3 Checklist
- [ ] Trees: Traversals (all 4), Max Depth, Validate BST
- [ ] Trees: LCA, Right Side View, Path Sum, Diameter
- [ ] Trees: Serialize/Deserialize
- [ ] Graphs: Number of Islands, Clone Graph
- [ ] Graphs: Course Schedule (cycle), Topological Sort
- [ ] Graphs: Word Ladder (BFS shortest path)

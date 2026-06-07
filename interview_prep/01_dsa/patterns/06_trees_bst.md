# 06 - Trees & BST Traversal
> When the input is a binary tree (or BST) and the answer is a property/aggregate that follows from each node's relationship to its children — recurse.

## When to use it (recognition triggers)
- Input is a `TreeNode` with `left`/`right`, or you're told it's a "binary tree" / "binary search tree".
- The answer at a node can be computed from its children's answers (height, balance, path sums, subtree match) — classic **post-order DFS**.
- You need things in sorted order, or to exploit `left < node < right` — that's a **BST in-order traversal** (in-order of a BST is sorted ascending).
- You need per-level / breadth grouping (level order, right-side view, min depth, zigzag) — that's **BFS with a queue**.
- You must rebuild or encode a tree (construct from traversals, serialize/deserialize) — fix a canonical traversal order and recurse.
- "Lowest common ancestor", "diameter", "max path sum" — node-level DFS where each node returns one thing upward but may update a global answer.

## Mental model
- A binary tree is self-similar: solve the whole tree by solving `left`, solving `right`, then combining at the current node. This combine step is the entire algorithm.
- Pick the traversal that matches the data flow: **pre-order** (node, left, right) when a node must be processed before its children (serialize, build a copy); **in-order** (left, node, right) when you need BST sorted order; **post-order** (left, right, node) when a node needs its children's results first (height, balance, sums).
- The "return one value up, mutate a shared answer to the side" idiom is the workhorse for diameter / max-path-sum: the function returns the best *single downward path*, but the global answer may *fork through* the node using both children.
- BST gives you a comparison shortcut: at each node you can discard half the tree. LCA, search, validation, and kth-smallest all use this to beat the generic O(n) where possible.
- For BFS, process the queue **one full level at a time** (snapshot `len(queue)` before the inner loop) so you can group/aggregate per level.

## Reusable template(s)
```python
from collections import deque
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- Post-order DFS: each node returns a value computed from children ---
def post_order(node: Optional[TreeNode]) -> int:
    if not node:
        return 0                      # base case: empty subtree
    l = post_order(node.left)
    r = post_order(node.right)
    return combine(l, r, node.val)    # combine children's results at this node

# --- In-order DFS (BST -> sorted stream); iterative with explicit stack ---
def in_order(root: Optional[TreeNode]):
    stack, cur = [], root
    while stack or cur:
        while cur:                    # go as far left as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()             # leftmost unvisited node
        yield cur.val                 # visit (values come out sorted for a BST)
        cur = cur.right               # then explore right subtree

# --- BFS level-order: process one level per outer iteration ---
def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):       # snapshot size = current level's node count
            n = q.popleft()
            level.append(n.val)
            if n.left:  q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out
```

## Complexity profile
- DFS / BFS over a tree visit each node once: **time O(n)**.
- Space is the recursion depth (or queue width): **O(h)** for DFS where h is height — O(log n) balanced, O(n) skewed — and **O(w)** for BFS where w is the max level width (up to O(n)).
- Brute force you're beating: re-walking subtrees from each node (e.g. naive diameter / balance recomputing height repeatedly) which is O(n²); a single post-order pass collapses it to O(n).

## Curated problems (easy -> hard)

### 1. Invert Binary Tree  -  Easy
- **Problem:** Given the root of a binary tree, swap every node's left and right child and return the new root.
- **Practice (free):** https://leetcode.com/problems/invert-binary-tree/
- **Video (free):** https://neetcode.io/problems/invert-a-binary-tree
- **Idea:** Recurse, swap the two child pointers at every node. Order of swap vs recursion doesn't matter.
```python
def invertTree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```
- **Complexity:** Time O(n), Space O(h) recursion stack.
- **Key insight / gotcha:** Swap pointers, not values. The simultaneous tuple assignment evaluates the right side first, so you don't need a temp variable.
- **Follow-up:** Do it iteratively — use a BFS queue or DFS stack and swap children as you pop each node.

### 2. Maximum Depth of Binary Tree  -  Easy
- **Problem:** Return the number of nodes along the longest path from the root down to the farthest leaf.
- **Practice (free):** https://leetcode.com/problems/maximum-depth-of-binary-tree/
- **Video (free):** https://neetcode.io/problems/depth-of-binary-tree
- **Idea:** Depth = 1 + max(depth of left, depth of right); empty subtree has depth 0.
```python
def maxDepth(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** This post-order "return 1 + max of children" is the height primitive reused by Diameter and Balanced — internalize it.
- **Follow-up:** Minimum depth differs: a node with one missing child is NOT a leaf, so you take the min only over *existing* children, else 1 + the present child's depth.

### 3. Same Tree  -  Easy
- **Problem:** Given two binary trees, return true iff they are structurally identical with equal node values.
- **Practice (free):** https://leetcode.com/problems/same-tree/
- **Video (free):** https://neetcode.io/problems/same-binary-tree
- **Idea:** Compare roots, then recurse on (left,left) and (right,right). Both null => equal; one null or values differ => not equal.
```python
def isSameTree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if not p and not q:
        return True
    if not p or not q or p.val != q.val:
        return False
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** Check the both-null case before the one-null case, otherwise you mis-handle leaves. This is the helper that Subtree-of-Another-Tree leans on.
- **Follow-up:** Symmetric Tree is the mirror version — compare (left.left, right.right) and (left.right, right.left).

### 4. Subtree of Another Tree  -  Easy
- **Problem:** Return true if `subRoot` is a subtree of `root` (same structure and values, anchored at some node of `root`).
- **Practice (free):** https://leetcode.com/problems/subtree-of-another-tree/
- **Video (free):** https://neetcode.io/problems/subtree-of-another-tree
- **Idea:** At each node of `root`, test `isSameTree(node, subRoot)`; otherwise recurse into children. Reuses Same Tree as a helper.
```python
def isSubtree(root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
    if not subRoot:
        return True            # empty tree is a subtree of anything
    if not root:
        return False           # non-empty subRoot can't match empty root
    if isSameTree(root, subRoot):
        return True
    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)
```
- **Complexity:** Time O(n·m) worst case (n,m = node counts), Space O(h).
- **Key insight / gotcha:** A subtree must match *all the way down to the leaves* — `subRoot` matches only if there are no extra descendants. A partial value match higher up is not enough.
- **Follow-up:** Optimize to O(n+m) by serializing both trees (with null markers) and checking substring containment via KMP, or hashing each subtree (Merkle-style).

### 5. Diameter of Binary Tree  -  Easy
- **Problem:** Return the length (in edges) of the longest path between any two nodes; the path need not pass through the root.
- **Practice (free):** https://leetcode.com/problems/diameter-of-binary-tree/
- **Video (free):** https://neetcode.io/problems/binary-tree-diameter
- **Idea:** For each node the longest path *through* it = leftHeight + rightHeight; track the max globally while a post-order returns each node's height upward.
```python
def diameterOfBinaryTree(root: Optional[TreeNode]) -> int:
    best = 0
    def height(node: Optional[TreeNode]) -> int:
        nonlocal best
        if not node:
            return 0
        l = height(node.left)
        r = height(node.right)
        best = max(best, l + r)      # path forking through this node (in edges)
        return 1 + max(l, r)         # height returned to parent (single path)
    height(root)
    return best
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** The function *returns* one downward path (1 + max) but *updates* the answer with the fork (l + r). Returning l+r would be wrong — a parent can't extend a path that already used both children.
- **Follow-up:** "Longest path with equal values" / "longest univalue path" — same skeleton, but only extend a side when the child's value equals the node's value.

### 6. Balanced Binary Tree  -  Easy
- **Problem:** Return true if for every node the heights of its two subtrees differ by at most 1.
- **Practice (free):** https://leetcode.com/problems/balanced-binary-tree/
- **Video (free):** https://neetcode.io/problems/balanced-binary-tree
- **Idea:** One post-order that returns height, but signals imbalance with a sentinel (-1) so the whole tree short-circuits in O(n).
```python
def isBalanced(root: Optional[TreeNode]) -> bool:
    def check(node: Optional[TreeNode]) -> int:
        if not node:
            return 0
        l = check(node.left)
        if l == -1: return -1                 # left subtree already unbalanced
        r = check(node.right)
        if r == -1: return -1
        if abs(l - r) > 1:
            return -1                          # imbalance found here
        return 1 + max(l, r)
    return check(root) != -1
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** The naive version (compute height separately for every node) is O(n²). The -1 sentinel folds the balance check into the height pass for O(n) — a very common interviewer escalation.
- **Follow-up:** "How would you keep it balanced under insertions?" — that's the motivation for self-balancing BSTs (AVL / red-black), which rotate to bound height at O(log n).

### 7. Binary Tree Level Order Traversal  -  Medium
- **Problem:** Return the node values grouped level by level, top to bottom, left to right.
- **Practice (free):** https://leetcode.com/problems/binary-tree-level-order-traversal/
- **Video (free):** https://neetcode.io/problems/level-order-traversal-of-binary-tree
- **Idea:** BFS with a queue; snapshot the queue length at the start of each level to know how many nodes belong to it.
```python
def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):          # fixed: exactly this level's nodes
            n = q.popleft()
            level.append(n.val)
            if n.left:  q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out
```
- **Complexity:** Time O(n), Space O(w) for the queue (max level width).
- **Key insight / gotcha:** You must capture `len(q)` *before* the inner loop; appending children mid-loop changes the queue size and would merge levels.
- **Follow-up:** Zigzag order — reverse every other level (or `appendleft` into a deque based on level parity).

### 8. Binary Tree Right Side View  -  Medium
- **Problem:** Return the values visible when looking at the tree from the right side, top to bottom (the last node of each level).
- **Practice (free):** https://leetcode.com/problems/binary-tree-right-side-view/
- **Video (free):** https://neetcode.io/problems/binary-tree-right-side-view
- **Idea:** Level-order BFS; the last node dequeued at each level is the rightmost visible one.
```python
def rightSideView(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        size = len(q)
        for i in range(size):
            n = q.popleft()
            if i == size - 1:            # last node in this level = rightmost
                out.append(n.val)
            if n.left:  q.append(n.left)
            if n.right: q.append(n.right)
    return out
```
- **Complexity:** Time O(n), Space O(w).
- **Key insight / gotcha:** "Rightmost" is per-level, not "the right subtree." A deep left subtree can be the only node on a level and is then visible. Enqueue left before right and take the last of the level.
- **Follow-up:** DFS alternative — traverse right-before-left and record the first node seen at each new depth: `if depth == len(out): out.append(node.val)`.

### 9. Lowest Common Ancestor of a Binary Search Tree  -  Medium
- **Problem:** Given a BST and two nodes p, q, return their lowest common ancestor (the deepest node that has both as descendants).
- **Practice (free):** https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/
- **Video (free):** https://neetcode.io/problems/lowest-common-ancestor-in-binary-search-tree
- **Idea:** Walk from the root: if both values are smaller go left, if both larger go right; the first node where they split (or that equals one of them) is the LCA.
```python
def lowestCommonAncestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    cur = root
    while cur:
        if p.val < cur.val and q.val < cur.val:
            cur = cur.left              # both in left subtree
        elif p.val > cur.val and q.val > cur.val:
            cur = cur.right             # both in right subtree
        else:
            return cur                  # split point (or cur == p or q) -> LCA
```
- **Complexity:** Time O(h), Space O(1) iterative.
- **Key insight / gotcha:** This is O(h), not O(n) — you exploit BST ordering to never explore both subtrees. The split point is the answer; if one node equals `cur`, `cur` is its own ancestor.
- **Follow-up:** LCA in a *general* binary tree (no ordering): recurse, return the node if found `p`/`q` in both subtrees or matched here — `if left and right: return node`.

### 10. Validate Binary Search Tree  -  Medium
- **Problem:** Return true if a binary tree is a valid BST: every node's value is strictly greater than all values in its left subtree and strictly less than all in its right subtree.
- **Practice (free):** https://leetcode.com/problems/validate-binary-search-tree/
- **Video (free):** https://neetcode.io/problems/valid-binary-search-tree
- **Idea:** Carry an allowed (low, high) open interval down the tree; each node must lie strictly inside, and it tightens the bound for its children.
```python
def isValidBST(root: Optional[TreeNode]) -> bool:
    def valid(node, low, high) -> bool:
        if not node:
            return True
        if not (low < node.val < high):    # must be strictly within bounds
            return False
        return (valid(node.left, low, node.val) and
                valid(node.right, node.val, high))
    return valid(root, float('-inf'), float('inf'))
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** Checking only `node.left.val < node.val < node.right.val` locally is WRONG — a deep descendant can violate an ancestor's bound. The interval must propagate from ancestors, not just the immediate parent.
- **Follow-up:** Alternative: do an in-order traversal and verify the values come out strictly increasing (track the previous value) — same O(n), and it's the cleaner mental check for "is it a BST."

### 11. Kth Smallest Element in a BST  -  Medium
- **Problem:** Return the k-th smallest value in a BST (1-indexed).
- **Practice (free):** https://leetcode.com/problems/kth-smallest-element-in-a-bst/
- **Video (free):** https://neetcode.io/problems/kth-smallest-integer-in-bst
- **Idea:** In-order traversal of a BST yields sorted values; stop at the k-th one. Iterative stack lets you halt early without walking the whole tree.
```python
def kthSmallest(root: Optional[TreeNode], k: int) -> int:
    stack, cur = [], root
    while stack or cur:
        while cur:                    # dive to the leftmost node
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:                    # k-th smallest in sorted (in-order) order
            return cur.val
        cur = cur.right
    return -1                          # unreachable for valid k
```
- **Complexity:** Time O(h + k), Space O(h).
- **Key insight / gotcha:** In-order = ascending for a BST. The iterative version stops as soon as you've popped k nodes — no need to traverse the rest.
- **Follow-up:** If the tree is modified often and many kth-queries arrive, augment each node with its subtree size so each query is O(h) by counting left-subtree sizes.

### 12. Construct Binary Tree from Preorder and Inorder Traversal  -  Medium
- **Problem:** Given preorder and inorder traversals of a tree with unique values, reconstruct and return the tree.
- **Practice (free):** https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/
- **Video (free):** https://neetcode.io/problems/build-binary-tree-from-preorder-and-inorder-traversal
- **Idea:** Preorder's first element is the root; its index in inorder splits inorder into left and right subtrees (and tells you each subtree's size). Recurse, consuming preorder front-to-back.
```python
def buildTree(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    idx = {v: i for i, v in enumerate(inorder)}   # value -> inorder position
    self_pre = iter(range(len(preorder)))         # not needed; use a pointer
    pre_pos = 0
    def build(lo: int, hi: int) -> Optional[TreeNode]:
        nonlocal pre_pos
        if lo > hi:
            return None
        root_val = preorder[pre_pos]
        pre_pos += 1                              # consume this root
        node = TreeNode(root_val)
        mid = idx[root_val]                       # split point in inorder
        node.left = build(lo, mid - 1)            # build left BEFORE right
        node.right = build(mid + 1, hi)
        return node
    return build(0, len(inorder) - 1)
```
- **Complexity:** Time O(n) with the inorder hash map (else O(n²) from repeated scans), Space O(n).
- **Key insight / gotcha:** Build the left subtree before the right — preorder lists the entire left subtree immediately after the root, so the moving `pre_pos` pointer must consume it first. The hash map turns "find root in inorder" from O(n) into O(1).
- **Follow-up:** From postorder + inorder: postorder's *last* element is the root, so consume postorder back-to-front and build the right subtree before the left.

### 13. Binary Tree Maximum Path Sum  -  Hard
- **Problem:** Find the maximum sum of any non-empty path; a path is any sequence of connected nodes (need not pass through the root, can start/end anywhere).
- **Practice (free):** https://leetcode.com/problems/binary-tree-maximum-path-sum/
- **Video (free):** https://neetcode.io/problems/binary-tree-maximum-path-sum
- **Idea:** Post-order: each call returns the best *downward* path gain from this node (node + best of one child, clamped at 0). Meanwhile update a global with the best *fork* through the node (node + left gain + right gain).
```python
def maxPathSum(root: TreeNode) -> int:
    best = float('-inf')
    def gain(node: Optional[TreeNode]) -> int:
        nonlocal best
        if not node:
            return 0
        l = max(gain(node.left), 0)      # drop negative subtree contributions
        r = max(gain(node.right), 0)
        best = max(best, node.val + l + r)   # path peaking at this node (fork)
        return node.val + max(l, r)          # extendable downward path for parent
    gain(root)
    return best
```
- **Complexity:** Time O(n), Space O(h).
- **Key insight / gotcha:** Two distinct quantities: the *returned* value can use only one child (so the parent can extend it into a path); the *global update* may use both children (the path turns at this node and can't go higher). Clamp negative gains to 0 — never worth including a path that hurts you.
- **Follow-up:** "Return the actual path, not just the sum" — store the node alongside the best fork and reconstruct by re-descending, choosing the child branch that produced each gain.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the post-order height/diameter/balance template from memory
- [ ] I can write the iterative in-order traversal from memory
- [ ] I can write the BFS level-order loop (with `len(q)` snapshot) from memory
- [ ] Invert Binary Tree — 🟡
- [ ] Maximum Depth — 🟡
- [ ] Same Tree — 🟡
- [ ] Subtree of Another Tree — 🟡
- [ ] Diameter of Binary Tree — 🟡
- [ ] Balanced Binary Tree (O(n) sentinel) — 🟡
- [ ] Level Order Traversal — 🟡
- [ ] Right Side View — 🟡
- [ ] LCA of a BST — 🟡
- [ ] Validate BST (interval method) — 🟡
- [ ] Kth Smallest in BST (early-stop in-order) — 🟡
- [ ] Construct from Preorder + Inorder — 🔴
- [ ] Serialize/Deserialize (see Follow-up note below) — 🔴
- [ ] Binary Tree Maximum Path Sum — 🔴

> Note: Serialize and Deserialize Binary Tree is folded in here as the canonical "encode a tree via traversal" exercise. Use **pre-order with explicit null markers**: serialize -> `node.val` then recurse left, right, writing `"#"` for null; deserialize -> read tokens left-to-right, build node, then recurse left, right. It is LeetCode Hard (https://leetcode.com/problems/serialize-and-deserialize-binary-tree/, free video https://neetcode.io/problems/serialize-and-deserialize-binary-tree). Template below.

```python
class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        out = []
        def dfs(node):
            if not node:
                out.append("#")               # null marker preserves structure
                return
            out.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ",".join(out)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        vals = iter(data.split(","))
        def dfs():
            v = next(vals)
            if v == "#":
                return None
            node = TreeNode(int(v))
            node.left = dfs()                 # same pre-order consumption order
            node.right = dfs()
            return node
        return dfs()
```
- **Complexity:** Time O(n) each way, Space O(n).
- **Key insight / gotcha:** Null markers are mandatory — without them a single traversal is ambiguous and can't be uniquely rebuilt. Serialize and deserialize must agree on the exact order (here pre-order); the deserializer consumes tokens in the same order they were written.

## Resources
- **Free:** NeetCode Trees roadmap section — https://neetcode.io/roadmap (Trees) ; LeetCode "Binary Tree" Explore card — https://leetcode.com/explore/learn/card/data-structure-tree/ ; takeUforward/Striver tree series (search) — https://www.youtube.com/results?search_query=striver+binary+tree+series
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" tree/BFS-DFS patterns — https://www.designgurus.io (free alternative: the NeetCode roadmap Trees section above covers the same patterns with video walkthroughs).

# Trie + Word Search — Confirmed 6sense Topic
**Study this carefully — this is a known 6sense problem**

---

## Part 1: Trie (Prefix Tree)

### Why Trie?
- O(L) insert and search where L = word length
- Critical for problems involving: prefix matching, dictionary lookups, word search in grid
- Better than HashSet when you need prefix queries

### Trie Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char -> TrieNode
        self.is_end = False     # marks end of a valid word
        self.word = None        # store the word itself (useful for Word Search II)

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word  # store word at end node

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
```

---

## Part 2: Word Search II (Confirmed 6sense Problem)

**Problem:** Given a 2D grid of characters and a list of words, find all words that exist in the grid. Words can be formed by sequentially adjacent cells in **all 8 directions** (horizontal, vertical, diagonal). A cell may not be used more than once per word.

**Why Trie?** Without Trie, you'd call DFS once per word = O(words × m×n×8^L). With Trie, one DFS pass finds ALL words = O(m×n×8^L).

```python
def find_words(board, words):
    # Build Trie from word list
    root = TrieNode()
    trie = Trie()
    for word in words:
        trie.insert(word)

    rows, cols = len(board), len(board[0])
    result = set()

    # 8 directions: horizontal, vertical, AND diagonal
    directions = [
        (-1,-1), (-1,0), (-1,1),
        ( 0,-1),          (0,1),
        ( 1,-1),  (1,0),  (1,1)
    ]

    def dfs(r, c, node, path):
        char = board[r][c]
        if char not in node.children:
            return
        next_node = node.children[char]
        if next_node.word:
            result.add(next_node.word)
            # Don't return — longer words may exist along this path

        board[r][c] = '#'  # mark visited (in-place, no extra space)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                dfs(nr, nc, next_node, path + board[nr][nc])
        board[r][c] = char  # restore (backtrack)

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")

    return list(result)

# Time: O(m*n*8^L) where L = max word length
# Space: O(W*L) for Trie where W = number of words
# Key insight: Trie prunes dead-end paths early — if no word starts with current prefix, stop DFS
```

### Optimization: Prune Trie nodes after finding a word
```python
# After finding a word, remove its leaf node so we don't find it again
def dfs_optimized(r, c, node):
    char = board[r][c]
    if char not in node.children:
        return
    next_node = node.children[char]
    if next_node.word:
        result.add(next_node.word)
        next_node.word = None  # clear to avoid re-adding

    board[r][c] = '#'
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
            dfs_optimized(nr, nc, next_node)
    board[r][c] = char

    # Prune: if this node has no more words in its subtree, remove it
    if not next_node.children and not next_node.word:
        del node.children[char]
```

---

## Part 3: Word Search I (Single Word, 4 directions — simpler variant)

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word): return True
        if r < 0 or r >= rows or c < 0 or c >= cols: return False
        if board[r][c] != word[idx]: return False

        board[r][c] = '#'  # mark visited
        found = (dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or
                 dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1))
        board[r][c] = word[idx]  # restore
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0): return True
    return False
# Time: O(m*n*4^L), Space: O(L) recursive stack
```

---

## Part 4: Other Trie Problems (Bonus)

### Implement Search with Wildcard ('.' matches any letter)
```python
def search_with_wildcard(word, root):
    def dfs(node, i):
        if i == len(word):
            return node.is_end
        char = word[i]
        if char == '.':
            return any(dfs(child, i+1) for child in node.children.values())
        if char not in node.children:
            return False
        return dfs(node.children[char], i+1)
    return dfs(root, 0)
```

### Longest Word With All Prefixes in Dictionary
```python
def longest_word(words):
    trie = Trie()
    for word in words:
        trie.insert(word)

    result = ""
    def dfs(node, current):
        nonlocal result
        if len(current) > len(result):
            result = current
        for char, child in node.children.items():
            if child.is_end:  # only follow valid word prefixes
                dfs(child, current + char)

    dfs(trie.root, "")
    return result
```

---

## How to Explain Trie in Interview

```
"I'll use a Trie here. Without it, searching for each word separately 
means traversing the grid once per word — O(words × m×n). 

With a Trie, I build the prefix tree once and run a single DFS pass 
over the grid. At each cell, I follow the Trie: if the current path 
doesn't match any prefix, I prune immediately. This way one pass 
finds all words.

Time: O(m×n×8^L) where L is max word length.
Space: O(total characters in all words) for the Trie."
```

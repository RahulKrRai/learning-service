# 07 - Trie (Prefix Tree)
> One-line: when you need fast prefix/word lookups over a set of strings, or to share work across many strings that have common prefixes.

## When to use it (recognition triggers)
- The problem talks about **prefixes**, **autocomplete**, **dictionary**, or "words that start with...".
- You must do **many** lookups against a **set of words** (a hash set handles full-word lookup, but not prefix queries cheaply).
- You need to match patterns with **wildcards** (`.` matches any char) — a Trie lets you branch only into existing children.
- You're searching a **grid/board for many words at once** and want to prune dead paths early (Word Search II) instead of running a separate DFS per word.
- Word-by-word or character-by-character **streaming** matching where shared prefixes should share computation.

## Mental model
- A Trie is a tree where each **edge is a character** and each **node represents a prefix** (the string spelled by the path from the root). The root is the empty prefix.
- Storing `n` words with shared prefixes collapses those prefixes into a single shared path, so lookups cost `O(word length)` regardless of how many words are stored — independent of `n`.
- A boolean flag (call it `is_end`/`$`) marks nodes that are the **end of a real word**, distinguishing the word `"app"` from the mere prefix of `"apple"`.
- Children are usually a `dict[char -> node]` (clean, handles any alphabet) or a fixed-size array of 26 (slightly faster, lowercase-only). Use the dict in interviews unless asked to optimize.
- Wildcards and grid search both work by **DFS over the Trie**: a `.` tries every child; a board search walks the board and the Trie in lockstep, abandoning a branch the instant the current character isn't a child.

## Reusable template(s)
```python
# Dict-based Trie. Each node is a dict of children plus an end marker.
class TrieNode:
    __slots__ = ("children", "is_end")
    def __init__(self):
        self.children = {}      # char -> TrieNode
        self.is_end = False     # True if a word ends here

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def _walk(self, s: str):
        # Return the node reached by following s, or None if any char is missing.
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
```

```python
# Even leaner: a plain nested dict as the Trie, with '$' as the end sentinel.
# Common in interviews because there's no class boilerplate.
def build_trie(words):
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})   # create child if absent, descend
        node['$'] = True                     # mark end of word
    return root
```

## Complexity profile
- **Insert / search / startsWith:** `O(L)` time where `L` = length of the word/prefix; independent of how many words are stored.
- **Space:** `O(total characters inserted)` in the worst case (no shared prefixes); shared prefixes save memory.
- **What you're beating:** a hash set gives `O(L)` full-word lookup but **cannot** answer prefix queries without scanning all `n` words (`O(n·L)` per prefix). Sorting + binary search gives `O(L·log n)` per prefix but doesn't share work for multi-word grid search. The Trie makes prefix work `O(L)` and lets grid/wildcard search prune across all words simultaneously.

## Curated problems (easy -> hard)

### 1. Implement Trie (Prefix Tree)  -  Medium
- **Problem:** Build a data structure supporting `insert(word)`, `search(word)` (exact word present?), and `startsWith(prefix)` (any word with this prefix?).
- **Practice (free):** https://leetcode.com/problems/implement-trie-prefix-tree/
- **Video (free):** https://neetcode.io/problems/implement-prefix-tree
- **Idea:** Walk character by character creating nodes on insert; mark word-ends with `is_end`. `search` requires reaching a node **and** that node being a word-end; `startsWith` only requires reaching a node.
```python
class TrieNode:
    __slots__ = ("children", "is_end")
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node
```
- **Complexity:** Time `O(L)` per op, Space `O(total chars inserted)`.
- **Key insight / gotcha:** The single most common bug is conflating "reached a node" with "found a word." `search("app")` must return `False` if you only inserted `"apple"` — the node for `app` exists but `is_end` is `False`.
- **Follow-up:** "Add `delete(word)`." Walk to the end, unset `is_end`; then unwind, pruning any node that has no children and is not itself a word-end. Be careful not to delete nodes shared by other words.

### 2. Design Add and Search Words Data Structure  -  Medium
- **Problem:** Support `addWord(word)` and `search(word)` where the search word may contain `.`, a wildcard that matches **any single letter**.
- **Practice (free):** https://leetcode.com/problems/design-add-and-search-words-data-structure/
- **Video (free):** https://neetcode.io/problems/design-word-search-data-structure
- **Idea:** Store words in a Trie as usual. For search, DFS: on a normal char descend into that one child; on `.` recurse into **every** child. Match succeeds when you consume the whole word at a node whose `is_end` is `True`.
```python
class WordDictionary:
    def __init__(self):
        self.root = {}                       # nested-dict Trie, '$' marks end

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True

    def search(self, word: str) -> bool:
        def dfs(node, i: int) -> bool:
            if i == len(word):
                return '$' in node           # full word consumed; is it an end?
            ch = word[i]
            if ch == '.':                    # wildcard: try every real child
                for k, child in node.items():
                    if k != '$' and dfs(child, i + 1):
                        return True
                return False
            if ch not in node:               # concrete char must exist
                return False
            return dfs(node[ch], i + 1)
        return dfs(self.root, 0)
```
- **Complexity:** Time `O(L)` for a wildcard-free search; worst case `O(26^d · L)`-ish when many `.`'s force branching (in practice bounded by the number of nodes visited). Space `O(L)` recursion depth plus the stored Trie.
- **Key insight / gotcha:** When iterating children for `.`, **skip the `'$'` end-marker key** — it's a sentinel, not a character. Forgetting this either crashes or treats `$` as a matchable letter.
- **Follow-up:** "What if `*` (matches zero or more)?" That turns it into regex matching; DFS still works but at each `*` you branch into "consume one more board/Trie char and stay on `*`" vs. "skip `*`," and you must memoize `(node, i)` to avoid exponential blowup.

### 3. Word Search II  -  Hard
- **Problem:** Given an `m x n` board of letters and a list of `words`, return every word that can be formed by a path of horizontally/vertically adjacent cells, where each cell is used at most once per word.
- **Practice (free):** https://leetcode.com/problems/word-search-ii/
- **Video (free):** https://neetcode.io/problems/search-for-word-ii
- **Idea:** Build a Trie of **all** the words, then DFS the board once, walking board and Trie together. The Trie prunes instantly when the current cell's letter isn't a Trie child, so you search for every word simultaneously instead of re-scanning per word.
```python
from typing import List

def findWords(board: List[List[str]], words: List[str]) -> List[str]:
    # Build Trie; store the full word at its end node for easy collection.
    trie = {}
    for w in words:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
        node['$'] = w

    rows, cols = len(board), len(board[0])
    res = []

    def dfs(r: int, c: int, node: dict) -> None:
        ch = board[r][c]
        nxt = node.get(ch)
        if nxt is None:                     # no word continues with this letter -> prune
            return
        word = nxt.pop('$', None)           # found a complete word; pop to avoid dupes
        if word is not None:
            res.append(word)

        board[r][c] = '#'                   # mark visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                dfs(nr, nc, nxt)
        board[r][c] = ch                    # restore (backtrack)

        if not nxt:                         # leaf with no children left -> prune from parent
            del node[ch]

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie)
    return res
```
- **Complexity:** Time `O(m·n·4·3^(L-1))` worst case where `L` is the longest word (each cell starts a DFS that branches into 3 unvisited neighbors per step), but Trie pruning makes the practical runtime far smaller. Space `O(total chars in words)` for the Trie.
- **Key insight / gotcha:** Two crucial optimizations: (1) **pop the word** from the end node when you find it so the same word isn't reported twice from different paths; (2) **delete exhausted leaf nodes** (`if not nxt: del node[ch]`) — this incrementally shrinks the Trie and is what turns TLE into AC on large inputs. Also remember to restore `board[r][c]` on backtrack.
- **Follow-up:** "Words can reuse a cell" — then it's no longer a path-uniqueness problem; you'd drop the visited-marking, but you'd need a different termination guard (e.g., bounded depth) since infinite revisits become possible. "Tens of thousands of words" — the shared Trie and leaf-pruning are exactly why this scales versus running Word Search I per word.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the dict-Trie and node-class templates from memory
- [ ] Implement Trie — 🔴 / 🟡 / 🟢
- [ ] Add and Search Words (wildcard `.`) — 🔴 / 🟡 / 🟢
- [ ] Word Search II (grid + Trie pruning + leaf deletion) — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode "Tries" roadmap section — https://neetcode.io/roadmap ; LeetCode Trie explore card / study plan — https://leetcode.com/explore/learn/card/trie/ ; takeUforward / striver Trie playlist (search) — https://www.youtube.com/results?search_query=takeuforward+trie+playlist
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Trie module) — https://www.designgurus.io (free alternative: the NeetCode roadmap Tries section above, which covers all three problems with video walkthroughs).

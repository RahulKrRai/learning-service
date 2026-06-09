# 22 - Object-Oriented / Low-Level Design (coding rounds)
> One-line: when the prompt is "design a data structure / mini-system" — you win on clean class design and the *right data-structure combo*, not on a clever algorithm.

> **Companion file:** this covers *data-structure* LLD (O(1) contracts: LRU/LFU/iterators). For *object-modeling* LLD — "design a parking lot / elevator / Splitwise / vending machine / movie booking", with entities, enums, and design patterns — see [../../02_system_design/low_level_design.md](../../02_system_design/low_level_design.md).

> **HIGH PRIORITY.** Atlassian builds *entire* coding rounds on this exact shape ("here's a data structure, now build it incrementally, and I'll keep adding requirements"). Amazon and Uber ask it constantly (LRU/LFU, rate limiters, GetRandom). Goldman/JPMorgan VP loops favour it because it doubles as a design signal. The skill being tested is: pick the data-structure combo that hits the required complexity, wrap it in a clean API, and extend it gracefully when constraints change — not graph theory.

## When to use it (recognition triggers)
- The prompt says **"design a ..."** / **"implement a class that supports ..."** and gives you a *method list* (`get`, `put`, `insert`, `getRandom`, `next`, `hasNext`) instead of a single function.
- There's an explicit **complexity contract** baked into the API: "all operations in O(1) average", "O(1) get and put". That contract *is* the puzzle — it dictates the data-structure combo.
- You're asked to **support an evolving set of operations** — the interviewer starts simple and adds features mid-round (Atlassian's signature move). Your code has to absorb new requirements without a rewrite.
- The problem is naturally about **entities and their relationships** (parking lot, tic-tac-toe, elevator) — they want enums, encapsulation, and clear responsibilities, and may not want runnable algorithm code at all.
- Phrases: "thread-safe-ish", "what if we also need ...", "how would you extend this", "talk me through the classes".

## Mental model
- **The complexity contract picks the data structure; the data structure picks the class.** Work backwards from the required Big-O. "O(1) get + O(1) eviction of the oldest" => you need both keyed lookup (hashmap) *and* ordered removal from either end (doubly-linked list). "O(1) insert/delete/getRandom" => array (random index) + hashmap (value -> index) + swap-with-last trick. Memorise these pairings; they recur.
- **Two layers, always.** A thin **public API** (the methods the prompt names) sitting on top of **private helpers** that manipulate the structure (`_add_node`, `_remove`, `_move_to_front`). Keep invariants inside the helpers so the public methods read like prose.
- **Sentinels kill edge cases.** A doubly-linked list with a dummy `head` and dummy `tail` means you never special-case "empty list" or "removing the only node" — every insert/remove has real neighbours on both sides. This single trick removes ~80% of LRU bugs.
- **Encapsulate the node.** A tiny inner `Node` class (key, value, prev, next) is cleaner than parallel arrays and signals OOP maturity. Store the *key* on the node too, so when you evict via the list you can also delete from the hashmap.
- **For discussion problems, design the nouns first.** Entities -> responsibilities (one class, one job) -> enums for fixed sets of states -> key methods -> relationships. Resist coding; narrate trade-offs and draw the class boxes.

## Reusable template(s)
```python
# ---- The "hashmap + doubly-linked list" skeleton (LRU / LFU backbone) ----
class Node:
    __slots__ = ("key", "val", "prev", "next")     # __slots__: less memory, faster attr access
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class DLL:
    """Doubly-linked list with sentinel head/tail so no operation hits a None edge."""
    def __init__(self):
        self.head, self.tail = Node(), Node()       # dummies, never hold real data
        self.head.next, self.tail.prev = self.tail, self.head

    def add_front(self, node):                        # insert right after head (most-recent end)
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def remove(self, node):                           # unlink an arbitrary node in O(1)
        node.prev.next, node.next.prev = node.next, node.prev

    def pop_back(self):                               # evict the node just before tail (LRU victim)
        if self.tail.prev is self.head:
            return None
        victim = self.tail.prev
        self.remove(victim)
        return victim

# ---- The "array + hashmap" skeleton (O(1) insert/delete/getRandom) ----
# vals = [];  idx = {value: position_in_vals}
# delete(x): swap vals[idx[x]] with vals[-1], fix the moved element's index, pop the tail.
```

## Complexity profile
- **Hashmap + doubly-linked list (LRU):** O(1) `get`, O(1) `put` (amortised, dict ops average O(1)); O(capacity) space. The DLL gives O(1) removal of *any* node and O(1) access to the LRU end; the hashmap gives O(1) key -> node.
- **LFU:** O(1) `get` and `put` by keeping, per frequency, its own DLL of nodes and tracking the current `min_freq`. Space O(capacity).
- **Array + hashmap (GetRandom):** O(1) `insert`, `remove`, `getRandom`. The swap-with-last avoids the O(n) shift a normal list delete costs; `random.randrange` over a contiguous array is O(1).
- **Iterators (flatten / peeking / nested):** pre-flatten = O(n) space; lazy (stack-based) = O(depth) space, O(1) amortised `next`. Know both — interviewers push on "what if the input is huge / infinite-ish".
- The point: every design here is a *constant-factor* / *space* trade against the naive version. There's rarely an asymptotic algorithm to discover — there's a structure to assemble.

## Curated problems (easy -> hard)

### 1. Min Stack  -  Easy  (cross-ref: see `09_stack` / monotonic-stack notes)
- **Problem:** Design a stack supporting `push`, `pop`, `top`, and `getMin`, all in O(1).
- **Practice (free):** https://leetcode.com/problems/min-stack/
- **Video (free):** https://neetcode.io/problems/minimum-stack
- **Idea:** Keep a second stack of running minimums in lockstep; the top of the min-stack is always the min of everything currently below. (Covered in depth in the stack pattern file — included here as the gateway design problem.)
```python
class MinStack:
    def __init__(self):
        self._stack = []
        self._mins = []                              # _mins[i] = min of _stack[:i+1]

    def push(self, val: int) -> None:
        self._stack.append(val)
        self._mins.append(val if not self._mins else min(val, self._mins[-1]))

    def pop(self) -> None:
        self._stack.pop()
        self._mins.pop()                             # keep the two stacks the same height

    def top(self) -> int:
        return self._stack[-1]

    def getMin(self) -> int:
        return self._mins[-1]
```
- **Complexity:** All operations O(1) time; O(n) extra space for the min-stack.
- **Key insight / gotcha:** The min-stack must move in lockstep with the data stack — push and pop on *both* every time, or the alignment (and your O(1) min) breaks.
- **Follow-up:** "Save space." Store only *strictly* decreasing mins, but then `pop` must compare before popping the min-stack; or encode deltas to the running min in the main stack.

### 2. Design HashMap (from scratch)  -  Easy
- **Problem:** Implement a `MyHashMap` (`put`, `get`, `remove`) without using any built-in hash table.
- **Practice (free):** https://leetcode.com/problems/design-hashmap/
- **Video (free):** https://www.youtube.com/results?search_query=design+hashmap+leetcode+separate+chaining
- **Idea:** Fixed bucket array; hash the key to a bucket; resolve collisions with separate chaining (a list per bucket). This is the "show me you understand hashing" warm-up — own it cold.
```python
class MyHashMap:
    def __init__(self, capacity: int = 1009):        # prime size => fewer collisions
        self._cap = capacity
        self._buckets = [[] for _ in range(capacity)]   # each bucket: list of [key, value]

    def _index(self, key: int) -> int:
        return key % self._cap

    def put(self, key: int, value: int) -> None:
        bucket = self._buckets[self._index(key)]
        for pair in bucket:                          # update in place if key exists
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])                  # else append a new pair

    def get(self, key: int) -> int:
        for k, v in self._buckets[self._index(key)]:
            if k == key:
                return v
        return -1                                    # contract: -1 when absent

    def remove(self, key: int) -> None:
        bucket = self._buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                return
```
- **Complexity:** O(1) average per op, O(n/capacity) = O(load factor) worst case per bucket; O(capacity + n) space.
- **Key insight / gotcha:** `put` must *update* an existing key, not blindly append — otherwise duplicates pile up in one bucket and `get` returns stale values.
- **Follow-up:** "Make it scale." Track size and **rehash** (double capacity, reinsert all) when load factor exceeds ~0.75, to keep buckets short; mention open addressing as the alternative collision strategy.

### 3. LRU Cache  -  Medium  (the canonical OOD interview problem)
- **Problem:** Design a cache with a fixed capacity supporting `get` and `put` in O(1); evict the least-recently-used key when full.
- **Practice (free):** https://leetcode.com/problems/lru-cache/
- **Video (free):** https://neetcode.io/problems/lru-cache
- **Idea (version A — `OrderedDict`):** An `OrderedDict` is exactly a hashmap+linked-list under the hood; `move_to_end` marks recency, `popitem(last=False)` evicts the oldest. Lead with this to show you know the stdlib — but be ready for them to ban it.
```python
from collections import OrderedDict

class LRUCacheOrdered:
    def __init__(self, capacity: int):
        self._cap = capacity
        self._d = OrderedDict()                      # insertion order == recency order

    def get(self, key: int) -> int:
        if key not in self._d:
            return -1
        self._d.move_to_end(key)                     # mark as most-recently-used
        return self._d[key]

    def put(self, key: int, value: int) -> None:
        if key in self._d:
            self._d.move_to_end(key)
        self._d[key] = value
        if len(self._d) > self._cap:
            self._d.popitem(last=False)              # evict the least-recently-used (front)
```
- **Idea (version B — hashmap + doubly-linked list, no `OrderedDict`):** Interviewers very often *ban* `OrderedDict` — the whole point is to see the structure. Hashmap maps key -> `Node`; a DLL with sentinels orders nodes by recency (front = most recent, back = LRU). `get`/`put` touch a node => move it to front; eviction = pop the back.
```python
class _Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self._cap = capacity
        self._map = {}                               # key -> _Node
        self._head, self._tail = _Node(), _Node()    # sentinels: front=MRU, back=LRU
        self._head.next, self._tail.prev = self._tail, self._head

    def _remove(self, node: "_Node") -> None:        # unlink any node in O(1)
        node.prev.next, node.next.prev = node.next, node.prev

    def _add_front(self, node: "_Node") -> None:     # insert right after head (MRU spot)
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: int) -> int:
        if key not in self._map:
            return -1
        node = self._map[key]
        self._remove(node)                           # touch => becomes most recent
        self._add_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self._map:                         # overwrite existing
            self._remove(self._map[key])
        node = _Node(key, value)
        self._map[key] = node
        self._add_front(node)
        if len(self._map) > self._cap:
            lru = self._tail.prev                    # node just before the tail sentinel
            self._remove(lru)
            del self._map[lru.key]                   # node stores its key => O(1) map cleanup
```
- **Complexity:** O(1) for both `get` and `put`; O(capacity) space.
- **Key insight / gotcha:** Store the **key inside the node**. On eviction you find the victim *via the list*, but you must also delete it from the *map* — without the key on the node you'd have no way to do that in O(1). And use sentinels: they make "remove the only node" and "list empty" just work.
- **Follow-up:** "Make it thread-safe." Wrap `get`/`put` in a `threading.Lock` (coarse lock) and discuss the contention trade-off; mention sharding the cache by key hash to reduce lock contention. "Add TTL." Store an expiry timestamp on the node and treat expired-on-read as a miss.

### 4. Insert Delete GetRandom O(1)  -  Medium
- **Problem:** Design a set supporting `insert`, `remove`, and `getRandom` (uniformly random element), each in O(1) average.
- **Practice (free):** https://leetcode.com/problems/insert-delete-getrandom-o1/
- **Video (free):** https://neetcode.io/problems/insert-delete-getrandom
- **Idea:** A dict alone can't do O(1) uniform random; an array alone can't do O(1) delete. Combine them: `vals` is a contiguous array (random index => O(1) random), `idx` maps value -> its position. To delete, **swap the victim with the last element**, fix the moved element's index, then `pop` the tail — no O(n) shift.
```python
import random

class RandomizedSet:
    def __init__(self):
        self._vals = []                              # contiguous => random.randrange is O(1)
        self._idx = {}                               # value -> index in _vals

    def insert(self, val: int) -> bool:
        if val in self._idx:
            return False
        self._idx[val] = len(self._vals)
        self._vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self._idx:
            return False
        i, last = self._idx[val], self._vals[-1]
        self._vals[i] = last                         # move last element into the hole
        self._idx[last] = i                          # fix its recorded index
        self._vals.pop()                             # drop the now-duplicated tail
        del self._idx[val]
        return True

    def getRandom(self) -> int:
        return self._vals[random.randrange(len(self._vals))]
```
- **Complexity:** O(1) average for all three; O(n) space.
- **Key insight / gotcha:** The swap-with-last is the whole trick — a plain `list.remove`/`pop(i)` is O(n) because it shifts everything after the hole. Also fix `_idx[last]` *before* popping, and handle the case where the victim *is* the last element (the swap is a no-op but the index fix is harmless).
- **Follow-up:** "Allow duplicates (GetRandom O(1) — Duplicates allowed)." Make `idx` map value -> a `set` of positions; swap-with-last still works, just remove/add positions in the sets. Keep `getRandom` uniform by index, not by value.

### 5. Design Browser History  -  Medium
- **Problem:** Implement browser history: `visit(url)` (clears forward history), `back(steps)`, `forward(steps)`, each clamped to bounds.
- **Practice (free):** https://leetcode.com/problems/design-browser-history/
- **Video (free):** https://www.youtube.com/results?search_query=design+browser+history+leetcode
- **Idea:** An array plus a `cur` cursor is cleanest. `visit` truncates everything after `cur` (forward stack is gone), appends, advances. `back`/`forward` just clamp the cursor — no copying. (Two stacks also works but the array+cursor reads cleaner and makes `visit`'s truncation O(1) in intent.)
```python
class BrowserHistory:
    def __init__(self, homepage: str):
        self._hist = [homepage]
        self._cur = 0                                # index of the currently-shown page

    def visit(self, url: str) -> None:
        del self._hist[self._cur + 1:]               # visiting kills all forward history
        self._hist.append(url)
        self._cur += 1

    def back(self, steps: int) -> str:
        self._cur = max(0, self._cur - steps)        # clamp at the oldest page
        return self._hist[self._cur]

    def forward(self, steps: int) -> str:
        self._cur = min(len(self._hist) - 1, self._cur + steps)   # clamp at the newest
        return self._hist[self._cur]
```
- **Complexity:** `visit` O(k) to drop k forward entries (O(1) amortised if you instead keep a logical length pointer), `back`/`forward` O(1); O(n) space.
- **Key insight / gotcha:** `visit` must **discard forward history** — that's the one rule people miss. The cursor model makes it a slice deletion; the two-stack model makes it "clear the forward stack".
- **Follow-up:** "Avoid reallocating on every visit." Keep a separate `length` field and overwrite in place instead of truncating, advancing/shrinking `length` logically — turns `visit` into O(1).

### 6. Min Stack via two-stacks vs single-stack  -  (variant drill, see #1)
- **Problem:** Same as Min Stack, but the interviewer asks for a *single*-stack solution to save space.
- **Practice (free):** https://leetcode.com/problems/min-stack/  (same problem, different constraint)
- **Video (free):** https://neetcode.io/problems/minimum-stack
- **Idea:** Push `(value, current_min)` tuples, or push the running min only when it changes. Shown here because Atlassian-style follow-ups love "now do it with less memory" on a structure you just built.
```python
class MinStackPairs:
    def __init__(self):
        self._stack = []                             # each entry: (value, min_so_far)

    def push(self, val: int) -> None:
        cur_min = val if not self._stack else min(val, self._stack[-1][1])
        self._stack.append((val, cur_min))

    def pop(self) -> None:
        self._stack.pop()

    def top(self) -> int:
        return self._stack[-1][0]

    def getMin(self) -> int:
        return self._stack[-1][1]
```
- **Complexity:** All O(1); O(n) space (one tuple per element).
- **Key insight / gotcha:** Bundling `(val, min)` keeps the min correct through interleaved push/pop automatically — no separate alignment to maintain.
- **Follow-up:** "getMax too?" Track a second running max in the tuple, same pattern.

### 7. Flatten Nested List Iterator  -  Medium
- **Problem:** Given a nested list of integers (each element is either an int or another nested list), implement an iterator (`next`, `hasNext`) that flattens it.
- **Practice (free):** https://leetcode.com/problems/flatten-nested-list-iterator/
- **Video (free):** https://neetcode.io/problems/flatten-nested-list-iterator
- **Idea (lazy, stack-based):** Push the list onto a stack in *reverse* so the first element is on top. On `hasNext`, peel lists open lazily — pop a list and push its children (reversed) until the top is an integer. Lazy beats eager flattening when the structure is huge or you may stop early.
```python
# The NestedInteger interface (given by LeetCode); stubbed here so the file runs standalone.
class NestedInteger:
    def __init__(self, value=None):
        self._int = value if isinstance(value, int) else None
        self._list = value if isinstance(value, list) else []
    def isInteger(self): return self._int is not None
    def getInteger(self): return self._int
    def getList(self): return self._list

class NestedIterator:
    def __init__(self, nestedList):
        self._stack = list(reversed(nestedList))     # top of stack = next item to inspect

    def hasNext(self) -> bool:
        while self._stack:                           # expand lists until top is an integer
            top = self._stack[-1]
            if top.isInteger():
                return True
            self._stack.pop()                        # it's a list: replace with its children
            self._stack.extend(reversed(top.getList()))
        return False

    def next(self) -> int:
        # contract: callers invoke hasNext() first, so the top is guaranteed an integer
        return self._stack.pop().getInteger()
```
- **Complexity:** O(1) amortised per `next`/`hasNext`; O(n + d) space (n top-level items + nesting depth d on the stack).
- **Key insight / gotcha:** Push children **reversed** so left-to-right order is preserved when popping. Do the flattening work inside `hasNext` (not `next`) — that's the lazy-evaluation contract iterators expect.
- **Follow-up:** "Eager version?" Recursively flatten into a flat list in the constructor and iterate with one index — simpler code, O(n) upfront space/time, but no early-exit savings.

### 8. Peeking Iterator  -  Medium
- **Problem:** Wrap an existing iterator so it also supports `peek()` (look at the next element without advancing), plus `next` and `hasNext`.
- **Practice (free):** https://leetcode.com/problems/peeking-iterator/
- **Video (free):** https://www.youtube.com/results?search_query=peeking+iterator+leetcode
- **Idea:** Buffer one element. Pull the next value eagerly into `_peeked`; `peek` returns the buffer, `next` returns it then refills, `hasNext` is true if the buffer is full or the underlying iterator has more. This "one-element lookahead" is the classic decorator pattern over an iterator.
```python
class PeekingIterator:
    def __init__(self, iterator):
        self._it = iterator
        self._buf = None                             # the buffered (peeked) value
        self._has = iterator.hasNext()
        if self._has:
            self._buf = self._it.next()              # pre-load one element

    def peek(self):
        return self._buf                             # look without consuming

    def next(self):
        val = self._buf
        self._has = self._it.hasNext()               # refill the buffer for next time
        self._buf = self._it.next() if self._has else None
        return val

    def hasNext(self) -> bool:
        return self._has
```
- **Complexity:** O(1) for `peek`, `next`, `hasNext`; O(1) extra space (single buffer).
- **Key insight / gotcha:** The lookahead is eager — you fetch the next element *before* it's asked for, so `hasNext` must reflect the *buffer's* state, not the underlying iterator's. Decorating without consuming is the trap; the buffer resolves it.
- **Follow-up:** "Arbitrary k-lookahead?" Buffer a deque of k pre-fetched elements; `peek(i)` indexes into it, `next` pops the front and refills the back.

### 9. Snapshot Array  -  Medium
- **Problem:** An array of given length supporting `set(index, val)`, `snap()` (take a snapshot, return its id), and `get(index, snap_id)` (value at that index when the snapshot was taken).
- **Practice (free):** https://leetcode.com/problems/snapshot-array/
- **Video (free):** https://www.youtube.com/results?search_query=snapshot+array+leetcode
- **Idea:** Don't copy the whole array on every `snap` (O(n) per snap is the trap). Per index, store a **list of `(snap_id, value)` records** and only append when the value changes. `get` binary-searches that index's history for the largest snap_id <= the queried one.
```python
import bisect

class SnapshotArray:
    def __init__(self, length: int):
        self._snap_id = 0
        self._hist = [[(0, 0)] for _ in range(length)]   # per index: sorted [(snap_id, val)]

    def set(self, index: int, val: int) -> None:
        records = self._hist[index]
        if records[-1][0] == self._snap_id:          # already wrote in this snap window
            records[-1] = (self._snap_id, val)       # overwrite, don't append a dup snap_id
        else:
            records.append((self._snap_id, val))

    def snap(self) -> int:
        self._snap_id += 1                           # O(1): just bump the counter
        return self._snap_id - 1

    def get(self, index: int, snap_id: int) -> int:
        records = self._hist[index]
        i = bisect.bisect_right(records, (snap_id, float("inf")))   # first record AFTER snap_id
        return records[i - 1][1]                      # so i-1 is the latest record <= snap_id
```
- **Complexity:** `set` O(1) amortised, `snap` O(1), `get` O(log m) where m = writes at that index; space O(total writes), not O(length × snaps).
- **Key insight / gotcha:** `snap` must be O(1) — incrementing a counter, *not* deep-copying. The records per index stay naturally sorted by snap_id (you only ever append), which is exactly what lets `get` binary-search.
- **Follow-up:** "Many indices, few writes — wasteful base records?" Lazily create the `(0, 0)` record only on first write; or store a single dict per index keyed by snap_id with a sorted key list.

### 10. LFU Cache  -  Hard
- **Problem:** Design a cache with capacity supporting O(1) `get` and `put`; evict the **least-frequently-used** key, breaking ties by least-recently-used.
- **Practice (free):** https://leetcode.com/problems/lfu-cache/
- **Video (free):** https://neetcode.io/problems/lfu-cache
- **Idea:** Three structures. `key -> Node` (value + its frequency). `freq -> OrderedDict of keys` at that frequency (insertion order gives the LRU tiebreak for free). A `min_freq` counter so eviction is O(1). On access, move the key from its `freq` bucket to the `freq+1` bucket; if you just emptied the `min_freq` bucket, bump `min_freq`.
```python
from collections import OrderedDict, defaultdict

class LFUCache:
    def __init__(self, capacity: int):
        self._cap = capacity
        self._key_to = {}                            # key -> (value, freq)
        self._buckets = defaultdict(OrderedDict)     # freq -> OrderedDict{key: None}, oldest first
        self._min_freq = 0

    def _bump(self, key: int) -> int:                # move key to the next-higher freq bucket
        val, freq = self._key_to[key]
        del self._buckets[freq][key]
        if not self._buckets[freq]:                  # bucket emptied
            del self._buckets[freq]
            if self._min_freq == freq:               # we just removed the rarest tier
                self._min_freq += 1
        self._buckets[freq + 1][key] = None          # appended => most-recent at this new freq
        self._key_to[key] = (val, freq + 1)
        return val

    def get(self, key: int) -> int:
        if key not in self._key_to:
            return -1
        return self._bump(key)

    def put(self, key: int, value: int) -> None:
        if self._cap <= 0:
            return
        if key in self._key_to:
            self._bump(key)
            v, f = self._key_to[key]
            self._key_to[key] = (value, f)           # update value, freq already bumped
            return
        if len(self._key_to) >= self._cap:           # evict LFU (then LRU within it)
            evict_key, _ = self._buckets[self._min_freq].popitem(last=False)  # oldest at min freq
            del self._key_to[evict_key]
            if not self._buckets[self._min_freq]:
                del self._buckets[self._min_freq]
        self._key_to[key] = (value, 1)               # new keys start at freq 1
        self._buckets[1][key] = None
        self._min_freq = 1                           # a brand-new key resets min freq to 1
```
- **Complexity:** O(1) for `get` and `put`; O(capacity) space.
- **Key insight / gotcha:** The two hard parts are (1) maintaining `min_freq` — it only ever *increases* on a `get`/`bump` (when the min bucket empties) and *resets to 1* whenever a new key is inserted; and (2) using an `OrderedDict` per frequency so the LRU tiebreak is automatic (`popitem(last=False)` = oldest). New keys reset `min_freq` to 1 *after* any eviction.
- **Follow-up:** "Why not one global frequency-sorted structure?" A heap gives O(log n), not O(1); the per-frequency bucket list is what makes both operations strictly O(1).

### 11. Design Twitter  -  Medium/Hard  (heap merge of feeds)
- **Problem:** Design Twitter: `postTweet`, `getNewsFeed` (10 most recent tweets from the user and those they follow), `follow`, `unfollow`.
- **Practice (free):** https://leetcode.com/problems/design-twitter/
- **Video (free):** https://neetcode.io/problems/design-twitter
- **Idea:** A global monotonic `time` stamps every tweet for ordering. Per user keep a list of `(time, tweet_id)` and a set of followees. `getNewsFeed` is a **k-way merge** of the relevant users' recent tweets — push each followee's latest tweet into a max-heap, pop the newest, then push that user's *next* tweet, 10 times. This is merge-k-sorted-lists wearing a product hat.
```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self._time = 0
        self._tweets = defaultdict(list)             # user_id -> list of (time, tweet_id)
        self._following = defaultdict(set)           # user_id -> set of followee ids

    def postTweet(self, userId: int, tweetId: int) -> None:
        self._tweets[userId].append((self._time, tweetId))
        self._time += 1                              # global clock => total order across users

    def getNewsFeed(self, userId: int) -> list:
        heap = []                                    # max-heap via negated time
        users = self._following[userId] | {userId}   # own tweets + followees'
        for uid in users:
            tw = self._tweets[uid]
            if tw:
                i = len(tw) - 1                      # index of this user's most recent tweet
                t, tid = tw[i]
                heapq.heappush(heap, (-t, tid, uid, i))
        feed = []
        while heap and len(feed) < 10:
            neg_t, tid, uid, i = heapq.heappop(heap)
            feed.append(tid)
            if i > 0:                                # pull this user's next-most-recent tweet
                t2, tid2 = self._tweets[uid][i - 1]
                heapq.heappush(heap, (-t2, tid2, uid, i - 1))
        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        self._following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self._following[followerId].discard(followeeId)   # discard => no error if absent
```
- **Complexity:** `postTweet`/`follow`/`unfollow` O(1); `getNewsFeed` O(f log f + 10 log f) where f = followees with tweets (heap of size f, at most 10 pops). Space O(users + tweets).
- **Key insight / gotcha:** The heap holds **one tweet per user at a time** (size = #followees), not every tweet — that's the merge-k-lists efficiency. Carry the per-user index in the heap entry so you can lazily fetch each user's next tweet only when needed. A global clock (not per-user counters) gives a consistent cross-user ordering.
- **Follow-up:** "Cap memory per user." Keep only the last N tweets per user (a bounded deque). "Hot users with millions of followers (fan-out)?" Discuss pull (compute feed on read, as above) vs push (write into followers' feeds on post) and the hybrid most real systems use.

## OOD discussion problems (talk + sketch, not full code)
These come up in the *design-leaning* slot of a coding loop (and in Amazon/Atlassian "design a system, small scope" rounds). They don't want a working algorithm — they want **clean entities, clear responsibilities, enums for fixed states, and you driving the conversation**. Sketch the class boxes, state the key methods, then narrate trade-offs.

### A. Design a Parking Lot
- **Practice / reference (free):** https://www.youtube.com/results?search_query=design+parking+lot+low+level+design ; write-up: https://github.com/donnemartin/system-design-primer (OOD section).
- **Drive the conversation:** start by pinning scope — "Multiple levels? Multiple vehicle sizes? Do we issue tickets and charge by time? Single entrance or many?" Lock the requirements, then design the nouns.
- **Entities & responsibilities (one class, one job):**
  - `ParkingLot` — owns the levels; top-level API `park(vehicle) -> Ticket | None`, `unpark(ticket) -> fee`. Delegates spot-finding to levels.
  - `Level` (or `Floor`) — holds its `ParkingSpot`s; knows its own availability counts per spot type; `find_spot(vehicle_size)`.
  - `ParkingSpot` — one stall: `spot_id`, `size`, `is_free`, `assign(vehicle)`, `vacate()`.
  - `Vehicle` (base) -> `Car`, `Motorcycle`, `Truck` subclasses, each carrying a `VehicleSize`.
  - `Ticket` — issued on entry: `ticket_id`, `spot`, `entry_time`; basis for the fee.
  - `FeeStrategy` (interface) — `compute(entry, exit) -> amount`; swap flat vs hourly vs tiered without touching `ParkingLot` (Strategy pattern — call this out).
- **Enums:** `VehicleSize {MOTORCYCLE, COMPACT, LARGE}`, `SpotType {MOTORCYCLE, COMPACT, LARGE}`, `TicketStatus {ACTIVE, PAID}`.
- **Key methods to name:** `ParkingLot.park`, `Level.find_spot`, `ParkingSpot.can_fit(size)`, `FeeStrategy.compute`.
- **Trade-offs to narrate:** how to find a free spot fast — a per-size **queue/heap of free spots per level** gives O(1) assignment vs scanning all stalls; whether a large vehicle may occupy a small spot (no) but a small one a large spot (allowed, with a policy flag); concurrency — two cars racing for the last spot needs a lock or atomic decrement. Mention the **Strategy pattern** for pricing and **Factory** for vehicle creation as the bits that show design maturity.

### B. Design Tic-Tac-Toe
- **Practice (free):** https://leetcode.com/problems/design-tic-tac-toe/ (Premium-locked) — **free alternative:** code it from the description below; video: https://www.youtube.com/results?search_query=design+tic+tac+toe+leetcode .
- **Drive the conversation:** the senior move is the **O(1)-per-move win check**. State it up front: "I won't rescan the board each move — I'll keep running tallies per row, column, and the two diagonals."
- **Entities & responsibilities:**
  - `TicTacToe` — owns the board state and the running tallies; `move(row, col, player) -> winner_or_0`.
  - `Player` enum and a `Board`/grid (for an n×n generalisation, the tallies matter more than the grid).
  - For a fuller game: `Game` (orchestrates turns), `Player`, `Move`, `GameStatus`.
- **Enums:** `Mark {EMPTY, X, O}`, `GameStatus {IN_PROGRESS, X_WON, O_WON, DRAW}`.
- **The O(1) trick (state it, optionally sketch):** keep `rows[n]`, `cols[n]`, and two scalars `diag`, `anti_diag`. Map player X to +1 and O to -1; on each move add the player's value to that move's row, col, and (if on a diagonal) the diagonals. If any tally hits `+n` or `-n`, that player just won — checked in O(1), no board scan.
```python
class TicTacToe:
    def __init__(self, n: int):
        self._n = n
        self._rows = [0] * n
        self._cols = [0] * n
        self._diag = 0
        self._anti = 0

    def move(self, row: int, col: int, player: int) -> int:
        delta = 1 if player == 1 else -1
        self._rows[row] += delta
        self._cols[col] += delta
        if row == col:
            self._diag += delta
        if row + col == self._n - 1:
            self._anti += delta
        if abs(self._rows[row]) == self._n or abs(self._cols[col]) == self._n \
           or abs(self._diag) == self._n or abs(self._anti) == self._n:
            return player                            # this move completed a line
        return 0                                     # no winner yet
```
- **Trade-offs to narrate:** O(1) per move vs O(n) rescan; generalising to n×n (and even "k-in-a-row" / Connect-style, where running tallies no longer suffice and you'd scan neighbourhoods of the last move); separating game *rules* from game *state* so you could swap in an AI player; how you'd detect a draw (a `moves_made` counter reaching n²).

## Atlassian-style tips (read this before the round)
- **Start with the simplest correct version, get it running, *then* extend.** Atlassian explicitly grades "can you build incrementally". For LRU: ship the `OrderedDict` version first and say "this works and is O(1); if you want me to show the underlying structure, I'll build the hashmap + doubly-linked list." Don't gold-plate before it runs.
- **They will add requirements mid-round** ("now make `get` also bump frequency", "now add TTL", "now make it thread-safe"). Design so the new requirement is a *small extension*, not a rewrite — that's exactly why the two-layer (public API over private helpers) structure pays off.
- **Narrate the data-structure trade-off out loud.** "I want O(1) eviction of the oldest *and* O(1) lookup, so I need an ordered structure I can delete from the middle of in O(1) — that's a doubly-linked list — paired with a hashmap for the lookup. A plain list would make eviction O(n)." Saying *why* the combo is what they're scoring.
- **Lead with the API and invariants.** Write the method signatures and one-line docstrings first; state the invariant ("the DLL is always ordered most-recent-first; the map and list always hold the same key set"). Then fill bodies. It keeps you (and them) oriented.
- **Use sentinels and small helper methods.** `_add_front`/`_remove`/`_move_to_front` with dummy head/tail nodes eliminate the edge cases that eat your time under pressure. Clean helpers also let you *talk* while your hands are busy.
- **Name your patterns when they apply** — Strategy (pricing), Factory (object creation), Decorator (peeking iterator), Iterator. Saying the name signals you've designed before; don't force one where it doesn't fit.
- **Test as you go.** A quick `if __name__ == "__main__":` driver that exercises the named operations catches the off-by-one in eviction before the interviewer does.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s ("design a ..." + a method list + a Big-O contract)
- [ ] I can map a complexity contract to its data-structure combo (O(1) get+evict => hashmap + DLL; O(1) insert/delete/random => array + hashmap)
- [ ] I can write the sentinel doubly-linked-list helpers from memory
- [ ] I can build LRU *without* `OrderedDict` from scratch
- [ ] I can drive a parking-lot / tic-tac-toe discussion (entities, enums, trade-offs) without writing full code
- [ ] Min Stack — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Design HashMap — 🔴 / 🟡 / 🟢
- [ ] LRU Cache (OrderedDict) — 🔴 / 🟡 / 🟢
- [ ] LRU Cache (from scratch) — 🔴 / 🟡 / 🟢
- [ ] Insert Delete GetRandom O(1) — 🔴 / 🟡 / 🟢
- [ ] Design Browser History — 🔴 / 🟡 / 🟢
- [ ] Flatten Nested List Iterator — 🔴 / 🟡 / 🟢
- [ ] Peeking Iterator — 🔴 / 🟡 / 🟢
- [ ] Snapshot Array — 🔴 / 🟡 / 🟢
- [ ] LFU Cache — 🔴 / 🟡 / 🟢
- [ ] Design Twitter — 🔴 / 🟡 / 🟢
- [ ] Design Parking Lot (discussion) — 🔴 / 🟡 / 🟢
- [ ] Design Tic-Tac-Toe (discussion + O(1) win check) — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (the "design" problems are scattered through Linked List / Heap / Stack sections) — https://neetcode.io/roadmap ; LeetCode "Design" tag — https://leetcode.com/problemset/?topicSlugs=design ; System Design Primer OOD section (parking lot, etc.) — https://github.com/donnemartin/system-design-primer ; Grokking-style LLD breakdowns on YouTube — https://www.youtube.com/results?search_query=low+level+design+interview+parking+lot+lru .
- **Paid (optional):** DesignGurus "Grokking the Low Level Design Interview" — https://www.designgurus.io (free alternative: the System Design Primer OOD section plus the NeetCode design problems above cover the same ground); "Head First Design Patterns" for Strategy/Factory/Decorator/Observer (free alternative: refactoring.guru's design-patterns catalogue — https://refactoring.guru/design-patterns ).

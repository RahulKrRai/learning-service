# 08 - Heap / Top-K / Merge-K
> One-line: reach for a heap whenever you need the "k best", a running min/max, or to repeatedly merge ordered streams without sorting everything.

## When to use it (recognition triggers)
- The problem asks for the **k-th largest/smallest**, **top-k**, or **k closest/most frequent** — but you do NOT need the full sorted order.
- You need a **running** min or max that updates as elements stream in (medians, schedulers, "process the largest remaining").
- You must **merge several already-sorted** lists/arrays/streams into one order.
- You see "at most k", "closest k", "k frequent", or "repeatedly take the largest/smallest and put something back".
- The naive answer is "sort everything (O(n log n))" but n is huge and k is small, or the data arrives online so you can't sort once.

## Mental model
- A binary heap is a complete tree giving O(1) peek at the extreme element and O(log n) push/pop. Python's `heapq` is a **min-heap**: `heap[0]` is the smallest.
- **Top-k trick:** to keep the k *largest*, maintain a min-heap of size k. The smallest of your k best sits at the top; when a bigger element arrives, pop the top and push the new one. This is O(n log k), beating a full sort when k << n.
- For a **max-heap** in Python, push negated values (`-x`) or wrap items in a comparable tuple. Pop and negate back.
- **Two-heaps** splits a stream into a low half (max-heap) and high half (min-heap) so the median is always at one or both tops — each insert is O(log n) and median is O(1).
- **Merge-k** seeds the heap with the head of every list, then repeatedly pops the global minimum and pushes that list's next element: O(N log k) for N total items across k lists.

## Reusable template(s)
```python
import heapq

# --- Top-k LARGEST: min-heap of size k ---
def top_k_largest(nums, k):
    heap = []                      # min-heap; heap[0] is the smallest of the k kept
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)    # evict the smallest -> only k largest survive
    return heap                    # heap[0] == k-th largest overall

# --- Max-heap via negation ---
def max_heap_demo(nums):
    heap = [-x for x in nums]
    heapq.heapify(heap)            # O(n)
    largest = -heapq.heappop(heap) # negate back on the way out
    return largest

# --- Merge-k sorted lists/arrays (heap of (value, list_idx, elem_idx)) ---
def merge_k(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out

# --- Two heaps for a streaming median ---
class MedianKeeper:
    def __init__(self):
        self.low = []   # max-heap (store negatives): smaller half
        self.high = []  # min-heap: larger half
    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))   # balance values
        if len(self.high) > len(self.low):                    # balance sizes
            heapq.heappush(self.low, -heapq.heappop(self.high))
    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

## Complexity profile
- Build heap: O(n) with `heapify`; push/pop: O(log n) each; peek: O(1).
- Top-k with a size-k heap: **O(n log k)** time, **O(k)** space — beats O(n log n) full sort.
- Merge-k of N total elements across k lists: **O(N log k)** time, **O(k)** heap space — beats O(N log N) concatenate-then-sort.
- Two-heaps median: **O(log n)** per insert, **O(1)** per query.

## Curated problems (easy -> hard)

### 1. Kth Largest Element in an Array  -  Medium
- **Problem:** Given an integer array `nums` and an integer `k`, return the k-th largest element (k-th in sorted-descending order, not the k-th distinct).
- **Practice (free):** https://leetcode.com/problems/kth-largest-element-in-an-array/
- **Video (free):** https://neetcode.io/problems/kth-largest-element-in-an-array
- **Idea:** Keep a min-heap of size k while scanning; the heap's top is always the k-th largest seen so far. (Quickselect is the O(n)-average alternative.)
```python
import heapq
from typing import List

def findKthLargest(nums: List[int], k: int) -> int:
    heap = []                      # min-heap holding the k largest so far
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)    # drop the smallest, keep k largest
    return heap[0]                 # smallest of the k largest = k-th largest
```
- **Complexity:** Time O(n log k), Space O(k)
- **Key insight / gotcha:** For the k-th *largest* you keep a *min*-heap (so you can cheaply evict the smallest of your kept set). Mixing this up is the classic mistake. `heapq.nlargest(k, nums)[-1]` works too but is less explicit.
- **Follow-up:** "Can you do it in O(n) average?" Use Quickselect (partition around a random pivot, recurse into the side containing index `n-k`); worst case O(n^2), avoided with random pivots / median-of-medians.

### 2. Last Stone Weight  -  Easy
- **Problem:** Repeatedly take the two heaviest stones and smash them; if unequal, the difference returns to the pile. Return the weight of the last remaining stone (or 0).
- **Practice (free):** https://leetcode.com/problems/last-stone-weight/
- **Video (free):** https://neetcode.io/problems/last-stone-weight
- **Idea:** A max-heap lets you pull the two largest in O(log n) each; push the difference back and repeat.
```python
import heapq
from typing import List

def lastStoneWeight(stones: List[int]) -> int:
    heap = [-s for s in stones]    # negate for a max-heap
    heapq.heapify(heap)
    while len(heap) > 1:
        a = -heapq.heappop(heap)   # heaviest
        b = -heapq.heappop(heap)   # second heaviest (a >= b)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return -heap[0] if heap else 0
```
- **Complexity:** Time O(n log n), Space O(n)
- **Key insight / gotcha:** Negate on the way in AND on the way out; forgetting one flips your comparisons silently. When `a == b` both stones vanish, so push nothing.
- **Follow-up:** "What if you smash the two *lightest* instead?" Use a plain min-heap (no negation) — the heap structure stays identical, only the sign convention changes.

### 3. K Closest Points to Origin  -  Medium
- **Problem:** Given points on a plane and an integer k, return the k points closest to the origin (Euclidean distance).
- **Practice (free):** https://leetcode.com/problems/k-closest-points-to-origin/
- **Video (free):** https://neetcode.io/problems/k-closest-points-to-origin
- **Idea:** Keep a max-heap of size k keyed on squared distance; when full, evict the farthest if a closer point appears. Compare squared distances — no `sqrt` needed.
```python
import heapq
from typing import List

def kClosest(points: List[List[int]], k: int) -> List[List[int]]:
    heap = []                              # max-heap of size k via negated distance
    for x, y in points:
        d = x * x + y * y                  # squared distance; monotonic, sqrt-free
        heapq.heappush(heap, (-d, x, y))
        if len(heap) > k:
            heapq.heappop(heap)            # evict the current farthest
    return [[x, y] for _, x, y in heap]
```
- **Complexity:** Time O(n log k), Space O(k)
- **Key insight / gotcha:** Use a *max*-heap of size k (largest distance on top) so you can discard the farthest in O(log k). Comparing `x*x + y*y` avoids floating-point and is faster.
- **Follow-up:** "k is close to n — anything better?" Quickselect partitions on distance for O(n) average and returns the k closest without ordering them.

### 4. Top K Frequent Elements  -  Medium
- **Problem:** Given an array `nums` and integer k, return the k most frequent elements (any order).
- **Practice (free):** https://leetcode.com/problems/top-k-frequent-elements/
- **Video (free):** https://neetcode.io/problems/top-k-frequent-elements
- **Idea:** Count frequencies, then keep a size-k min-heap keyed on frequency. (Bucket sort by frequency gives a clean O(n) alternative.)
```python
import heapq
from collections import Counter
from typing import List

def topKFrequent(nums: List[int], k: int) -> List[int]:
    freq = Counter(nums)
    heap = []                              # min-heap of (count, value), size k
    for val, cnt in freq.items():
        heapq.heappush(heap, (cnt, val))
        if len(heap) > k:
            heapq.heappop(heap)            # drop least frequent of the kept set
    return [val for _, val in heap]
```
- **Complexity:** Time O(m log k) where m = distinct values, Space O(m)
- **Key insight / gotcha:** Heap on (count, value); the size-k min-heap keeps the most frequent. For guaranteed O(n), bucket the values into an array indexed by frequency (0..n) and read buckets from the top.
- **Follow-up:** "True O(n)?" Bucket sort: `buckets[count].append(val)`, then walk `count` from high to low collecting k items — no log factor.

### 5. Task Scheduler  -  Medium
- **Problem:** Given CPU tasks (letters) and a cooldown `n` (same task must be `n` intervals apart), return the minimum number of intervals (including idles) to finish all tasks.
- **Practice (free):** https://leetcode.com/problems/task-scheduler/
- **Video (free):** https://neetcode.io/problems/task-scheduler
- **Idea:** Greedily run the most frequent available task each tick. A max-heap of remaining counts plus a cooldown queue of `(ready_time, count)` models this directly. (A closed-form math formula also exists.)
```python
import heapq
from collections import Counter, deque
from typing import List

def leastInterval(tasks: List[str], n: int) -> int:
    counts = Counter(tasks)
    heap = [-c for c in counts.values()]   # max-heap of remaining counts
    heapq.heapify(heap)
    cooldown = deque()                     # (count_remaining, time_ready_again)
    time = 0
    while heap or cooldown:
        time += 1
        if heap:
            cnt = heapq.heappop(heap) + 1  # ran one instance (cnt is negative)
            if cnt < 0:                    # still has copies left
                cooldown.append((cnt, time + n))
        if cooldown and cooldown[0][1] == time:
            heapq.heappush(heap, cooldown.popleft()[0])
    return time
```
- **Complexity:** Time O(T) ticks * O(log 26) ≈ O(T), Space O(26)
- **Key insight / gotcha:** Always run the task with the most remaining copies first; that minimizes future idles. The cooldown queue holds a task until exactly `time + n`, then returns it to the heap. (Counts are kept negative so `+1` moves them toward zero.)
- **Follow-up:** "O(1) without simulation?" Formula: `max(len(tasks), (maxFreq - 1) * (n + 1) + numTasksWithMaxFreq)`.

### 6. Design Twitter  -  Medium
- **Problem:** Design a mini-Twitter: `postTweet`, `getNewsFeed` (10 most recent tweets from the user and everyone they follow), `follow`, `unfollow`.
- **Practice (free):** https://leetcode.com/problems/design-twitter/
- **Video (free):** https://neetcode.io/problems/design-twitter
- **Idea:** Store each user's tweets as `(timestamp, id)`. For the feed, merge the relevant users' recent tweets with a max-heap on timestamp and pop the 10 newest — a bounded merge-k.
```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)        # user -> list of (time, tweetId)
        self.following = defaultdict(set)      # user -> set of followees

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> list:
        heap = []                              # max-heap on time (negate)
        users = self.following[userId] | {userId}
        for u in users:
            for t, tid in self.tweets[u][-10:]:   # only the last 10 per user matter
                heapq.heappush(heap, (-t, tid))
        feed = []
        while heap and len(feed) < 10:
            feed.append(heapq.heappop(heap)[1])
        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.following[followerId].discard(followeeId)
```
- **Complexity:** `getNewsFeed` O(F log F) with F followees (capped at 10 tweets each); other ops O(1).
- **Key insight / gotcha:** A global incrementing `time` gives a total order across users, so the heap can merge feeds correctly. Slicing `[-10:]` bounds work — you never need older tweets for a 10-item feed. Always include the user's own tweets (`| {userId}`).
- **Follow-up:** "Millions of followers (the celebrity / fan-out problem)?" Don't fan-out on write for huge accounts; pull their tweets at read time and merge with the precomputed feed — exactly the hybrid Twitter uses in production.

### 7. Find Median from Data Stream  -  Hard
- **Problem:** Support `addNum(x)` for a stream of integers and `findMedian()` returning the median of all numbers seen so far, both efficiently.
- **Practice (free):** https://leetcode.com/problems/find-median-from-data-stream/
- **Video (free):** https://neetcode.io/problems/find-median-from-data-stream
- **Idea:** Keep two heaps: a max-heap `low` for the smaller half and a min-heap `high` for the larger half, balanced so their tops straddle the median.
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []    # max-heap (negated): smaller half
        self.high = []   # min-heap: larger half

    def addNum(self, num: int) -> None:
        heapq.heappush(self.low, -num)
        # move low's largest into high to enforce low_max <= high_min
        heapq.heappush(self.high, -heapq.heappop(self.low))
        # keep low the same size or one larger than high
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self) -> float:
        if len(self.low) > len(self.high):
            return -self.low[0]               # odd total -> low holds the middle
        return (-self.low[0] + self.high[0]) / 2.0
```
- **Complexity:** `addNum` O(log n), `findMedian` O(1), Space O(n)
- **Key insight / gotcha:** Two invariants must hold simultaneously: **value** (`max(low) <= min(high)`) and **size** (`len(low) - len(high) ∈ {0, 1}`). The push-to-low-then-shift-to-high dance enforces value ordering before you rebalance sizes.
- **Follow-up:** "99% of numbers are in [0,100]?" Use a counting array / bucketed histogram with a running count for O(1) median; for a fixed small range you don't even need heaps.

### 8. Merge k Sorted Lists  -  Hard
- **Problem:** Merge k sorted linked lists into one sorted linked list and return its head.
- **Practice (free):** https://leetcode.com/problems/merge-k-sorted-lists/
- **Video (free):** https://neetcode.io/problems/merge-k-sorted-lists
- **Idea:** Seed a min-heap with the head node of each list; repeatedly pop the smallest, append it to the result, and push that node's successor.
```python
import heapq
from typing import List, Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    heap = []
    # (value, tie_breaker_index, node) — index avoids comparing ListNode objects
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```
- **Complexity:** Time O(N log k), Space O(k) for N total nodes across k lists.
- **Key insight / gotcha:** Push a tie-breaker (the list index) BEFORE the node, because when two nodes share a value Python would otherwise try to compare `ListNode` objects and raise `TypeError`. The dummy head keeps append logic clean.
- **Follow-up:** "No heap allowed?" Divide-and-conquer: pairwise-merge lists (merge-sort style) in log k rounds — same O(N log k), O(1) extra space beyond recursion.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the size-k min-heap and max-heap-via-negation templates from memory
- [ ] I can write the two-heaps median balance from memory
- [ ] 1. Kth Largest Element  🔴/🟡/🟢
- [ ] 2. Last Stone Weight  🔴/🟡/🟢
- [ ] 3. K Closest Points to Origin  🔴/🟡/🟢
- [ ] 4. Top K Frequent Elements  🔴/🟡/🟢
- [ ] 5. Task Scheduler  🔴/🟡/🟢
- [ ] 6. Design Twitter  🔴/🟡/🟢
- [ ] 7. Find Median from Data Stream  🔴/🟡/🟢
- [ ] 8. Merge k Sorted Lists  🔴/🟡/🟢

## Resources
- **Free:** NeetCode "Heap / Priority Queue" roadmap section — https://neetcode.io/roadmap ; Python `heapq` docs (heapify/nlargest/nsmallest) — https://docs.python.org/3/library/heapq.html ; LeetCode Heap explore card — https://leetcode.com/explore/learn/card/heap/
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" Top-K & Two-Heaps patterns — https://www.designgurus.io (free alternative: the NeetCode roadmap section above covers the same patterns with videos).

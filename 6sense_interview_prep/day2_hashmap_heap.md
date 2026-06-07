# Day 2 — HashMap, Sets, Heap, Sorting
**Target: 3–4 hours | Date: April 1**

---

## Part 1: HashMap Patterns (1.5 hours)

### Core Idea
HashMap gives O(1) average lookup/insert. Use it when you need:
- Frequency counting
- Seen/visited tracking
- Complement lookup (Two Sum)
- Index storage

---

### Problem 1: Two Sum (Unsorted)
```python
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
# Time: O(n), Space: O(n)
# Key insight: for each element, check if its complement was seen before
```

### Problem 2: Longest Consecutive Sequence
```python
def longest_consecutive(nums):
    num_set = set(nums)
    max_len = 0
    for num in num_set:
        if num - 1 not in num_set:  # only start from sequence beginning
            current = num
            length = 1
            while current + 1 in num_set:
                current += 1
                length += 1
            max_len = max(max_len, length)
    return max_len
# Time: O(n), Space: O(n)
# Key insight: only start counting from the smallest element of each sequence
```

### Problem 3: First Non-Repeating Character
```python
from collections import Counter

def first_uniq_char(s):
    count = Counter(s)
    for i, char in enumerate(s):
        if count[char] == 1:
            return i
    return -1
# Time: O(n), Space: O(1) — at most 26 keys
```

### Problem 4: 4Sum II (Count tuples summing to zero)
```python
def four_sum_count(A, B, C, D):
    ab_sums = {}
    for a in A:
        for b in B:
            ab_sums[a+b] = ab_sums.get(a+b, 0) + 1
    count = 0
    for c in C:
        for d in D:
            count += ab_sums.get(-(c+d), 0)
    return count
# Time: O(n^2), Space: O(n^2)
# Key insight: split 4 arrays into 2 pairs, use hashmap to count complements
```

### Problem 5: Subarray with Equal Number of 0s and 1s
```python
def find_max_length(nums):
    # Replace 0 with -1, then find longest subarray with sum 0
    prefix_sum = 0
    first_seen = {0: -1}
    max_len = 0
    for i, num in enumerate(nums):
        prefix_sum += 1 if num == 1 else -1
        if prefix_sum in first_seen:
            max_len = max(max_len, i - first_seen[prefix_sum])
        else:
            first_seen[prefix_sum] = i
    return max_len
# Time: O(n), Space: O(n)
```

### Problem 6: Count Distinct Elements in Every Window of Size K
```python
def count_distinct(nums, k):
    freq = {}
    result = []
    for i in range(len(nums)):
        freq[nums[i]] = freq.get(nums[i], 0) + 1
        if i >= k:
            old = nums[i - k]
            freq[old] -= 1
            if freq[old] == 0:
                del freq[old]
        if i >= k - 1:
            result.append(len(freq))
    return result
# Time: O(n), Space: O(k)
```

---

## Part 2: Heap / Priority Queue (1.5 hours)

### Core Idea
Python's `heapq` is a **min-heap** by default.
- For max-heap: negate values (`heapq.heappush(h, -val)`)
- `heapq.heappush(h, val)` — insert in O(log n)
- `heapq.heappop(h)` — remove min in O(log n)
- `h[0]` — peek min in O(1)

---

### Problem 7: Kth Largest Element in Array
```python
import heapq

def find_kth_largest(nums, k):
    # Maintain min-heap of size k
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]  # smallest of top k = kth largest
# Time: O(n log k), Space: O(k)

# Alternative: O(n) average with quickselect, but heap is safer in interviews
```

### Problem 8: Top K Frequent Elements
```python
from collections import Counter
import heapq

def top_k_frequent(nums, k):
    freq = Counter(nums)
    # Min-heap of (frequency, element) — keep top k by frequency
    heap = []
    for num, count in freq.items():
        heapq.heappush(heap, (count, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for count, num in heap]
# Time: O(n log k), Space: O(n)

# Bucket sort alternative: O(n)
def top_k_frequent_bucket(nums, k):
    freq = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, count in freq.items():
        buckets[count].append(num)
    result = []
    for i in range(len(buckets) - 1, -1, -1):
        result.extend(buckets[i])
        if len(result) >= k:
            return result[:k]
```

### Problem 9: K Closest Points to Origin
```python
def k_closest(points, k):
    # Max-heap of size k (negate distance to use min-heap as max-heap)
    heap = []
    for x, y in points:
        dist = x*x + y*y  # no need for sqrt
        heapq.heappush(heap, (-dist, x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return [[x, y] for _, x, y in heap]
# Time: O(n log k), Space: O(k)
```

### Problem 10: Merge K Sorted Lists
```python
from heapq import heappush, heappop

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heappush(heap, (node.val, i, node))  # (val, list_idx, node)

    dummy = ListNode()
    curr = dummy
    while heap:
        val, i, node = heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next
# Time: O(N log k) where N = total nodes, k = number of lists
```

### Problem 11: Find Median from Data Stream
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []  # max-heap (lower half) — negate values
        self.large = []  # min-heap (upper half)

    def addNum(self, num):
        heapq.heappush(self.small, -num)
        # Balance: max of small <= min of large
        if self.small and self.large and (-self.small[0]) > self.large[0]:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        # Balance sizes
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2.0
# Time: O(log n) per add, O(1) per median
# Key insight: two heaps — max-heap for lower half, min-heap for upper half
```

---

## Part 3: Sorting-Based Problems (30 min)

### Problem 12: Sort Colors (Dutch National Flag)
```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
# Time: O(n), Space: O(1) — single pass
```

### Problem 13: Meeting Rooms II (Min Rooms Needed)
```python
def min_meeting_rooms(intervals):
    if not intervals: return 0
    intervals.sort(key=lambda x: x[0])
    heap = []  # end times of ongoing meetings
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)  # reuse room
        else:
            heapq.heappush(heap, end)  # new room needed
    return len(heap)
# Time: O(n log n), Space: O(n)
```

---

## Day 2 Checklist
- [ ] HashMap: Two Sum, Longest Consecutive, Subarray Equal 0s 1s
- [ ] Heap: Kth Largest, Top K Frequent, K Closest Points
- [ ] Heap Advanced: Merge K Lists, Median from Stream
- [ ] Sorting: Dutch National Flag, Meeting Rooms II

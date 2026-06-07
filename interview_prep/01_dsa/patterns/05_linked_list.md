# 05 - Linked List
> One-line: reach for this when you must rewire `next` pointers in place, run two pointers at different speeds, or maintain ordering/structure that an array can't mutate cheaply at the head/middle.

## When to use it (recognition triggers)
- The input is given as a `ListNode` head (singly/doubly linked), and you're asked to reverse, merge, reorder, or detect structure.
- You need O(1) insert/delete at arbitrary positions, or O(1) splice — something arrays do in O(n).
- "Find the middle / nth-from-end / cycle / where the cycle begins" -> fast & slow pointers.
- "Do it in one pass" or "without extra space / O(1) space" -> in-place pointer surgery, not copying to an array.
- Order matters and you'll repeatedly merge sorted sequences (k lists) -> heap + linked list, or divide & conquer.
- An LRU/LFU-style cache where you must move/evict nodes in O(1) -> doubly linked list + hash map.

## Mental model
- A linked list is just a chain of nodes where each holds a value and a pointer to the next node. You never index into it; you walk it. The only thing you ever truly own is the `head`.
- Almost every hard bug is a lost pointer: before you overwrite `cur.next`, save it. The canonical reversal is "remember next, flip current's arrow backward, advance both."
- A **dummy/sentinel head** (`dummy = ListNode(0); dummy.next = head`) removes special-casing for the head when nodes get inserted or removed at the front. Return `dummy.next`.
- **Fast & slow pointers** (Floyd): slow moves 1, fast moves 2. Fast reaches the end when slow is at the middle; if there's a cycle they collide. To find the cycle's entry, reset one pointer to head and advance both by 1 — they meet at the entry (provable from the distance equations).
- For ordering across many lists, a min-heap of the current front nodes gives you the global minimum in O(log k) per pop, stitched onto a result chain.

## Reusable template(s)
```python
# Standard node definition used throughout.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# --- Template 1: in-place reversal ---
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next      # 1. save the next node
        cur.next = prev     # 2. flip the arrow backward
        prev = cur          # 3. advance prev
        cur = nxt           # 4. advance cur
    return prev             # prev is the new head

# --- Template 2: fast & slow (middle / cycle) ---
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow             # 2nd middle for even length

# --- Template 3: dummy head for safe insert/remove ---
def with_dummy(head):
    dummy = ListNode(0, head)
    # ... operate on dummy.next, splice freely ...
    return dummy.next
```

## Complexity profile
- Reverse / traverse / fast-slow: **Time O(n), Space O(1)**.
- Merge two sorted lists: **Time O(n+m), Space O(1)**.
- Merge k lists (heap): **Time O(N log k)** for N total nodes, **Space O(k)**.
- Copy with random pointer (interleave trick): **Time O(n), Space O(1)** extra (beats the O(n) hash-map version).
- The brute force you're beating: copying the list into an array to use indices (O(n) extra space), or repeatedly re-scanning to find a node (O(n²)).

## Curated problems (easy -> hard)

### 1. Reverse Linked List  -  Easy
- **Problem:** Given the head of a singly linked list, reverse it and return the new head.
- **Practice (free):** https://leetcode.com/problems/reverse-linked-list/
- **Video (free):** https://neetcode.io/problems/reverse-a-linked-list
- **Idea:** Walk the list flipping each node's `next` to point at the previous node; the last node you visit becomes the head.
```python
def reverseList(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next   # save before we clobber it
        cur.next = prev  # reverse the link
        prev = cur       # move prev forward
        cur = nxt        # move cur forward
    return prev          # new head
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** You must cache `cur.next` *before* reassigning it, or you lose the rest of the list. This is the muscle-memory move every other problem builds on.
- **Follow-up:** "Do it recursively." Recurse to the tail, then on the way back set `head.next.next = head; head.next = None`. O(n) stack space — mention the iterative version is preferred for long lists.

### 2. Merge Two Sorted Lists  -  Easy
- **Problem:** Merge two sorted linked lists into one sorted list by splicing nodes together; return its head.
- **Practice (free):** https://leetcode.com/problems/merge-two-sorted-lists/
- **Video (free):** https://neetcode.io/problems/merge-two-sorted-linked-lists
- **Idea:** Use a dummy head; repeatedly append the smaller of the two front nodes, then attach whatever list remains.
```python
def mergeTwoLists(l1, l2):
    dummy = tail = ListNode()
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 or l2   # attach the non-empty remainder
    return dummy.next
```
- **Complexity:** Time O(n+m), Space O(1)
- **Key insight / gotcha:** The dummy node lets you avoid a separate "which list is the initial head?" check. `tail.next = l1 or l2` cleanly attaches the leftover tail in one line.
- **Follow-up:** "Merge them stably / what about descending order?" Use `<=` (as above) to keep equal elements in l1-before-l2 order; flip the comparison for descending.

### 3. Linked List Cycle  -  Easy
- **Problem:** Determine whether a linked list has a cycle (some node's `next` points back into the list).
- **Practice (free):** https://leetcode.com/problems/linked-list-cycle/
- **Video (free):** https://neetcode.io/problems/linked-list-cycle
- **Idea:** Floyd's tortoise & hare — slow moves 1 step, fast moves 2; if they ever meet, there's a cycle.
```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:     # pointers collided -> cycle
            return True
    return False             # fast hit the end -> no cycle
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** The loop guard must check both `fast` and `fast.next` before the double hop, or you'll dereference `None`. The hash-set approach also works but uses O(n) space.
- **Follow-up:** "Return the node where the cycle begins." (Linked List Cycle II) After they meet, reset one pointer to `head` and advance both by 1; they meet at the cycle's entry.

### 4. Middle of the Linked List  -  Easy
- **Problem:** Return the middle node of a linked list; for even length return the second of the two middles.
- **Practice (free):** https://leetcode.com/problems/middle-of-the-linked-list/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+middle+of+the+linked+list
- **Idea:** Fast & slow pointers — when fast reaches the end, slow sits at the middle.
```python
def middleNode(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Starting both at `head` yields the *second* middle for even length. To get the *first* middle instead, start `fast = head.next`. Know which one the problem wants (Reorder List below needs the first middle).
- **Follow-up:** "Split the list into two halves." Walk to the middle, then sever with `mid.next = None` before processing the second half.

### 5. Remove Nth Node From End of List  -  Medium
- **Problem:** Remove the nth node counting from the end of the list and return the head, in one pass.
- **Practice (free):** https://leetcode.com/problems/remove-nth-node-from-end-of-list/
- **Video (free):** https://neetcode.io/problems/remove-node-from-end-of-linked-list
- **Idea:** Advance a `fast` pointer n nodes ahead, then move `fast` and `slow` together until `fast` hits the end; `slow` now sits just before the target.
```python
def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n):       # create an n-node gap
        fast = fast.next
    while fast.next:         # move both until fast is at the last node
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next   # unlink the nth-from-end
    return dummy.next
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Anchoring both pointers at `dummy` (not `head`) makes removing the head itself fall out naturally — no special case. The gap of n guarantees `slow` lands on the predecessor.
- **Follow-up:** "What if n can exceed the length?" Validate the input or guard the advance loop; in the standard problem n is guaranteed valid (1 ≤ n ≤ length).

### 6. Reorder List  -  Medium
- **Problem:** Reorder L0->L1->...->Ln to L0->Ln->L1->Ln-1->... in place, modifying node links (not values).
- **Practice (free):** https://leetcode.com/problems/reorder-list/
- **Video (free):** https://neetcode.io/problems/reorder-linked-list
- **Idea:** Three moves: find the (first) middle, reverse the second half, then merge the two halves alternately.
```python
def reorderList(head):
    if not head or not head.next:
        return
    # 1. find first middle (slow ends on first middle for even length)
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    # 2. reverse the second half
    second = slow.next
    slow.next = None         # cut the list in two
    prev = None
    while second:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt
    # 3. weave the two halves together
    first, second = head, prev
    while second:
        n1, n2 = first.next, second.next
        first.next = second
        second.next = n1
        first, second = n1, n2
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Cut the list (`slow.next = None`) before reversing, and merge driven by the *second* half being the shorter/equal one — that's why the weave loop conditions on `second`. Using `fast = head.next` gets the first middle so the front half is never shorter than the back.
- **Follow-up:** "Can you do it without reversing?" You could stack the second half (O(n) space) — but the reverse-and-merge approach is the expected O(1)-space answer.

### 7. Copy List with Random Pointer  -  Medium
- **Problem:** Deep-copy a list where each node has a `next` and a `random` pointer (which may point anywhere or be `None`).
- **Practice (free):** https://leetcode.com/problems/copy-list-with-random-pointer/
- **Video (free):** https://neetcode.io/problems/copy-linked-list-with-random-pointer
- **Idea (O(1) space):** Interleave each copy right after its original (A->A'->B->B'...), wire copies' `random` from originals' `random.next`, then unzip the two lists.
```python
class Node:
    def __init__(self, x, next=None, random=None):
        self.val = x
        self.next = next
        self.random = random

def copyRandomList(head):
    if not head:
        return None
    # 1. interleave clones: A -> A' -> B -> B' -> ...
    cur = head
    while cur:
        clone = Node(cur.val, cur.next)
        cur.next = clone
        cur = clone.next
    # 2. assign random pointers on the clones
    cur = head
    while cur:
        if cur.random:
            cur.next.random = cur.random.next
        cur = cur.next.next
    # 3. unzip into original and copied lists
    cur = head
    new_head = head.next
    while cur:
        clone = cur.next
        cur.next = clone.next
        clone.next = clone.next.next if clone.next else None
        cur = cur.next
    return new_head
```
- **Complexity:** Time O(n), Space O(1) extra
- **Key insight / gotcha:** The clone of a node sits at `original.next`, so a copy's random is exactly `original.random.next`. The simpler, very acceptable alternative is a `{original: clone}` hash map in two passes — O(n) space. Mention both; lead with the map version if short on time, then offer the interleave optimization.
- **Follow-up:** "What if the list is huge and memory-constrained?" The interleave method is the answer — no auxiliary structure proportional to n.

### 8. Add Two Numbers  -  Medium
- **Problem:** Two numbers are stored as linked lists with digits in reverse order, one digit per node; return their sum as a linked list.
- **Practice (free):** https://leetcode.com/problems/add-two-numbers/
- **Video (free):** https://neetcode.io/problems/add-two-numbers
- **Idea:** Walk both lists together adding digits plus a running carry, creating a new node per digit; don't forget a final carry node.
```python
def addTwoNumbers(l1, l2):
    dummy = tail = ListNode()
    carry = 0
    while l1 or l2 or carry:
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        carry, digit = divmod(v1 + v2 + carry, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next
```
- **Complexity:** Time O(max(n,m)), Space O(max(n,m)) for the result
- **Key insight / gotcha:** The `or carry` in the loop condition handles the case where the final addition overflows (e.g. 5+5 -> a leading 1). `divmod(total, 10)` gives carry and digit in one call.
- **Follow-up:** "What if digits are stored in forward order?" (Add Two Numbers II) Reverse both lists first, or push onto stacks and build the result from the front — discuss the trade-off of mutating input.

### 9. LRU Cache  -  Medium
- **Problem:** Design a cache with O(1) `get` and `put` that evicts the least-recently-used key when capacity is exceeded.
- **Practice (free):** https://leetcode.com/problems/lru-cache/
- **Video (free):** https://neetcode.io/problems/lru-cache
- **Idea:** Hash map from key -> node, plus a doubly linked list ordered by recency (most-recent near head, LRU near tail). Touching a key moves its node to the front; eviction pops the tail.
```python
class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}                 # key -> Node
        self.head, self.tail = Node(), Node()  # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _insert_front(self, node):      # right after head = most recent
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_front(node)        # mark as most recently used
        return node.val

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._insert_front(node)
        if len(self.cache) > self.cap:  # evict LRU (node before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```
- **Complexity:** Time O(1) per `get`/`put`, Space O(capacity)
- **Key insight / gotcha:** Store the `key` inside the node so eviction can delete from the hash map in O(1). Two sentinel nodes (head/tail) eliminate every null-check in `_remove`/`_insert_front`. Note: Python's `collections.OrderedDict` (with `move_to_end` and `popitem(last=False)`) solves this too — name it, but interviewers usually want the manual DLL build.
- **Follow-up:** "Now do LFU Cache." Maintain a frequency -> DLL map plus a min-frequency tracker; promote nodes between frequency buckets. Much fiddlier — flag it as a known hard escalation.

### 10. Merge k Sorted Lists  -  Hard
- **Problem:** Merge k sorted linked lists into one sorted list and return its head.
- **Practice (free):** https://leetcode.com/problems/merge-k-sorted-lists/
- **Video (free):** https://neetcode.io/problems/merge-k-sorted-linked-lists
- **Idea:** Push the head of each list into a min-heap; repeatedly pop the global minimum, append it, and push its successor. (Tie-break by an index so heapq never compares `ListNode`s.)
```python
import heapq

def mergeKLists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))  # i breaks val ties
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```
- **Complexity:** Time O(N log k) for N total nodes, Space O(k)
- **Key insight / gotcha:** The middle tuple element (the list index `i`) is essential — when two nodes have equal `val`, Python tries to compare the next tuple element; comparing `ListNode` objects raises a `TypeError`. The index makes ties resolvable without touching the nodes.
- **Follow-up:** "Without a heap?" Divide & conquer: pairwise-merge lists (problem #2) in log k rounds — same O(N log k) time, O(1) extra space (ignoring recursion). Often preferred when k is large but values are heavy to heap-compare.

### 11. Reverse Nodes in k-Group  -  Hard
- **Problem:** Reverse the nodes of the list k at a time; if the final group has fewer than k nodes, leave it as-is.
- **Practice (free):** https://leetcode.com/problems/reverse-nodes-in-k-group/
- **Video (free):** https://neetcode.io/problems/reverse-nodes-in-k-group
- **Idea:** For each block, first check k nodes exist; reverse exactly k links; then reconnect the previous block's tail to the new block head and the block's old head (now tail) to the rest.
```python
def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        # find the k-th node from group_prev; bail if fewer than k remain
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next
        # reverse the group [group_prev.next ... kth]
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        # reconnect: group_prev.next was the group's head, now its tail
        tail = group_prev.next
        group_prev.next = kth      # kth is the reversed group's head
        group_prev = tail          # advance to this group's (new) tail
    # unreachable; loop returns from inside
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** Reverse the group "into" `group_next` (initialize `prev = group_next`) so the block's last node already points at the rest of the list — no extra fix-up. The `while cur is not group_next` bound stops exactly after k flips. Counting k nodes *before* reversing is what handles the "leftover < k" requirement.
- **Follow-up:** "Reverse the leftover tail too." Drop the early `return` guard: when fewer than k remain, reverse what's left anyway. Clarify the spec with the interviewer first.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the reversal and fast/slow templates from memory
- [ ] I can set up a dummy head without thinking about it
- [ ] Reverse Linked List 🔴/🟡/🟢
- [ ] Merge Two Sorted Lists 🔴/🟡/🟢
- [ ] Linked List Cycle (+ find entry) 🔴/🟡/🟢
- [ ] Middle of the Linked List 🔴/🟡/🟢
- [ ] Remove Nth Node From End 🔴/🟡/🟢
- [ ] Reorder List 🔴/🟡/🟢
- [ ] Copy List with Random Pointer 🔴/🟡/🟢
- [ ] Add Two Numbers 🔴/🟡/🟢
- [ ] LRU Cache (manual DLL) 🔴/🟡/🟢
- [ ] Merge k Sorted Lists 🔴/🟡/🟢
- [ ] Reverse Nodes in k-Group 🔴/🟡/🟢

## Resources
- **Free:** NeetCode roadmap, Linked List section — https://neetcode.io/roadmap ; LeetCode "Linked List" Explore card — https://leetcode.com/explore/learn/card/linked-list/ ; takeUforward/Striver linked-list playlist — https://www.youtube.com/results?search_query=striver+linked+list+playlist
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Fast & Slow Pointers + In-place Reversal modules) — https://www.designgurus.io  *(free alternative: the NeetCode roadmap sections above cover the same patterns)*.

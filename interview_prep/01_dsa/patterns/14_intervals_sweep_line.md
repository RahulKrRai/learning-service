# 14 - Intervals & Sweep Line
> One-line: when you have a list of `[start, end]` ranges and need to merge, count overlaps, or find gaps — sort by an endpoint and sweep.

## When to use it (recognition triggers)
- Input is a list of pairs/ranges: `[start, end]`, intervals, time slots, `[x_start, x_end]`, bookings, meetings.
- You're asked to **merge** overlapping ranges, **count overlaps** at a point, find the **maximum concurrency** (e.g. rooms/CPUs needed), or **remove the fewest** intervals to make them disjoint.
- Phrases like "minimum number of X to cover/hit all", "can a person attend all", "free time common to everyone", "burst all balloons".
- A geometric flavor: events happening on a timeline; you care about what's active "right now" as you scan left to right.
- The answer depends on relative order of starts and ends, not their absolute values — a strong hint to **sort first**.

## Mental model
- Almost every interval problem reduces to one decision: **sort by start** or **sort by end**, then make a single greedy pass.
- **Sort by start** when you're stitching ranges together (Merge, Insert) or tracking how many are simultaneously active (Meeting Rooms II): once sorted by start, an interval can only overlap the running frontier.
- **Sort by end** when you want to **keep/pick as many non-conflicting intervals as possible** or **hit all with the fewest points** (Non-overlapping, Arrows). Greedily committing to the smallest end leaves maximum room for the rest — this is the classic activity-selection argument.
- **Sweep line**: turn each interval into two events `(start, +1)` and `(end, -1)`, sort all events by time, and walk through them keeping a running counter. The running counter is the number of active intervals; its max is the peak concurrency. A heap of end-times is an equivalent, often cleaner, way to track "what's still open."
- The single recurring comparison: interval `B` overlaps the current frontier iff `B.start <= frontier.end` (use `<` vs `<=` depending on whether touching endpoints count as overlapping — clarify this with the interviewer).

## Reusable template(s)
```python
import heapq

# ---- Template A: merge / stitch (sort by START) ----
def merge_template(intervals):
    intervals.sort(key=lambda x: x[0])
    out = []
    for s, e in intervals:
        if out and s <= out[-1][1]:          # overlaps current frontier
            out[-1][1] = max(out[-1][1], e)  # extend it
        else:
            out.append([s, e])               # disjoint -> start new block
    return out

# ---- Template B: greedy non-conflicting / hitting set (sort by END) ----
def greedy_by_end(intervals):
    intervals.sort(key=lambda x: x[1])
    last_end = float('-inf')
    chosen = 0
    for s, e in intervals:
        if s >= last_end:      # no conflict with last chosen -> take it
            chosen += 1
            last_end = e
    return chosen

# ---- Template C: max concurrency (sweep line OR min-heap of end times) ----
def max_concurrency_heap(intervals):
    intervals.sort(key=lambda x: x[0])       # process in start order
    heap = []                                # min-heap of end times (active intervals)
    for s, e in intervals:
        if heap and heap[0] <= s:            # earliest-ending interval has freed up
            heapq.heappop(heap)
        heapq.heappush(heap, e)
    return len(heap)                         # peak size = max overlap
```

## Complexity profile
- Dominated by the sort: **Time O(n log n)**, **Space O(n)** (output) or **O(n)** for the heap/event arrays; the sweep itself is O(n).
- Brute force you're beating: checking every pair of intervals for overlap is **O(n^2)**; counting concurrency by sampling every timestamp is even worse. Sorting + one greedy pass collapses this to O(n log n).

## Curated problems (easy -> hard)

### 1. Merge Intervals  -  Medium
- **Problem:** Given a list of intervals, merge all overlapping ones and return the resulting disjoint intervals.
- **Practice (free):** https://leetcode.com/problems/merge-intervals/
- **Video (free):** https://neetcode.io/problems/merge-intervals
- **Idea:** Sort by start; walk through, extending the last merged block whenever the next interval starts at or before its end, otherwise open a new block.
```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])           # sort by start
    merged = []
    for s, e in intervals:
        if merged and s <= merged[-1][1]:         # overlaps the last block
            merged[-1][1] = max(merged[-1][1], e) # extend (don't assume e is bigger)
        else:
            merged.append([s, e])                 # disjoint -> new block
    return merged
```
- **Complexity:** Time O(n log n), Space O(n) for output.
- **Key insight / gotcha:** Use `max(merged[-1][1], e)` when extending — the next interval can be fully *inside* the current block (e.g. `[1,10]` then `[2,3]`); blindly assigning `e` would shrink it.
- **Follow-up:** "What if intervals stream in already sorted by start?" Then drop the sort and merge in O(n); if they arrive unsorted one at a time, maintain a balanced BST / sorted structure and do per-insert work (this becomes Insert Interval repeatedly).

### 2. Insert Interval  -  Medium
- **Problem:** Given a list of non-overlapping intervals sorted by start and a new interval, insert it and merge if necessary, keeping the result sorted and disjoint.
- **Practice (free):** https://leetcode.com/problems/insert-interval/
- **Video (free):** https://neetcode.io/problems/insert-new-interval
- **Idea:** Three phases — copy intervals strictly before the new one, merge everything that overlaps it into one widened interval, then copy the rest. No full sort needed since input is pre-sorted.
```python
def insert(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    res, i, n = [], 0, len(intervals)
    # 1) intervals ending before newInterval starts -> untouched
    while i < n and intervals[i][1] < newInterval[0]:
        res.append(intervals[i]); i += 1
    # 2) all overlapping intervals -> absorb into newInterval
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    res.append(newInterval)
    # 3) intervals starting after newInterval ends -> untouched
    while i < n:
        res.append(intervals[i]); i += 1
    return res
```
- **Complexity:** Time O(n), Space O(n) for output.
- **Key insight / gotcha:** Two intervals overlap (for merging) when `a.start <= b.end` AND `b.start <= a.end`. The phase-2 loop condition `intervals[i][0] <= newInterval[1]` works only because phase 1 already skipped everything ending before `newInterval` starts.
- **Follow-up:** "Endpoints touching — is `[1,2]` and `[2,3]` an overlap?" If they should merge, keep `<=`/`<`; if not, flip the comparisons to strict. Always confirm this convention up front.

### 3. Meeting Rooms  -  Easy
- **Problem:** Given meeting time intervals, determine whether one person can attend all of them (i.e. no two overlap).
- **Practice (free):** https://leetcode.com/problems/meeting-rooms/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/920/
- **Video (free):** https://neetcode.io/problems/meeting-schedule
- **Idea:** Sort by start; if any meeting begins before the previous one ends, there's a conflict.
```python
def canAttendMeetings(intervals: list[list[int]]) -> bool:
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:  # starts before prev ends
            return False
    return True
```
- **Complexity:** Time O(n log n), Space O(1) extra (in-place sort).
- **Key insight / gotcha:** After sorting by start, you only ever need to compare each meeting to its immediate predecessor — not all earlier ones. Back-to-back meetings (`[1,2]`,`[2,3]`) don't conflict, so use strict `<`.
- **Follow-up:** "Now return how many rooms you'd need" -> that's exactly Meeting Rooms II below.

### 4. Non-overlapping Intervals  -  Medium
- **Problem:** Find the minimum number of intervals to remove so the rest are pairwise non-overlapping.
- **Practice (free):** https://leetcode.com/problems/non-overlapping-intervals/
- **Video (free):** https://neetcode.io/problems/non-overlapping-intervals
- **Idea:** Maximize how many you *keep* (classic activity selection): sort by end, greedily keep an interval whenever it starts at/after the last kept one's end. Removals = total - kept.
```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: x[1])     # sort by END
    removals, last_end = 0, float('-inf')
    for s, e in intervals:
        if s >= last_end:                  # no conflict -> keep it
            last_end = e
        else:                              # conflict -> drop this one
            removals += 1
    return removals
```
- **Complexity:** Time O(n log n), Space O(1) extra.
- **Key insight / gotcha:** Sort by **end**, not start. Greedily keeping the interval that ends earliest leaves the most room for future picks — this is provably optimal. Sorting by start fails on cases like `[[1,100],[2,3],[3,4]]`.
- **Follow-up:** "What if you can't reorder and must process as a stream?" Without lookahead you can't guarantee optimal removal; you'd need the full set or a more complex DP/weighted variant (Weighted Interval Scheduling, solved with DP + binary search).

### 5. Minimum Number of Arrows to Burst Balloons  -  Medium
- **Problem:** Balloons span horizontal intervals `[start, end]`; an arrow shot at x bursts every balloon whose interval contains x. Find the minimum arrows to burst all balloons.
- **Practice (free):** https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/
- **Video (free):** https://neetcode.io/problems/minimum-interval-to-include-each-query (related interval-greedy) — or YouTube: https://www.youtube.com/results?search_query=neetcode+minimum+number+of+arrows+to+burst+balloons
- **Idea:** This is the "hitting set" twin of activity selection. Sort by end; place an arrow at the end of the current group; any balloon starting after that arrow's x needs a fresh arrow.
```python
def findMinArrowShots(points: list[list[int]]) -> int:
    points.sort(key=lambda x: x[1])        # sort by END
    arrows, arrow_x = 0, float('-inf')
    for x_start, x_end in points:
        if x_start > arrow_x:              # current arrow can't reach this balloon
            arrows += 1
            arrow_x = x_end                # shoot at this balloon's end
    return arrows
```
- **Complexity:** Time O(n log n), Space O(1) extra.
- **Key insight / gotcha:** Touching balloons *can* be burst together (`[1,2]` and `[2,3]` share x=2), so the test is strict `x_start > arrow_x`. Compare with Non-overlapping Intervals: same sort-by-end greedy, but the comparison flips (`>` here vs `>=` there) because touching counts as a hit, not a conflict.
- **Follow-up:** "What if an arrow has limited range / bursts at most k balloons?" The clean greedy breaks; you'd model it as interval covering with capacity, typically DP or a more careful sweep.

### 6. Meeting Rooms II  -  Medium
- **Problem:** Given meeting intervals, return the minimum number of conference rooms required so no two simultaneous meetings share a room.
- **Practice (free):** https://leetcode.com/problems/meeting-rooms-ii/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/919/
- **Video (free):** https://neetcode.io/problems/meeting-schedule-ii
- **Idea:** The answer is the maximum number of meetings overlapping at any instant. Track active meetings with a min-heap of end times (pop one whenever a meeting starts after it ends); heap size at peak = rooms needed. The sweep-line variant counts +1 at starts and -1 at ends.
```python
import heapq

def minMeetingRooms(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])     # process meetings in start order
    heap = []                              # min-heap of end times of in-use rooms
    for s, e in intervals:
        if heap and heap[0] <= s:          # a room freed before this meeting starts
            heapq.heappop(heap)            # reuse it
        heapq.heappush(heap, e)            # occupy a room until time e
    return len(heap)                       # rooms never released = peak concurrency

# Sweep-line alternative (two sorted arrays of boundary times):
def minMeetingRooms_sweep(intervals: list[list[int]]) -> int:
    starts = sorted(i[0] for i in intervals)
    ends   = sorted(i[1] for i in intervals)
    rooms = peak = 0
    s = e = 0
    while s < len(starts):
        if starts[s] < ends[e]:            # a meeting starts before next one ends
            rooms += 1; s += 1             # need another room
            peak = max(peak, rooms)
        else:
            rooms -= 1; e += 1             # a meeting ended -> free a room
    return peak
```
- **Complexity:** Time O(n log n), Space O(n) for the heap / boundary arrays.
- **Key insight / gotcha:** "Min rooms" = "max simultaneous overlap," nothing more. In the heap version, only pop when `heap[0] <= s` (room freed *at or before* this start) — using `<` would over-allocate when a meeting ends exactly as another begins. In the sweep version the `<` on `starts[s] < ends[e]` enforces the same touching-is-not-overlap rule. Pick whichever convention the interviewer wants.
- **Follow-up:** "Also return *which* meeting goes in which room." Push `(end_time, room_id)` into the heap and recycle the popped room's id; you then label each meeting as you assign it.

### 7. Employee Free Time  -  Hard
- **Problem:** Given each employee's list of busy intervals (each list sorted, non-overlapping), return the finite intervals of free time common to *all* employees.
- **Practice (free):** https://leetcode.com/problems/employee-free-time/ (LeetCode Premium) — free alternative: https://www.lintcode.com/problem/850/
- **Video (free):** https://www.youtube.com/results?search_query=employee+free+time+leetcode
- **Idea:** Flatten everyone's busy intervals into one list, sort by start, and merge as you scan; any gap between the running max end and the next start is free time for everyone.
```python
def employeeFreeTime(schedule: list[list[list[int]]]) -> list[list[int]]:
    # flatten all busy intervals across all employees
    intervals = sorted((iv for emp in schedule for iv in emp), key=lambda x: x[0])
    res = []
    prev_end = intervals[0][1]
    for s, e in intervals[1:]:
        if s > prev_end:               # gap between busy blocks -> common free time
            res.append([prev_end, s])
            prev_end = e
        else:
            prev_end = max(prev_end, e) # overlapping/adjacent busy -> just extend
    return res
```
- **Complexity:** Time O(n log n) for n total intervals, Space O(n).
- **Key insight / gotcha:** A point is free for *everyone* exactly when it lies in **no** busy interval — so once you merge all busy intervals into a single timeline, free time is simply the gaps. Track `prev_end` as the running max (`max(prev_end, e)`) so a short interval nested inside a longer one doesn't falsely create a gap. Use strict `s > prev_end` so touching busy blocks yield no zero-width free slot.
- **Follow-up:** "Inputs are huge / streaming per employee — avoid flattening." Use a min-heap merge across the k sorted employee lists (like Merge k Sorted Lists): pull intervals in start order from the heap and detect gaps on the fly, keeping memory O(k) instead of O(n).

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the template from memory
- [ ] I instantly know whether to sort by **start** (merge/concurrency) or **end** (keep-most/hitting set)
- [ ] Merge Intervals — 🔴 / 🟡 / 🟢
- [ ] Insert Interval — 🔴 / 🟡 / 🟢
- [ ] Meeting Rooms — 🔴 / 🟡 / 🟢
- [ ] Non-overlapping Intervals — 🔴 / 🟡 / 🟢
- [ ] Minimum Number of Arrows to Burst Balloons — 🔴 / 🟡 / 🟢
- [ ] Meeting Rooms II (heap + sweep) — 🔴 / 🟡 / 🟢
- [ ] Employee Free Time — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap (Intervals section): https://neetcode.io/roadmap  |  NeetCode practice list: https://neetcode.io/practice  |  LeetCode "Interval" tag study: https://leetcode.com/tag/interval/
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" — Merge Intervals pattern: https://www.designgurus.io  (free alternative: NeetCode's Intervals roadmap section above, which covers the same problem set with video walkthroughs).

# 04 - Stack & Monotonic Stack
> One-line: when you need to remember "the most recent unresolved thing" (matching/nesting) or "the nearest greater/smaller element to one side", reach for a stack.

## When to use it (recognition triggers)
- Matching/nesting structure: brackets, tags, expressions, "valid", "balanced", "remove adjacent duplicates".
- You need the **nearest greater / nearest smaller** element to the left or right of each element.
- Phrases like "next warmer day", "next greater element", "span", "how many days until...".
- Histogram / skyline / "largest rectangle / area" problems on bar heights.
- Trapping water between bars, building fleets/cars that catch up, stock spans.
- You're scanning left-to-right and each new element can "resolve" or "pop" several pending earlier elements.

## Mental model
- A **stack** keeps the most recently seen, not-yet-resolved items on top. When the current item resolves them, you pop.
- A **monotonic stack** maintains its contents in sorted order (increasing or decreasing). Before pushing the current element, you pop everything that violates the order — and *those pops are the answer* for the popped elements.
- Decreasing stack -> each pop's "next greater" is the current element. Increasing stack -> each pop's "next smaller" is the current element. Pick the direction by what you're searching for.
- Store **indices**, not values, when you need distances/widths (you can always look up the value via the index, but you can't recover the index from a value).
- The amortized cost is O(n): each element is pushed once and popped at most once, even though there's a nested `while`.
- For "next" problems scan as needed; for circular arrays, iterate `2n` with modulo indexing.

## Reusable template(s)
```python
# --- Generic monotonic stack: next greater element to the RIGHT ---
def next_greater_right(nums):
    n = len(nums)
    res = [-1] * n          # default: no greater element
    stack = []              # holds INDICES; values are strictly decreasing
    for i, x in enumerate(nums):
        # current x resolves every pending index whose value is smaller
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x      # x is the next greater for that index
        stack.append(i)
    return res

# --- Bracket / matching stack ---
def balanced(s, pairs={')': '(', ']': '[', '}': '{'}):
    stack = []
    for c in s:
        if c in pairs.values():       # an opener
            stack.append(c)
        elif c in pairs:              # a closer
            if not stack or stack.pop() != pairs[c]:
                return False
    return not stack
```

## Complexity profile
- Time **O(n)** amortized for a single-pass monotonic/matching stack (each index pushed and popped once); O(2n)=O(n) for circular variants.
- Space **O(n)** for the stack in the worst case (e.g., already-sorted input).
- Beats the naive **O(n^2)** "for each element, scan the rest to find the next greater/smaller" or "for each bar, expand left/right".

## Curated problems (easy -> hard)

### 1. Valid Parentheses  -  Easy
- **Problem:** Given a string of `()[]{}`, decide if every bracket is closed by the correct type in the correct order.
- **Practice (free):** https://leetcode.com/problems/valid-parentheses/
- **Video (free):** https://neetcode.io/problems/valid-parentheses
- **Idea:** Push openers; on a closer, the top of the stack must be its matching opener, else invalid. Stack must be empty at the end.
```python
def isValid(s: str) -> bool:
    match = {')': '(', ']': '[', '}': '{'}
    stack = []
    for c in s:
        if c in match:                       # c is a closing bracket
            if not stack or stack.pop() != match[c]:
                return False
        else:                                # c is an opening bracket
            stack.append(c)
    return not stack                          # leftover openers -> invalid
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Check `not stack` *before* popping — a closer with an empty stack is invalid. Forgetting the final `not stack` check accepts `"("`.
- **Follow-up:** "What if the string also contains letters?" Just ignore any char that isn't a bracket (it falls into neither branch).

### 2. Min Stack  -  Medium
- **Problem:** Design a stack supporting `push`, `pop`, `top`, and `getMin`, all in O(1).
- **Practice (free):** https://leetcode.com/problems/min-stack/
- **Video (free):** https://neetcode.io/problems/min-stack
- **Idea:** Keep a parallel stack whose top is always the running minimum, so the min is recoverable as you pop.
```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.mins = []                        # mins[-1] == min of current stack

    def push(self, val: int) -> None:
        self.stack.append(val)
        # push the smaller of val and the current min (or val if empty)
        self.mins.append(val if not self.mins else min(val, self.mins[-1]))

    def pop(self) -> None:
        self.stack.pop()
        self.mins.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.mins[-1]
```
- **Complexity:** Time O(1) per op, Space O(n)
- **Key insight / gotcha:** Push to `mins` on *every* push (even duplicates) so the two stacks stay aligned and `pop` is a simple double-pop. The "store delta from min" trick saves space but is error-prone — only mention it if pressed.
- **Follow-up:** "Reduce extra space?" Store on `mins` only when a new value `<= current min`, and pop from `mins` only when the popped value equals `mins[-1]` (use `<=` / equality to handle duplicate minimums correctly).

### 3. Evaluate Reverse Polish Notation  -  Medium
- **Problem:** Evaluate an arithmetic expression given in postfix (RPN) form, e.g. `["2","1","+","3","*"]` -> 9.
- **Practice (free):** https://leetcode.com/problems/evaluate-reverse-polish-notation/
- **Video (free):** https://neetcode.io/problems/evaluate-reverse-polish-notation
- **Idea:** Push numbers; on an operator pop the two most recent operands, apply, and push the result. Order matters for `-` and `/`.
```python
def evalRPN(tokens: list[str]) -> int:
    ops = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        # truncate toward zero, not floor (int() does this in Python)
        '/': lambda a, b: int(a / b),
    }
    stack = []
    for t in tokens:
        if t in ops:
            b = stack.pop()                   # second operand (popped first)
            a = stack.pop()                   # first operand
            stack.append(ops[t](a, b))
        else:
            stack.append(int(t))
    return stack[0]
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Operand order: the first pop is the **right** operand. `a // b` floors toward negative infinity (`-7 // 2 == -4`); the problem wants truncation toward zero, so use `int(a / b)`.
- **Follow-up:** "Handle infix instead?" Convert infix -> postfix with the shunting-yard algorithm (operator stack + precedence), then evaluate as above.

### 4. Daily Temperatures  -  Medium
- **Problem:** For each day, how many days until a warmer temperature; 0 if none.
- **Practice (free):** https://leetcode.com/problems/daily-temperatures/
- **Video (free):** https://neetcode.io/problems/daily-temperatures
- **Idea:** Monotonic **decreasing** stack of indices. When today is warmer than the day on top, pop it and record the day gap.
```python
def dailyTemperatures(temps: list[int]) -> list[int]:
    res = [0] * len(temps)
    stack = []                                # indices, temps strictly decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j                    # days waited for a warmer day
        stack.append(i)
    return res
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Store **indices** so you can compute the distance `i - j`. Days left on the stack at the end keep their default `0` (no warmer day ever came).
- **Follow-up:** "Next *cooler* day?" Flip the comparison to `temps[stack[-1]] > t` (a monotonic increasing stack).

### 5. Next Greater Element II (circular)  -  Medium
- **Problem:** For each element in a circular array, find the next greater element scanning circularly; -1 if none.
- **Practice (free):** https://leetcode.com/problems/next-greater-element-ii/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+next+greater+element+ii
- **Idea:** Same decreasing-index stack, but iterate `2n` times using `i % n` so wrap-around neighbors are considered; only push during the first pass.
```python
def nextGreaterElements(nums: list[int]) -> list[int]:
    n = len(nums)
    res = [-1] * n
    stack = []                                # indices into nums
    for i in range(2 * n):                    # two laps to simulate circularity
        cur = nums[i % n]
        while stack and nums[stack[-1]] < cur:
            res[stack.pop()] = cur
        if i < n:                             # only push real (first-lap) indices
            stack.append(i)
    return res
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Guard `if i < n` before pushing — otherwise duplicate indices on the second lap corrupt results. Two laps suffice; a third never resolves anything new.
- **Follow-up:** "Next Greater Element I (two arrays, no duplicates)?" Build a value->next-greater map from `nums2` with this stack, then look up each `nums1` value in O(1).

### 6. Car Fleet  -  Medium
- **Problem:** Cars at given positions head to a target at given speeds; a faster car catching a slower one forms a fleet (capped to the slower car's speed). Count the fleets that arrive.
- **Practice (free):** https://leetcode.com/problems/car-fleet/
- **Video (free):** https://neetcode.io/problems/car-fleet
- **Idea:** Sort cars by start position descending (closest to target first). Compute each car's arrival time `(target - pos)/speed`. Walking from the front, a car starts a new fleet only if its time exceeds the current lead fleet's time; otherwise it merges.
```python
def carFleet(target: int, position: list[int], speed: list[int]) -> int:
    # pair up, then sort by position from nearest-the-target down
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    lead_time = -1.0                          # arrival time of the current front fleet
    for pos, spd in cars:
        time = (target - pos) / spd           # time to reach target alone
        if time > lead_time:                  # can't catch the fleet ahead -> new fleet
            fleets += 1
            lead_time = time
        # else: catches up and merges; lead_time unchanged (slower car dominates)
    return fleets
```
- **Complexity:** Time O(n log n) (the sort dominates), Space O(n)
- **Key insight / gotcha:** It's really a monotonic stack of arrival times where you only count "peaks"; you don't need to materialize the stack — a single `lead_time` watermark works. Use strict `>`: equal arrival times at the same target merge into one fleet.
- **Follow-up:** "Cars moving in different directions?" Split by direction and solve each side independently (the target/edge for each side differs).

### 7. Largest Rectangle in Histogram  -  Hard
- **Problem:** Given bar heights of width 1, find the area of the largest axis-aligned rectangle that fits inside the histogram.
- **Practice (free):** https://leetcode.com/problems/largest-rectangle-in-histogram/
- **Video (free):** https://neetcode.io/problems/largest-rectangle-in-histogram
- **Idea:** Monotonic **increasing** stack of indices. When a shorter bar arrives, pop taller bars; each popped bar is the limiting height of a rectangle whose width spans from the new bar back to the element now below it on the stack.
```python
def largestRectangleArea(heights: list[int]) -> int:
    stack = []                                # indices, heights non-decreasing
    best = 0
    # append a 0 sentinel to force-flush the stack at the end
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]     # this bar is the rectangle's height
            # width = from the bar after the new left boundary, up to i-1
            left = stack[-1] if stack else -1
            width = i - left - 1
            best = max(best, height * width)
        stack.append(i)
    return best
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** When you pop bar `j`, its rectangle extends right to `i-1` and left to `stack[-1]+1` (or 0 if the stack is now empty) — hence `width = i - stack[-1] - 1`. The trailing `0` sentinel guarantees every remaining bar gets popped and measured.
- **Follow-up:** "Maximal Rectangle in a 0/1 matrix?" Build a histogram of consecutive 1s per column row-by-row and run this function on each row's heights, taking the max.

### 8. Trapping Rain Water (stack approach)  -  Hard
- **Problem:** Given an elevation map of bar heights, compute how much water is trapped after raining.
- **Practice (free):** https://leetcode.com/problems/trapping-rain-water/
- **Video (free):** https://neetcode.io/problems/trapping-rain-water
- **Idea:** Monotonic **decreasing** stack of indices. When a taller bar arrives, it forms a right wall; pop the dip, and the water above it is bounded by `min(left wall, right wall) - dip height` across the gap.
```python
def trap(height: list[int]) -> int:
    stack = []                                # indices, heights non-increasing
    water = 0
    for i, h in enumerate(height):
        # current bar h is a right wall for any lower bar(s) on the stack
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()              # the dip being filled
            if not stack:                     # no left wall -> water spills off
                break
            left = stack[-1]
            width = i - left - 1              # horizontal span between the walls
            bounded = min(height[left], h) - height[bottom]
            water += width * bounded
        stack.append(i)
    return water
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** The stack fills water *horizontally, layer by layer*, not column by column. After popping `bottom`, if the stack is empty there's no left wall, so that layer holds no water — `break` out. The water height is bounded by the **shorter** of the two walls.
- **Follow-up:** "Do it in O(1) space?" Use the two-pointer method: move the pointer on the side with the smaller wall inward, accumulating `wall_max - height` — same answer, constant space.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the `next_greater_right` template from memory
- [ ] I can derive width `= i - stack[-1] - 1` without re-looking it up
- [ ] Valid Parentheses  🔴/🟡/🟢
- [ ] Min Stack  🔴/🟡/🟢
- [ ] Evaluate Reverse Polish Notation  🔴/🟡/🟢
- [ ] Daily Temperatures  🔴/🟡/🟢
- [ ] Next Greater Element II  🔴/🟡/🟢
- [ ] Car Fleet  🔴/🟡/🟢
- [ ] Largest Rectangle in Histogram  🔴/🟡/🟢
- [ ] Trapping Rain Water (stack)  🔴/🟡/🟢

## Resources
- **Free:** NeetCode Stack roadmap section — https://neetcode.io/roadmap (the "Stack" group covers all 8 above). LeetCode Stack explore card — https://leetcode.com/explore/learn/card/queue-stack/. takeUforward/striver "Monotonic Stack" playlist (search) — https://www.youtube.com/results?search_query=striver+monotonic+stack.
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" — https://www.designgurus.io (pattern-based; free alternative is the NeetCode roadmap above). AlgoMonster monotonic-stack track — https://algo.monster (free alternative: NeetCode problem pages with embedded videos).

# Behavioral — How to Talk Through Code in Interviews
## Senior SWE Bar

At Senior level, the interviewer is NOT just checking if you can solve the problem.
They're checking if you **think like a Senior engineer**:

- You should **smell the right pattern fast** — within 2–3 min max
- You should **dismiss suboptimal approaches yourself** before they ask: *"Can you do better?"*
- You should **drive the conversation**, not wait to be guided
- You should discuss **edge cases proactively**, not when prompted
- Your code should look like code you'd submit in a PR — not scratch work

**Senior red flags (avoid):**
- Taking 10+ min to get to the right approach
- Writing a brute force and waiting for interviewer to ask for optimization
- Not knowing complexity of your own solution
- Asking "is this right?" instead of verifying yourself by tracing through
- Silence for more than 60 seconds

---

## The Mental Model: Interviewer Wants to See Your Brain

The code is secondary. They want to know:
- Do you break problems down logically?
- Do you recognize patterns?
- Can you communicate technical decisions?
- Do you handle being stuck gracefully?

---

## Script for Starting Any Problem

```
"Let me first make sure I understand the problem correctly.
 We have [restate input], and we want to [restate output].
 Can I assume [clarifying questions]?"

Clarifying questions to always ask:
- Is the array sorted?
- Can there be duplicates?
- What's the range of values? (matters for O(n) tricks)
- Should I return indices or values?
- What happens with empty input?

"Okay, let me think through this. 
 A naive approach would be [brute force + complexity].
 But I think we can do better because [pattern recognition].
 Let me try [optimized approach]."
```

---

## Phrases to Use While Coding

| Situation | What to say |
|-----------|-------------|
| Choosing data structure | "I'll use a HashMap here to get O(1) lookup instead of O(n) scan." |
| Two pointers | "Since the array is sorted, I can use two pointers to avoid the O(n^2) nested loop." |
| Sliding window | "This is a subarray constraint problem — I'll use a sliding window to maintain a valid window." |
| BFS vs DFS | "I'll use BFS here because we want the shortest path. DFS would give us existence, not minimum." |
| DP choice | "I'll memoize because we have overlapping subproblems — same subproblem is computed multiple times." |
| Edge case | "Let me check the edge case where the array is empty... okay, we return 0 there." |
| After coding | "Let me trace through the example: input [2,7,11,15], target 9... looks correct." |
| Complexity | "This runs in O(n log n) because we sort, then do a single pass. Space is O(1) extra." |

---

## When You're Stuck

**Don't go silent.** Narrate your confusion:

```
"I'm thinking about this... my initial approach of [X] runs into a problem because [Y].
 Let me step back. What information haven't I used yet?
 [pause] Ah, the array is sorted — that opens up binary search or two pointers."
```

If truly stuck after 5 min, ask:
```
"I have a sense the solution involves [general approach], but I'm not seeing
 the exact recurrence / transition. Could you give me a hint on the data structure
 or the key insight?"
```

---

## Handling "Is There a Better Solution?"

They're asking this to test if you know about the optimal approach.
```
"My current solution is O(n^2). I believe there's an O(n log n) solution
 using a sorted structure / binary search / heap, or even O(n) using a HashMap.
 Would you like me to optimize?"
```

---

## Testing Your Own Code (Last 5 min)

Walk through like a debugger:
```
"Let me trace through: nums = [1, 2, 3], target = 5
 Iteration 1: i=0, seen={}, complement=4, not in seen, add seen[1]=0
 Iteration 2: i=1, complement=3, not in seen, add seen[2]=1
 Iteration 3: i=2, complement=2, 2 in seen at index 1 → return [1, 2] ✓"

Edge cases to always mention:
- Empty input → "we return [] / 0 / -1"
- Single element → "handled by the base case"  
- All elements same → "the duplicate check covers this"
- Negative numbers → "the algorithm still works because..."
```

---

## Quick Self-Assessment After Each Interview

- Did the solution work? (correctness)
- Was complexity optimal? (efficiency)  
- Did I communicate throughout? (communication)
- Did I handle edge cases? (robustness)
- Did I write clean, readable code? (code quality)

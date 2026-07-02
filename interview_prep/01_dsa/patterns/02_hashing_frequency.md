# 02 - Hashing & Frequency Maps
> One-line: when you need O(1) "have I seen this / how many times" lookups, reach for a dict (or set).

## When to use it (recognition triggers)
- The problem asks "does X exist", "how many of X", or "have I seen X before" as you scan.
- You're tempted to write a nested loop comparing every pair — a hash map usually collapses it to one pass.
- You need to **group** items by a derived key (sorted string, count signature, sign).
- You need **counts / frequencies** and then the top-K, the most common, or the first unique.
- A subarray/substring problem where you track a **running quantity** (prefix sum, char counts) and look up complements.
- You need to deduplicate, find intersections, or test set membership cheaply.

## Mental model
- A hash map trades memory for time: it turns "search the whole collection" (O(n)) into "ask one question" (O(1) average). That single swap is what kills most O(n^2) brute forces.
- Two recurring moves: (1) **complement lookup** — while scanning, ask "is the thing that completes my answer already in the map?" (Two Sum, Subarray Sum = K); (2) **canonical key** — map many items to one bucket by computing an invariant key (sorted letters or a 26-count tuple for anagrams).
- For counts, `collections.Counter` is a frequency map with batteries included; for "have I seen it" a `set` is enough.
- Top-K problems combine a Counter with a heap (O(n log k)) or bucket sort (O(n)) — don't sort the whole thing if you only need k.
- Prefix-sum + hashmap is the secret weapon for "contiguous subarray sums": store cumulative sums and look up `prefix - k` instead of recomputing every window.
- Hashing gives **average** O(1); worst case is O(n) under adversarial collisions, but you can quote average-case in interviews.

## Reusable template(s)
```python
from collections import defaultdict, Counter
import heapq

# 1) Complement / "seen" lookup in one pass
def has_complement(nums, target):
    seen = set()                      # or dict: value -> index
    for x in nums:
        if target - x in seen:        # the piece that completes the answer
            return True
        seen.add(x)
    return False

# 2) Group by a canonical key
def group_by_key(items, key_fn):
    buckets = defaultdict(list)
    for it in items:
        buckets[key_fn(it)].append(it)   # all items sharing a key land together
    return list(buckets.values())

# 3) Frequency map -> top K (heap, O(n log k))
def top_k(nums, k):
    freq = Counter(nums)
    return [v for v, _ in heapq.nlargest(k, freq.items(), key=lambda kv: kv[1])]

# 4) Prefix-sum + hashmap for contiguous subarrays
def count_subarrays_sum_k(nums, k):
    seen = defaultdict(int)
    seen[0] = 1                       # empty prefix
    running = ans = 0
    for x in nums:
        running += x
        ans += seen[running - k]      # how many earlier prefixes complete a sum of k
        seen[running] += 1
    return ans
```

## Complexity profile
- Membership / complement / counting: **O(n) time, O(n) space**, beating the O(n^2) brute force of comparing all pairs.
- Grouping: O(n * k) where k is the cost to build each key (e.g. O(L log L) to sort a string of length L).
- Top-K via heap: O(n log k) time; via bucket sort: O(n) time, O(n) space.
- Worst-case hashing is O(n) per op under pathological collisions, but interviewers accept average-case O(1).

## Curated problems (easy -> hard)

### 1. Two Sum  -  Easy
- **Problem:** Given an array and a target, return the indices of the two numbers that add up to the target (exactly one solution, no reuse).
- **Practice (free):** https://leetcode.com/problems/two-sum/
- **Video (free):** https://neetcode.io/problems/two-integer-sum
- **Idea:** Keep a map of value -> index; for each number check whether its complement `target - x` was already seen.
```python
from typing import List

def twoSum(nums: List[int], target: int) -> List[int]:
    seen = {}                          # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []                          # problem guarantees a solution
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Store *after* checking, so you never pair an element with itself. The complement check is the whole pattern.
- **Follow-up:** "What if the array is sorted?" -> two-pointer gives O(1) extra space; "What if many queries on the same array?" -> precompute the map once.

### 2. Contains Duplicate  -  Easy
- **Problem:** Return true if any value appears at least twice in the array.
- **Practice (free):** https://leetcode.com/problems/contains-duplicate/
- **Video (free):** https://neetcode.io/problems/duplicate-integer
- **Idea:** Add to a set while scanning; the moment you try to add something already present, you've found a duplicate.
```python
from typing import List

def containsDuplicate(nums: List[int]) -> bool:
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** `len(set(nums)) != len(nums)` is a one-liner, but the explicit loop short-circuits early — mention both.
- **Follow-up:** "Contains Duplicate II — within distance k?" -> slide a fixed-size set/window of the last k elements.

### 3. Valid Anagram  -  Easy
- **Problem:** Given two strings, determine whether one is a rearrangement of the other (same letters, same counts).
- **Practice (free):** https://leetcode.com/problems/valid-anagram/
- **Video (free):** https://neetcode.io/problems/is-anagram
- **Idea:** Two strings are anagrams iff their character-frequency maps are identical.
```python
from collections import Counter

def isAnagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)    # dict equality compares all counts
```
- **Complexity:** Time O(n), Space O(1) for lowercase ASCII (at most 26 keys), else O(k) for alphabet size k.
- **Key insight / gotcha:** Early length check avoids work and edge cases. `Counter` comparison ignores ordering, which is exactly what an anagram is.
- **Follow-up:** "Unicode / huge alphabet?" -> Counter still works and is O(n); fixed 26-int array only helps for known small alphabets.

### 4. Group Anagrams  -  Medium
- **Problem:** Group a list of strings so that all anagrams of each other are in the same sublist.
- **Practice (free):** https://leetcode.com/problems/group-anagrams/
- **Video (free):** https://neetcode.io/problems/anagram-groups
- **Idea:** Compute a canonical key per word (sorted letters, or a 26-length count tuple) and bucket words by that key.
```python
from typing import List
from collections import defaultdict

def groupAnagrams(strs: List[str]) -> List[List[str]]:
    buckets = defaultdict(list)
    for w in strs:
        count = [0] * 26               # canonical key via letter counts
        for c in w:
            count[ord(c) - ord('a')] += 1
        buckets[tuple(count)].append(w)
    return list(buckets.values())
```
- **Complexity:** Time O(n * L) with the count-tuple key (L = word length); O(n * L log L) if you sort each word instead. Space O(n * L).
- **Key insight / gotcha:** The key must be **hashable** — use a `tuple`, not a `list`. The count-tuple key beats sorting for long words.
- **Follow-up:** "Anagrams across mixed case / unicode?" -> use `tuple(sorted(w))` or a `Counter`-derived frozenset of items as the key.

### 5. Top K Frequent Elements  -  Medium
- **Problem:** Return the k most frequent elements in an array (any order).
- **Practice (free):** https://leetcode.com/problems/top-k-frequent-elements/
- **Video (free):** https://neetcode.io/problems/top-k-elements-in-list
- **Idea:** Count frequencies, then **bucket-sort by frequency** (index = count) to collect the top k in O(n) without a full sort.
```python
from typing import List
from collections import Counter

def topKFrequent(nums: List[int], k: int) -> List[int]:
    freq = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]   # buckets[f] = values seen f times
    for val, f in freq.items():
        buckets[f].append(val)

    res = []
    for f in range(len(buckets) - 1, 0, -1):        # walk from highest frequency down
        for val in buckets[f]:
            res.append(val)
            if len(res) == k:
                return res
    return res
```
- **Complexity:** Time O(n), Space O(n). (A heap variant is O(n log k) — fine when k is small relative to n.)
- **Key insight / gotcha:** Max frequency is bounded by n, so an array of buckets indexed by count gives linear time — no comparison sort needed.
- **Follow-up:** "Streaming / can't hold all data?" -> a size-k min-heap keeps memory O(k) and handles unbounded streams.

### 6. Top K Frequent Words  -  Medium
- **Problem:** Return the k most frequent words, sorted by frequency descending, ties broken **alphabetically (ascending)**.
- **Practice (free):** https://leetcode.com/problems/top-k-frequent-words/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+top+k+frequent+words
- **Idea:** Count words, then order by `(-frequency, word)` so higher counts come first and equal counts fall back to lexicographic order.
```python
from typing import List
from collections import Counter

def topKFrequentWords(words: List[str], k: int) -> List[str]:
    freq = Counter(words)
    # sort by frequency descending, then word ascending for ties
    ordered = sorted(freq, key=lambda w: (-freq[w], w))
    return ordered[:k]
```
- **Complexity:** Time O(n + m log m) (m = distinct words; full sort). Space O(n).
- **Key insight / gotcha:** The tie-break is the trap: you can't just negate frequency *and* word, since words aren't numeric. The `(-freq, word)` tuple sorts frequency descending while keeping words ascending. For optimal O(n log k), use a heap whose comparator flips word order on the *higher-frequency* boundary — but the sort is cleaner and usually accepted.
- **Follow-up:** "Make it O(n log k)." -> push `(freq, word)` into a min-heap of size k with a custom comparator: when popping ties, the lexicographically *larger* word should be evicted first.

### 7. Subarray Sum Equals K  -  Medium
- **Problem:** Count the number of contiguous subarrays whose elements sum to exactly k (values may be negative).
- **Practice (free):** https://leetcode.com/problems/subarray-sum-equals-k/
- **Video (free):** https://neetcode.io/problems/subarray-sum-equals-k
- **Idea:** Track running prefix sums in a map; a subarray ending here sums to k iff some earlier prefix equals `running - k`.
```python
from typing import List
from collections import defaultdict

def subarraySum(nums: List[int], k: int) -> int:
    seen = defaultdict(int)
    seen[0] = 1                        # one empty prefix => sum 0 before we start
    running = ans = 0
    for x in nums:
        running += x
        ans += seen[running - k]       # count earlier prefixes that complete sum k
        seen[running] += 1
    return ans
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** Negatives break the sliding-window approach, so prefix-sum + hashmap is required. Seeding `seen[0] = 1` is what counts subarrays starting at index 0.
- **Follow-up:** "Longest subarray summing to k?" -> store the *first* index for each prefix sum and track max length instead of a count.

### 8. Longest Consecutive Sequence  -  Hard
- **Problem:** Given an unsorted array, find the length of the longest run of consecutive integers (e.g. [100,4,200,1,3,2] -> 4 for [1,2,3,4]).
- **Practice (free):** https://leetcode.com/problems/longest-consecutive-sequence/
- **Video (free):** https://neetcode.io/problems/longest-consecutive-sequence
- **Idea:** Put everything in a set; only start counting a run from a number whose predecessor is absent (a true sequence start), then walk upward.
```python
from typing import List

def longestConsecutive(nums: List[int]) -> int:
    num_set = set(nums)
    best = 0
    for x in num_set:
        if x - 1 not in num_set:       # x is the start of a sequence
            length = 1
            while x + length in num_set:
                length += 1
            best = max(best, length)
    return best
```
- **Complexity:** Time O(n), Space O(n)
- **Key insight / gotcha:** The "start only if `x-1` absent" guard makes it O(n) overall, not O(n^2): each number is visited by at most one inner walk. Sorting would be O(n log n) — the hash set beats it.
- **Follow-up:** "Return the actual sequence, not just length?" -> track the starting value of the best run and reconstruct by walking up from it.

### 9. Encode and Decode Strings  -  Medium
- **Problem:** Design `encode(list[str]) -> str` and `decode(str) -> list[str]` that round-trip a list of arbitrary strings (any chars, including delimiters) over a single string channel.
- **Practice (free):** https://leetcode.com/problems/encode-and-decode-strings/ (LeetCode Premium) — free alternative: https://neetcode.io/problems/string-encode-and-decode
- **Video (free):** https://neetcode.io/problems/string-encode-and-decode
- **Idea:** Length-prefix each string as `len#payload`; on decode, read the integer length up to `#`, then slice exactly that many chars — so the payload can contain anything.
```python
from typing import List

class Codec:
    def encode(self, strs: List[str]) -> str:
        # length + '#' delimiter makes the payload self-describing
        return ''.join(f"{len(s)}#{s}" for s in strs)

    def decode(self, s: str) -> List[str]:
        res, i = [], 0
        while i < len(s):
            j = i
            while s[j] != '#':         # read the length digits
                j += 1
            length = int(s[i:j])
            start = j + 1
            res.append(s[start:start + length])  # slice exactly `length` chars
            i = start + length
        return res
```
- **Complexity:** Time O(total chars) for both directions, Space O(total chars).
- **Key insight / gotcha:** A plain separator (comma, space) fails when the data itself contains it. Length-prefixing sidesteps delimiter collisions entirely — this is the same idea as netstrings / TCP length-prefixed framing.
- **Follow-up:** "Why not just escape the delimiter?" -> escaping works but needs careful unescape logic and is bug-prone; length-prefix decode is unambiguous and is how real wire protocols frame messages.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the complement-lookup and prefix-sum templates from memory
- [Y] Two Sum  -  🟡
- [Y] Contains Duplicate  -  🟡
- [Y] Valid Anagram  -  🟡
- [N] Group Anagrams  -  🟡
- [ ] Top K Frequent Elements  -  🟡
- [ ] Top K Frequent Words (tie-break)  -  🔴
- [ ] Subarray Sum Equals K  -  🔴
- [ ] Longest Consecutive Sequence  -  🔴
- [ ] Encode and Decode Strings  -  🟡

## Resources
- **Free:** NeetCode Arrays & Hashing roadmap section — https://neetcode.io/roadmap ; LeetCode "Top Interview 150" / "HashTable" study tag — https://leetcode.com/problem-list/hash-table/ ; Python `collections` docs (Counter, defaultdict) — https://docs.python.org/3/library/collections.html
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (pattern-based) — https://www.designgurus.io (free alternative: NeetCode practice list https://neetcode.io/practice ); AlgoMonster — https://algo.monster (free alternative: the NeetCode roadmap above).

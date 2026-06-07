# 19 - Bit Manipulation
> One-line: when the answer hinges on individual bits, on XOR's cancel-the-pairs magic, or you must add/count/reverse without normal arithmetic.

## When to use it (recognition triggers)
- "Every element appears twice (or k times) except one" -> XOR or bit-counting.
- The problem mentions a fixed width ("32-bit signed integer", "n is unsigned") and asks you to count, reverse, or overflow-check bits.
- You need O(1) extra space where a hash map would be the "obvious" answer (e.g. find the missing/duplicate number in [0..n]).
- You're asked to do arithmetic (sum, multiply) *without* using `+`/`-`/`*` -> simulate with XOR (sum) and AND-shift (carry).
- You see "is power of two", "toggle/set/clear the i-th bit", "count set bits", or subset enumeration -> bitmask.
- Constraints scream constant-factor speed and the value range is small (`n <= 20` subsets -> 2^n bitmasks).

## Mental model
- A number is just a bit vector. XOR is addition mod 2 per bit: `x ^ x == 0` and `x ^ 0 == x`, so XOR-ing a stream cancels every value that appears an even number of times, leaving the odd one out.
- AND with a shifted value isolates carries; XOR gives the sum-without-carry. Repeating "sum = a^b, carry = (a&b)<<1" until carry is 0 reproduces grade-school addition — that's how hardware adds.
- `n & (n-1)` clears the lowest set bit (Brian Kernighan); `n & (-n)` *isolates* the lowest set bit. These two tricks power most "count bits" and "partition by a differing bit" solutions.
- Python ints are arbitrary precision, so to emulate fixed-width hardware you mask with `0xFFFFFFFF` and re-interpret the sign bit manually. This is the single biggest gotcha for Python bit problems.
- For DP over bits, the relation `bits(i) = bits(i >> 1) + (i & 1)` says "i is its half shifted left, plus whether i is odd" — reuse the already-computed smaller answer.

## Reusable template(s)
```python
# --- Single-value bit utilities (operate on one integer) ---
n.bit_length()          # number of bits to represent n (n>0)
n & (n - 1)             # clear the lowest set bit
n & (-n)                # isolate the lowest set bit (lowest 1, all else 0)
(n >> i) & 1            # read the i-th bit (0-indexed from LSB)
n | (1 << i)            # set the i-th bit
n & ~(1 << i)           # clear the i-th bit
n ^ (1 << i)            # toggle the i-th bit
(n & (n - 1)) == 0      # n is a power of two  (n > 0)

# --- XOR over a stream: cancels every value appearing an even # of times ---
acc = 0
for x in stream:
    acc ^= x            # survivors are the odd-count values

# --- Brian Kernighan: count set bits in O(#set bits) ---
def popcount(n: int) -> int:
    c = 0
    while n:
        n &= n - 1      # drop lowest set bit each step
        c += 1
    return c

# --- Fixed-width emulation in Python (32-bit signed) ---
MASK = 0xFFFFFFFF       # keep only low 32 bits
INT_MAX = 0x7FFFFFFF    # 2**31 - 1
# after computing `a & MASK`, treat as negative if sign bit (bit 31) is set:
#   value = a if a <= INT_MAX else ~(a ^ MASK)
```

## Complexity profile
- XOR/Kernighan stream tricks: **Time O(n·w)** worst case but effectively **O(n)** for fixed width w=32/64; **Space O(1)** — beating the O(n) space hash-map / sorting approaches.
- Per-bit loops (reverse, sum, count for one number): **O(w)** time, **O(1)** space, where w is the word width (32).
- Counting-bits DP: **O(n)** time, **O(n)** space for the output array — beating the naive O(n·w) of popcounting each number independently.

## Curated problems (easy -> hard)

### 1. Single Number  -  Easy
- **Problem:** Every element in an array appears exactly twice except one element that appears once; return that single element using O(1) extra space.
- **Practice (free):** https://leetcode.com/problems/single-number/
- **Video (free):** https://neetcode.io/problems/single-number
- **Idea:** XOR all numbers; pairs cancel to 0, leaving the unique value.
```python
from typing import List

def singleNumber(nums: List[int]) -> int:
    acc = 0
    for n in nums:        # x ^ x = 0, so every pair vanishes
        acc ^= n
    return acc            # only the lone number survives
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** XOR is commutative and associative, so order doesn't matter — you don't need the array sorted or a seen-set.
- **Follow-up:** "What if it appears three times instead of twice?" -> XOR no longer cancels triples; switch to the bit-counting / two-state machine of Single Number II below.

### 2. Number of 1 Bits (Hamming Weight)  -  Easy
- **Problem:** Given an unsigned integer, return how many bits are set to 1 in its binary representation.
- **Practice (free):** https://leetcode.com/problems/number-of-1-bits/
- **Video (free):** https://neetcode.io/problems/number-of-one-bits
- **Idea:** Repeatedly clear the lowest set bit with `n &= n-1`; the number of iterations is the popcount.
```python
def hammingWeight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1        # erases exactly the lowest 1 bit
        count += 1        # one iteration per set bit
    return count
```
- **Complexity:** Time O(#set bits) (<= 32), Space O(1)
- **Key insight / gotcha:** `n & (n-1)` works because subtracting 1 flips the lowest 1 and all trailing 0s; AND-ing keeps everything above untouched and zeroes that region. Beats the naive `for i in range(32): n>>1` loop on sparse inputs.
- **Follow-up:** "Called millions of times — speed it up?" -> precompute a 256-entry lookup table and sum the popcounts of each byte, or just use `bin(n).count('1')` / `int.bit_count()` in Python 3.10+.

### 3. Counting Bits  -  Easy
- **Problem:** Given `n`, return an array `ans` of length `n+1` where `ans[i]` is the number of 1 bits in `i`.
- **Practice (free):** https://leetcode.com/problems/counting-bits/
- **Video (free):** https://neetcode.io/problems/counting-bits
- **Idea:** DP reusing the answer for `i >> 1`: `i` has the same bits as `i//2` shifted left, plus the new low bit `i & 1`.
```python
from typing import List

def countBits(n: int) -> List[int]:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)   # half's count, plus this odd bit
    return dp
```
- **Complexity:** Time O(n), Space O(n) (output)
- **Key insight / gotcha:** The recurrence beats the obvious O(n·32) of popcounting each number; an equivalent form is `dp[i] = dp[i & (i-1)] + 1` (lowest-set-bit relation).
- **Follow-up:** "Prove O(n)" -> each `dp[i]` is O(1) work given previously computed smaller values, so total is O(n); no per-bit loop needed.

### 4. Reverse Bits  -  Easy
- **Problem:** Reverse the bits of a given 32-bit unsigned integer (bit 0 becomes bit 31, etc.).
- **Practice (free):** https://leetcode.com/problems/reverse-bits/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+reverse+bits
- **Idea:** Shift result left and OR in the current lowest bit of `n`, 32 times — pulling bits off the bottom of `n` and stacking them onto `res`.
```python
def reverseBits(n: int) -> int:
    res = 0
    for _ in range(32):           # fixed 32-bit width
        res = (res << 1) | (n & 1)  # push n's LSB onto res
        n >>= 1                     # consume that bit
    return res
```
- **Complexity:** Time O(32) = O(1), Space O(1)
- **Key insight / gotcha:** You MUST loop exactly 32 times even when `n` becomes 0 early, otherwise leading zeros of the original aren't placed correctly in the reversed result.
- **Follow-up:** "Optimize if the function is called repeatedly?" -> reverse byte-by-byte with a cached `{byte: reversed_byte}` map (4 lookups), or do the classic divide-and-conquer mask swaps (swap halves, then quarters, ... in O(log w)).

### 5. Missing Number  -  Easy
- **Problem:** Given an array of `n` distinct numbers taken from `[0, n]`, find the single number in that range missing from the array.
- **Practice (free):** https://leetcode.com/problems/missing-number/
- **Video (free):** https://neetcode.io/problems/missing-number
- **Idea:** XOR together all indices `0..n` and all array values; every present number cancels, leaving the missing one.
```python
from typing import List

def missingNumber(nums: List[int]) -> int:
    res = len(nums)               # start with index n (the value not used as an index)
    for i, n in enumerate(nums):
        res ^= i ^ n              # cancel each index with its value
    return res
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** XOR avoids the integer-overflow risk of the Gauss sum `n*(n+1)//2 - sum(nums)` (a valid alternative in languages with fixed-width ints; in Python both are safe but XOR shows the bit insight).
- **Follow-up:** "Two numbers missing?" -> sum/XOR alone underdetermine two unknowns; XOR everything to get `a^b`, then split the array by a differing bit (same partition trick as Single Number III).

### 6. Reverse Integer  -  Medium
- **Problem:** Reverse the digits of a signed 32-bit integer; return 0 if the reversed value overflows the 32-bit signed range.
- **Practice (free):** https://leetcode.com/problems/reverse-integer/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+reverse+integer
- **Idea:** Peel digits off with `%10` / `//10`, rebuild reversed, then bounds-check against `[-2^31, 2^31-1]`.
```python
def reverse(x: int) -> int:
    INT_MIN, INT_MAX = -2**31, 2**31 - 1
    sign = -1 if x < 0 else 1
    x = abs(x)
    rev = 0
    while x:
        rev = rev * 10 + x % 10   # append last digit of x to rev
        x //= 10
    rev *= sign
    return rev if INT_MIN <= rev <= INT_MAX else 0
```
- **Complexity:** Time O(#digits) = O(log x), Space O(1)
- **Key insight / gotcha:** The whole point is the 32-bit overflow check — in C/Java you must detect overflow *before* it happens (`rev > INT_MAX//10`); Python's big ints let you reverse first then validate, but interviewers want you to name the overflow concern explicitly.
- **Follow-up:** "Do it without Python's arbitrary precision (simulate 32-bit)?" -> before multiplying, check `rev > INT_MAX // 10 or (rev == INT_MAX // 10 and digit > 7)` and bail to 0.

### 7. Sum of Two Integers  -  Medium
- **Problem:** Compute `a + b` without using the `+` or `-` operators.
- **Practice (free):** https://leetcode.com/problems/sum-of-two-integers/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+sum+of+two+integers
- **Idea:** XOR gives sum-without-carry, `(a & b) << 1` gives the carry; loop until there's no carry left. Mask to 32 bits and reinterpret the sign so Python doesn't run forever on negatives.
```python
def getSum(a: int, b: int) -> int:
    MASK = 0xFFFFFFFF
    INT_MAX = 0x7FFFFFFF
    while b & MASK:                  # while a carry remains within 32 bits
        carry = (a & b) << 1         # bits where both are 1 carry left
        a = a ^ b                    # add without carry
        b = carry
    a &= MASK
    # if bit 31 is set, it's a negative number in two's complement
    return a if a <= INT_MAX else ~(a ^ MASK)
```
- **Complexity:** Time O(32) = O(1), Space O(1)
- **Key insight / gotcha:** In Python you *must* mask with `0xFFFFFFFF` — without it, negative operands produce an infinite leftward carry because ints never overflow. The final `~(a ^ MASK)` converts a 32-bit two's-complement pattern back to a Python negative int.
- **Follow-up:** "Subtract without `-`?" -> `a - b == getSum(a, ~b + 1)`, i.e. add the two's complement (negate by flipping bits and adding 1, itself done via `getSum`).

### 8. Single Number II  -  Medium
- **Problem:** Every element appears exactly three times except one that appears once; find it in O(1) extra space.
- **Practice (free):** https://leetcode.com/problems/single-number-ii/
- **Video (free):** https://neetcode.io/problems/single-number-ii
- **Idea:** Track each bit's count mod 3 with a two-state machine (`ones`, `twos`): a bit seen 3 times resets to 0, so the lone element's bits remain in `ones`.
```python
from typing import List

def singleNumber(nums: List[int]) -> int:
    ones = twos = 0
    for n in nums:
        ones = (ones ^ n) & ~twos   # add n to "seen once", drop if already "seen twice"
        twos = (twos ^ n) & ~ones   # promote to "seen twice", drop if now "seen thrice"
    return ones                     # bits seen exactly once
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** `ones`/`twos` are per-bit counters mod 3 (states 00->01->10->00). A simpler-to-explain alternative: for each of the 32 bit positions, sum the bit across all numbers and take `% 3`; that residual bit belongs to the answer.
- **Follow-up:** "Generalize to k repeats with one single?" -> use `ceil(log2(k))` state variables (a mod-k counter per bit), or the bit-sum `% k` approach across all 32 positions.

### 9. Single Number III  -  Medium
- **Problem:** Exactly two elements appear once and all others appear twice; return the two singletons (any order) in O(1) space.
- **Practice (free):** https://leetcode.com/problems/single-number-iii/
- **Video (free):** https://www.youtube.com/results?search_query=neetcode+single+number+iii
- **Idea:** XOR everything to get `a ^ b`; isolate any bit where they differ with `xor & (-xor)`, then partition all numbers by that bit into two groups, each yielding one singleton via XOR.
```python
from typing import List

def singleNumber(nums: List[int]) -> List[int]:
    xor = 0
    for n in nums:
        xor ^= n                # xor == a ^ b (the pairs cancel)
    diff = xor & (-xor)         # lowest bit where a and b differ
    a = b = 0
    for n in nums:
        if n & diff:            # group by that distinguishing bit
            a ^= n
        else:
            b ^= n
    return [a, b]
```
- **Complexity:** Time O(n), Space O(1)
- **Key insight / gotcha:** `a` and `b` differ, so `a ^ b != 0` and has at least one set bit; that bit separates `a` from `b` while each duplicate pair stays together in one group (so it still cancels). `x & (-x)` cleanly grabs the lowest set bit via two's complement.
- **Follow-up:** "What if some elements appear more than twice but still even counts?" -> XOR-cancellation only needs *even* multiplicity, so the same partition works as long as exactly two values have odd counts.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s
- [ ] I can write the Kernighan popcount and the `n&(n-1)` / `n&(-n)` tricks from memory
- [ ] I remember to mask with `0xFFFFFFFF` and reinterpret the sign for fixed-width problems in Python
- [ ] Single Number (XOR all) ... 🟡
- [ ] Number of 1 Bits (Kernighan) ... 🟡
- [ ] Counting Bits (dp[i>>1] + i&1) ... 🟡
- [ ] Reverse Bits (loop exactly 32) ... 🔴
- [ ] Missing Number (XOR indices & values) ... 🟡
- [ ] Reverse Integer (overflow check) ... 🟡
- [ ] Sum of Two Integers (XOR + carry, masked) ... 🔴
- [ ] Single Number II (ones/twos mod-3 machine) ... 🔴
- [ ] Single Number III (xor + differing-bit partition) ... 🔴

## Resources
- **Free:** NeetCode roadmap (Bit Manipulation section) https://neetcode.io/roadmap ; LeetCode "Bit Manipulation" explore card / study plan https://leetcode.com/explore/learn/card/bit-manipulation/ ; HackerEarth bit-manipulation basics https://www.hackerearth.com/practice/basic-programming/bit-manipulation/basics-of-bit-manipulation/tutorial/
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" https://www.designgurus.io (bit-manip module) — free alternative: the NeetCode per-problem videos linked above cover the same problems with walkthroughs.

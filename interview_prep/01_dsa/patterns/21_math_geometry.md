# 21 - Math, Number Theory & Randomized
> One-line: when the answer comes from a numeric identity, a base/representation trick, or a provably-uniform random procedure — not from a data-structure traversal.
>
> **Frequency: MEDIUM-HIGH** — especially **Google** (clean implementation + overflow reasoning) and the **banks (Goldman Sachs / JPMorgan) HackerRank OAs**, which lean math/implementation-heavy: fast power, primes, base conversion, overflow-safe integer parsing. Randomized questions (reservoir sampling, Fisher-Yates, rejection sampling) show up at **Uber / Confluent / Amazon** as "design-an-API-and-prove-it's-uniform" problems.

## When to use it (recognition triggers)
- The problem is stated in terms of **numbers themselves** — "compute x^n", "is this prime", "count primes below n", "trailing zeroes of n!" — with no obvious graph/tree/array structure to traverse.
- You need a **closed-form or logarithmic** answer where the naive loop is O(n) or worse and the constraints (n up to 10^9, 2^31) scream "don't iterate one at a time".
- The input/output crosses a **fixed integer width** (32-bit) and the gotcha is **overflow**, not the algorithm — Reverse Integer, Excel column math, `mid = (lo+hi)//2`.
- The problem is a **base/representation conversion** in disguise: Excel columns are base-26, Roman numerals are positional, "happy number" digit-squaring is a transform on the decimal representation.
- The problem says **"random"**, **"uniform"**, **"pick with probability proportional to ..."**, or **"shuffle"** — and the hard part is *proving* every outcome is equally (or correctly weighted) likely, often under a **streaming / unknown-length** constraint (reservoir sampling).
- You're asked to **build one random primitive out of another** (Rand10 from Rand7) — that's rejection sampling.

## Mental model
- **Fast exponentiation (binary exponentiation):** to compute `x^n`, look at `n` in binary. Square the base each step; whenever the current bit is 1, multiply it into the result. `n` halves every iteration -> O(log n). Same idea powers modular exponentiation and matrix-power Fibonacci.
- **Sieve of Eratosthenes:** instead of testing each number for primality, *cross out* multiples. Start at the first prime, strike `p*p, p*p+p, ...`; what survives is prime. The whole sieve runs in O(n log log n) — effectively linear.
- **GCD / Euclid:** `gcd(a, b) = gcd(b, a % b)`. The remainder shrinks geometrically, so it's O(log(min(a,b))). `lcm(a, b) = a // gcd(a, b) * b` (divide *before* multiply to avoid overflow in fixed-width languages).
- **Cycle detection on a numeric transform (Happy Number):** repeatedly applying a deterministic function to a finite state space *must* eventually cycle. Detect the cycle either with a `seen` set or with **Floyd's slow/fast pointers** — the same tortoise-and-hare you use on linked lists.
- **Base conversion:** Excel columns and number systems are positional. The only wrinkle is **1-indexed** systems (no "zero digit"): subtract 1 before each `%`/`//` so 'A'..'Z' map to 1..26 cleanly.
- **Overflow discipline:** Python ints are unbounded, so 32-bit problems are *artificial* constraints — you must **manually clamp** to `[-2^31, 2^31 - 1]` and return 0 on overflow. State the bound explicitly; interviewers in C++/Java land care a lot.
- **Randomized correctness = prove uniformity by induction.** Fisher-Yates: the element placed at position `i` is chosen uniformly from the remaining unseen ones, so by induction every permutation is equally likely. Reservoir sampling: the `i`-th element is kept with probability `k/i`, and an inductive argument shows every seen element survives with probability `k/n` at the end. Rejection sampling: map a *uniform* range onto a multiple of your target range and **reject the leftover tail** so the kept outcomes stay uniform — never bias by `%`-folding the tail back in.

## Reusable template(s)
```python
# ---- Fast (binary) exponentiation: x^n, optionally mod m ----
def fast_pow(x, n, mod=None):
    if n < 0:                       # x^-n = (1/x)^n
        x, n = 1 / x, -n            # for modular inverse use pow(x, m-2, m) instead
    result = 1
    while n:
        if n & 1:                   # current low bit set
            result = result * x
            if mod: result %= mod
        x = x * x                   # square the base
        if mod: x %= mod
        n >>= 1                     # next bit
    return result

# ---- Sieve of Eratosthenes: all primes < n (returns boolean array) ----
def sieve(n):
    if n < 2:
        return [False] * max(n, 0)
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if is_prime[p]:
            for multiple in range(p * p, n, p):   # start at p*p; smaller multiples already struck
                is_prime[multiple] = False
    return is_prime

# ---- GCD / LCM (Euclid) ----
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
def lcm(a, b):
    return a // gcd(a, b) * b        # divide first => no overflow

# ---- Reservoir sampling: pick 1 item uniformly from a stream of unknown length ----
import random
def reservoir_pick(stream):
    chosen, count = None, 0
    for x in stream:
        count += 1
        if random.randrange(count) == 0:   # keep x with probability 1/count
            chosen = x
    return chosen

# ---- Fisher-Yates: unbiased in-place shuffle ----
def fisher_yates(a):
    for i in range(len(a) - 1, 0, -1):
        j = random.randint(0, i)            # j in [0, i] inclusive
        a[i], a[j] = a[j], a[i]
    return a
```

## Complexity profile
- **Fast power:** O(log n) time, O(1) space (iterative) — vs O(n) for the naive multiply loop.
- **Sieve:** O(n log log n) time, O(n) space. Counting primes below n this way beats per-number trial division (O(n·sqrt(n))) by orders of magnitude.
- **GCD / LCM:** O(log(min(a, b))) time, O(1) space.
- **Base conversion / digit transforms:** O(number of digits) = O(log n).
- **Reservoir sampling:** O(n) time over the stream, O(k) space — *independent of stream length*, which is the whole point.
- **Fisher-Yates:** O(n) time, O(1) extra space, perfectly uniform over all n! permutations.
- **Rejection sampling (Rand10 from Rand7):** expected O(1) calls but unbounded worst case; expected ~2.2 Rand7 calls per Rand10 with the standard rejection scheme.

## Curated problems (easy -> hard)

### 1. Sqrt(x)  -  Easy
- **Problem:** Given a non-negative integer x, return the integer square root (floor of sqrt(x)), without using built-in sqrt.
- **Practice (free):** https://leetcode.com/problems/sqrtx/
- **Video (free):** https://neetcode.io/problems/squares-of-a-sorted-array (sqrt walkthrough) — or search https://www.youtube.com/results?search_query=sqrt+x+binary+search+leetcode
- **Idea:** Binary search the answer in `[0, x]`; the largest `m` with `m*m <= x` is the floor. Compare with `m*m <= x` (not `m <= x/m`) since Python has no overflow.
```python
def mySqrt(x):
    lo, hi, ans = 0, x, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            ans = mid               # candidate; try larger
            lo = mid + 1
        else:
            hi = mid - 1
    return ans
```
- **Complexity:** Time O(log x), Space O(1).
- **Key insight / gotcha:** In C++/Java `mid*mid` overflows — there you'd compare `mid <= x / mid` or use `long`. Track the last valid `mid` in `ans` so you return the floor, not where the loop stalls.
- **Follow-up:** "Need decimals?" Switch to Newton's method: `r = (r + x/r) / 2` converges quadratically; or binary-search on a fixed epsilon.

### 2. Pow(x, n)  -  Medium
- **Problem:** Implement `pow(x, n)` — x raised to the integer power n — in better than O(n).
- **Practice (free):** https://leetcode.com/problems/powx-n/
- **Video (free):** https://neetcode.io/problems/pow-x-n
- **Idea:** Binary exponentiation. Read `n` bit by bit: square the base each step, and when the low bit is 1, fold the current base into the result. Handle negative `n` by inverting once.
```python
def myPow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result
```
- **Complexity:** Time O(log n), Space O(1).
- **Key insight / gotcha:** Inverting `n` with `-n` is safe in Python, but in 32-bit languages `n = -2^31` overflows when negated — convert to a wider type (`long`) first. The naive `x*x*...` loop is O(n) and TLEs at n ~ 10^9.
- **Follow-up:** "Modular version for huge exponents?" Same loop with `result = result * x % mod` and `x = x * x % mod`; that's the core of RSA / competitive modpow (`pow(x, n, mod)` in Python).

### 3. Count Primes  -  Medium
- **Problem:** Count the number of prime numbers strictly less than n.
- **Practice (free):** https://leetcode.com/problems/count-primes/
- **Video (free):** https://neetcode.io/problems/count-primes — or search https://www.youtube.com/results?search_query=count+primes+sieve+of+eratosthenes
- **Idea:** Sieve of Eratosthenes. Mark composites by striking out multiples of each prime starting at `p*p`; count what remains true.
```python
def countPrimes(n):
    if n < 2:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if is_prime[p]:
            is_prime[p * p : n : p] = [False] * len(range(p * p, n, p))  # strike multiples
    return sum(is_prime)
```
- **Complexity:** Time O(n log log n), Space O(n).
- **Key insight / gotcha:** Start striking at `p*p`, not `2*p` — every smaller multiple of `p` (`2p, 3p, ...`) was already struck by a smaller prime. The outer loop only needs to go to `sqrt(n)` for the same reason.
- **Follow-up:** "Memory too tight for the boolean array?" Use a segmented sieve (process ranges of size ~sqrt(n) at a time), or a bitarray to cut space 8x.

### 4. Happy Number  -  Easy
- **Problem:** A number is happy if repeatedly replacing it with the sum of the squares of its digits eventually reaches 1. Return whether n is happy.
- **Practice (free):** https://leetcode.com/problems/happy-number/
- **Video (free):** https://neetcode.io/problems/non-cyclical-number
- **Idea:** The digit-square transform on a bounded state space must cycle. Detect the cycle: either a `seen` set, or Floyd's slow/fast pointers for O(1) space.
```python
def isHappy(n):
    def squares(x):
        total = 0
        while x:
            x, d = divmod(x, 10)
            total += d * d
        return total
    slow, fast = n, squares(n)
    while fast != 1 and slow != fast:        # Floyd's cycle detection
        slow = squares(slow)
        fast = squares(squares(fast))
    return fast == 1
```
- **Complexity:** Time O(log n) per step, O(1) space (Floyd's) — the cycle is reached quickly because values collapse below 1000 fast.
- **Key insight / gotcha:** Unhappy numbers loop forever; without cycle detection you never terminate. The set solution is fine and simpler to explain — reach for Floyd's only if asked for O(1) space.
- **Follow-up:** "Why is it guaranteed to cycle?" After a couple of steps every value is bounded (max digit-square sum for ≤3-digit numbers is 243), so the sequence lives in a finite set and must repeat — pigeonhole.

### 5. Excel Sheet Column Number  -  Easy
- **Problem:** Given an Excel column title like "A", "AB", "ZY", return its corresponding column number (A=1, B=2, ..., Z=26, AA=27).
- **Practice (free):** https://leetcode.com/problems/excel-sheet-column-number/
- **Video (free):** https://www.youtube.com/results?search_query=excel+sheet+column+number+leetcode
- **Idea:** Base-26 conversion, but **1-indexed** (no zero digit). Accumulate `result = result*26 + value(char)` left to right.
```python
def titleToNumber(columnTitle):
    result = 0
    for ch in columnTitle:
        result = result * 26 + (ord(ch) - ord('A') + 1)   # 'A' -> 1, not 0
    return result
```
- **Complexity:** Time O(len), Space O(1).
- **Key insight / gotcha:** It's a *bijective* base-26 system — there is no "0" digit, so 'A' maps to 1. That `+1` is the entire trick and the inverse (column number) below has to compensate for it.
- **Follow-up:** Pairs with the reverse, Excel Sheet Column Title (next).

### 6. Excel Sheet Column Title  -  Easy
- **Problem:** Given a column number (1-indexed), return its Excel column title. 1 -> "A", 28 -> "AB", 701 -> "ZY".
- **Practice (free):** https://leetcode.com/problems/excel-sheet-column-title/
- **Video (free):** https://www.youtube.com/results?search_query=excel+sheet+column+title+leetcode
- **Idea:** Repeated division by 26, but **decrement by 1 each step** before taking the remainder to handle the missing zero digit, then reverse.
```python
def convertToTitle(columnNumber):
    chars = []
    while columnNumber > 0:
        columnNumber -= 1                          # shift to 0-indexed for this digit
        columnNumber, rem = divmod(columnNumber, 26)
        chars.append(chr(rem + ord('A')))
    return ''.join(reversed(chars))
```
- **Complexity:** Time O(log_26 n), Space O(log_26 n) for the output.
- **Key insight / gotcha:** Without the `columnNumber -= 1`, 26 would wrongly produce "A@" instead of "Z" — the decrement converts the 1-indexed system into ordinary base-26 for that digit. Build digits least-significant-first, then reverse.
- **Follow-up:** "One-liner sanity check?" Verify round-trip: `titleToNumber(convertToTitle(k)) == k` for all k in a range.

### 7. Reverse Integer  -  Medium
- **Problem:** Given a signed 32-bit integer x, reverse its digits. Return 0 if the reversed value overflows the 32-bit signed range `[-2^31, 2^31 - 1]`.
- **Practice (free):** https://leetcode.com/problems/reverse-integer/
- **Video (free):** https://neetcode.io/problems/reverse-integer
- **Idea:** Pop digits with `divmod` and push onto the reversed value; after each push, check the 32-bit bound and bail out to 0 if exceeded.
```python
def reverse(x):
    INT_MIN, INT_MAX = -2**31, 2**31 - 1
    sign = -1 if x < 0 else 1
    x = abs(x)
    rev = 0
    while x:
        x, d = divmod(x, 10)
        rev = rev * 10 + d
    rev *= sign
    return rev if INT_MIN <= rev <= INT_MAX else 0   # clamp manually
```
- **Complexity:** Time O(log x), Space O(1).
- **Key insight / gotcha:** Python ints never overflow, so the 32-bit limit is *artificial* — you must check it explicitly. In C++/Java you check **before** the `rev*10 + d` multiply (compare against `INT_MAX/10`), because the overflow happens *during* the push, not after. Mention this distinction — it's the whole point of the problem.
- **Follow-up:** "String to Integer (atoi)?" Same overflow clamping plus whitespace/sign/non-digit parsing — a classic Google/Amazon spec-following question.

### 8. Greatest Common Divisor of Strings  -  Easy
- **Problem:** Two strings str1, str2 have a common divisor string t if t concatenated some number of times equals each. Return the longest such t (or "").
- **Practice (free):** https://leetcode.com/problems/greatest-common-divisor-of-strings/
- **Video (free):** https://www.youtube.com/results?search_query=greatest+common+divisor+of+strings+leetcode
- **Idea:** A common divisor string exists **iff** `str1 + str2 == str2 + str1`. If so, its length is `gcd(len1, len2)` — pure number theory on the lengths.
```python
from math import gcd
def gcdOfStrings(str1, str2):
    if str1 + str2 != str2 + str1:        # no common base string
        return ""
    return str1[:gcd(len(str1), len(str2))]
```
- **Complexity:** Time O(n + m) for the concatenation check, Space O(n + m).
- **Key insight / gotcha:** The `str1+str2 == str2+str1` test is the clever part: concatenation commuting proves both strings are powers of a single base string. Given that, the answer length is exactly the gcd of the two lengths — the same Euclid identity as integers.
- **Follow-up:** "Prove the gcd-of-lengths claim." If both are repetitions of `t`, every common divisor's length divides both lengths, so the longest is the gcd of the lengths; the commuting check guarantees such a `t` exists.

### 9. Factorial Trailing Zeroes  -  Medium
- **Problem:** Given n, return the number of trailing zeroes in n! (n factorial).
- **Practice (free):** https://leetcode.com/problems/factorial-trailing-zeroes/
- **Video (free):** https://www.youtube.com/results?search_query=factorial+trailing+zeroes+leetcode
- **Idea:** A trailing zero comes from a factor of 10 = 2·5; 2s are far more plentiful than 5s, so the count of 5s in `n!` decides. Count multiples of 5, then 25, then 125, ... (Legendre's formula).
```python
def trailingZeroes(n):
    count = 0
    power = 5
    while power <= n:
        count += n // power      # multiples of 5, then 25, then 125, ...
        power *= 5
    return count
```
- **Complexity:** Time O(log_5 n), Space O(1).
- **Key insight / gotcha:** Don't compute `n!` (it explodes and is pointless) — count the 5s. `25 = 5^2` contributes *two* 5s, which is exactly why you keep dividing by higher powers of 5; each `n // 5^k` term catches the k-th 5 in numbers divisible by `5^k`.
- **Follow-up:** "Trailing zeroes in base b?" Factorize b into primes and take the **minimum** over `(count of prime p in n!) // (exponent of p in b)` across all prime factors.

### 10. Random Pick with Weight  -  Medium
- **Problem:** Given an array `w` of positive weights, implement `pickIndex()` returning index `i` with probability `w[i] / sum(w)`.
- **Practice (free):** https://leetcode.com/problems/random-pick-with-weight/
- **Video (free):** https://www.youtube.com/results?search_query=random+pick+with+weight+prefix+sum+binary+search
- **Idea:** Build a prefix-sum array; draw a uniform target in `(0, total]`; binary-search for the first prefix sum >= target. Each index "owns" an interval of width `w[i]`, so it's hit proportionally.
```python
import random, bisect
class Solution:
    def __init__(self, w):
        self.prefix = []
        s = 0
        for x in w:
            s += x
            self.prefix.append(s)
        self.total = s
    def pickIndex(self):
        target = random.randint(1, self.total)      # uniform in [1, total]
        return bisect.bisect_left(self.prefix, target)
```
- **Complexity:** `__init__` O(n); `pickIndex` O(log n) time, O(n) space.
- **Key insight / gotcha:** Use `bisect_left` against the *cumulative* sums and draw `target` in `[1, total]` (inclusive on both sides matters for the boundary indices). Reducing a weighted choice to "find the bucket a uniform point falls into" is the reusable trick.
- **Follow-up:** "Weights change often?" A Fenwick/BIT supports O(log n) updates and prefix queries; or for static heavy use, the **alias method** gives O(1) sampling after O(n) setup.

### 11. Shuffle an Array  -  Medium
- **Problem:** Implement an object that can `reset()` to the original array and `shuffle()` to return a uniformly random permutation.
- **Practice (free):** https://leetcode.com/problems/shuffle-an-array/
- **Video (free):** https://www.youtube.com/results?search_query=shuffle+an+array+fisher+yates+leetcode
- **Idea:** Fisher-Yates. Walk from the last index down; swap each element with a random index in `[0, i]`. Every permutation is equally likely.
```python
import random
class Solution:
    def __init__(self, nums):
        self.original = nums[:]
        self.arr = nums[:]
    def reset(self):
        self.arr = self.original[:]
        return self.arr
    def shuffle(self):
        a = self.arr
        for i in range(len(a) - 1, 0, -1):
            j = random.randint(0, i)         # pick from the unshuffled prefix [0, i]
            a[i], a[j] = a[j], a[i]
        return a
```
- **Complexity:** Time O(n) per shuffle, Space O(n) to hold the original.
- **Key insight / gotcha:** The random index must be `[0, i]` **inclusive** (an element may stay in place). The common bug — picking `j` from `[0, n)` every iteration — is *not* uniform (it produces n^n equally-likely sequences mapping unevenly onto n! permutations, biasing the result). Keep a pristine `original` copy for `reset()`.
- **Follow-up:** "Prove uniformity." By induction: position `n-1` gets each element with prob 1/n; conditioned on that, the sub-shuffle on the first n-1 is uniform, so all n! outcomes have probability 1/n!.

### 12. Linked List Random Node  -  Medium
- **Problem:** Given a singly linked list of unknown length, return a random node's value such that each node is equally likely — using O(1) extra space.
- **Practice (free):** https://leetcode.com/problems/linked-list-random-node/
- **Video (free):** https://www.youtube.com/results?search_query=linked+list+random+node+reservoir+sampling
- **Idea:** Reservoir sampling (k=1). Walk the list once; keep the `i`-th node (1-indexed) with probability `1/i`. The last kept value is uniform over all nodes.
```python
import random
class Solution:
    def __init__(self, head):
        self.head = head
    def getRandom(self):
        result, node, i = None, self.head, 0
        while node:
            i += 1
            if random.randrange(i) == 0:     # keep with probability 1/i
                result = node.val
            node = node.next
        return result
```
- **Complexity:** Time O(n) per call, Space O(1) — no need to know or store the length.
- **Key insight / gotcha:** The magic is `random.randrange(i) == 0` (probability `1/i`). Proof: the `i`-th node is kept with prob `1/i`, and survives all later replacements with prob `prod_{j>i}(1 - 1/j) = i/n`, so its final prob is `(1/i)·(i/n) = 1/n` — uniform. This is *the* answer when length is unknown or the stream doesn't fit in memory.
- **Follow-up:** "Pick k nodes?" Keep a reservoir of size k: fill the first k, then for the `i`-th element (i>k) replace a random reservoir slot with probability `k/i`.

### 13. Implement Rand10() Using Rand7()  -  Medium
- **Problem:** Given `rand7()` (uniform 1..7), implement `rand10()` (uniform 1..10) using only `rand7()`.
- **Practice (free):** https://leetcode.com/problems/implement-rand10-using-rand7/ *(LeetCode Premium to submit; problem statement is public and the logic is fully testable locally)*
- **Free alternative:** read the statement above and test the function below against a frequency histogram; walkthrough: https://www.youtube.com/results?search_query=rand10+using+rand7+rejection+sampling
- **Idea:** Rejection sampling. Two `rand7()` calls give a uniform value in 1..49. Keep only 1..40 (the largest multiple of 10 ≤ 49) and map to 1..10; **reject and retry** on 41..49 so no outcome is biased.
```python
# rand7() is given: returns a uniform integer in [1, 7].
def rand10():
    while True:
        row = rand7()
        col = rand7()
        idx = (row - 1) * 7 + col        # uniform in [1, 49]
        if idx <= 40:                    # keep the uniform prefix
            return (idx - 1) % 10 + 1    # map [1,40] -> [1,10] uniformly
        # else reject (41..49) and retry
```
- **Complexity:** Expected O(1) calls (~2.45 rand7() calls per result with the basic 49->40 scheme), unbounded worst case; O(1) space.
- **Key insight / gotcha:** You must **reject** the leftover tail (41..49), not fold it back with `% 10` — folding 49 outcomes onto 10 buckets makes some buckets more likely and breaks uniformity. The only valid map is from a range whose size is an *exact multiple* of 10.
- **Follow-up:** "Reduce rejections." Recycle the rejected 41..49 (9 values) as a fresh uniform source for the next round instead of discarding — drops expected calls toward ~2.2.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (numbers/base/random, not a traversal)
- [ ] I can write fast binary exponentiation from memory (and the modular variant)
- [ ] I can write the Sieve of Eratosthenes and explain the `p*p` start
- [ ] I can write Euclid's gcd and the overflow-safe lcm
- [ ] I can state the 32-bit clamp for Reverse Integer and where the overflow check goes in C++/Java
- [ ] I can write Fisher-Yates and explain why `[0, i]` inclusive is required
- [ ] I can write reservoir sampling and prove the `1/n` uniformity
- [ ] I can explain why rejection sampling must drop the tail, not `%`-fold it
- [ ] Sqrt(x) — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Pow(x, n) — 🔴 / 🟡 / 🟢
- [ ] Count Primes — 🔴 / 🟡 / 🟢
- [ ] Happy Number — 🔴 / 🟡 / 🟢
- [ ] Excel Column Number — 🔴 / 🟡 / 🟢
- [ ] Excel Column Title — 🔴 / 🟡 / 🟢
- [ ] Reverse Integer — 🔴 / 🟡 / 🟢
- [ ] GCD of Strings — 🔴 / 🟡 / 🟢
- [ ] Factorial Trailing Zeroes — 🔴 / 🟡 / 🟢
- [ ] Random Pick with Weight — 🔴 / 🟡 / 🟢
- [ ] Shuffle an Array — 🔴 / 🟡 / 🟢
- [ ] Linked List Random Node — 🔴 / 🟡 / 🟢
- [ ] Rand10 from Rand7 — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode roadmap, "Math & Geometry" section — https://neetcode.io/roadmap ; CP-Algorithms (binary exponentiation, sieve, Euclid, modular inverse) — https://cp-algorithms.com/ ; Fisher-Yates correctness write-up (Wikipedia) — https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle ; reservoir sampling — https://en.wikipedia.org/wiki/Reservoir_sampling ; takeUforward/Striver math series — https://www.youtube.com/results?search_query=striver+maths+for+dsa
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" (Math/Bit-Manipulation patterns) — https://www.designgurus.io (free alternative: the NeetCode roadmap + CP-Algorithms links above cover fast power, sieve, gcd, and the randomized templates with proofs).

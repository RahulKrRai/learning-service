# 24 - Advanced String Matching — KMP, Rabin-Karp, rolling hash
> One-line: substring search and periodicity problems solved in linear time by reusing previously-matched prefix information (KMP) or by hashing windows incrementally (Rabin-Karp).

> ⚠️ **GOOGLE-HARD / lower-frequency.** These show up rarely, but when a string-matching hard appears it's brutal to derive from scratch under pressure. **Learn the three templates cold (KMP prefix function, Rabin-Karp rolling hash, Z-function) so it can't blindside you — then move on.** Don't over-invest here at the expense of higher-frequency patterns (sliding window, DP, graphs).

## When to use it (recognition triggers)
- You need to find a pattern inside a text and the naive O(n·m) scan is too slow, or the prompt explicitly forbids built-in `find`/`in`.
- The problem is about **periodicity**: "is this string a repetition of a smaller block?", "longest prefix that is also a suffix", "shortest characters to prepend to make a palindrome".
- You need to detect **repeated fixed-length substrings** (e.g. all length-10 DNA windows seen more than once) — rolling hash gives O(1) per window.
- "Longest [duplicate / common] substring" where a length is the unknown — think **binary search on the length + a hash/automaton check** at each candidate length.
- Anything that screams "match a prefix against a suffix" — the KMP **LPS (longest proper prefix = suffix)** array is the universal tool.

## Mental model
- **KMP's one idea:** when a mismatch happens after matching some characters, you already know those characters — so instead of restarting, jump the pattern pointer back to the length of the **longest proper prefix of what you matched that is also a suffix of it**. That jump table is the `lps` array (a.k.a. the prefix/failure function). Computing it *is* the algorithm; the search is just the same logic run over text + pattern.
- A **proper prefix** excludes the whole string; `lps[i]` = length of the longest proper prefix of `s[:i+1]` that's also a suffix of `s[:i+1]`. Building it is itself a self-matching of the string against itself.
- **Rabin-Karp's one idea:** treat a window of characters as a base-B number mod a big prime. Sliding the window one step is O(1): subtract the leaving char's contribution, multiply by B, add the entering char. Equal hashes ⇒ *probably* equal strings; on a hit you either verify char-by-char (deterministic) or trust the hash with a large prime / double hashing (probabilistic). **Always say the word "collision" in an interview** — a naive single small modulus can be defeated.
- **Binary search + hashing** turns "longest duplicate substring" into "for a fixed length L, does any duplicate of length L exist?" — monotone in L, so binary-search L and answer each check with a hash set of rolling hashes.
- **Z-function** is the close cousin of LPS (covered below): `z[i]` = length of the longest substring starting at `i` that matches a prefix of the string. Either tool solves most matching/periodicity problems; pick whichever you can write correctly.

## Reusable template(s)
```python
# ---- 1) KMP prefix function (LPS / failure array) ----
def build_lps(p):
    """lps[i] = length of the longest proper prefix of p[:i+1] that is also a suffix."""
    lps = [0] * len(p)
    k = 0                                  # length of current matched prefix
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:      # mismatch: fall back along the chain
            k = lps[k - 1]
        if p[i] == p[k]:                   # extend the matched prefix
            k += 1
        lps[i] = k
    return lps

def kmp_search(text, p):
    """Return all start indices where pattern p occurs in text. O(n + m)."""
    if not p:
        return list(range(len(text) + 1))
    lps, res, k = build_lps(p), [], 0
    for i, ch in enumerate(text):
        while k > 0 and ch != p[k]:
            k = lps[k - 1]                 # reuse already-matched prefix
        if ch == p[k]:
            k += 1
        if k == len(p):
            res.append(i - k + 1)
            k = lps[k - 1]                 # continue for overlapping matches
    return res


# ---- 2) Rabin-Karp rolling hash (collision-aware) ----
def rabin_karp(text, p):
    """Return all start indices of p in text using a rolling polynomial hash."""
    n, m = len(text), len(p)
    if m == 0 or m > n:
        return [] if m > n else list(range(n + 1))
    BASE, MOD = 256, (1 << 61) - 1         # large prime modulus => collisions ~ negligible
    high = pow(BASE, m - 1, MOD)           # weight of the leading character
    ph = th = 0
    for i in range(m):                     # hash the pattern and the first window
        ph = (ph * BASE + ord(p[i])) % MOD
        th = (th * BASE + ord(text[i])) % MOD
    res = []
    for i in range(n - m + 1):
        if ph == th and text[i:i + m] == p:   # verify on hash hit (kills collisions)
            res.append(i)
        if i < n - m:                      # roll the window forward in O(1)
            th = (th - ord(text[i]) * high) % MOD
            th = (th * BASE + ord(text[i + m])) % MOD
    return res
# Collision note: equal hashes do NOT guarantee equal strings. Either verify the slice
# (above) for a deterministic answer, or use a 61-bit prime / two independent moduli
# (double hashing) when verification is too expensive (e.g. millions of windows).
```

**Z-function (alternative to LPS), one paragraph:** the Z-array of a string `s` is defined by `z[i]` = the length of the longest substring starting at `i` that is also a prefix of `s` (`z[0]` is conventionally 0 or `len(s)`). It is built in O(n) by maintaining the rightmost match window `[l, r]` seen so far: for each `i` inside the window you reuse `z[i - l]` as a head start, then extend naively past `r`. To search for a pattern `p` in text `t`, run the Z-function over `p + sep + t` (with `sep` a char in neither) and any position whose `z`-value equals `len(p)` is a match. Anything KMP's LPS solves — matching, periodicity, "prefix = suffix" — the Z-function solves too, so just learn whichever one you can reproduce without bugs; LPS is the more commonly expected answer in interviews.

## Complexity profile
- **KMP:** O(n + m) time (build LPS in O(m), scan text in O(n)), O(m) extra space — strictly linear, the classic "why this beats naive" answer.
- **Rabin-Karp:** O(n + m) expected, O(n·m) worst case if hashes keep colliding and you verify every hit; a large prime modulus makes the worst case practically unreachable.
- **Binary search + Rabin-Karp (longest duplicate substring):** O(n log n) expected — `log n` length candidates, each an O(n) rolling-hash sweep.
- **Z-function:** O(n) time / O(n) space, same asymptotics as KMP.
- The recurring win: naive search re-examines text characters you already matched; KMP/Z never moves the text pointer backward, and Rabin-Karp collapses a whole window comparison into one O(1) hash update.

## Curated problems (easy -> hard)

### 1. Implement strStr()  -  Easy (KMP under the hood)
- **Problem:** Return the index of the first occurrence of `needle` in `haystack`, or -1 if it isn't present (return 0 if `needle` is empty).
- **Practice (free):** https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
- **Video (free):** https://neetcode.io/problems/kmp  (KMP walkthrough) ; alt search: https://www.youtube.com/results?search_query=KMP+algorithm+strStr+explained
- **Idea:** Build the LPS for `needle`, then scan `haystack` once. On a mismatch, fall back the pattern pointer to `lps[k-1]` instead of restarting from 0 — that reuse is what makes it linear. **Step-by-step LPS for `"aabaaa"`:** start `k=0`. `i=1 'a'` matches `p[0]='a'` ⇒ `k=1`, `lps[1]=1`. `i=2 'b'`≠`p[1]='a'`, `k>0` so `k=lps[0]=0`; `'b'`≠`p[0]` ⇒ `lps[2]=0`. `i=3 'a'`=`p[0]` ⇒ `k=1`, `lps[3]=1`. `i=4 'a'`=`p[1]` ⇒ `k=2`, `lps[4]=2`. `i=5 'a'`≠`p[2]='b'`, fall back `k=lps[1]=1`; `'a'`=`p[1]` ⇒ `k=2`, `lps[5]=2`. Final `lps=[0,1,0,1,2,2]`.
```python
def strStr(haystack, needle):
    if not needle:
        return 0
    n, m = len(haystack), len(needle)
    lps = [0] * m
    k = 0
    for i in range(1, m):                      # build failure function
        while k > 0 and needle[i] != needle[k]:
            k = lps[k - 1]
        if needle[i] == needle[k]:
            k += 1
        lps[i] = k
    k = 0
    for i in range(n):                         # scan the haystack once
        while k > 0 and haystack[i] != needle[k]:
            k = lps[k - 1]
        if haystack[i] == needle[k]:
            k += 1
        if k == m:
            return i - m + 1                   # first full match
    return -1
```
- **Complexity:** Time O(n + m), Space O(m) for the LPS.
- **Key insight / gotcha:** The `while k > 0` fallback loop is amortized O(1) per character — `k` rises by at most 1 per step and the `while` can only drop it, so total work is linear, not quadratic. Don't reset `k=0` on a mismatch.
- **Follow-up:** "Why not just use the naive double loop?" Naive is O(n·m) and re-scans matched text on every mismatch (worst case `"aaaa…ab"` in `"aaaa…aa"`); KMP never re-reads a text character.

### 2. Repeated Substring Pattern  -  Easy
- **Problem:** Given a string, return true if it can be constructed by taking some substring and concatenating it two or more times.
- **Practice (free):** https://leetcode.com/problems/repeated-substring-pattern/
- **Video (free):** https://www.youtube.com/results?search_query=repeated+substring+pattern+KMP+lps
- **Idea (LPS trick):** Build the LPS; let `k = lps[-1]` be the longest prefix=suffix. The string is periodic iff `k > 0` **and** `n % (n - k) == 0` — the period length is `n - k`, and it must tile the whole string evenly.
```python
def repeatedSubstringPattern(s):
    n = len(s)
    lps = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = lps[k - 1]
        if s[i] == s[k]:
            k += 1
        lps[i] = k
    period = n - lps[-1]
    return lps[-1] > 0 and n % period == 0
```
- **Complexity:** Time O(n), Space O(n).
- **Key insight / gotcha:** `n - lps[-1]` is the smallest period only when `n % (n - lps[-1]) == 0`; the divisibility check is essential (e.g. `"aabaaba"` has `lps[-1]=4`, period 3, but 7 % 3 ≠ 0 ⇒ not repeated).
- **Follow-up:** "One-liner without KMP?" `(s + s)[1:-1].find(s) != -1` — doubling and chopping one char off each end exposes the repeat; correct but O(n²) with `find`, whereas the LPS version is O(n).

### 3. Longest Happy Prefix  -  Hard (pure LPS)
- **Problem:** A "happy prefix" is a non-empty prefix that is also a suffix (excluding the whole string). Return the longest happy prefix, or `""` if none.
- **Practice (free):** https://leetcode.com/problems/longest-happy-prefix/
- **Video (free):** https://www.youtube.com/results?search_query=longest+happy+prefix+KMP+prefix+function
- **Idea:** This is literally `lps[-1]`. Build the prefix function over the whole string; the answer is `s[:lps[-1]]`. No search phase needed — the definition of LPS *is* "longest proper prefix that is also a suffix".
```python
def longestPrefix(s):
    n = len(s)
    lps = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = lps[k - 1]
        if s[i] == s[k]:
            k += 1
        lps[i] = k
    return s[:lps[-1]]
```
- **Complexity:** Time O(n), Space O(n).
- **Key insight / gotcha:** "Proper" prefix means it cannot be the entire string — the LPS construction guarantees this because `i` ranges over `1..n-1` and `k` can never reach `n`. This is the cleanest possible demonstration that you understand the failure function.
- **Follow-up:** "Could a rolling hash do this?" Yes — compare prefix and suffix hashes for each length and take the largest match, but you'd want double hashing to be safe and it's O(n) hashing anyway, so LPS is simpler and deterministic.

### 4. Shortest Palindrome  -  Hard (KMP)
- **Problem:** Given a string `s`, prepend the fewest characters in front of it to make it a palindrome; return the resulting palindrome.
- **Practice (free):** https://leetcode.com/problems/shortest-palindrome/
- **Video (free):** https://www.youtube.com/results?search_query=shortest+palindrome+KMP+leetcode
- **Idea:** Find the longest prefix of `s` that is itself a palindrome — those characters are already symmetric and need nothing prepended; the rest (its reverse) is what you add up front. Compute it with KMP: build the LPS of `s + sep + reverse(s)`; `lps[-1]` is the length of the longest prefix of `s` matching a suffix of `reverse(s)` — i.e. the longest palindromic prefix.
```python
def shortestPalindrome(s):
    if not s:
        return s
    combined = s + '#' + s[::-1]           # '#' separator avoids overcounting
    n = len(combined)
    lps = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and combined[i] != combined[k]:
            k = lps[k - 1]
        if combined[i] == combined[k]:
            k += 1
        lps[i] = k
    longest_pal_prefix = lps[-1]           # length of longest palindromic prefix of s
    suffix = s[longest_pal_prefix:]        # the part not yet symmetric
    return suffix[::-1] + s
```
- **Complexity:** Time O(n), Space O(n) for the combined string and its LPS.
- **Key insight / gotcha:** The `'#'` separator (a char that appears in neither half) prevents the matched length from running past `len(s)` and producing a bogus overlap; without it `"aaaa"`-type inputs over-match.
- **Follow-up:** "Why reverse and concatenate?" Matching `s` against `reverse(s)` via LPS finds the longest prefix-of-`s` = suffix-of-`reverse(s)`, which is exactly the longest palindromic prefix — KMP repurposed for a palindrome question.

### 5. Find All Anagrams in a String  -  Medium (sliding-window counts, cross-ref)
- **Problem:** Given strings `s` and `p`, return the start indices of all of `p`'s anagrams in `s`.
- **Practice (free):** https://leetcode.com/problems/find-all-anagrams-in-a-string/
- **Video (free):** https://neetcode.io/problems/find-all-anagrams-in-a-string
- **Idea:** Not KMP — this is a fixed-size **sliding window of character counts** (see `06_sliding_window.md`). Maintain a count array for the current window of length `len(p)`; slide one char at a time and compare counts to `p`'s. Listed here because people reach for string matching, but counts win.
```python
from collections import Counter

def findAnagrams(s, p):
    if len(p) > len(s):
        return []
    need = Counter(p)
    window = Counter(s[:len(p)])
    res = [0] if window == need else []
    for i in range(len(p), len(s)):
        window[s[i]] += 1                  # add the entering char
        left = s[i - len(p)]
        window[left] -= 1                  # remove the leaving char
        if window[left] == 0:
            del window[left]               # keep Counter clean so == works
        if window == need:
            res.append(i - len(p) + 1)
    return res
```
- **Complexity:** Time O(n) (each `Counter` comparison is O(26) for lowercase letters), Space O(1) for fixed alphabet.
- **Key insight / gotcha:** `del` the key when its count hits 0 — a `Counter` with a lingering `0` entry is `!=` one without it, breaking the equality check. A fixed-size `[0]*26` array with a `matches` counter avoids this entirely and is the more interview-robust form.
- **Follow-up:** "Permutation in String (LC 567)" is the same window asking only *whether* one anagram exists — return `True` on the first match. Cross-reference the sliding-window pattern file.

### 6. Repeated DNA Sequences  -  Medium (Rabin-Karp rolling hash)
- **Problem:** Return all 10-letter substrings (over A/C/G/T) that occur more than once in a DNA string.
- **Practice (free):** https://leetcode.com/problems/repeated-dna-sequences/
- **Video (free):** https://neetcode.io/problems/repeated-dna-sequences  ; alt: https://www.youtube.com/results?search_query=repeated+dna+sequences+rolling+hash
- **Idea:** Fixed window length 10 ⇒ classic rolling hash. Map each base to 0–3 (2 bits), roll a base-4 hash across the string in O(1) per step, and record substrings whose hash-window appears a second time. (A set of raw slices is also O(n) here, but rolling hash is the point of the exercise and generalizes to long windows.)
```python
def findRepeatedDnaSequences(s):
    L = 10
    if len(s) <= L:
        return []
    enc = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    nums = [enc[c] for c in s]
    BASE = 4
    high = BASE ** (L - 1)                  # 2-bit alphabet => exact 20-bit key, no collisions
    h = 0
    for i in range(L):                      # hash the first window
        h = h * BASE + nums[i]
    seen, out = {h}, set()
    for i in range(1, len(s) - L + 1):
        h = (h - nums[i - 1] * high) * BASE + nums[i + L - 1]   # roll forward
        if h in seen:
            out.add(s[i:i + L])
        else:
            seen.add(h)
    return list(out)
```
- **Complexity:** Time O(n), Space O(n) for the hash set.
- **Key insight / gotcha:** With a 4-letter alphabet and length 10 the hash fits in 20 bits and is a *perfect* encoding — no collisions, no verification needed. For a large alphabet you'd take it mod a big prime and verify on hits.
- **Follow-up:** "Length is a parameter / alphabet is large." Generalize `L`, switch to `(h * BASE + c) % MOD` with a 61-bit prime, and verify slices on hash equality.

### 7. Longest Duplicate Substring  -  Hard (binary search + Rabin-Karp) ⚠️ genuinely hard
- **Problem:** Return any longest substring that appears at least twice in `s` (return `""` if none).
- **Practice (free):** https://leetcode.com/problems/longest-duplicate-substring/
- **Video (free):** https://www.youtube.com/results?search_query=longest+duplicate+substring+binary+search+rabin+karp
- **Idea:** "Does a duplicate of length L exist?" is **monotone** in L (if length L repeats, so does any L′ < L). Binary-search L; for each candidate, roll a hash over all length-L windows and check a hash set — on a hash hit, verify the slice to defeat collisions. This is among the harder string problems; expect to need two moduli (double hashing) in a strict setting.
```python
def longestDupSubstring(s):
    n = len(s)
    nums = [ord(c) - ord('a') for c in s]
    BASE, MOD = 26, (1 << 61) - 1

    def search(L):
        """Return start index of a duplicated length-L substring, or -1."""
        if L == 0:
            return 0
        high = pow(BASE, L - 1, MOD)
        h = 0
        for i in range(L):
            h = (h * BASE + nums[i]) % MOD
        seen = {h: [0]}                     # hash -> list of start indices (collision-safe)
        for i in range(1, n - L + 1):
            h = ((h - nums[i - 1] * high) * BASE + nums[i + L - 1]) % MOD
            if h in seen:
                cand = s[i:i + L]
                for j in seen[h]:           # verify against every same-hash candidate
                    if s[j:j + L] == cand:
                        return i
                seen[h].append(i)
            else:
                seen[h] = [i]
        return -1

    lo, hi, start, length = 1, n - 1, 0, 0
    while lo <= hi:                         # binary search on the answer length
        mid = (lo + hi) // 2
        idx = search(mid)
        if idx != -1:
            start, length = idx, mid        # length mid works -> try longer
            lo = mid + 1
        else:
            hi = mid - 1                     # too long -> shrink
    return s[start:start + length]
```
- **Complexity:** Time O(n log n) expected (log n length candidates × O(n) sweep), Space O(n).
- **Key insight / gotcha:** Store hash → *list* of start indices and verify the actual slices; a single 61-bit prime plus verification is deterministic. Skipping verification with one small modulus is how this problem gets you wrong-answer on adversarial inputs.
- **Follow-up:** "Truly worst-case linear?" A suffix automaton / suffix array with LCP solves it in O(n) or O(n log n) deterministically without hashing — much harder to code and rarely expected; mention you know it exists.

## Self-rating checklist
- [ ] I can recognise this pattern in <30s (periodicity / prefix=suffix / fixed-window repeats)
- [ ] I can write the KMP LPS (prefix function) from memory and trace it on a small string
- [ ] I can explain why the KMP fallback loop is amortized O(1) (linear, not quadratic)
- [ ] I can write a Rabin-Karp rolling hash and say the word "collision" + how I handle it
- [ ] I can recall the Z-function's definition and the `p + sep + t` search trick
- [ ] Implement strStr() (KMP) — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Repeated Substring Pattern — 🔴 / 🟡 / 🟢
- [ ] Longest Happy Prefix — 🔴 / 🟡 / 🟢
- [ ] Shortest Palindrome — 🔴 / 🟡 / 🟢
- [ ] Find All Anagrams in a String — 🔴 / 🟡 / 🟢
- [ ] Repeated DNA Sequences — 🔴 / 🟡 / 🟢
- [ ] Longest Duplicate Substring — 🔴 / 🟡 / 🟢

## Resources
- **Free:** NeetCode KMP page — https://neetcode.io/problems/kmp ; CP-Algorithms prefix function (KMP) — https://cp-algorithms.com/string/prefix-function.html ; CP-Algorithms Z-function — https://cp-algorithms.com/string/z-function.html ; CP-Algorithms string hashing (Rabin-Karp) — https://cp-algorithms.com/string/string-hashing.html ; Abdul Bari KMP video — https://www.youtube.com/results?search_query=abdul+bari+KMP+algorithm
- **Paid (optional):** DesignGurus "Grokking the Coding Interview" string-search modules — https://www.designgurus.io (free alternative: the CP-Algorithms pages above cover KMP, Z-function, and hashing with full derivations and code).

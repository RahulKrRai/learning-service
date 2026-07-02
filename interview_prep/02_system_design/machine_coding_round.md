# Machine Coding Round
> One-line: a timed (60-120 min) round where you *build working, running code* for a small system — graded on clean, extensible OO design, not on algorithms. **Atlassian's signature round; also seen at Uber, Flipkart, Swiggy, and many product companies.**

> **Why this file exists:** This is distinct from [low-level design](./low_level_design.md) (whiteboard object modeling) and from DSA. Here you actually type a compiling program with a `main()` driver, in-memory state, and clean class boundaries — and they run/read it. Atlassian is a PRIMARY target and this is its make-or-break round. If you've only ever whiteboarded LLD, you will feel the difference: the clock is real and the code must *work*.

---

## What they're actually grading (the rubric)

Interviewers score on a rubric like this — internalize it, because knowing it changes what you spend minutes on:

| Dimension | What "good" looks like | Weight |
|---|---|---|
| **Working code** | It compiles and runs the happy path end-to-end. A demo `main()` exercises the features. | 🔴 must-have — a non-running solution often auto-fails |
| **Correctness / edge cases** | Handles the obvious edge cases you called out; no crashes on bad input. | 🔴 high |
| **Extensibility / OOP** | New requirement (a new "type", a new strategy) = add a class, not edit a switch. Interfaces + composition. | 🔴 high — this is the point of the round |
| **Clean code** | Meaningful names, small methods, single responsibility, no god-class, no dead code. | 🟡 medium |
| **Separation of concerns** | Entities / services / repository (storage) / driver are separate. Business logic not in `main()`. | 🟡 medium |
| **Thread-safety / concurrency** | *Only if asked* — don't gold-plate. Mention it, add it if there's time. | 🔵 situational |
| **Tests** | A couple of assertions or a test method earns real credit and buys trust. | 🟡 medium |

**The trap:** candidates over-engineer (DB layers, config, 12 design patterns) and run out of time with nothing running. **A working, clean, extensible core beats a half-built cathedral.** Ship the walking skeleton first.

---

## The 6-step approach (time-boxed for a 90-min round)

1. **Clarify & freeze scope (5-10 min).** List the features out loud, then *cut*. Say: "I'll build core features A, B, C fully; D and E I'll design for but stub if time runs short." Get a nod. **In-memory only** unless told otherwise — no real DB.
2. **Model the entities (10 min).** Nouns -> classes. Enums for fixed sets (status, type). Keep entities as data + invariants; keep behavior in services. Sketch the 4-6 core classes and their relationships before typing much.
3. **Pick the seams for extensibility (5 min).** Where will requirements change? That's where an **interface + Strategy** goes (pricing, eviction, matching, notification channel). This is what earns the "extensible" score.
4. **Build the walking skeleton (30-40 min).** Storage (a repo class wrapping dicts) -> services (business logic) -> a `main()` that runs the happy path. Get *something running* by the halfway mark, then flesh out.
5. **Edge cases + a couple of tests (10-15 min).** Guard invalid input, empty states, capacity limits. Add 2-3 assertions. Narrate the edge cases you're *choosing not* to handle and why.
6. **Walk them through it (5 min).** Run it, show output, point at your extension seam: "to add a new X, you implement this interface — nothing else changes."

**Design patterns that pay off here (don't force them):** Strategy (pluggable behavior — the #1 useful one), Factory (create-by-type), Singleton (the in-memory store/registry), Observer (event notifications), State (lifecycle/status machines). Reach for one because it removes an `if/elif` chain, not to show off.

---

## Fully worked example: In-memory cache with pluggable eviction + TTL

A perfect machine-coding prompt: small enough to finish, but the **eviction policy is the extension seam** (LRU today, LFU tomorrow) — exactly what the rubric rewards. Runnable Python 3, standard library only.

```python
import time
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict

# ---- Extension seam: an eviction policy is a Strategy ----
class EvictionPolicy(ABC):
    @abstractmethod
    def key_accessed(self, key): ...          # called on get/put
    @abstractmethod
    def evict_key(self):        ...           # return the key to remove
    @abstractmethod
    def remove(self, key):      ...           # key gone (expired/deleted)

class LRUPolicy(EvictionPolicy):
    def __init__(self):
        self._order = OrderedDict()           # key -> None, ordered by recency
    def key_accessed(self, key):
        self._order.pop(key, None)
        self._order[key] = None               # most-recent at the end
    def evict_key(self):
        key, _ = self._order.popitem(last=False)  # least-recent at the front
        return key
    def remove(self, key):
        self._order.pop(key, None)

class LFUPolicy(EvictionPolicy):
    def __init__(self):
        self._freq = defaultdict(int)
    def key_accessed(self, key):
        self._freq[key] += 1
    def evict_key(self):
        key = min(self._freq, key=self._freq.get)   # least-frequently used
        del self._freq[key]
        return key
    def remove(self, key):
        self._freq.pop(key, None)

# ---- Core service: depends on the abstraction, not a concrete policy ----
class Cache:
    def __init__(self, capacity, policy: EvictionPolicy):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._cap = capacity
        self._policy = policy
        self._store = {}                      # key -> (value, expiry_epoch|None)
        self._lock = threading.Lock()         # asked-for thread safety, kept minimal

    def put(self, key, value, ttl_seconds=None):
        with self._lock:
            expiry = (time.time() + ttl_seconds) if ttl_seconds else None
            if key not in self._store and len(self._store) >= self._cap:
                victim = self._policy.evict_key()
                self._store.pop(victim, None)
            self._store[key] = (value, expiry)
            self._policy.key_accessed(key)

    def get(self, key):
        with self._lock:
            if key not in self._store:
                return None
            value, expiry = self._store[key]
            if expiry is not None and time.time() > expiry:   # lazy TTL expiry
                self._store.pop(key, None)
                self._policy.remove(key)
                return None
            self._policy.key_accessed(key)
            return value

# ---- Driver / demo: business logic is NOT in here, it just exercises the API ----
if __name__ == "__main__":
    cache = Cache(capacity=2, policy=LRUPolicy())
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1          # 'a' now most-recent
    cache.put("c", 3)                   # capacity hit -> evicts LRU ('b')
    assert cache.get("b") is None
    assert cache.get("c") == 3
    print("LRU eviction OK")

    # Swap the policy with zero changes to Cache -> the extensibility win
    lfu = Cache(capacity=2, policy=LFUPolicy())
    lfu.put("x", 1); lfu.get("x"); lfu.get("x")   # x used 2x
    lfu.put("y", 2)                                # y used 1x
    lfu.put("z", 3)                                # evicts least-frequent ('y')
    assert lfu.get("y") is None and lfu.get("x") == 1
    print("LFU eviction OK")

    # TTL expiry
    ttl = Cache(capacity=2, policy=LRUPolicy())
    ttl.put("temp", 99, ttl_seconds=0.01)
    time.sleep(0.02)
    assert ttl.get("temp") is None
    print("TTL expiry OK")
```

**Why this scores well:** the happy path runs; `Cache` depends on the `EvictionPolicy` abstraction so a new policy is a new class (open/closed principle in action); TTL and capacity edge cases are handled; there's a demo with assertions; thread-safety is present but minimal (not gold-plated). If asked to add "FIFO eviction", you write one 6-line class and change nothing else — say that out loud.

---

## Practice drills (build each in a strict time-box, then diff against your instinct)

Do these *by actually writing running code*, not by whiteboarding. Aim for 60-90 min each, then cut it to 45.

1. **Splitwise / expense sharing** — add expenses (equal/exact/percent split — Strategy seam), show balances, simplify debts. (Reference object model: [low_level_design.md](./low_level_design.md).)
2. **Parking lot** — multiple vehicle types + spot types, park/unpark, pricing strategy, find nearest spot. (Reference: [low_level_design.md](./low_level_design.md).)
3. **In-memory key-value store with transactions** — `begin` / `commit` / `rollback`, nested transactions. (Great for showing a stack-of-maps design.)
4. **Rate limiter** — pluggable algorithm (token bucket / sliding window — Strategy seam). Ties to [classic_designs/01_rate_limiter.md](./classic_designs/01_rate_limiter.md).
5. **Snake & Ladder / board game** — dice, players, board with jumps, turn loop, win condition. (State + clean turn engine.)
6. **Logging framework** — pluggable sinks (console/file) + levels + a Chain-of-Responsibility on level. (Strategy + Observer.)
7. **Movie ticket booking** — seat hold with concurrency (no double-book), idempotent booking. Ties to [classic_designs/17_ticketmaster_booking.md](./classic_designs/17_ticketmaster_booking.md).

**Where to run them:** any local editor + `python3 file.py`, or an online IDE if the interview provides one. Practice in the environment you'll interview in (some Atlassian loops use a shared editor with no autocomplete — like Google's coding round).

---

## Pre-round checklist
- [ ] I have `python3` + a scratch file ready; I can run code in <5s.
- [ ] I default to **in-memory** storage (dict-backed repo class) and say so.
- [ ] I freeze scope out loud and get a nod before typing.
- [ ] I get a **running happy path by the halfway mark**, then deepen.
- [ ] I put the extension seam behind an interface (Strategy) and name it when I walk through.
- [ ] I add 2-3 assertions/tests and narrate the edge cases I chose to skip.
- [ ] I do NOT add a DB, framework, or 5 design patterns unless asked.

## Resources
- **Free:** "Machine Coding Round — how to prepare" walkthroughs: https://www.youtube.com/results?search_query=machine+coding+round+interview+preparation  |  Refactoring Guru (design patterns, free to read): https://refactoring.guru/design-patterns
- **Free:** SOLID principles refresher: https://www.youtube.com/results?search_query=SOLID+principles+explained
- **Paid (optional):** "Grokking the Low Level Design Interview Using OOD Principles" (DesignGurus): https://www.designgurus.io  (free alternative: build the 7 drills above and read Refactoring Guru).

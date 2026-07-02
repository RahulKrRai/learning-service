# 27 - Concurrency & Multithreading
> One-line: when a problem asks you to coordinate multiple threads — order their output, share a buffer, or protect shared state — reach for a lock + a condition variable (or a thread-safe queue), never a busy-wait.

> **Why this file exists:** Uber and Atlassian (and sometimes Google/Amazon) drop a live concurrency problem into the coding round — "implement a thread-safe bounded queue", "print these in order", "coordinate N threads". It's a distinct muscle from the other 26 patterns: correctness under interleaving, not algorithmic cleverness. This is your rusty spot with the highest surprise factor, so drill the templates until they're reflex.

## When to use it (recognition triggers)
- The prompt literally says **thread**, **concurrent**, **synchronize**, **at the same time**, **race condition**, or gives you method stubs that "will be called by different threads".
- You must **enforce an order** across threads that otherwise run freely (Print in Order, FooBar, Zero-Even-Odd).
- Multiple producers/consumers share a **bounded buffer** and must block when full/empty (Bounded Blocking Queue).
- A fixed **capacity / resource pool** must be respected (Building H2O — 2 H then 1 O; dining philosophers — forks).
- You're asked about **deadlock, starvation, livelock**, or "what happens if two threads call this simultaneously".

## Mental model
- **Three primitives cover ~95% of interview problems.** Know exactly when each applies:
  - **`Lock` (mutex):** mutual exclusion around a critical section. "Only one thread touches this at a time." Always use `with lock:` so it's released on exception.
  - **`Condition`:** *wait until a predicate is true, then proceed* — for ordering and producer/consumer. `cond.wait()` atomically releases the lock and sleeps; `cond.notify_all()` wakes waiters to re-check. **Always wait in a `while` loop**, never an `if` (spurious wakeups + the predicate may have flipped back).
  - **`Semaphore`:** a counter of permits — "at most N threads past this point." Perfect for capacity/ordering-by-signal (Print in Order becomes trivial with two semaphores).
- **The golden rule of `Condition`:** `while not predicate: cond.wait()`. Re-check the condition after every wake. This one line prevents most concurrency bugs.
- **Prefer `queue.Queue` when you can.** It's a *fully thread-safe* bounded blocking queue out of the box (internally a lock + two conditions). If the problem is "producer/consumer", the honest senior answer is often "use `queue.Queue`" — then show you can build it by hand when they ask.
- **Deadlock needs all four Coffman conditions**; break any one. The interview-friendly fix is **lock ordering**: every thread acquires locks in the same global order (by id), so no cycle can form. (Dining Philosophers = make one philosopher pick up forks in the opposite order, or use a semaphore capping diners at N-1.)
- **The Python GIL caveat — say this out loud, it signals seniority:** CPython's GIL means threads don't run Python bytecode in parallel, so threads help with **I/O-bound** work but not **CPU-bound** (use `multiprocessing` for that). *The synchronization logic you write is still correct and still required* — the GIL doesn't make your code thread-safe (a `+=` is still three non-atomic bytecodes). Interviewers want the correct locking regardless of GIL.

## Reusable template(s)
```python
import threading
from collections import deque

# ---- Template A: protect shared state (Lock) ----
class Counter:
    def __init__(self):
        self._n = 0
        self._lock = threading.Lock()
    def incr(self):
        with self._lock:          # released even if body raises
            self._n += 1          # NOT atomic without the lock

# ---- Template B: wait-for-condition (Condition) — the workhorse ----
class Gate:
    def __init__(self):
        self._cond = threading.Condition()
        self._open = False
    def wait_until_open(self):
        with self._cond:
            while not self._open:      # ALWAYS a while, never if
                self._cond.wait()      # releases lock, sleeps, re-acquires on wake
    def open(self):
        with self._cond:
            self._open = True
            self._cond.notify_all()    # wake everyone to re-check

# ---- Template C: bounded blocking queue by hand (two-condition pattern) ----
class BoundedQueue:
    def __init__(self, capacity):
        self._q = deque()
        self._cap = capacity
        self._cond = threading.Condition()
    def put(self, item):
        with self._cond:
            while len(self._q) == self._cap:   # full -> block producers
                self._cond.wait()
            self._q.append(item)
            self._cond.notify_all()            # a consumer may be waiting
    def get(self):
        with self._cond:
            while not self._q:                 # empty -> block consumers
                self._cond.wait()
            item = self._q.popleft()
            self._cond.notify_all()            # a producer may be waiting
            return item

# ---- Template D: cap concurrent access (Semaphore) ----
sem = threading.Semaphore(3)     # at most 3 threads in the pool at once
def use_resource():
    with sem:                    # acquire a permit (blocks if 0 left); release on exit
        do_work()

# ---- Template E: ordering with semaphores (cleanest for Print in Order) ----
class Foo:
    def __init__(self):
        self._second = threading.Semaphore(0)   # start locked
        self._third  = threading.Semaphore(0)
    def first(self, printFirst):
        printFirst(); self._second.release()     # unlock second
    def second(self, printSecond):
        self._second.acquire(); printSecond(); self._third.release()
    def third(self, printThird):
        self._third.acquire(); printThird()
```

## Complexity profile
- Concurrency problems are graded on **correctness under all interleavings**, not Big-O. State it as: each operation is O(1) work under the lock; the lock serializes the critical section.
- The trap to name out loud: **holding a lock while doing slow work** (I/O inside `with lock:`) kills throughput — keep critical sections tiny. And **busy-waiting** (`while not ready: pass`) burns a core — always block on a `Condition`/`Semaphore` instead.

## Curated problems (easy -> hard)

### 1. Print in Order  -  Easy
- **Problem:** Three threads call `first()`, `second()`, `third()` in arbitrary order; guarantee output is always "first second third".
- **Practice (free):** https://leetcode.com/problems/print-in-order/
- **Video (free):** https://www.youtube.com/results?search_query=leetcode+print+in+order+concurrency
- **Idea:** Two semaphores initialized to 0 act as gates; each method releases the next. (Template E above.)
- **Key insight / gotcha:** Semaphores starting at 0 are the simplest "happens-before" signal — no shared flag, no condition loop needed. A `Condition` + two boolean flags also works but is more code.
- **Follow-up:** "Do it without semaphores" -> use a `Condition` with an integer `stage` and `while stage != k: cond.wait()`.

### 2. Print FooBar Alternately  -  Medium
- **Problem:** Two threads, one prints "foo", one prints "bar", n times each; output must be "foobar" repeated, strictly alternating.
- **Practice (free):** https://leetcode.com/problems/print-foobar-alternately/
- **Video (free):** https://www.youtube.com/results?search_query=leetcode+print+foobar+alternately
- **Idea:** Two semaphores ping-pong control: `foo` starts unlocked (permit=1), `bar` locked (permit=0); each release hands the turn to the other.
- **Key insight / gotcha:** Alternation = a single permit bouncing between two semaphores. With a `Condition` you'd use a boolean `foo_turn` and `notify_all` each flip — heavier but also fine.
- **Follow-up:** "Generalize to k threads round-robin (Zero-Even-Odd style)" -> array of semaphores, thread i releases thread (i+1) % k.

### 3. Design Bounded Blocking Queue  -  Medium
- **Problem:** Implement `enqueue`/`dequeue`/`size` for a queue of fixed capacity; `enqueue` blocks when full, `dequeue` blocks when empty; thread-safe for many producers/consumers.
- **Practice (free):** https://leetcode.com/problems/design-bounded-blocking-queue/
- **Video (free):** https://www.youtube.com/results?search_query=leetcode+design+bounded+blocking+queue
- **Idea:** Template C exactly — one `Condition`, guard `put` on `len == cap`, guard `get` on empty, `notify_all` after every mutation.
- **Key insight / gotcha:** Two separate semaphores (one counting empty slots, one counting items) is the *cleaner* production pattern and avoids waking the wrong side; the single-condition version is easier to reason about live. Know both. **The honest answer:** "In real code I'd just use `queue.Queue(maxsize=cap)`."
- **Follow-up:** "Why `notify_all` not `notify`?" With a single condition, `notify` might wake a producer when only consumers can proceed -> lost wakeup. `notify_all` is safe; two-semaphore or two-condition designs let you use targeted signaling.

### 4. The Dining Philosophers  -  Medium
- **Problem:** Five philosophers, five forks; each needs both neighbouring forks to eat. Prevent deadlock and starvation.
- **Practice (free):** https://leetcode.com/problems/the-dining-philosophers/
- **Video (free):** https://www.youtube.com/results?search_query=dining+philosophers+problem+solution
- **Idea:** Break the deadlock cycle. Simplest: a semaphore that permits at most **4** philosophers to reach for forks at once (guarantees at least one can get both). Alternative: **lock ordering** — always pick up the lower-numbered fork first.
- **Key insight / gotcha:** Naïve "pick up left, then right" deadlocks when all five grab left simultaneously (circular wait). Name the four Coffman conditions and say which one you're breaking.
- **Follow-up:** "Avoid starvation too" -> the capacity-of-N-1 semaphore gives progress; strict fairness needs a queue/ticket order on forks.

### 5. Building H2O  -  Medium
- **Problem:** Threads call `hydrogen()` or `oxygen()`; let them through only in groups forming one water molecule (2 H + 1 O) before any next molecule proceeds.
- **Practice (free):** https://leetcode.com/problems/building-h2o/
- **Video (free):** https://www.youtube.com/results?search_query=leetcode+building+h2o+concurrency
- **Idea:** Two semaphores as quotas — `hydrogen` semaphore = 2 permits, `oxygen` = 1 permit — plus a `Barrier(3)` so all three bond together before releasing the permits for the next molecule.
- **Key insight / gotcha:** `threading.Barrier(3)` is the elegant tool: the first two H and one O all `wait()` at the barrier, then release together. Resetting the semaphores after the barrier lets the next molecule form.
- **Follow-up:** "No Barrier available" -> count H's and O's under a lock/condition and release exactly when a full group is present.

### 6. Web Crawler Multithreaded  -  Medium/Hard
- **Problem:** Crawl all URLs under the same hostname as the start URL, using a thread pool; each URL visited once.
- **Practice (free):** https://leetcode.com/problems/web-crawler-multithreaded/
- **Video (free):** https://www.youtube.com/results?search_query=leetcode+web+crawler+multithreaded
- **Idea:** A thread-safe `visited` set (behind a lock) + a work queue; worker threads pull URLs, fetch, filter by hostname, and enqueue unseen links. Join when the queue drains.
- **Key insight / gotcha:** The termination condition is the hard part — you can't just "queue empty" because a worker might still be about to add more. Use `queue.Queue` with `task_done()`/`join()`, or an in-flight counter. This problem is the bridge from concurrency toy to real systems (mirrors the [Web Crawler system design](../../02_system_design/classic_designs/14_web_crawler.md)).
- **Follow-up:** "Politeness / rate-limit per host" -> per-host semaphore or delay; ties directly into the SD version's frontier + politeness discussion.

## Self-rating checklist
- [ ] I can recognise a concurrency problem in <15s and reach for lock / condition / semaphore correctly
- [ ] I write `while not predicate: cond.wait()` reflexively — never `if`
- [ ] I can implement a bounded blocking queue from memory (single-condition AND two-semaphore)
- [ ] I can explain and fix deadlock via lock ordering or a capacity semaphore
- [ ] I can state the GIL caveat crisply (threads = I/O-bound; locking still required)
- [ ] Print in Order — 🔴 / 🟡 / 🟢
- [ ] Print FooBar Alternately — 🔴 / 🟡 / 🟢
- [ ] Design Bounded Blocking Queue — 🔴 / 🟡 / 🟢
- [ ] The Dining Philosophers — 🔴 / 🟡 / 🟢
- [ ] Building H2O — 🔴 / 🟡 / 🟢
- [ ] Web Crawler Multithreaded — 🔴 / 🟡 / 🟢

## Resources
- **Free:** LeetCode Concurrency problem set: https://leetcode.com/problem-list/concurrency/  |  Python `threading` docs: https://docs.python.org/3/library/threading.html  |  Python `queue` docs (thread-safe queues): https://docs.python.org/3/library/queue.html
- **Concept refresher (free):** "Deadlock & the Dining Philosophers" — https://www.youtube.com/results?search_query=dining+philosophers+deadlock+coffman+conditions
- **Paid (optional):** "Grokking Multithreading & Concurrency for Coding Interviews" (DesignGurus): https://www.designgurus.io  (free alternative: the LeetCode concurrency list above covers the same problems with community solutions).

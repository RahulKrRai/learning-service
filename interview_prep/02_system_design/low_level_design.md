# Low-Level Design (Object Modeling / Machine Coding)

> One-line: when the prompt is "design a *system* — give me the classes" (parking lot, elevator, Splitwise), you win on **clean entities, the right design patterns, and driving the conversation** — not on algorithms or distributed-systems scale.

> **Where this sits.** This is the *object-modeling* sibling of two other files:
> - For **distributed / HLD** ("design Twitter at scale, QPS, sharding") → [README.md](./README.md) + the classic designs.
> - For **data-structure coding LLD** (LRU/LFU/iterators, O(1) contracts) → [../01_dsa/patterns/22_object_oriented_design.md](../01_dsa/patterns/22_object_oriented_design.md).
> - **This file** is the in-between: "model a real-world system as classes." Discussion + sketch, occasionally a 45–90 min machine-coding build.

> **Who asks it (your targets).** 🔥 **Atlassian** and **bank VP loops** (Goldman/JPMorgan) lean on object modeling. Amazon and Uber sometimes slot it into a coding round. **Google does essentially zero machine-coding** — don't over-invest for Google. Confluent leads with distributed HLD. So: study this for Atlassian + banks, skim for Amazon/Uber, skip for Google prep.

---

## When to use it (recognition triggers)
- The prompt is a **real-world system**, not a data structure: "design a parking lot / elevator / vending machine / Splitwise / movie-booking / chess / file system."
- They want **classes, responsibilities, and relationships** — "walk me through your class diagram", "what are the entities", "which design pattern fits here".
- The scale is **single-machine, in-memory** — no QPS math, no sharding. If they wanted distributed scale they'd say "millions of users"; here it's "model the domain correctly."
- A **machine-coding** variant: 45–90 min to produce *compiling, runnable* code with a `main`/driver that exercises the operations. Graded on structure, extensibility, and that it actually runs.

---

## The universal LLD attack framework (5 steps — say them out loud)

1. **Clarify scope & requirements (3–5 min).** Pin functional requirements ("multiple floors? vehicle sizes? payment?") and *explicitly defer* the rest ("I'll assume single building, ignore auth for now — flag me if you want it"). Write a short bullet list of in-scope operations. **This is graded** — jumping to classes without scoping is the #1 junior tell.
2. **Identify the entities (the nouns).** Underline the nouns in the requirements: *parking lot, level, spot, vehicle, ticket*. Each becomes a class. One class = one responsibility.
3. **Define relationships & multiplicity.** Has-a (composition: `ParkingLot` *has* `Level`s), is-a (inheritance: `Car` *is-a* `Vehicle`), and cardinality (1 lot → many levels). Draw boxes and arrows.
4. **Design the API + enums + invariants.** Write method signatures first (`park(vehicle) -> Ticket | None`), enums for fixed state sets (`VehicleSize`, `SpotType`), and state the invariants ("a spot is either free or holds exactly one vehicle"). *Then* fill bodies.
5. **Name the patterns & trade-offs.** Call out Strategy/Factory/State/Observer where they fit (and *only* where they fit). Discuss concurrency, extensibility ("to add a new vehicle type I only touch the factory"), and what you deliberately left out.

> **Atlassian/bank tip:** start with the *simplest correct version that runs*, then extend. They add requirements mid-round on purpose ("now add motorcycles", "now charge by the hour") — your two-layer design (public API over private helpers) should absorb each as a *small* change, not a rewrite.

---

## Design-pattern cheat sheet (the 6 that actually recur in LLD)

| Pattern | One-liner | Classic LLD use |
|---|---|---|
| **Strategy** | Swap an algorithm behind an interface at runtime | Parking fee (flat/hourly/tiered); Splitwise split (equal/exact/percent) |
| **Factory** | Centralize object creation; callers don't `new` concrete types | `VehicleFactory.create(type)`; piece creation in chess |
| **State** | Object changes behavior as its internal state changes | Vending machine (idle→has-money→dispensing); elevator (moving/idle/door-open) |
| **Observer** | Subscribers get notified on state change | Notify displays when a parking level fills; price-drop alerts |
| **Singleton** | Exactly one instance, global access | The `ParkingLot`/`Bank` root object (use sparingly — it hides dependencies) |
| **Decorator** | Wrap an object to add behavior without subclassing | Add toppings to a pizza/coffee; add features to a `Notification` |

> Say the pattern's *name* when you use it — it signals you've designed before. Never force one where a plain method does. "I'd use Strategy for pricing so a new fee model is a new class, not an `if/elif` edit" is a senior sentence.

---

## Worked design 1 — Parking Lot  (the canonical opener)

**Scope to confirm:** multiple levels; vehicle sizes (motorcycle/car/truck); a small vehicle may take a larger spot but not vice-versa; issue a ticket on entry, charge by time on exit; single entrance for now.

**Entities & responsibilities (one class, one job):**
- `ParkingLot` (root) — owns levels; API `park(vehicle) -> Ticket | None`, `unpark(ticket) -> fee`. Delegates spot-finding down.
- `Level` — holds `ParkingSpot`s; tracks free spots **per size** for O(1) assignment; `find_spot(size)`.
- `ParkingSpot` — one stall: `spot_id`, `size`, `is_free`, `assign(vehicle)`, `vacate()`.
- `Vehicle` (base) → `Motorcycle`, `Car`, `Truck`, each carrying a `VehicleSize`.
- `Ticket` — `ticket_id`, `spot`, `entry_time`; basis for the fee.
- `FeeStrategy` (interface) → `FlatFee`, `HourlyFee` — **Strategy pattern** so a new pricing model is a new class.

**Enums:** `VehicleSize {MOTORCYCLE, COMPACT, LARGE}`, `SpotType {MOTORCYCLE, COMPACT, LARGE}`, `TicketStatus {ACTIVE, PAID}`.

```python
from enum import Enum
from collections import defaultdict

class Size(Enum):                       # one ordering: a vehicle fits a spot of >= its size
    MOTORCYCLE, COMPACT, LARGE = 1, 2, 3

class Vehicle:
    def __init__(self, plate: str, size: Size):
        self.plate, self.size = plate, size

class Ticket:
    def __init__(self, ticket_id: int, spot_id: str, entry_time: int):
        self.ticket_id, self.spot_id, self.entry_time = ticket_id, spot_id, entry_time

class FeeStrategy:                      # Strategy: swap pricing without touching the lot
    def compute(self, entry: int, exit: int) -> int:
        raise NotImplementedError

class HourlyFee(FeeStrategy):
    def __init__(self, rate: int): self.rate = rate
    def compute(self, entry: int, exit: int) -> int:
        hours = max(1, (exit - entry + 3599) // 3600)   # round up, min 1 hour
        return hours * self.rate

class Level:
    def __init__(self, level_id: int, spots_by_size: dict):
        self.level_id = level_id
        # free spot ids bucketed by size => O(1) find/assign, no scanning stalls
        self._free = {s: list(ids) for s, ids in spots_by_size.items()}
        self._occupied = {}                              # spot_id -> Vehicle

    def find_and_assign(self, vehicle: Vehicle):
        for s in Size:                                   # try exact size, then larger
            if s.value >= vehicle.size.value and self._free.get(s):
                spot_id = self._free[s].pop()
                self._occupied[spot_id] = vehicle
                return spot_id
        return None

    def vacate(self, spot_id: str, size: Size):
        self._occupied.pop(spot_id, None)
        self._free.setdefault(size, []).append(spot_id)

class ParkingLot:
    def __init__(self, levels: list, fee: FeeStrategy):
        self._levels = levels
        self._fee = fee
        self._next_ticket = 0
        self._tickets = {}                               # ticket_id -> (Ticket, Level, size)

    def park(self, vehicle: Vehicle, now: int):
        for level in self._levels:
            spot_id = level.find_and_assign(vehicle)
            if spot_id is not None:
                t = Ticket(self._next_ticket, spot_id, now)
                self._tickets[t.ticket_id] = (t, level, vehicle.size)
                self._next_ticket += 1
                return t
        return None                                      # lot full

    def unpark(self, ticket_id: int, now: int) -> int:
        t, level, size = self._tickets.pop(ticket_id)
        level.vacate(t.spot_id, size)
        return self._fee.compute(t.entry_time, now)

if __name__ == "__main__":
    lot = ParkingLot(
        [Level(0, {Size.COMPACT: ["C0", "C1"], Size.LARGE: ["L0"]})],
        HourlyFee(rate=40),
    )
    car = Vehicle("KA01", Size.COMPACT)
    tk = lot.park(car, now=0)
    print("parked at", tk.spot_id)                       # parked at C1
    print("fee:", lot.unpark(tk.ticket_id, now=7200))    # fee: 80  (2 hours * 40)
```

**Trade-offs to narrate:** per-size free-list gives **O(1)** assignment vs O(n) scanning; small-in-large allowed via the `>=` size check; **concurrency** — two cars racing for the last spot needs a lock or atomic pop (here `list.pop` would need a `threading.Lock` in a real multi-threaded lot); Strategy for pricing, Factory for vehicle creation are the bits that read as design maturity.

**Common follow-ups:** multiple entrances (per-entrance spot reservation); EV charging spots (a new `SpotType` + a feature flag on the spot); lost-ticket flat fee; reserved/handicap spots (priority buckets).

---

## Worked design 2 — Elevator System  (the State-pattern showcase)

**Scope to confirm:** N elevators, M floors; external requests (floor + up/down) and internal requests (target floor); goal is a reasonable scheduling policy, not the perfect one.

**Entities:**
- `Elevator` — `current_floor`, `direction`, `state`, two sorted request sets (`up_stops`, `down_stops`); `step()` advances one tick.
- `Direction {UP, DOWN, IDLE}` and `ElevatorState {MOVING, STOPPED, DOOR_OPEN, IDLE}` enums (this is where **State** lives — behavior on `step()` depends on state).
- `Request` — `(source_floor, target_floor)` for internal; `(floor, direction)` for external (hall call).
- `ElevatorController` (the scheduler) — owns all elevators; `dispatch(request)` picks the best elevator.

**The interesting decision — dispatch policy.** State it explicitly:
- **Nearest-car / SCAN ("elevator algorithm"):** an elevator moving up keeps serving up-stops in increasing floor order until none remain above, then reverses. Assign a hall call to the elevator that will pass that floor soonest *in the matching direction*. This is the senior answer — it avoids the naive "send the closest idle car" which causes starvation and zig-zagging.

```python
from enum import Enum
import heapq

class Direction(Enum):
    UP, DOWN, IDLE = 1, -1, 0

class Elevator:
    def __init__(self, eid: int):
        self.eid = eid
        self.floor = 0
        self.direction = Direction.IDLE
        self._up = []          # min-heap of stops above (served ascending)
        self._down = []        # max-heap (negated) of stops below (served descending)

    def add_stop(self, floor: int):
        if floor > self.floor:
            heapq.heappush(self._up, floor)
        elif floor < self.floor:
            heapq.heappush(self._down, -floor)
        # floor == current: door opens this tick, nothing to schedule

    def step(self):
        """Advance one floor toward the next stop in the current direction (SCAN)."""
        if self.direction == Direction.UP or (self.direction == Direction.IDLE and self._up):
            self.direction = Direction.UP
            if self._up:
                target = self._up[0]
                self.floor += 1 if self.floor < target else 0
                if self.floor == target:
                    heapq.heappop(self._up)      # arrived: open doors (omitted)
            if not self._up:                     # nothing above => flip
                self.direction = Direction.DOWN if self._down else Direction.IDLE
        elif self.direction == Direction.DOWN and self._down:
            target = -self._down[0]
            self.floor -= 1 if self.floor > target else 0
            if self.floor == target:
                heapq.heappop(self._down)
            if not self._down:
                self.direction = Direction.UP if self._up else Direction.IDLE

class ElevatorController:
    def __init__(self, n: int):
        self._elevators = [Elevator(i) for i in range(n)]

    def dispatch(self, floor: int):
        # pick the elevator whose current position is closest (simplified nearest-car)
        best = min(self._elevators, key=lambda e: abs(e.floor - floor))
        best.add_stop(floor)
        return best.eid

if __name__ == "__main__":
    ctrl = ElevatorController(n=2)
    print("assigned elevator", ctrl.dispatch(5))   # assigned elevator 0
```

**Trade-offs to narrate:** SCAN vs nearest-idle (starvation); separate up/down stop sets so a car doesn't reverse mid-trip; how `State` would make `step()` a `self.state.handle(self)` call instead of `if/elif` (cleaner for door-open/maintenance states); fairness vs throughput.

**Follow-ups:** express elevators (only certain floors), maintenance state, weight limits, peak-hour zoning.

---

## Worked design 3 — Splitwise / Expense Sharing  (the Strategy + graph one)

**Scope:** users in groups; add an expense paid by one, split among several (equally / exact amounts / percentages); show net balances; "settle up" simplification.

**Entities:**
- `User` — `user_id`, `name`.
- `Expense` — `paid_by`, `amount`, `participants`, a `SplitStrategy`.
- `SplitStrategy` (interface) → `EqualSplit`, `ExactSplit`, `PercentSplit` — **Strategy pattern**, the heart of this design.
- `Split` — `(user, amount_owed)` produced by the strategy.
- `ExpenseManager` — holds a balance sheet: `balances[a][b]` = how much `a` owes `b`.

```python
class SplitStrategy:
    def split(self, amount: float, participants: list, meta=None) -> dict:
        raise NotImplementedError

class EqualSplit(SplitStrategy):
    def split(self, amount, participants, meta=None):
        share = round(amount / len(participants), 2)
        return {u: share for u in participants}

class ExactSplit(SplitStrategy):
    def split(self, amount, participants, meta=None):   # meta = {user: exact_amount}
        assert abs(sum(meta.values()) - amount) < 1e-6, "exact splits must sum to total"
        return dict(meta)

class ExpenseManager:
    def __init__(self):
        from collections import defaultdict
        self._owes = defaultdict(lambda: defaultdict(float))  # owes[a][b] = a owes b

    def add_expense(self, paid_by, amount, participants, strategy: SplitStrategy, meta=None):
        shares = strategy.split(amount, participants, meta)
        for user, owed in shares.items():
            if user == paid_by:
                continue
            self._owes[user][paid_by] += owed            # user now owes the payer their share

    def balance(self, a, b) -> float:
        return round(self._owes[a][b] - self._owes[b][a], 2)   # net of mutual debts

if __name__ == "__main__":
    mgr = ExpenseManager()
    mgr.add_expense("alice", 900, ["alice", "bob", "carol"], EqualSplit())
    print("bob owes alice:", mgr.balance("bob", "alice"))    # bob owes alice: 300.0
```

**Trade-offs to narrate:** Strategy makes a new split type a new class, not an `if/elif`; netting mutual debts (`a` owes `b` minus `b` owes `a`); **debt simplification** as a follow-up — minimize the number of transactions by greedily matching the biggest creditor with the biggest debtor (this is the algorithmic depth they probe for). Floating point → store **integer paise/cents** in production.

**Follow-ups:** simplify debts across a group (min cash flow); multi-currency; group vs friend-level balances; concurrency on the balance sheet.

---

## Worked design 4 — Vending Machine  (the textbook State machine)

**Scope:** select product, insert coins, dispense + change, refund. This is *the* problem to show off the **State pattern**.

**States** (`State {IDLE, ITEM_SELECTED, HAS_MONEY, DISPENSING}`): each state defines what the legal transitions are. Inserting money in `IDLE` is rejected; selecting in `HAS_MONEY` is rejected. Behavior lives in the state object, so `VendingMachine` just delegates.

**Entities:** `VendingMachine` (context, holds `current_state`, `inventory`, `balance`), `State` (interface: `select_item`, `insert_money`, `dispense`), concrete states, `Inventory` (`product -> (price, count)`).

```python
class VendingMachine:
    def __init__(self, inventory: dict):       # inventory: {name: [price, count]}
        self._inv = inventory
        self._state = "IDLE"
        self._selected = None
        self._balance = 0

    def select(self, name):
        if self._state != "IDLE" or self._inv.get(name, [0, 0])[1] <= 0:
            return "rejected"
        self._selected, self._state = name, "ITEM_SELECTED"
        return f"selected {name}, price {self._inv[name][0]}"

    def insert(self, amount):
        if self._state not in ("ITEM_SELECTED", "HAS_MONEY"):
            return "rejected"
        self._balance += amount
        self._state = "HAS_MONEY"
        return f"balance {self._balance}"

    def dispense(self):
        if self._state != "HAS_MONEY":
            return "rejected"
        price = self._inv[self._selected][0]
        if self._balance < price:
            return f"need {price - self._balance} more"
        self._inv[self._selected][1] -= 1
        change = self._balance - price
        item, self._selected, self._balance, self._state = self._selected, None, 0, "IDLE"
        return f"dispensed {item}, change {change}"

if __name__ == "__main__":
    vm = VendingMachine({"coke": [50, 2]})
    print(vm.select("coke"))     # selected coke, price 50
    print(vm.insert(30))         # balance 30
    print(vm.insert(40))         # balance 70
    print(vm.dispense())         # dispensed coke, change 20
```

**Trade-offs to narrate:** the `if self._state != ...` guards *are* the state machine — in a fuller design each state is its own class implementing a `State` interface, so adding a "MAINTENANCE" state touches no existing state's code (open/closed principle); change-making is a coin-denomination greedy/DP sub-problem; concurrency if two buyers hit the same machine.

**Follow-ups:** exact-change-only mode; multiple simultaneous selections; restocking; the coin-change algorithm for optimal change.

---

## Worked design 5 — Movie Ticket Booking (BookMyShow)  (the concurrency one)

**Scope:** browse shows; **select & hold seats**; pay within a timeout; release on timeout. The whole point of this problem is **seat-locking under concurrency** — two users must not book the same seat.

**Entities:** `Movie`, `Theatre`, `Screen`, `Show` (movie × screen × time), `Seat`, `SeatStatus {AVAILABLE, HELD, BOOKED}`, `Booking`, `BookingService`.

**The crux — preventing double-booking.** State the options:
1. **Pessimistic lock / hold with TTL:** mark seats `HELD` with an expiry when the user selects; only that user can confirm before TTL; a sweeper (or lazy check) releases expired holds. *This is the expected answer.*
2. Optimistic: let both proceed, detect the conflict at confirm with a version check / `SELECT ... FOR UPDATE`, fail the loser.

```python
class Show:
    def __init__(self, show_id, seats):
        self.show_id = show_id
        self._status = {s: "AVAILABLE" for s in seats}   # seat -> AVAILABLE/HELD/BOOKED
        self._hold_expiry = {}                            # seat -> expiry timestamp

    def hold(self, seats, user, now, ttl=300):
        # all-or-nothing: verify every requested seat is free first
        for s in seats:
            free = self._status.get(s) == "AVAILABLE"
            expired = self._status.get(s) == "HELD" and self._hold_expiry.get(s, 0) <= now
            if not (free or expired):
                return False                              # someone else holds/booked it
        for s in seats:
            self._status[s] = "HELD"
            self._hold_expiry[s] = now + ttl
        return True

    def confirm(self, seats, now):
        for s in seats:                                   # holds must still be valid
            if self._status.get(s) != "HELD" or self._hold_expiry.get(s, 0) <= now:
                return False
        for s in seats:
            self._status[s] = "BOOKED"
            self._hold_expiry.pop(s, None)
        return True

if __name__ == "__main__":
    show = Show("s1", ["A1", "A2", "A3"])
    print(show.hold(["A1", "A2"], "alice", now=0))   # True
    print(show.hold(["A2"], "bob", now=10))          # False (alice holds A2)
    print(show.confirm(["A1", "A2"], now=20))        # True
```

**Trade-offs to narrate:** the **all-or-nothing hold** (check all seats free *before* mutating any) avoids a partial hold; TTL release so abandoned carts don't lock seats forever; in a distributed system this hold lives in **Redis with `SET NX` + TTL** or a DB row lock — say that, it bridges LLD to HLD; idempotent confirm so a retried payment doesn't double-book.

**Follow-ups:** seat-map adjacency ("3 seats together"); payment-failure rollback; surge/dynamic pricing (Strategy again); waitlist.

---

## Concurrency in LLD — the one paragraph to have ready
Most LLD prompts are single-threaded until the interviewer asks "what if two users do this at once?" Have this ready: **identify the shared mutable state** (the free-spot list, the seat map, the balance sheet), then pick the cheapest correct guard — a `threading.Lock` around the critical section for in-process; an atomic compare-and-set / DB row lock / `Redis SETNX`+TTL for cross-process. Name the trade-off: **coarse lock = simple but contended; fine-grained/sharded locks = scalable but deadlock-prone.** Prefer **immutable** objects and **all-or-nothing** mutations (hold all seats or none) to shrink the critical section.

---

## Self-rating checklist
- [ ] I can run the 5-step framework (scope → entities → relationships → API+enums → patterns) in <2 min on any prompt
- [ ] I can name when each of the 6 patterns applies (Strategy/Factory/State/Observer/Singleton/Decorator) — and when *not* to force one
- [ ] Parking Lot — 🔴 rusty / 🟡 ok / 🟢 fast
- [ ] Elevator (SCAN dispatch + State) — 🔴 / 🟡 / 🟢
- [ ] Splitwise (Strategy splits + debt netting) — 🔴 / 🟡 / 🟢
- [ ] Vending Machine (State machine) — 🔴 / 🟡 / 🟢
- [ ] Movie Booking (seat hold + TTL, concurrency) — 🔴 / 🟡 / 🟢
- [ ] I can give the concurrency paragraph (shared state → lock → trade-off) for any of them

## Resources
- **Free:**
  - System Design Primer — OOD section (parking lot, etc.): https://github.com/donnemartin/system-design-primer
  - "Low Level Design" playlists (parking lot / elevator / Splitwise walkthroughs): https://www.youtube.com/results?search_query=low+level+design+interview+parking+lot+elevator
  - Refactoring.Guru design-patterns catalogue (the 6 above, with diagrams): https://refactoring.guru/design-patterns
  - `awesome-low-level-design` GitHub repo (problem list + solutions): https://github.com/ashishps1/awesome-low-level-design
- **Paid (optional):**
  - DesignGurus "Grokking the Low Level Design Interview": https://www.designgurus.io  *(free alternative: the System Design Primer OOD section + the awesome-low-level-design repo cover the same ground.)*
  - "Head First Design Patterns" — patterns deep-dive  *(free alternative: refactoring.guru, linked above.)*

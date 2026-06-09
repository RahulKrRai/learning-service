# My System-Design Framework (in your own words)

> Write your own version of the interview framework here, from memory, until you can run it without notes.
> Canonical reference to check yourself against: [framework_and_estimation.md](./framework_and_estimation.md).
> Owning *one* repeatable framework is what keeps you calm in the room.

---

## My 7-step loop (fill in your own one-liners + time budget)

1. **Clarify requirements** (~5 min) — functional + non-functional; ask 2-3 sharp questions. _your note:_
2. **Estimate scale** (~3 min) — QPS, storage, bandwidth; show the napkin math. _your note:_
3. **API design** — key endpoints/RPCs. _your note:_
4. **Data model** — entities, keys, the partition/shard key and why. _your note:_
5. **High-level architecture** — boxes & arrows; walk the request path. _your note:_
6. **Deep dive (1-2 components)** — the real engineering: consistency, hotspots, idempotency, fan-out. _your note:_
7. **Bottlenecks, failure modes & trade-offs** — what breaks at 10x; name trade-offs explicitly. _your note:_

## My personal reminders (what *you* tend to forget)
- [ ] State numbers out loud.
- [ ] Name the trade-off, don't just pick a side.
- [ ] Lead the conversation — don't wait to be prompted (this is the L5/Senior bar).
- [ ] _add your own after each mock..._

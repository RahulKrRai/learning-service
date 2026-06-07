# System Design Hub

> System design is your strongest pillar — you have real production systems at 10M+ records to draw on. Own it.

## The Interview Framework (45 min)

| Step | Time | What you do |
|------|------|-------------|
| 1. Clarify requirements | ~3 min | Functional vs non-functional; ask 2-3 scoped questions |
| 2. Back-of-envelope estimation | ~3 min | QPS, storage, bandwidth — show your arithmetic |
| 3. API design | ~4 min | Key endpoints, request/response sketches |
| 4. High-level architecture | ~8 min | ASCII diagram + request flow walkthrough |
| 5. Data model | ~5 min | Tables/keys, partitioning strategy |
| 6. Deep dives (1-2 components) | ~15 min | The real engineering — consistency, fan-out, hotspots |
| 7. Bottlenecks & trade-offs | ~5 min | What breaks at 10x; name CAP/consistency choices explicitly |
| 8. Failure modes | ~2 min | What fails, how you detect it, how you recover |

See [framework_and_estimation.md](./framework_and_estimation.md) for the full framework + estimation cheat sheet.
See [fundamentals.md](./fundamentals.md) for building-block references (caching, Kafka, sharding, etc.).

---

## Your Edge

You have shipped production systems at scale. When you say "at Logward we ingested 10M+ container tracking events with multi-tenant isolation," that is a real design story — not a textbook answer. Lead with your production experience, then pivot to "at 10x scale, here's what I'd change."

---

## Designs

### Your 4 Home Designs (memorize cold — these are yours)

| File | System | Why it's on your list |
|------|--------|----------------------|
| [1_container_tracking_platform.md](./project_designs/1_container_tracking_platform.md) | Real-time container/shipment tracking | Logward — 10M+ records, multi-tenant, event-driven |
| [2_multitenant_trigger_service.md](./project_designs/2_multitenant_trigger_service.md) | Multi-tenant trigger & notification service | Logward — -60% latency, your biggest architecture win |
| [3_payment_links_reconciliation.md](./project_designs/3_payment_links_reconciliation.md) | Payment link + reconciliation system | 56 AI / Razorpay — -70% manual effort |
| [4_autopay_recurring_scheduler.md](./project_designs/4_autopay_recurring_scheduler.md) | Recurring payment / Autopay scheduler | 56 AI Autopay — -30% manual intervention |

### 8 Classic Designs (competent and fast)

| File | System | Key depth |
|------|--------|-----------|
| [01_rate_limiter.md](./classic_designs/01_rate_limiter.md) | Rate Limiter | Token bucket vs sliding window, distributed Redis |
| [02_distributed_cache.md](./classic_designs/02_distributed_cache.md) | Distributed Cache | Consistent hashing, eviction, hot keys |
| [03_url_shortener.md](./classic_designs/03_url_shortener.md) | URL Shortener | Key generation, collision, read-heavy scaling |
| [04_news_feed_fanout.md](./classic_designs/04_news_feed_fanout.md) | News Feed / Fan-out | Write vs read fan-out, celebrity problem |
| [05_typeahead_autocomplete.md](./classic_designs/05_typeahead_autocomplete.md) | Typeahead Autocomplete | Trie at scale, top-K per prefix |
| [06_distributed_message_log_kafka.md](./classic_designs/06_distributed_message_log_kafka.md) | Distributed Message Log (Kafka) | **Confluent interview** — go deep |
| [07_ride_dispatch_matching.md](./classic_designs/07_ride_dispatch_matching.md) | Ride Dispatch / Matching | **Uber interview** — geospatial, matching |
| [08_distributed_job_scheduler.md](./classic_designs/08_distributed_job_scheduler.md) | Distributed Job Scheduler | Exactly-once, leader election, cron at scale |

---

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — comprehensive reference
- [ByteByteGo YouTube](https://www.youtube.com/results?search_query=bytebytego+system+design) — concise visual walkthroughs
- [Hello Interview](https://www.hellointerview.com) — structured interview practice
- [Confluent Engineering Blog](https://www.confluent.io/blog/) — Kafka in production
- [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/) — dispatch, geo, scale

**Paid (optional):**
- [ByteByteGo](https://bytebytego.com) — Alex Xu's book + newsletter
- [DesignGurus / Grokking the System Design Interview](https://www.designgurus.io)
- "Designing Data-Intensive Applications" by Martin Kleppmann — the authoritative book

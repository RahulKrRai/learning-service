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
See [low_level_design.md](./low_level_design.md) for **object-modeling / LLD** (parking lot, elevator, Splitwise, vending machine, movie booking) — the distinct round Atlassian and bank VP loops lean on. For data-structure LLD (LRU/LFU/iterators) see [../01_dsa/patterns/22_object_oriented_design.md](../01_dsa/patterns/22_object_oriented_design.md).
See [engineering_hygiene.md](./engineering_hygiene.md) for **operational maturity** — the 12-factor app, deploy/release patterns, observability, SLI/SLO/error budgets, resilience patterns, and a production-readiness checklist. Use it in the bottlenecks and failure-modes steps to signal you've actually operated software at scale.

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

### 8 Original Classic Designs (competent and fast)

| File | System | Key depth |
|------|--------|-----------|
| [01_rate_limiter.md](./classic_designs/01_rate_limiter.md) | Rate Limiter | Token bucket vs sliding window, distributed Redis |
| [02_distributed_cache.md](./classic_designs/02_distributed_cache.md) | Distributed Cache | Consistent hashing, eviction, hot keys |
| [03_url_shortener.md](./classic_designs/03_url_shortener.md) | URL Shortener / Pastebin | Key generation, collision, read-heavy scaling |
| [04_news_feed_fanout.md](./classic_designs/04_news_feed_fanout.md) | News Feed / Fan-out | Write vs read fan-out, celebrity problem |
| [05_typeahead_autocomplete.md](./classic_designs/05_typeahead_autocomplete.md) | Typeahead Autocomplete | Trie at scale, top-K per prefix |
| [06_distributed_message_log_kafka.md](./classic_designs/06_distributed_message_log_kafka.md) | Distributed Message Log (Kafka) | **Confluent interview** — go deep |
| [07_ride_dispatch_matching.md](./classic_designs/07_ride_dispatch_matching.md) | Ride Dispatch / Matching | **Uber interview** — geospatial, matching |
| [08_distributed_job_scheduler.md](./classic_designs/08_distributed_job_scheduler.md) | Distributed Job Scheduler | Exactly-once, leader election, cron at scale |

### 13 Grokking Designs (the canonical set — added to push breadth to 95%+)

> These cover the rest of the "Grokking the System Design Interview" question bank. Together with the 8 above and your 4 home designs, you'll rarely meet a prompt you haven't drilled. Free Grokking-equivalent links are in each file's Resources section; see also [../05_resources/master_resource_list.md](../05_resources/master_resource_list.md).

| File | System | Key depth | 🔥 for |
|------|--------|-----------|--------|
| [09_chat_messaging_whatsapp.md](./classic_designs/09_chat_messaging_whatsapp.md) | Chat (WhatsApp/Messenger) | WebSocket conn mgmt, delivery/read receipts, wide-column store | everyone |
| [10_twitter_timeline.md](./classic_designs/10_twitter_timeline.md) | Twitter (timeline + tweet) | Hybrid fan-out, tweet object, celebrity merge | Google/Uber/Amazon |
| [11_video_streaming_youtube.md](./classic_designs/11_video_streaming_youtube.md) | Video Streaming (YouTube/Netflix) | Transcoding pipeline, CDN, adaptive bitrate | Google/Amazon |
| [12_photo_sharing_instagram.md](./classic_designs/12_photo_sharing_instagram.md) | Instagram | Media pipeline, CDN, sharded counters | everyone |
| [13_file_storage_dropbox.md](./classic_designs/13_file_storage_dropbox.md) | File Storage (Dropbox/Drive) | Chunking + dedup, delta sync, conflict resolution | Google/Amazon/Atlassian |
| [14_web_crawler.md](./classic_designs/14_web_crawler.md) | Web Crawler | URL frontier + politeness, bloom-filter dedup | **Google** |
| [15_proximity_service_yelp.md](./classic_designs/15_proximity_service_yelp.md) | Proximity / Yelp / Nearby | Geohash vs quadtree vs S2, read-heavy search | Uber/Google |
| [16_notification_system.md](./classic_designs/16_notification_system.md) | Notification System | Multi-channel fan-out, retries/DLQ, rate limits | everyone (**your prod edge**) |
| [17_ticketmaster_booking.md](./classic_designs/17_ticketmaster_booking.md) | Ticketmaster / Booking | Seat-hold concurrency, no double-booking, idempotent pay | Amazon/Atlassian/banks |
| [18_unique_id_generator.md](./classic_designs/18_unique_id_generator.md) | Unique ID Generator | Snowflake bit layout, clock skew, range allocation | standalone Q |
| [19_collaborative_editor_google_docs.md](./classic_designs/19_collaborative_editor_google_docs.md) | Collaborative Editor (Docs/Confluence) | OT vs CRDT, real-time sync, op log | Google/**Atlassian** |
| [20_blob_store_s3.md](./classic_designs/20_blob_store_s3.md) | Blob Store (S3) | Metadata/data split, erasure coding, multipart | **Amazon** |
| [21_distributed_search.md](./classic_designs/21_distributed_search.md) | Distributed Search | Inverted index, NRT indexing, scatter-gather | Google/Amazon |

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

# Distributed Search / Full-Text Search (e.g. Twitter Search)

> Appears at: Google, Amazon (L6), plus any "search over a large corpus" framing (logs, products, documents). Tests inverted indexes, index sharding, scatter-gather, and near-real-time ingestion. This is full-text *ranked retrieval* — distinct from [05_typeahead_autocomplete.md](./05_typeahead_autocomplete.md), which is *prefix suggestion* (next-keystroke completions off a trie). Here a user types a full query and you return the top-K most *relevant* documents, ranked. Know the difference cold — interviewers probe it.

## 1. Requirements

**Functional:**
- Index documents (tweets) as they are created — searchable within seconds (near-real-time, NRT).
- Full-text query: `GET /search?q=world cup final` → ranked list of matching tweets.
- Boolean / phrase matching: multi-term AND by default; phrase queries (`"world cup"`).
- Ranking by relevance (term match) blended with recency and popularity (likes/retweets).
- Pagination: return results page by page (`from`/`size` or cursor).
- Filters: by author, language, time range.

**Non-functional:**
- Read-heavy: search QPS >> indexing QPS, but indexing is continuous and unbounded.
- Query latency < 200ms p99 — users abandon slow search.
- NRT: a tweet should be findable within ~1-5s of posting.
- Huge corpus: billions of documents; index does not fit on one machine → must shard.
- High availability for reads; eventual consistency on the index is acceptable.

**Clarifying questions:**
1. "How fresh must results be?" → seconds (NRT), not milliseconds. This rules out re-indexing the world synchronously.
2. "Top-K only, or full result set?" → top-K (paginated). You never materialize all matches.
3. "Ranking — pure relevance or blended?" → blended: text relevance + recency + engagement. Keep scoring pluggable.
4. "Are deletes/edits required?" → yes (deleted tweets must drop out). Handle via tombstones since segments are immutable.

## 2. Back-of-Envelope Estimation

```
Corpus:               500M tweets/day = ~5,800/sec avg, ~15,000/sec peak (indexing rate)
Search QPS:           Assume 1.5x tweet volume in searches → ~10,000 QPS avg, ~50,000 peak

Doc size on index:    tweet text ~200B + metadata (author, ts, lang, engagement) ~300B
Avg terms per tweet:  ~15 unique terms after tokenization/stopword removal

Inverted index size estimate (per day):
  postings = 500M docs x 15 terms = 7.5B postings/day
  each posting ~ docID(8B) + positions/freq(~8B) = 16B
  raw = 7.5B x 16B = 120 GB/day  (before compression)
  with delta+varint compression (~4-6x) → ~25 GB/day of index

Retention (90 days searchable):  25 GB/day x 90 ≈ 2.3 TB index → MUST shard
Number of shards:                target ~30-50 GB/shard → ~50-75 primary shards
Replication:                     x2 or x3 replicas for read QPS + HA → ~150 total shards

Query fan-out:                   scatter to all N primary shards, gather top-K from each
  with 50 shards, each query touches 50 nodes → tail latency dominated by slowest shard
```

Takeaway you say out loud: index size forces sharding; sharding forces scatter-gather; scatter-gather makes the **slowest shard** your latency, so replication and balanced shards matter.

## 3. API Design

```
# Search (the primary read path)
GET /api/v1/search?q=world+cup+final&from=0&size=20&sort=relevance&lang=en
→ 200 {
    total_hits: 12453,           # approximate is fine at scale
    took_ms: 47,
    results: [
      { doc_id, text, author, created_at, score, highlights: [...] },
      ...
    ],
    next_cursor: "..."           # prefer cursor over deep from/size offsets
  }

# Index a document (internal — called by the ingestion pipeline, not end users)
POST /internal/v1/index
Body: { doc_id, text, author_id, created_at, lang, engagement: {...} }
→ 202 Accepted   # buffered; searchable after next refresh, not synchronously

# Delete (tombstone — actual removal happens at segment merge)
DELETE /internal/v1/index/{doc_id}
→ 202 Accepted
```

Notes you mention: indexing is `202 Accepted` (async, NRT — not immediately searchable). Prefer **cursor pagination** over deep `from`/`size`: scatter-gather with `from=100000` forces every shard to return 100020 docs to the coordinator (deep-paging cost grows with offset).

## 4. High-Level Architecture

```
                          WRITE / INGESTION PATH
Tweet Service ──► Kafka topic "tweets" ──► Indexer workers (consumer group)
                  (see 06_distributed_                │
                   message_log_kafka.md)              │ tokenize, analyze,
                                                      │ route by hash(docID)
                                                      ▼
                                          ┌───────────────────────┐
                                          │  Index shard nodes     │
                                          │  (document-partitioned)│
                                          │  in-mem buffer → flush │
                                          │  → immutable segments  │
                                          └───────────────────────┘
                          READ / QUERY PATH                ▲
Client                                                     │
  │ GET /search?q=...                                      │
  ▼                                                        │
┌──────────────┐   ┌──────────────────┐                    │
│ Load Balancer│──►│ Query Coordinator│── scatter ─────────┤ (to every shard)
└──────────────┘   │  (aggregator)    │◄─ gather top-K ────┘
                   └────────┬─────────┘
                            │  merge → global top-K → fetch docs → return
                            ▼
                   ┌──────────────────┐
                   │ Query result cache│  (Redis: popular queries → result IDs)
                   └──────────────────┘
```

**Read flow (scatter-gather):**
1. Coordinator receives `q`, parses/analyzes it (same tokenizer as indexing).
2. Check query-result cache (popular queries). Hit → return cached IDs, fetch docs.
3. Miss → **scatter** the query to all N primary shards in parallel.
4. Each shard searches its local inverted index, scores matches, returns its **local top-K**.
5. Coordinator **gathers** N partial lists, **merges** to a global top-K (k-way merge of scored lists).
6. Fetch full documents for the K winners, build highlights, return.

**Write flow (NRT):**
1. Tweet posted → published to Kafka (durable log, replayable — see [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md)).
2. Indexer consumers route each doc to a shard by `hash(doc_id) % num_shards` (document-partitioned).
3. Shard appends to an in-memory buffer; a periodic **refresh** makes the buffer searchable; a periodic **flush** persists it as an immutable on-disk segment.

## 5. Data Model

The "table" here is the **inverted index**, not a row store. Two logical structures:

```
# Inverted index (per shard, in-memory + on-disk segments)
# term  → posting list (sorted doc IDs, with per-doc freq + positions)

"cup"   → [ (doc=1012, tf=2, pos=[3,9]), (doc=1188, tf=1, pos=[0]), ... ]
"final" → [ (doc=1012, tf=1, pos=[10]), (doc=2051, tf=3, pos=[...]), ... ]
"world" → [ (doc=1012, tf=1, pos=[2]),  (doc=2099, tf=1, pos=[...]), ... ]

# Doc IDs are sorted → AND of "world cup final" = intersection of 3 posting lists
# (galloping / skip-list intersection, see 6c).
```

```sql
-- Document store (source of truth, separate from the index)
-- Postgres or a KV store; the index holds doc_ids, this holds the payload.
CREATE TABLE documents (
  doc_id       BIGINT PRIMARY KEY,        -- Snowflake ID (time-sortable, useful for recency)
  author_id    BIGINT NOT NULL,
  text         TEXT NOT NULL,
  lang         VARCHAR(8),
  created_at   TIMESTAMPTZ NOT NULL,
  likes        BIGINT DEFAULT 0,          -- engagement, updated async for ranking boost
  retweets     BIGINT DEFAULT 0,
  deleted      BOOLEAN DEFAULT FALSE      -- tombstone; index removes at merge time
);
```

**Shard key: `doc_id`** (document-partitioned — each shard owns a disjoint set of documents and a *complete* inverted index over only those docs). Why this and not term-partitioning is the central trade-off — see 6a. Doc IDs are **Snowflake IDs** so they sort by time, which makes recency filtering and merges cheap.

## 6. Deep Dives

### 6a. Inverted Index, Tokenization & Sharding Strategy

**The inverted index** maps each *term* to a *posting list* of documents containing it. Building it requires an **analysis pipeline** applied identically at index time and query time (mismatched analyzers = silent zero-result bugs):

```python
def analyze(text: str) -> list[tuple[str, int]]:
    # 1. Tokenize: split on non-word boundaries, lowercase.
    tokens = re.findall(r"\w+", text.lower())
    # 2. Remove stopwords ("the", "a", "of") — they bloat posting lists, add little signal.
    tokens = [t for t in tokens if t not in STOPWORDS]
    # 3. Stem / normalize: "running" -> "run", "cups" -> "cup" (Porter stemmer).
    tokens = [stem(t) for t in tokens]
    # 4. Emit (term, position) — positions enable phrase queries.
    return [(t, i) for i, t in enumerate(tokens)]
```

**Posting lists are compressed:** doc IDs stored as **deltas** (gaps between sorted IDs) then varint/Frame-of-Reference encoded. Gaps are small integers → compress heavily. This is why doc IDs are kept sorted.

**Segment-based immutable index (Lucene-style):** you do **not** mutate an inverted index in place — concurrent readers + random-access updates to compressed posting lists is a nightmare. Instead:
- New docs accumulate in an in-memory buffer, periodically written as a **new immutable segment** (its own mini inverted index).
- A search queries **all** segments and unions the results.
- Background **merges** combine many small segments into fewer large ones (tiered merge policy), reclaiming space and dropping tombstoned docs.
- Deletes/edits are **tombstones** (a `.del` bitset marking dead doc IDs); the doc physically disappears only when its segment is merged away.

```
Shard = [segment_0][segment_1][segment_2]...[buffer]
            (immutable, on disk)              (in-mem, mutable)
search(q) = union over all segments + buffer, minus tombstoned doc IDs
```

**Sharding strategy — the key decision:**

| | Document-partitioned (recommended) | Term-partitioned |
|---|---|---|
| Each shard holds | a complete index over a *subset of docs* | the full posting lists for a *subset of terms* |
| Query routing | **scatter-gather** to all shards | route to shards owning the query's terms |
| Indexing | local, simple — route doc by `hash(doc_id)` | a single doc's terms spread across many shards |
| Multi-term AND | local on each shard, then merge | must ship huge posting lists between shards to intersect |
| Hot terms | spread across all shards | one shard owns "the" → catastrophic hotspot |
| Used by | Elasticsearch, Solr, most production systems | rare; only niche cases |

You pick **document-partitioned**. Term-partitioned sounds efficient (a single-term query hits one shard) but multi-term intersection requires moving multi-GB posting lists across the network, and frequent terms create unfixable hot shards. Document-partitioning trades that for scatter-gather fan-out, which is the accepted cost.

### 6b. Ingestion / Near-Real-Time Indexing

The pipeline that gets a tweet from "posted" to "searchable" in seconds:

```
Tweet Service → Kafka "tweets" → Indexer consumer group → shard node
                                                              │
                       ┌──────────────────────────────────────┘
                       ▼
        in-memory buffer  ──refresh (every ~1s)──►  searchable (still in RAM)
                       │
                       └──flush (every ~30s or on size)──► immutable segment on disk
                       │
                       └──translog (write-ahead log) ──► durability before flush
```

The three intervals interviewers want you to separate clearly:

- **Refresh interval (~1s):** makes the in-memory buffer *searchable* by opening a new in-memory segment. This is what gives you NRT — *not* a disk write. Cheap, frequent. Lower it for fresher results at the cost of more tiny segments (more merge pressure).
- **Flush (~30s / size threshold):** persists in-memory segments to disk as durable immutable files and truncates the translog. Expensive, infrequent.
- **Translog (write-ahead log):** every indexed doc is appended here *before* it's searchable, so a crash between refresh and flush doesn't lose data — replay the translog on restart. (Kafka offsets serve the same role at the pipeline level: you can replay from the last committed offset.)

```python
# Indexer consumer (conceptual)
for msg in kafka_consumer:                  # at-least-once delivery
    doc = parse(msg.value)
    shard = doc.doc_id % NUM_SHARDS         # document-partitioned routing
    translog.append(shard, doc)             # durability first
    buffers[shard].add(analyze(doc.text), doc.doc_id)
    if buffers[shard].size > REFRESH_THRESHOLD or refresh_timer.elapsed():
        open_new_in_memory_segment(shard)   # now searchable (NRT)
    kafka_consumer.commit(msg.offset)       # after buffering, not before
```

Why Kafka in front: decouples bursty tweet creation from indexing, gives you a **replayable** log to rebuild a shard from scratch (or reindex with a new analyzer), and lets indexer workers scale independently as a consumer group.

### 6c. Query Serving & Ranking

**Posting-list intersection (multi-term AND):** sorted doc IDs let you intersect by advancing pointers / skipping:

```python
def intersect(list_a, list_b):              # both sorted by doc_id
    i = j = 0
    out = []
    while i < len(list_a) and j < len(list_b):
        if list_a[i] == list_b[j]:
            out.append(list_a[i]); i += 1; j += 1
        elif list_a[i] < list_b[j]:
            i += 1                           # (real impl: skip-list "gallop" to next >= list_b[j])
        else:
            j += 1
    return out
# Start with the SHORTEST posting list to minimize work.
```

**Relevance scoring — TF-IDF → BM25 (high level):**
- **TF (term frequency):** more occurrences of the term in a doc → higher score.
- **IDF (inverse document frequency):** rarer terms across the corpus are more informative ("final" matters more than "the").
- **BM25** is the production standard: TF-IDF with **saturation** (the 10th occurrence of a term adds less than the 2nd) and **length normalization** (a hit in a short tweet counts more than in a long doc). You don't derive the formula — you name it and say "TF that saturates, IDF weighting, doc-length normalized."
- **Blended ranking:** final score = BM25 text relevance + recency boost (doc_id is time-sortable) + engagement boost (likes/retweets). Keep it a pluggable scoring function; for serious ranking, a two-phase approach: BM25 retrieves candidates, then an ML model (learning-to-rank) re-ranks the top few hundred.

**Scatter-gather merge:** each shard returns its local top-K (by score). The coordinator does a **k-way merge** of N sorted lists to produce the global top-K, then fetches the K full documents. To get a page at offset `f`, each shard must return `f + size` results — hence deep pagination is expensive; use **cursor pagination** (search-after the last seen score+doc_id) instead.

**Caching popular queries:** a small fraction of queries (trending topics) are a large fraction of traffic (Zipfian). Cache `normalized_query → result doc_ids` in Redis with a short TTL (seconds, because NRT — stale results for trending queries look broken). Cache the doc payloads separately so multiple queries reuse them. This is your single biggest QPS lever on the read path.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Document- vs term-partition (restated as a trade-off):** document-partitioning costs you query fan-out (every query touches every shard, so the slowest shard sets latency) but buys you simple indexing, local intersection, and no term hotspots. Term-partitioning would cut fan-out but is unworkable for multi-term queries and hot terms. You take fan-out and mitigate it with replication + balanced shards + request hedging.

**Replication for read QPS + HA:** each primary shard has R replicas holding the same segments. The coordinator load-balances reads across `{primary + replicas}` → read throughput scales ~linearly with replica count, and a node failure just removes one copy. Writes go to the primary and replicate (the indexing path is the same — replicas consume the same translog/segments).

**Hot-shard handling:** with `hash(doc_id)` routing, document load is uniform — but *query* load can concentrate (a celebrity's tweets, a trending term) on whichever shards hold the hot docs. Mitigations:
- **More replicas on hot shards** — spread the read QPS across more copies.
- **Query result cache** absorbs repeated trending queries before they ever scatter.
- **Request hedging:** the coordinator sends a duplicate request to a replica if the first is slow, taking whichever returns first — caps tail latency from one slow shard.
- **Time-based index tiering:** route recent docs to "hot" shards (small, fast, heavily replicated) and age older docs into "warm/cold" shards with fewer replicas — most search traffic is for recent content.

**Tail latency from fan-out:** with 50 shards, p99 of the *query* ≈ p99 of the *slowest of 50 shards* — fan-out amplifies tails. Mitigate with hedged requests and by keeping shards balanced/small so no single shard is a straggler.

**Merge storms:** a low refresh interval creates many tiny segments; merging them is CPU+IO heavy and can starve queries. Trade-off: fresher results (low refresh) vs merge cost. Tune refresh to the freshness SLA, not lower.

**Failure modes:**
- A shard's replicas all down → that slice of the corpus is unsearchable; coordinator returns partial results (mark `partial: true`) rather than failing the whole query — graceful degradation.
- Indexer lag (Kafka backlog) → search results go stale, not wrong. Alert on consumer lag; scale the consumer group.
- Translog/segment corruption → rebuild the shard by replaying from Kafka offsets (the log is the source of truth for ingestion).
- Analyzer mismatch between index and query time → zero results despite matching docs. Version analyzers; reindex from Kafka when changing them.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify. Pin down: NRT freshness (seconds), top-K paginated (not full set),
           blended ranking, deletes via tombstones. State FT vs typeahead distinction.
3-6 min:   Estimation. 500M docs/day, ~2.3TB index over 90d → MUST shard (~50 shards),
           ~50K peak search QPS. Conclude: sharding → scatter-gather → slowest shard = latency.
6-12 min:  Architecture. Two paths. WRITE: Kafka → indexers → shards. READ: coordinator
           scatter-gather → merge top-K. Draw the diagram, walk both flows.
12-15 min: Data model. Inverted index (term → posting list), separate doc store,
           shard key = doc_id (Snowflake, time-sortable). Tee up the partition trade-off.
15-25 min: DEEP DIVE 1 — Inverted index + sharding. Tokenization/analysis pipeline,
           compressed posting lists, immutable segments + merges + tombstones.
           Document- vs term-partitioned table; justify document-partitioned.
25-32 min: DEEP DIVE 2 — NRT ingestion. Kafka → indexer → buffer → REFRESH (1s, searchable,
           in-RAM) vs FLUSH (30s, durable on disk) vs TRANSLOG (crash recovery). The three
           intervals are the whole point of NRT.
32-40 min: DEEP DIVE 3 — Query serving + ranking. Posting-list intersection (shortest first),
           BM25 (TF saturates + IDF + length norm), scatter-gather k-way merge, cursor
           pagination, popular-query cache.
40-45 min: Bottlenecks: hot shards (more replicas, hedged requests, cache), fan-out tail
           latency, partial results on shard failure, reindex-from-Kafka. Questions.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — sections on indexing, sharding, and read-heavy scaling.
- [Hello Interview — system design](https://www.hellointerview.com) — search / scatter-gather walkthroughs.
- [ByteByteGo — search system / Elasticsearch design](https://www.youtube.com/results?search_query=bytebytego+search+system+design)
- [NeetCode — distributed search system design](https://www.youtube.com/results?search_query=neetcode+distributed+search+system+design)

**Paid (optional):**
- "System Design Interview — Volume 2" by Alex Xu — Chapter: Design a Search Autocomplete / and the search-indexing material (pairs with this design's full-text retrieval).
- [Grokking the System Design Interview](https://www.designgurus.io) — "Designing a Search Engine / Twitter Search" module.

Related siblings: [05_typeahead_autocomplete.md](./05_typeahead_autocomplete.md) (prefix suggestion — the complement to full-text search), [06_distributed_message_log_kafka.md](./06_distributed_message_log_kafka.md) (the ingestion backbone), [02_distributed_cache.md](./02_distributed_cache.md) (the query-result cache).

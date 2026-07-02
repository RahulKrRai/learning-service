# Proximity Service (Yelp / Nearby Places)

> Appears at: Uber, Google L5, Amazon L6. The **static-POI** geospatial design — "find restaurants/businesses within X km of me, ranked." Rahul: the moving-driver-location + matching variant is a *different* problem — see [07_ride_dispatch_matching.md](./07_ride_dispatch_matching.md). The contrast is the whole game: static POIs change rarely, so the geo index can be **precomputed and cached heavily**; moving drivers need 250K location writes/sec into an ephemeral index. Lead with that distinction and you've already shown senior judgment.

## 1. Requirements

**Functional:**
- Given a user's `(lat, lng)` and a radius (or "nearby" default 5 km), return businesses within that radius.
- Filter by category (restaurant, cafe, gas station), rating, price tier, and **open-now**.
- Rank results (distance, rating, popularity, sponsored — your call, defend it).
- Business CRUD: owners add/edit/delete a business (name, address, hours, category, photos).
- Get full business detail by `business_id`.

**Non-functional:**
- ~200M businesses globally; ~100M daily active users.
- **Read-heavy**: search QPS far exceeds write QPS (read:write ≈ 1000:1). Businesses change rarely.
- Search latency < 100 ms p99.
- Eventual consistency is fine: a newly added restaurant appearing in search 1–2 min late is acceptable.
- High availability on the read path; write path can tolerate brief downtime.

**Clarifying questions:**
1. "Is the user's location moving (live tracking) or a single point per query?" → Single point. **This is what separates it from ride dispatch** — no continuous location stream, so the index is static and cacheable.
2. "Fixed radius, or does the client pass it?" → Client passes radius (capped, e.g. 1–50 km); default 5 km.
3. "Do we rank, or just return everything in radius?" → Rank by a blend of distance + rating + popularity. Confirm whether sponsored/ads are in scope (usually out for the core design).
4. "Global, or single region?" → Global; must handle dense cities (Manhattan) and sparse areas (rural Montana) gracefully.

## 2. Back-of-Envelope Estimation

```
Businesses (POIs):        200M total
Business record:          ~1 KB (name, address, lat/lng, category, hours, rating, photo URLs)
Metadata storage:         200M × 1 KB = 200 GB  (easily fits sharded Postgres)

Geo index entries:        200M × (business_id 8B + cell_id 8B) = ~3.2 GB
                          → the LOCATION index is tiny vs metadata. Keep them SEPARATE.

Search QPS:               100M DAU × 5 searches/day = 500M/day
                          = ~5,800 searches/sec avg, ~30,000/sec peak

Write QPS (business CRUD): ~1M edits/day = ~12/sec. NEGLIGIBLE.
                          read:write ≈ 5,800 : 12 ≈ 480:1 (peak skews far higher)

Cache sizing (hot areas): Pareto — 20% of geo cells serve 80% of queries.
                          Dense city cells: ~50K hot cells × (list of ~200 biz IDs × 8B)
                          ≈ 50K × 1.6 KB = 80 MB of cell->biz-ID lists. Trivially fits Redis.
                          Cache business detail too: top 1M businesses × 1 KB = 1 GB.
```

**The headline number to say out loud:** writes are ~12/sec, reads are ~30K/sec peak. This is a **cache-and-replica problem, not a write-scaling problem** — the opposite of ride dispatch.

## 3. API Design

```
# Search nearby (the primary read path)
GET /v1/search?lat=37.78&lng=-122.41&radius_km=5
      &category=restaurant&min_rating=4.0&open_now=true
      &sort=relevance&limit=20&cursor=<opaque>
→ 200 {
    results: [
      { business_id, name, distance_m: 320, rating: 4.5, price: "$$",
        category: "restaurant", is_open: true, lat, lng, thumbnail_url }
    ],
    next_cursor: "<opaque>"   # keyset pagination
  }

# Business detail
GET /v1/businesses/{business_id}
→ 200 { business_id, name, address, hours, phone, rating, review_count, photos[], ... }

# Business CRUD (owner / admin — write path)
POST   /v1/businesses          Body: { name, address, lat, lng, category, hours, ... } → 201 { business_id }
PUT    /v1/businesses/{id}      Body: { ...updated fields... }                          → 200
DELETE /v1/businesses/{id}                                                              → 204
```

Notes: `radius_km` is server-capped. Pagination is **keyset/cursor** (rank score + business_id), never `OFFSET` — offsets are slow and unstable as data changes. `open_now` is computed at query time from the business hours + the cell's timezone.

## 4. High-Level Architecture

```
                         Clients (web / mobile)
                                  |
                            [CDN / Edge]   <-- caches popular search responses (short TTL)
                                  |
                          [API Gateway / LB]
                            /            \
                  READ PATH               WRITE PATH
                     |                        |
            [Search Service]          [Business Service]
             (stateless, x-scaled)     (CRUD, validation)
                |        |                    |
                |        |              [Business DB - Postgres]  (source of truth)
                |        |               sharded by business_id
                |        |                    |
        [Redis Cache]  [Geo Index] <----------+--- (CDC / outbox)
        (cell->IDs,    [Read Replicas]   [Index Builder]
         biz detail)                     (rebuild + incremental update)
                                              |
                                         [Geo Index store]
                                         (cell_id -> [business_id])
                                              |
                                       Kafka topic: business-changes
                                       (consumed by index builder,
                                        search-cache invalidator, analytics)
```

**Read flow:** Client sends `(lat, lng, radius)` → Search Service computes the **covering set of geo cells** for that circle (center cell + neighbors) → checks Redis for each cell's business-ID list (hot cells hit cache) → on miss, reads the geo index (replica) → fetches business metadata (batched, from cache/replica) → applies filters (category, rating, open-now) → ranks → paginates → returns. CDN may serve the whole response for very hot coordinates with a short TTL.

**Write flow:** Owner edits a business → Business Service writes to Postgres (source of truth) → emits a `business-changes` event (outbox → Kafka) → Index Builder updates the geo index for the affected cell(s) → cache invalidator drops the stale cell list and business-detail entry. Because writes are ~12/sec, this pipeline is cheap and can be eventually consistent.

## 5. Data Model

**Business metadata (Postgres, sharded by `business_id`):**

```sql
CREATE TABLE businesses (
  business_id   UUID PRIMARY KEY,
  name          TEXT NOT NULL,
  address       TEXT,
  lat           DECIMAL(9,6) NOT NULL,
  lng           DECIMAL(9,6) NOT NULL,
  category      VARCHAR(40),          -- denormalized for filtering
  price_tier    SMALLINT,             -- 1..4  ($ .. $$$$)
  rating        DECIMAL(2,1),         -- cached aggregate from reviews
  review_count  INTEGER,
  hours         JSONB,                -- {"mon": [["09:00","22:00"]], ...}
  timezone      VARCHAR(40),          -- for open-now computation
  photos        JSONB,
  geo_cell      BIGINT,               -- precomputed index cell (S2/H3 id) at chosen level
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_biz_cell_cat ON businesses(geo_cell, category, rating);
```

**Shard key — `business_id`** (hash). Detail lookups are point reads by ID, so hashing spreads load evenly and avoids hot shards. We deliberately do **not** shard by geo cell, because a viral city cell would create a hot shard; the *geo index* (below) is what's organized by cell, and it's small enough to replicate widely.

**Geo index (the location index — kept SEPARATE from metadata):**

```
# Inverted index: cell_id -> list of business_ids in that cell.
# Stored in Redis (hot) backed by a durable copy (Postgres table or RocksDB).
Key:   "cell:{cell_id}"            e.g. "cell:9q8yyk"
Value: Redis SET of business_ids   { "biz_1", "biz_2", ... }

# Why separate from metadata?
# - The index is ~3 GB; metadata is ~200 GB. Different scaling and update cadence.
# - The index is rebuildable from metadata at any time (it's derived data).
# - You can swap indexing schemes (geohash -> S2) without touching the metadata DB.
```

This separation mirrors ride dispatch's split of geo index vs trip DB — but here the index is **durable and cache-friendly**, not an ephemeral TTL'd structure.

## 6. Deep Dives

### 6a. Geo Indexing — Geohash vs QuadTree vs S2 / H3

The core problem: map a 2D `(lat, lng)` into a 1D key so that "nearby" points share keys, and a radius query becomes "look up a handful of cells." (For the basics of geohash prefixes and the boundary problem, see [07_ride_dispatch_matching.md](./07_ride_dispatch_matching.md) §6a — here we focus on the *static* angle.)

**Geohash** — base-32 string; longer prefix = smaller cell (5 chars ≈ 4.9 km, 6 chars ≈ 1.2 km, 7 chars ≈ 153 m). Simple, sorts lexicographically (range scans work in any KV store). **Two weaknesses for proximity search:** (1) fixed grid → can't adapt to density, so a Manhattan cell holds 5,000 restaurants while a rural cell holds 2; (2) the **boundary problem** — points just across a cell edge have totally different geohashes.

**QuadTree** — recursively splits a cell into 4 when it exceeds a capacity (say 100 POIs). **Adaptive density is its superpower:** dense cities subdivide into tiny leaf cells; sparse areas stay as large cells. A radius query walks the tree to find leaves intersecting the circle. Because our POIs are **static**, the tree is built once and rebuilt rarely — none of the rebalancing pain that kills it for moving drivers. The cost: it's an in-memory structure you build and shard yourself, and it doesn't map cleanly to a simple KV key.

**Google S2** — projects the sphere onto a cube, orders cells along a **Hilbert curve**; 30 levels, near-equal-area cells, excellent locality. A region is covered by a *cell union* (S2 has a built-in "covering" algorithm: give it a circle, it returns the minimal set of cells). **Uber H3** — hexagonal grid; hexagons have 6 uniform neighbors (no corner-adjacency ambiguity) and "k-ring" gives all cells within k steps, which maps a radius onto neighbors cleanly.

**How a radius query maps to cells (the part you must draw):**

```python
# Generic: find candidate businesses within radius_km of (lat, lng)
def candidate_cells(lat, lng, radius_km, level):
    center = to_cell(lat, lng, level)          # geohash/S2/H3 cell at chosen level
    # cell edge ~ a few hundred m; cover the circle with center + enough neighbor rings
    k = ceil(radius_km / cell_edge_km(level))  # how many rings out to reach the radius
    return neighbors_within_k_rings(center, k) # H3 k-ring / S2 covering / geohash 8-neighbors

def search(lat, lng, radius_km):
    cells = candidate_cells(lat, lng, radius_km, INDEX_LEVEL)
    ids = set()
    for c in cells:                            # each is a Redis "cell:{c}" SET lookup
        ids |= geo_index.get_business_ids(c)
    # RECALL: union over neighbor cells avoids missing businesses near a boundary.
    # PRECISION: cells overshoot the circle, so re-filter by true distance:
    return [b for b in fetch(ids)
            if haversine(lat, lng, b.lat, b.lng) <= radius_km]
```

The cell lookup gives you **recall** (don't miss anything near the edge → that's why you union neighbor cells); the haversine re-filter gives you **precision** (drop the corner businesses that are in the cell but outside the true circle). Precision-vs-recall lives at the cell boundary — see §7.

**Dense vs sparse — pick QuadTree (or S2 with adaptive level), justify it:** A fixed geohash/H3 level forces a bad trade: too fine and rural queries must scan thousands of empty cells; too coarse and a Manhattan cell returns 5,000 businesses you must sort and trim. **QuadTree adapts** — one structure handles both. For an interview I'd say: *"I'll use a QuadTree (or equivalently S2 with variable cell levels) because POIs are static and density varies wildly across the globe; the tree subdivides only where data is dense, so query cost is roughly constant regardless of whether you're in Manhattan or Montana."* If the interviewer wants the simplest thing that ships, fall back to **S2/H3 at a fixed level + cache** — and name that as the deliberate trade-off.

**Why not Redis GEOSEARCH like ride dispatch?** You can, and it's a fine "simple answer." But Redis GEO is a single sorted set per region — great for a small ephemeral driver set, awkward for 200M durable POIs with category/rating filters. For static POIs the cell->ID inverted index + metadata DB filtering scales and caches better.

### 6b. Read-Heavy Search, Filtering & Ranking

This is where 99.9% of traffic goes, so it gets the most attention.

```python
def search(req):
    cells = candidate_cells(req.lat, req.lng, req.radius_km, INDEX_LEVEL)

    # 1) Candidate retrieval — mostly cache hits in hot areas
    biz_ids = set()
    for c in cells:
        ids = redis.smembers(f"cell:{c}")        # hot city cells: cache hit
        if ids is None:                          # cold cell: fall to replica + backfill
            ids = geo_index_replica.get(c)
            redis.sadd(f"cell:{c}", *ids); redis.expire(f"cell:{c}", 600)
        biz_ids |= ids

    # 2) Fetch metadata (batched mget; top businesses are cached as JSON)
    rows = batched_get_business(biz_ids)         # Redis mget -> replica fallback

    # 3) Filter
    out = []
    for b in rows:
        if haversine(req.lat, req.lng, b.lat, b.lng) > req.radius_km: continue   # precision
        if req.category and b.category != req.category: continue
        if req.min_rating and b.rating < req.min_rating: continue
        if req.open_now and not is_open(b.hours, b.timezone, now()): continue
        out.append(b)

    # 4) Rank
    out.sort(key=lambda b: -score(b, req))
    return paginate(out, req.cursor, req.limit)

def score(b, req):
    dist = haversine(req.lat, req.lng, b.lat, b.lng)
    return (0.5 * proximity(dist)        # closer is better (normalized)
          + 0.3 * (b.rating / 5.0)       # quality
          + 0.2 * popularity(b))         # log(review_count), capped
```

**Heavy caching of popular areas:** three cache layers, each justified by the static-POI nature of the data — cells barely change, so TTLs can be long:
- **CDN / edge:** for extremely hot coordinates (Times Square at noon), cache the *entire* search response keyed by a rounded (lat, lng, radius, filters) tuple, short TTL (30–60 s). Absorbs the spike before it ever reaches a server.
- **Cell->ID lists in Redis** (TTL ~10 min): the Pareto-hot 20% of cells serve 80% of queries from memory (~80 MB).
- **Business-detail JSON in Redis** (top ~1M businesses, 1 GB): the same famous restaurants appear in millions of result sets.

**Read replicas:** point business-detail and geo-index cold reads at N Postgres read replicas; the primary only takes the ~12 writes/sec. Reads scale linearly with replicas. This is the right lever precisely *because* writes are negligible — contrast ride dispatch, where the bottleneck is **write** throughput into Redis.

**open-now** is computed at request time, not indexed, because "is it open" changes every minute. Store hours + timezone on the business; evaluate against the query timestamp.

### 6c. Write Path & Building / Updating the Geo Index

Writes are rare (~12/sec) but must propagate correctly to derived data (the geo index + caches).

```
Owner edits business
   -> Business Service: validate, write row to Postgres (source of truth)
                        write an outbox row in the SAME transaction (exactly-once-ish)
   -> Outbox poller -> Kafka topic "business-changes" { business_id, old_cell, new_cell, op }
   -> Consumers:
        (a) Index Builder:    incremental update of the geo index
        (b) Cache invalidator: DEL cell:{old}, cell:{new}, biz:{id}
        (c) Analytics
```

**Incremental update (the default — cheap because writes are rare):**
```python
def apply_change(ev):
    if ev.op == "DELETE":
        geo_index.srem(f"cell:{ev.old_cell}", ev.business_id)
    elif ev.op == "CREATE":
        geo_index.sadd(f"cell:{ev.new_cell}", ev.business_id)
    elif ev.op == "MOVE" or ev.old_cell != ev.new_cell:   # address/coords changed
        geo_index.srem(f"cell:{ev.old_cell}", ev.business_id)
        geo_index.sadd(f"cell:{ev.new_cell}", ev.business_id)
    invalidate_cache(ev.old_cell, ev.new_cell, ev.business_id)
```

**Full rebuild (rare — schema/index-scheme change, corruption, or switching geohash→S2):** a batch job scans `businesses`, recomputes each row's `geo_cell`, and writes a *new* index version (blue/green: build `index_v2` alongside `index_v1`, then atomically flip a pointer). Because the index is **derived data**, you can always rebuild it from the metadata DB — a property worth stating explicitly. Replay `business-changes` from Kafka to catch up writes that landed during the rebuild.

**Separation of location index from metadata** (recap, because interviewers probe it): metadata = 200 GB, source of truth, sharded by `business_id`; geo index = ~3 GB, derived, organized by cell, replicated/cached everywhere. They scale, update, and fail independently. Losing the index is recoverable (rebuild); losing metadata is not (back it up). This is the same *index-vs-truth* split as ride dispatch, but there the index is ephemeral and write-hot, here it's durable and read-hot.

## 7. Bottlenecks, Failure Modes & Trade-offs

| Concern | Risk | Mitigation |
|---|---|---|
| **Precision vs recall at cell boundaries** | Union of neighbor cells over-returns (corner POIs outside the true circle) → low precision; too few cells → miss POIs near edge → low recall | Always union center + neighbor rings (recall), then **haversine re-filter** by true distance (precision). Tune `k` rings from radius / cell-edge. |
| Hot city cell (Manhattan) returns 5,000 POIs | Slow sort/filter, fat cache entry | Adaptive cells (QuadTree) cap per-cell count; or cap results per cell + rank, paginate; cache the hot cell aggressively. |
| Sparse area scans many empty cells | Wasted lookups | Adaptive cells keep rural areas as large single cells; with fixed grid, short-circuit on empty cell sets. |
| Cache stampede on a hot cell expiry | 10K queries miss simultaneously, hammer replica | Per-key lock / request coalescing ("single-flight"); jittered TTLs; serve slightly-stale on miss while one request refills. |
| Stale cache after a business edit | User sees closed/moved business | Event-driven invalidation via `business-changes`; short TTLs; acceptable since eventual consistency was a stated requirement. |
| Postgres primary failure (writes) | Owners can't edit | Tolerable — read path (CDN, cache, replicas) keeps serving search. Failover primary; writes resume. |
| Geo index corruption | Wrong/empty search results | It's derived data — rebuild from metadata (blue/green) + replay Kafka. No data loss. |
| Read replica lag | Newly-edited business briefly stale | Acceptable per requirements; route the *owner's own* reads to primary if they need read-your-writes. |

**Key trade-offs:**
- **QuadTree (adaptive) vs fixed-grid geohash/H3:** adaptivity handles dense/sparse cleanly but is a custom in-memory structure you must shard and persist; fixed-grid is dead simple and maps to any KV store but trades query cost across density. Static POIs make adaptivity cheap to maintain — pick it, but be ready to defend fixed-grid+cache as the "ship it Monday" option.
- **Index cell level:** finer = smaller cells, more lookups per query, better per-cell cache locality; coarser = fewer lookups, fatter cells, worse precision pre-filter. Tune to median urban density.
- **Cache TTL:** long TTLs (data is static) maximize hit rate, but slow propagation of edits → lean on event-driven invalidation so you get *both* long TTL and freshness.
- **Static vs dynamic geo (the framing trade-off):** because POIs are static you precompute, cache, and replica-scale. The moment locations move (drivers), none of that holds and you're back in [07_ride_dispatch_matching.md](./07_ride_dispatch_matching.md)'s write-heavy world.

## 8. Talk Track (35-45 min)

```
00:00-04:00  Clarify: single point vs moving location (THIS is the static-POI variant,
             contrast ride dispatch). Radius source/cap. Ranking in scope? Global?
             State it: read-heavy, ~1000:1, eventual consistency OK.
04:00-09:00  Estimation: 200M POIs (~200GB metadata), geo index only ~3GB,
             ~30K search/sec peak vs ~12 write/sec. Headline: cache+replica problem,
             NOT a write-scaling problem. Hot 20% cells -> ~80MB cache.
09:00-15:00  Architecture: read path (Search Svc -> cells -> Redis -> metadata ->
             filter -> rank -> paginate) and write path (Business Svc -> Postgres ->
             outbox -> Kafka -> index builder + cache invalidator). CDN on read path.
15:00-17:00  Data model: metadata (Postgres, shard by business_id) SEPARATE from
             geo index (cell->IDs, derived, Redis+durable). Justify both shard choices.
17:00-26:00  DEEP DIVE 1 — Geo indexing. Geohash (boundary problem) -> QuadTree
             (adaptive density, cheap because static) -> S2/H3 (covering / k-ring).
             Draw radius->cells: union neighbors (recall) + haversine refilter (precision).
             Pick QuadTree/adaptive-S2 and justify with dense-vs-sparse.
26:00-34:00  DEEP DIVE 2 — Read-heavy search & ranking. 3 cache layers (CDN, cell lists,
             biz detail), read replicas, open-now at query time, ranking blend.
             Cache stampede / single-flight.
34:00-39:00  DEEP DIVE 3 — Write path & index build. Incremental (default) vs full
             rebuild (blue/green, replay Kafka). Index is derived -> always rebuildable.
39:00-43:00  Bottlenecks: precision/recall at boundaries, hot cells, stampede, replica lag.
43:00-45:00  Extensions: autocomplete/typeahead, reviews subsystem, personalization,
             "search along a route." Contrast once more with moving-driver dispatch.
```

## Resources

**Free:**
- System Design Primer — https://github.com/donnemartin/system-design-primer (search "geohash", "proximity")
- Hello Interview — https://www.hellointerview.com (search "proximity" / "nearby places")
- ByteByteGo YouTube — https://www.youtube.com/results?search_query=bytebytego+proximity+service+nearby+friends
- NeetCode YouTube — https://www.youtube.com/results?search_query=neetcode+proximity+service+yelp+system+design
- Uber H3 docs — https://h3geo.org  ·  Google S2 — https://s2geometry.io

**Paid (optional):**
- "System Design Interview — Volume 2" by Alex Xu — Chapter: "Proximity Service"
- DesignGurus — https://www.designgurus.io (Grokking the System Design Interview: "Designing Yelp / Nearby Friends")

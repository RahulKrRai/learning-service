# Ride Dispatch / Matching (Uber-style)
> THE design for Uber Senior interviews. Also appears at Lyft, DoorDash (delivery matching), Google Maps (ETA). Rahul — this is your geospatial deep dive. Be precise about the indexing trade-offs.

## 1. Requirements

### Functional
- Riders request a ride from location A to destination B; system matches them to the nearest available driver.
- Drivers continuously broadcast their location (every 4 seconds).
- System returns ETA and surge pricing estimate before rider confirms.
- On match: driver notified, ride state machine begins (accepted → en route → arrived → in progress → completed).
- Support cancellation by either party; re-match if driver cancels.
- Surge pricing: dynamically computed based on supply/demand in a geographic zone.

### Non-Functional
- Driver location writes: up to 1 M active drivers × 1 write/4s = 250,000 writes/sec.
- Match latency: rider sees a matched driver in <3 seconds of requesting.
- ETA accuracy: within 2 minutes for trips up to 30 min.
- Availability: 99.99% (core dispatch path).
- Geospatial query: find all available drivers within X km in <50 ms.
- Scale to 100 M+ trips/day globally (Uber peak).

### Clarifying Questions to Ask
1. "Should the system optimize for closest driver, or also consider driver rating, vehicle type, and surge zone?" — drives matching algorithm complexity.
2. "Is ETA computed in real-time using a live traffic graph, or estimated from historical averages?" — determines whether you integrate OSRM/Google Maps or build an internal graph engine.
3. "What are the consistency requirements for driver location? Can a rider see a driver that just became unavailable?" — soft consistency is fine; hard consistency would require distributed locks.

---

## 2. Back-of-Envelope Estimation

```
Driver location updates:
  1M active drivers × 1 update/4s = 250,000 writes/sec
  Each update: driver_id (8B) + lat/lng (16B) + timestamp (8B) + status (1B) = ~33B
  Bandwidth: 250K × 33B ≈ 8 MB/s ingestion — trivial

Rider requests:
  100M trips/day / 86,400 ≈ 1,160 match requests/sec (average)
  Peak (rush hour): ~5× = 5,800 match requests/sec

Geospatial index write throughput:
  250K/sec driver updates into in-memory geo-index (Redis GEOADD)
  Redis single-node: ~100K-200K ops/sec; need ~2-3 Redis shards by city/region

Storage (driver state — ephemeral):
  1M drivers × 50B per record = 50 MB — trivially fits in Redis

Trip history storage:
  100M trips/day × 500B per trip = 50 GB/day → 18 TB/year
  Write to PostgreSQL (sharded by trip_id) + archive to S3 after 90 days

ETA cache:
  Pre-compute ETAs for common origin→geohash-zone pairs
  ~10M cached entries × 100B = 1 GB — fits in Redis
```

---

## 3. API Design

### Rider-facing
```
// Request a ride
POST /v1/rides
Body: {
  rider_id:    string,
  origin:      { lat: float, lng: float },
  destination: { lat: float, lng: float },
  vehicle_type: enum { UberX, UberXL, Black },
  payment_method_id: string
}
Response 202 Accepted:
{
  ride_id:    string,
  status:     "MATCHING",
  eta_seconds: 180,
  surge_multiplier: 1.4,
  estimated_price: { min: 12.50, max: 15.00, currency: "USD" }
}

// Poll ride status (or use WebSocket / SSE)
GET /v1/rides/{ride_id}
Response: { status, driver: { name, rating, vehicle, location }, eta_seconds }

// Cancel ride
DELETE /v1/rides/{ride_id}
```

### Driver-facing
```
// Location heartbeat (every 4s, from mobile SDK)
PUT /v1/drivers/{driver_id}/location
Body: { lat: float, lng: float, heading: float, speed: float, status: enum { available, busy, offline } }
Response: 204 No Content

// Accept / reject a ride offer
POST /v1/drivers/{driver_id}/ride-offers/{offer_id}/accept
POST /v1/drivers/{driver_id}/ride-offers/{offer_id}/reject
```

### Internal (matching service)
```
// Find nearby drivers
GET /internal/v1/drivers/nearby?lat=&lng=&radius_m=&vehicle_type=&limit=20
Response: [{ driver_id, lat, lng, eta_seconds, distance_m }]
```

---

## 4. High-Level Architecture

```
Mobile Clients (Rider / Driver apps)
       |                  |
  [WebSocket /        [Location
   SSE gateway]        Ingestor]
       |                  |
       v                  v
  [Ride Service]    [Location Service]  <-- 250K writes/sec
       |                  |
       |           [Geo Index — Redis Cluster]
       |           (GEOADD per driver update)
       |                  |
  [Matching         [Geospatial Query]
   Service]  <----------- +
       |            (GEOSEARCH within radius)
       |
  [ETA Service] <-- [Traffic Graph / OSRM]
       |
  [Surge Pricing Service]
  (supply/demand ratio per geohash zone)
       |
  [Notification Service]
  (push to driver: WebSocket / FCM / APNs)
       |
  [Trip State Machine — PostgreSQL]
  (trip lifecycle, audit log)

Driver Location Pub/Sub:
  Driver → Location Ingestor
          → Kafka topic: driver-locations (keyed by driver_id)
          → Flink consumer → update Redis Geo Index
          → Matching Service subscribes for real-time driver positions
```

**Flow:** Driver apps ping the Location Ingestor every 4s. Updates flow through Kafka into a Flink job that writes to Redis using `GEOADD`. When a rider requests a ride, the Matching Service calls `GEOSEARCH` on Redis to get candidates, fetches ETA for each, ranks them, and sends an offer to the best driver via the WebSocket gateway. The driver has 10s to accept; on timeout or rejection, the next candidate is offered.

---

## 5. Data Model

### Redis Geo Index (ephemeral, per city shard)
```
Key:    "drivers:available:{vehicle_type}"   e.g. "drivers:available:UberX"
Type:   Redis Sorted Set with geospatial encoding (GEOADD)
Value:  member=driver_id, score=geohash(lat,lng) as 52-bit integer

Commands:
  GEOADD drivers:available:UberX <lng> <lat> <driver_id>
  GEOSEARCH drivers:available:UberX FROMMEMBER <rider_geo> BYRADIUS 3 km ASC COUNT 20
```

### Driver State (Redis Hash, TTL=30s — evicts if driver goes offline)
```
Key:   "driver:{driver_id}"
Fields: lat, lng, heading, speed, status, vehicle_type, last_seen_at, rating
TTL:   30s (refresh on each 4s heartbeat; expiry = driver went offline)
```

### Trip (PostgreSQL, sharded by trip_id hash)
```sql
CREATE TABLE trips (
  trip_id          UUID PRIMARY KEY,
  rider_id         UUID NOT NULL,
  driver_id        UUID,
  status           VARCHAR(20),    -- MATCHING, ACCEPTED, EN_ROUTE, IN_PROGRESS, COMPLETED, CANCELLED
  origin_lat       DECIMAL(9,6),
  origin_lng       DECIMAL(9,6),
  dest_lat         DECIMAL(9,6),
  dest_lng         DECIMAL(9,6),
  vehicle_type     VARCHAR(20),
  surge_multiplier DECIMAL(4,2),
  fare_cents       INTEGER,
  requested_at     TIMESTAMPTZ,
  matched_at       TIMESTAMPTZ,
  completed_at     TIMESTAMPTZ,
  -- Geohash of origin for surge zone queries
  origin_geohash   VARCHAR(12)
);
CREATE INDEX idx_trips_driver ON trips(driver_id, status);
CREATE INDEX idx_trips_rider  ON trips(rider_id, requested_at DESC);
```

### Surge Zone State (Redis, computed every 1 min by Surge Service)
```
Key:   "surge:{geohash_6char}"   (geohash precision 6 ≈ 1.2km × 0.6km cell)
Value: { supply: int, demand: int, multiplier: float, computed_at: timestamp }
TTL:   90s
```

**Partitioning:** Redis geo index is partitioned by city/region (not by geohash) to keep each shard's dataset small and to enable city-level failover. Each city shard serves all geospatial queries for that region.

---

## 6. Deep Dives

### 6a. Geospatial Indexing — Geohash vs QuadTree vs Google S2

All three encode 2D geographic coordinates into a 1D structure that preserves proximity. The right choice depends on the use case.

**Geohash:**
- Encodes lat/lng into a base-32 string (e.g., `dr5ru7`). Each character adds precision.
- **Prefix = proximity:** two locations sharing a long common prefix are close. `dr5ru` contains all points in a ~4.9km × 4.9km cell; `dr5r` is the parent ~39km × 20km cell.
- Precision levels: 4 chars ≈ 39km, 5 chars ≈ 4.9km, 6 chars ≈ 1.2km, 7 chars ≈ 153m.
- **Limitation — boundary problem:** two points near a cell boundary can have completely different geohashes. Fix: always query the 8 neighboring cells in addition to the center cell.
- **Why good for Kafka topic keying:** use geohash prefix (5–6 chars) as partition key → all driver updates in a zone go to the same partition → matching service reads a zone's updates from a single partition.
- **Redis GEOSEARCH uses geohash internally** — `GEOADD` encodes lat/lng into a 52-bit geohash stored as a sorted set score.

**QuadTree:**
- Recursively subdivides a bounding box into 4 quadrants. Leaf nodes contain up to a capacity (e.g., 50 drivers); subdivide when full.
- **Adaptive density:** cells are smaller in dense urban areas (many drivers) and larger in sparse rural areas. Eliminates boundary imbalance.
- **Good for:** static or slowly-changing datasets; tile-based map rendering; situations where cell size must adapt to data density.
- **Drawback for driver tracking:** tree must be rebalanced as drivers move in and out of cells — complex to maintain in a distributed, high-write-rate environment.
- **When to use:** if asked about a static geospatial index (restaurants, landmarks) or a read-heavy index with infrequent updates.

**Google S2 (Spherical Geometry):**
- Projects the Earth's surface onto a cube face, then subdivides using a Hilbert space-filling curve. Results in cells at 30 levels of granularity.
- **Key advantage:** cells are approximately equal area at each level (unlike geohash, which has non-uniform cell shapes). Hilbert curve maximizes spatial locality — adjacent cells in the curve are geographically adjacent.
- **No boundary problem** in the same way as geohash — Hilbert curve wraps smoothly.
- Used by Google Maps, Uber (H3 is Uber's hexagonal alternative).
- **Drawback:** more complex to implement from scratch; library required (`s2geometry`).
- **When to use:** when you need high accuracy for spherical distance (near poles, or high precision global routing) or are building on top of existing S2 tooling.

**Decision for ride dispatch:** Use **Redis GEOADD/GEOSEARCH** (geohash-based) for the driver location index — it's battle-tested, gives O(log N) proximity queries, and integrates directly with Redis. Use **geohash prefix (6 chars)** as the Kafka topic key for driver location streaming. Use **H3 hexagonal grid** (Uber's open-source library) for surge zone computation — hexagons tile the plane without gaps and have uniform neighbors, making zone aggregation cleaner.

### 6b. Driver Location Updates at Scale — 250K Writes/Sec

**Problem:** 1M active drivers pinging every 4s = 250K writes/sec. A naive single Redis instance can handle ~100-200K ops/sec.

**Architecture:**
1. **Location Ingestor** (stateless, horizontally scaled): receives driver pings via HTTP/2 or gRPC, validates, and publishes to Kafka topic `driver-locations` (partitioned by `driver_id` — 200 partitions).
2. **Flink Consumer Group** (one consumer per partition): reads from Kafka, batches updates for the same geohash region, applies them to Redis. Flink provides backpressure: if Redis is slow, Kafka consumer lag grows but no data is lost.
3. **Redis Cluster** (partitioned by city/region): 6–10 nodes for 250K writes/sec. Each city is an independent Redis shard.
4. **Driver State TTL:** Driver state in Redis expires after 30s if no heartbeat — automatically removes offline drivers from the geo index without a separate cleanup job.

**Why Kafka in the middle:**
- Decouples ingestion rate from Redis write rate (buffer for spikes).
- Driver location stream is also consumed by the Matching Service (for real-time awareness), the Surge Service (for computing supply per zone), and the Analytics pipeline — one produce, multiple consumers.
- Replay capability: if the geo index is corrupted, replay the last N minutes of `driver-locations` to rebuild it.

### 6c. Matching Algorithm, Fairness, and ETA

**Greedy nearest-driver matching:**
1. `GEOSEARCH` with initial radius (e.g., 2 km), get top-20 candidates.
2. For each candidate, fetch ETA from ETA Service (pre-computed for the origin geohash zone, or real-time OSRM call).
3. Rank by ETA (not raw distance — a driver 3 km away on a highway may arrive before one 1 km away in traffic).
4. Send offer to rank-1 driver. If rejected or timeout (10s), send to rank-2. Repeat up to 5 times.
5. If no driver accepts in initial radius, expand radius (2 km → 5 km → 10 km) and repeat.

**Starvation / fairness problem:**
- Greedy always picks the nearest driver → far drivers are never matched.
- **Mitigation 1 — Batching (Uber's real approach):** Instead of greedy sequential offers, batch all incoming ride requests in a 500ms window and run a global assignment optimization (linear programming / Hungarian algorithm) across all available drivers in the city. Maximizes global efficiency, not greedy local optimum.
- **Mitigation 2 — Driver score:** Add a "time since last ride" bonus to far drivers so they aren't permanently starved.
- **Mitigation 3 — Probabilistic offers:** occasionally offer to a non-nearest driver to improve geographic equity.

**ETA calculation:**
- **Fast path (cache):** pre-compute ETAs from all geohash-6 zones to all other zones using historical traffic data. Store in Redis. Cache hit → O(1).
- **Slow path (real-time):** call OSRM (Open Source Routing Machine) with the live traffic-adjusted road graph, or Google Maps Distance Matrix API. Takes 50–200 ms per call.
- **Hybrid:** use cached ETA for initial ranking; when driver accepts, trigger a real-time OSRM call for the accurate ETA shown to the rider.

### 6d. Surge Pricing

**Mechanism:**
- Divide the city into geohash-6 zones (~1.2 km cells).
- Every 60 seconds, the Surge Service computes for each zone:
  ```
  supply  = count of available drivers in zone (from Redis geo index)
  demand  = count of pending ride requests in zone (last 60s, from trip DB)
  ratio   = demand / max(supply, 1)
  multiplier = clamp(1.0 + 0.5 × (ratio - 1.0), 1.0, 5.0)
  ```
- Write `(zone, multiplier)` to Redis with TTL=90s.
- Apply **hysteresis**: multiplier only changes if the new value differs from current by >10%, preventing oscillation.

**Smooth surge:** Use exponential moving average on the multiplier to prevent jarring price jumps.

**Rider transparency:** Show surge multiplier and estimated price band before rider confirms. Require explicit confirmation if multiplier > 2×.

---

## 7. Bottlenecks, Failure Modes & Trade-offs

| Concern | Risk | Mitigation |
|---|---|---|
| Redis geo index shard failure | Drivers in that city invisible to matching | Redis Sentinel/Cluster with replica failover; warm standby; fallback to PostgreSQL geo query (slower) |
| Kafka consumer lag (Flink) | Geo index staleness — riders see stale driver positions | Alert on lag >10s; scale Flink parallelism; increase partitions |
| Driver ping storm on app foreground | All 1M drivers reconnect simultaneously after outage | Exponential backoff + jitter on client reconnect |
| Matching service cascades on ETA timeout | OSRM slow → matching hangs → rider waits | Circuit breaker on ETA service; fall back to distance-based ranking with cached ETA |
| Ghost drivers (driver went offline, not evicted from index) | Rider matched to unreachable driver | TTL=30s on driver Redis key; heartbeat monitoring; driver status check before sending offer |
| Hot city shard | One city (NYC, Bangalore) overwhelms a Redis shard | Partition large cities into sub-city shards (borough/district level) |
| Surge zone boundary arbitrage | Drivers cluster at the high-surge side of a boundary | Use smooth surge (gradual gradient), not binary zone thresholds |
| Double-booking a driver | Two match requests claim the same driver | Optimistic locking: atomic Redis `SET driver:{id}:status busy NX EX 30` before sending offer |

**Key trade-offs:**
- **Greedy matching vs global optimization:** greedy is O(1) per match, simple, but suboptimal globally. Batched optimization is better for utilization but adds 500ms latency. Uber uses batching in production.
- **Geohash vs H3:** geohash has non-uniform cell shapes and boundary issues; H3 hexagons are uniform but require a library and more complex zone hierarchy. Use geohash for simplicity in an interview; mention H3 as the production choice.
- **Fake real-time driver position on map:** Uber's rider app animates the driver icon using dead reckoning (speed + heading + time since last update) between 4s pings — the "real-time" movement is interpolated, not truly real-time.

---

## 8. Talk Track (35–45 Min)

```
00:00–04:00  Clarify: optimization criteria (nearest vs ETA vs rating)?
             ETA source (internal graph vs Maps API)?
             Consistency requirements for driver state?
04:00–10:00  Estimation: 250K writes/sec (driver location), 5.8K match
             requests/sec, Redis geo index size (50 MB), 50 GB/day trip storage
10:00–17:00  High-level architecture: Location Ingestor → Kafka → Flink → Redis
             Matching Service → ETA Service → Notification → Trip DB
             Walk the full ride request flow
17:00–25:00  Deep dive 1 — Geospatial indexing
             - Geohash: prefix=proximity, boundary problem, 8-neighbor query
             - QuadTree: adaptive density, high maintenance cost at 250K writes/sec
             - S2/H3: uniform cells, spherical geometry, Uber's choice
             - Decision: Redis GEOADD (geohash) for driver index; H3 for surge zones
25:00–33:00  Deep dive 2 — Driver location at scale
             - 250K writes/sec → Kafka buffer → Flink → Redis cluster
             - TTL=30s for automatic offline eviction
             - Driver state as Kafka event stream (multi-consumer: matching, surge, analytics)
33:00–38:00  Matching algorithm: greedy vs batched, ETA ranking, radius expansion,
             double-booking prevention (Redis NX)
             Surge pricing: supply/demand ratio, hysteresis, H3 zone computation
38:00–42:00  Failure modes, fallbacks, trade-offs
42:00–45:00  Extensions: multi-stop trips, carpooling (Uber Pool — combinatorial
             matching), food delivery (DoorDash — batched pickups at restaurant)
```

---

## Resources

### Free
- System Design Primer — https://github.com/donnemartin/system-design-primer (search "Uber")
- ByteByteGo YouTube — https://www.youtube.com/results?search_query=bytebytego+uber+ride+sharing+system+design
- Hello Interview — https://www.hellointerview.com (search "Uber" or "ride sharing")
- Uber Engineering Blog (free) — https://www.uber.com/blog/engineering/ (search "geospatial", "dispatch", "H3")
- H3 docs — https://h3geo.org

### Paid
- ByteByteGo — https://bytebytego.com (Chapter: "Design Uber / Lyft")
- DesignGurus — https://www.designgurus.io (Grokking System Design: "Designing Uber Backend")

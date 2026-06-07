# Real-Time Container / Shipment Tracking Platform

> Appears at: Logward (your actual system), and is a strong home design for Google L5, Confluent, Uber, Amazon — event-driven data platform at 10M+ records with multi-tenant enterprise customers.

## 1. Requirements

**Functional:**
- Ingest real-time location and lifecycle events from carriers, IoT devices, and shipping APIs
- Track container statuses (BOOKED → LOADED → IN_TRANSIT → AT_PORT → DELIVERED)
- Serve enterprise (multi-tenant) customers: each customer sees only their containers
- Support geo queries: "show all containers currently near port X"
- Provide real-time dashboard updates for operations teams
- Historical location replay for auditing

**Non-functional:**
- 10M+ container records; 100K+ events/day ingested (peak ~5K events/sec during bulk carrier feeds)
- 99.9% availability for read APIs; reads < 100ms p95
- Multi-tenant: full data isolation between enterprise customers; a bug must not leak tenant A's data to tenant B
- Idempotent event ingestion (carrier feeds may send duplicates)
- At least 3-year event history for audit

**Clarifying questions to ask:**
1. "Is this B2B (enterprise customers managing their own shipments) or B2C (individual consumers)?" → B2B multi-tenant.
2. "Are location updates push (carrier webhook/IoT device) or pull (we poll carrier APIs)?" → Both — poll some carriers, receive webhooks from others.
3. "What's the SLA for real-time updates? Sub-second, or a few seconds of lag is fine?" → A few seconds is acceptable; this is logistics, not financial trading.

## 2. Back-of-Envelope Estimation

```
Containers tracked:       10M active containers
Carriers / data sources:  ~50 carrier APIs + IoT streams
Events per container/day: ~10 (location pings + status transitions)
Write QPS:                10M × 10 / 86,400 ≈ 1,200 writes/sec (avg)
Peak write QPS:           ~5,000/sec (bulk carrier feed windows)
Read QPS:                 10× writes ≈ 12,000 reads/sec (dashboards, APIs)

Event record size:         ~500 bytes (container_id, timestamp, lat/lon, status, carrier_ref)
Events stored (3 yr):      10M × 10 × 365 × 3 × 500B ≈ 55 TB
Location history:          stored separately in time-series store, ~1 KB/ping
Storage for locations:     10M × 10 × 365 × 3 × 1KB ≈ 110 TB

Bandwidth inbound:         5,000 writes/sec × 500B ≈ 2.5 MB/s
Bandwidth outbound:        12,000 reads/sec × 5KB avg response ≈ 60 MB/s
```

## 3. API Design

```
# Ingest
POST /v1/events
Body: { container_id, event_type, timestamp, lat, lon, status, carrier_ref, idempotency_key }
→ 202 Accepted (async processing)

# Container state
GET /v1/containers/{container_id}
→ { container_id, current_status, last_location, last_updated, tenant_id }

# Location history
GET /v1/containers/{container_id}/history?from=ISO8601&to=ISO8601
→ [{ timestamp, lat, lon, event_type }]

# Geo query
GET /v1/containers?near=lat,lon&radius_km=50&status=IN_TRANSIT
→ [{ container_id, current_status, lat, lon, distance_km }]

# Tenant-scoped container list
GET /v1/containers?page_token=X&limit=100
→ [container summaries] (tenant_id injected from JWT, never from request body)
```

## 4. High-Level Architecture

```
Carrier APIs / IoT                   Enterprise Customers
     │  webhooks / polling                │  REST / WebSocket
     ▼                                    ▼
┌─────────────┐              ┌─────────────────────────┐
│  Ingestion  │              │      API Gateway         │
│  Service    │──────────┐   │  (Auth + Tenant Context) │
└─────────────┘          │   └──────────┬──────────────┘
     │ Kafka topic:       │              │
     │ raw.events         │              ▼
     ▼                    │   ┌─────────────────────┐
┌─────────────┐           │   │  Query Service       │
│  Validation │           │   │  (container state,  │
│  & Enrichment│          │   │   geo queries,       │
│  Service    │           │   │   history)           │
└──────┬──────┘           │   └──────┬──────────────┘
       │ Kafka topic:      │          │
       │ enriched.events   │          │
       ▼                   │          ▼
┌─────────────────┐        │   ┌──────────────────┐
│  Lifecycle FSM  │        │   │  Redis Cache      │
│  (state machine)│        └──►│  (container state │
└──────┬──────────┘            │   per tenant)     │
       │                       └──────────────────┘
       ├──► PostgreSQL (container state + metadata)
       │    [partitioned by tenant_id]
       │
       └──► TimescaleDB / ClickHouse (location history / time-series)
```

**Request flow (ingest):**
1. Carrier webhook hits Ingestion Service → idempotency check (Redis SET NX on `idempotency_key`) → publish to `raw.events` Kafka topic.
2. Validation & Enrichment Service consumes `raw.events` → validates against known container IDs, enriches with carrier metadata → publishes to `enriched.events`.
3. Lifecycle FSM Service consumes `enriched.events` → applies state machine transitions → upserts container state in PostgreSQL → appends to TimescaleDB for location history → publishes `container.status_changed` events for downstream consumers (webhooks, notifications).

**Request flow (read):**
API Gateway injects `tenant_id` from JWT → Query Service reads from Redis cache (with tenant-namespaced key) → on cache miss, reads from PostgreSQL with `WHERE tenant_id = ?` → returns result.

## 5. Data Model

```sql
-- Container current state (PostgreSQL, partitioned by tenant_id)
CREATE TABLE containers (
  container_id     TEXT PRIMARY KEY,
  tenant_id        UUID NOT NULL,  -- partition key
  current_status   TEXT NOT NULL,
  last_event_id    UUID,
  last_lat         DECIMAL(9,6),
  last_lon         DECIMAL(9,6),
  last_updated_at  TIMESTAMPTZ NOT NULL,
  carrier_ref      TEXT,
  created_at       TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_containers_tenant ON containers(tenant_id);
CREATE INDEX idx_containers_status ON containers(tenant_id, current_status);

-- Location history (TimescaleDB hypertable, partitioned by time)
CREATE TABLE location_events (
  event_id        UUID PRIMARY KEY,
  container_id    TEXT NOT NULL,
  tenant_id       UUID NOT NULL,
  timestamp       TIMESTAMPTZ NOT NULL,  -- partition key (hypertable)
  lat             DECIMAL(9,6),
  lon             DECIMAL(9,6),
  event_type      TEXT,
  raw_payload     JSONB
);
SELECT create_hypertable('location_events', 'timestamp');

-- Idempotency log (Redis with 24h TTL, key = idempotency_key)
-- container:{tenant_id}:{container_id} → serialized state (Redis cache)
```

**Partitioning strategy:** PostgreSQL `containers` table partitioned by `tenant_id` using range or hash partitioning — keeps tenant data co-located and makes tenant-scoped queries fast. TimescaleDB `location_events` partitioned by time (chunk interval = 1 week) — supports efficient time-range queries and data retention.

## 6. Deep Dives

### 6a. Multi-Tenant Data Isolation

**The risk:** A bug in the query layer returns tenant A's containers to tenant B. At enterprise scale, this is a contract violation and potentially a GDPR breach.

**Defense in depth:**
1. **JWT-injected tenant_id:** API Gateway extracts `tenant_id` from the validated JWT and injects it as a header. The Query Service never reads `tenant_id` from the request body — only from the injected header. Prevents client-side spoofing.
2. **Row-Level Security (PostgreSQL RLS):** `CREATE POLICY tenant_isolation ON containers USING (tenant_id = current_setting('app.tenant_id')::uuid)`. Even if the application query forgets the `WHERE tenant_id = ?` clause, the DB enforces it. Belt-and-suspenders.
3. **Per-tenant cache namespace:** Redis keys are `container:{tenant_id}:{container_id}`. A cache bug can only return data within the same tenant namespace.
4. **Noisy-neighbor prevention:** Per-tenant rate limiting at the API Gateway (token bucket per `tenant_id`). Large enterprise tenants (bulk exporters) get a higher burst limit but are still bounded.

### 6b. Idempotent Event Ingestion

Carrier feeds and IoT streams may resend the same event (at-least-once delivery). Processing duplicates twice would create false status transitions or duplicate location pings.

**Solution:** Each inbound event must carry a client-provided `idempotency_key` (e.g. `carrier_ref + event_type + timestamp`). On arrival:
1. `SETNX idempotency:{key} "1" EX 86400` in Redis. If key already exists → return 202 immediately (already processed).
2. Otherwise, publish to Kafka. The `idempotency_key` is included in the Kafka message — downstream consumers also deduplicate on `event_id` using PostgreSQL's `ON CONFLICT DO NOTHING`.

## 7. Bottlenecks, Failure Modes & Trade-offs

**At 10x scale (100M containers):**
- PostgreSQL `containers` table at ~100M rows — consider sharding by `tenant_id` hash across multiple Postgres instances (Citus or application-level sharding). Read replicas for query traffic.
- TimescaleDB compression + automatic data tiering (move old chunks to cheaper object storage via Parquet/S3).
- Kafka consumer lag: add partitions and consumer instances for high-throughput tenants.

**Failure modes:**
- Carrier API down: Ingestion Service retries with exponential backoff; events queue in Kafka; no data loss.
- Validation Service crashes: Kafka consumer offset not committed; events reprocessed on restart (idempotent consumers handle duplicates).
- Redis cache eviction: Query Service falls back to PostgreSQL; higher latency but correct.

**Trade-offs:**
- Async ingestion (Kafka) vs synchronous DB write: we chose async — higher throughput, but a client's "202 Accepted" doesn't guarantee immediate consistency. Acceptable for logistics (few-second lag is fine).
- Per-row RLS vs application-level filtering: RLS is slower (extra policy check per row) but provides a safety net. We use both.
- TimescaleDB vs ClickHouse for location history: TimescaleDB integrates with PostgreSQL tooling (familiar, SQL); ClickHouse would give better analytical query performance at extreme scale. Current choice: TimescaleDB unless analytical QPS demands ClickHouse.

## 8. Talk Track (35-45 min)

```
0-3 min:  "Let me clarify a few things..." — ask the 3 questions above, state assumptions.
3-6 min:  Run the estimation: 1,200 write/sec avg, 12,000 read/sec, ~165 TB total storage over 3 years.
6-10 min: Draw the ASCII diagram. "Data flows: carrier feed → Ingestion → Kafka → Validation → FSM → Postgres + TimescaleDB. Reads go through API Gateway → Query Service → Redis → Postgres."
10-15 min: Walk the API. Show the idempotency_key field. Mention 202 Accepted (async).
15-20 min: Data model. Explain why tenant_id is the partition key, and why time-series data goes to TimescaleDB.
20-32 min: Deep dive on multi-tenant isolation (RLS + JWT injection). Then idempotent ingestion (Redis NX + Kafka + DB ON CONFLICT). This is where you'll be challenged — prepare to defend each layer.
32-38 min: Bottlenecks at 10x. Postgres sharding, TimescaleDB tiering, Kafka partition scaling.
38-43 min: Failure modes. Carrier API down, consumer crash, Redis eviction.
43-45 min: Invite questions. "What aspect would you like me to go deeper on?"
```

**Authority hook:** *"I built this at Logward — we handle 10M+ records with enterprise multi-tenancy. Here's what we actually did vs. what I'd change at 10x scale..."* Use this to anchor the conversation in real production experience, then pivot to the design question.

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [TimescaleDB time-series best practices](https://www.youtube.com/results?search_query=timescaledb+system+design+time+series)
- [Confluent Kafka multi-tenancy patterns](https://www.confluent.io/blog/)

**Paid (optional):**
- "Designing Data-Intensive Applications" by Martin Kleppmann — Chapter 11 (stream processing) is directly relevant
- [ByteByteGo](https://bytebytego.com) — event-driven architecture patterns

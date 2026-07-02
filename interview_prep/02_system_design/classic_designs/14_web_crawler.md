# Web Crawler

> Appears at: Google (very common — it's their home turf), Amazon L6, Atlassian. Tests how you think about politeness, distributed coordination, and dedup at scale. The trap is treating it as "a loop that fetches URLs." The real interview is the **URL frontier** (politeness + priority) and **dedup** (have I seen this URL/content). Be a good citizen, not a DDoS bot.

## 1. Requirements

**Functional:**
- Given a set of seed URLs, crawl the web: fetch a page, extract links, enqueue new links, repeat (BFS).
- Store the fetched content (HTML) for downstream consumers (search index, ML training).
- Extract and store the link graph (which page links to which).
- Respect `robots.txt` (allow/disallow rules, crawl-delay).
- Politeness: never hammer a single host — bound requests per host.
- Recrawl: revisit pages to keep content fresh (news changes hourly, archives never).

**Non-functional:**
- Scale: ~1B pages/month. Politeness-bound, not CPU-bound.
- Robustness: crawler traps (infinite calendars, session-id loops), malformed HTML, slow/dead hosts must not stall the whole fleet.
- Extensibility: pluggable parsers (HTML today, PDF/images later).
- Distributed: hundreds of worker machines coordinating on a shared frontier.

**Clarifying questions:**
1. "HTML only, or also images/PDF/video?" → HTML for the link graph; store other content types as opaque blobs, don't parse.
2. "Is freshness in scope, or one-shot crawl?" → Continuous with recrawl. This is what makes the frontier interesting.
3. "Do we render JavaScript?" → Out of scope for v1 (headless-browser rendering is 10x the cost). Fetch raw HTML.
4. "Politeness as a hard constraint?" → Yes. Getting a domain to block our IP range is a P0 failure.

## 2. Back-of-Envelope Estimation

```
Pages/month:      1B = ~385 pages/sec average
Peak (2x):        ~770 pages/sec

Per-page work:
  avg HTML size:        ~500 KB raw (compress to ~100 KB stored)
  links extracted:      ~50 outlinks/page

Fetch bandwidth:        385 pages/sec x 500 KB = ~190 MB/sec = ~1.5 Gbps sustained
Storage (raw, 1 mo):    1B x 100 KB compressed = ~100 TB/month in blob store
Link graph:             1B x 50 links x ~20 B (src_id, dst_id) = ~1 TB/month

URL-seen set (dedup):   We DISCOVER far more URLs than we crawl.
                        1B crawled x 50 outlinks = 50B URL references/month,
                        ~10B of them unique. Need a cheap "seen?" check for 10B URLs.
                        (See 6b — a bloom filter does this in ~12 GB.)

Worker count:           If one worker does ~5 fetches/sec (network-bound, polite waits),
                        need 770 / 5 = ~150 fetcher workers at peak.
DNS:                    Naive = 1 DNS lookup/fetch = 385 QPS to resolvers (50ms each)
                        => DNS becomes the bottleneck. Must cache aggressively (6c).
```

The headline: this system is **I/O- and politeness-bound**, not compute-bound. You could fetch 100x faster than 385/sec technically — politeness is what caps you. Your job is to maximize throughput *within* the good-citizen envelope.

## 3. API Design (internal interfaces + config)

A crawler has no public REST API. The "API" is the contract between components and the operator-facing config.

```python
# --- URL Frontier: the heart of the system ---
class URLFrontier:
    def add_url(self, url: str, priority: int) -> None: ...   # enqueue a discovered URL
    def get_next_url(self) -> str | None: ...                 # worker pulls next *crawlable* URL
                                                              #   (respects per-host readiness)
    def mark_done(self, url: str, host: str) -> None: ...      # frees the host for its next fetch

# --- Fetcher / Worker ---
class Fetcher:
    def fetch(self, url: str) -> FetchResult: ...   # FetchResult{status, headers, body, fetch_time}

# --- Parser ---
class Parser:
    def extract_links(self, base_url: str, html: bytes) -> list[str]: ...
    def content_fingerprint(self, html: bytes) -> int: ...   # SimHash, see 6b

# --- Dedup ---
class SeenSet:
    def seen(self, url_or_hash: str) -> bool: ...   # bloom-filter check
    def add(self, url_or_hash: str) -> None: ...

# --- Robots ---
class RobotsCache:
    def allowed(self, url: str, agent="LogwardBot") -> bool: ...
    def crawl_delay(self, host: str) -> float: ...   # seconds; default 1.0 if unset
```

```yaml
# Operator config (the knobs that matter)
user_agent:          "LogwardBot/1.0 (+https://logward.com/bot)"   # identify yourself!
default_crawl_delay: 1.0          # seconds between hits to the same host
max_pages_per_host:  10000        # avoid getting lost in one giant site
max_url_depth:       20           # crawler-trap guard
max_url_length:      2048         # reject pathological URLs
recrawl_policy:      adaptive     # see 6c
respect_robots:      true         # non-negotiable
```

## 4. High-Level Architecture

```
                 seed URLs
                    │
                    ▼
        ┌───────────────────────┐
        │     URL FRONTIER      │   priority + politeness queues (Mercator)
        │  front-Qs (priority)  │   <─── prioritizer (PageRank, freshness)
        │  back-Qs  (per-host)  │
        └───────────┬───────────┘
                    │ get_next_url()  (host is "ready", crawl-delay elapsed)
                    ▼
   ┌──────────────────────────────────┐
   │   FETCHER WORKERS (sharded by     │
   │   host-hash; ~150 of them)        │
   └───┬───────────────┬───────────────┘
       │               │
   robots.txt      DNS resolver
   cache (6c)      + DNS cache (6c)
       │               │
       ▼               ▼
   ┌──────────────────────────────────┐
   │  HTTP GET  →  raw HTML response   │
   └───────────────┬──────────────────┘
                   │
                   ▼
   ┌──────────────────────────────────┐
   │  CONTENT DEDUP (SimHash/checksum) │  near-dup? ── yes ──► drop, don't re-store
   └───────────────┬──────────────────┘
                   │ new content
        ┌──────────┴───────────┐
        ▼                      ▼
   ┌──────────┐         ┌─────────────┐
   │BLOB STORE│         │   PARSER    │  extract <a href> links
   │ (S3): raw│         └──────┬──────┘
   │  HTML    │                │
   └──────────┘                ▼
                      ┌──────────────────┐
                      │  URL-SEEN bloom  │  seen this URL before?
                      │  filter (6b)     │
                      └────────┬─────────┘
                               │ unseen URLs only
                               ▼
                        back to FRONTIER.add_url()
```

**Flow:** Frontier hands a worker a URL whose host is ready → worker checks robots, resolves DNS (cached), fetches → content-dedup → store raw HTML in blob store + parse links → each link checked against URL-seen bloom → unseen ones go back into the frontier with a computed priority. The loop is closed; seeds prime it.

## 5. Data Model

The crawler's "database" is mostly queues, a blob store, and probabilistic sets — not a relational schema. But you do persist metadata.

```sql
-- Crawl metadata (Postgres / Cassandra). Shard key: hash(host)
-- Co-locating a host's rows on one shard makes politeness + recrawl decisions local.
CREATE TABLE crawled_urls (
  url_hash      BYTEA PRIMARY KEY,        -- 16-byte hash of normalized URL
  url           TEXT NOT NULL,
  host          TEXT NOT NULL,            -- shard key
  http_status   INT,
  content_hash  BYTEA,                    -- SimHash/checksum for content dedup
  blob_key      TEXT,                     -- S3 key of raw HTML
  fetched_at    TIMESTAMPTZ,
  next_crawl_at TIMESTAMPTZ,              -- recrawl scheduling (6c)
  depth         INT                       -- distance from a seed (trap guard)
);
CREATE INDEX idx_recrawl ON crawled_urls(host, next_crawl_at);
```

```
# Blob store (S3): raw fetched content
key:   <host>/<url_hash>          # partition by host
value: gzip(raw HTML bytes)       # ~100 KB compressed

# Link graph (Cassandra / adjacency list). Partition key: src_url_hash
src_url_hash  →  [dst_url_hash, dst_url_hash, ...]   # used later for PageRank

# URL-seen set (bloom filter, in memory / RocksDB) — NOT a row store
# robots.txt cache (Redis): host → {rules, crawl_delay, fetched_at}, TTL ~24h
```

**Why shard by host:** every politeness decision ("when did I last hit example.com?"), every robots lookup, and most recrawl scheduling is *per-host*. Sharding by host keeps that state on one machine — no cross-shard coordination for the hot path. (Same instinct as sharding by partition key in [the Kafka design](06_distributed_message_log_kafka.md).)

## 6. Deep Dives

### 6a. The URL Frontier — priority + politeness (Mercator design)

The frontier is the crawler. It answers one question: *"which URL should a worker fetch next, such that we crawl important pages first AND never hammer a host?"* Two competing goals → two stages of queues.

```
                discovered URLs
                      │
                      ▼
   ┌─────────── FRONT QUEUES (prioritization) ───────────┐
   │  F1 (highest prio) ... Fk (lowest)                  │
   │  A URL's priority p = f(PageRank, freshness, depth) │
   │  Prioritizer drops the URL into queue F_p.          │
   └──────────────────────┬──────────────────────────────┘
                          │  biased picker: pulls from
                          │  high-prio front-Qs more often
                          ▼
   ┌─────────── BACK QUEUES (politeness) ────────────────┐
   │  B1 ... Bm   — each back-queue holds URLs for        │
   │               EXACTLY ONE host (invariant).          │
   │  host→queue mapping table: example.com → B7          │
   │                                                      │
   │  Priority heap of (next_ready_time, back_queue_id):  │
   │     a worker pops the queue whose host is ready now. │
   └──────────────────────────────────────────────────────┘
```

**Front queues = priority.** Important pages (high PageRank, news that changes often, shallow depth) land in higher-priority front queues. The picker is *biased* toward high-priority queues but still services low ones occasionally (avoid starvation). This is what makes it BFS-with-priority rather than pure FIFO BFS.

**Back queues = politeness.** Invariant: **one back-queue holds URLs for exactly one host.** A worker is bound to a back-queue, so it never has two threads hitting the same host. After fetching, the worker sets that host's `next_ready_time = now + crawl_delay` and pushes it onto a min-heap keyed by ready-time.

```python
import heapq, time

class PolitenessRouter:
    def __init__(self):
        self.heap = []                  # (next_ready_time, back_queue_id)
        self.host_to_queue = {}          # host -> back_queue_id
        self.queues = {}                 # back_queue_id -> deque[url]

    def get_next_url(self):
        # Pop the host that's been waiting longest AND is past its crawl-delay.
        if not self.heap:
            return None
        ready_time, qid = self.heap[0]
        if ready_time > time.time():
            return None                  # nobody ready yet; worker waits/backs off
        heapq.heappop(self.heap)
        url = self.queues[qid].popleft()
        return url, qid

    def mark_done(self, qid, host, crawl_delay):
        # Re-arm this host's queue for its next fetch after the delay.
        if self.queues[qid]:
            heapq.heappush(self.heap, (time.time() + crawl_delay, qid))
```

**robots.txt** is enforced *before* a URL ever enters the frontier (and re-checked, since rules change). Cache parsed robots per host (Redis, ~24h TTL). Honor `Crawl-delay` if present — it overrides your default. Honor `Disallow`. Identify yourself in `User-Agent` so site owners can contact you instead of just blocking you.

**Prioritization signals:** PageRank (or in-degree as a proxy early on), update frequency / freshness, content quality, depth-from-seed. Google's whole edge here is good priority — crawl the important 10% of the web first.

> Politeness vs throughput is the central tension. More back-queues + more hosts in flight = more throughput. But you can never exceed one-in-flight-per-host. So throughput scales with **host diversity**, not worker count. Crawling 1000 hosts at 1 req/sec = 1000 req/sec, politely. Crawling 1 host needs you to crawl at 1 req/sec — adding workers does nothing.

### 6b. Deduplication — URL-seen set + content fingerprinting

Two distinct dedup problems. Don't conflate them.

**(i) URL-seen: "have I already discovered this URL?"** Checked ~50B times/month against ~10B unique URLs. Storing 10B URLs as strings = ~1 TB+ and slow. Use a **bloom filter**: probabilistic set, no false negatives (if it says "not seen," it's definitely new), small false-positive rate (says "seen" when actually new → we skip a real page, acceptable).

```
Bloom filter math (memorize this — it's the money slide):
  n = 10e9 unique URLs
  p = target false-positive rate = 0.01 (1%)

  bits needed:   m = -n * ln(p) / (ln 2)^2
               = -10e9 * ln(0.01) / 0.4805
               = 10e9 * 4.605 / 0.4805
               ≈ 9.58e10 bits ≈ 12 GB        <-- fits in RAM on one big box!

  optimal hashes: k = (m/n) * ln 2 = 9.58 * 0.693 ≈ 7 hash functions

  Compare: 10e9 URLs x ~100 B as strings = 1 TB. Bloom = 12 GB. ~80x smaller.
```

```python
# Conceptual bloom filter
class BloomFilter:
    def __init__(self, m_bits, k_hashes):
        self.bits = bytearray(m_bits // 8)
        self.m, self.k = m_bits, k_hashes
    def _idx(self, item, i):
        return (hash((i, item))) % self.m
    def add(self, item):
        for i in range(self.k):
            b = self._idx(item, i); self.bits[b // 8] |= (1 << (b % 8))
    def __contains__(self, item):       # False => DEFINITELY not seen (no false negatives)
        return all(self.bits[(b:=self._idx(item,i)) // 8] & (1 << (b % 8)) for i in range(self.k))
```

Always **normalize the URL first** (lowercase host, strip default ports, sort query params, drop fragments `#...`, resolve `.`/`..`) so `Example.com/a?b=1&c=2` and `example.com/a?c=2&b=1` dedup to the same key. Distributed: shard the bloom filter by `hash(url) % N`, or back it with RocksDB if it must exceed RAM. (Bloom filters also show up in [the distributed cache design](02_distributed_cache.md) for "don't bother hitting the DB.")

**(ii) Content dedup: "is this page near-identical to one I already stored?"** The web is full of mirrors, syndicated articles, and print-vs-mobile variants of the same content at different URLs. Exact checksum (MD5 of body) catches byte-identical dupes only. For *near*-duplicates use **SimHash**: a locality-sensitive hash where similar documents produce hashes with small Hamming distance.

```python
def simhash(tokens, bits=64):
    v = [0] * bits
    for tok in tokens:                       # tokens = shingles / words of the page
        h = hash(tok)
        for i in range(bits):
            v[i] += 1 if (h >> i) & 1 else -1
    fp = 0
    for i in range(bits):
        if v[i] > 0: fp |= (1 << i)
    return fp                                # two near-dup pages => Hamming distance < ~3

def near_duplicate(fp_a, fp_b, threshold=3):
    return bin(fp_a ^ fp_b).count("1") <= threshold
```

If a fetched page's SimHash is within Hamming distance ~3 of one we've stored, treat it as a duplicate: don't re-store the blob, don't re-extract links. Saves storage and avoids re-crawling mirror farms.

### 6c. Distributed coordination, DNS, and robustness

**Sharding the crawl by host hash.** Each worker (or shard) owns a slice of hosts: `worker_id = hash(host) % num_workers`. This gives you three wins for free: (1) all of a host's politeness state lives on one worker — no distributed lock to enforce crawl-delay; (2) robots.txt for a host is cached on exactly one worker; (3) clean horizontal scaling — add workers, rebalance the host→worker map (consistent hashing so a worker join/leave only moves 1/N of hosts — same technique as [the distributed cache](02_distributed_cache.md)).

**DNS caching.** A naive crawler does one DNS lookup per fetch → at 385 fetches/sec that's 385 DNS QPS, each ~10-200ms, and you'll get rate-limited by resolvers. Since many URLs share a host, cache resolved IPs (respect TTL, but floor it to e.g. 60s). Run a local caching resolver per worker. This collapses DNS from per-page to per-host.

**Crawler traps / infinite spaces.** The adversarial part. Defenses:
- **Depth limit:** drop URLs deeper than `max_url_depth` (e.g. 20) from a seed — calendars generate `?date=2099-12-31` forever.
- **Per-host page cap:** `max_pages_per_host` (e.g. 10K) so one giant/malicious site can't starve the frontier.
- **URL length + pattern limits:** reject absurdly long URLs and obvious session-id / param-explosion loops.
- **Content dedup (6b):** trap pages are often near-identical → SimHash catches and drops them.
- **robots.txt:** honest sites disallow their trap directories; respecting robots avoids many traps for free.

**Recrawl / freshness policy.** Pages change at wildly different rates. An **adaptive** policy estimates change frequency from history: a news homepage seen to change every visit → recrawl hourly; a 2009 archived PDF that never changes → recrawl monthly. Store `next_crawl_at` per URL; a scheduler re-injects URLs into the frontier when due. This is where the priority machinery (6a) and freshness meet — high-churn high-value pages get high priority *and* short recrawl intervals.

**Storing content.** Raw HTML → blob store (S3), keyed by `host/url_hash`, gzipped. Metadata (status, content_hash, blob_key) → the `crawled_urls` table. Extracted links → the link-graph store for downstream PageRank. Keep the crawler itself stateless beyond its queues; persistence lives in S3 + the DBs so a worker crash loses at most the in-flight fetches.

## 7. Bottlenecks, Failure Modes & Trade-offs

**Politeness vs throughput (the headline trade-off).** You are *deliberately* slower than you could be. Throughput scales with host diversity, not hardware. The right answer to "how do we go faster?" is "crawl more distinct hosts concurrently," never "remove the crawl-delay." Being a good citizen — honest User-Agent, robots compliance, crawl-delay, backing off on 429/503 — is what keeps your IPs un-blocked, which is the *real* long-term throughput.

**Frontier is the bottleneck and a SPOF risk.** It holds billions of pending URLs. Persist it (don't keep it purely in RAM) — back queues on disk/RocksDB or a durable queue (Kafka). On restart, reload from the persisted frontier; otherwise a crash forgets the entire crawl. Partition the frontier by host across machines so no single node holds it all.

**Slow / dead hosts.** A host that takes 30s/request or hangs must not block a worker forever. Per-fetch timeout (e.g. 10s), then mark failed and move on. Exponential backoff + retry budget per host; after N failures, quarantine the host. One bad host should never stall the fleet — this is why one back-queue = one host (isolation).

**Hotspot / skew.** A few hosts (huge sites) have millions of pages. The per-host page cap and priority demotion prevent one site from monopolizing the frontier. Conversely, a long tail of tiny hosts means lots of back-queues with one URL each — fine, that's where your parallelism comes from.

**Failure modes:**
- *Worker crash:* loses in-flight fetches only (frontier + S3 are durable). Host map reassigns its hosts to survivors via consistent hashing.
- *DNS resolver down:* cached entries keep serving; new hosts can't be resolved → those URLs retry later. Run redundant resolvers.
- *Bloom filter false positive:* we wrongly skip a new URL. Tunable (lower p → more RAM). Acceptable: missing a page is cheaper than re-crawling the web. Note bloom filters can't delete — periodically rebuild, or use a counting/scalable bloom variant.
- *We accidentally DDoS a site:* the nightmare. Mitigation: hard per-host concurrency = 1, honor crawl-delay, honor `429 Too Many Requests`/`503` with backoff, global per-IP-range rate ceiling as a backstop.

**Trade-offs to voice:** BFS (breadth, fresh important pages first) vs DFS (depth, easy to fall into traps) → priority-BFS wins. Strict politeness (slow, safe) vs aggressive (fast, gets you blocked) → polite wins for any crawler that needs to run for years. Bloom filter (12 GB, 1% FP) vs exact set (1 TB, exact) → bloom wins; the FP cost is negligible.

## 8. Talk Track (35-45 min)

```
0-3 min:   Clarify: HTML-only + opaque blobs for other types; continuous w/ recrawl;
           no JS rendering v1; politeness is a HARD constraint. State scope: 1B pages/mo.
3-7 min:   Estimation: ~385 pages/sec, ~1.5 Gbps, ~100 TB/mo storage, 10B unique URLs to
           dedup, ~150 workers. Land the punchline: politeness-bound, not compute-bound.
7-12 min:  High-level architecture. Draw the loop: Frontier → Fetcher → dedup → blob store
           + parser → URL-seen → back to Frontier. Name robots + DNS as side caches.
12-22 min: DEEP DIVE 6a — URL Frontier. Front queues (priority: PageRank/freshness) +
           back queues (politeness: one host per queue, ready-time min-heap). robots.txt.
           Voice the politeness-vs-throughput trade-off: throughput ~ host diversity.
22-30 min: DEEP DIVE 6b — Dedup. URL-seen bloom filter; DO THE MATH on the whiteboard
           (10B URLs, p=1%, ~12 GB, k=7). Then content dedup: SimHash for near-dupes.
30-37 min: DEEP DIVE 6c — Distributed: shard by host-hash (politeness state local),
           DNS caching (else DNS is the bottleneck), crawler traps (depth + per-host cap +
           dedup), adaptive recrawl, blob storage.
37-42 min: Bottlenecks: frontier persistence/SPOF, slow hosts, skew, "don't DDoS" backoff.
42-45 min: Trade-offs + questions: BFS-priority vs DFS, bloom FP cost, being a good citizen.
```

## Resources

**Free:**
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Hello Interview — Web Crawler](https://www.hellointerview.com)
- [ByteByteGo — Design a Web Crawler](https://www.youtube.com/results?search_query=bytebytego+design+a+web+crawler)
- [NeetCode — Web Crawler system design](https://www.youtube.com/results?search_query=neetcode+web+crawler+system+design)
- The Mercator paper ("A scalable, extensible web crawler") — the origin of the front-queue/back-queue frontier: [search](https://www.youtube.com/results?search_query=mercator+web+crawler+frontier+design)

**Paid (optional):**
- "System Design Interview" by Alex Xu — Chapter: Design a Web Crawler
- [Grokking the System Design Interview](https://www.designgurus.io) — Designing a Web Crawler

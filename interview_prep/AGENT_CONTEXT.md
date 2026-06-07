# Agent Context Document
> For any AI agent or future session picking up this folder. Read this before touching any file.

---

## What This Folder Is

A complete, self-contained interview preparation system for **Rahul Kumar Rai** targeting a move from Logward (54 LPA, Senior Backend Engineer) to a senior big-tech / top-product role at Rs 95L-1.3Cr by ~September 2026. Built June 2026.

**50 markdown files across 6 sections. The folder is now COMPLETE.**

---

## Who Rahul Is (Brief — for tailoring any new content)

- **7+ years** backend engineering. Bangalore, India. NIT Silchar CS 2019.
- **Current:** Logward (Feb 2024–present) — container tracking platform, 10M+ records, enterprise multi-tenant. Built multi-tenant Trigger Service (-60% latency), data validation layer, container lifecycle orchestration.
- **Prior:** 56 AI Technologies (payments, Razorpay Payment Links -70% fraud/effort, Autopay -30% manual ops), PharmEasy (warehouse/supply-chain, B2B Synergy, Purchase Return V2, Atlas platform, on-call ownership), Wipro intern (blockchain).
- **Stack:** Python (primary for interviews), Go, Node.js, TypeScript, Kafka, Redis, PostgreSQL, MongoDB, AWS, Kubernetes.
- **Strengths:** System design (strong), behavioral (good stories exist), DSA (rusty, needs reps).
- **Constraints:** India only, no relocation. Won't accept Amazon SDE II (L6 or nothing). Won't accept bank offer < Rs 75-80L.

---

## Target Companies (Priority Order)

| Company | Level | Est. 4-yr TTC | Priority |
|---------|-------|--------------|----------|
| Confluent | Senior | ~Rs 1.21Cr/yr | PRIMARY — best stack fit (Kafka) |
| Google | L5 | ~Rs 1.1Cr/yr | PRIMARY |
| Uber | Senior | Rs 1.07-1.76Cr/yr | PRIMARY |
| Amazon | SDE III / L6 | ~Rs 1.25Cr/yr | PRIMARY |
| Atlassian | Senior | ~Rs 90L-1.1Cr/yr | PRIMARY — best WLB |
| Goldman Sachs | VP | ~Rs 75-1Cr/yr | LEVERAGE only |
| JPMorgan | VP | ~Rs 70-90L/yr | LEVERAGE only |

**Sequence:** Banks first (weeks 4-6, warm-up reps + competing offer floor) → Tier-1 onsites clustered in weeks 9-11 for offer leverage.

---

## Folder Structure — What Exists

```
interview_prep/
├── README.md                          ← Master index with full TOC (START HERE)
├── AGENT_CONTEXT.md                   ← This file
│
├── 00_strategy/                       ← 5 files, COMPLETE
│   ├── strategy_and_targets.md        ← North star, comp math, decision rules
│   ├── 12_week_plan.md               ← Full calendar Jun 8 – Aug 30, 2026
│   ├── daily_plan.md                 ← Day-by-day Phase 1; weekly rhythm template
│   ├── company_playbooks.md          ← Per-company interview structure + tips
│   └── application_tracker.md        ← Tracking table, referral drafts
│
├── 01_dsa/                           ← 21 files, COMPLETE
│   ├── README.md                     ← DSA hub, 19-pattern checklist, frameworks
│   ├── templates.md                  ← ~20 Python 3 templates (copy-pasteable)
│   └── patterns/                     ← 19 pattern files (01 through 19)
│       ├── 01_two_pointers_sliding_window.md
│       ├── 02_hashing_frequency.md
│       ├── 03_binary_search.md
│       ├── 04_stack_monotonic.md
│       ├── 05_linked_list.md
│       ├── 06_trees_bst.md
│       ├── 07_trie.md
│       ├── 08_heap_topk_mergek.md
│       ├── 09_graph_bfs_dfs.md
│       ├── 10_topological_sort.md
│       ├── 11_union_find.md
│       ├── 12_shortest_path.md
│       ├── 13_backtracking.md
│       ├── 14_intervals_sweep_line.md
│       ├── 15_dp_1d.md
│       ├── 16_dp_2d_grid.md
│       ├── 17_knapsack_subset.md
│       ├── 18_greedy.md
│       └── 19_bit_manipulation.md
│
├── 02_system_design/                 ← 15 files, COMPLETE
│   ├── README.md                     ← SD hub, framework overview
│   ├── framework_and_estimation.md   ← 8-step framework, latency table, formulas, checklist
│   ├── fundamentals.md               ← Building blocks (caching, Kafka deep, sharding, CAP, etc.)
│   ├── project_designs/              ← Rahul's 4 home designs (biggest edge)
│   │   ├── 1_container_tracking_platform.md
│   │   ├── 2_multitenant_trigger_service.md
│   │   ├── 3_payment_links_reconciliation.md
│   │   └── 4_autopay_recurring_scheduler.md
│   └── classic_designs/              ← 8 classic designs
│       ├── 01_rate_limiter.md
│       ├── 02_distributed_cache.md
│       ├── 03_url_shortener.md
│       ├── 04_news_feed_fanout.md
│       ├── 05_typeahead_autocomplete.md
│       ├── 06_distributed_message_log_kafka.md  ← Deep; for Confluent
│       ├── 07_ride_dispatch_matching.md          ← Deep; for Uber
│       └── 08_distributed_job_scheduler.md
│
├── 03_behavioral/                    ← 5 files, COMPLETE
│   ├── README.md                     ← Hub, STAR format, rehearsal protocol
│   ├── story_bank.md                 ← 18 fully-drafted STAR stories (13 real + 5 gap)
│   ├── amazon_leadership_principles.md ← All 16 LPs, story mappings, coverage matrix
│   ├── per_company_framing.md        ← Reframing per company + "Why X" drafts
│   └── behavioral_question_bank.md   ← ~40 questions, "tell me about yourself" script
│
├── 04_ai_fluency/                    ← 1 file, COMPLETE
│   └── ai_fluency_drills.md          ← 4 drills for 2026 AI-fluency round
│
└── 05_resources/                     ← 2 files, COMPLETE
    ├── master_resource_list.md        ← All resources by section, free first
    └── negotiation_playbook.md        ← Comp math, Amazon vesting trap, 5 scripts
```

---

## Known Issues / Inconsistencies to Fix (if agent picks up)

1. **12_week_plan.md uses old file references:** It links to `../01_dsa/patterns/01_arrays_hashing.md`, `02_two_pointers.md`, `03_sliding_window.md`, etc. — these paths don't exist. The actual files are named `01_two_pointers_sliding_window.md`, `02_hashing_frequency.md`, etc. A future agent should update the links in `12_week_plan.md` (and `daily_plan.md` if it has the same issue) to match the actual file names.

2. **daily_plan.md links may have the same stale pattern references** — verify and fix to match actual `patterns/` filenames.

3. **Verify:** DSA pattern files 01-19 all exist and have content (confirmed: 370+ lines in pattern 01). No empty files found.

---

## Design Decisions / What NOT to Change

- **All Python code in DSA files is Python 3, standard library only** — do not add dependencies.
- **All links follow the link policy:** LeetCode slugs only (no `/problems/two-sum/description/` variants), YouTube search URLs (no fabricated video IDs), free alternatives always present when a paid resource is mentioned.
- **Story bank uses first person "I"** throughout — do not change to "we" in edits.
- **System design files use the 8-section SD template** (Requirements → Estimation → API → Architecture → Data Model → Deep Dives → Bottlenecks → Talk Track) — maintain this structure for any new designs.
- **Tone throughout is second-person coaching** ("you", "your") where addressing Rahul, not third-person.

---

## If You Are an Agent Completing a Specific Task

Before writing any file:
1. Read this document fully.
2. `find /Users/rahul/Desktop/Logward/learning-service/interview_prep -type f -name "*.md"` to see what exists.
3. Read the specific file you're editing (if it already exists) before modifying.
4. Follow the link policy strictly — no fabricated YouTube video IDs.
5. Match the format of adjacent files (DSA pattern files all share the same section structure).

**Use the Write tool** for new files. **Use the Edit tool** for modifying existing files (requires reading first). Bash is available for checking file existence.

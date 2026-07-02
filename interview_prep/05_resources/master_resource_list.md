# Master Resource List

> Curated by section. FREE options listed first. Paid options are clearly marked. "If you only have time for 3 things" shortlist at the bottom of each section.

---

## 1. Coding / DSA

### Free
| Resource | URL | What it is |
|----------|-----|------------|
| NeetCode 150 / Roadmap | https://neetcode.io/roadmap | 150 curated problems with free video solutions; organized by pattern |
| NeetCode Practice | https://neetcode.io/practice | All 150 problems in one place with progress tracking |
| Blind 75 (LeetCode list) | https://leetcode.com/discuss/general-discussion/460599/blind-75-leetcode-questions | The original curated 75 — minimal, high-signal |
| LeetCode Company Tags (Free) | https://leetcode.com/problemset/ | Filter by company (some require Premium) |
| LeetCode Explore Cards | https://leetcode.com/explore/ | Free topic-by-topic courses with problems |
| LeetCode Study Plans | https://leetcode.com/studyplan/ | Free 30/60/90 day plans organized by topic |

### Paid (optional)
| Resource | URL | Note |
|----------|-----|------|
| LeetCode Premium | https://leetcode.com/subscribe/ | Company-tagged problems, frequency data |
| AlgoMonster | https://algo.monster | Pattern-first approach, paid but efficient |
| Grokking the Coding Interview | https://www.designgurus.io | Pattern-based, 16 patterns covered |
| educative.io | https://www.educative.io | Interactive courses; Grokking series |

### If you only have time for 3 things:
1. **NeetCode 150** — the curriculum; video explanations are excellent
2. **LeetCode company-tagged problems** for Google/Confluent/Uber/Amazon (some free, some Premium)
3. **Your DSA patterns folder** — `01_dsa/patterns/` — this is your reference, not NeetCode

---

## 2. System Design

### Free
| Resource | URL | What it is |
|----------|-----|------------|
| System Design Primer | https://github.com/donnemartin/system-design-primer | Most comprehensive free SD resource; start here |
| ByteByteGo YouTube | https://www.youtube.com/results?search_query=bytebytego+system+design | Concise visual walkthroughs; 10-15 min videos |
| Hello Interview | https://www.hellointerview.com | Structured SD interview practice; free articles |
| Confluent Engineering Blog | https://www.confluent.io/blog/ | Kafka at scale; real production insights |
| Uber Engineering Blog | https://www.uber.com/en-US/blog/engineering/ | Dispatch, geo, microservices at extreme scale |
| Netflix Tech Blog | https://netflixtechblog.com | Streaming, CDN, resilience patterns |
| Stripe Engineering Blog | https://stripe.com/blog/engineering | Payments, idempotency, reliability |
| Martin Fowler's Blog | https://martinfowler.com | Architecture patterns, microservices, event sourcing |

### 🆓 Free Grokking-Equivalent Curriculum

> You don't need to buy Grokking. Between your own files + the four pillars below, you have a complete, legal, no-cost curriculum covering 100% of the Grokking question bank. Use the paid course (listed under "Paid") only as an optional cross-check.

**The four pillars (cover ~everything — start here):**
1. **Your own designs** — [../02_system_design/classic_designs/](../02_system_design/classic_designs/) files 01–21 + your 4 home designs. This *is* the Grokking bank, written out. Primary resource.
2. **System Design Primer** — https://github.com/donnemartin/system-design-primer — free, MIT-licensed; the building-blocks + several full designs.
3. **Hello Interview** — https://www.hellointerview.com/learn/system-design — free written walkthroughs by ex-Meta/Amazon staff; as good as Grokking, arguably better for interview framing.
4. **ByteByteGo YouTube** — https://www.youtube.com/@ByteByteGo — Alex Xu's free animated breakdowns of most designs.

**Per-design map — best free VIDEO + best free WRITTEN walkthrough** (YouTube entries are search links so they survive video re-uploads):

| Grokking design | Your file | Free VIDEO | Free WRITTEN walkthrough |
|-----------------|-----------|------------|--------------------------|
| Chat / Messenger | [09](../02_system_design/classic_designs/09_chat_messaging_whatsapp.md) | https://www.youtube.com/results?search_query=gaurav+sen+design+whatsapp | https://www.hellointerview.com/learn/system-design/problem-breakdowns/whatsapp |
| Twitter | [10](../02_system_design/classic_designs/10_twitter_timeline.md) | https://www.youtube.com/results?search_query=bytebytego+design+twitter | https://www.hellointerview.com/learn/system-design/problem-breakdowns/tweet |
| YouTube / Netflix | [11](../02_system_design/classic_designs/11_video_streaming_youtube.md) | https://www.youtube.com/results?search_query=bytebytego+design+youtube | https://netflixtechblog.com (Netflix Tech Blog — encoding/CDN posts) |
| Instagram | [12](../02_system_design/classic_designs/12_photo_sharing_instagram.md) | https://www.youtube.com/results?search_query=bytebytego+design+instagram | https://github.com/donnemartin/system-design-primer |
| Dropbox / Drive | [13](../02_system_design/classic_designs/13_file_storage_dropbox.md) | https://www.youtube.com/results?search_query=bytebytego+design+google+drive | https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox |
| Web Crawler | [14](../02_system_design/classic_designs/14_web_crawler.md) | https://www.youtube.com/results?search_query=gaurav+sen+web+crawler+system+design | https://github.com/donnemartin/system-design-primer |
| Proximity / Yelp | [15](../02_system_design/classic_designs/15_proximity_service_yelp.md) | https://www.youtube.com/results?search_query=bytebytego+proximity+service | https://www.uber.com/en-US/blog/engineering/ (geo / H3 posts) |
| Notification system | [16](../02_system_design/classic_designs/16_notification_system.md) | https://www.youtube.com/results?search_query=bytebytego+notification+system | https://github.com/donnemartin/system-design-primer |
| Ticketmaster / booking | [17](../02_system_design/classic_designs/17_ticketmaster_booking.md) | https://www.youtube.com/results?search_query=hello+interview+ticketmaster+system+design | https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster |
| Unique ID generator | [18](../02_system_design/classic_designs/18_unique_id_generator.md) | https://www.youtube.com/results?search_query=bytebytego+unique+id+generator+snowflake | https://github.com/donnemartin/system-design-primer |
| Google Docs / collab | [19](../02_system_design/classic_designs/19_collaborative_editor_google_docs.md) | https://www.youtube.com/results?search_query=operational+transformation+vs+crdt | https://www.hellointerview.com/learn/system-design (collaborative editing) |
| Blob store / S3 | [20](../02_system_design/classic_designs/20_blob_store_s3.md) | https://www.youtube.com/results?search_query=bytebytego+design+s3+object+storage | https://github.com/donnemartin/system-design-primer |
| Distributed search | [21](../02_system_design/classic_designs/21_distributed_search.md) | https://www.youtube.com/results?search_query=elasticsearch+internals+inverted+index | https://www.elastic.co/blog (inverted index / sharding posts) |

> For the original 8 (files 01–08), search `bytebytego <topic>` or `neetcode <topic> system design` on YouTube + the matching System Design Primer section.

**Real-systems depth = your Confluent edge (the "Advanced" Grokking content, all free):**
Read the primary papers — they're free PDFs and beat any course summary: **Kafka**, **Amazon Dynamo**, **Cassandra**, **Google Bigtable**, **GFS**, **Spanner**, **MapReduce**. Pair with the **Confluent**, **Uber**, **Netflix**, and **Stripe** engineering blogs (URLs in the Free table above). Search e.g. `kafka paper jay kreps the log` or `dynamo paper amazon`.

**Legitimate ways to see the paid course free/cheap:** Educative offers a free 7-day trial + frequent 50–70% annual sales; Design Gurus discounts on Black Friday and via student email. Don't use pirated dumps — they're a known malware vector and infringe copyright.

### Paid (optional)
| Resource | URL | Note |
|----------|-----|------|
| ByteByteGo | https://bytebytego.com | Alex Xu's books + newsletter; best bang/buck for SD |
| Grokking the System Design Interview | https://www.designgurus.io | The source course; Rahul's files 09–21 mirror its question bank |
| Grokking (educative.io edition) | https://www.educative.io/courses/grokking-the-system-design-interview | Same course on educative; interactive |
| "System Design Interview" Vol 1 & 2 | (books by Alex Xu) | Chapter-per-design; the best paid companion to your files |
| "Designing Data-Intensive Applications" | (book by Martin Kleppmann) | The definitive reference; read chs 5-12 |

### If you only have time for 3 things:
1. **System Design Primer** — read the overview and the designs relevant to your targets
2. **Your project_designs/ folder** — these are your home designs; own them cold
3. **ByteByteGo YouTube** for classic designs you haven't studied

---

## 3. Behavioral

### Free
| Resource | URL | What it is |
|----------|-----|------------|
| Amazon Leadership Principles | https://www.amazon.jobs/content/en/our-workplace/leadership-principles | Read every word. This is the curriculum for Amazon. |
| Dan Croitor — Amazon LP coaching | https://www.youtube.com/results?search_query=dan+croitor+amazon+leadership+principles | Best free YouTube resource for Amazon behavioral prep |
| Exponent YouTube | https://www.youtube.com/results?search_query=exponent+behavioral+interview+amazon | Mock behavioral interview walkthroughs |
| Pramp | https://www.pramp.com | Free peer-to-peer mock interviews (behavioral + coding) |
| interviewing.io (free tier) | https://interviewing.io | Anonymous mocks; free trial available |

### Paid (optional)
| Resource | URL | Note |
|----------|-----|------|
| Exponent (paid) | https://www.tryexponent.com | Structured prep + expert mock interviews |
| "Cracking the Coding Interview" | (book by Gayle McDowell) | Behavioral chapter is underrated |

### If you only have time for 3 things:
1. **Your story_bank.md** — 18 drafted STAR stories; deliver them out loud until they're fluid
2. **Amazon LP page** — map every LP to a story before any Amazon loop
3. **Pramp** — do 3+ behavioral mocks before going live

---

## 4. Mock Interviews

### Free
| Resource | URL | What it is |
|----------|-----|------------|
| Pramp | https://www.pramp.com | Free peer mocks; coding + behavioral + system design |
| interviewing.io (free trial) | https://interviewing.io | Anonymous mocks with engineers from FAANG |
| LeetCode Mock Interview | https://leetcode.com/interview/ | Self-timed mock with timer and coding environment |
| NeetCode Mock | https://neetcode.io/practice | Practice with timer |
| A trusted engineer friend | — | Schedule a weekly 45-min mock from week 5 on |

### Paid (optional)
| Resource | URL | Note |
|----------|-----|------|
| interviewing.io (paid) | https://interviewing.io | Expert mocks with feedback; $100-225/session |
| Exponent (paid) | https://www.tryexponent.com | SD and PM mocks with structured feedback |

### If you only have time for 3 things:
1. **Pramp** — start in week 5; 2 mocks/week in weeks 9-12
2. **interviewing.io free trial** — 1-2 company-specific mocks before your real loops
3. **Self-timed LeetCode sessions** — simulate the real environment (no hints, 45 min)

---

## 5. Comp Data

| Resource | URL | What it is |
|----------|-----|------------|
| levels.fyi | https://www.levels.fyi | Crowdsourced total comp by company, level, location — the best data |
| Glassdoor | https://www.glassdoor.co.in | Salary ranges + interview reviews |
| LinkedIn Salary | https://www.linkedin.com/salary/ | Role-based salary data in India |
| Grapevine (India) | https://www.grapevine.in | India-specific tech salary discussions |
| Blind | https://www.teamblind.com | Anonymous comp discussions; noisy but useful for real numbers |

**How to use levels.fyi:** Filter by company → level (L5/L6/Senior) → India. Look at base, RSU (4-yr total), sign-on, bonus. Compute 4-year average, not year-1 number.

### If you only have time for 3 things:
1. **levels.fyi** — know the 4-yr TTC for Google L5, Amazon L6, Confluent Senior before any offer
2. **Your negotiation_playbook.md** — have your scripts ready
3. **Glassdoor** for interview experience reviews

---

## 6. AI Fluency

| Resource | URL | What it is |
|----------|-----|------------|
| Your ai_fluency_drills.md | ../04_ai_fluency/ai_fluency_drills.md | The 4 drills + validation talking points |
| GitHub Copilot docs | https://docs.github.com/en/copilot | How to use AI in your IDE effectively |
| Claude (Anthropic) | https://claude.ai | Best for code explanation and architecture discussion |
| Anthropic prompt engineering guide | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview | How to write precise, scoped prompts |

### If you only have time for 3 things:
1. **Your ai_fluency_drills.md** — do all 4 drills at least once before week 8
2. **Practice precise prompting** daily (it's a skill, not a one-time read)
3. **Memorize your validation talking points** — "how do you use AI in your workflow" will come up

---

## Master Shortlist: If You Only Have Time for 10 Resources Total

| Priority | Resource | Why |
|----------|----------|-----|
| 1 | **Your DSA patterns folder** (01_dsa/patterns/) | Your curriculum; everything is tailored to you |
| 2 | **NeetCode 150** | Best quality/quantity for pattern practice |
| 3 | **Your story_bank.md** | Behavioral is make-or-break at Amazon |
| 4 | **Your project_designs/** | Your biggest system design edge |
| 5 | **System Design Primer** | The free canonical SD reference |
| 6 | **Amazon LP page** | Read 3x before every Amazon round |
| 7 | **levels.fyi** | Know your numbers before any offer |
| 8 | **Your negotiation_playbook.md** | Never leave money on the table |
| 9 | **Pramp mocks** | Execution under pressure is a separate skill |
| 10 | **Your ai_fluency_drills.md** | New in 2026; don't get blindsided |

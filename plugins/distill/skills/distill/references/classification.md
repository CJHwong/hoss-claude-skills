# Article Classification — Insight vs. Noise

Criteria for deciding which articles deserve extraction and which get skipped. Read this before running classification on scraped content.

## Core Heuristic

Ask one question: **"Can you state a non-obvious takeaway in one sentence that would change how someone thinks about a topic?"**

If yes, it's insight-worthy. If the best you can do is summarize what happened or list things, it's noise.

## Insight-Worthy Signals

### Positive (keep it)

- **Original data or research** — the author ran experiments, collected data, or analyzed something firsthand
- **Novel frameworks** — a new mental model or way of organizing existing knowledge
- **Counterintuitive findings** — conclusions that contradict conventional wisdom, backed by evidence
- **Deep technical explanations** — goes beyond "how to" into "why it works this way"
- **Actionable techniques** — specific methods you can apply, not vague advice
- **Practitioner war stories** — real-world failure/success narratives with concrete lessons

### Negative (skip it)

- **News rehashes** — reporting on an announcement without adding analysis
- **Listicles** — "10 Tools Every Developer Should Know" with one-paragraph blurbs
- **Promotional content** — thinly disguised product pitches or company announcements
- **Shallow overviews** — introductions that never go deeper than Wikipedia
- **Purely procedural tutorials** — step-by-step instructions with no transferable insight ("How to install X on Ubuntu")
- **Aggregator pages** — link roundups, newsletters that just list other articles

## Two-Pass Classification

### Pass 1: Per-Article Assessment

Run immediately after scraping each article. For every article, output:

| Field | Values | Notes |
|-------|--------|-------|
| `insight_worthy` | `yes` / `no` / `unsure` | When torn, use `unsure` — Pass 2 resolves it |
| `confidence` | `high` / `medium` / `low` | How sure you are about the classification |
| `core_insight` | One sentence | Only if `yes` or `unsure`. The non-obvious takeaway. |
| `concept_tags` | 2-3 tags | Lowercase hyphenated. See Concept Tagging below. |
| `rejection_reason` | Short phrase | Only if `no`. Why it failed the heuristic. |

### Pass 2: Batch Grouping

After all articles in a run are classified:

1. Review all `unsure` articles against the `yes` articles — does the unsure article add something the confirmed ones don't?
2. Consolidate synonymous tags (e.g., `llm-evaluation` and `ai-evals` should merge)
3. Propose concept clusters — groups of 3+ articles sharing tags that form a coherent theme
4. Flag any `yes` article whose `core_insight` duplicates another — keep the deeper one

## Few-Shot Examples

### Clear Insight

**Title:** "Why We Moved Off Microservices — A Post-Mortem After 3 Years"
**Signals:** Practitioner war story, original data (their own metrics), counterintuitive (going against the microservices trend)
**Verdict:** `yes`, confidence `high`
**Core insight:** "Microservices introduced more operational overhead than the team could absorb, and the latency tax from inter-service calls negated the scaling benefits for their traffic profile."
**Tags:** `distributed-systems`, `architecture-decisions`

### Clear Noise

**Title:** "OpenAI Announces GPT-5 With Improved Reasoning"
**Signals:** News rehash, no original analysis, summarizes a press release
**Verdict:** `no`, confidence `high`
**Rejection reason:** News announcement, no original analysis

### Borderline — Leans Yes

**Title:** "A Practical Guide to Database Indexing Strategies"
**Signals:** Starts procedural, but includes benchmarks the author ran on real datasets and a decision framework for choosing index types based on query patterns
**Verdict:** `unsure` → resolved to `yes` in Pass 2
**Core insight:** "Composite index column order should follow selectivity (most selective first), not query frequency — the author's benchmarks show 3-10x improvement."
**Tags:** `databases`, `performance-optimization`

### Borderline — Leans No

**Title:** "7 Rust Features That Will Blow Your Mind"
**Signals:** Listicle format, but some items include genuinely deep explanations of ownership semantics
**Verdict:** `unsure` → resolved to `no` in Pass 2
**Rejection reason:** Deep content buried in listicle structure; the good parts are better covered by dedicated articles already tagged

## Concept Tagging

### Format Rules

- Lowercase, hyphenated: `distributed-systems`, `llm-evaluation`, `api-design`
- Broad enough to cluster (not `rust-ownership-semantics`, just `rust` or `memory-management`)
- Narrow enough to mean something (not `programming` or `technology`)
- 2-3 tags per article, no more

### Source Tags as Hints

Some sources carry user-applied tags (Pocket tags, Raindrop collections, browser bookmark folders). Use these as hints when generating concept tags, but don't copy them verbatim:
- A Pocket tag `python` confirms the topic. Use it.
- A Pocket tag `to-read` is status metadata, not a concept. Ignore it.
- A bookmark folder `Engineering` is too broad. Derive a more specific concept from the content.

### Cross-Run Vocabulary

Concept tags accumulate over time. Before inventing a new tag:

1. Check existing vault notes for tags that cover the same concept
2. If a near-synonym exists, use the existing one
3. Only create a new tag when nothing in the vocabulary fits

A vocabulary of 30-50 tags is healthy. Over 100 means you're tagging too narrowly.

## Gotchas

### Good Title, Shallow Content

A compelling title like "The Hidden Cost of Technical Debt" might lead to a 500-word blog post that says nothing beyond "tech debt is bad." **Classify based on content, not title.** The core heuristic applies to what the article actually delivers.

### Deep Content, Clickbait Title

The inverse: "You Won't Believe What Happened When We Rewrote Our Queue" might contain genuine performance analysis with numbers. Don't penalize good content for bad titles.

### GitHub READMEs

A repository README can be insight-worthy if it explains *why* the tool exists and what problem it solves in a non-obvious way. A README that's just installation instructions and API docs is not. Judge by the README content, not by the fact that it's on GitHub.

### Recency Bias

New doesn't mean insightful. A 2019 article with original research is more valuable than a 2024 hot take. Don't boost articles just because they're recent.

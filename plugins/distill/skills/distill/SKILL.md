---
name: distill
description: Distill insights from browser bookmarks/history, bookmark exports, URL lists, or read-later services into an Obsidian-compatible knowledge base. Use this skill when a user mentions extracting insights from browsing history, building a knowledge base from bookmarks, organizing saved links, processing a Pocket/Raindrop export, sorting through URLs, or distilling articles.
---

# Distill

Distill insights from any collection of URLs into a growing Obsidian-compatible knowledge base. Works with browser history, bookmark exports, read-later services, or plain URL lists.

Two outputs per run:
1. **Insight notes** in `{topic}/` folders with YAML frontmatter, key takeaways, and concept tags.
2. **Noise log** (`_noise.md`) listing every article-candidate URL that was classified as not insight-worthy.

## Supported Sources

| Source | How to provide | Adapter |
|--------|---------------|---------|
| **Zen Browser** | Auto-detect profile, read `places.sqlite` | `references/browser-schemas.md` (Firefox schema) |
| **Firefox** | Auto-detect profile, read `places.sqlite` | Same schema as Zen |
| **Chrome / Arc / Brave / Edge** | Auto-detect profile, read `History` DB | `references/browser-schemas.md` (Chromium schema) |
| **Safari** | Read `History.db` | `references/browser-schemas.md` (Safari schema) |
| **Bookmark HTML export** | User provides file path | Parse Netscape bookmark format |
| **Pocket / Raindrop / Instapaper export** | User provides CSV/JSON file | Parse export format |
| **Plain URL list** | User provides text file or pastes URLs | One URL per line |

On first run, ask the user what source to use. If they just say "my bookmarks" or "my history," auto-detect installed browsers and ask which one.

## How This Works

The pipeline runs in 8 phases. Phases 1-7 are automated. Phase 8 is interactive review.

Read `references/pipeline.md` for detailed phase-by-phase instructions.

| Phase | What | How | LLM? |
|-------|------|-----|------|
| 1. Identify Source | Ask user for source, detect browser, extract URLs | Interactive + code | No |
| 2. Domain Triage | Classify domains as article-source/tool/mixed | Deterministic rules + Haiku | Haiku |
| 3. URL Triage | Filter mixed-domain URLs by title + path | Deterministic rules + Haiku | Haiku |
| 4. Scrape | Fetch article content | `curl` with parallel workers | No |
| 5. Extract Text | Strip HTML to plain text, filter short pages | Python | No |
| 6. Classify | Read content, judge insight vs noise | Sonnet | Sonnet |
| 7. Export | Write insight notes + noise log | File I/O | No |
| 8. Review + Restructure | Present summary, user overrides, consolidate folders | Interactive | Session model |

## Key Architecture Decisions (learned from production runs)

### Scraping: curl, not WebFetch

**WebFetch through LLM agents is unreliable at scale.** Agents timeout, die mid-scrape, and waste tokens on HTTP overhead. Instead:
- Phase 4 uses `curl` with 20 parallel workers via Python's ThreadPoolExecutor
- 10-second timeout per URL, no retries
- Scraping 1,600 URLs takes ~2 minutes and zero LLM tokens
- Results saved to temp files on disk, then fed to classification agents

This separation (scrape with code, classify with LLM) is the single most important reliability improvement.

### SQL filter: minimal (browser sources only)

For browser history sources, don't over-filter at the SQL level. The `visit_count/frecency` filter removes almost nothing. **Domain triage is the real volume reducer** (drops ~70% of URLs). Process all visited URLs and let domain triage handle it.

Bookmarks with `visit_count = 0` (imported/synced but never opened) must also be processed.

### Agent reliability

- **Max 5-10 classification batches per agent.** Agents processing 25+ batches die before writing results.
- **Write results incrementally.** Agents must write to their output JSON after every batch, not accumulate and write at the end.
- **Parallel agents: 2-5 at a time.** More than 5 risks rate limits. Split work into small agents and run in waves.

### Folder consolidation is a separate final step

Different classification agents create inconsistent folder names. After all notes are written, a consolidation step restructures into a clean nested hierarchy. This is NOT part of the per-run pipeline.

## Key Decisions You Make (Not the User)

**Source detection (Phase 1):** If the user doesn't specify, check for installed browsers in order: Zen, Firefox, Chrome, Arc, Brave, Safari. Ask which one.

**Domain triage (Phase 2):** Classify each unique domain as `article-source`, `tool`, or `mixed`. Deterministic rules handle ~80%. Haiku classifies the rest. Cached in `domain-cache.yaml`.

**URL triage (Phase 3):** For `mixed` domains, read title + URL path to decide article vs skip.

**Insight classification (Phase 6):** Sonnet reads scraped text and decides: genuine insight or noise?

**Concept tagging:** Tags emerge from content. Stored in frontmatter `concepts` field.

**Topic grouping:** Notes go into `{topic}/` folders. Topics emerge from content, not a fixed taxonomy.

## Key Decisions the User Makes (Not You)

- **Source** — which browser or file to process. Ask on first run.
- **Vault path** — where to write. Ask on first run.
- **Overrides** — promote noise to insight or demote during review.
- **Folder restructure** — user triggers consolidation when ready.

## Output Format

Each insight article becomes a `.md` file in `{topic}/`:

```markdown
---
url: "https://..."
title: "Article Title"
source: "zen-history" or "chrome-bookmark" or "pocket-export" etc.
date_processed: 2026-04-01
confidence: high
insight_summary: "One-line core takeaway"
concepts:
  - "topic-tag"
---

# Article Title

> [Original](url)

## Key Insight

{2-3 sentence summary of the core takeaway}

## Takeaways

- {bullet points of actionable or notable points}

## Context

{1 paragraph situating the article}

---

{scraped content}
```

The `source` field identifies where the URL came from:
- Browser sources: `{browser}-bookmark` or `{browser}-history` (e.g., `zen-bookmark`, `chrome-history`, `safari-history`)
- Export sources: `pocket-export`, `raindrop-export`, `instapaper-export`
- Manual: `url-list`, `manual`

Never overwrite existing `.md` files.

### Noise Log

`_noise.md` lists article candidates classified as not insight-worthy, grouped by source folder. Users can scan it to catch misclassifications.

## Model Routing

| Phase | Model | Why |
|-------|-------|-----|
| 2. Domain Triage | **Haiku** (for uncached domains only) | Trivial: "blog or dashboard?" |
| 3. URL Triage | **Haiku** (for ambiguous mixed-domain URLs) | Pattern matching on title + path |
| 6. Classify | **Sonnet** | Needs content comprehension |
| 7. Export (note generation) | **Sonnet** | Summarization and extraction |

Phases 1, 4, 5 are pure code. Phase 8 uses the session model.

## State Management

Two state files in the vault root:

**`.distill-state.yaml`** — run config and watermarks:
```yaml
last_run: 2026-04-01T12:00:00
vault_path: /Users/.../Obsidian/Insights
source:
  type: zen                    # or: firefox, chrome, arc, brave, safari, file
  profile_path: ~/Library/...  # for browser sources
  last_bookmark_id: 2405       # browser-specific watermarks
  last_history_timestamp: 1774972539187785
```

**`domain-cache.yaml`** — cached domain classifications (shared across all sources):
```yaml
domains:
  simonwillison.net: article-source
  github.com: mixed
  grafana.hardcoretech.co: tool
```

## Principles

1. **Scrape with code, classify with LLM.** curl for fetching (free, fast, reliable). LLM only for judgment calls.
2. **Domain cache is the scalability lever.** Shared across sources and runs. Only new domains need LLM.
3. **Source-agnostic after Phase 1.** Once URLs are extracted, the pipeline doesn't care where they came from.
4. **Small agents, incremental writes.** Max 10 batches per agent. Write after every batch.
5. **Interactive only at Phase 1 and Phase 8.** Phase 1 asks what to process. Phase 8 reviews results. Everything between is automated.
6. **Never overwrite existing notes.** Check before writing.
7. **Tags emerge from content.** No pre-defined categories.
8. **Noise is expected.** 10-20% insight rate from article candidates.
9. **State file updates last.** Only after user approves the review.
10. **Folder consolidation is separate.** Clean up after, not during.

## References

- `references/pipeline.md` — Phase-by-phase execution with edge cases
- `references/classification.md` — Insight vs noise classification guide
- `references/browser-schemas.md` — Browser database schemas (Firefox, Chromium, Safari)

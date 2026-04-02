# Distill — Detailed Pipeline

Phase-by-phase instructions with edge cases and gotchas. Reflects lessons learned from processing 76K+ URLs across 33 months of browser history.

## Scripts

The skill includes Python scripts under `scripts/` for the code-heavy phases. These run with zero LLM tokens.

| Script | Phase | What it does |
|--------|-------|-------------|
| `scripts/scrape.py` | 4 | Parallel curl scraping. `python3 scripts/scrape.py candidates.json --output-dir /tmp/scraped --workers 20 --timeout 10` |
| `scripts/extract_text.py` | 5 | HTML-to-text + batch prep. `python3 scripts/extract_text.py scrape-results.json candidates.json --batch-size 20` |
| `scripts/write_vault.py` | 7 | Merge results + write notes. `python3 scripts/write_vault.py ~/Obsidian/Insights results-1.json results-2.json` |
| `scripts/restructure.py` | 8 | Audit folders + find problems. `python3 scripts/restructure.py ~/Obsidian/Insights --audit-only` |

All scripts read from stdin/args and write to disk. No API keys or LLM calls. The LLM-dependent phases (2, 3, 6) are handled by spawning agents with appropriate model routing.

## Phase 1: Identify Source + Extract URLs

This is the only phase that's source-specific. Ask the user what to process, detect the source, extract URLs into a normalized JSON format. Everything after this phase is source-agnostic.

### How It Works

1. Check `.distill-state.yaml` in the vault. If it exists, use the saved source config.
2. If first run, ask the user: "What do you want to process? Browser history, a bookmark export, a URL list?"
3. If they say "browser" or "my bookmarks," auto-detect installed browsers by checking profile paths (see `references/browser-schemas.md`). List what's found, ask which one.
4. Extract URLs using the appropriate adapter.
5. Output: a JSON array of `{url, title, source, date}` saved to `/tmp/distill-workdir/candidates.json`.

### Browser Sources (SQLite)

For any browser source, the flow is:
1. Find the profile directory (see `references/browser-schemas.md` for paths)
2. Copy DB files to `/tmp/distill-workdir/` (WAL copy strategy varies by browser)
3. Run the appropriate SQL queries for bookmarks and history
4. **Timestamps differ per browser** - Firefox uses microseconds since Unix epoch, Chromium uses microseconds since 1601, Safari uses seconds since 2001. See `references/browser-schemas.md` for conversion formulas.

### File Sources

- **Bookmark HTML export:** Parse `<DT><A HREF="...">Title</A>` tags
- **Pocket/Raindrop CSV:** Parse columns for url, title, date, tags
- **Plain URL list:** One URL per line, title fetched during scraping

### Incremental Runs (browser sources)

State file tracks watermarks per source type:
```yaml
source:
  type: zen
  profile_path: ~/Library/...
  last_bookmark_dateAdded: 1774784941635000
  last_history_timestamp: 1774972539187785
```

Only new items (after watermarks) get processed. File-based sources don't have watermarks - they process the entire file each time, deduplicating against existing vault URLs.

### Cross-Source Deduplication

Before passing URLs to Phase 2, deduplicate against:
1. **Existing vault notes** (read URLs from frontmatter)
2. **Existing `_noise.md` entries** (already classified as noise, no need to re-classify)

This prevents wasting scrape + classify effort on URLs already processed from another source (e.g., same article bookmarked in browser AND saved in Pocket).

Normalize URLs before comparing: strip `www.`, trailing slashes, lowercase hostname + path.

### Gotchas

- **Each browser has different timestamp formats.** This is the #1 bug source. Always check `references/browser-schemas.md` before writing queries.
- **Chromium bookmarks are JSON, not SQLite.** Read `{profile}/Bookmarks` file, not the History DB.
- **Safari requires Full Disk Access.** `History.db` is in a protected directory. The user may need to grant permissions.
- **Browser must be copied, not read live.** All browsers lock their DBs while running.
- **Bookmarks with visit_count=0 exist.** Synced/imported bookmarks may never have been opened. Always process them.
- **Same URL from multiple sources.** Dedup before scraping, not after. Scraping is the expensive step.

## Phase 2: Domain Triage

The scalability lever. Classify domains to eliminate tool/app URLs before any scraping or LLM classification.

### Deterministic Rules (no LLM, ~80% of domains)

Apply these first:

| Pattern | Classification |
|---------|---------------|
| `localhost`, `127.0.0.1`, `192.168.*`, `10.*` | tool |
| `about:*`, `chrome:*`, `moz-extension:*` | tool |
| `*.google.com` (mail, calendar, meet, drive, docs, accounts, etc.) | tool |
| `youtube.com`, `music.youtube.com`, `netflix.com`, `spotify.com` | tool |
| `facebook.com`, `twitter.com`, `x.com`, `instagram.com`, `linkedin.com` | tool |
| `*.slack.com`, `*.atlassian.net`, `*.atlassian.com` | tool |
| User's work domains (e.g., `*.gofreight.co`, `*.hardcoretech.co`) | tool |
| `github.com`, `news.ycombinator.com`, `medium.com`, `dev.to` | mixed |

### LLM Classification (Haiku, for uncached unknowns)

For domains not matching deterministic rules and not in the cache, batch them and send to a Haiku agent. Include sample page titles from the batch to help classification.

### Cache

Load `domain-cache.yaml` before classifying. Save newly classified domains immediately (even if the run is aborted later). A mature cache (~3,600 domains) makes this phase near-instant.

### After Triage

- `tool` domains: skip (except bookmarked URLs, which always pass)
- `article-source` domains: pass to Phase 4
- `mixed` domains: pass to Phase 3

## Phase 3: URL Triage

For `mixed` domain URLs, decide per-URL whether it's an article.

### Deterministic Rules (most cases)

| Pattern | Decision |
|---------|----------|
| Path contains `/blog/`, `/posts/`, `/article/`, `/engineering/` | article |
| Path has a dated slug: `/2026/03/some-topic` | article |
| Path is root, settings, notifications, issues, pulls, actions | skip |
| `github.com`: `/notifications`, `/settings`, `/pulls`, `/issues/` | skip |
| `github.com`: repo root with descriptive title | article (let Phase 6 judge) |
| `news.ycombinator.com`: front page, `/newest` | skip |
| `news.ycombinator.com`: `/item?id=` with descriptive title | article |

### LLM for Ambiguous Cases (Haiku)

Batch 50+ URLs per call. Only needed for URLs that don't match deterministic patterns.

## Phase 4: Scrape

**Use `curl` with parallel workers. NOT WebFetch.**

WebFetch through LLM agents is unreliable at scale (agents timeout, die mid-scrape, waste tokens). curl is free, fast, and doesn't consume LLM context.

### Implementation

```python
import subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor

def scrape_url(url):
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    outfile = f"/tmp/distill-workdir/scraped/{url_hash}.txt"
    subprocess.run(
        ["curl", "-sL", "-m", "10", "-A", "Mozilla/5.0", "-o", outfile, "-w", "%{http_code}", url],
        capture_output=True, text=True, timeout=15
    )
    return outfile

# 20 parallel workers, 10-second timeout, no retries
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(scrape_url, url): url for url in candidates}
```

### Performance

| URLs | Time | Tokens |
|------|------|--------|
| 400 | ~30 seconds | 0 |
| 1,600 | ~2 minutes | 0 |
| 4,000 | ~5 minutes | 0 |

### Failure Handling

10-second timeout. No retries. Failed URLs get logged in the skip log. Expect 10-15% failure rate on old bookmarks (404s, dead domains).

## Phase 5: Extract Text

Strip HTML to plain text using Python's `HTMLParser`. Filter out `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<noscript>` tags.

- Truncate at 15K chars for classification (3K for preview, full text for note generation)
- Skip pages with < 200 chars of text (not real articles)
- Save as JSON batches of 20 articles for classification agents

This phase is pure Python, zero tokens.

## Phase 6: Classify

The core LLM step. Sonnet reads pre-scraped text and judges insight vs noise.

See `references/classification.md` for the detailed guide.

### Agent Structure

- Spawn multiple Sonnet agents, each processing 5-10 batches (100-200 articles)
- Each batch has 20 articles with `url`, `title`, `text_preview` (3K chars), `full_text`
- Agents write results to separate JSON files: `{url, title, topic_folder, filename, note_content}`
- **Critical: agents must write after every batch, not accumulate.**

### Output Per Article

| Field | Values |
|-------|--------|
| classification | `insight` or `noise` |
| confidence | `high`, `medium`, `low` |
| insight_summary | One-line core takeaway (insight only) |
| concepts | 2-3 topic tags (insight only) |
| noise_reason | One-line reason (noise only, for skip log) |

### Insight Rate

Target 10-20% of articles that reach this phase. If higher, the bar is too low. The triage phases already filtered most noise, so surviving candidates have higher quality than raw history.

### Gotchas

- **simonwillison.net link posts** are mostly noise (short quotes linking to other articles). Only keep if the commentary itself adds insight.
- **News sites (iThome, TechCrunch, etc.)** are almost always noise. Rehashes without original analysis.
- **Link aggregator blogs (gslin.org, Ruanyifeng weekly)** are noise. Short summaries with links.
- **Max 10 batches per agent.** Agents processing 25+ batches die before writing results.

## Phase 7: Export

### Insight Notes

Merge results from all classification agents. For each insight:

1. Check existing vault for duplicate URL (grep frontmatter). Skip if exists.
2. Write to `{topic_folder}/{filename}.md` using the template from SKILL.md.

### Skip Log

Append article candidates classified as noise to `_noise.md`:

```markdown
## YYYY-MM-DD

- [Title](url) — noise: {reason}
- [Title](url) — fetch failed: 404
```

Only log post-triage candidates. Don't log tool-domain URLs.

### Directory Structure

```
vault/
  ai/
    agents/
    engineering/
    llm/
      internals/
    safety/
  software/
    architecture/
    distributed-systems/
  python/
  security/
  databases/
  _noise.md
  .distill-state.yaml
  domain-cache.yaml
```

### Gotchas

- **Different agents create inconsistent folder names.** One agent writes to `ai-engineering/`, another to `ai/engineering/`. This is expected. Phase 8 handles consolidation.
- **Filename collisions**: Append a short hash suffix if filename already exists with a different URL.

## Phase 8: Review + Restructure

### Review

Present the run summary:

```
Triage funnel:
  {total} URLs extracted
  {n} dropped by domain triage
  {n} dropped by URL triage
  {n} scraped
  {n} classified → {n_insights} insights, {n_noise} noise

New insights by topic: ...
```

Show review table sorted by confidence (low first). User can promote/demote.

### Folder Restructure (periodic, not every run)

After multiple runs, the vault accumulates inconsistent folder names. When the user asks to restructure:

1. Audit all folders: count notes, identify singletons and overlaps
2. Propose a nested hierarchy (e.g., `ai-engineering/` + `ai-agents/` + `agentic-coding/` → `ai/engineering/`, `ai/agents/`)
3. Merge singletons into parent topics (folders with 1 note join the nearest related folder)
4. Target: no singletons, no folder with 50+ notes, 2 levels max depth
5. Present proposal, user approves, then move files

This is a separate operation, not part of the extraction pipeline.

### Gotchas

- **State update is the last step.** Only after user approves.
- **Don't overwhelm with the review table.** 50+ items: show only low/medium confidence.
- **Promoted items need full treatment.** Generate complete insight note, not just title + link.

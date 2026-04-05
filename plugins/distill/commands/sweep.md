---
description: Run the full insight extraction pipeline on any URL data source (browser history, bookmark export, CSV/URL dump)
argument-hint: [optional: vault-path] [optional: since-date]
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - Task
---

## Context

Read these before starting:
- @skills/distill/SKILL.md
- @skills/distill/references/pipeline.md
- @skills/distill/references/classification.md

## Task Workflow

**Vault path:** `$1` (if empty, check state file or ask user)
**Since override:** `$2` (if provided, ignore state file watermarks and process from this date)

### Phase 1: Identify Source + Extract

1. Read `.distill-state.yaml` from the vault (path from `$1` or current dir). If it exists, use saved source config and skip to step 3.
2. **First run (no state file):** Use `AskUserQuestion` to gather:
   - **Source:** What data source to process. Auto-detect installed browsers by checking profile paths from `references/browser-schemas.md`. Present all detected options plus file-based options (bookmark HTML, CSV export, URL list, Pocket/Raindrop/Instapaper export).
   - **Vault path:** Where to write the Obsidian notes (if not provided as `$1`).
3. For browser sources: copy DB files to `/tmp/distill-workdir/`, query bookmarks + history using the appropriate schema. Mind the timestamp format differences per browser.
4. For file sources: read the provided file (HTML bookmarks, CSV export, URL list, JSON export).
5. Output: `/tmp/distill-workdir/candidates.json` as normalized `[{url, title, source, date}]`.
6. Deduplicate by normalized URL against existing vault notes.

### Phase 2: Domain Triage

6. Extract unique domains. Load `domain-cache.yaml`.
7. Apply deterministic tool rules (localhost, google apps, social, streaming, work domains).
8. For uncached non-deterministic domains, spawn a **haiku** agent to classify. Batch all unknowns in one call.
9. Save updated `domain-cache.yaml` immediately.
10. Drop tool-domain URLs (except bookmarks which always pass).

### Phase 3: URL Triage

11. For mixed-domain URLs, apply deterministic path rules first.
12. For ambiguous mixed URLs, spawn a **haiku** agent to classify. Batch 50+ per call.
13. Drop non-article URLs.

### Phase 4: Scrape

14. Use the scrape script: `python3 scripts/scrape.py` with the candidate URLs.
    - 20 parallel curl workers, 10-second timeout, no retries
    - Output: one file per URL in `/tmp/distill-workdir/scraped/`
    - Zero LLM tokens

### Phase 5: Extract Text

15. Use the text extraction script: `python3 scripts/extract_text.py`
    - Strips HTML, filters <200 char pages
    - Outputs JSON batches of 20 articles in `/tmp/distill-workdir/classify-batch-{N}.json`

### Phase 6: Classify

16. Spawn **sonnet** agents to classify batches. Max 10 batches per agent.
    - Each agent reads batch JSONs, classifies per `classification.md`
    - Writes results to `/tmp/distill-workdir/results-{name}.json`
    - **Must write after every batch** (incremental saves)
17. Wait for all agents to complete. Collect results.
18. Sanity check: insight rate should be 10-20%.

### Phase 7: Export

19. Merge all result JSONs. Deduplicate by URL against existing vault notes.
20. Write insight notes to vault `{topic}/` folders. Never overwrite existing files.
21. Append noise URLs to `_noise.md` with reasons.

### Phase 8: Review + Restructure

22. Present triage funnel and review table (low confidence first).
23. Process user overrides (promote/demote).
24. Update `.distill-state.yaml` watermarks.
25. If user requests: run folder restructure (audit, propose hierarchy, move files).

## Orchestration Strategy

- **Phase 1:** Single Bash command for DB copy + sqlite3 queries
- **Phase 2:** Deterministic rules in Bash/Python, one haiku agent for unknowns
- **Phase 3:** Deterministic rules first, one haiku agent for ambiguous
- **Phase 4:** Python script with parallel curl. No LLM.
- **Phase 5:** Python script. No LLM.
- **Phase 6:** 2-5 parallel sonnet agents, each handling 5-10 batches. More agents = faster but higher rate-limit risk.
- **Phase 7:** Single pass to merge and write. No LLM.
- **Phase 8:** Interactive with user.
- **State safety:** Watermarks update only after user approves. Domain cache saves immediately.

## Expected Outcome

- New insight notes in `{topic}/` with frontmatter, takeaways, and scraped content
- Skip log updated in `_noise.md`
- State file updated with new watermarks
- Domain cache updated with any new domains

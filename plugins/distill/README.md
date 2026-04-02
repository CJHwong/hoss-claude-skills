# distill

Distill insights from Zen browser bookmarks and history into an Obsidian vault.

Periodically sweeps your places.sqlite for new bookmarks/history, scrapes articles with parallel curl workers, classifies them as insight vs noise using LLM reasoning, and exports tagged notes. Scraping is free (no LLM tokens). Classification uses model routing (haiku for triage, sonnet for content).

## Commands

- `/distill:sweep` - Run the full extraction pipeline
- `/distill:check <url>` - Classify a single URL and optionally add to vault
- `/distill:review` - Review and correct past classifications

## Examples

**Run a periodic sweep:**
> "Sweep my recent bookmarks for anything worth keeping."

**Check a single article:**
> "Check this: https://example.com/some-article"

**Review past classifications:**
> "Show me what was classified last time, I want to fix some."

## Install

```
/plugin marketplace add CJHwong/claude-skills
/plugin install distill@claude-skills
```

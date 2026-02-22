# agents-md-skill

Write AGENTS.md / CLAUDE.md files that actually help coding agents.

Most auto-generated context files make agents worse — a study across 438 tasks and four agents (arXiv:2602.11988v1, ETH Zurich, Feb 2026) found they reduce success rates by 2-3% and increase cost by 20%. This skill applies those findings: it keeps only what agents can't discover through their own tools and cuts everything else.

## What it does

- Audits existing AGENTS.md / CLAUDE.md files against research-backed criteria
- Creates new context files from scratch by exploring the codebase
- Handles monorepos with nested context files — promotes buried content, removes duplication
- Works on any repo, any language

## Examples

**Audit an existing file:**
> "Review my project's CLAUDE.md and tell me what's actually useful."

**Create from scratch:**
> "Generate an AGENTS.md for this project."

**Clean up a monorepo:**
> "This repo has CLAUDE.md files scattered across subdirectories, clean them up."

## Install

```
/plugin marketplace add CJHwong/claude-skills
/plugin install agents-md-skill@claude-skills
```

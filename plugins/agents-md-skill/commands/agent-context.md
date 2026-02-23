---
description: Capture non-discoverable repo context into an AGENTS.md or CLAUDE.md, backed by research on what helps vs. hurts agent performance
argument-hint: [optional: audit|create|prune] [optional: target-file]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---

## Research Foundation

A February 2026 study (arXiv:2602.11988v1, ETH Zurich) across 438 tasks and 4 coding agents found:
- LLM-generated context files **reduce** success rates by 2-3% and increase cost by 20-23%
- Developer-written files help marginally (+4%) but still increase cost
- Codebase overviews provide zero navigational benefit — agents explore repos effectively alone
- Context files only clearly help when the repo has **no other documentation** (+2.7%)
- Every line is an instruction the agent will spend time following. Only include lines worth that cost.

## Task Workflow

**Mode:** `$1` (if empty, auto-detect: context file exists → audit/prune, otherwise → create)
**Target:** `$2` (if empty, default to `CLAUDE.md`)

### Step 1: Audit the Repository

Read these in parallel to understand what documentation already exists:

- `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`
- Build/config files for the detected language:
  - Python: `pyproject.toml`, `setup.cfg`, `tox.ini`, `Makefile`
  - JS/TS: `package.json`, `tsconfig.json`, `turbo.json`
  - Rust: `Cargo.toml`, `build.rs`
  - Go: `go.mod`, `Makefile`
  - Java/Kotlin: `build.gradle`, `pom.xml`
  - General: `Makefile`, `Justfile`, `Taskfile.yml`, `docker-compose.yml`
- Linter/formatter configs (`.eslintrc`, `.pre-commit-config.yaml`, `rustfmt.toml`, etc.)
- CI configs (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`)
- Monorepo orchestration configs (`turbo.json`, `nx.json`, `pnpm-workspace.yaml`, `rush.json`)
- Existing `AGENTS.md` / `CLAUDE.md` files (root and subdirectories)

### Step 2: Assess Documentation Level

Classify the repo — this determines how much content is justified:

- **Well-documented** (good README, CONTRIBUTING, docs/) → Minimal context file. Possibly no file at all.
- **Partially documented** (basic README, no CONTRIBUTING) → Fill gaps, focus on non-obvious requirements.
- **Undocumented** (no README or just a stub) → More content justified. Include brief overview + architecture notes. Recommend user write proper docs. Ask about tooling choices — don't guess.

### Step 3: Decide — Should This Repo Even Have a Context File?

**Create one if** the repo has:
- Non-standard build/test tooling (not the language default)
- Required env setup not documented elsewhere
- Hard constraints agents can't infer from code or linter configs
- Repository-specific CLI tools or scripts
- Little or no existing documentation

**Skip it if** the repo:
- Uses standard tooling with standard configs (`cargo test`, `npm test`, `pytest` with no special flags)
- Already has a good README and/or CONTRIBUTING.md covering setup
- Has CI configs that clearly document the build/test pipeline
- Would only contain generic advice

**If the answer is "skip it,"** tell the user directly with reasoning. Don't create a file just to have one.

### Step 4: Identify Non-Discoverable Requirements

Ask: "What does an agent need to know that ISN'T in any existing file?"

- Non-standard tooling or custom scripts
- Required environment variables or system dependencies
- Custom test flags or test infrastructure setup
- Build order dependencies or prerequisites
- Hard constraints not enforced by automated tooling (or enforced by linters that don't tell the agent what to use instead)
- Known gotchas that have actually caused real problems

### Step 5: Write or Prune

**If creating:** Use this template. **Delete any section that doesn't apply** — an empty section is worse than none.

```markdown
# [Project Name] — Agent Instructions

## Required Tooling
<!-- Only if non-standard for the language. Delete if defaults work. -->

## Build & Test
<!-- Only non-obvious commands. Delete if standard tooling works. -->

## Environment Setup
<!-- Required env vars, system deps, non-obvious setup steps. Delete if none. -->

## Hard Constraints
<!-- Non-negotiable rules not enforced by linters/CI. Keep extremely brief. -->

## Common Pitfalls
<!-- Only issues that have actually occurred. Delete if speculative. -->
```

For undocumented repos only, you may add before the template sections:
- **Project Overview** — 2-3 sentences max. Justified only because there's no README.
- **Architecture Notes** — Brief component relationships and data flow. 5-8 lines max. NOT a directory listing.

**If auditing/pruning:** For each line, apply the filter:
- Discoverable from existing docs/configs? → **Remove**
- Generic advice for this language? → **Remove**
- Codebase overview or directory listing? → **Remove**
- Would an agent fail without it? → **Keep**
- Actionable with a concrete command or rule? → **Keep**
- Speculative or aspirational? → **Remove**
- References a file (e.g., `.env.example`)? → **Verify it exists**

### Step 6: Handle Monorepos

If monorepo detected:

1. Root file covers workspace-level commands, build orchestration, shared constraints
2. Create nested files **only** for sub-projects with genuinely different tooling (different language, non-standard build, unique constraints)
3. Audit each nested file against the same quality bar as root
4. Promote buried useful content upward to parent files
5. Explain nesting decisions to user with reasoning — even when the answer is "no nested files needed"

### Step 7: Validate and Present

Show the user:
- What was written/kept and **why** each line earns its place
- What was omitted/removed and **why**
- For pruning: section/word counts before and after
- For monorepos: nesting decisions with rationale
- File naming recommendation (CLAUDE.md vs AGENTS.md) based on target agents

**Wait for user approval before saving.** If the user wants changes, iterate.

### Step 8: File Naming and Symlinks

| Agent | File | Notes |
|-------|------|-------|
| Claude Code | `CLAUDE.md` | Repo root |
| OpenAI Codex / Qwen Code | `AGENTS.md` | Broadest compatibility |

For multi-agent support: write one canonical file, symlink the other. Don't maintain two separate files — they'll drift apart.

## What to NEVER Include

These are research-confirmed performance killers. Remove on sight:

1. **Codebase overviews / directory listings** — agents explore repos effectively alone
2. **Restated README or docs content** — if it's written somewhere, the agent will find it
3. **Generic coding advice** — "write clean code", "add docstrings", "follow PEP 8"
4. **Technology stack listings** — "Python 3.12, Django 5.1, PostgreSQL" — agent reads config files
5. **File-by-file descriptions** — "src/models/user.py contains the User model"
6. **Standard workflow descriptions** — "clone the repo, install deps, run tests"
7. **Git workflow instructions** — "use feature branches, require PR reviews"
8. **Personality/tone instructions** — belong in user's personal config, not repo-level

## Quality Bar for Sections

Each section must pass: **"Would an agent fail, produce wrong results, or burn significant effort rediscovering this?"**

Technically discoverable but expensive info is worth including — a multi-file update checklist touching 8 files, or 15+ banned modules with project-specific replacements. If rediscovery costs multiple failed attempts, include it.

**Tooling instructions must be actionable:** "Use uv" is too vague. "`uv sync` to install, `uv run pytest` to test" is actionable.

**Constraints already enforced by linters:** Skip unless the linter error message doesn't tell the agent what to use instead. A linter banning `requests` won't say "use httpx instead" — that's worth including. Import ordering enforcement is self-correcting — skip it.

## Orchestration Strategy

- **Parallel reads:** In Step 1, batch all doc/config/CI file reads into a single turn
- **Explore subagent:** Use `Task(Explore)` for monorepo structure discovery if the repo has 5+ top-level directories or unclear package layout
- **Sequential gates:** Steps 2-3 (assess + decide) must complete before Step 5 (write/prune)
- **User checkpoints:**
  - After Step 3 if recommendation is "skip" — confirm with user before stopping
  - After Step 7 — present full results and wait for approval before saving
- **Monorepo processing:** Root file first, then nested files sequentially. Check in with user after root is approved before proceeding to nested files.

## Expected Outcome

- A minimal, research-backed context file containing only non-discoverable, actionable instructions
- Clear reasoning for every inclusion and exclusion
- For existing files: before/after comparison with word/section counts
- For monorepos: nesting strategy with explicit rationale
- Saved to repo root (or subdirectories for monorepo nested files)

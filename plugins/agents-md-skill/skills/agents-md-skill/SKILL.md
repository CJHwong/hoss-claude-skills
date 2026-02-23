---
name: agents-md-skill
description: Create or improve AGENTS.md, CLAUDE.md, CODEX.md, or similar repository-level context files for coding agents. Also capture conversation workflows into reusable slash commands. Use this skill whenever the user wants to create, write, edit, update, or optimize an AGENTS.md or CLAUDE.md file, or asks about how to guide AI coding agents in their repository. Also trigger when users mention "context file for agents", "agent instructions", "coding agent setup", repository onboarding for AI, or want to improve how Claude Code, Codex, Qwen Code, or other coding agents work with their codebase. Trigger for "capture workflow", "save this as a command", "create a slash command from this conversation", or similar requests to extract reusable patterns from conversations. This skill encodes empirical research findings on what actually helps vs. hurts agent performance — most auto-generated context files actively decrease success rates and increase costs, so getting this right matters. The same principles apply to slash commands: every line costs reasoning tokens. Trigger even for non-Python repos — the principles are language-agnostic.
---

# AGENTS.md / CLAUDE.md Creator

## The Core Insight

A February 2026 study from ETH Zurich rigorously tested whether context files help coding agents solve real-world tasks. The key finding: **most context files make agents worse, not better.**

- **LLM-generated context files reduce success rates by 2-3%** while increasing cost by 20-23%
- **Developer-written files help only marginally (+4%)** and still increase cost
- **Codebase overviews don't help agents navigate** — agents find relevant files just as fast without them
- **Agents reliably follow instructions**, which is the problem — unnecessary instructions waste reasoning tokens (up to 22% more) and steps on compliance instead of problem-solving
- **Context files only clearly help when the repo has no other documentation** — in that setting, they improve performance by ~2.7%

The research was conducted on Python repositories, but the underlying dynamics (instruction-following overhead, redundancy with existing docs, ineffective overviews) are language-agnostic. The principles below apply to any codebase.

**The golden rule: every line in a context file is an instruction the agent will spend time following. Only include lines worth that cost.**

For detailed numbers, see `references/research-data.md`.

---

## Decision: Should This Repo Even Have a Context File?

Before writing anything, assess whether a context file is justified:

**Create one if** the repo has any of these:
- Non-standard build/test tooling (not the language's default)
- Required environment setup that isn't documented elsewhere
- Hard constraints an agent can't infer from code or linter configs
- Repository-specific CLI tools or scripts
- Security/compliance requirements for code changes
- Little or no existing documentation (README, CONTRIBUTING, docs/)

**Skip it if** the repo:
- Uses standard tooling with standard configs (e.g., `cargo test`, `npm test`, `pytest` with no special flags)
- Already has a good README and/or CONTRIBUTING.md covering setup
- Has CI configs that clearly document the build/test pipeline
- Would only contain generic advice ("write clean code", "add tests")

When a repo already has thorough documentation, adding a context file is redundant and the research shows it actively hurts. Tell the user this directly.

---

## File Naming

| Agent | Filename | Notes |
|-------|----------|-------|
| Claude Code | `CLAUDE.md` | Placed at repo root |
| OpenAI Codex | `AGENTS.md` | Also used by Qwen Code |
| Multi-agent / general | `AGENTS.md` | Broadest compatibility |

Place the file at the repository root. See the Monorepo section below for nested files.

If the repo needs to support multiple agents (Claude Code reads `CLAUDE.md`, Codex/Qwen read `AGENTS.md`), write one canonical file and symlink the other: `ln -s AGENTS.md CLAUDE.md` (or vice versa). Don't maintain two separate files with overlapping content — they'll drift apart and the repo now has two sources of truth, both slightly wrong.

When revising a repo that already uses symlinks, identify which file is canonical (the real file) and which is the symlink. Edit only the canonical file — the symlink follows automatically.

---

## Writing the Context File

### Template

Start from this. **Delete any section that doesn't apply** — an empty or inapplicable section is worse than no section.

```markdown
# [Project Name] — Agent Instructions

## Required Tooling
<!-- Only if non-standard for the language. Delete if defaults work. -->

## Build & Test
<!-- Only commands that aren't obvious. Delete if standard tooling works. -->

## Environment Setup
<!-- Required env vars, system deps, non-obvious setup steps. Delete if none. -->

## Hard Constraints
<!-- Non-negotiable rules. Keep extremely brief. -->

## Common Pitfalls
<!-- Only issues that have actually occurred. Delete if speculative. -->
```

### What Makes a Good Section

Each section should pass this test: **"Would an agent fail, produce wrong results, or burn significant effort rediscovering this?"**

The test isn't strictly binary. Some information is technically discoverable but expensive to rediscover — a multi-file update checklist touching 8 files, or a set of 15+ banned modules each with project-specific replacements. If an agent would need multiple failed attempts or extensive grep sessions to piece something together, that's worth including even though it's not "impossible" to find.

#### Required Tooling — only if non-standard

Agents know the default toolchain for every popular language. Only document deviations.

**Good (non-obvious):**
```markdown
## Required Tooling
- Use `pnpm` (not npm/yarn) — the lockfile is pnpm-lock.yaml
- Use `uv` for Python dependency management: `uv sync` to install
- Protobuf compilation: `buf generate` (not protoc directly)
```

**Bad (agents already know this):**
```markdown
## Required Tooling
- Use cargo for building Rust code
- Use pip for Python dependencies  
- Use git for version control
```

#### Build & Test — only non-obvious commands

If `pytest`, `cargo test`, `npm test`, `go test ./...` or the language equivalent works with no flags, don't document it.

**Good (non-obvious):**
```markdown
## Build & Test
# Must build the WASM module before running JS tests
cd packages/wasm && wasm-pack build --target web
cd ../.. && pnpm test

# Integration tests require a running Postgres instance
docker compose up -d postgres && sleep 3
DATABASE_URL=postgres://localhost:5432/test pnpm test:integration
```

**Bad (standard commands):**
```markdown
## Build & Test
Run `npm install` to install dependencies.
Run `npm test` to run the test suite.
Tests are located in the `__tests__/` directory.
```

#### Environment Setup — required but non-discoverable

Environment variables, system dependencies, or setup steps that aren't documented in README or discoverable from config files.

**Good:**
```markdown
## Environment Setup
Required env vars (see .env.example for all values):
- DATABASE_URL, REDIS_URL — must be set even for unit tests
- SENDGRID_API_KEY — required for notification tests (use test key from .env.example)

System deps: libmagic (for file type detection) — `brew install libmagic` or `apt install libmagic-dev`
```

**Bad (discoverable from project files):**
```markdown
## Environment Setup
This project requires Node.js 20+. Install dependencies with npm install.
```

#### Hard Constraints — brief, non-negotiable rules

Only include rules that aren't enforced by linters, CI, or type checkers. If `ruff` or `eslint` already catches it, don't repeat it here — **unless the error message wouldn't tell the agent what to use instead**. For example, a linter that bans `requests` will say "requests is not allowed" but won't say "use httpx instead" — that's worth including. A linter that enforces import ordering is self-correcting and doesn't need a context file entry.

Volume matters here too. A single linter ban is self-correcting — one failed lint, one fix, move on. But if a project bans 10+ modules each with project-specific replacements, documenting the full list upfront saves the agent from a lint-fail-fix cycle on every new file it writes. Use judgment: a handful of bans can be discovered by failure, a minefield is worth a map.

**Good:**
```markdown
## Hard Constraints
- Never modify files under `src/generated/` — auto-generated from OpenAPI spec
- All database queries must go through the repository pattern in `src/db/repos/`
- Do not add new dependencies without adding to the SECURITY.md allowlist
- Use `httpx` for HTTP requests (not `requests`) — the linter will flag `requests` but won't tell you the alternative
```

**Bad (vague, generic, or already enforced by tooling):**
```markdown
## Hard Constraints
- Follow the existing code style
- Write tests for new features
- Keep functions small and focused
- Use meaningful variable names
```

#### Common Pitfalls — only real, observed issues

Only include problems that have actually tripped up contributors or agents. Speculative warnings waste attention.

**Good:**
```markdown
## Common Pitfalls
- `make build` must run before `make test` on first clone (compiles native extensions)
- The config loader silently falls back to defaults — always check key existence
- Hot reload breaks if you modify files in `core/` — restart the dev server
```

### What to NEVER Include

The research is unambiguous on these — they hurt performance:

1. **Codebase overviews / directory listings** — Agents explore repos effectively on their own. 95-100% of LLM-generated files include these; they provide zero navigational benefit while adding cost.

2. **Restated README or docs content** — If it's already written somewhere, the agent will find it. Duplicating it is the #1 reason LLM-generated files hurt performance.

3. **Generic coding advice** — "Write clean code", "Add docstrings", "Follow PEP 8 / Airbnb style guide". Agents know language conventions.

4. **Technology stack listings** — "Python 3.12, Django 5.1, PostgreSQL". The agent can read config files.

5. **File-by-file descriptions** — "src/models/user.py contains the User model". The agent can read the filesystem.

6. **Standard workflow descriptions** — "Clone the repo, install deps, run tests". This is the same for every project.

7. **Git workflow instructions** — "Use feature branches, require PR reviews". Not relevant to task completion.

8. **Personality or tone instructions** — "Be concise", "Respond like a senior engineer", "Use emojis". These are user preferences, not repository requirements. They belong in the user's personal config (`~/.claude/CLAUDE.md` for Claude Code) where they apply across all repos, not in a repo-level file where they'd impose one person's style on every contributor.

---

## Repos With No Documentation

This is the one scenario where the research shows context files clearly help (+2.7% when all other docs are removed). When a repo lacks a README, CONTRIBUTING.md, or docs directory, the context file serves as a substitute — and more content is justified.

For undocumented repos, you may expand the template to include:

```markdown
## Project Overview
<!-- 2-3 sentences max. What does this project do? What problem does it solve? -->
<!-- This is justified ONLY because there's no README. -->

## Architecture Notes
<!-- Brief description of how the major components connect. -->
<!-- Keep to 5-8 lines. NOT a directory listing — describe relationships and data flow. -->
```

Even here, keep it brief. The goal is to compensate for missing docs, not to write a comprehensive wiki. A 2-3 sentence overview plus architecture notes is far more useful than an exhaustive directory listing.

**Always recommend that the user also write a proper README** — a context file is a poor substitute for real documentation.

**For undocumented repos, ask before assuming.** Don't guess at tooling choices — ask the user what package manager, test framework, and build tools they use. An undocumented repo is exactly the scenario where assumptions are most likely to be wrong.

---

## Monorepos

Monorepos need special care. The wrong approach is creating a context file for every package/service. The right approach is based on whether sub-projects have **genuinely different tooling requirements**.

### Decision Framework

```
Root AGENTS.md (always, if the monorepo warrants a context file at all)
├── Covers: workspace-level commands, build orchestration, shared constraints
│
├── packages/frontend/    → No nested file (standard tooling, covered by root)
├── packages/api/         → No nested file (same language/tooling as root)
├── packages/ml-pipeline/ → AGENTS.md here (different language, different tooling)
└── packages/legacy/      → AGENTS.md here (unusual build process, known pitfalls)
```

### Root Context File for Monorepos

The root file should cover:
- Workspace-level package manager commands (e.g., `pnpm install`, `lerna bootstrap`)
- Build orchestration tool usage if non-obvious (e.g., Turborepo, Nx, Bazel)
- Cross-package constraints (e.g., shared dependency versions, build order requirements)
- Runtime version pinning if packages require different versions (e.g., different Node versions via `.nvmrc` or Volta, different Python versions via `.python-version`)

```markdown
# MyMonorepo — Agent Instructions

## Required Tooling
- Use `pnpm` with workspaces — run `pnpm install` from root
- Build orchestration via Turborepo: `pnpm turbo run build`

## Build Order
packages/core must build before packages/api or packages/web.
Turborepo handles this automatically, but if running manually: build core first.

## Hard Constraints
- Shared types live in packages/types/ — import from there, don't duplicate
```

### Auditing Existing Nested Files

Many repos use nested context files as **lazy-loaded scoped context** — the agent only reads a subdirectory's CLAUDE.md when it enters that folder. This is a sound design. The problem isn't that nested files exist, it's that they're usually bloated with the same LLM-generated filler as root files: directory listings, restated README content, generic advice.

When a repo already has nested context files, apply the same quality bar to each one: audit it against its local README and config files, prune everything discoverable, and keep only what an agent entering that folder genuinely couldn't figure out on its own. A scoped context file should contain constraints and workflows specific to that subtree — not a restatement of "this module handles X" that the agent can read from the code.

Treat this as a **full-repo pass**: root file first, then each nested file in turn, each held to the same quality standard.

During the pass, you may find useful content buried in a deeply nested file that would serve better in a parent file. Promote it — consolidate upward so agents encounter critical information earlier rather than only if they happen to enter the right subdirectory. After promotion, the nested file can either shrink to cover only its local scope or be marked as removable if nothing local-only remains.

### Nested Context Files

Create a nested context file **only when** a sub-project:
- Uses a different language or runtime than the majority of the repo
- Has non-standard build/test commands specific to that package
- Has unique constraints or pitfalls not covered by the root file

**Always communicate your nesting decision to the user with reasoning.** Even when the answer is "no nested files needed," say so explicitly: "The TypeScript packages all use the same tooling, so they're covered by the root file. Only ml-pipeline needs its own because it uses Python." This helps the user understand the framework and maintain it as the repo evolves.

The nested file should cover only what's different — don't repeat root-level info.

```markdown
# packages/ml-pipeline — Agent Instructions
<!-- This package uses Python, unlike the rest of the TypeScript monorepo -->

## Required Tooling
- Python environment: `cd packages/ml-pipeline && uv sync`
- Tests: `uv run pytest` (not the root-level pnpm test)

## Environment Setup  
- Requires CUDA 12.1+ for GPU tests — CPU-only tests: `uv run pytest -m "not gpu"`
```

---

## Pruning an Existing Context File

When the user has an auto-generated or bloated context file, the primary job is aggressive removal.

### Process

1. **Read the existing file** and the repo's other documentation (README, config files, CI)
2. **For each section**, apply the test: "Would removing this cause an agent to fail?"
3. **Remove** anything that's:
   - Discoverable from existing docs or config files
   - Generic advice true of any project in this language
   - A codebase overview or directory listing
   - Standard workflow descriptions
4. **Show the user** what was removed and why, alongside the trimmed result
5. **Validate** the remaining content is actionable (concrete commands, specific rules)

### Communicating Removals

When pruning, explain the reasoning. Something like:

> I removed 11 of 14 sections. Research shows redundant context files decrease agent performance by 2-3% while increasing cost by 20%+. The remaining sections contain information agents can't discover on their own: [list what's left and why].

This helps users understand the "less is more" principle rather than feeling like their work was arbitrarily deleted.

---

## Creating a Context File: Full Workflow

### Step 1: Audit the Repository

Before writing anything, examine what already exists:

```
1. Read README.md, CONTRIBUTING.md, DEVELOPMENT.md (if present)
2. Check build/config files:
   - Python: pyproject.toml, setup.cfg, tox.ini, Makefile
   - JavaScript/TypeScript: package.json, tsconfig.json, turbo.json
   - Rust: Cargo.toml, build.rs
   - Go: go.mod, Makefile
   - Java/Kotlin: build.gradle, pom.xml
   - General: Makefile, Justfile, Taskfile.yml, docker-compose.yml
3. Check linter/formatter configs (.pre-commit-config.yaml, .eslintrc, rustfmt.toml, etc.)
4. Check CI configs (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
5. For monorepos, also check orchestration configs:
   - turbo.json, nx.json, lerna.json, pnpm-workspace.yaml, rush.json
   - Per-package overrides (.nvmrc, .node-version, .python-version, .tool-versions)
6. Check for existing AGENTS.md / CLAUDE.md
7. Assess documentation level: is there a docs/ folder? Inline code docs?
```

### Step 2: Assess Documentation Level

This determines how much content is justified:

- **Well-documented** (good README, CONTRIBUTING, docs/) → Minimal context file, only non-discoverable requirements. Possibly no file at all.
- **Partially documented** (basic README, no CONTRIBUTING) → Slightly more content to fill gaps, but still focus on non-obvious requirements.
- **Undocumented** (no README or just a stub) → More content is justified. Include a brief project overview and architecture notes. Recommend the user write proper docs.

For repos with nested context files, assess documentation level **per subtree**, not just at the root. A repo can have a thorough root README while specific subdirectories have no local docs at all. A nested context file for an undocumented subtree is justified in including more content than one for a well-documented subtree, even within the same repo.

### Step 3: Identify Non-Discoverable Requirements

Ask: "What does an agent need to know that ISN'T in any existing file?" Common answers:
- Non-standard tooling or custom scripts
- Required environment variables or system dependencies
- Custom test flags or test infrastructure setup
- Build order dependencies or prerequisites
- Hard constraints not enforced by automated tooling
- Known gotchas that have caused real problems

### Step 4: Write Minimal Content

Using the template, write **only** sections addressing real gaps from Step 3. Show the user what you wrote AND what you intentionally omitted.

### Step 5: Validate Each Line

For every line in the draft:
- Discoverable from existing docs/configs? → Remove
- Generic advice for this language? → Remove  
- Would an agent fail without it? → Keep
- Actionable with a concrete command or rule? → Keep
- Speculative or aspirational? → Remove
- References a file (e.g., .env.example, CONTRIBUTING.md)? → Verify it actually exists in the repo

---

## Reviewing an Existing Context File: Checklist

1. **Count sections and words.** Research average: 9.7 sections, 641 words. If significantly larger, it's likely hurting. Target fewer sections, higher signal.
2. **Cross-reference with README and config files.** Any overlap is redundancy to remove.
3. **Flag codebase overviews.** Directory listings, component descriptions → remove.
4. **Flag generic advice.** True of any project in this language → remove.
5. **Check that tooling instructions are actionable.** "Use uv" is too vague. "Run `uv sync` to install, `uv run pytest` to test" is actionable.
6. **Verify constraints aren't already enforced.** If a linter or CI check catches it, the context file doesn't need to mention it.

---

## Research Methodology Note

The findings referenced throughout this skill come from evaluation across 4 coding agents (Claude Code, Codex, Qwen Code) on 438 total tasks (300 SWE-Bench Lite + 138 AgentBench) in Python repositories. While the specific numbers are Python-focused, the mechanisms that make context files harmful (instruction-following overhead, redundancy with existing docs, ineffective overviews) are not language-specific. Apply the principles with confidence across languages, but note that for languages less represented in LLM training data, context files about unfamiliar toolchains might provide more value.

For the full dataset, see `references/research-data.md`.

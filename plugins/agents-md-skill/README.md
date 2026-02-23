# agents-md-skill

Write lean, effective agent instructions — context files and slash commands — backed by empirical research.

A February 2026 study across 438 tasks and four agents (arXiv:2602.11988v1, ETH Zurich) found that most auto-generated context files reduce success rates by 2-3% and increase cost by 20%+. The same principle applies to slash commands: every line is an instruction the agent will spend reasoning tokens following. This skill knows what to keep and what to cut.

## What it does

**Context files** (AGENTS.md, CLAUDE.md):
- Creates new context files by exploring the repo and keeping only non-discoverable info
- Audits and prunes existing files against research-backed criteria
- Handles monorepos with nested context files
- Works on any repo, any language

**Slash commands** (capture-workflow):
- Extracts workflow steps and orchestration patterns from conversations
- Generates reusable commands with the same quality bar
- Filters out meta-protocol and generic advice that waste tokens

## Commands

| Command | Description |
|---------|-------------|
| `/agent-context` | Create, audit, or prune an AGENTS.md / CLAUDE.md |
| `/capture-workflow` | Capture a conversation workflow as a reusable slash command |

## Examples

**Create a context file:**
> `/agent-context create`

**Audit an existing file:**
> `/agent-context audit`

**Capture a workflow from the current conversation:**
> `/capture-workflow deploy-service`

## Install

```
/plugin marketplace add CJHwong/claude-skills
/plugin install agents-md-skill@claude-skills
```

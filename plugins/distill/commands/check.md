---
description: Classify a single URL as insight or noise, and add it to the vault if applicable
argument-hint: <url>
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - Glob
  - Grep
  - AskUserQuestion
---

## Context

Read the skill definition for output formats and classification criteria:
- @skills/distill/SKILL.md
- @skills/distill/references/classification.md

## Task Workflow

**URL:** `$1`

### Step 0: Find Vault

0. Look for `.distill-state.yaml` in the current directory, then `~/Obsidian/Insights/`. If not found, ask the user for the vault path.

### Step 1: Fetch

1. WebFetch the URL. If it fails, report the error and ask if the user wants to classify based on title alone. (WebFetch is fine for single URLs - the curl approach is only needed for batch scraping.)

### Step 2: Classify

2. Read the content and apply the insight heuristic from `classification.md`.
3. Present the verdict to the user:

**If insight:**
```
Verdict: insight ({confidence})
Summary: {one-line insight summary}
Concepts: {tags}
Topic: {proposed folder}
```

**If noise:**
```
Verdict: noise
Reason: {why it doesn't meet the insight bar}
```

**If unclear:**
```
Verdict: borderline
For: {what makes it potentially insightful}
Against: {what makes it potentially noise}
```

4. Ask the user: "Add to vault?" (for insight/borderline) or "Add to noise log?" (for noise).

### Step 3: Write

5. If user says yes to insight:
   - Read `.distill-state.yaml` for vault path
   - Generate full insight note (frontmatter + Key Insight + Takeaways + Context + scraped content)
   - Write to `{vault}/{topic}/{filename}.md`

6. If user says yes to noise:
   - Append to `{vault}/_noise.md`: `- [Title](url) — noise: {reason}`

7. If user says ignore: do nothing.

## Expected Outcome

- Quick classification of a single URL with reasoning shown
- User decides whether to add
- Note or noise log entry written if approved

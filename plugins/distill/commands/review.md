---
description: Review and correct past insight classifications
argument-hint: [optional: vault-path] [optional: date-or-session]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - AskUserQuestion
---

## Context

Read the skill definition for output formats:
- @skills/distill/SKILL.md

## Task Workflow

**Vault path:** `$1` (if empty, read from `.distill-state.yaml` in current directory)
**Date filter:** `$2` (if provided, only show items from that date/month)

### Step 1: Load Insight Notes

1. Read `.distill-state.yaml` to get the vault path.
2. Glob for `**/*.md` in the vault, excluding state/config files.
3. Parse frontmatter from each note: title, url, confidence, insight_summary, concepts, date_processed.
4. Filter by `$2` if provided.

### Step 2: Present for Review

5. Present counts: total insights, broken down by confidence level.
6. Show table sorted by confidence (low first): title, confidence, concepts, insight_summary.

### Step 3: Collect Overrides

7. Ask user which items to change. Accept:
   - "demote #2, #5" — delete those insight notes
   - "retag #4 with X instead of Y" — update frontmatter concepts
   - "move #3 to different-topic/" — move file to different topic folder
   - "looks good" — no changes needed

### Step 4: Apply Changes

8. **Demoting:** Delete the insight note file. If the topic folder is now empty, remove it.
9. **Retagging:** Update the insight note's frontmatter `concepts` list.
10. **Moving:** Move the file to the new topic folder, create folder if needed.

### Step 5: Confirm

11. Show a summary of changes made (N demoted, N retagged, N moved).

## Orchestration Strategy

- **Parallel reads:** Glob and read all notes simultaneously in Step 1
- **User checkpoint:** Step 3 is the core interaction
- **Sequential:** File modifications in Step 4 happen after user confirms

## Expected Outcome

- Misclassified insights removed
- Tags and topic folders corrected
- Summary of all changes presented to user

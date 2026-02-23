---
description: Capture key steps from conversation and save them as a reusable slash command
argument-hint: [optional: command-name] [optional: description]
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
---

## Your Task

Analyze the current conversation to extract the key workflow steps, agentic orchestration patterns, and decisions. Transform these into a reusable slash command that captures BOTH what was done and how it was orchestrated.

**User-Provided Name (if any):** `$1`
**User-Provided Description (if any):** `$2`

## Quality Principle

Every line in a generated command is an instruction the agent will spend reasoning tokens following. Research on agent context files (arXiv:2602.11988v1) shows unnecessary instructions reduce success rates by 2-3% and increase cost by 20%+. The same dynamic applies to slash commands — bloated commands produce worse results than lean ones.

**The bar:** If removing a line from the command wouldn't cause the agent to fail or produce wrong results, that line shouldn't be there.

## CLAUDE.md Isolation Guard

**CRITICAL:** When analyzing the conversation, you MUST distinguish between:

- **Workflow steps** — Domain-specific actions that were performed to accomplish the task (reading files, running commands, editing code, making decisions). CAPTURE THESE.
- **Operating protocol / meta-instructions** — General behavioral rules from CLAUDE.md or system instructions (e.g., PRAR phases, "Verify Then Trust," Chesterton's Fence, commit conventions, tone guidelines, definition of done checklists). IGNORE THESE.

Operating protocol tells Claude *how to behave in general*. Workflow steps tell Claude *what to do for this specific task*. Only the latter belongs in a captured command.

**Test:** If a step would appear identically in ANY captured command regardless of domain (e.g., "Phase 1: Perceive requirements"), it is meta-protocol, not workflow. Exclude it.

## Step-by-Step Instructions

### 1. Analyze Conversation History — Track A: Task Workflow (What Was Done)

Review the conversation and identify domain-specific actions:

**Key Actions Performed:**
- What files were read, created, or modified?
- What bash commands were executed and why?
- What tools were used and in what sequence?

**Decision Points:**
- What questions were asked of the user?
- What choices were made and why?
- What validation or checks were performed?

**Workflow Pattern:**
- What was the logical sequence of steps?
- What dependencies exist between steps?
- What could be parameterized for reuse?

**Primary Domain/Topic:**
- What is the main subject? (git, testing, deployment, refactoring, etc.)
- What action verb best describes it? (create, review, fix, setup, etc.)

### 2. Analyze Conversation History — Track B: Agentic Orchestration (How It Was Done)

Review the conversation for orchestration patterns Claude used:

**Parallel Operations:**
- Which tool calls were batched in single turns? (e.g., reading multiple files simultaneously, running parallel Glob/Grep searches)
- Where did parallelism provide a real speedup?

**Subagent Delegation:**
- Which Task tool invocations were made? Note the `subagent_type` used (Explore, test-runner-reporter, Plan, brutal-code-reviewer, etc.)
- What was each subagent tasked with and why was delegation appropriate?

**Background Tasks:**
- Were any commands run with `run_in_background`?
- How were background results collected and used?

**Task Decomposition:**
- Was TaskCreate used to break work into tracked units?
- What was the task dependency graph?

**Iterative Loops:**
- Were there failure → diagnose → fix → re-run cycles?
- How many iterations occurred and what triggered convergence?

**User Decision Points:**
- Where was AskUserQuestion used to get human input?
- What decisions were deferred to the user vs. made autonomously?

**Sequential Dependencies:**
- Which steps had to wait on prior results?
- Which steps could (and did) run in parallel?

### 3. Auto-Generate Name and Description (if not provided)

**If `$1` is empty or not provided:**

Generate a command name by:
1. Identifying the primary action verb (e.g., create, review, fix, setup, deploy)
2. Identifying the primary subject (e.g., pr, commit, test, component, service)
3. Combining as: `<verb>-<subject>` or `<subject>-<action>`

Examples:
- PR review workflow → `review-pr`
- Setting up a new service → `setup-service`
- Fixing lint errors → `fix-lint`
- Running eval and iterating → `run-eval-loop`

**If `$2` is empty or not provided:**

Generate a description by:
1. Summarizing what the workflow accomplishes in one sentence
2. Starting with an action verb
3. Being specific about inputs/outputs

### 4. Extract Reusable Elements

Identify elements that should become:
- **Arguments** (`$1`, `$2`, `$ARGUMENTS`): Values that change per invocation
- **File references** (`@path`): Files that are consistently needed
- **Dynamic context** (bang-backtick syntax): Commands that gather runtime context
- **Static instructions**: Steps that remain constant
- **Orchestration directives**: Parallelism hints, subagent selections, iteration strategies

### 5. Draft the Command

Create a slash command following this structure:

```markdown
---
description: <clear, concise description>
argument-hint: <document expected arguments>
allowed-tools: <list only tools the command needs>
---

## Context
<Dynamic context gathering — bang-backtick for shell commands, @ for file refs>

## Task Workflow
<Domain-specific steps — what to do, in order>
<Each step should be concrete and actionable>
<Parameterize variable elements with $1, $2, etc.>

## Orchestration Strategy
<How to execute the workflow efficiently>
<Parallel operations: which steps to batch>
<Subagent delegation: which Task types to use and when>
<Iteration strategy: when to loop and what signals convergence>
<User checkpoints: where to pause for human decisions>

## Expected Outcome
<What success looks like — concrete deliverables or state changes>
```

**NOTE on dynamic shell syntax:** When writing the generated command template, use the bang-backtick pattern to gather dynamic context (the exclamation mark prefix before a backtick-wrapped shell command). However, do NOT place raw instances of this pattern inside fenced code blocks within the template file itself — the command loader will attempt to execute them at parse time. Instead, describe the commands in prose or use inline code for the shell command portion only.

### 6. Validate the Draft

Before presenting to the user, run every line through this filter:

- **Would the agent fail without this line?** If no → cut it.
- **Is this generic advice true of any command?** ("Be thorough", "Handle errors") → cut it.
- **Is this discoverable from the tools or context already available?** → cut it.
- **Is this meta-protocol leaking in?** (PRAR phases, tone rules, definition of done) → cut it.
- **Is this a concrete, actionable instruction specific to this workflow?** → keep it.
- **Does this orchestration hint save meaningful time or prevent failure?** → keep it.

A good command is 30-80 lines of dense, actionable instructions. If your draft exceeds 120 lines, you're probably including filler.

### 7. Present Draft for Review (MANDATORY)

**CRITICAL: You MUST present a draft and wait for user approval. NEVER save without explicit confirmation.**

Show the user:

```
=== Captured Workflow Command ===

Suggested Name: <name>
Suggested Description: <description>
Location: ~/.claude/commands/<name>.md

--- Draft Preview ---
<show the complete command content>
--- End Preview ---

Key workflow steps captured:
1. <step 1>
2. <step 2>
...

Agentic patterns captured:
- <pattern>: <how it was used>
- <pattern>: <how it was used>
...

Arguments extracted:
- $1: <what it represents>
- $2: <what it represents>

---
Options:
- Type "yes" or "save" to save this command
- Type "edit" to request changes
- Suggest a different name/description
- Type "no" to cancel
```

### 8. Handle User Response

**If "yes" or "save":** Save the command to `~/.claude/commands/<name>.md`

**If user suggests different name/description:** Update and show revised draft

**If "edit":** Ask what changes are needed, revise, and present again

**If "no":** Ask what went wrong and whether to try a different approach

### 9. Confirm Save (only after approval)

After saving, verify and report:

```
Command saved: ~/.claude/commands/<name>.md

You can now use it with: /<name> [arguments]

Tip: Test your new command to verify it works as expected.
```

## Guidelines for Good Commands

**DO:**
- Keep commands focused on a single workflow
- Use clear, descriptive names for arguments
- Restrict allowed-tools to what's actually needed
- Capture orchestration patterns (parallelism, subagent delegation, iteration loops)
- Write commands as agent instructions, not human runbooks
- Aim for density — every line should carry its weight

**DON'T:**
- Capture one-off debugging steps
- Include hardcoded paths that won't work elsewhere
- Create commands that are too specific to be reusable
- Forget to parameterize variable elements
- Incorporate operating protocol from CLAUDE.md (PRAR phases, Chesterton's Fence, Definition of Done checklists, tone guidelines)
- Write human runbooks — write agent instructions that leverage Claude's tool-calling capabilities
- Pad with generic advice ("be thorough", "handle edge cases", "write clean code")
- Include codebase overviews or directory structure descriptions
- Restate information the agent can discover from existing files

## What to NEVER Include in Commands

These waste reasoning tokens and make commands perform worse:

1. **Generic quality advice** — "Write clean code", "Add error handling", "Be thorough". The agent already does this.
2. **Codebase overviews** — "The project uses React with Redux for state management". The agent can read config files.
3. **Standard tool usage** — "Use git to commit changes". The agent knows its tools.
4. **Meta-protocol** — PRAR phases, behavioral rules, tone instructions. These are session-level, not command-level.
5. **Redundant context** — Information already available through the command's `@` references or dynamic context.
6. **Defensive padding** — "If X doesn't work, try Y, or possibly Z". State the expected path. Handle failure in orchestration strategy only if a retry loop was actually part of the observed workflow.

## Example Transformation

**Conversation workflow observed:**
1. User asks to run evals and iterate until score improves
2. Claude uses Explore subagent to find eval config files
3. Claude reads 3 config files in parallel
4. Claude runs eval via Bash (background)
5. Eval fails — Claude diagnoses, fixes prompt, re-runs
6. Second run passes threshold
7. Claude asks user whether to commit or keep iterating

**Becomes command:**

The generated command file (described in prose to avoid parse issues):

- **Frontmatter:** description, argument-hint for eval name, allowed-tools including Bash, Read, Edit, Task, AskUserQuestion
- **Context section:** Dynamic context using bang-backtick to list available eval configs
- **Task Workflow section:**
  1. Locate eval configuration for the given argument
  2. Read eval config, prompt template, and scoring rubric (in parallel)
  3. Run the eval suite
  4. If score below threshold: analyze failures, identify root cause, fix prompt, re-run (loop up to 3 times)
  5. Present results to user for decision
- **Orchestration Strategy section:**
  - Use Explore subagent to locate eval files if directory structure is unknown
  - Read config files in parallel (single turn, multiple Read calls)
  - Run eval in background if it takes more than 30 seconds
  - Iterate on failures: read failure cases, diagnose pattern, edit prompt, re-run — max 3 iterations
  - Use AskUserQuestion after passing threshold to confirm commit vs. continue
- **Expected Outcome section:** Eval passing target threshold, with commit ready for user approval

## Handling Edge Cases

**If conversation has no clear workflow:**
Ask user to describe what they want to capture or point to specific messages.

**If workflow is too complex:**
Suggest breaking into multiple commands or simplifying.

**If no agentic patterns were used:**
The Orchestration Strategy section can be minimal or omitted — not every workflow needs complex orchestration.

**If `$1` is not provided:**
Ask user for a command name before proceeding.

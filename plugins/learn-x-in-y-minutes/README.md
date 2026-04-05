# learn-x-in-y-minutes

Generate a [learnxinyminutes.com](https://learnxinyminutes.com)-style tutorial for anything: a CLI command, language, library, framework, algorithm, concept, or GitHub repo.

Pulls from the right source for each subject — `man` pages and `--help` for commands, `gh` CLI for repos, WebFetch for docs, built-in knowledge for well-known topics — then produces a scannable tutorial in the format that fits the category.

## Examples

**CLI command:**
> "How does `cat` work?" / "Explain `awk` to me"

**GitHub repo:**
> "Generate a learnxinyminutes tutorial for https://github.com/sharkdp/bat"

**Local codebase:**
> "Quick-start guide for the current directory"

**Concept or algorithm:**
> "Explain consistent hashing" / "Quick overview of dynamic programming"

**Trigger phrases (no need to say "learnxinyminutes"):**
> "How does X work", "explain X", "quick-start guide for X", "quick overview of X"

## Output format by category

| Category | Structure |
|----------|-----------|
| Language | Short prose intro + one big code block with comment-style section dividers |
| Framework / Library | Same as language — `///` or `####` dividers inside a single code block |
| Tool | Concept prose → `## Commands` sections → per-command code blocks |
| Algorithm / DS | Concept explanation → annotated code examples → complexity table |

## Install

```
/plugin marketplace add CJHwong/claude-skills
/plugin install learn-x-in-y-minutes@claude-skills
```

# Research Data Reference

- **Source**: "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
- **Authors**: Gloaguen, Mündler, Müller, Raychev, Vechev (ETH Zurich / LogicStar.ai)
- **Date**: February 13, 2026
- **ArXiv**: 2602.11988v1

## Experimental Setup

### Agents Tested
- Claude Code with Sonnet-4.5 (temp=0)
- Codex with GPT-5.2 (temp=0)
- Codex with GPT-5.1 Mini (temp=0)
- Qwen Code with Qwen3-30B-Coder (temp=0.7, top-p=0.8)

### Benchmarks
- **SWE-Bench Lite**: 300 tasks, 11 popular Python repos, no dev-written context files
- **AgentBench (novel)**: 138 tasks, 12 niche Python repos, all with dev-written context files

### Three Settings
1. **None**: No context file
2. **LLM**: Auto-generated context file (using each agent's recommended init command)
3. **Human**: Developer-provided context file (AgentBench only)

## Key Results Tables

### Success Rates (approximate from Figure 3)

#### SWE-Bench Lite
| Model | None | LLM | Delta |
|-------|------|-----|-------|
| Sonnet-4.5 | ~54% | ~53% | -1% |
| GPT-5.2 | ~57% | ~55% | -2% |
| GPT-5.1 Mini | ~41% | ~40% | -1% |
| Qwen3-30B | ~38% | ~39% | +1% |

#### AgentBench
| Model | None | LLM | Human | LLM Δ | Human Δ |
|-------|------|-----|-------|-------|---------|
| Sonnet-4.5 | ~60% | ~56% | ~58% | -4% | -2% |
| GPT-5.2 | ~65% | ~62% | ~67% | -3% | +2% |
| GPT-5.1 Mini | ~40% | ~39% | ~44% | -1% | +4% |
| Qwen3-30B | ~37% | ~35% | ~43% | -2% | +6% |

### Cost and Steps (Table 2 from paper — exact values)

#### SWE-Bench Lite
| | Sonnet-4.5 | GPT-5.2 | GPT-5.1 Mini | Qwen3-30B |
|---|---|---|---|---|
| None: Steps | **54.4** | **12.5** | **40.9** | **29.7** |
| LLM: Steps | 57.2 | 12.7 | 45.2 | 32.2 |
| None: Cost($) | **1.30** | **0.32** | **0.18** | **0.12** |
| LLM: Cost($) | 1.51 | 0.43 | 0.22 | 0.13 |

#### AgentBench
| | Sonnet-4.5 | GPT-5.2 | GPT-5.1 Mini | Qwen3-30B |
|---|---|---|---|---|
| None: Steps | **40.7** | **12.1** | **40.6** | **31.5** |
| LLM: Steps | 46.5 | 13.1 | 46.9 | 34.2 |
| Human: Steps | 45.3 | 13.6 | 46.6 | 32.8 |
| None: Cost($) | **1.15** | **0.38** | **0.18** | **0.13** |
| LLM: Cost($) | 1.33 | 0.57 | 0.20 | 0.15 |
| Human: Cost($) | 1.30 | 0.54 | 0.19 | 0.15 |

### Reasoning Token Increase (Figure 7)
| Model | LLM (SWE-Bench) | LLM (AgentBench) | Human (AgentBench) |
|-------|-----------------|-------------------|---------------------|
| GPT-5.2 | +22% | +14% | +20% |
| GPT-5.1 Mini | +14% | +10% | +2% |

### Tool Usage When Mentioned vs Not (Section 4.3)
- `uv`: 1.6 calls/instance when mentioned, <0.01 when not mentioned
- `repo_tool`: 2.5 calls/instance when mentioned, <0.05 when not mentioned
- This pattern holds across nearly all measured tools

### Context File Statistics (Table 1 — AgentBench repos)
| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Words | 641.0 | 24 | 2003 |
| Sections | 9.7 | 1 | 29 |

### Overview Prevalence in LLM-Generated Files
- Sonnet-4.5: 100% contain overviews
- GPT-5.2: 99% contain overviews
- Qwen3-30B: 95% contain overviews
- GPT-5.1 Mini: 36% contain overviews

### Documentation Removal Experiment (Figure 5)
When all .md files, example code, and docs/ are removed from repos:
- LLM-generated context files improve performance by +2.7% on average
- LLM-generated files outperform developer-written files in this setting
- Conclusion: context files are only clearly helpful as a *substitute* for missing docs

## AgentBench Repositories
The 12 repos with developer-written context files:
ragas (14), smolagents (16), openai-agents-python (17), transformers (6), pr-agent (10), graphiti (3), fastmcp (12), wagtail (12), opshin (14), ansible (11), pdm (10), tinygrad (13)

## Key Ablation Findings
1. **Stronger models don't generate better context files** — GPT-5.2 generated files improved SWE-Bench (+2%) but degraded AgentBench (-3%)
2. **Different prompts don't matter much** — Codex vs Claude Code prompts showed no consistent winner
3. **Per-repository analysis** — No single repo showed significant impact from context files

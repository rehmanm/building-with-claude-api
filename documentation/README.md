# Claude Certified Architect – Foundations: Study Documentation

Week-by-week study notes, quiz questions, answers, and explanations for the
**Claude Certified Architect – Foundations** certification exam.

**Target exam date:** Oct 31, 2026
**Pass score:** 720 / 1000
**Format:** Multiple choice — 1 correct + 3 distractors. No penalty for guessing.

## Domain weightings

| Domain | Weight |
|---|---|
| 1. Agentic Architecture & Orchestration | 27% |
| 3. Claude Code Configuration & Workflows | 20% |
| 4. Prompt Engineering & Structured Output | 20% |
| 2. Tool Design & MCP Integration | 18% |
| 5. Context Management & Reliability | 15% |

## The decision heuristics that win most questions

- Deterministic guarantee needed (money, identity, ordering) → **hooks / programmatic enforcement**, never prompts.
- Probabilistic quality improvement → **prompts / few-shot / better tool descriptions**, not classifiers or new infra.
- LLM self-reported confidence & customer sentiment → **unreliable proxies**; rarely the answer.
- "First step" / "most effective" → the **low-effort, high-leverage root-cause fix**, not the architectural rewrite.
- **A true fact that doesn't match the symptom is still the wrong answer.**
- **Read the whole option** — distractors bury the fatal clause after a reasonable-sounding opening.

## Index

| Week | Topic | Notes | Flashcards | Status |
|---|---|---|---|---|
| Week 1 | The agentic loop (`stop_reason`, tool-result handling, anti-patterns) | [notes](week-01-agentic-loop.md) | [cards](week-01-flashcards.md) | ✅ Complete |
| Week 2 | Multi-agent orchestration (hub-and-spoke, subagents, decomposition) | [notes](week-02-multi-agent-orchestration.md) | [cards](week-02-flashcards.md) | ✅ Complete |
| Week 3 | Hooks, enforcement & handoffs | [notes](week-03-hooks-enforcement.md) | — | In progress |
| Week 4 | Task decomposition & sessions | — | — | Pending |
| Week 5 | Domain 1 consolidation + Exercise 1 | — | — | Pending |
| Week 6 | CLAUDE.md hierarchy & rules | — | — | Pending |
| Week 7 | Commands, skills & plan mode | — | — | Pending |
| Week 8 | Claude Code in CI/CD + Exercise 2 | — | — | Pending |
| Week 9 | MCP integration (Domain 2) | — | — | Pending |
| Week 10 | Structured output & tool_use (Domain 4) | — | — | Pending |
| Week 11 | Validation, batch & multi-pass review + Exercise 3 | — | — | Pending |
| Week 12 | Context management & reliability (Domain 5) | — | — | Pending |
| Week 13 | Full practice pass + Exercise 4 | — | — | Pending |
| Week 14 | Targeted gap-filling | — | — | Pending |
| Week 15 | Final review & exam | — | — | Pending |

## ⚠️ Exam-guide vs. current-docs naming drift

Answer the **exam** with the guide's terms; know the current terms so live docs don't confuse you.

| Concept | Exam guide (Feb 2025) | Current docs | Answer on exam |
|---|---|---|---|
| Subagent-spawning tool | `Task` | `Agent` (renamed in Claude Code v2.1.63) | `Task` |
| Allow-list field value | `allowedTools` includes `"Task"` | `allowedTools` includes `"Agent"` | `"Task"` |
| Config object | `AgentDefinition` | `AgentDefinition` (unchanged) | no conflict |

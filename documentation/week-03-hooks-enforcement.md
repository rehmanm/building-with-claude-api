# Week 3 — Hooks, Enforcement & Handoffs

**Domain:** 1 (Agentic Architecture & Orchestration) — Task Statements 1.4 & 1.5
**Status:** In progress — concepts captured; quiz Q&A to be appended after the quiz

## Resources
- [Intercept and control agent behavior with hooks](https://code.claude.com/docs/en/agent-sdk/hooks) — PRIMARY (read "How hooks work," "Available hooks," and the PreToolUse / PostToolUse examples; skip the long tail of TS-only hook events)
- Exam guide **sample Q1** (block `process_refund` until `get_customer` verified) — the Week 3 concept in one question

---

## Concepts

### The mental model
A **hook** is a callback that fires at a defined point in the agent loop, receives
details about what's happening (tool name, arguments, session ID), and returns a
decision: **allow / block / modify / inject.**

### The two hooks that matter for the exam
| Hook | Fires | Superpower | Exam use |
|---|---|---|---|
| `PreToolUse` | *Before* a tool call executes | **Block or modify the outgoing call** | Enforce compliance — block refunds > $500, block `process_refund` until identity verified, redirect to escalation |
| `PostToolUse` | *After* a tool returns its result | **Transform/normalize the result** before the model sees it | Normalize heterogeneous data (Unix timestamps, ISO 8601, numeric status codes) from different MCP tools |

### The PreToolUse block mechanism
The callback inspects the tool's input and, to block, returns
`permissionDecision: "deny"` with a **reason string**. The tool never runs; the model
is told why and adapts. That reason string is how you "redirect to an alternative
workflow" (e.g., human escalation).

### The dominant heuristic (this week AND the exam)
> **Deterministic compliance → hook. Probabilistic guidance → prompt.**

- **Must be a hook** when the rule *cannot* be violated: money (refund thresholds),
  identity (verify-before-act), ordering (prerequisite gates), destructive-action guards.
  A prompt instruction has a **non-zero failure rate** — fine for guidance, fatal for guarantees.
- **A prompt is enough** for style, tone, soft preferences — where an occasional miss is acceptable.

Same "structured contract, not prose" spine as Week 1, applied to **enforcement**.

### Three testable facts
1. **`PreToolUse` = the enforcement hook.** Blocks/modifies *before* execution. The answer
   whenever a stem says "guarantee," "must," "policy," "compliance," "before processing X."
2. **`PostToolUse` = the normalization hook.** Transforms *results* before the model reasons
   on them. The answer for "different tools return different formats — how do you standardize?"
3. **Structured handoff on escalation.** When escalating to a human who can't see the
   conversation, compile a structured summary: **customer ID, root cause, refund amount,
   recommended action.** (Domain 1.4 — the handoff half of the week.)

### The Week-3 distractor trap
The exam offers a **prompt-based** fix as a tempting distractor for a problem that demands a
hook. Sample Q1 archetype: "system prompt says verification is mandatory" and "few-shot
examples showing the right order" both rely on **probabilistic LLM compliance** — wrong when
money's involved. The hook is the only deterministic guarantee.

**Watch for:** "enhance the system prompt to…", "add few-shot examples showing…", "instruct
the agent to always…" as distractors when the stem says **guarantee / must / policy / financial**.

### Connections to earlier weeks
- **Week 1 echo:** structured contract (a hook's decision) beats prose (a prompt instruction).
- **Carded Week-2 gap (structured error handling):** a `PreToolUse` block that returns a
  reason and redirects *is* the deterministic version of "handle it gracefully and route on."

---

## Quiz — Questions, Answers, Explanations
_(to be appended after the Week 3 quiz)_

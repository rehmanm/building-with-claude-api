# Week 2 — Multi-Agent Orchestration

**Domain:** 1 (Agentic Architecture & Orchestration) — Task Statements 1.2 & 1.3
**Status:** ✅ Complete — quizzes 5/7, then distractor-discipline drills

## Resources
- [Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents) — PRIMARY
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) — filesystem-based, built-in, nesting
- [Dynamic workflows](https://code.claude.com/docs/en/workflows) — large-scale orchestration (skim)

---

## Concepts

### Architecture: Hub-and-spoke (coordinator ↔ subagents)
```
                    ┌───────────────┐
              ┌────▶│  Web Search   │  (spoke)
              │     └───────────────┘
┌─────────────┴─┐   ┌───────────────┐
│  COORDINATOR  │──▶│ Doc Analysis  │  (spoke)
│    (hub)      │   └───────────────┘
└─────────────┬─┘   ┌───────────────┐
              └────▶│  Synthesis    │  (spoke)
                    └───────────────┘
```
**Defining rule: spokes never talk to each other. All communication goes through the hub.**

Coordinator (hub) owns four jobs: **task decomposition, delegation, result
aggregation, routing & error handling.**

**Why hub-and-spoke, not a mesh?** Observability · consistent error handling ·
controlled information flow. If an answer proposes direct spoke-to-spoke communication,
it's the distractor.

### Workflow patterns that run *on* the architecture
| Pattern | What it is | When it's the answer |
|---|---|---|
| Static pipeline (prompt chaining) | Fixed A→B→C every time | Predictable, steps known in advance |
| Dynamic decomposition | Coordinator generates subtasks from findings | Open-ended investigation |
| Parallel fan-out | Multiple subagents in ONE coordinator response | Independent subtasks (finish in slowest, not sum) |
| Iterative refinement loop | Evaluate synthesis for gaps → re-delegate → re-synthesize | Research quality control; *fixes* the Q7 incomplete-coverage problem |
| Scope partitioning | Assign distinct subtopics/source-types per subagent | Broad topics, minimize duplication |

**Design principle:** coordinator prompts specify **goals and quality criteria**, not
step-by-step procedures. Goals > scripts (the multi-agent echo of Week 1's model-driven
vs pre-configured).

### Subagent mechanics (six facts)
1. **Fresh context, always.** A subagent receives its own system prompt + the prompt
   string passed via the Task tool (+ project CLAUDE.md if configured). It does **not**
   receive the parent's conversation history, tool results, or system prompt.
   → Put every file path, prior finding, error, decision in the prompt string. **#1 trap.**
2. **Only the final message returns** to the parent. Intermediate tool calls/results stay
   inside the subagent — this is the whole point (context isolation).
3. **`AgentDefinition` fields:** `description` (tells the coordinator *when* to invoke —
   drives auto-delegation), `prompt` (role/behavior), `tools` (restrict; omit = inherit all).
4. **Tool restriction = safety + reliability.** A tool left out **isn't in the subagent's
   session at all** — no error, no prompt, just absent.
5. **Delegation is `description`-driven (automatic) or name-driven (explicit).**
6. **Parallel = multiple Task calls in ONE response.** Splitting across turns = sequential.

---

## Quiz Round 1 — Questions, Answers, Explanations

### Q1
Coordinator tries to spawn a subagent but just answers directly instead. Most likely cause?

A) Subagent's `prompt` too long
B) `allowedTools` doesn't include `"Task"`, so the spawn isn't approved
C) Coordinator's model too small
D) Subagent given no `tools`

**Answer: B**
The spawn isn't approved without `"Task"` in `allowedTools`.
**Distractor note (A):** the Windows 8191-char prompt limit is real but causes a subagent
with a long *prompt* to *fail* — not a coordinator declining to delegate. A true fact that
doesn't match the symptom is still wrong.

### Q2
A synthesis subagent needs earlier subagents' outputs. How does that information reach it?

A) Automatically inherited from the coordinator's conversation history
B) The coordinator must include those findings directly in the synthesis subagent's prompt
C) Subagents share a common memory store
D) The synthesis subagent re-runs the earlier subagents

**Answer: B**
Fresh context, no inheritance — pass findings in the prompt string.

### Q3 (Sample Q7 pattern)
Research on "AI in creative industries." Every subagent succeeds, but the report only
covers visual arts. Coordinator log shows it decomposed into digital art / graphic design /
photography. Root cause?

A) Synthesis lacks gap-detection instructions
B) Coordinator's task decomposition too narrow — subagents assigned scope that didn't cover the full topic
C) Web-search queries not comprehensive
D) Doc-analysis filtered out non-visual sources

**Answer: B**
The gap was baked in at **decomposition time**. Subagents did their assigned jobs
perfectly. **Principle:** when every subagent "succeeds" but coverage is incomplete,
suspect the coordinator's decomposition — not the correctly-working downstream agents.
Adding gap-detection to synthesis (A) can't recover data no subagent was ever tasked to gather.

### Q4
Coordinator needs to run two independent subagents in parallel. How?

A) Emit both `Task` tool calls in a single coordinator response
B) Call the first, wait, then call the second next turn
C) Merge them into one subagent
D) Parallel execution isn't possible

**Answer: A**

### Q5
In hub-and-spoke, why route all inter-subagent communication through the coordinator?

A) Only technically possible design
B) For observability, consistent error handling, and controlled information flow
C) Subagents can't produce output
D) To reduce token usage

**Answer: B**

### Q6 (Sample Q9 pattern)
Synthesis agent round-trips through the coordinator to verify simple facts (+40% latency).
85% simple fact-checks, 15% deep. Best fix?

A) Give synthesis a scoped `verify_fact` tool for simple lookups; keep complex verifications routing through the coordinator
B) Give synthesis access to *all* web-search tools
C) Batch all verification needs and send at end of pass
D) Web-search agent pre-caches extra context around every source

**Answer: A**
Principle of least privilege — optimize the common case with a narrowly scoped tool.
**Distractor note (B):** over-provisions the synthesis agent, inviting misuse and
violating separation of concerns. NOTE: this is **API-level tool distribution**, distinct
from the Claude Code `allowedTools` approval list in Q1.

### Q7
When a subagent finishes, what does the coordinator receive back?

A) The entire transcript, including every intermediate tool call/result
B) Only the subagent's final message
C) Nothing — coordinator must poll
D) A live stream of reasoning tokens

**Answer: B**

---

## Distractor-Discipline Drill — Questions, Answers, Explanations

Format practiced: **letter + why + why the top distractor is wrong.**

### D1
Reports consistently miss entire subtopics though each subagent completes flawlessly.
*Prevent* it going forward. Best design change?

A) Add gap-detection to the synthesis subagent's prompt
B) Give the coordinator an iterative refinement loop (evaluate synthesis for gaps → re-delegate → re-synthesize until sufficient)
C) More capable synthesis model
D) Increase each subagent's `max_tokens`

**Answer: B** — the coordinator must check coverage and re-delegate; a one-shot
decomposition can't self-correct. **A** patches downstream and can't recover un-gathered data.

### D2
A subagent must know that `auth/session.py` was the bug source the coordinator found earlier,
but acts as if it has no idea which file to look at. Why, and fix?

A) Model too small
B) Subagents don't inherit parent context — the coordinator must include `auth/session.py` (and the finding) in the subagent's prompt string
C) Missing the Read tool
D) Needs a shared memory store to query

**Answer: B** — symptom is "no idea *which* file" = missing **context**, not missing tool.
**C is the trap:** a Read tool lets you open a file only if you already know which one; the
subagent doesn't, because it never received the coordinator's finding.

### D3
Three independent review agents. Teammate proposes direct spoke-to-spoke messaging to save a
round-trip. Evaluate.

A) Good — reduces latency
B) Reject — routing through the coordinator preserves observability, consistent error handling, and controlled flow; run the three in parallel instead
C) Good, if all three share a memory store
D) Reject — subagents can't produce usable output

**Answer: B** — direct spoke-to-spoke isn't impossible (agents like SendMessage exist);
it's **rejected by design** because it destroys the hub's guarantees. **D is wrong** because
subagents obviously produce output.

### D4
A subagent's web-search call times out. What should it return to the coordinator?

A) Retry with backoff internally; on final failure return a generic "search unavailable" status
B) Return structured error context: failure type, attempted query, partial results, alternatives
C) Catch the timeout and return an empty result marked successful
D) Propagate the exception to a top-level handler that terminates the whole workflow

**Answer: B** — the coordinator makes recovery decisions, so hand it rich structured context.
**A is the trap:** it *sounds* responsible (it retries!) but its tail returns a **generic
status** that hides the context the coordinator needs. Read the whole option — the flaw is at the end.

### D5
Coordinator prompt: "Step 1 search X. Step 2 search Y. Step 3 synthesize." Reviews come back
narrow. Best change for adaptability?

A) Add two more hard-coded search steps
B) Rewrite the prompt to specify goal + quality criteria ("comprehensively cover all major sectors; omit no major domain") rather than fixed steps
C) Increase the iteration cap
D) Give more search tools

**Answer: B** — goals over scripts.

### D6
A `doc-reviewer` defined with `tools=["Read","Grep","Glob"]`. The task would require it to
*edit* a file. What happens?

A) It edits; restrictions are advisory
B) It can't edit — Edit/Write aren't in its session at all; it works within read-only tools with no error
C) The run crashes with a permission error
D) It escalates to the coordinator to request Edit access

**Answer: B** — restricted tool = **absent, not denied**. Nothing to crash on.
**C is the trap:** picturing runtime permission systems where "no access → error." Here the
tool was never loaded, so no exception is raised. Mental model: **"not in the room," not
"locked door."**

---

## Two carded gaps to keep drilling
1. **Subagent error handling:** local recovery for transient errors → then return
   **structured** context (type, attempt, partial, alternatives). Never generic. Never halt-all.
2. **Tool restriction:** **omission, not denial.** Absent tool = works without it, no error.

## Key takeaways
> When subagents all "succeed" but output is incomplete, the fault is almost always the
> **coordinator's task decomposition** — not the downstream agents.

> A **true fact that doesn't match the symptom** is still the wrong answer. **Read the whole
> option** — distractors bury the fatal clause after a reasonable-sounding opening.

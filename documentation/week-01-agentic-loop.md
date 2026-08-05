# Week 1 — The Agentic Loop

**Domain:** 1 (Agentic Architecture & Orchestration) — Task Statement 1.1
**Status:** ✅ Complete — quiz 6/6

## Resources
- [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- [Tutorial: Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent)
- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [How the agent loop works (Agent SDK)](https://code.claude.com/docs/en/agent-sdk/agent-loop)

---

## Concepts

### The core idea
An "agent" is a **loop** you (the harness) run around the model. The model can't
execute anything itself — it only *says* "I want to call tool X with these inputs."
Your code executes the tool and hands the result back. Repeat until the model says
it's done. The loop is driven by **one field in every response: `stop_reason`.**

### The lifecycle
```
1. Send request to Claude (messages + tools)
2. Claude responds. Inspect stop_reason:
      ├─ "tool_use"  → Claude wants a tool.
      │                 a. Execute the requested tool(s)
      │                 b. Append the assistant's tool_use block to history
      │                 c. Append the tool_result (with matching tool_use_id) to history
      │                 d. GO BACK TO STEP 1
      │
      └─ "end_turn"  → Claude is done. Present the final response. STOP.
```
**Loop while `stop_reason == "tool_use"`; terminate on `"end_turn"`.**

### History-appending rules (tested)
- Append **both** the assistant's `tool_use` block **and** the `tool_result`.
- The `tool_result` must carry the **matching `tool_use_id`**.
- If multiple tools were called in one turn, return **all** results in a **single**
  user message before looping.
- The API is **stateless** — it remembers nothing; you resend full history each turn.

### Model-driven vs pre-configured
| Model-driven (correct) | Pre-configured (distractor) |
|---|---|
| Claude reasons about which tool to call next from context | Hard-coded decision tree / fixed tool sequence |
| Adapts when a tool returns something unexpected | Breaks when reality doesn't match the script |

### The three loop-termination anti-patterns (answer-eliminators)
1. **Parsing natural-language signals** to decide the loop is done ("if text contains 'complete', stop").
2. **Arbitrary iteration caps as the primary stopping mechanism** (a cap is a *backstop*, not the decision).
3. **Checking assistant text content as a completion indicator.**

Unifying principle: **terminate on the structured `stop_reason` field, not on interpreting the model's words.**

---

## Quiz — Questions, Answers, Explanations

### Q1
Your agent loop stops when the model's text output contains "I've completed the task."
It sometimes terminates early or hangs. Best fix?

A) Add more phrase variants to match
B) Terminate based on `stop_reason == "end_turn"` instead of parsing text
C) Set a hard cap of 10 iterations as the primary stopping mechanism
D) System-prompt the model to always end with the exact string "TASK_COMPLETE"

**Answer: B**
Terminate on the structured `stop_reason` field. A and D are "parse the text"
anti-patterns (fragile — phrasing varies). C makes a *safety backstop* the *primary*
decision, which the guide explicitly calls an anti-pattern.

### Q2
After Claude returns `stop_reason: "tool_use"` and you execute the tool, what must you
append to history before the next call?

A) Only the tool's result text as a new user message
B) The assistant's `tool_use` block, then a `tool_result` block with the matching `tool_use_id`
C) A summary of what the tool did, to save context tokens
D) Nothing — the API remembers the previous turn automatically

**Answer: B**
Append the assistant's `content` (incl. `tool_use`) **and** a `tool_result` with the
matching `tool_use_id` — the id threads result → call. **D is the trap:** the API is
stateless; it remembers nothing.

### Q3
A support agent is a fixed sequence: always `get_customer` → `lookup_order` →
`process_refund`. It mishandles requests that don't fit that order. Most accurate
description of the problem?

A) Tool descriptions too vague
B) Needs a larger context window
C) Uses a pre-configured tool sequence instead of letting the model decide which tool to call next based on context
D) Iteration cap too low

**Answer: C**
The rigid hard-coded sequence is the fault. A/B/D blame the wrong layer.

### Q4
Which is a *legitimate* use of an iteration cap?

A) As the primary mechanism to decide the task is finished
B) As a safety backstop against runaway loops, while `stop_reason` remains the real termination signal
C) To force the model to call exactly N tools before responding
D) Iteration caps should never be used

**Answer: B**
Cap = safety backstop, never the termination decision.

### Q5
In one turn Claude returns **two** `tool_use` blocks (parallel). How to return results?

A) Send the first, wait, then send the second in a later turn
B) Return both `tool_result` blocks in a single user message, each with its matching `tool_use_id`
C) Merge both into one `tool_result` with a combined id
D) Return only the more important result

**Answer: B**
All results in **one** user message, each with its own id. Splitting across turns
(A) silently trains the model to stop making parallel calls; dropping one (D) breaks the turn.

### Q6
Which single field is the authoritative signal to branch on for "call a tool" vs "done"?

A) The presence of any text in `content`
B) `stop_reason`
C) The `usage.output_tokens` count
D) Whether the last `content` block is a `tool_use` block

**Answer: B**
`stop_reason` is the contract. **D is a well-designed distractor** — "is the last block
a tool_use?" correlates in practice but the structured field is what you branch on.

---

## Key takeaway
> **Branch on the structured `stop_reason` field, not on interpreting the model's words.
> Enforcement and termination come from your code's contract with the API, not from prose.**

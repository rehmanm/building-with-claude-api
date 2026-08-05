# Week 2 Flashcards — Multi-Agent Orchestration

Active recall. Read the **Q**, answer out loud/in your head, then reveal **A**.

---

**Q:** Name the multi-agent architecture the exam is built on.
**A:** Hub-and-spoke — a coordinator (hub) and subagents (spokes).

---

**Q:** In hub-and-spoke, can subagents talk to each other directly?
**A:** No. All communication routes through the coordinator.

---

**Q:** Why route everything through the coordinator instead of a mesh?
**A:** Observability, consistent error handling, and controlled information flow.

---

**Q:** What are the coordinator's four jobs?
**A:** Task decomposition, delegation, result aggregation, and routing/error handling.

---

**Q:** Does a subagent inherit the coordinator's conversation history, tool results, or system prompt?
**A:** No. It starts with **fresh context** — only its own system prompt plus the prompt string passed via the Task tool (and project CLAUDE.md if configured).

---

**Q:** If a subagent needs a file path or a prior finding, how does it get it?
**A:** The coordinator must put it **directly in the subagent's prompt string**. (The #1 Week-2 trap.)

---

**Q:** When a subagent finishes, what does the coordinator receive?
**A:** Only the subagent's **final message**. Intermediate tool calls/results stay inside the subagent.

---

**Q:** Name the three `AgentDefinition` fields and what each does.
**A:** `description` (tells the coordinator *when* to invoke it — drives auto-delegation), `prompt` (the subagent's role/behavior), `tools` (restricts what it can do; omit = inherit all).

---

**Q:** How do you spawn subagents in parallel?
**A:** Emit multiple Task tool calls in a **single** coordinator response. (Wall-clock = slowest one, not the sum.)

---

**Q:** A subagent is defined with `tools=["Read","Grep"]` but needs to edit a file. What happens?
**A:** It **can't** — Edit/Write were never in its session. No crash, no error, no prompt; it works within its tools. Restricted = **absent, not denied** ("not in the room," not "locked door").

---

**Q:** Every subagent succeeds but the final report misses whole subtopics. Where's the fault?
**A:** The **coordinator's task decomposition** was too narrow. Downstream agents worked correctly within their assigned scope. (Sample Q7 pattern.)

---

**Q:** How do you *prevent* narrow-decomposition coverage gaps going forward?
**A:** Give the coordinator an **iterative refinement loop**: evaluate synthesis for gaps → re-delegate targeted queries → re-synthesize until coverage is sufficient.

---

**Q:** Synthesis agent round-trips through the coordinator for simple fact-checks (85% simple, 15% complex). Best fix?
**A:** Give it a **scoped `verify_fact` tool** for the simple case; keep complex verifications routing through the coordinator. (Least privilege — don't over-provision. Sample Q9 pattern.)

---

**Q:** Static pipeline vs dynamic decomposition — when each?
**A:** Static pipeline (prompt chaining) for predictable work with steps known in advance. Dynamic decomposition for open-ended investigation where subtasks emerge from findings.

---

**Q:** Should a coordinator prompt give step-by-step procedures or goals?
**A:** Goals and quality criteria, not scripts. Goals let subagents adapt; scripts reproduce failures like narrow decomposition.

---

**Q:** A subagent's tool call hits a transient timeout. What should it return to the coordinator?
**A:** Recover locally first (retry the transient error); on final failure return **structured context** — failure type, attempted call, partial results, alternatives. Never a generic status, never silent success, never halt-the-whole-workflow.

---

**Q:** Exam-guide term for the subagent-spawning tool vs the current-docs term?
**A:** Exam guide says `Task` (and `allowedTools` must include `"Task"`). Current docs say `Agent` (renamed in v2.1.63). **Answer `Task` on the exam.**

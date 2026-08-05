# Week 1 Flashcards — The Agentic Loop

Active recall. Read the **Q**, answer out loud/in your head, then reveal **A**.

---

**Q:** What single field in a Claude response drives the agentic loop?
**A:** `stop_reason`.

---

**Q:** What are the two `stop_reason` values that control the loop, and what does each mean?
**A:** `"tool_use"` = Claude wants a tool; execute it and loop again. `"end_turn"` = Claude is done; stop.

---

**Q:** After executing a tool, what TWO things do you append to `messages` before the next call?
**A:** (1) The assistant's `content` including its `tool_use` block, and (2) a `tool_result` block carrying the matching `tool_use_id`.

---

**Q:** What connects a `tool_result` back to the specific call it answers?
**A:** The matching `tool_use_id`.

---

**Q:** Does the Claude API remember previous turns for you?
**A:** No — it's **stateless**. You resend the full conversation history every request.

---

**Q:** Claude returns two `tool_use` blocks in one turn. How do you return the results?
**A:** All `tool_result` blocks in a **single** user message, each with its own `tool_use_id`.

---

**Q:** What happens if you split parallel tool results across multiple turns?
**A:** It works but silently trains the model to **stop making parallel calls** (and adds latency).

---

**Q:** Name the three loop-termination anti-patterns.
**A:** (1) Parsing natural-language signals ("if text says 'done', stop"), (2) using an arbitrary iteration cap as the *primary* stop mechanism, (3) checking assistant text content as a completion indicator.

---

**Q:** Is an iteration cap ever legitimate?
**A:** Yes — as a **safety backstop** against runaway loops. Never as the primary termination *decision* (that's `stop_reason`).

---

**Q:** Model-driven vs pre-configured decision-making — which is the correct agentic pattern, and why?
**A:** Model-driven. Claude reasons about which tool to call next from context and adapts to unexpected results. A hard-coded decision tree / fixed sequence breaks when reality doesn't match the script.

---

**Q:** A loop stops when the model's text contains "task complete" and sometimes ends early or hangs. Root fix?
**A:** Terminate on `stop_reason == "end_turn"`, not on parsing text.

---

**Q:** One-sentence spine of Week 1?
**A:** Branch on the structured `stop_reason` field, not on interpreting the model's words.

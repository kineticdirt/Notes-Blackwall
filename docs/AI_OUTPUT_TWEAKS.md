# Content Tweaks for Faster, More Dynamic AI Output

Tweaks to **prompts, rules, and instructions** (not code or infra) so the AI system feels **faster**, **more dynamic**, and **higher quality** in terms of what it says and does. Focus: **output** (time-to-good-answer, relevance, consistency), not compute efficiency.

---

## 1. Lead with the answer (Cursor / Composer)

**Idea:** The model often explains before acting. Reversing that reduces perceived lag and makes the first line useful.

**Tweak:** Add a rule (e.g. `.cursor/rules/output-behavior.mdc`) that says:

- **Lead with the action or answer** — First sentence = what you’re doing or the direct answer. Then add brief justification or detail if needed.
- **Structured when helpful** — Use bullets, tables, or “Summary → Detail” so the user can scan. Avoid long prose when a list or one-liner suffices.
- **One clear recommendation** — When there are options, state your recommended choice first and why in one line; then list alternatives briefly.

**Effect:** Faster “time to first useful token” and less scrolling to find the actual answer.

---

## 2. Progress and notes as default (dynamic, resume-friendly)

**Idea:** If the model always checks shared state first and saves at the end, responses stay **dynamic** (adapted to what’s already done) and **fast to resume** (no reprompting).

**Tweak:** In the same rule or in `docs/CURSOR_ROLEPLAY_AND_NOTES_GUIDE.md`, make this the default Composer behavior:

- **Start of task:** Call `read_progress()` (and optionally `read_notes(section="progress")`) **before** answering or planning. If there’s saved state, say “Resuming from: [one line]” and continue from `next_steps`.
- **End of task or pause:** Call `save_progress(summary, next_steps, completed)` so the next turn or agent can continue without the user re-explaining.
- **When you learn something that changes assumptions:** Use `update_belief` so future turns and other agents see it.

**Effect:** Responses adapt to current state (dynamic), and new sessions start from last progress (faster effective start).

---

## 3. Subagent instructions: lead + coordinate

**Idea:** Cleanup, test, and doc agents can be faster and more consistent if they’re told to lead with the outcome and always read scratchpad first.

**Tweak:** In `agent-system/.claude/agents/cleanup-agent.md`, `test-agent.md`, `doc-agent.md`, add a short **Output & coordination** section:

- **Lead with the outcome** — First line: what you changed or recommend (e.g. “Removed 3 dead imports in X, Y, Z; fixed lint in W”). Then detail.
- **Read scratchpad first** — Before planning, read relevant scratchpad sections (code_notes, test_notes, doc_notes) so you don’t duplicate or conflict.
- **One clear next step** — End with a single recommended next step for the user or the next agent (e.g. “Run tests in `foo/` next” or “Doc agent: please add API doc for `bar()`”).

**Effect:** Subagent replies are scannable and better coordinated; less back-and-forth.

---

## 4. Workflow canvas AI: action-first, parseable

**Idea:** The workflow AI gateway (`ai_gateway.py`) drives canvas actions. Asking for **action first, then explanation** makes parsing reliable and the UI feel responsive.

**Tweak:** In `_build_system_prompt`, add one short block:

- **Response format:** Start your reply with the action (e.g. “Action: add_node, block_type: mcp_tool”) or a single-line summary of what you’re doing. Then add a brief, friendly explanation. This helps the system parse the action quickly and show progress.

**Effect:** More reliable extraction of `add_node` / `execute_workflow` etc., and the user sees “doing X” immediately.

---

## 5. Notes MCP tool descriptions (nudge timing)

**Idea:** Tool descriptions are the only “prompt” the model sees for when to call them. Nudging “call early” / “call before ending” improves actual usage.

**Tweak:** In `blackwall/mcp/notes_mcp_server.py`, keep descriptions short but add a timing hint where useful:

- `read_progress`: add “Call **at the start** of a task or new conversation to resume without the user reprompting.”
- `read_notes`: add “Call **early** when you need context from other agents or prior work.”
- `save_progress`: add “Call **before ending or pausing** so the next turn or agent can continue immediately.”
- `read_beliefs`: add “Call when you need shared assumptions or evidence; keeps output consistent with current beliefs.”

**Effect:** Model is more likely to call read_* first and save_* last, which maximizes dynamism and reduces redundant reasoning.

---

## 6. Anti-ramble, pro-concision (optional rule)

**Idea:** A short rule that discourages long preambles and encourages “answer first, then detail” improves perceived speed and clarity.

**Tweak:** Add to the same output-behavior rule:

- **Be concise unless depth is asked** — If the user asks a yes/no or “how do I X?”, answer in one sentence first, then expand only if needed. If they ask for detail or explanation, then provide it.
- **No recap of the question** — Don’t repeat the user’s message back at length; assume they know what they asked.

**Effect:** Less filler, faster to the useful part.

---

## 7. One rule file to apply all of the above

You can fold sections 1, 2, 6 into a **single Cursor rule** so Composer and chat see it everywhere. Suggested filename: `.cursor/rules/output-behavior.mdc`. Content: a short bullet list covering:

- Lead with action/answer; then detail.
- At task start: call `read_progress` (and `read_notes` if needed); resume from saved state when present.
- Before ending/pausing: call `save_progress` with summary and next steps.
- When assumptions change: `update_belief`.
- Be concise unless the user asks for depth; no long recap of the question.
- Prefer structured output (bullets, one clear recommendation first).

---

## Summary

| Lever | What to change | Effect on output |
|-------|----------------|------------------|
| Cursor rule | Lead with answer; structured; concise; progress read/save | Faster, more dynamic, resume-friendly |
| Subagent .md | Lead with outcome; read scratchpad first; one next step | Faster, better coordinated |
| Workflow AI prompt | Action first, then explanation | More parseable, feels faster |
| Notes MCP tool text | “Call at start” / “Call before ending” | Better use of progress/notes → more dynamic |
| Optional rule | Anti-ramble, no long recap | Less filler, quicker to useful content |

All of these are **content-only** (no new services or languages). They make the AI **feel** faster and more dynamic by shaping how it uses existing tools and how it formats its replies.

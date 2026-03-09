# Roleplay, Persistent Notes, and Progress Persistence in Cursor

This setup does three things:

1. **Parallel agents** — Shared notes and progress so multiple agents (or Composer sessions) can coordinate: read what others did, avoid duplicate work, and hand off cleanly.
2. **Save progress** — Agents write summaries, next steps, and completed items to a persistent store so the next turn (or a new conversation) can **resume without the user reprompting or manually re-pasting context**. Context window limits matter less because state lives in the notes file.
3. **Roleplay + BDH-style context** — Optional role/persona and beliefs with likelihood/evidence so behavior stays consistent and evidence-based.

---

## Summary of options

| Goal | Native (no MCP) | Via MCP |
|------|------------------|---------|
| **Parallel agents / shared context** | Single file all agents read/write; conventions for sections | MCP: `read_notes`, `append_note`, `read_progress`, `save_progress` |
| **Save progress (resume without reprompting)** | One file with “last summary + next steps”; AI reads it at start | MCP: `save_progress`, `read_progress` so agent persists state and next agent/session resumes from it |
| **Roleplay / persona** | Cursor Rules + optional notes file | `get_role` / `set_role` or AgentPersona |
| **BDH-style (likelihood + evidence)** | Notes file with structured schema (see below) | `read_beliefs`, `update_belief` |

---

## 1. Progress persistence and parallel agents

**Why:** So agents can **save progress** (summary, next steps, completed items) and the next agent or new conversation can **resume without the user reprompting or manually shrinking context**.

### How it works

- **Single shared store** (file or MCP): All agents read/write the same notes and a dedicated **progress** slot.
- **Before starting:** Agent calls `read_progress()` (and optionally `read_notes`) to see what’s already done and what’s next.
- **While working:** Agent can `append_note` for discoveries or coordination (e.g. section `"progress"` with a prefix like `"Agent cleanup:"` so parallel agents don’t overwrite each other’s trail).
- **Before ending or when pausing:** Agent calls `save_progress(summary, next_steps, completed)` so the next turn or another agent has a canonical “here is where we are; do this next.”
- **New conversation / new agent:** Reads `read_progress()` first, then continues from `next_steps` without the user re-explaining or pasting context.

### Parallel agents

- **One canonical progress:** Use `save_progress` for the main handoff (“current summary + next steps”). The last agent to finish updates it; the next reader resumes from that.
- **Per-agent trail:** Use `append_note(section="progress", content="Agent X: did A; next B.")` so multiple agents leave a log. Others can `read_notes(section="progress")` to see who did what and avoid duplicate work.
- **Beliefs:** Use `update_belief` when an agent discovers something that should change shared assumptions (likelihood/evidence); others see it via `read_beliefs`.

### Native (no MCP)

Keep a file e.g. `.cursor/context/progress.json` with `{ "last_summary": "", "next_steps": [], "completed": [], "updated_at": "" }`. Rule: “At conversation start, read this file. Before ending, update it with a short summary and next steps.”

### Via MCP

Use the **cursor-notes** MCP tools: `read_progress`, `save_progress`, plus `read_notes` / `append_note` for coordination. No manual context trimming; the agent persists state and the next session loads it.

---

## 2. Roleplay system in Cursor

### Native method

- **Cursor Rules** (`.cursor/rules/*.mdc` or project rules): Define the AI’s role, tone, and constraints in prose. The model sees these every time.
- **Persistent “role + state” file**: Keep a file (e.g. `.cursor/context/role_and_state.md`) that the AI is told to read at the start of a conversation and update when the “situation” or “discoveries” change. Example:

```markdown
# Current role and focus
- **Persona**: Senior engineer, concise, evidence-based.
- **Current focus**: Refactoring auth module; prefer minimal breaking changes.
- **Last discovery**: Legacy API still used by mobile; don’t remove until we have a replacement.
```

Rule text you can add: *“At the start of each conversation, read `.cursor/context/role_and_state.md` (if it exists) for current role and focus. When you make important discoveries or change focus, update that file.”*

### Via MCP

- You already have **AgentPersona** in `.mcp.json`. If that MCP exposes a “current persona” or “role” to the model, that’s the MCP-based roleplay path.
- A **custom MCP** can expose a tool like `get_current_role()` that returns the same kind of content from a file or DB; Cursor (Composer) can call it when needed.

---

## 3. AI saving context / notes for itself

### Native method

- **Single notes file** the AI is allowed to read and write (e.g. `.cursor/context/notes.md` or `ledger/ai_notes.json`).
- **Cursor Rule**: Tell the AI to (1) read this file when starting a task or when context is unclear, (2) append or update it when it learns something important (e.g. “user prefers X”, “Y is deprecated”, “Z is the source of truth”).
- **Format**: Markdown or JSON; keep one “notes” store so the AI doesn’t scatter state.

### Via MCP

- **MCP tools**: `read_notes`, `append_note`, `update_note` (and optionally `update_belief` for BDH-style). The MCP server persists to a file (e.g. same path as above). Composer will call these when the model decides it needs to remember or recall something.
- **Advantage**: Clear boundaries (only these tools touch the notes), and the model can be prompted to “use the notes tools to remember this” or “check notes before answering.”

---

## 4. BDH-style: dynamic, reactive context with likelihood and evidence

**BDH** here means: notes that are **dynamic and reactive to changes and discoveries**, with **percentages of likelihood** and **evidence/logic** (so the AI can reason about confidence and update over time).

### Schema (for notes or MCP store)

Use a single store (file or backend of an MCP server) with entries that look like this:

```json
{
  "beliefs": [
    {
      "id": "auth-migration",
      "statement": "Legacy auth will be replaced by OAuth in Q2.",
      "likelihood_percent": 75,
      "evidence": ["ADR-004", "sprint planning notes"],
      "logic": "Product committed; timeline from PM.",
      "updated_at": "2025-02-18T12:00:00Z"
    },
    {
      "id": "mobile-api",
      "statement": "Mobile still uses /v1/profile.",
      "likelihood_percent": 95,
      "evidence": ["grep in mobile repo", "runbook"],
      "logic": "Verified in code and docs.",
      "updated_at": "2025-02-18T11:00:00Z"
    }
  ],
  "notes": [
    {
      "id": "n1",
      "content": "User prefers minimal diffs and separate PRs per concern.",
      "updated_at": "2025-02-18T10:00:00Z"
    }
  ],
  "role": {
    "persona": "Senior engineer, concise, evidence-based.",
    "current_focus": "Refactoring auth; avoid breaking mobile until replacement exists."
  }
}
```

- **beliefs**: High-value context with `likelihood_percent`, `evidence`, and `logic`. The AI (or a script) can update these as new evidence appears.
- **notes**: Free-form context (preferences, discoveries) without a likelihood.
- **role**: Current persona and focus; can be updated by the AI or by you.

### Using BDH in Cursor

- **Native**: Put this JSON in e.g. `.cursor/context/notes.json`. Rule: “Read `.cursor/context/notes.json` when you need project context or beliefs. When you get new evidence or change your confidence, update the file (edit the relevant belief or add a note).”
- **MCP**: Implement tools that read/write this structure:
  - `read_notes` / `read_beliefs`: return full or filtered notes/beliefs.
  - `append_note(content)`.
  - `update_belief(id, statement?, likelihood_percent?, evidence?, logic?)` so the model can make context “reactive” to discoveries.

You can still run **workflow-canvas BDH (Batch Dynamic Ingestion)** separately for RAG; this “beliefs + likelihood” store is a separate, Cursor-facing context layer that can later feed into RAG if you want.

---

## 5. Implementing in Cursor

### Option A: Native only (no new dependencies)

1. Create `.cursor/context/notes.json` (or `role_and_state.md` + `notes.json`) with the schema above (or a subset).
2. Add a **Cursor Rule** that:
   - Defines the AI’s default role (roleplay).
   - Tells the AI to read `.cursor/context/notes.json` (and role file if separate) when starting or when context is unclear.
   - Tells the AI to update that file when it learns something important or changes a belief (with likelihood/evidence when relevant).
3. No MCP required; works in normal chat and Composer as long as the AI can read/write those files.

### Option B: MCP for notes and beliefs

1. Run the **notes MCP server** (see below) so it exposes `read_notes`, `append_note`, `read_beliefs`, `update_belief`, and optionally `get_role` / `set_role`.
2. In **Cursor → Settings → MCP**, add the server (stdio command pointing at the Python script).
3. In **Composer**, the model will see these tools and can read/update notes and beliefs; you can prompt: “Before answering, check notes; after discovering something important, update beliefs with likelihood and evidence.”

### Option C: Combine both

- **Roleplay**: Rule + optional `role` in the same JSON (or AgentPersona MCP if you prefer).
- **Persistence**: MCP tools for structured notes/beliefs; rule tells the AI to use them.
- **BDH-style**: Same JSON schema and `update_belief` so context stays dynamic and evidence-based.

---

## 6. MCP notes server (in this repo)

A small **notes + beliefs** MCP server is provided so Cursor can use persistent notes and BDH-style beliefs via tools.

- **Location**: `blackwall/mcp/notes_mcp_server.py`
- **Data file**: `.cursor/context/notes.json` (created automatically)
- **Tools** (for Composer):
  - **Progress (resume without reprompting):** `read_progress` – get last summary, next steps, completed; `save_progress` – write summary, next_steps, completed so the next agent/session can resume.
  - **Notes (parallel agents / shared context):** `read_notes` – return all notes or filter by section; `append_note` – add a note (section, content).
  - **Beliefs (BDH-style):** `read_beliefs` – return beliefs (optional min likelihood); `update_belief` – add or update a belief (id, statement, likelihood_percent, evidence, logic).
  - **Roleplay:** `get_role`, `set_role` – persona and current focus.

**Setup:** Install the MCP SDK once: `pip install mcp`

**Cursor MCP config** (in `.mcp.json` or Cursor Settings → MCP):

```json
{
  "mcpServers": {
    "cursor-notes": {
      "command": "python",
      "args": ["-m", "blackwall.mcp.notes_mcp_server"],
      "env": {
        "CURSOR_NOTES_PATH": ".cursor/context/notes.json"
      }
    }
  }
}
```

If the project is not installed as a package, run the script directly (from repo root):

```json
"command": "python",
"args": ["blackwall/mcp/notes_mcp_server.py"],
"env": { "CURSOR_NOTES_PATH": ".cursor/context/notes.json" }
```

---

**Suggested rule for Composer:** “When you start a task, call `read_progress` and optionally `read_notes(section='progress')` to see existing state. When you pause or finish, call `save_progress` with a short summary and the next steps so the next turn or another agent can continue without the user reprompting.”

---

## 7. References

- **Cursor MCP**: [Cursor MCP docs](https://docs.cursor.com/context/mcp)
- **Persistent memory (community)**: [MCP Add Persistent Memory in Cursor](https://forum.cursor.com/t/mcp-add-persistent-memory-in-cursor/57497)
- **This repo**: `agent-system/scratchpad.py` (shared agent notes), `workflow-canvas` BDH (RAG ingestion), `assistant/manifest.yaml` (MCP boundary)

The notes/beliefs store and MCP server are separate from the existing scratchpad and ledger; you can later wire them (e.g. have the MCP server write into the same ledger or trigger BDH ingestion) if you want one unified context pipeline.

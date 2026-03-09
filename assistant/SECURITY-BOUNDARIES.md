# Security Boundaries — Per-Orchestrator

The personal assistant is defined by `manifest.yaml`. Each orchestrator has a **boundary**: what it may and may not do. Consistency is enforced by: (1) pipeline order, (2) no secrets in manifest, (3) audit sink.

---

## prompt_injection_gate

- **Input**: Raw user message.
- **Output**: Either `passed_text` (sanitized or unchanged) or `block_message` (no call to downstream).
- **Allowed**: Scan, block, sanitize. No storage of user secrets or credentials.
- **Handoff**: Only `passed_text` goes to MCP / workflow_canvas; blocked requests never reach them.

---

## mcp

- **Allowed tools**: Only those listed in manifest `boundary.allowed_tools`. No dynamic tool injection from user input.
- **Secrets**: Never in manifest. API keys / tokens via env or Cursor/MCP config outside this repo.
- **Handoff**: Results can feed workflow_canvas or subagents per pipeline.

---

## workflow_canvas

- **Allowed blocks**: Only block types in manifest `boundary.allowed_blocks`. No arbitrary code execution blocks from untrusted workflow JSON.
- **Secrets**: No raw API keys or passwords in workflow JSON; use env or vault references.
- **Handoff**: Output can feed subagents.

---

## subagents

- **Allowed agents**: Only cleanup, test, doc (or list in manifest). Ledger path fixed; no user-controlled paths.
- **Boundary**: Subagents use agent-system ledger and scratchpad only; no direct file system access outside declared resources.
- **Handoff**: None (terminal in pipeline).

---

## overseer_contract

- **Allowed actions**: Append to log and scratchpad only. No file write outside `.overseer`.
- **Goal**: From env `OVERSEE_GOAL` only; not from user message.
- **Handoff**: None.

---

## Consistency Rules (Global)

1. **Pipeline order**: User input passes through orchestrators in `manifest.yaml` `consistency.pipeline_order`. No skipping the input filter.
2. **Secrets**: Never in `manifest.yaml`. Use environment variables or a vault; reference by name only in manifest (e.g. `goal_from_env: "OVERSEE_GOAL"`).
3. **Audit**: Any orchestrator that modifies state must write to `consistency.audit_sink` (e.g. append-only log). Single sink for review.
4. **Single definition**: `manifest.yaml` is the only source of truth for orchestrator set, boundaries, and pipeline. Other configs (MCP, workflow JSON, .claude/agents) must stay consistent with this manifest by convention or tooling.

# Blackwall Agents — Detection, Protection, MCP-Aware

**Blackwall agents** live in `blackwall/agents/`: they perform detection, protection, and tool use via [[MCP-Integration]]. They are separate from the Claude **[[Subagents]]** in `agent-system/`. See [[Core-Protection]] for text/image processing and [[Autonomous-System]] for autonomous variants.

---

## Location

- **Path**: `blackwall/agents/`
- **Files**: `detection_agent.py`, `protection_agent.py`, `mcp_aware_agent.py`

---

## Hierarchy

```
MCPAwareAgent (base)
    ├── DetectionAgent   — detect watermarks in text/image
    └── ProtectionAgent — protect (watermark/poison) text/image
```

`MCPAwareAgent` provides tool awareness; Detection and Protection use [[Core-Protection]] (UnifiedProcessor, registry).

---

## MCP-Aware Agent (`mcp_aware_agent.py`)

Base for Blackwall agents that use MCP tools.

- **MCP**: Uses `blackwall/mcp/mcp_integration.MCPIntegration` for `list_tools()`, `get_tool_schema()`, `list_resources()`.
- **Tools** (typical): read_file, write_file, search_replace, codebase_search, grep, run_terminal_cmd, read_lints, list_dir, glob_file_search, delete_file.
- **Optional base**: If `agent-system` is on path, can wrap `BaseAgent` for ledger/scratchpad; otherwise works standalone.
- **Methods**: `use_tool(name, **kwargs)` (delegates to MCP), agent state and metadata.

---

## Detection Agent (`detection_agent.py`)

**Role**: Detect watermarks in text and images using [[Core-Protection]] and registry.

- **Extends**: `MCPAwareAgent` (agent_type=`"detection"`).
- **Dependencies**: `UnifiedProcessor`, `BlackwallRegistry`.
- **Capabilities**: detect_text, detect_image, scan_directory.

**Methods**:
- `detect_watermark(content_path, content_type="auto")` — auto-detect type, run detection, optionally lookup UUID in registry; returns result dict (e.g. `detected`, `uuid`, `registry_match`).
- `scan_directory(directory, content_type="auto")` — scan dir for text/image files, run detection on each, return list of results where `detected` is true.

---

## Protection Agent (`protection_agent.py`)

**Role**: Protect content (text and images) with watermarking/poisoning via [[Core-Protection]].

- **Extends**: `MCPAwareAgent` (agent_type=`"protection"`).
- **Dependencies**: `UnifiedProcessor`, `BlackwallRegistry`.
- **Capabilities**: protect_text, protect_image, poison, watermark.

**Methods**:
- `protect_content(content_path, content_type="auto")` — declare intent, read file (MCP or direct), run `UnifiedProcessor.process_text` / image path, write protected output, register in registry; returns protection result.

---

## Relation to Other Systems

- **Agent-system**: Optional; if present, MCP-aware agent can use [[Agent-System]] ledger and scratchpad via `BaseAgent`.
- **Autonomous**: [[Autonomous-System]] has `AutonomousProtectionAgent` that also uses UnifiedProcessor and registry but operates independently.
- **MCP**: All tool use goes through [[MCP-Integration]].

---

## Related

- [[MCP-Integration]] — Tools and resources used by these agents.
- [[Core-Protection]] — UnifiedProcessor, text/image poisoning and watermarking.
- [[Subagents]] — Claude subagents (cleanup, test, doc, etc.) in agent-system.
- [[Autonomous-System]] — Orchestrator and autonomous protection agent.

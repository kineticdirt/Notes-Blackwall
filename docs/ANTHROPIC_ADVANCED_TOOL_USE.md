# Anthropic Advanced Tool Use — Summary & Application

Concise summary and application notes from [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use) (Nov 24, 2025). Use this to decide when and how to adopt the three beta features with Claude and MCP in this repo.

---

## 1. The three features

| Feature | What it does | Main benefit |
|--------|----------------|---------------|
| **Tool Search Tool** | Discover tools on-demand instead of loading all definitions upfront | ~85% token reduction; better tool selection (e.g. Opus 4.5: 79.5% → 88.1% on MCP evals) |
| **Programmatic Tool Calling** | Claude invokes tools from **code execution** (orchestration in Python); intermediate results stay out of context | ~37% token reduction on complex tasks; fewer inference round-trips; more accurate multi-step workflows |
| **Tool Use Examples** | Attach `input_examples` to tool definitions so Claude sees real usage patterns, not just JSON schema | Fewer malformed calls; internal testing: 72% → 90% on complex parameter handling |

---

## 2. When to use each

### Tool Search Tool

**Use when:** Tool definitions >10K tokens; tool selection errors; multiple MCP servers; 10+ tools.  
**Less useful when:** &lt;10 tools; every tool used every session; definitions already small.

**Mechanism:** Mark tools with `defer_loading: true`. Claude only sees the Tool Search Tool (~500 tokens) plus non-deferred tools. When it needs a capability, it searches; matching tools are expanded into context (e.g. 3–5 tools, ~3K tokens). Prompt caching still works because deferred tools aren’t in the initial prompt.

### Programmatic Tool Calling

**Use when:** Large datasets where you need only aggregates/summaries; 3+ dependent tool calls; filtering/sorting/transforming results before Claude sees them; parallel operations (e.g. many endpoints).  
**Less useful when:** Single simple tool call; Claude should reason over every intermediate result.

**Mechanism:** Add `code_execution` and set `allowed_callers: ["code_execution_20250825"]` on tools. Claude emits a `server_tool_use` for `code_execution` with Python that calls your tools. Tool results go to the code execution environment, not to Claude’s context; only the code’s final output (e.g. `stdout`) is returned to the model.

### Tool Use Examples

**Use when:** Complex nested params; many optional params with non-obvious patterns; domain conventions not in schema; similar tool names (e.g. `create_ticket` vs `create_incident`).  
**Less useful when:** Simple single-parameter tools; standard formats Claude already knows.

**Mechanism:** Add `input_examples` (array of example `input` objects) to the tool definition. Claude learns formats (e.g. dates, IDs), when to fill nested fields, and correlations (e.g. critical → full contact + escalation).

---

## 3. Implementation snippets (from Anthropic)

### Tool Search Tool

```json
{
  "tools": [
    {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
    {
      "name": "github.createPullRequest",
      "description": "Create a pull request",
      "input_schema": {...},
      "defer_loading": true
    }
  ]
}
```

For MCP servers: defer the whole server but keep a few tools loaded:

```json
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-drive",
  "default_config": {"defer_loading": true},
  "configs": {
    "search_files": {"defer_loading": false}
  }
}
```

### Programmatic Tool Calling

Opt-in tools:

```json
{
  "name": "get_team_members",
  "description": "Get all members of a department...",
  "input_schema": {...},
  "allowed_callers": ["code_execution_20250825"]
}
```

Tool requests from code include `caller`; you return results to the API; they’re fed into the code execution environment. Only the final `code_execution_tool_result` (e.g. stdout) goes to Claude.

### Tool Use Examples

```json
{
  "name": "create_ticket",
  "input_schema": {...},
  "input_examples": [
    {
      "title": "Login page returns 500 error",
      "priority": "critical",
      "labels": ["bug", "authentication", "production"],
      "reporter": {"id": "USR-12345", "name": "Jane Smith", "contact": {"email": "jane@acme.com"}},
      "due_date": "2024-11-06",
      "escalation": {"level": 2, "notify_manager": true, "sla_hours": 4}
    },
    { "title": "Add dark mode support", "labels": ["feature-request", "ui"] }
  ]
}
```

---

## 4. Best practices (from the post)

- **Layer by bottleneck:** Context from tool definitions → Tool Search; large intermediate results → Programmatic Tool Calling; parameter errors → Tool Use Examples.
- **Tool Search:** Clear names and descriptions (good: `search_customer_orders` + “Search for customer orders by date range, status…”); system prompt hint (“Use the tool search to find specific capabilities”); keep 3–5 high-use tools loaded, defer the rest.
- **Programmatic Tool Calling:** Document return formats in tool descriptions so Claude can write correct parsing code; prefer parallel-safe, idempotent tools for orchestration.
- **Tool Use Examples:** Realistic data; 1–5 examples per tool; minimal, partial, and full specs; only where schema is ambiguous.

---

## 5. Enabling on the API (beta)

```python
client.beta.messages.create(
    betas=["advanced-tool-use-2025-11-20"],
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=[
        {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
        {"type": "code_execution_20250825", "name": "code_execution"},
        # Your tools with defer_loading, allowed_callers, input_examples
    ]
)
```

See [Anthropic advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) for full API docs and cookbooks.

---

## 6. Application to this repo

| Piece | How advanced tool use applies |
|-------|-------------------------------|
| **Cursor + MCP (notes server)** | If you add many MCP servers (filesystem, Brave Search, custom tools), Tool Search + `defer_loading` on MCP toolsets keeps context small. Tool Use Examples on `read_progress` / `save_progress` / `update_belief` can clarify sections and list formats. |
| **Workflow-canvas** | Workflows that chain many MCP or HTTP tools could be expressed as Programmatic Tool Calling in a future Claude-backed node (orchestrate in code, return only summary to the model). |
| **Adversarial arena** | Defender/attacker tools could be defined with examples (e.g. payload shape, round_id) and, at scale, discovered via a search tool instead of loading every tool upfront. |
| **Manifest / pipeline** | Advanced tool use is a **client/platform** feature (Claude API + MCP). Your manifest and pipeline stay unchanged; adoption is in how you configure tools when calling Claude (e.g. via Cursor or your own API integration). |

---

*Source: [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use), Anthropic Engineering, Nov 24, 2025. Beta features; check Anthropic docs for current availability and API shape.*

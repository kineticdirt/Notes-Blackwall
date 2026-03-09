# MCP Integration — Framework, Servers, Tools, Resources

**MCP (Model Context Protocol)** integration in Blackwall provides reusable servers with tools, prompts, and resource access. [[Blackwall-Agents]] use MCP for tool calls; workflow-canvas and Cursor can connect to MCP servers. See [[Architecture-Overview]] for placement.

---

## Location

- **Path**: `blackwall/mcp/`
- **Key files**: `server_framework.py`, `server_builder.py`, `mcp_integration.py`, `agent_integration.py`, `cloud_agents_integration.py`

---

## Server Framework (`server_framework.py`)

- **ResourceAccess**: Enum for read_only, read_write, full, none.
- **MCPResource**: uri, name, description, mime_type, access_level, metadata.
- **MCPToolDefinition**: name, description, parameters (inputSchema), resource_access, access_level, handler, server_id; `to_mcp_schema()`.
- **MCPPromptTemplate**: name, description, template, resource_access, access_level, variables; `render(context, resources)`.
- **BackendConnection**: Abstract base for backend connect/disconnect/execute/is_connected.
- **MCPServer**: Registers tools, prompts, resources; `register_tool()`, `register_prompt()`, `load_resources()`, `render_prompt()`, `get_tool_schemas()`, `get_prompt_schemas()`.
- **ServerRegistry**: Holds multiple servers; `register_server()`, `render_prompt(server_id, prompt_name, context)`; `discover_prompts()`.

---

## Server Builder (`server_builder.py`)

- **MCPServerBuilder**: Fluent API to build servers: `add_tool()`, `add_prompt()`, `add_resource()`, `set_backend()`, `build()`.
- **Config**: Load from YAML/JSON (tools, prompts, resources, backend).
- **Export**: `to_config()` for tools, prompts, resources.

---

## MCP Integration (`mcp_integration.py`)

- **MCPIntegration**: Lists tools, get tool schema, list resources; bridge to actual MCP runtime (e.g. Cursor MCP clients).
- Used by [[Blackwall-Agents]] (MCPAwareAgent) for `list_tools()`, `get_tool_schema()`, `list_resources()`.

---

## Agent Integration (`agent_integration.py`)

- **AgentIntegrationBridge**: Discovers tools and prompts across servers; `get_available_tools()`, `get_available_prompts()`, `call_tool()`, `render_prompt()`.
- **AgentContext**: Full context (tools, prompts, resources) for agents.

---

## Cloud Agents Integration (`cloud_agents_integration.py`)

- Integration with Claude Cloud Agents / external agent APIs.
- Tools and prompts exposed for cloud agent workflows.

---

## Related

- [[Blackwall-Agents]] — Detection and protection agents use MCP tools.
- [[Workflow-Canvas]] — Workflow backend can call MCP tools (e.g. mcp_tool block).
- [[index]] — Compendium index.

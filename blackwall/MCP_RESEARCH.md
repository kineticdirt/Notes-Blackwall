# MCP (Model Context Protocol) Research

## What is MCP?

**Model Context Protocol (MCP)** is Anthropic's protocol for connecting AI models to external tools and data sources. It's the foundation for how Claude accesses tools and resources.

## Key Concepts

### Tools
Tools are functions that Claude can call. In Blackwall, these include:
- `read_file` - Read file contents
- `write_file` - Write to files
- `codebase_search` - Semantic code search
- `grep` - Pattern matching
- `run_terminal_cmd` - Execute commands
- `read_lints` - Get linter errors

### Resources
Resources are data that can be accessed:
- Ledger (AI_GROUPCHAT.json)
- Scratchpad
- Registry
- File system

### Servers
MCP servers expose tools and resources. Blackwall can be an MCP server.

## How MCP Works

1. **Server Registration**: MCP server registers with Claude
2. **Tool Discovery**: Claude discovers available tools
3. **Tool Execution**: Claude calls tools when needed
4. **Resource Access**: Claude accesses resources via URIs

## MCP in Blackwall

Blackwall's tools ARE MCP tools:
- All the tools available in this environment are part of Blackwall
- Agents use these tools via MCP protocol
- Resources (ledger, scratchpad) are MCP resources

## Integration Strategy

1. **Tool Awareness**: Agents know what MCP tools are available
2. **Resource Access**: Agents access MCP resources (ledger, scratchpad)
3. **Server Capability**: Blackwall can act as MCP server
4. **Protocol Compliance**: Follow MCP specifications

## References

- MCP is Anthropic's protocol for tool integration
- Tools are exposed via MCP servers
- Resources are accessed via MCP resource URIs
- Blackwall integrates with MCP to provide tools and resources

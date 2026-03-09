# Workflow Canvas — Visual Workflow, AI Gateway, Blocks

**Workflow-canvas** is a visual workflow editor with blocks, execution, AI gateway, and optional MCP and n8n export. It can be wired to [[Prompt-Injection]] for user input before the main AI. See [[MCP-Integration]] for MCP tools used by blocks.

---

## Location

- **Path**: `workflow-canvas/`
- **Backend**: `backend/` (api, blocks, workflow_engine, ai_gateway, execution_scheduler, mcp_integration, n8n_converter, rag_graph, streaming)
- **Frontend**: `frontend/` (index.html, app.js, blocks.js, canvas.js, workflow.js, streaming.js, styles.css)

---

## Components

### Backend

- **api.py**: REST API for workflows, nodes, execution.
- **blocks.py**: Block definitions and execution; block types include input_http, output_http, mcp_tool, mcp_chain, prompt_llm, prompt_template, prompt_chain, resource_*, transform_*, control_*, restriction_*, output_console.
- **workflow_engine.py**: Workflow execution and node lifecycle.
- **execution_scheduler.py**: Scheduling and run management.
- **ai_gateway.py**: AI Gateway for chat; builds system/user prompts, calls AI (rule-based or Anthropic/OpenAI); can be extended to use [[Prompt-Injection]] gate before calling AI.
- **mcp_integration.py**: MCP tool invocation for mcp_tool / mcp_chain blocks.
- **n8n_converter.py**: Export workflows to n8n format.
- **rag_graph.py**: RAG graph and search blocks.
- **streaming.py**: Streaming responses.

### Frontend

- **index.html**, **app.js**: App shell and routing.
- **blocks.js**: Block palette and definitions.
- **canvas.js**: Canvas and node placement.
- **workflow.js**: Workflow state and persistence.
- **streaming.js**: Streaming UI.
- **styles.css**: Styling.

---

## AI Gateway

- **AIGateway**: Provider (anthropic, openai, local), API key from env; `process_command(command, context)` → response with action and message.
- **Prompts**: System prompt describes workflow blocks and actions; user prompt includes command and context.
- **Calls**: Rule-based fallback or `call_claude_api(messages)` / OpenAI; returns parsed action (add_node, clear_canvas, connect, save_workflow, execute_workflow, list_nodes, etc.).
- **Integration with Prompt Injection**: Before building prompts or calling AI, run user command through [[Prompt-Injection]] SacrificialGate; if blocked, return block message; otherwise use passed_text as command.

---

## Block Categories

- **Tools**: input_http, output_http, mcp_tool, mcp_chain.
- **Prompts**: prompt_llm, prompt_template, prompt_chain.
- **Resources**: resource_data, rag_ingest, rag_search, resource_file, resource_database, etc.
- **Transform**: transform_json, transform_text.
- **Control**: control_if, control_loop.
- **Restrictions**: restriction_rate_limit, restriction_access_control, restriction_validation, etc.
- **Output**: output_console.

---

## Related

- [[Prompt-Injection]] — Gate user input before AI gateway.
- [[MCP-Integration]] — MCP tools for mcp_tool / mcp_chain blocks.
- [[index]] — Compendium index.

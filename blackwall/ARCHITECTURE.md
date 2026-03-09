# Blackwall Architecture: Unified System

## Why Blackwall is Separate (Current Design)

Blackwall was created as a separate folder because:
1. **Different Purpose**: Blackwall extends Nightshade for text + images
2. **Different Dependencies**: Text processing requires transformers, NLP models
3. **Modularity**: Can be used independently or integrated

## Proposed Unified Architecture

Blackwall should be the **unified system** that includes:
- Agent system (coordination, subagents)
- Nightshade tracker (image protection)
- Text protection (new)
- MCP integration (tools and resources)

## Unified Structure

```
blackwall/
├── agents/              # Agent system (from agent-system/)
│   ├── coordinator.py
│   ├── ledger.py
│   ├── scratchpad.py
│   └── specialized/
│       ├── cleanup_agent.py
│       ├── test_agent.py
│       └── doc_agent.py
├── protection/          # Protection modules
│   ├── image/          # From nightshade-tracker
│   │   ├── poisoning.py
│   │   └── watermarking.py
│   └── text/           # New text protection
│       ├── poisoning.py
│       └── watermarking.py
├── mcp/                # MCP integration
│   ├── servers/
│   └── tools/
├── database/
│   └── registry.py
└── cli.py
```

## Integration Plan

1. Move agent-system into blackwall/agents/
2. Move nightshade-tracker into blackwall/protection/image/
3. Keep text protection in blackwall/protection/text/
4. Add MCP integration in blackwall/mcp/
5. Unified CLI and registry

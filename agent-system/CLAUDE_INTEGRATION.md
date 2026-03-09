# Claude Integration Guide

This guide explains how the agent system integrates with Claude Code's plugin and subagent systems.

## LSP (Language Server Protocol) Integration

The agent system automatically detects project languages and checks for LSP support.

### Automatic LSP Detection

The `LSPManager` class:
- Detects programming languages in your project
- Checks for required language server binaries
- Provides installation commands for Claude LSP plugins

### Supported Languages

Based on [Claude's official documentation](https://code.claude.com/docs/en/discover-plugins):

| Language | Plugin | Binary Required |
|----------|--------|----------------|
| Python | `pyright-lsp@claude-plugins-official` | `pyright-langserver` |
| TypeScript | `typescript-lsp@claude-plugins-official` | `typescript-language-server` |
| Rust | `rust-analyzer-lsp@claude-plugins-official` | `rust-analyzer` |
| Go | `gopls-lsp@claude-plugins-official` | `gopls` |
| Java | `jdtls-lsp@claude-plugins-official` | `jdtls` |
| C/C++ | `clangd-lsp@claude-plugins-official` | `clangd` |
| C# | `csharp-lsp@claude-plugins-official` | `csharp-ls` |
| Lua | `lua-lsp@claude-plugins-official` | `lua-language-server` |
| PHP | `php-lsp@claude-plugins-official` | `intelephense` |
| Swift | `swift-lsp@claude-plugins-official` | `sourcekit-lsp` |

### Installing LSP Plugins

1. **Install Language Server Binary** (if not already installed):
   ```bash
   # Python
   npm install -g pyright
   
   # TypeScript
   npm install -g typescript-language-server
   
   # Rust
   rustup component add rust-analyzer
   ```

2. **Install Claude Plugin** (in Claude Code):
   ```
   /plugin install pyright-lsp@claude-plugins-official
   /plugin install typescript-lsp@claude-plugins-official
   ```

### Using LSP Manager

```python
from lsp_manager import LSPManager

# Initialize
lsp_manager = LSPManager()

# Detect project languages
languages = lsp_manager.detect_project_languages(".")

# Get required LSPs
required = lsp_manager.get_required_lsps(languages)

# Get installation commands
commands = lsp_manager.get_installation_commands(languages)
for cmd in commands:
    print(cmd)  # /plugin install ...
```

## Subagent Integration

The agent system uses Claude's subagent system for specialized agents.

### Subagent Configuration

Subagents are configured in `.claude/agents/` directory using Markdown files with YAML frontmatter.

### Available Subagents

1. **cleanup-agent** (`.claude/agents/cleanup-agent.md`)
   - Specialized for code cleanup and refactoring
   - Automatically invoked when cleanup is needed

2. **test-agent** (`.claude/agents/test-agent.md`)
   - Specialized for writing test cases
   - Automatically invoked when tests are needed

3. **doc-agent** (`.claude/agents/doc-agent.md`)
   - Specialized for documentation
   - Automatically invoked when documentation is needed

### Subagent Configuration Format

```markdown
---
name: agent-name
description: When this agent should be invoked
tools: tool1, tool2, tool3
model: sonnet
---

# Agent Description

Agent system prompt and instructions...
```

### Key Fields

- **name**: Unique identifier (lowercase with hyphens)
- **description**: Natural language description of when to invoke
- **tools**: Comma-separated list of tools (or inherit all)
- **model**: Model to use (sonnet, opus, haiku, or inherit)

### File Locations

- **Project Subagents**: `.claude/agents/` (project-specific, highest priority)
- **User Subagents**: `~/.claude/agents/` (available across all projects)

### Using Subagents

Subagents are automatically invoked by Claude Code based on:
- The task description
- The agent's description field
- Context and available tools

You can also invoke them explicitly:
```
/agents cleanup-agent
/agents test-agent
/agents doc-agent
```

## Enhanced Workflow Coordinator

The `EnhancedWorkflowCoordinator` integrates both systems:

```python
from enhanced_workflow_coordinator import EnhancedWorkflowCoordinator

# Initialize with LSP checking
coordinator = EnhancedWorkflowCoordinator(project_path=".")

# Get LSP report
report = coordinator.get_lsp_report()
print(f"Detected languages: {report['detected_languages']}")

# Generate setup guide
guide = coordinator.generate_lsp_setup_guide()
print(guide)

# Run workflow with LSP awareness
coordinator.run_workflow_with_lsp(".", ["file1.py", "file2.py"])
```

## Best Practices

1. **LSP Setup**: Always check LSP status before running workflows
2. **Subagent Configuration**: Keep descriptions clear and specific
3. **Tool Selection**: Only include necessary tools in subagent configs
4. **Model Selection**: Use `sonnet` for complex tasks, `haiku` for simple ones
5. **Coordination**: Use scratchpad and ledger for agent communication

## References

- [Claude Plugins Documentation](https://code.claude.com/docs/en/discover-plugins)
- [Claude Subagents Documentation](https://code.claude.com/docs/en/sub-agents)

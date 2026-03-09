# Claude Integration: LSP & Subagents

This system integrates with Claude Code's official plugin and subagent systems.

## Quick Setup

```bash
# Run setup script
python setup_claude_integration.py
```

This will:
1. Detect project languages
2. Check LSP binary availability
3. Generate installation commands
4. Verify subagent configuration

## LSP Integration

### Automatic Detection

The system automatically:
- Detects programming languages in your project
- Checks for required language server binaries
- Provides Claude plugin installation commands

### Installation Steps

1. **Install Language Server Binary**:
   ```bash
   # For Python
   npm install -g pyright
   
   # For TypeScript
   npm install -g typescript-language-server
   ```

2. **Install Claude Plugin** (in Claude Code):
   ```
   /plugin install pyright-lsp@claude-plugins-official
   ```

### Supported Languages

All languages from [Claude's official documentation](https://code.claude.com/docs/en/discover-plugins):
- Python: `pyright-lsp@claude-plugins-official`
- TypeScript: `typescript-lsp@claude-plugins-official`
- Rust: `rust-analyzer-lsp@claude-plugins-official`
- Go: `gopls-lsp@claude-plugins-official`
- Java: `jdtls-lsp@claude-plugins-official`
- C/C++: `clangd-lsp@claude-plugins-official`
- C#: `csharp-lsp@claude-plugins-official`
- Lua: `lua-lsp@claude-plugins-official`
- PHP: `php-lsp@claude-plugins-official`
- Swift: `swift-lsp@claude-plugins-official`

## Subagent Integration

### Configured Subagents

Three specialized subagents are configured in `.claude/agents/`:

1. **cleanup-agent.md** - Code cleanup and refactoring
2. **test-agent.md** - Test case writing
3. **doc-agent.md** - Documentation writing

### How Subagents Work

Based on [Claude's subagent documentation](https://code.claude.com/docs/en/sub-agents):

- **Automatic Invocation**: Claude Code automatically invokes subagents based on task descriptions
- **Project-Level**: Subagents in `.claude/agents/` are project-specific
- **Tool Access**: Each subagent has access to specific tools
- **Model Selection**: Uses `sonnet` for complex tasks

### Using Subagents

Subagents are automatically invoked, or you can invoke them explicitly:

```
/agents cleanup-agent
/agents test-agent
/agents doc-agent
```

## Enhanced Workflow

The `EnhancedWorkflowCoordinator` integrates everything:

```python
from enhanced_workflow_coordinator import EnhancedWorkflowCoordinator

# Initialize with LSP checking
coordinator = EnhancedWorkflowCoordinator(project_path=".")

# Get LSP status
report = coordinator.get_lsp_report()
print(report)

# Run workflow with LSP awareness
coordinator.run_workflow_with_lsp(".", ["file1.py"])
```

## Benefits

1. **Code Intelligence**: LSP provides jump-to-definition, find-references, type checking
2. **Specialized Agents**: Subagents handle specific tasks automatically
3. **Better Coordination**: Agents use LSP for code understanding
4. **Official Integration**: Uses Claude's official plugin system

## References

- [Claude Plugins Documentation](https://code.claude.com/docs/en/discover-plugins)
- [Claude Subagents Documentation](https://code.claude.com/docs/en/sub-agents)

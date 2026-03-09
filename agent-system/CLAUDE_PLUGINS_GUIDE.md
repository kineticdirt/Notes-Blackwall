# Claude Plugins Installation Guide

## Overview

This guide explains how to install official Claude plugins from the `claude-plugins-official` repository.

## Installation Command Format

The command format for installing plugins is:

```
/plugin install plugin-name@claude-plugins-official
```

## How to Install Plugins

### Method 1: Using Cursor/Claude Code Command

1. Open Cursor or Claude Code
2. In the chat/command interface, type:
   ```
   /plugin install plugin-name@claude-plugins-official
   ```
3. Replace `plugin-name` with the actual plugin name

### Method 2: Using the Plugin Marketplace

1. Open Cursor/Claude Code
2. Navigate to Settings → Plugins
3. Browse the official plugin marketplace
4. Click "Install" on desired plugins

## Official Plugin Registry

Run the discovery script to see available plugins:

```bash
python install_claude_plugins.py
```

This will:
- List currently installed plugins
- Create a registry of official plugins
- Generate installation commands

## Common Official Plugins

Based on typical Claude plugin ecosystems, common official plugins include:

1. **GitHub Plugin** - GitHub integration
   ```
   /plugin install github@claude-plugins-official
   ```

2. **Filesystem Plugin** - Enhanced file operations
   ```
   /plugin install filesystem@claude-plugins-official
   ```

3. **Web Search Plugin** - Web search capabilities
   ```
   /plugin install web-search@claude-plugins-official
   ```

4. **Database Plugin** - Database connectivity
   ```
   /plugin install database@claude-plugins-official
   ```

5. **API Client Plugin** - API utilities
   ```
   /plugin install api-client@claude-plugins-official
   ```

## Plugin Directory Structure

Plugins are installed to:
```
~/.claude/plugins/
```

Each plugin has its own directory with:
- `package.json` - Plugin manifest
- Plugin code and resources

## Discovering Available Plugins

To discover all available official plugins:

1. **Check Cursor Documentation**: Visit Cursor's plugin documentation
2. **Use Plugin Registry**: Run `install_claude_plugins.py` to generate a registry
3. **Browse Marketplace**: Use Cursor's built-in plugin marketplace UI

## Installation Script

The `install_claude_plugins.py` script provides:

- Plugin discovery
- Installation command generation
- Registry creation
- Status checking

Run it with:
```bash
python install_claude_plugins.py
```

## Troubleshooting

### Plugin Not Found

If a plugin isn't found:
1. Verify the plugin name is correct
2. Check if it's in the official repository
3. Ensure you're using the `@claude-plugins-official` suffix

### Installation Fails

1. Check Cursor/Claude Code version compatibility
2. Verify plugin permissions
3. Check plugin directory permissions: `~/.claude/plugins/`

### Finding Plugin Names

To find the exact plugin names:
1. Check Cursor's plugin marketplace
2. Review official documentation
3. Use the discovery script

## Notes

- Plugin installation must be done within Cursor/Claude Code, not from terminal
- The `/plugin install` command is a Cursor/Claude Code command, not a shell command
- Official plugins are maintained by the Claude/Cursor team
- Plugins may require specific Cursor/Claude Code versions

## Next Steps

1. Run `python install_claude_plugins.py` to discover plugins
2. Review the generated `claude_plugins_registry.json`
3. Install plugins using the `/plugin install` command in Cursor
4. Verify installation in `~/.claude/plugins/`

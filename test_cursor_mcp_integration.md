# Testing Cursor Cloud Agents MCP Integration

## Quick Test Checklist

After restarting Cursor, test the integration with these commands in Cursor Chat:

### 1. Check if MCP Server is Loaded
```
What MCP tools are available?
```

or

```
List all available tools from MCP servers
```

### 2. Test Cloud Agents Tools
```
List my Cloud Agents
```

Expected: Should show your Cloud Agents (may be empty if none created)

### 3. Test Agent Information
```
What Cloud Agents tools can I use?
```

Expected: Should list tools like:
- `launch_agent`
- `list_agents`
- `get_agent`
- `add_followup`
- `stop_agent`
- `delete_agent`
- `list_repositories`
- `list_models`

### 4. Test Repository Listing
```
List my GitHub repositories that Cloud Agents can access
```

### 5. Test Model Listing
```
What LLM models are available for Cloud Agents?
```

### 6. Test Agent Launch (if you have a repo)
```
Launch a Cloud Agent to analyze my codebase and suggest improvements
```

## Troubleshooting

### If MCP tools don't appear:

1. **Check Cursor Settings**
   - Open Settings (Cmd+,)
   - Search for "mcp"
   - Verify `cursor-cloud-agents` is listed under `mcpServers`

2. **Check Cursor Logs**
   - Open Developer Tools (Help → Toggle Developer Tools)
   - Check Console for MCP-related errors

3. **Verify API Key**
   - Run: `python3 test_mcp_connection.py`
   - Should show successful API connection

4. **Restart Cursor Again**
   - Sometimes MCP servers need a full restart to load

### If you see errors:

- **"Command not found"**: The npm package might need to be installed globally
  ```bash
  npm install -g @willpowell8/cursor-cloud-agent-mcp
  ```

- **"API Key invalid"**: Check your API key in settings.json

- **"Connection timeout"**: The MCP server might be starting slowly, wait a moment and try again

## Expected Behavior

When working correctly:
- Cursor Chat should recognize Cloud Agents commands
- You should be able to list, launch, and manage Cloud Agents
- The MCP server runs in the background via stdio
- All API calls go through the MCP protocol

## Next Steps After Testing

Once confirmed working:
1. Try launching your first Cloud Agent
2. Monitor agent status
3. Add follow-up instructions
4. Integrate with your workflow

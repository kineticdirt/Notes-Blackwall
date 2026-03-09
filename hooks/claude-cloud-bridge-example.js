/**
 * Example Hook: Claude Code to Cloud Agents Bridge
 * 
 * This hook intercepts prompts in Cursor and routes them to Cloud Agents
 * when certain conditions are met (e.g., prefix [CLOUD] or large tasks).
 * 
 * Setup:
 * 1. Place this file in your hooks directory
 * 2. Configure in Cursor settings:
 *    {
 *      "hooks": {
 *        "beforeSubmitPrompt": {
 *          "script": "/path/to/hooks/claude-cloud-bridge-example.js",
 *          "enabled": true
 *        }
 *      }
 *    }
 */

/**
 * Hook: beforeSubmitPrompt
 * Runs before the agent submits a prompt to the AI model
 * 
 * @param {Object} context - Prompt context
 * @param {string} context.prompt - The prompt text
 * @param {Object} context.metadata - Additional metadata
 * @returns {Object} Modified context
 */
export async function beforeSubmitPrompt(context) {
  const { prompt, metadata = {} } = context;
  
  // Check if prompt should be routed to Cloud Agent
  const shouldUseCloudAgent = checkIfShouldUseCloudAgent(prompt, metadata);
  
  if (shouldUseCloudAgent) {
    try {
      // Launch Cloud Agent via MCP
      const cloudAgentResult = await launchCloudAgent({
        prompt: cleanPrompt(prompt),
        repository: metadata.repository || getDefaultRepository(),
        autoCreatePr: metadata.autoCreatePr !== false,
        branch: metadata.branch
      });
      
      // Return modified context
      return {
        ...context,
        response: formatCloudAgentResponse(cloudAgentResult),
        executeLocally: false, // Don't execute locally, use Cloud Agent
        cloudAgentId: cloudAgentResult.id,
        cloudAgentUrl: `https://cursor.com/agents/${cloudAgentResult.id}`
      };
    } catch (error) {
      console.error('Failed to launch Cloud Agent:', error);
      // Fall back to local execution
      return {
        ...context,
        response: `Failed to launch Cloud Agent: ${error.message}. Executing locally instead.`
      };
    }
  }
  
  // Normal execution
  return context;
}

/**
 * Hook: beforeShellCommand
 * Runs before shell commands execute
 * 
 * Use this to log commands or block dangerous operations
 */
export async function beforeShellCommand(context) {
  const { command } = context;
  
  // Log all commands for observability
  logCommand(command);
  
  // Block dangerous commands (example)
  const dangerousCommands = ['rm -rf /', 'format c:', 'del /f /s /q'];
  if (dangerousCommands.some(cmd => command.includes(cmd))) {
    return {
      ...context,
      blocked: true,
      reason: 'Dangerous command detected'
    };
  }
  
  return context;
}

/**
 * Hook: afterToolCall
 * Runs after a tool is executed
 * 
 * Use this for logging, metrics, or triggering follow-up actions
 */
export async function afterToolCall(context) {
  const { toolName, result, error } = context;
  
  // Log tool usage
  logToolUsage(toolName, result, error);
  
  // If tool execution failed, optionally launch Cloud Agent
  if (error && shouldRetryWithCloudAgent(toolName, error)) {
    console.log(`Tool ${toolName} failed, considering Cloud Agent fallback`);
  }
  
  return context;
}

// Helper functions

function checkIfShouldUseCloudAgent(prompt, metadata) {
  // Route to Cloud Agent if:
  // 1. Prompt starts with [CLOUD]
  if (prompt.trim().startsWith('[CLOUD]')) {
    return true;
  }
  
  // 2. Prompt is very long (complex task)
  if (prompt.length > 2000) {
    return true;
  }
  
  // 3. Metadata explicitly requests Cloud Agent
  if (metadata.useCloudAgent === true) {
    return true;
  }
  
  // 4. Contains keywords indicating complex task
  const complexKeywords = [
    'refactor entire',
    'migrate',
    'rewrite',
    'implement full',
    'complete feature'
  ];
  if (complexKeywords.some(keyword => prompt.toLowerCase().includes(keyword))) {
    return true;
  }
  
  return false;
}

function cleanPrompt(prompt) {
  // Remove [CLOUD] prefix and clean up
  return prompt.replace(/^\[CLOUD\]\s*/i, '').trim();
}

async function launchCloudAgent(config) {
  // Connect to MCP server
  const mcpClient = await getMCPClient();
  
  // Prepare launch parameters
  const params = {
    prompt: {
      text: config.prompt
    },
    source: {
      repository: config.repository
    },
    target: {
      autoCreatePr: config.autoCreatePr !== false
    }
  };
  
  if (config.branch) {
    params.source.ref = config.branch;
  }
  
  if (config.model) {
    params.model = config.model;
  }
  
  // Launch agent via MCP
  const result = await mcpClient.callTool('launch_agent', params);
  
  return result;
}

async function getMCPClient() {
  // Initialize MCP client
  // This depends on your MCP client implementation
  // Example using stdio transport:
  
  const { spawn } = require('child_process');
  const mcp = require('@modelcontextprotocol/sdk');
  
  // Spawn MCP server process
  const serverProcess = spawn('npx', ['-y', '@willpowell8/cursor-cloud-agent-mcp']);
  
  // Create MCP client
  const client = new mcp.Client({
    name: 'claude-cloud-bridge',
    version: '1.0.0'
  }, {
    capabilities: {}
  });
  
  // Connect via stdio
  await client.connect({
    command: serverProcess,
    args: []
  });
  
  return client;
}

function formatCloudAgentResponse(result) {
  return `
🚀 Cloud Agent Launched Successfully!

Agent ID: ${result.id}
Status: ${result.status || 'CREATING'}

Monitor progress at: https://cursor.com/agents/${result.id}

The agent will:
- Analyze the repository
- Execute your instructions
- Create a pull request when complete

You can add follow-up instructions or check status using the Cloud Agents tools.
  `.trim();
}

function getDefaultRepository() {
  // Try to get from environment or git config
  const repo = process.env.GITHUB_REPOSITORY || 
                process.env.CLOUD_AGENT_DEFAULT_REPO;
  
  if (!repo) {
    throw new Error('No repository specified. Set GITHUB_REPOSITORY or CLOUD_AGENT_DEFAULT_REPO');
  }
  
  // Ensure full URL format
  if (!repo.startsWith('http')) {
    return `https://github.com/${repo}`;
  }
  
  return repo;
}

function logCommand(command) {
  // Log to file, database, or monitoring service
  console.log(`[HOOK] Command executed: ${command}`);
  // Example: send to logging service
  // logService.log('command', { command, timestamp: Date.now() });
}

function logToolUsage(toolName, result, error) {
  console.log(`[HOOK] Tool: ${toolName}`, {
    success: !error,
    error: error?.message
  });
}

function shouldRetryWithCloudAgent(toolName, error) {
  // Decide if failed tool should retry with Cloud Agent
  const retryableErrors = ['timeout', 'rate limit', 'connection'];
  return retryableErrors.some(err => 
    error.message.toLowerCase().includes(err)
  );
}

// Export all hooks
export default {
  beforeSubmitPrompt,
  beforeShellCommand,
  afterToolCall
};

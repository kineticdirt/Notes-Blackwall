/**
 * Custom error classes for the orchestration system
 */

export class OrchestrationError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly metadata?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'OrchestrationError';
    Error.captureStackTrace(this, this.constructor);
  }
}

export class RoundNotFoundError extends OrchestrationError {
  constructor(roundId: string) {
    super(`Round not found: ${roundId}`, 'ROUND_NOT_FOUND', { roundId });
    this.name = 'RoundNotFoundError';
  }
}

export class RoundAlreadyRunningError extends OrchestrationError {
  constructor(roundId: string) {
    super(`Round already running: ${roundId}`, 'ROUND_ALREADY_RUNNING', { roundId });
    this.name = 'RoundAlreadyRunningError';
  }
}

export class AgentNotFoundError extends OrchestrationError {
  constructor(agentId: string) {
    super(`Agent not found: ${agentId}`, 'AGENT_NOT_FOUND', { agentId });
    this.name = 'AgentNotFoundError';
  }
}

export class WorkspaceNotFoundError extends OrchestrationError {
  constructor(workspaceId: string) {
    super(`Workspace not found: ${workspaceId}`, 'WORKSPACE_NOT_FOUND', { workspaceId });
    this.name = 'WorkspaceNotFoundError';
  }
}

export class PluginLoadError extends OrchestrationError {
  constructor(pluginId: string, reason: string) {
    super(`Failed to load plugin ${pluginId}: ${reason}`, 'PLUGIN_LOAD_ERROR', {
      pluginId,
      reason,
    });
    this.name = 'PluginLoadError';
  }
}

export class RPCError extends OrchestrationError {
  constructor(
    message: string,
    public readonly rpcCode: number,
    metadata?: Record<string, unknown>
  ) {
    super(message, 'RPC_ERROR', metadata);
    this.name = 'RPCError';
  }
}

/**
 * Configuration loader with environment variable support
 */

import { z } from 'zod';

const ConfigSchema = z.object({
  // Server config
  socketPath: z.string().default('/tmp/worktree-orch-v2.sock'),
  dashboardPort: z.coerce.number().default(4000),
  dashboardHost: z.string().default('localhost'),

  // Workspace config
  workspaceBasePath: z.string().default('/tmp/worktree-workspaces'),
  maxWorkspaces: z.coerce.number().default(100),
  workspaceCleanupInterval: z.coerce.number().default(3600000), // 1 hour

  // Event bus config
  eventReplayBufferSize: z.coerce.number().default(1000),

  // Round config
  defaultRoundTimeout: z.coerce.number().default(300000), // 5 minutes
  defaultActionTimeout: z.coerce.number().default(30000), // 30 seconds

  // Plugin config
  pluginPath: z.string().default('./plugins'),
  enableHotReload: z.coerce.boolean().default(false),

  // Logging
  logLevel: z.enum(['trace', 'debug', 'info', 'warn', 'error', 'fatal']).default('info'),
});

export type Config = z.infer<typeof ConfigSchema>;

let cachedConfig: Config | null = null;

export function loadConfig(): Config {
  if (cachedConfig) {
    return cachedConfig;
  }

  const rawConfig = {
    socketPath: process.env.SOCKET_PATH,
    dashboardPort: process.env.DASHBOARD_PORT,
    dashboardHost: process.env.DASHBOARD_HOST,
    workspaceBasePath: process.env.WORKSPACE_BASE_PATH,
    maxWorkspaces: process.env.MAX_WORKSPACES,
    workspaceCleanupInterval: process.env.WORKSPACE_CLEANUP_INTERVAL,
    eventReplayBufferSize: process.env.EVENT_REPLAY_BUFFER_SIZE,
    defaultRoundTimeout: process.env.DEFAULT_ROUND_TIMEOUT,
    defaultActionTimeout: process.env.DEFAULT_ACTION_TIMEOUT,
    pluginPath: process.env.PLUGIN_PATH,
    enableHotReload: process.env.ENABLE_HOT_RELOAD,
    logLevel: process.env.LOG_LEVEL,
  };

  cachedConfig = ConfigSchema.parse(rawConfig);
  return cachedConfig;
}

export function getConfig(): Config {
  return cachedConfig || loadConfig();
}

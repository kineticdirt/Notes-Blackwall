/**
 * Core type definitions for the event-driven orchestration system
 */

import { z } from 'zod';

// ============================================================================
// Event System Types
// ============================================================================

export const EventTypeSchema = z.enum([
  // Round events
  'round.started',
  'round.completed',
  'round.failed',
  'round.scored',
  
  // Agent events
  'agent.registered',
  'agent.action.executed',
  'agent.action.failed',
  'agent.timeout',
  
  // Workspace events
  'workspace.created',
  'workspace.destroyed',
  'workspace.snapshot.created',
  'workspace.snapshot.restored',
  
  // Plugin events
  'plugin.loaded',
  'plugin.unloaded',
  'plugin.error',
  
  // System events
  'system.ready',
  'system.shutdown',
]);

export type EventType = z.infer<typeof EventTypeSchema>;

export interface BaseEvent {
  type: EventType;
  timestamp: number;
  id: string;
  metadata?: Record<string, unknown>;
}

export interface RoundStartedEvent extends BaseEvent {
  type: 'round.started';
  roundId: string;
  agents: string[];
  task: string;
  config: RoundConfig;
}

export interface RoundCompletedEvent extends BaseEvent {
  type: 'round.completed';
  roundId: string;
  duration: number;
  winner?: string;
}

export interface RoundScoredEvent extends BaseEvent {
  type: 'round.scored';
  roundId: string;
  scores: Record<string, Score>;
}

export interface AgentActionExecutedEvent extends BaseEvent {
  type: 'agent.action.executed';
  roundId: string;
  agentId: string;
  action: string;
  result: unknown;
  duration: number;
}

export interface WorkspaceCreatedEvent extends BaseEvent {
  type: 'workspace.created';
  workspaceId: string;
  path: string;
  agentId?: string;
  roundId?: string;
}

export interface PluginLoadedEvent extends BaseEvent {
  type: 'plugin.loaded';
  pluginId: string;
  version: string;
  path: string;
}

export type OrchestrationEvent =
  | RoundStartedEvent
  | RoundCompletedEvent
  | RoundScoredEvent
  | AgentActionExecutedEvent
  | WorkspaceCreatedEvent
  | PluginLoadedEvent
  | BaseEvent;

// ============================================================================
// Round System Types
// ============================================================================

export interface RoundConfig {
  id: string;
  task: string;
  agents: string[];
  timeout?: number; // milliseconds
  actionTimeout?: number; // milliseconds per action
  scoringStrategy?: string;
  metadata?: Record<string, unknown>;
}

export interface Score {
  value: number;
  breakdown: Record<string, number>;
  timestamp: number;
}

export interface RoundResult {
  roundId: string;
  status: 'completed' | 'failed' | 'timeout';
  scores: Record<string, Score>;
  duration: number;
  winner?: string;
  error?: string;
}

// ============================================================================
// Agent Types
// ============================================================================

export interface Agent {
  id: string;
  name: string;
  pluginId: string;
  config: Record<string, unknown>;
}

export interface AgentAction {
  id: string;
  agentId: string;
  type: string;
  params: Record<string, unknown>;
  timestamp: number;
}

export interface AgentActionResult {
  actionId: string;
  success: boolean;
  result?: unknown;
  error?: string;
  duration: number;
}

// ============================================================================
// Workspace Types
// ============================================================================

export interface WorkspaceConfig {
  id: string;
  basePath: string;
  agentId?: string;
  roundId?: string;
  env?: Record<string, string>;
  metadata?: Record<string, unknown>;
}

export interface WorkspaceSnapshot {
  id: string;
  workspaceId: string;
  path: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// Plugin Types
// ============================================================================

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description?: string;
  dependencies?: string[];
  events?: EventType[];
  rpcMethods?: string[];
}

export interface PluginContext {
  eventBus: EventBus;
  workspace: WorkspaceManager;
  logger: Logger;
  config: Record<string, unknown>;
}

export interface Plugin {
  manifest: PluginManifest;
  initialize(context: PluginContext): Promise<void>;
  shutdown(): Promise<void>;
  onEvent?(event: OrchestrationEvent): Promise<void>;
}

// ============================================================================
// Service Interfaces
// ============================================================================

export interface EventBus {
  emit(event: OrchestrationEvent): void;
  on<T extends OrchestrationEvent>(
    type: T['type'],
    handler: (event: T) => void | Promise<void>
  ): () => void; // Returns unsubscribe function
  once<T extends OrchestrationEvent>(
    type: T['type'],
    handler: (event: T) => void | Promise<void>
  ): void;
  off(type: EventType, handler: (event: OrchestrationEvent) => void): void;
}

export interface WorkspaceManager {
  create(config: WorkspaceConfig): Promise<string>; // Returns workspace path
  destroy(workspaceId: string): Promise<void>;
  snapshot(workspaceId: string): Promise<WorkspaceSnapshot>;
  restore(snapshotId: string, workspaceId: string): Promise<void>;
  getPath(workspaceId: string): string | null;
  list(): Promise<string[]>;
}

export interface Logger {
  debug(message: string, meta?: Record<string, unknown>): void;
  info(message: string, meta?: Record<string, unknown>): void;
  warn(message: string, meta?: Record<string, unknown>): void;
  error(message: string, error?: Error, meta?: Record<string, unknown>): void;
}

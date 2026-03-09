/**
 * Round Engine - Orchestrates competitive AI rounds
 * 
 * Manages the lifecycle of competitive rounds where multiple agents
 * compete to solve tasks. Handles timeouts, scoring, and result aggregation.
 */

import type {
  RoundConfig,
  RoundResult,
  Agent,
  AgentAction,
  AgentActionResult,
  Score,
  OrchestrationEvent,
} from './types.js';
import type { EventBus } from './types.js';
import { createLogger } from '../utils/logger.js';
import type { ScoringEngine } from '../scoring/engine.js';

const logger = createLogger('RoundEngine');

export class RoundEngine {
  private activeRounds = new Map<string, ActiveRound>();
  private agents = new Map<string, Agent>();
  private scoringEngine: ScoringEngine;

  constructor(
    private eventBus: EventBus,
    scoringEngine: ScoringEngine
  ) {
    this.scoringEngine = scoringEngine;
    this.setupEventHandlers();
  }

  /**
   * Register an agent for participation in rounds
   */
  registerAgent(agent: Agent): void {
    this.agents.set(agent.id, agent);
    
    this.eventBus.emit({
      type: 'agent.registered',
      id: `agent-reg-${Date.now()}`,
      timestamp: Date.now(),
      metadata: { agentId: agent.id },
    } as OrchestrationEvent);

    logger.info('Agent registered', { agentId: agent.id, name: agent.name });
  }

  /**
   * Start a new competitive round
   */
  async startRound(config: RoundConfig): Promise<string> {
    const roundId = config.id || `round-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

    // Validate agents exist
    for (const agentId of config.agents) {
      if (!this.agents.has(agentId)) {
        throw new Error(`Agent ${agentId} not registered`);
      }
    }

    const activeRound: ActiveRound = {
      id: roundId,
      config,
      startTime: Date.now(),
      agentActions: new Map(),
      agentResults: new Map(),
      status: 'running',
      timeouts: [],
    };

    // Set up timeout
    if (config.timeout) {
      const timeoutId = setTimeout(() => {
        this.handleRoundTimeout(roundId);
      }, config.timeout);
      activeRound.timeouts.push(timeoutId);
    }

    this.activeRounds.set(roundId, activeRound);

    // Emit round started event
    this.eventBus.emit({
      type: 'round.started',
      id: `round-started-${Date.now()}`,
      timestamp: Date.now(),
      roundId,
      agents: config.agents,
      task: config.task,
      config,
    } as OrchestrationEvent);

    logger.info('Round started', {
      roundId,
      agents: config.agents,
      task: config.task,
      timeout: config.timeout,
    });

    return roundId;
  }

  /**
   * Record an agent action execution
   */
  recordAction(action: AgentAction, result: AgentActionResult): void {
    const round = this.findRoundForAgent(action.agentId);
    if (!round) {
      logger.warn('Action recorded for unknown round', { agentId: action.agentId });
      return;
    }

    if (!round.agentActions.has(action.agentId)) {
      round.agentActions.set(action.agentId, []);
    }
    round.agentActions.get(action.agentId)!.push(action);

    round.agentResults.set(action.id, result);

    // Emit action executed event
    this.eventBus.emit({
      type: 'agent.action.executed',
      id: `action-${Date.now()}`,
      timestamp: Date.now(),
      roundId: round.id,
      agentId: action.agentId,
      action: action.type,
      result: result.result,
      duration: result.duration,
    } as OrchestrationEvent);

    logger.debug('Action recorded', {
      roundId: round.id,
      agentId: action.agentId,
      actionType: action.type,
      success: result.success,
    });
  }

  /**
   * Complete a round and calculate scores
   */
  async completeRound(roundId: string): Promise<RoundResult> {
    const round = this.activeRounds.get(roundId);
    if (!round) {
      throw new Error(`Round ${roundId} not found`);
    }

    if (round.status !== 'running') {
      throw new Error(`Round ${roundId} is not running (status: ${round.status})`);
    }

    // Clear timeouts
    for (const timeoutId of round.timeouts) {
      clearTimeout(timeoutId);
    }

    round.status = 'completed';
    const duration = Date.now() - round.startTime;

    // Calculate scores
    const scores = await this.scoringEngine.evaluateRound({
      roundId,
      agents: round.config.agents,
      actions: Object.fromEntries(round.agentActions),
      results: Object.fromEntries(round.agentResults),
      duration,
    });

    // Determine winner
    let winner: string | undefined;
    let maxScore = -Infinity;
    for (const [agentId, score] of Object.entries(scores)) {
      if (score.value > maxScore) {
        maxScore = score.value;
        winner = agentId;
      }
    }

    const result: RoundResult = {
      roundId,
      status: 'completed',
      scores,
      duration,
      winner,
    };

    // Emit scored event
    this.eventBus.emit({
      type: 'round.scored',
      id: `round-scored-${Date.now()}`,
      timestamp: Date.now(),
      roundId,
      scores,
    } as OrchestrationEvent);

    // Emit completed event
    this.eventBus.emit({
      type: 'round.completed',
      id: `round-completed-${Date.now()}`,
      timestamp: Date.now(),
      roundId,
      duration,
      winner,
    } as OrchestrationEvent);

    this.activeRounds.delete(roundId);

    logger.info('Round completed', {
      roundId,
      duration,
      winner,
      scores: Object.fromEntries(
        Object.entries(scores).map(([k, v]) => [k, v.value])
      ),
    });

    return result;
  }

  /**
   * Get round status
   */
  getRoundStatus(roundId: string): ActiveRound | null {
    return this.activeRounds.get(roundId) || null;
  }

  /**
   * List all active rounds
   */
  listActiveRounds(): string[] {
    return Array.from(this.activeRounds.keys());
  }

  /**
   * Find round for an agent (simplified - assumes agent in one round)
   */
  private findRoundForAgent(agentId: string): ActiveRound | null {
    for (const round of this.activeRounds.values()) {
      if (round.config.agents.includes(agentId)) {
        return round;
      }
    }
    return null;
  }

  /**
   * Handle round timeout
   */
  private async handleRoundTimeout(roundId: string): Promise<void> {
    const round = this.activeRounds.get(roundId);
    if (!round || round.status !== 'running') {
      return;
    }

    logger.warn('Round timeout', { roundId });

    // Complete round with timeout status
    round.status = 'timeout';
    const duration = Date.now() - round.startTime;

    // Calculate partial scores
    const scores = await this.scoringEngine.evaluateRound({
      roundId,
      agents: round.config.agents,
      actions: Object.fromEntries(round.agentActions),
      results: Object.fromEntries(round.agentResults),
      duration,
    });

    const result: RoundResult = {
      roundId,
      status: 'timeout',
      scores,
      duration,
    };

    this.eventBus.emit({
      type: 'round.completed',
      id: `round-timeout-${Date.now()}`,
      timestamp: Date.now(),
      roundId,
      duration,
    } as OrchestrationEvent);

    this.activeRounds.delete(roundId);

    logger.info('Round timed out', { roundId, duration });
  }

  /**
   * Setup event handlers
   */
  private setupEventHandlers(): void {
    // Could subscribe to events here if needed
  }
}

interface ActiveRound {
  id: string;
  config: RoundConfig;
  startTime: number;
  status: 'running' | 'completed' | 'timeout' | 'failed';
  agentActions: Map<string, AgentAction[]>;
  agentResults: Map<string, AgentActionResult>;
  timeouts: NodeJS.Timeout[];
}

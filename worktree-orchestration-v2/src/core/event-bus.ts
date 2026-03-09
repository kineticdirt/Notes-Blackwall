/**
 * Event Bus - RxJS-based reactive event system
 * 
 * Core of the event-driven architecture. All components communicate
 * through this centralized event bus using reactive streams.
 */

import { Subject, Observable, filter, map } from 'rxjs';
import type {
  EventBus,
  OrchestrationEvent,
  EventType,
} from './types.js';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('EventBus');

export class RxEventBus implements EventBus {
  private subject = new Subject<OrchestrationEvent>();
  private replayBuffer: OrchestrationEvent[] = [];
  private readonly maxReplaySize: number;

  constructor(maxReplaySize = 1000) {
    this.maxReplaySize = maxReplaySize;
    logger.info('Event bus initialized', { maxReplaySize });
  }

  /**
   * Emit an event to all subscribers
   */
  emit(event: OrchestrationEvent): void {
    // Add timestamp if not present
    if (!event.timestamp) {
      event.timestamp = Date.now();
    }

    // Add ID if not present
    if (!event.id) {
      event.id = `${event.type}-${event.timestamp}-${Math.random().toString(36).slice(2, 9)}`;
    }

    // Add to replay buffer
    this.replayBuffer.push(event);
    if (this.replayBuffer.length > this.maxReplaySize) {
      this.replayBuffer.shift();
    }

    // Emit to subscribers
    this.subject.next(event);
    
    logger.debug('Event emitted', { 
      type: event.type, 
      id: event.id,
      timestamp: event.timestamp 
    });
  }

  /**
   * Subscribe to events of a specific type
   * Returns unsubscribe function
   */
  on<T extends OrchestrationEvent>(
    type: T['type'],
    handler: (event: T) => void | Promise<void>
  ): () => void {
    const subscription = this.subject
      .pipe(
        filter((event): event is T => event.type === type),
        map(async (event) => {
          try {
            await handler(event);
          } catch (error) {
            logger.error(`Error in event handler for ${type}`, error as Error, {
              eventId: event.id,
              eventType: event.type,
            });
          }
        })
      )
      .subscribe();

    logger.debug('Event subscription created', { type });

    // Return unsubscribe function
    return () => {
      subscription.unsubscribe();
      logger.debug('Event subscription removed', { type });
    };
  }

  /**
   * Subscribe to a single event occurrence
   */
  once<T extends OrchestrationEvent>(
    type: T['type'],
    handler: (event: T) => void | Promise<void>
  ): void {
    let unsub: (() => void) | null = null;
    
    unsub = this.on(type, async (event) => {
      await handler(event);
      if (unsub) {
        unsub();
      }
    });
  }

  /**
   * Unsubscribe from events (legacy API, prefer using returned unsubscribe function)
   */
  off(type: EventType, handler: (event: OrchestrationEvent) => void): void {
    // Note: This is a simplified implementation
    // In practice, you'd need to track handlers more carefully
    logger.warn('off() called - prefer using unsubscribe function from on()', { type });
  }

  /**
   * Get observable stream for a specific event type
   * Useful for advanced reactive patterns
   */
  stream<T extends OrchestrationEvent>(type: T['type']): Observable<T> {
    return this.subject.pipe(
      filter((event): event is T => event.type === type)
    );
  }

  /**
   * Get observable stream for all events
   */
  streamAll(): Observable<OrchestrationEvent> {
    return this.subject.asObservable();
  }

  /**
   * Replay recent events to a new subscriber
   */
  replay(handler: (event: OrchestrationEvent) => void | Promise<void>): void {
    for (const event of this.replayBuffer) {
      handler(event).catch((error) => {
        logger.error('Error replaying event', error, {
          eventId: event.id,
          eventType: event.type,
        });
      });
    }
  }

  /**
   * Get current replay buffer (for debugging)
   */
  getReplayBuffer(): readonly OrchestrationEvent[] {
    return [...this.replayBuffer];
  }

  /**
   * Clear replay buffer
   */
  clearReplayBuffer(): void {
    this.replayBuffer = [];
    logger.info('Replay buffer cleared');
  }

  /**
   * Shutdown event bus
   */
  shutdown(): void {
    this.subject.complete();
    this.replayBuffer = [];
    logger.info('Event bus shut down');
  }
}

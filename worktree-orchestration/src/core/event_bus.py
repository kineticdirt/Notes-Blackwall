"""
Event bus implementation - lightweight, async, with backpressure.

No heavy dependencies - pure Python asyncio with bounded queues.
"""
import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, TypeVar

from .event_types import Event, EventType, OrchestrationEvent

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Event)


class EventBus:
    """
    Lightweight async event bus with bounded queues and backpressure.
    
    Features:
    - Async event emission and handling
    - Bounded queues prevent memory bloat
    - Event replay for crash recovery
    - Type-safe event subscriptions
    - Backpressure handling via queue size limits
    """
    
    def __init__(
        self,
        max_queue_size: int = 1000,
        max_replay_size: int = 1000,
        enable_replay: bool = True
    ):
        """
        Initialize event bus.
        
        Args:
            max_queue_size: Maximum events in queue before backpressure
            max_replay_size: Maximum events in replay buffer
            enable_replay: Enable event replay for new subscribers
        """
        self.max_queue_size = max_queue_size
        self.max_replay_size = max_replay_size
        self.enable_replay = enable_replay
        
        # Event queues per type
        self._queues: Dict[EventType, asyncio.Queue] = {}
        
        # Subscribers: event_type -> list of handlers
        self._subscribers: Dict[EventType, List[Callable[[Any], Any]]] = defaultdict(list)
        
        # Replay buffer
        self._replay_buffer: List[OrchestrationEvent] = []
        
        # Background task for processing events
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self._stats = {
            "events_emitted": 0,
            "events_processed": 0,
            "events_dropped": 0,
            "subscribers": 0,
        }
    
    async def start(self):
        """Start event bus processing."""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")
    
    async def stop(self):
        """Stop event bus processing."""
        if not self._running:
            return
        
        self._running = False
        
        # Wait for queue to drain
        for queue in self._queues.values():
            await queue.join()
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Event bus stopped")
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Any], Any],
        replay: bool = True
    ) -> Callable[[], None]:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Async or sync handler function
            replay: Replay recent events to this subscriber
            
        Returns:
            Unsubscribe function
        """
        self._subscribers[event_type].append(handler)
        self._stats["subscribers"] += 1
        
        # Ensure queue exists
        if event_type not in self._queues:
            self._queues[event_type] = asyncio.Queue(maxsize=self.max_queue_size)
        
        # Replay recent events if enabled
        if replay and self.enable_replay:
            asyncio.create_task(self._replay_to_handler(event_type, handler))
        
        logger.debug(f"Subscribed to {event_type}")
        
        def unsubscribe():
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                self._stats["subscribers"] -= 1
                logger.debug(f"Unsubscribed from {event_type}")
        
        return unsubscribe
    
    async def emit(self, event: OrchestrationEvent):
        """
        Emit an event to all subscribers.
        
        Non-blocking - returns immediately. Events are processed asynchronously.
        If queue is full, event is dropped (backpressure).
        
        Args:
            event: Event to emit
        """
        event_type = event.type
        
        # Add to replay buffer
        if self.enable_replay:
            self._replay_buffer.append(event)
            if len(self._replay_buffer) > self.max_replay_size:
                self._replay_buffer.pop(0)
        
        # Ensure queue exists
        if event_type not in self._queues:
            self._queues[event_type] = asyncio.Queue(maxsize=self.max_queue_size)
        
        # Try to put event in queue (non-blocking)
        try:
            self._queues[event_type].put_nowait(event)
            self._stats["events_emitted"] += 1
        except asyncio.QueueFull:
            self._stats["events_dropped"] += 1
            logger.warning(f"Event queue full, dropping event: {event_type}")
    
    async def _process_events(self):
        """Background task to process events from queues."""
        while self._running:
            try:
                # Process events from all queues
                tasks = []
                for event_type, queue in self._queues.items():
                    if not queue.empty():
                        try:
                            event = queue.get_nowait()
                            tasks.append(self._handle_event(event_type, event))
                            queue.task_done()
                        except asyncio.QueueEmpty:
                            continue
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    # No events, sleep briefly
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Error processing events: {e}", exc_info=True)
                await asyncio.sleep(0.1)
    
    async def _handle_event(self, event_type: EventType, event: OrchestrationEvent):
        """Handle a single event by calling all subscribers."""
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            return
        
        # Call all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                self._stats["events_processed"] += 1
            except Exception as e:
                logger.error(
                    f"Error in handler for {event_type}: {e}",
                    exc_info=True
                )
    
    async def _replay_to_handler(self, event_type: EventType, handler: Callable):
        """Replay recent events of a type to a new handler."""
        for event in self._replay_buffer:
            if event.type == event_type:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error replaying event: {e}", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        queue_sizes = {
            str(et): q.qsize() for et, q in self._queues.items()
        }
        return {
            **self._stats,
            "queue_sizes": queue_sizes,
            "replay_buffer_size": len(self._replay_buffer),
        }
    
    def clear_replay_buffer(self):
        """Clear replay buffer."""
        self._replay_buffer.clear()
        logger.info("Replay buffer cleared")


# Global event bus instance (singleton pattern)
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus():
    """Reset global event bus (for testing)."""
    global _event_bus
    _event_bus = None

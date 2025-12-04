"""
FAZA 28 – Agent Execution Loop (AEL)
Event Bus

Internal event system for inter-agent communication.
Provides publish/subscribe mechanism for agent coordination.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    Event data structure.

    Attributes:
        type: Event type identifier (e.g., 'task_completed', 'error_occurred')
        source: Name of agent/component that emitted the event
        data: Event payload (arbitrary data)
        timestamp: Event creation time
        metadata: Additional event metadata
    """
    type: str
    source: str
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<Event: {self.type} from {self.source}>"


class EventBus:
    """
    Internal event bus for agent communication.

    Provides:
    - Event publishing
    - Event subscription with callbacks
    - Event filtering by type
    - Subscription management

    TODO: Add event persistence/logging
    TODO: Add event replay functionality
    TODO: Add async event handlers
    TODO: Add event priority/ordering
    """

    def __init__(self):
        """Initialize event bus"""
        # Subscriptions: event_type -> list of (subscriber_name, callback)
        self._subscriptions: Dict[str, List[tuple[str, Callable]]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = 1000  # Keep last 1000 events
        logger.info("EventBus initialized")

    def subscribe(self, event_type: str, subscriber_name: str, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to (e.g., 'task_completed')
            subscriber_name: Name of subscriber (usually agent name)
            callback: Function to call when event is published

        TODO: Add subscription filters (by source, data patterns)
        TODO: Add subscription priority
        TODO: Emit subscription_added event
        """
        self._subscriptions[event_type].append((subscriber_name, callback))
        logger.debug(f"Subscription added: {subscriber_name} -> {event_type}")

    def unsubscribe(self, event_type: str, subscriber_name: str) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event type to unsubscribe from
            subscriber_name: Name of subscriber

        TODO: Emit subscription_removed event
        """
        if event_type in self._subscriptions:
            self._subscriptions[event_type] = [
                (name, cb) for name, cb in self._subscriptions[event_type]
                if name != subscriber_name
            ]
            logger.debug(f"Subscription removed: {subscriber_name} <- {event_type}")

    def unsubscribe_all(self, subscriber_name: str) -> None:
        """
        Unsubscribe from all events.

        Args:
            subscriber_name: Name of subscriber
        """
        for event_type in list(self._subscriptions.keys()):
            self.unsubscribe(event_type, subscriber_name)
        logger.debug(f"All subscriptions removed for: {subscriber_name}")

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event instance to publish

        TODO: Add async event dispatch
        TODO: Add event validation
        TODO: Add rate limiting per source
        """
        logger.debug(f"Publishing event: {event.type} from {event.source}")

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify subscribers
        if event.type in self._subscriptions:
            for subscriber_name, callback in self._subscriptions[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {subscriber_name}: {e}")

    def emit(self, event_type: str, source: str, data: Any = None, metadata: Optional[Dict] = None) -> None:
        """
        Convenience method to create and publish an event.

        Args:
            event_type: Type of event
            source: Event source (agent/component name)
            data: Event payload
            metadata: Additional metadata
        """
        event = Event(
            type=event_type,
            source=source,
            data=data,
            metadata=metadata or {}
        )
        self.publish(event)

    def get_event_history(self, event_type: Optional[str] = None, source: Optional[str] = None) -> List[Event]:
        """
        Get event history with optional filtering.

        Args:
            event_type: Filter by event type (None = all types)
            source: Filter by source (None = all sources)

        Returns:
            List of events matching filters
        """
        events = self._event_history

        if event_type:
            events = [e for e in events if e.type == event_type]

        if source:
            events = [e for e in events if e.source == source]

        return events

    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
        logger.debug("Event history cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics.

        Returns:
            Dictionary with statistics
        """
        event_types = set(e.type for e in self._event_history)
        event_sources = set(e.source for e in self._event_history)

        return {
            "total_events": len(self._event_history),
            "event_types": len(event_types),
            "event_sources": len(event_sources),
            "subscriptions": {
                event_type: len(subscribers)
                for event_type, subscribers in self._subscriptions.items()
            },
            "max_history": self._max_history
        }

    def __repr__(self) -> str:
        return f"<EventBus: {len(self._event_history)} events, {len(self._subscriptions)} subscription types>"


# Singleton instance
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get singleton EventBus instance.

    Returns:
        Global EventBus instance
    """
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


def create_event_bus() -> EventBus:
    """
    Factory function: create new EventBus instance.

    Returns:
        New EventBus instance
    """
    return EventBus()

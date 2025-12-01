"""
Memory Events - FAZA 12
Location: senti_core_module/senti_memory/memory_events.py

EventBus integration for memory system.
Publishes memory-related events to system EventBus.
"""

from typing import Any, Dict, Optional


class MemoryEvents:
    """
    Memory system event publisher.
    Integrates with Senti Core EventBus.
    """

    # Event type constants
    EVENT_MEMORY_ADDED = "memory.added"
    EVENT_MEMORY_RETRIEVED = "memory.retrieved"
    EVENT_MEMORY_CONSOLIDATED = "memory.consolidated"
    EVENT_MEMORY_CLEANED = "memory.cleaned"
    EVENT_MEMORY_ERROR = "memory.error"

    def __init__(self, event_bus):
        """
        Initialize memory events publisher.

        Args:
            event_bus: EventBus instance from Senti Core
        """
        self.event_bus = event_bus

    # =====================================================
    # EVENT PUBLISHERS
    # =====================================================

    def publish_memory_added(
        self,
        memory_type: str,
        key: str,
        size_bytes: Optional[int] = None
    ) -> None:
        """
        Publish memory added event.

        Args:
            memory_type: Type of memory (working, episodic, semantic)
            key: Memory key/identifier
            size_bytes: Optional data size
        """
        payload = {
            "memory_type": memory_type,
            "key": key,
            "action": "added"
        }

        if size_bytes is not None:
            payload["size_bytes"] = size_bytes

        self.event_bus.publish(self.EVENT_MEMORY_ADDED, payload)

    def publish_memory_retrieved(
        self,
        memory_type: str,
        key: str,
        found: bool
    ) -> None:
        """
        Publish memory retrieved event.

        Args:
            memory_type: Type of memory
            key: Memory key
            found: Whether item was found
        """
        payload = {
            "memory_type": memory_type,
            "key": key,
            "action": "retrieved",
            "found": found
        }

        self.event_bus.publish(self.EVENT_MEMORY_RETRIEVED, payload)

    def publish_memory_consolidated(
        self,
        episodic_count: int,
        semantic_count: int,
        duration_ms: Optional[float] = None
    ) -> None:
        """
        Publish memory consolidation event.

        Args:
            episodic_count: Number of episodic events processed
            semantic_count: Number of semantic facts created
            duration_ms: Consolidation duration in milliseconds
        """
        payload = {
            "action": "consolidated",
            "episodic_count": episodic_count,
            "semantic_count": semantic_count
        }

        if duration_ms is not None:
            payload["duration_ms"] = duration_ms

        self.event_bus.publish(self.EVENT_MEMORY_CONSOLIDATED, payload)

    def publish_memory_cleaned(
        self,
        memory_type: str,
        items_removed: int,
        cleanup_type: str = "expired"
    ) -> None:
        """
        Publish memory cleanup event.

        Args:
            memory_type: Type of memory
            items_removed: Number of items removed
            cleanup_type: Type of cleanup (expired, pruned, cleared)
        """
        payload = {
            "memory_type": memory_type,
            "action": "cleaned",
            "cleanup_type": cleanup_type,
            "items_removed": items_removed
        }

        self.event_bus.publish(self.EVENT_MEMORY_CLEANED, payload)

    def publish_memory_error(
        self,
        memory_type: str,
        action: str,
        error_message: str
    ) -> None:
        """
        Publish memory error event.

        Args:
            memory_type: Type of memory
            action: Action that failed
            error_message: Error description
        """
        payload = {
            "memory_type": memory_type,
            "action": action,
            "error": error_message
        }

        self.event_bus.publish(self.EVENT_MEMORY_ERROR, payload)

    # =====================================================
    # BATCH EVENT PUBLISHING
    # =====================================================

    def publish_episodic_batch_recorded(self, event_count: int) -> None:
        """
        Publish event for batch episodic recording.

        Args:
            event_count: Number of events recorded
        """
        payload = {
            "memory_type": "episodic",
            "action": "batch_added",
            "event_count": event_count
        }

        self.event_bus.publish(self.EVENT_MEMORY_ADDED, payload)

    def publish_semantic_batch_saved(self, fact_count: int) -> None:
        """
        Publish event for batch semantic save.

        Args:
            fact_count: Number of facts saved
        """
        payload = {
            "memory_type": "semantic",
            "action": "batch_added",
            "fact_count": fact_count
        }

        self.event_bus.publish(self.EVENT_MEMORY_ADDED, payload)

    # =====================================================
    # STATISTICS EVENTS
    # =====================================================

    def publish_memory_stats(
        self,
        working_items: int,
        episodic_events: int,
        semantic_facts: int
    ) -> None:
        """
        Publish memory statistics snapshot.

        Args:
            working_items: Working memory item count
            episodic_events: Episodic memory event count
            semantic_facts: Semantic memory fact count
        """
        payload = {
            "action": "stats_snapshot",
            "working_items": working_items,
            "episodic_events": episodic_events,
            "semantic_facts": semantic_facts
        }

        self.event_bus.publish("memory.stats", payload)


class MemoryEventListener:
    """
    Helper class for subscribing to memory events.
    """

    def __init__(self, event_bus):
        """
        Initialize event listener.

        Args:
            event_bus: EventBus instance
        """
        self.event_bus = event_bus
        self.handlers = {}

    def subscribe_to_memory_events(
        self,
        on_added: Optional[callable] = None,
        on_retrieved: Optional[callable] = None,
        on_consolidated: Optional[callable] = None,
        on_cleaned: Optional[callable] = None,
        on_error: Optional[callable] = None
    ) -> None:
        """
        Subscribe to memory events with custom handlers.

        Args:
            on_added: Handler for memory added events
            on_retrieved: Handler for memory retrieved events
            on_consolidated: Handler for consolidation events
            on_cleaned: Handler for cleanup events
            on_error: Handler for error events
        """
        if on_added:
            self.event_bus.subscribe(MemoryEvents.EVENT_MEMORY_ADDED, on_added)
            self.handlers[MemoryEvents.EVENT_MEMORY_ADDED] = on_added

        if on_retrieved:
            self.event_bus.subscribe(MemoryEvents.EVENT_MEMORY_RETRIEVED, on_retrieved)
            self.handlers[MemoryEvents.EVENT_MEMORY_RETRIEVED] = on_retrieved

        if on_consolidated:
            self.event_bus.subscribe(MemoryEvents.EVENT_MEMORY_CONSOLIDATED, on_consolidated)
            self.handlers[MemoryEvents.EVENT_MEMORY_CONSOLIDATED] = on_consolidated

        if on_cleaned:
            self.event_bus.subscribe(MemoryEvents.EVENT_MEMORY_CLEANED, on_cleaned)
            self.handlers[MemoryEvents.EVENT_MEMORY_CLEANED] = on_cleaned

        if on_error:
            self.event_bus.subscribe(MemoryEvents.EVENT_MEMORY_ERROR, on_error)
            self.handlers[MemoryEvents.EVENT_MEMORY_ERROR] = on_error

    def unsubscribe_all(self) -> None:
        """Unsubscribe from all memory events."""
        for event_type, handler in self.handlers.items():
            self.event_bus.unsubscribe(event_type, handler)

        self.handlers.clear()

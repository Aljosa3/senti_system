"""
FAZA 41 — Event Context
-----------------------
Structured container for event data passed through EventBus.

EventContext provides:
- Event metadata (type, source, timestamp)
- Event payload (arbitrary data)
- Event properties (priority, category)
- Serialization support
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import time


class EventContext:
    """
    Structured event data container.

    Every event published through EventBus is wrapped in an EventContext
    which provides standardized metadata and payload structure.
    """

    def __init__(
        self,
        event_type: str,
        source: str,
        payload: Dict[str, Any],
        category: Optional[str] = None,
        priority: int = 5
    ):
        """
        Create an event context.

        Args:
            event_type: Event type identifier (e.g., "module.loaded")
            source: Source module/component name
            payload: Event-specific data
            category: Optional event category (e.g., "lifecycle", "state")
            priority: Event priority (1=highest, 10=lowest), default=5
        """
        self.event_type = event_type
        self.source = source
        self.payload = payload
        self.category = category or "general"
        self.priority = priority
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize event context to dict.

        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "category": self.category,
            "priority": self.priority,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventContext:
        """
        Deserialize event context from dict.

        Args:
            data: Dictionary containing event data

        Returns:
            EventContext instance
        """
        ctx = cls(
            event_type=data["event_type"],
            source=data["source"],
            payload=data.get("payload", {}),
            category=data.get("category", "general"),
            priority=data.get("priority", 5)
        )

        # Restore timestamp if provided
        if "timestamp" in data:
            ctx.timestamp = data["timestamp"]

        return ctx

    def __repr__(self) -> str:
        return f"EventContext(type={self.event_type}, source={self.source}, category={self.category})"

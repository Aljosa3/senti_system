"""
FAZA 19 - UIL Event Bus

Unified Interaction Layer event bus with publish/subscribe architecture.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import threading


class EventCategory(Enum):
    """Event categories for UIL."""
    OS_STATUS = "os_status"
    TASK_PROGRESS = "task_progress"
    LLM_ROUTING = "llm_routing"
    EXPLAINABILITY = "explainability"
    MODEL_ENSEMBLE = "model_ensemble"
    ORCHESTRATION_STEP = "orchestration_step"
    AUTH_FLOW = "auth_flow"
    WAIT_EXTERNAL_BIOMETRIC = "wait_external_biometric"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class UILEvent:
    """Unified Interaction Layer event."""
    event_id: str
    category: EventCategory
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source_device_id: Optional[str] = None


class UILEventBus:
    """
    Event bus for Unified Interaction Layer.

    Implements publish/subscribe pattern for real-time communication
    across multiple devices.
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[EventCategory, List[Callable]] = {}
        self._event_history: List[UILEvent] = []
        self._event_counter = 0
        self._lock = threading.Lock()

    def subscribe(
        self,
        category: EventCategory,
        callback: Callable[[UILEvent], None]
    ) -> str:
        """
        Subscribe to event category.

        Args:
            category: Event category to subscribe to.
            callback: Function to call when event is published.

        Returns:
            Subscription ID.
        """
        with self._lock:
            if category not in self._subscribers:
                self._subscribers[category] = []
            self._subscribers[category].append(callback)
            return f"sub_{category.value}_{len(self._subscribers[category])}"

    def publish(
        self,
        category: EventCategory,
        event_type: str,
        data: Dict[str, Any],
        source_device_id: Optional[str] = None
    ) -> str:
        """
        Publish event to subscribers.

        Args:
            category: Event category.
            event_type: Specific event type.
            data: Event data.
            source_device_id: Optional source device ID.

        Returns:
            Event ID.
        """
        with self._lock:
            self._event_counter += 1
            event_id = f"evt_{self._event_counter}"

            event = UILEvent(
                event_id=event_id,
                category=category,
                event_type=event_type,
                data=data,
                timestamp=datetime.utcnow(),
                source_device_id=source_device_id
            )

            # Store in history
            self._event_history.append(event)

            # Notify subscribers
            subscribers = self._subscribers.get(category, [])
            for callback in subscribers:
                try:
                    callback(event)
                except Exception:
                    # Subscriber error should not break event bus
                    pass

            return event_id

    def get_event_history(
        self,
        category: Optional[EventCategory] = None,
        limit: int = 100
    ) -> List[UILEvent]:
        """Get event history."""
        with self._lock:
            events = self._event_history
            if category:
                events = [e for e in events if e.category == category]
            return events[-limit:]

    def clear_history(self):
        """Clear event history."""
        with self._lock:
            self._event_history.clear()


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "uil_event_bus",
        "faza": "19",
        "version": "1.0.0",
        "description": "Event bus for Unified Interaction Layer"
    }

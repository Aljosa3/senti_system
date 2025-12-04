"""
FAZA 29 – Enterprise Governance Engine
Event Hooks

Defines all FAZA 29 events and schemas.
Wraps FAZA 28 EventBus for type safety and consistent event naming.
"""

import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """FAZA 29 event types"""
    # Governance events
    GOVERNANCE_DECISION = "governance.decision"
    GOVERNANCE_ALLOW = "governance.allow"
    GOVERNANCE_BLOCK = "governance.block"
    GOVERNANCE_ESCALATE = "governance.escalate"
    GOVERNANCE_OVERRIDE = "governance.override"

    # Risk events
    RISK_ASSESSED = "risk.assessed"
    RISK_HIGH = "risk.high"
    RISK_CRITICAL = "risk.critical"
    RISK_FACTOR_CRITICAL = "risk.factor_critical"

    # Override events
    OVERRIDE_PUSHED = "override.pushed"
    OVERRIDE_POPPED = "override.popped"
    OVERRIDE_CLEARED = "override.cleared"
    OVERRIDE_EMERGENCY = "override.emergency"

    # Takeover events
    TAKEOVER_WARNING = "takeover.warning"
    TAKEOVER_INITIATED = "takeover.initiated"
    TAKEOVER_SAFE_MODE = "takeover.safe_mode_entered"
    TAKEOVER_SCHEDULER_FROZEN = "takeover.scheduler_frozen"
    TAKEOVER_RECOVERY = "takeover.recovery_initiated"

    # Tick events
    TICK_ADJUSTED = "tick.adjusted"
    TICK_SPIKE_SUPPRESSED = "tick.spike_suppressed"

    # Feedback events
    FEEDBACK_CORRECTION = "feedback.correction"
    FEEDBACK_STABILIZED = "feedback.stabilized"

    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"


@dataclass
class FazaEvent:
    """
    FAZA 29 event structure.

    Attributes:
        event_type: Event type
        source: Event source component
        data: Event data payload
        timestamp: Event timestamp
        severity: Event severity (0-10)
        metadata: Additional metadata
    """
    event_type: EventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "metadata": self.metadata
        }


class EventHooks:
    """
    FAZA 29 event hooks manager.

    Provides type-safe event publishing and subscription
    wrapper around FAZA 28 EventBus.
    """

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize event hooks.

        Args:
            event_bus: Optional FAZA 28 EventBus instance
        """
        self.event_bus = event_bus
        self.subscribers: Dict[EventType, list] = {}

        # Statistics
        self.stats = {
            "events_published": 0,
            "events_by_type": {},
            "subscribers_count": 0
        }

    def publish(self, event: FazaEvent) -> None:
        """
        Publish event.

        Args:
            event: FazaEvent to publish
        """
        # Update statistics
        self.stats["events_published"] += 1
        event_type_str = event.event_type.value
        self.stats["events_by_type"][event_type_str] = \
            self.stats["events_by_type"].get(event_type_str, 0) + 1

        # Publish to FAZA 28 EventBus if available
        if self.event_bus is not None:
            try:
                self.event_bus.publish(event.to_dict())
            except Exception as e:
                logger.error(f"Failed to publish event {event.event_type.value}: {e}")

        # Notify local subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")

        logger.debug(f"Event published: {event.event_type.value}")

    def subscribe(self, event_type: EventType, callback: Callable[[FazaEvent], None]) -> None:
        """
        Subscribe to event type.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)
        self.stats["subscribers_count"] += 1

        logger.debug(f"Subscribed to {event_type.value}")

    def unsubscribe(self, event_type: EventType, callback: Callable) -> bool:
        """
        Unsubscribe from event type.

        Args:
            event_type: Event type
            callback: Callback to remove

        Returns:
            True if unsubscribed, False if not found
        """
        if event_type not in self.subscribers:
            return False

        if callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.stats["subscribers_count"] -= 1
            return True

        return False

    # Convenience methods for common events

    def publish_governance_decision(self, decision: str, context: Dict[str, Any]) -> None:
        """Publish governance decision event"""
        event = FazaEvent(
            event_type=EventType.GOVERNANCE_DECISION,
            source="governance_engine",
            data={"decision": decision, "context": context},
            severity=7
        )
        self.publish(event)

    def publish_risk_assessed(self, risk_score: float, breakdown: Dict[str, Any]) -> None:
        """Publish risk assessment event"""
        severity = 10 if risk_score >= 80 else 7 if risk_score >= 60 else 5
        event = FazaEvent(
            event_type=EventType.RISK_ASSESSED,
            source="risk_model",
            data={"risk_score": risk_score, "breakdown": breakdown},
            severity=severity
        )
        self.publish(event)

    def publish_takeover_initiated(self, reason: str, metrics: Dict[str, Any]) -> None:
        """Publish takeover initiated event"""
        event = FazaEvent(
            event_type=EventType.TAKEOVER_INITIATED,
            source="takeover_manager",
            data={"reason": reason, "metrics": metrics},
            severity=10
        )
        self.publish(event)

    def publish_override_pushed(self, override_id: str, override_data: Dict[str, Any]) -> None:
        """Publish override pushed event"""
        event = FazaEvent(
            event_type=EventType.OVERRIDE_PUSHED,
            source="override_system",
            data={"override_id": override_id, "override": override_data},
            severity=8
        )
        self.publish(event)

    def publish_tick_adjusted(self, new_hz: float, factors: Dict[str, float]) -> None:
        """Publish tick adjusted event"""
        event = FazaEvent(
            event_type=EventType.TICK_ADJUSTED,
            source="adaptive_tick",
            data={"hz": new_hz, "factors": factors},
            severity=3
        )
        self.publish(event)

    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics"""
        return {
            "events_published": self.stats["events_published"],
            "events_by_type": self.stats["events_by_type"],
            "subscribers_count": self.stats["subscribers_count"],
            "event_types_count": len(EventType)
        }


def create_event_hooks(event_bus: Optional[Any] = None) -> EventHooks:
    """
    Factory function to create EventHooks instance.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        EventHooks instance
    """
    return EventHooks(event_bus)

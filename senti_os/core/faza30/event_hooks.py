"""
FAZA 30 – Event Hooks

Type-safe event system for self-healing events.

Provides:
- Event type definitions
- Event publishing
- Event subscription
- FAZA 28 EventBus integration
- Event statistics

Architecture:
    EventType - Event type enumeration
    FazaEvent - Event structure
    EventHooks - Event manager

Usage:
    from senti_os.core.faza30.event_hooks import EventHooks

    hooks = EventHooks(event_bus)
    hooks.publish_event("fault_detected", {"fault_id": "f123"})
    hooks.subscribe("fault_detected", my_callback)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime


class EventType(Enum):
    """
    FAZA 30 event types.

    Categories:
    - Detection events
    - Classification events
    - Repair events
    - Healing events
    - Health events
    - Snapshot events
    - Autorepair events
    - Controller events
    """
    # Detection events
    FAULT_DETECTED = "fault_detected"
    FAULT_RESOLVED = "fault_resolved"
    CRITICAL_FAULT = "critical_fault"
    PREDICTION_MADE = "prediction_made"

    # Classification events
    FAULT_CLASSIFIED = "fault_classified"
    CLASSIFICATION_FAILED = "classification_failed"

    # Repair events
    REPAIR_STARTED = "repair_started"
    REPAIR_COMPLETED = "repair_completed"
    REPAIR_FAILED = "repair_failed"
    REPAIR_VERIFIED = "repair_verified"

    # Healing events
    HEALING_CYCLE_STARTED = "healing_cycle_started"
    HEALING_CYCLE_COMPLETED = "healing_cycle_completed"
    HEALING_CYCLE_FAILED = "healing_cycle_failed"
    ROLLBACK_PERFORMED = "rollback_performed"

    # Health events
    HEALTH_COMPUTED = "health_computed"
    HEALTH_DEGRADED = "health_degraded"
    HEALTH_IMPROVED = "health_improved"
    HEALTH_CRITICAL = "health_critical"

    # Snapshot events
    SNAPSHOT_CREATED = "snapshot_created"
    SNAPSHOT_RESTORED = "snapshot_restored"
    SNAPSHOT_DELETED = "snapshot_deleted"

    # Autorepair events
    AUTOREPAIR_STARTED = "autorepair_started"
    AUTOREPAIR_STOPPED = "autorepair_stopped"
    AUTOREPAIR_MODE_CHANGED = "autorepair_mode_changed"
    AUTOREPAIR_THROTTLED = "autorepair_throttled"
    AUTOREPAIR_BLOCKED = "autorepair_blocked"
    FORCED_HEALING_CYCLE = "forced_healing_cycle"

    # Controller events
    CONTROLLER_INITIALIZED = "controller_initialized"
    CONTROLLER_STARTED = "controller_started"
    CONTROLLER_STOPPED = "controller_stopped"
    AUTOREPAIR_CONFIG_UPDATED = "autorepair_config_updated"
    AUTOREPAIR_ERROR = "autorepair_error"


@dataclass
class FazaEvent:
    """
    FAZA 30 event structure.

    Attributes:
        event_type: Type of event
        data: Event data payload
        timestamp: When event occurred
        source: Event source (usually "faza30")
    """
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "faza30"


class EventHooks:
    """
    Event management system for FAZA 30.

    Features:
    - Type-safe event publishing
    - Local subscription system
    - FAZA 28 EventBus integration
    - Event history
    - Statistics tracking

    Events can be subscribed to locally and/or published to FAZA 28 EventBus.
    """

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize event hooks.

        Args:
            event_bus: Optional FAZA 28 EventBus for integration
        """
        self.event_bus = event_bus

        # Local subscriptions
        self._subscriptions: Dict[str, List[Callable]] = {}

        # Event history (limited to most recent)
        self._event_history: List[FazaEvent] = []
        self._max_history = 100

        # Statistics
        self._stats = {
            "total_events_published": 0,
            "events_by_type": {},
            "subscriptions_active": 0
        }

    def publish_event(
        self,
        event_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish an event.

        Args:
            event_type: Type of event (can be EventType enum or string)
            data: Optional event data
        """
        # Normalize event type
        if isinstance(event_type, EventType):
            event_type = event_type.value

        # Create event
        event = FazaEvent(
            event_type=event_type,
            data=data or {},
            timestamp=datetime.now()
        )

        # Update statistics
        self._stats["total_events_published"] += 1
        self._stats["events_by_type"][event_type] = self._stats["events_by_type"].get(event_type, 0) + 1

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # Publish to local subscribers
        self._publish_local(event)

        # Publish to FAZA 28 EventBus if available
        self._publish_to_event_bus(event)

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[FazaEvent], None]
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function
        """
        # Normalize event type
        if isinstance(event_type, EventType):
            event_type = event_type.value

        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        self._subscriptions[event_type].append(callback)
        self._stats["subscriptions_active"] += 1

    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[FazaEvent], None]
    ) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event type to unsubscribe from
            callback: Callback function to remove
        """
        # Normalize event type
        if isinstance(event_type, EventType):
            event_type = event_type.value

        if event_type in self._subscriptions:
            if callback in self._subscriptions[event_type]:
                self._subscriptions[event_type].remove(callback)
                self._stats["subscriptions_active"] -= 1

    def _publish_local(self, event: FazaEvent) -> None:
        """Publish event to local subscribers."""
        if event.event_type in self._subscriptions:
            for callback in self._subscriptions[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    # Ignore callback errors
                    pass

    def _publish_to_event_bus(self, event: FazaEvent) -> None:
        """Publish event to FAZA 28 EventBus."""
        if self.event_bus and hasattr(self.event_bus, 'publish'):
            try:
                event_name = f"faza30.{event.event_type}"
                event_data = {
                    **event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source
                }
                self.event_bus.publish(event_name, event_data)
            except Exception:
                # Ignore EventBus errors
                pass

    # ======================
    # Convenience Methods
    # ======================

    def publish_fault_detected(self, fault_id: str, severity: str, fault_type: str) -> None:
        """Publish fault detected event."""
        self.publish_event(EventType.FAULT_DETECTED, {
            "fault_id": fault_id,
            "severity": severity,
            "fault_type": fault_type
        })

    def publish_fault_resolved(self, fault_id: str) -> None:
        """Publish fault resolved event."""
        self.publish_event(EventType.FAULT_RESOLVED, {
            "fault_id": fault_id
        })

    def publish_critical_fault(self, fault_id: str, description: str) -> None:
        """Publish critical fault event."""
        self.publish_event(EventType.CRITICAL_FAULT, {
            "fault_id": fault_id,
            "description": description
        })

    def publish_repair_started(self, fault_id: str, repair_type: str) -> None:
        """Publish repair started event."""
        self.publish_event(EventType.REPAIR_STARTED, {
            "fault_id": fault_id,
            "repair_type": repair_type
        })

    def publish_repair_completed(
        self,
        fault_id: str,
        repair_type: str,
        success: bool,
        duration: float
    ) -> None:
        """Publish repair completed event."""
        self.publish_event(EventType.REPAIR_COMPLETED, {
            "fault_id": fault_id,
            "repair_type": repair_type,
            "success": success,
            "duration": duration
        })

    def publish_healing_cycle_started(self, cycle_id: str) -> None:
        """Publish healing cycle started event."""
        self.publish_event(EventType.HEALING_CYCLE_STARTED, {
            "cycle_id": cycle_id
        })

    def publish_healing_cycle_completed(
        self,
        cycle_id: str,
        outcome: str,
        faults_detected: int,
        faults_repaired: int,
        health_improvement: float
    ) -> None:
        """Publish healing cycle completed event."""
        self.publish_event(EventType.HEALING_CYCLE_COMPLETED, {
            "cycle_id": cycle_id,
            "outcome": outcome,
            "faults_detected": faults_detected,
            "faults_repaired": faults_repaired,
            "health_improvement": health_improvement
        })

    def publish_health_computed(self, overall_score: float, level: str) -> None:
        """Publish health computed event."""
        self.publish_event(EventType.HEALTH_COMPUTED, {
            "overall_score": overall_score,
            "level": level
        })

    def publish_health_critical(self, overall_score: float) -> None:
        """Publish health critical event."""
        self.publish_event(EventType.HEALTH_CRITICAL, {
            "overall_score": overall_score
        })

    def publish_snapshot_created(self, snapshot_id: str, snapshot_type: str) -> None:
        """Publish snapshot created event."""
        self.publish_event(EventType.SNAPSHOT_CREATED, {
            "snapshot_id": snapshot_id,
            "snapshot_type": snapshot_type
        })

    def publish_snapshot_restored(self, snapshot_id: str) -> None:
        """Publish snapshot restored event."""
        self.publish_event(EventType.SNAPSHOT_RESTORED, {
            "snapshot_id": snapshot_id
        })

    def publish_autorepair_throttled(self, reason: str) -> None:
        """Publish autorepair throttled event."""
        self.publish_event(EventType.AUTOREPAIR_THROTTLED, {
            "reason": reason
        })

    def publish_autorepair_blocked(self, reason: str) -> None:
        """Publish autorepair blocked event."""
        self.publish_event(EventType.AUTOREPAIR_BLOCKED, {
            "reason": reason
        })

    # ======================
    # Query Methods
    # ======================

    def get_event_history(self, limit: int = 50) -> List[FazaEvent]:
        """
        Get recent event history.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        return self._event_history[-limit:]

    def get_events_by_type(self, event_type: str, limit: int = 20) -> List[FazaEvent]:
        """
        Get recent events of a specific type.

        Args:
            event_type: Event type to filter
            limit: Maximum number of events to return

        Returns:
            List of events of specified type
        """
        # Normalize event type
        if isinstance(event_type, EventType):
            event_type = event_type.value

        matching_events = [e for e in self._event_history if e.event_type == event_type]
        return matching_events[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event statistics.

        Returns:
            Dict with event statistics
        """
        return {
            **self._stats,
            "history_size": len(self._event_history),
            "event_types_seen": len(self._stats["events_by_type"]),
            "top_events": sorted(
                self._stats["events_by_type"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


def create_event_hooks(event_bus: Optional[Any] = None) -> EventHooks:
    """
    Factory function to create EventHooks.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        Initialized EventHooks instance
    """
    return EventHooks(event_bus=event_bus)

"""
FAZA 29 – Enterprise Governance Engine
Override System

Implements user override mechanism (ALWAYS FINAL AUTHORITY).
Features:
- Override stack (LIFO)
- Cooldown model
- Logging and FAZA 28 event notices
- Fallback rules for system instability
- Emergency override capabilities
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class OverrideType(Enum):
    """Override type enumeration"""
    USER = "user"               # User-initiated override
    EMERGENCY = "emergency"     # Emergency override
    SYSTEM = "system"           # System-initiated override
    FALLBACK = "fallback"       # Fallback override


class OverrideReason(Enum):
    """Override reason codes"""
    MANUAL = "manual"                       # Manual user override
    EMERGENCY_STOP = "emergency_stop"       # Emergency system stop
    INSTABILITY = "instability"             # System instability detected
    POLICY_OVERRIDE = "policy_override"     # Policy override required
    TESTING = "testing"                     # Testing/debugging
    MAINTENANCE = "maintenance"             # Maintenance mode


@dataclass
class Override:
    """
    Individual override entry.

    Attributes:
        override_id: Unique override identifier
        override_type: Type of override
        reason: Override reason
        timestamp: Override timestamp
        expiry: Optional expiry time
        metadata: Additional metadata
        active: Override active status
    """
    override_id: str
    override_type: OverrideType
    reason: OverrideReason
    timestamp: datetime = field(default_factory=datetime.now)
    expiry: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def is_expired(self) -> bool:
        """Check if override is expired"""
        if self.expiry is None:
            return False
        return datetime.now() >= self.expiry

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "override_id": self.override_id,
            "override_type": self.override_type.value,
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "metadata": self.metadata,
            "active": self.active
        }


class OverrideSystem:
    """
    User override system with stack management and cooldown.

    Ensures user override ALWAYS has final authority over all
    automated governance decisions.
    """

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize override system.

        Args:
            event_bus: Optional FAZA 28 EventBus for notifications
        """
        self.event_bus = event_bus

        # Override stack (LIFO)
        self.override_stack: List[Override] = []

        # Cooldown settings
        self.cooldown_enabled = True
        self.cooldown_duration = timedelta(seconds=30)
        self.last_override_time: Optional[datetime] = None

        # Statistics
        self.stats = {
            "total_overrides": 0,
            "user_overrides": 0,
            "emergency_overrides": 0,
            "system_overrides": 0,
            "expired_overrides": 0,
            "cooldown_violations": 0
        }

    def push_override(
        self,
        override_type: OverrideType,
        reason: OverrideReason,
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Push new override onto stack.

        Args:
            override_type: Type of override
            reason: Override reason
            duration_seconds: Optional duration (None = permanent)
            metadata: Additional metadata

        Returns:
            Override ID
        """
        # Check cooldown
        if self.cooldown_enabled and self._in_cooldown():
            logger.warning("Override rejected: cooldown period active")
            self.stats["cooldown_violations"] += 1
            raise RuntimeError("Override cooldown period active")

        # Create override
        override_id = f"override_{datetime.now().timestamp()}"
        expiry = None
        if duration_seconds is not None:
            expiry = datetime.now() + timedelta(seconds=duration_seconds)

        override = Override(
            override_id=override_id,
            override_type=override_type,
            reason=reason,
            expiry=expiry,
            metadata=metadata or {}
        )

        # Push to stack
        self.override_stack.append(override)
        self.last_override_time = datetime.now()

        # Update statistics
        self.stats["total_overrides"] += 1
        if override_type == OverrideType.USER:
            self.stats["user_overrides"] += 1
        elif override_type == OverrideType.EMERGENCY:
            self.stats["emergency_overrides"] += 1
        elif override_type == OverrideType.SYSTEM:
            self.stats["system_overrides"] += 1

        logger.info(f"Override pushed: {override_id} ({override_type.value}, {reason.value})")

        # Emit event
        self._emit_event("override.pushed", override.to_dict())

        return override_id

    def pop_override(self) -> Optional[Override]:
        """
        Pop override from stack (LIFO).

        Returns:
            Popped override, or None if stack empty
        """
        if not self.override_stack:
            return None

        override = self.override_stack.pop()
        override.active = False

        logger.info(f"Override popped: {override.override_id}")

        # Emit event
        self._emit_event("override.popped", override.to_dict())

        return override

    def clear_stack(self) -> int:
        """
        Clear entire override stack.

        Returns:
            Number of overrides cleared
        """
        count = len(self.override_stack)
        self.override_stack.clear()

        logger.info(f"Override stack cleared: {count} overrides removed")

        # Emit event
        self._emit_event("override.cleared", {"count": count})

        return count

    def is_override_active(self) -> bool:
        """
        Check if any override is currently active.

        Returns:
            True if override active, False otherwise
        """
        # Clean expired overrides first
        self._clean_expired()

        return len(self.override_stack) > 0

    def get_active_override(self) -> Optional[Override]:
        """
        Get current active override (top of stack).

        Returns:
            Active override, or None if stack empty
        """
        # Clean expired overrides first
        self._clean_expired()

        if not self.override_stack:
            return None

        return self.override_stack[-1]

    def _clean_expired(self) -> None:
        """Remove expired overrides from stack"""
        original_count = len(self.override_stack)

        # Filter out expired overrides
        self.override_stack = [o for o in self.override_stack if not o.is_expired()]

        expired_count = original_count - len(self.override_stack)
        if expired_count > 0:
            self.stats["expired_overrides"] += expired_count
            logger.debug(f"Cleaned {expired_count} expired overrides")

    def _in_cooldown(self) -> bool:
        """
        Check if system is in cooldown period.

        Returns:
            True if in cooldown, False otherwise
        """
        if self.last_override_time is None:
            return False

        time_since_last = datetime.now() - self.last_override_time
        return time_since_last < self.cooldown_duration

    def get_cooldown_remaining(self) -> float:
        """
        Get remaining cooldown time in seconds.

        Returns:
            Remaining cooldown seconds, or 0 if not in cooldown
        """
        if not self._in_cooldown():
            return 0.0

        time_since_last = datetime.now() - self.last_override_time
        remaining = self.cooldown_duration - time_since_last
        return remaining.total_seconds()

    def emergency_override(
        self,
        reason: str = "Emergency stop",
        duration_seconds: float = 300.0
    ) -> str:
        """
        Activate emergency override (bypasses cooldown).

        Args:
            reason: Emergency reason
            duration_seconds: Override duration

        Returns:
            Override ID
        """
        # Temporarily disable cooldown for emergency
        cooldown_state = self.cooldown_enabled
        self.cooldown_enabled = False

        try:
            override_id = self.push_override(
                override_type=OverrideType.EMERGENCY,
                reason=OverrideReason.EMERGENCY_STOP,
                duration_seconds=duration_seconds,
                metadata={"reason": reason}
            )

            logger.warning(f"EMERGENCY OVERRIDE ACTIVATED: {reason}")

            # Emit emergency event
            self._emit_event("override.emergency", {
                "override_id": override_id,
                "reason": reason
            })

            return override_id

        finally:
            # Restore cooldown state
            self.cooldown_enabled = cooldown_state

    def instability_fallback(self, instability_score: float) -> str:
        """
        Activate fallback override due to system instability.

        Args:
            instability_score: Instability metric (0-1)

        Returns:
            Override ID
        """
        override_id = self.push_override(
            override_type=OverrideType.FALLBACK,
            reason=OverrideReason.INSTABILITY,
            duration_seconds=60.0,  # 1 minute fallback
            metadata={"instability_score": instability_score}
        )

        logger.warning(f"Instability fallback activated: score={instability_score:.2f}")

        return override_id

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit event to FAZA 28 EventBus.

        Args:
            event_type: Event type
            data: Event data
        """
        if self.event_bus is None:
            return

        try:
            from datetime import datetime
            event = {
                "type": event_type,
                "source": "override_system",
                "data": data,
                "timestamp": datetime.now()
            }
            self.event_bus.publish(event)
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")

    def get_stack_size(self) -> int:
        """Get current stack size"""
        self._clean_expired()
        return len(self.override_stack)

    def get_all_overrides(self) -> List[Override]:
        """Get all active overrides"""
        self._clean_expired()
        return self.override_stack.copy()

    def set_cooldown_duration(self, seconds: float) -> None:
        """
        Set cooldown duration.

        Args:
            seconds: Cooldown duration in seconds
        """
        self.cooldown_duration = timedelta(seconds=seconds)
        logger.info(f"Cooldown duration set to {seconds}s")

    def enable_cooldown(self) -> None:
        """Enable cooldown mechanism"""
        self.cooldown_enabled = True
        logger.info("Cooldown enabled")

    def disable_cooldown(self) -> None:
        """Disable cooldown mechanism"""
        self.cooldown_enabled = False
        logger.warning("Cooldown disabled")

    def get_statistics(self) -> Dict[str, Any]:
        """Get override system statistics"""
        return {
            "total_overrides": self.stats["total_overrides"],
            "user_overrides": self.stats["user_overrides"],
            "emergency_overrides": self.stats["emergency_overrides"],
            "system_overrides": self.stats["system_overrides"],
            "expired_overrides": self.stats["expired_overrides"],
            "cooldown_violations": self.stats["cooldown_violations"],
            "active_overrides": self.get_stack_size(),
            "in_cooldown": self._in_cooldown(),
            "cooldown_remaining": round(self.get_cooldown_remaining(), 2)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get override system status"""
        active = self.get_active_override()

        return {
            "override_active": active is not None,
            "active_override": active.to_dict() if active else None,
            "stack_size": self.get_stack_size(),
            "in_cooldown": self._in_cooldown(),
            "cooldown_enabled": self.cooldown_enabled
        }


def create_override_system(event_bus: Optional[Any] = None) -> OverrideSystem:
    """
    Factory function to create OverrideSystem instance.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        OverrideSystem instance
    """
    return OverrideSystem(event_bus)

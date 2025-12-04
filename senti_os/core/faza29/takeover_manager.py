"""
FAZA 29 – Enterprise Governance Engine
Takeover Manager

Implements system takeover mechanism when threshold (70%) is exceeded.
Takeover conditions:
- Runaway agent detection
- Resource collapse
- Governance violation by agents
- Repeated instability (FAZA 28.5)

Features:
- Safe-mode transition
- Forced scheduler freeze
- Priority reassignment
- Meta-layer notification
- Recovery logic with cooldown periods
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TakeoverState(Enum):
    """Takeover state enumeration"""
    NORMAL = "normal"           # Normal operation
    WARNING = "warning"         # Warning threshold reached
    TAKEOVER = "takeover"       # Takeover active
    SAFE_MODE = "safe_mode"     # Safe mode active
    RECOVERY = "recovery"       # Recovery in progress


class TakeoverReason(Enum):
    """Takeover reason codes"""
    RUNAWAY_AGENT = "runaway_agent"
    RESOURCE_COLLAPSE = "resource_collapse"
    GOVERNANCE_VIOLATION = "governance_violation"
    INSTABILITY = "instability"
    CASCADING_FAILURE = "cascading_failure"
    MANUAL = "manual"


@dataclass
class TakeoverCondition:
    """
    Takeover condition definition.

    Attributes:
        condition_id: Unique condition identifier
        name: Condition name
        threshold: Activation threshold (0-1)
        weight: Condition weight
        enabled: Condition enabled status
    """
    condition_id: str
    name: str
    threshold: float
    weight: float = 1.0
    enabled: bool = True


@dataclass
class TakeoverEvent:
    """
    Takeover event record.

    Attributes:
        event_id: Unique event identifier
        reason: Takeover reason
        timestamp: Event timestamp
        metrics: Metrics at takeover
        recovery_time: Optional recovery timestamp
    """
    event_id: str
    reason: TakeoverReason
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recovery_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "event_id": self.event_id,
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "recovery_time": self.recovery_time.isoformat() if self.recovery_time else None
        }


class TakeoverManager:
    """
    System takeover manager.

    Monitors system conditions and initiates takeover when thresholds
    are exceeded to protect system integrity.
    """

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize takeover manager.

        Args:
            event_bus: Optional FAZA 28 EventBus for notifications
        """
        self.event_bus = event_bus

        # State
        self.state = TakeoverState.NORMAL
        self.takeover_score = 0.0

        # Thresholds
        self.warning_threshold = 0.50  # 50%
        self.takeover_threshold = 0.70  # 70% (specified)
        self.critical_threshold = 0.90  # 90%

        # Conditions
        self.conditions: Dict[str, TakeoverCondition] = {}
        self._init_conditions()

        # Takeover state
        self.takeover_active = False
        self.safe_mode_active = False
        self.scheduler_frozen = False

        # History
        self.takeover_history: List[TakeoverEvent] = []

        # Recovery
        self.recovery_cooldown = timedelta(minutes=5)
        self.last_takeover_time: Optional[datetime] = None

        # Statistics
        self.stats = {
            "takeovers": 0,
            "runaway_agent_takeovers": 0,
            "resource_collapse_takeovers": 0,
            "governance_violation_takeovers": 0,
            "instability_takeovers": 0,
            "manual_takeovers": 0,
            "recoveries": 0
        }

    def _init_conditions(self) -> None:
        """Initialize takeover conditions"""
        self.conditions = {
            "runaway_agent": TakeoverCondition(
                condition_id="runaway_agent",
                name="Runaway Agent Detection",
                threshold=0.80,
                weight=1.5
            ),
            "resource_collapse": TakeoverCondition(
                condition_id="resource_collapse",
                name="Resource Collapse",
                threshold=0.85,
                weight=1.8
            ),
            "governance_violation": TakeoverCondition(
                condition_id="governance_violation",
                name="Governance Violation",
                threshold=0.75,
                weight=1.3
            ),
            "instability": TakeoverCondition(
                condition_id="instability",
                name="System Instability",
                threshold=0.70,
                weight=1.4
            ),
            "cascading_failure": TakeoverCondition(
                condition_id="cascading_failure",
                name="Cascading Failure",
                threshold=0.90,
                weight=2.0
            )
        }

    def evaluate(
        self,
        agent_metrics: Optional[Dict[str, Any]] = None,
        system_metrics: Optional[Dict[str, Any]] = None,
        risk_score: float = 0.0
    ) -> TakeoverState:
        """
        Evaluate takeover conditions.

        Args:
            agent_metrics: Agent performance metrics
            system_metrics: System health metrics
            risk_score: Current risk score (0-100)

        Returns:
            Current takeover state
        """
        agent_metrics = agent_metrics or {}
        system_metrics = system_metrics or {}

        # Calculate takeover score
        self.takeover_score = self._calculate_takeover_score(
            agent_metrics,
            system_metrics,
            risk_score
        )

        # Determine state based on score
        previous_state = self.state

        if self.takeover_score >= self.takeover_threshold:
            if not self.takeover_active:
                # Initiate takeover
                reason = self._determine_takeover_reason(agent_metrics, system_metrics)
                self._initiate_takeover(reason, agent_metrics, system_metrics)
            self.state = TakeoverState.TAKEOVER
        elif self.takeover_score >= self.warning_threshold:
            self.state = TakeoverState.WARNING
        else:
            # Check if we can exit takeover
            if self.takeover_active and self._can_recover():
                self._initiate_recovery()
            self.state = TakeoverState.NORMAL

        # Log state change
        if self.state != previous_state:
            logger.info(f"Takeover state changed: {previous_state.value} -> {self.state.value}")

        return self.state

    def _calculate_takeover_score(
        self,
        agent_metrics: Dict[str, Any],
        system_metrics: Dict[str, Any],
        risk_score: float
    ) -> float:
        """
        Calculate takeover score (0-1).

        Args:
            agent_metrics: Agent metrics
            system_metrics: System metrics
            risk_score: Risk score (0-100)

        Returns:
            Takeover score (0-1)
        """
        scores = []
        weights = []

        # Risk score contribution
        normalized_risk = risk_score / 100.0
        scores.append(normalized_risk)
        weights.append(1.0)

        # Runaway agent check
        if self.conditions["runaway_agent"].enabled:
            runaway_score = agent_metrics.get("runaway_detected", 0.0)
            scores.append(runaway_score)
            weights.append(self.conditions["runaway_agent"].weight)

        # Resource collapse check
        if self.conditions["resource_collapse"].enabled:
            cpu_usage = system_metrics.get("cpu_usage", 0.0)
            memory_usage = system_metrics.get("memory_usage", 0.0)
            resource_score = max(cpu_usage, memory_usage)
            scores.append(resource_score)
            weights.append(self.conditions["resource_collapse"].weight)

        # Governance violation check
        if self.conditions["governance_violation"].enabled:
            violation_score = agent_metrics.get("governance_violations", 0.0)
            scores.append(violation_score)
            weights.append(self.conditions["governance_violation"].weight)

        # Instability check
        if self.conditions["instability"].enabled:
            instability_score = 1.0 - agent_metrics.get("stability_score", 1.0)
            scores.append(instability_score)
            weights.append(self.conditions["instability"].weight)

        # Weighted average
        if not scores:
            return 0.0

        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _determine_takeover_reason(
        self,
        agent_metrics: Dict[str, Any],
        system_metrics: Dict[str, Any]
    ) -> TakeoverReason:
        """
        Determine primary takeover reason.

        Args:
            agent_metrics: Agent metrics
            system_metrics: System metrics

        Returns:
            Takeover reason
        """
        # Check each condition
        if agent_metrics.get("runaway_detected", 0.0) > self.conditions["runaway_agent"].threshold:
            return TakeoverReason.RUNAWAY_AGENT

        cpu_usage = system_metrics.get("cpu_usage", 0.0)
        memory_usage = system_metrics.get("memory_usage", 0.0)
        if max(cpu_usage, memory_usage) > self.conditions["resource_collapse"].threshold:
            return TakeoverReason.RESOURCE_COLLAPSE

        if agent_metrics.get("governance_violations", 0.0) > self.conditions["governance_violation"].threshold:
            return TakeoverReason.GOVERNANCE_VIOLATION

        instability = 1.0 - agent_metrics.get("stability_score", 1.0)
        if instability > self.conditions["instability"].threshold:
            return TakeoverReason.INSTABILITY

        # Default to instability
        return TakeoverReason.INSTABILITY

    def _initiate_takeover(
        self,
        reason: TakeoverReason,
        agent_metrics: Dict[str, Any],
        system_metrics: Dict[str, Any]
    ) -> None:
        """
        Initiate system takeover.

        Args:
            reason: Takeover reason
            agent_metrics: Agent metrics
            system_metrics: System metrics
        """
        logger.critical(f"SYSTEM TAKEOVER INITIATED: {reason.value}")

        self.takeover_active = True
        self.last_takeover_time = datetime.now()

        # Create takeover event
        event = TakeoverEvent(
            event_id=f"takeover_{datetime.now().timestamp()}",
            reason=reason,
            metrics={
                "agent_metrics": agent_metrics,
                "system_metrics": system_metrics,
                "takeover_score": self.takeover_score
            }
        )
        self.takeover_history.append(event)

        # Update statistics
        self.stats["takeovers"] += 1
        if reason == TakeoverReason.RUNAWAY_AGENT:
            self.stats["runaway_agent_takeovers"] += 1
        elif reason == TakeoverReason.RESOURCE_COLLAPSE:
            self.stats["resource_collapse_takeovers"] += 1
        elif reason == TakeoverReason.GOVERNANCE_VIOLATION:
            self.stats["governance_violation_takeovers"] += 1
        elif reason == TakeoverReason.INSTABILITY:
            self.stats["instability_takeovers"] += 1

        # Execute takeover actions
        self._enter_safe_mode()
        self._freeze_scheduler()
        self._reassign_priorities()

        # Emit event
        self._emit_event("takeover.initiated", event.to_dict())

    def _enter_safe_mode(self) -> None:
        """Enter safe mode"""
        self.safe_mode_active = True
        logger.warning("Entering SAFE MODE")

        # Emit event
        self._emit_event("takeover.safe_mode_entered", {})

    def _freeze_scheduler(self) -> None:
        """Freeze scheduler"""
        self.scheduler_frozen = True
        logger.warning("Scheduler FROZEN")

        # Emit event
        self._emit_event("takeover.scheduler_frozen", {})

    def _reassign_priorities(self) -> None:
        """Reassign agent priorities (emergency)"""
        logger.info("Reassigning priorities for emergency operation")

        # Emit event
        self._emit_event("takeover.priorities_reassigned", {})

    def _can_recover(self) -> bool:
        """
        Check if system can recover from takeover.

        Returns:
            True if recovery possible, False otherwise
        """
        if not self.takeover_active:
            return False

        # Check cooldown
        if self.last_takeover_time is None:
            return True

        time_since_takeover = datetime.now() - self.last_takeover_time
        return time_since_takeover >= self.recovery_cooldown

    def _initiate_recovery(self) -> None:
        """Initiate recovery from takeover"""
        logger.info("Initiating recovery from takeover")

        self.takeover_active = False
        self.safe_mode_active = False
        self.scheduler_frozen = False
        self.state = TakeoverState.RECOVERY

        # Update last event with recovery time
        if self.takeover_history:
            self.takeover_history[-1].recovery_time = datetime.now()

        self.stats["recoveries"] += 1

        # Emit event
        self._emit_event("takeover.recovery_initiated", {})

        logger.info("Recovery complete - returning to normal operation")

    def manual_takeover(self, reason: str = "Manual takeover") -> None:
        """
        Manually initiate takeover.

        Args:
            reason: Manual takeover reason
        """
        logger.warning(f"Manual takeover initiated: {reason}")

        self._initiate_takeover(
            TakeoverReason.MANUAL,
            {"manual_reason": reason},
            {}
        )

        self.stats["manual_takeovers"] += 1

    def force_recovery(self) -> None:
        """Force immediate recovery"""
        logger.warning("Forcing immediate recovery")
        self._initiate_recovery()

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
            event = {
                "type": event_type,
                "source": "takeover_manager",
                "data": data,
                "timestamp": datetime.now()
            }
            self.event_bus.publish(event)
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")

    def get_state(self) -> TakeoverState:
        """Get current takeover state"""
        return self.state

    def get_takeover_score(self) -> float:
        """Get current takeover score"""
        return self.takeover_score

    def is_takeover_active(self) -> bool:
        """Check if takeover is active"""
        return self.takeover_active

    def is_safe_mode_active(self) -> bool:
        """Check if safe mode is active"""
        return self.safe_mode_active

    def is_scheduler_frozen(self) -> bool:
        """Check if scheduler is frozen"""
        return self.scheduler_frozen

    def get_statistics(self) -> Dict[str, Any]:
        """Get takeover manager statistics"""
        return {
            "takeovers": self.stats["takeovers"],
            "runaway_agent_takeovers": self.stats["runaway_agent_takeovers"],
            "resource_collapse_takeovers": self.stats["resource_collapse_takeovers"],
            "governance_violation_takeovers": self.stats["governance_violation_takeovers"],
            "instability_takeovers": self.stats["instability_takeovers"],
            "manual_takeovers": self.stats["manual_takeovers"],
            "recoveries": self.stats["recoveries"],
            "takeover_history_count": len(self.takeover_history)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get takeover manager status"""
        return {
            "state": self.state.value,
            "takeover_score": round(self.takeover_score, 3),
            "takeover_active": self.takeover_active,
            "safe_mode_active": self.safe_mode_active,
            "scheduler_frozen": self.scheduler_frozen,
            "warning_threshold": self.warning_threshold,
            "takeover_threshold": self.takeover_threshold,
            "can_recover": self._can_recover() if self.takeover_active else False
        }


def create_takeover_manager(event_bus: Optional[Any] = None) -> TakeoverManager:
    """
    Factory function to create TakeoverManager instance.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        TakeoverManager instance
    """
    return TakeoverManager(event_bus)

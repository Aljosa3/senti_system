"""
FAZA 15 - Strategy Events
Event definitions for strategic planning system
"""

from datetime import datetime
from typing import Dict, Any, Optional


class StrategyEvent:
    """Base class for strategy events."""

    def __init__(self, event_type: str, payload: Dict[str, Any], timestamp: Optional[str] = None):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }


class StrategyCreatedEvent(StrategyEvent):
    """Event emitted when a new strategy is created."""

    def __init__(self, plan_id: str, objective: str, risk_score: int, details: Dict[str, Any]):
        super().__init__(
            event_type="STRATEGY_CREATED",
            payload={
                "plan_id": plan_id,
                "objective": objective,
                "risk_score": risk_score,
                "details": details
            }
        )


class StrategyOptimizedEvent(StrategyEvent):
    """Event emitted when a strategy is optimized."""

    def __init__(self, plan_id: str, optimization_count: int, improvements: Dict[str, Any]):
        super().__init__(
            event_type="STRATEGY_OPTIMIZED",
            payload={
                "plan_id": plan_id,
                "optimization_count": optimization_count,
                "improvements": improvements
            }
        )


class StrategyRejectedEvent(StrategyEvent):
    """Event emitted when a strategy is rejected."""

    def __init__(self, plan_id: str, reason: str, violations: list):
        super().__init__(
            event_type="STRATEGY_REJECTED",
            payload={
                "plan_id": plan_id,
                "reason": reason,
                "violations": violations
            }
        )


class HighRiskStrategyEvent(StrategyEvent):
    """Event emitted when a high-risk strategy is detected."""

    def __init__(self, plan_id: str, risk_score: int, objective: str, risk_factors: list):
        super().__init__(
            event_type="HIGH_RISK_STRATEGY",
            payload={
                "plan_id": plan_id,
                "risk_score": risk_score,
                "objective": objective,
                "risk_factors": risk_factors
            }
        )


class StrategyExecutedEvent(StrategyEvent):
    """Event emitted when a strategy execution completes."""

    def __init__(self, plan_id: str, success: bool, results: Dict[str, Any]):
        super().__init__(
            event_type="STRATEGY_EXECUTED",
            payload={
                "plan_id": plan_id,
                "success": success,
                "results": results
            }
        )


class StrategySimulationEvent(StrategyEvent):
    """Event emitted when a strategy simulation completes."""

    def __init__(self, plan_id: str, simulation_results: Dict[str, Any]):
        super().__init__(
            event_type="STRATEGY_SIMULATION_RESULT",
            payload={
                "plan_id": plan_id,
                "simulation_results": simulation_results
            }
        )


# Event type constants
STRATEGY_CREATED = "STRATEGY_CREATED"
STRATEGY_OPTIMIZED = "STRATEGY_OPTIMIZED"
STRATEGY_REJECTED = "STRATEGY_REJECTED"
HIGH_RISK_STRATEGY = "HIGH_RISK_STRATEGY"
STRATEGY_EXECUTED = "STRATEGY_EXECUTED"
STRATEGY_SIMULATION_RESULT = "STRATEGY_SIMULATION_RESULT"

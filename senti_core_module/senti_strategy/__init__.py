"""
FAZA 15 - Senti OS AI Strategy Engine
Strategic planning and autonomous reasoning for Senti OS

Provides goal decomposition, plan generation, reasoning, optimization,
and execution capabilities integrated with FAZA 5-14.

Components:
- StrategyEngine: Core strategic planning mechanism
- ReasoningEngine: Chain-of-thought reasoning without LLM
- StrategyManager: High-level orchestrator
- StrategyRules: FAZA 8 security validation
- OptimizerService: FAZA 6 periodic optimization
- Plan Templates: High-level, mid-level, and atomic action structures
- Events: Strategy event definitions

Example usage:
    from senti_core_module.senti_strategy import StrategyManager

    manager = StrategyManager(memory_manager, prediction_manager, anomaly_manager, event_bus)
    plan = manager.create_strategy("Optimize system performance", {})
    evaluation = manager.evaluate_strategy(plan)
    optimized_plan = manager.optimize_strategy(plan.plan_id)
"""

from .strategy_engine import StrategyEngine
from .reasoning_engine import ReasoningEngine
from .strategy_manager import StrategyManager
from .strategy_rules import StrategyRules
from .optimizer_service import OptimizerService
from .plan_template import (
    HighLevelPlan,
    MidLevelStep,
    AtomicAction,
    ActionPriority,
    ActionStatus,
    StrategyTemplate
)
from .strategy_events import (
    StrategyEvent,
    StrategyCreatedEvent,
    StrategyOptimizedEvent,
    StrategyRejectedEvent,
    HighRiskStrategyEvent,
    StrategyExecutedEvent,
    StrategySimulationEvent,
    STRATEGY_CREATED,
    STRATEGY_OPTIMIZED,
    STRATEGY_REJECTED,
    HIGH_RISK_STRATEGY,
    STRATEGY_EXECUTED,
    STRATEGY_SIMULATION_RESULT
)

__all__ = [
    # Core components
    "StrategyEngine",
    "ReasoningEngine",
    "StrategyManager",
    "StrategyRules",
    "OptimizerService",

    # Plan structures
    "HighLevelPlan",
    "MidLevelStep",
    "AtomicAction",
    "ActionPriority",
    "ActionStatus",
    "StrategyTemplate",

    # Events
    "StrategyEvent",
    "StrategyCreatedEvent",
    "StrategyOptimizedEvent",
    "StrategyRejectedEvent",
    "HighRiskStrategyEvent",
    "StrategyExecutedEvent",
    "StrategySimulationEvent",

    # Event constants
    "STRATEGY_CREATED",
    "STRATEGY_OPTIMIZED",
    "STRATEGY_REJECTED",
    "HIGH_RISK_STRATEGY",
    "STRATEGY_EXECUTED",
    "STRATEGY_SIMULATION_RESULT"
]

__version__ = "1.0.0"
__faza__ = "FAZA 15"

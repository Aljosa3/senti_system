"""
FAZA 29 – Enterprise Governance Engine

Comprehensive governance and control layer for Senti OS.

Provides:
- Governance rules with 3-layer architecture (System, Meta, Override)
- Risk scoring (0-100) from multiple FAZA layers
- User override system (ALWAYS final authority)
- System takeover at 70% threshold
- Adaptive tick frequency control
- Feedback loop stabilization
- Integration with FAZA 25/26/27/27.5/28/28.5

Architecture:
    Governance Rules    - 3-layer rule engine with priorities
    Risk Model          - 16 risk factors across 3 layers
    Override System     - LIFO stack with cooldown
    Takeover Manager    - 70% threshold with safe mode
    Adaptive Tick       - Dynamic frequency (0.1-10 Hz)
    Feedback Loop       - PID-like stability control
    Integration Layer   - Non-intrusive FAZA hooks
    Event Hooks         - Type-safe event system

Usage:
    from senti_os.core.faza29 import get_governance_controller

    # Get controller
    controller = get_governance_controller(event_bus)

    # Start governance loop
    await controller.start()

    # Get status
    status = controller.get_status()
    risk = controller.get_risk()
    decision = controller.get_governance_decision()

    # Manual override
    controller.get_override_system().push_override(
        override_type=OverrideType.USER,
        reason=OverrideReason.MANUAL
    )

Enterprise Features:
- Real-time governance decisions
- Automatic takeover protection
- User override (final authority)
- Dynamic system adaptation
- Comprehensive risk assessment
- Multi-layer integration
"""

# Main governance engine
from senti_os.core.faza29.governance_engine import (
    GovernanceController,
    get_governance_controller,
    create_governance_controller
)

# Governance rules
from senti_os.core.faza29.governance_rules import (
    GovernanceRuleEngine,
    GovernanceRule,
    RuleChain,
    GovernanceDecision,
    RuleLayer,
    RulePriority,
    create_governance_rule_engine
)

# Risk model
from senti_os.core.faza29.risk_model import (
    RiskModel,
    RiskBreakdown,
    RiskFactor,
    compute_risk,
    create_risk_model
)

# Override system
from senti_os.core.faza29.override_system import (
    OverrideSystem,
    Override,
    OverrideType,
    OverrideReason,
    create_override_system
)

# Takeover manager
from senti_os.core.faza29.takeover_manager import (
    TakeoverManager,
    TakeoverState,
    TakeoverReason,
    TakeoverCondition,
    TakeoverEvent,
    create_takeover_manager
)

# Adaptive tick
from senti_os.core.faza29.adaptive_tick import (
    AdaptiveTickEngine,
    TickConfig,
    create_adaptive_tick_engine
)

# Feedback loop
from senti_os.core.faza29.feedback_loop import (
    FeedbackLoop,
    FeedbackConfig,
    FeedbackState,
    create_feedback_loop
)

# Integration layer
from senti_os.core.faza29.integration_layer import (
    IntegrationLayer,
    create_integration_layer
)

# Event hooks
from senti_os.core.faza29.event_hooks import (
    EventHooks,
    FazaEvent,
    EventType,
    create_event_hooks
)


__all__ = [
    # Main governance engine
    "GovernanceController",
    "get_governance_controller",
    "create_governance_controller",

    # Governance rules
    "GovernanceRuleEngine",
    "GovernanceRule",
    "RuleChain",
    "GovernanceDecision",
    "RuleLayer",
    "RulePriority",
    "create_governance_rule_engine",

    # Risk model
    "RiskModel",
    "RiskBreakdown",
    "RiskFactor",
    "compute_risk",
    "create_risk_model",

    # Override system
    "OverrideSystem",
    "Override",
    "OverrideType",
    "OverrideReason",
    "create_override_system",

    # Takeover manager
    "TakeoverManager",
    "TakeoverState",
    "TakeoverReason",
    "TakeoverCondition",
    "TakeoverEvent",
    "create_takeover_manager",

    # Adaptive tick
    "AdaptiveTickEngine",
    "TickConfig",
    "create_adaptive_tick_engine",

    # Feedback loop
    "FeedbackLoop",
    "FeedbackConfig",
    "FeedbackState",
    "create_feedback_loop",

    # Integration layer
    "IntegrationLayer",
    "create_integration_layer",

    # Event hooks
    "EventHooks",
    "FazaEvent",
    "EventType",
    "create_event_hooks",
]


__version__ = "1.0.0"
__author__ = "Senti System - FAZA 29 Enterprise Edition"
__description__ = "FAZA 29 - Enterprise Governance Engine"

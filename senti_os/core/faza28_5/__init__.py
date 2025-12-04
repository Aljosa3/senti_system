"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)

Enterprise meta-layer for FAZA 28 Agent Execution Loop.

Provides:
- Agent scoring and performance tracking
- Meta-policy framework (safety, load-balance, conflict resolution)
- Anomaly detection (rule-based, statistical, threshold)
- Stability engine (feedback loops, deadlocks, runaway agents)
- Strategy adapter (dynamic system behavior adaptation)
- Oversight agent (meta-agent monitoring all agents)
- Integration layer (deep FAZA 28 integration)

Architecture:
    Agent Scorer        - Performance, reliability, cooperation, stability scoring
    Policy Manager      - Pluggable safety and operational policies
    Anomaly Detector    - Multi-method anomaly detection
    Stability Engine    - Multi-agent stability analysis
    Strategy Adapter    - Dynamic system adaptation
    Oversight Agent     - Main meta-agent coordinator
    Integration Layer   - FAZA 28 integration and public API

Usage:
    from senti_os.core.faza28_5 import (
        get_meta_layer,
        get_agent_scores,
        get_system_risk,
        get_policy_status
    )

    # Initialize meta-layer
    meta_layer = get_meta_layer()
    meta_layer.initialize()

    # Attach to FAZA 28 (optional)
    from senti_os.core.faza28 import get_event_bus, get_state_context
    meta_layer.attach_to_faza28(
        event_bus=get_event_bus(),
        state_context=get_state_context()
    )

    # Start monitoring
    await meta_layer.start()

    # Get meta-evaluation data
    scores = get_agent_scores()
    risk = get_system_risk()
    report = meta_layer.get_meta_report()

Enterprise Features:
- Real-time agent performance monitoring
- Automatic anomaly detection
- Policy-driven safety enforcement
- Dynamic system adaptation
- Comprehensive meta-reporting
"""

# Agent Scorer
from senti_os.core.faza28_5.agent_scorer import (
    AgentScorer,
    AgentScore,
    AgentMetrics,
    get_agent_scorer,
    create_agent_scorer
)

# Meta Policies
from senti_os.core.faza28_5.meta_policies import (
    Policy,
    PolicyType,
    PolicyAction,
    PolicyDecision,
    PolicyManager,
    KillSwitchPolicy,
    IsolationPolicy,
    LoadBalancePolicy,
    OverloadPolicy,
    ConflictResolutionPolicy,
    EscalationPolicy,
    FailoverPolicy,
    get_policy_manager,
    create_policy_manager
)

# Anomaly Detector
from senti_os.core.faza28_5.anomaly_detector import (
    AnomalyDetector,
    Anomaly,
    AnomalyType,
    AnomalySeverity,
    get_anomaly_detector,
    create_anomaly_detector
)

# Stability Engine
from senti_os.core.faza28_5.stability_engine import (
    StabilityEngine,
    StabilityReport,
    StabilityIssue,
    RecoveryAction,
    get_stability_engine,
    create_stability_engine
)

# Strategy Adapter
from senti_os.core.faza28_5.strategy_adapter import (
    StrategyAdapter,
    SystemStrategy,
    AdaptationAction,
    get_strategy_adapter,
    create_strategy_adapter
)

# Oversight Agent
from senti_os.core.faza28_5.oversight_agent import (
    OversightAgent,
    get_oversight_agent,
    create_oversight_agent
)

# Integration Layer (Main API)
from senti_os.core.faza28_5.integration_layer import (
    MetaEvaluationLayer,
    get_meta_layer,
    create_meta_layer,
    get_agent_scores,
    get_system_risk,
    get_policy_status,
    get_stability_summary
)


__all__ = [
    # Agent Scorer
    "AgentScorer",
    "AgentScore",
    "AgentMetrics",
    "get_agent_scorer",
    "create_agent_scorer",

    # Meta Policies
    "Policy",
    "PolicyType",
    "PolicyAction",
    "PolicyDecision",
    "PolicyManager",
    "KillSwitchPolicy",
    "IsolationPolicy",
    "LoadBalancePolicy",
    "OverloadPolicy",
    "ConflictResolutionPolicy",
    "EscalationPolicy",
    "FailoverPolicy",
    "get_policy_manager",
    "create_policy_manager",

    # Anomaly Detector
    "AnomalyDetector",
    "Anomaly",
    "AnomalyType",
    "AnomalySeverity",
    "get_anomaly_detector",
    "create_anomaly_detector",

    # Stability Engine
    "StabilityEngine",
    "StabilityReport",
    "StabilityIssue",
    "RecoveryAction",
    "get_stability_engine",
    "create_stability_engine",

    # Strategy Adapter
    "StrategyAdapter",
    "SystemStrategy",
    "AdaptationAction",
    "get_strategy_adapter",
    "create_strategy_adapter",

    # Oversight Agent
    "OversightAgent",
    "get_oversight_agent",
    "create_oversight_agent",

    # Integration Layer (Primary API)
    "MetaEvaluationLayer",
    "get_meta_layer",
    "create_meta_layer",
    "get_agent_scores",
    "get_system_risk",
    "get_policy_status",
    "get_stability_summary",
]


__version__ = "1.0.0"
__author__ = "Senti System - Enterprise Edition"
__description__ = "FAZA 28.5 - Meta-Agent Oversight Layer (Enterprise Edition)"

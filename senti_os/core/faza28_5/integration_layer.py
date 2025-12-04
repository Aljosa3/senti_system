"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Integration Layer

Deep core integration with FAZA 28:
- Hook into FAZA 28 event_bus
- Hook into FAZA 28 scheduler
- Hook into FAZA 28 state_context
- Orchestrate all FAZA 28.5 submodules
- Provide meta-evaluation API

This is the main entry point for FAZA 28.5.
"""

import logging
from typing import Dict, List, Optional, Any
import asyncio

# FAZA 28.5 components
from .agent_scorer import AgentScorer, get_agent_scorer
from .meta_policies import PolicyManager, get_policy_manager
from .anomaly_detector import AnomalyDetector, get_anomaly_detector
from .stability_engine import StabilityEngine, get_stability_engine
from .strategy_adapter import StrategyAdapter, get_strategy_adapter
from .oversight_agent import OversightAgent, get_oversight_agent

logger = logging.getLogger(__name__)


class MetaEvaluationLayer:
    """
    Enterprise meta-evaluation layer.

    Provides integration between FAZA 28 and FAZA 28.5.
    Orchestrates all meta-oversight subsystems.

    Main API for accessing meta-layer functionality.
    """

    def __init__(
        self,
        auto_initialize: bool = True
    ):
        """
        Initialize meta-evaluation layer.

        Args:
            auto_initialize: Automatically initialize all subsystems
        """
        self.auto_initialize = auto_initialize

        # FAZA 28 components (set by attach_to_faza28)
        self.event_bus = None
        self.scheduler = None
        self.state_context = None
        self.agent_manager = None

        # FAZA 28.5 subsystems
        self.scorer: Optional[AgentScorer] = None
        self.policy_manager: Optional[PolicyManager] = None
        self.anomaly_detector: Optional[AnomalyDetector] = None
        self.stability_engine: Optional[StabilityEngine] = None
        self.strategy_adapter: Optional[StrategyAdapter] = None
        self.oversight_agent: Optional[OversightAgent] = None

        # State
        self._initialized = False
        self._attached = False

        logger.info("MetaEvaluationLayer created")

        if self.auto_initialize:
            self.initialize()

    def initialize(self) -> None:
        """
        Initialize all FAZA 28.5 subsystems.

        Creates singleton instances of all components.
        """
        if self._initialized:
            logger.warning("MetaEvaluationLayer already initialized")
            return

        logger.info("Initializing FAZA 28.5 subsystems...")

        # Initialize components
        self.scorer = get_agent_scorer()
        self.policy_manager = get_policy_manager()
        self.anomaly_detector = get_anomaly_detector()
        self.stability_engine = get_stability_engine()
        self.strategy_adapter = get_strategy_adapter()
        self.oversight_agent = get_oversight_agent()

        # Wire oversight agent to subsystems
        self.oversight_agent.scorer = self.scorer
        self.oversight_agent.anomaly_detector = self.anomaly_detector
        self.oversight_agent.stability_engine = self.stability_engine
        self.oversight_agent.policy_manager = self.policy_manager
        self.oversight_agent.strategy_adapter = self.strategy_adapter

        self._initialized = True
        logger.info("FAZA 28.5 subsystems initialized")

    def attach_to_faza28(
        self,
        event_bus: Any = None,
        scheduler: Any = None,
        state_context: Any = None,
        agent_manager: Any = None
    ) -> None:
        """
        Attach to FAZA 28 components.

        Args:
            event_bus: FAZA 28 EventBus instance
            scheduler: FAZA 28 Scheduler instance
            state_context: FAZA 28 StateContext instance
            agent_manager: FAZA 28 AgentManager instance

        TODO: Auto-discover FAZA 28 components if not provided
        TODO: Verify component compatibility
        """
        if self._attached:
            logger.warning("MetaEvaluationLayer already attached")
            return

        logger.info("Attaching to FAZA 28...")

        self.event_bus = event_bus
        self.scheduler = scheduler
        self.state_context = state_context
        self.agent_manager = agent_manager

        # Subscribe oversight agent to all events
        if self.event_bus and self.oversight_agent:
            # Subscribe to ALL event types
            # In production, would subscribe to specific event types
            logger.info("Subscribing oversight agent to FAZA 28 event bus")
            # TODO: Implement actual subscription
            # self.event_bus.subscribe("*", "oversight_agent", self.oversight_agent.on_event)

        # Store meta-layer reference in state_context
        if self.state_context:
            self.state_context.set("meta_evaluation_layer", self)
            self.state_context.set("faza28_5_active", True)

        self._attached = True
        logger.info("FAZA 28.5 attached to FAZA 28")

    def register_as_agent(self, agent_manager: Any = None) -> None:
        """
        Register oversight agent with FAZA 28 AgentManager.

        Args:
            agent_manager: FAZA 28 AgentManager (uses stored if None)

        TODO: Implement AgentBase interface for oversight_agent
        """
        if agent_manager is None:
            agent_manager = self.agent_manager

        if not agent_manager:
            logger.warning("Cannot register oversight agent: no agent_manager")
            return

        logger.info("Registering oversight agent with FAZA 28")
        # TODO: Implement registration
        # agent_manager.register(self.oversight_agent)

    async def start(self, context: Any = None) -> None:
        """
        Start meta-evaluation layer.

        Args:
            context: StateContext from FAZA 28

        Starts oversight agent and begins monitoring.
        """
        if not self._initialized:
            self.initialize()

        logger.info("Starting FAZA 28.5 Meta-Evaluation Layer...")

        if context is None:
            context = self.state_context

        if self.oversight_agent:
            await self.oversight_agent.on_start(context)

        logger.info("FAZA 28.5 Meta-Evaluation Layer started")

    async def shutdown(self, context: Any = None) -> None:
        """
        Shutdown meta-evaluation layer.

        Args:
            context: StateContext from FAZA 28
        """
        logger.info("Shutting down FAZA 28.5...")

        if context is None:
            context = self.state_context

        if self.oversight_agent:
            await self.oversight_agent.on_shutdown(context)

        if self.state_context:
            self.state_context.set("faza28_5_active", False)

        logger.info("FAZA 28.5 shutdown complete")

    # ============ Meta-Evaluation API ============

    def get_agent_scores(self) -> Dict[str, Any]:
        """
        Get scores for all agents.

        Returns:
            Dictionary of agent_name -> AgentScore

        API endpoint for external access.
        """
        if not self.scorer:
            return {}

        scores = self.scorer.get_all_scores()
        return {name: score.__dict__ for name, score in scores.items()}

    def get_system_risk(self) -> Dict[str, Any]:
        """
        Get system-wide risk assessment.

        Returns:
            Dictionary with risk metrics

        Combines anomaly and stability data.
        """
        risk = {
            "overall_risk": "low",
            "risk_score": 0.0,
            "contributing_factors": []
        }

        # Anomalies
        if self.anomaly_detector:
            anomaly_summary = self.anomaly_detector.get_anomaly_summary()
            critical_anomalies = anomaly_summary.get("anomalies_by_severity", {}).get("CRITICAL", 0)

            if critical_anomalies > 0:
                risk["risk_score"] += 0.3
                risk["contributing_factors"].append(f"{critical_anomalies} critical anomalies")

        # Stability
        if self.stability_engine:
            stability_summary = self.stability_engine.get_stability_summary()
            critical_issues = stability_summary.get("critical_issues", 0)

            if critical_issues > 0:
                risk["risk_score"] += 0.4
                risk["contributing_factors"].append(f"{critical_issues} critical stability issues")

        # Overall assessment
        if risk["risk_score"] > 0.7:
            risk["overall_risk"] = "critical"
        elif risk["risk_score"] > 0.4:
            risk["overall_risk"] = "high"
        elif risk["risk_score"] > 0.2:
            risk["overall_risk"] = "medium"

        return risk

    def get_policy_status(self) -> Dict[str, Any]:
        """
        Get policy manager status.

        Returns:
            Dictionary with policy statistics
        """
        if not self.policy_manager:
            return {}

        return self.policy_manager.get_stats()

    def get_stability_summary(self) -> Dict[str, Any]:
        """
        Get stability engine summary.

        Returns:
            Dictionary with stability statistics
        """
        if not self.stability_engine:
            return {}

        return self.stability_engine.get_stability_summary()

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """
        Get strategy adapter summary.

        Returns:
            Dictionary with adaptation statistics
        """
        if not self.strategy_adapter:
            return {}

        return self.strategy_adapter.get_adaptation_summary()

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """
        Get anomaly detector summary.

        Returns:
            Dictionary with anomaly statistics
        """
        if not self.anomaly_detector:
            return {}

        return self.anomaly_detector.get_anomaly_summary()

    def get_meta_report(self) -> Optional[Dict[str, Any]]:
        """
        Get latest system meta-report.

        Returns:
            Latest meta-report or None
        """
        if not self.oversight_agent:
            return None

        return self.oversight_agent.get_latest_report()

    def get_complete_status(self) -> Dict[str, Any]:
        """
        Get complete FAZA 28.5 status.

        Returns:
            Comprehensive status dictionary
        """
        return {
            "initialized": self._initialized,
            "attached": self._attached,
            "agent_scores": self.get_agent_scores(),
            "system_risk": self.get_system_risk(),
            "policy_status": self.get_policy_status(),
            "stability_summary": self.get_stability_summary(),
            "adaptation_summary": self.get_adaptation_summary(),
            "anomaly_summary": self.get_anomaly_summary(),
            "meta_report": self.get_meta_report(),
            "oversight_stats": self.oversight_agent.get_stats() if self.oversight_agent else {}
        }

    def __repr__(self) -> str:
        return f"<MetaEvaluationLayer: initialized={self._initialized}, attached={self._attached}>"


# Singleton instance
_meta_evaluation_layer_instance: Optional[MetaEvaluationLayer] = None


def get_meta_layer() -> MetaEvaluationLayer:
    """
    Get singleton MetaEvaluationLayer instance.

    Returns:
        Global MetaEvaluationLayer instance
    """
    global _meta_evaluation_layer_instance
    if _meta_evaluation_layer_instance is None:
        _meta_evaluation_layer_instance = MetaEvaluationLayer()
    return _meta_evaluation_layer_instance


def create_meta_layer(**kwargs) -> MetaEvaluationLayer:
    """
    Factory function: create new MetaEvaluationLayer instance.

    Args:
        **kwargs: Arguments passed to MetaEvaluationLayer constructor

    Returns:
        New MetaEvaluationLayer instance
    """
    return MetaEvaluationLayer(**kwargs)


# Convenience functions for quick access

def get_agent_scores() -> Dict[str, Any]:
    """Get agent scores from meta-layer"""
    return get_meta_layer().get_agent_scores()


def get_system_risk() -> Dict[str, Any]:
    """Get system risk assessment from meta-layer"""
    return get_meta_layer().get_system_risk()


def get_policy_status() -> Dict[str, Any]:
    """Get policy status from meta-layer"""
    return get_meta_layer().get_policy_status()


def get_stability_summary() -> Dict[str, Any]:
    """Get stability summary from meta-layer"""
    return get_meta_layer().get_stability_summary()

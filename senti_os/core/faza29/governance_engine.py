"""
FAZA 29 – Enterprise Governance Engine
Main Governance Controller

Hybrid governance model that integrates:
- Governance rules engine
- Risk model
- Override system
- Takeover manager
- Adaptive tick control
- Feedback loop
- Integration layer

Provides unified governance API for the entire Senti OS system.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from senti_os.core.faza29.governance_rules import (
    GovernanceRuleEngine, GovernanceDecision, create_governance_rule_engine
)
from senti_os.core.faza29.risk_model import RiskModel, create_risk_model
from senti_os.core.faza29.override_system import OverrideSystem, create_override_system
from senti_os.core.faza29.takeover_manager import TakeoverManager, TakeoverState, create_takeover_manager
from senti_os.core.faza29.adaptive_tick import AdaptiveTickEngine, create_adaptive_tick_engine
from senti_os.core.faza29.feedback_loop import FeedbackLoop, create_feedback_loop
from senti_os.core.faza29.integration_layer import IntegrationLayer, create_integration_layer
from senti_os.core.faza29.event_hooks import EventHooks, create_event_hooks

logger = logging.getLogger(__name__)


class GovernanceController:
    """
    Main FAZA 29 governance controller.

    Hybrid governance model that coordinates all governance subsystems
    to provide comprehensive system oversight and control.
    """

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize governance controller.

        Args:
            event_bus: Optional FAZA 28 EventBus
        """
        # Initialize components
        self.rule_engine = create_governance_rule_engine()
        self.risk_model = create_risk_model()
        self.override_system = create_override_system(event_bus)
        self.takeover_manager = create_takeover_manager(event_bus)
        self.tick_engine = create_adaptive_tick_engine()
        self.feedback_loop = create_feedback_loop()
        self.integration = create_integration_layer()
        self.events = create_event_hooks(event_bus)

        # Attach event bus to integration
        if event_bus:
            self.integration.attach_faza28_event_bus(event_bus)

        # Controller state
        self.running = False
        self.governance_loop_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            "governance_cycles": 0,
            "decisions_made": 0,
            "overrides_active": 0,
            "takeovers": 0,
            "risk_assessments": 0
        }

        logger.info("FAZA 29 Governance Controller initialized")

    # ==================== Main Governance API ====================

    def evaluate_governance(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive governance evaluation.

        Args:
            context: Governance context (optional)

        Returns:
            Governance evaluation result
        """
        context = context or {}

        # Step 1: Check override system (ALWAYS FIRST)
        override_active = self.override_system.is_override_active()
        if override_active:
            active_override = self.override_system.get_active_override()
            decision = GovernanceDecision.OVERRIDE
            self.stats["overrides_active"] += 1

            result = {
                "decision": decision.value,
                "override_active": True,
                "override": active_override.to_dict() if active_override else None,
                "reason": "User override active (final authority)",
                "timestamp": datetime.now().isoformat()
            }

            # Emit event
            self.events.publish_governance_decision(decision.value, result)
            return result

        # Step 2: Gather metrics from all FAZA layers
        system_metrics = self._gather_system_metrics()
        agent_metrics = self._gather_agent_metrics()
        graph_metrics = self._gather_graph_metrics()

        # Step 3: Compute risk score
        risk_breakdown = self.risk_model.compute_risk(
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            graph_metrics=graph_metrics
        )
        self.stats["risk_assessments"] += 1

        # Emit risk event
        self.events.publish_risk_assessed(
            risk_breakdown.total_risk,
            risk_breakdown.to_dict()
        )

        # Step 4: Evaluate takeover conditions
        takeover_state = self.takeover_manager.evaluate(
            agent_metrics=agent_metrics,
            system_metrics=system_metrics,
            risk_score=risk_breakdown.total_risk
        )

        if takeover_state == TakeoverState.TAKEOVER:
            self.stats["takeovers"] += 1

        # Step 5: Update feedback loop
        stability_measurement = 1.0 - (risk_breakdown.total_risk / 100.0)
        corrective_signal, smoothing_factor, damping_coeff = self.feedback_loop.update(
            measurement=stability_measurement,
            dt=1.0
        )

        # Step 6: Build governance context
        governance_context = {
            "risk_score": risk_breakdown.total_risk,
            "agent_score": agent_metrics.get("agent_performance", 0.5),
            "system_load": system_metrics.get("cpu_usage", 0.0),
            "stability_score": stability_measurement,
            "user_override": override_active,
            "policy_violation": agent_metrics.get("governance_violations", 0.0) > 0.5,
            "anomaly_detected": agent_metrics.get("anomaly_rate", 0.0) > 0.4,
            "takeover_active": takeover_state == TakeoverState.TAKEOVER
        }

        # Step 7: Evaluate governance rules
        decision, decision_context = self.rule_engine.evaluate(governance_context)
        self.stats["decisions_made"] += 1

        # Step 8: Build result
        result = {
            "decision": decision.value,
            "override_active": False,
            "risk_score": risk_breakdown.total_risk,
            "risk_level": self.risk_model.get_risk_level(risk_breakdown.total_risk),
            "takeover_state": takeover_state.value,
            "stability_score": round(stability_measurement, 3),
            "corrective_signal": round(corrective_signal, 3),
            "smoothing_factor": round(smoothing_factor, 3),
            "damping_coefficient": round(damping_coeff, 3),
            "decision_context": decision_context,
            "critical_factors": risk_breakdown.critical_factors,
            "timestamp": datetime.now().isoformat()
        }

        # Emit governance event
        self.events.publish_governance_decision(decision.value, result)

        # Trigger integration callbacks
        self.integration.trigger_governance_callbacks(decision.value, result)

        return result

    def _gather_system_metrics(self) -> Dict[str, Any]:
        """Gather system-level metrics"""
        metrics = self.integration.get_orchestrator_metrics()

        # Add default values if not available
        if "cpu_usage" not in metrics:
            metrics["cpu_usage"] = 0.0
        if "memory_usage" not in metrics:
            metrics["memory_usage"] = 0.0
        if "error_rate" not in metrics:
            metrics["error_rate"] = 0.0

        return metrics

    def _gather_agent_metrics(self) -> Dict[str, Any]:
        """Gather agent-level metrics"""
        metrics = self.integration.get_meta_metrics()

        # Add default values
        if "agent_performance" not in metrics:
            metrics["agent_performance"] = 0.8
        if "agent_stability" not in metrics:
            metrics["agent_stability"] = 0.8
        if "anomaly_rate" not in metrics:
            metrics["anomaly_rate"] = 0.0

        return metrics

    def _gather_graph_metrics(self) -> Dict[str, Any]:
        """Gather graph-level metrics"""
        metrics = self.integration.get_graph_metrics()

        # Add default values
        if "graph_complexity" not in metrics:
            metrics["graph_complexity"] = 0.5
        if "parallelization_index" not in metrics:
            metrics["parallelization_index"] = 0.5

        return metrics

    # ==================== Governance Loop ====================

    async def start(self) -> None:
        """Start governance loop"""
        if self.running:
            logger.warning("Governance controller already running")
            return

        self.running = True
        self.governance_loop_task = asyncio.create_task(self._governance_loop())

        logger.info("FAZA 29 Governance Controller started")
        self.events.publish(FazaEvent(
            event_type=EventType.SYSTEM_STARTED,
            source="governance_controller",
            severity=7
        ))

    async def stop(self) -> None:
        """Stop governance loop"""
        if not self.running:
            return

        self.running = False

        if self.governance_loop_task:
            self.governance_loop_task.cancel()
            try:
                await self.governance_loop_task
            except asyncio.CancelledError:
                pass

        logger.info("FAZA 29 Governance Controller stopped")
        self.events.publish(FazaEvent(
            event_type=EventType.SYSTEM_STOPPED,
            source="governance_controller",
            severity=7
        ))

    async def _governance_loop(self) -> None:
        """Main governance loop"""
        logger.info("Governance loop started")

        while self.running:
            try:
                # Perform governance evaluation
                result = self.evaluate_governance()

                # Update tick frequency based on conditions
                self.tick_engine.update(
                    system_load=result.get("risk_score", 0.0) / 100.0,
                    risk_score=result.get("risk_score", 0.0),
                    warning_level=0.5 if result.get("takeover_state") == "warning" else 0.0,
                    override_active=result.get("override_active", False)
                )

                # Update statistics
                self.stats["governance_cycles"] += 1

                # Sleep for tick interval
                tick_interval = self.tick_engine.get_tick_interval()
                await asyncio.sleep(tick_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Governance loop error: {e}")
                await asyncio.sleep(1.0)  # Error backoff

        logger.info("Governance loop stopped")

    # ==================== Component Access ====================

    def get_rule_engine(self) -> GovernanceRuleEngine:
        """Get governance rule engine"""
        return self.rule_engine

    def get_risk_model(self) -> RiskModel:
        """Get risk model"""
        return self.risk_model

    def get_override_system(self) -> OverrideSystem:
        """Get override system"""
        return self.override_system

    def get_takeover_manager(self) -> TakeoverManager:
        """Get takeover manager"""
        return self.takeover_manager

    def get_tick_engine(self) -> AdaptiveTickEngine:
        """Get adaptive tick engine"""
        return self.tick_engine

    def get_feedback_loop(self) -> FeedbackLoop:
        """Get feedback loop"""
        return self.feedback_loop

    def get_integration_layer(self) -> IntegrationLayer:
        """Get integration layer"""
        return self.integration

    # ==================== Status and Metrics ====================

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive governance status"""
        return {
            "running": self.running,
            "override_active": self.override_system.is_override_active(),
            "takeover_state": self.takeover_manager.get_state().value,
            "takeover_score": round(self.takeover_manager.get_takeover_score(), 3),
            "current_tick_hz": round(self.tick_engine.get_current_hz(), 2),
            "feedback_stable": self.feedback_loop.is_stable(),
            "integrations": self.integration.get_integration_status(),
            "timestamp": datetime.now().isoformat()
        }

    def get_risk(self) -> Dict[str, Any]:
        """Get current risk assessment"""
        system_metrics = self._gather_system_metrics()
        agent_metrics = self._gather_agent_metrics()
        graph_metrics = self._gather_graph_metrics()

        risk_breakdown = self.risk_model.compute_risk(
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            graph_metrics=graph_metrics
        )

        return risk_breakdown.to_dict()

    def get_tick_rate(self) -> float:
        """Get current tick rate (Hz)"""
        return self.tick_engine.get_current_hz()

    def get_takeover_state(self) -> str:
        """Get current takeover state"""
        return self.takeover_manager.get_state().value

    def get_governance_decision(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Get governance decision for context"""
        result = self.evaluate_governance(context)
        return result["decision"]

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            "controller": self.stats,
            "rule_engine": self.rule_engine.get_statistics(),
            "risk_model": self.risk_model.get_statistics(),
            "override_system": self.override_system.get_statistics(),
            "takeover_manager": self.takeover_manager.get_statistics(),
            "tick_engine": self.tick_engine.get_statistics(),
            "feedback_loop": self.feedback_loop.get_statistics(),
            "integration": self.integration.get_statistics(),
            "events": self.events.get_statistics()
        }


# Global controller instance
_governance_controller: Optional[GovernanceController] = None


def get_governance_controller(event_bus: Optional[Any] = None) -> GovernanceController:
    """
    Get or create global governance controller instance.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        GovernanceController instance
    """
    global _governance_controller

    if _governance_controller is None:
        _governance_controller = GovernanceController(event_bus)

    return _governance_controller


def create_governance_controller(event_bus: Optional[Any] = None) -> GovernanceController:
    """
    Factory function to create new governance controller.

    Args:
        event_bus: Optional FAZA 28 EventBus

    Returns:
        GovernanceController instance
    """
    return GovernanceController(event_bus)


# Import EventType and FazaEvent for loop
from senti_os.core.faza29.event_hooks import EventType, FazaEvent

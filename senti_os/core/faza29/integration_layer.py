"""
FAZA 29 – Enterprise Governance Engine
Integration Layer

Connects FAZA 29 to other FAZA layers:
- FAZA 28: Event bus integration
- FAZA 25: Orchestrator hooks
- FAZA 27/27.5: Graph optimizer hooks
- FAZA 28.5: Meta-layer integration

All hooks are non-intrusive and optional.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrationLayer:
    """
    FAZA 29 integration layer.

    Provides non-intrusive hooks to connect FAZA 29 governance
    with other FAZA system layers.
    """

    def __init__(self):
        """Initialize integration layer"""
        # Component references
        self.faza28_event_bus: Optional[Any] = None
        self.faza25_orchestrator: Optional[Any] = None
        self.faza27_optimizer: Optional[Any] = None
        self.faza28_5_meta_layer: Optional[Any] = None

        # Integration status
        self.integrations = {
            "faza28": False,
            "faza25": False,
            "faza27": False,
            "faza28_5": False
        }

        # Event callbacks
        self.governance_callbacks: List[Callable] = []
        self.takeover_callbacks: List[Callable] = []
        self.override_callbacks: List[Callable] = []

        # Statistics
        self.stats = {
            "faza28_events_sent": 0,
            "faza25_hooks_called": 0,
            "faza27_queries": 0,
            "faza28_5_queries": 0,
            "governance_events": 0,
            "takeover_events": 0,
            "override_events": 0
        }

    # ==================== FAZA 28 Integration ====================

    def attach_faza28_event_bus(self, event_bus: Any) -> None:
        """
        Attach to FAZA 28 EventBus.

        Args:
            event_bus: FAZA 28 EventBus instance
        """
        self.faza28_event_bus = event_bus
        self.integrations["faza28"] = True
        logger.info("FAZA 28 EventBus attached")

    def detach_faza28_event_bus(self) -> None:
        """Detach from FAZA 28 EventBus"""
        self.faza28_event_bus = None
        self.integrations["faza28"] = False
        logger.info("FAZA 28 EventBus detached")

    def emit_governance_event(self, decision: str, context: Dict[str, Any]) -> None:
        """
        Emit governance event to FAZA 28.

        Args:
            decision: Governance decision
            context: Decision context
        """
        if not self.faza28_event_bus:
            return

        try:
            event = {
                "type": "faza29.governance.decision",
                "source": "faza29_governance",
                "data": {
                    "decision": decision,
                    "context": context
                },
                "timestamp": datetime.now()
            }
            self.faza28_event_bus.publish(event)
            self.stats["faza28_events_sent"] += 1
            self.stats["governance_events"] += 1
        except Exception as e:
            logger.error(f"Failed to emit governance event: {e}")

    def emit_takeover_event(self, state: str, reason: str) -> None:
        """
        Emit takeover event to FAZA 28.

        Args:
            state: Takeover state
            reason: Takeover reason
        """
        if not self.faza28_event_bus:
            return

        try:
            event = {
                "type": "faza29.takeover",
                "source": "faza29_takeover",
                "data": {
                    "state": state,
                    "reason": reason
                },
                "timestamp": datetime.now()
            }
            self.faza28_event_bus.publish(event)
            self.stats["faza28_events_sent"] += 1
            self.stats["takeover_events"] += 1
        except Exception as e:
            logger.error(f"Failed to emit takeover event: {e}")

    def emit_override_event(self, override_id: str, override_type: str) -> None:
        """
        Emit override event to FAZA 28.

        Args:
            override_id: Override identifier
            override_type: Override type
        """
        if not self.faza28_event_bus:
            return

        try:
            event = {
                "type": "faza29.override",
                "source": "faza29_override",
                "data": {
                    "override_id": override_id,
                    "override_type": override_type
                },
                "timestamp": datetime.now()
            }
            self.faza28_event_bus.publish(event)
            self.stats["faza28_events_sent"] += 1
            self.stats["override_events"] += 1
        except Exception as e:
            logger.error(f"Failed to emit override event: {e}")

    # ==================== FAZA 25 Integration ====================

    def attach_faza25_orchestrator(self, orchestrator: Any) -> None:
        """
        Attach to FAZA 25 Orchestrator.

        Args:
            orchestrator: FAZA 25 Orchestrator instance
        """
        self.faza25_orchestrator = orchestrator
        self.integrations["faza25"] = True
        logger.info("FAZA 25 Orchestrator attached")

    def detach_faza25_orchestrator(self) -> None:
        """Detach from FAZA 25 Orchestrator"""
        self.faza25_orchestrator = None
        self.integrations["faza25"] = False
        logger.info("FAZA 25 Orchestrator detached")

    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 25 Orchestrator.

        Returns:
            Orchestrator metrics or empty dict
        """
        if not self.faza25_orchestrator:
            return {}

        try:
            self.stats["faza25_hooks_called"] += 1

            # Try to get metrics from orchestrator
            if hasattr(self.faza25_orchestrator, 'get_metrics'):
                return self.faza25_orchestrator.get_metrics()

            # Fallback: estimate from task queue
            if hasattr(self.faza25_orchestrator, 'task_queue'):
                queue_size = len(self.faza25_orchestrator.task_queue)
                return {
                    "queue_size": queue_size,
                    "estimated_load": min(queue_size / 100.0, 1.0)
                }

            return {}

        except Exception as e:
            logger.error(f"Failed to get orchestrator metrics: {e}")
            return {}

    # ==================== FAZA 27/27.5 Integration ====================

    def attach_faza27_optimizer(self, optimizer: Any) -> None:
        """
        Attach to FAZA 27/27.5 Graph Optimizer.

        Args:
            optimizer: FAZA 27/27.5 Optimizer instance
        """
        self.faza27_optimizer = optimizer
        self.integrations["faza27"] = True
        logger.info("FAZA 27/27.5 Optimizer attached")

    def detach_faza27_optimizer(self) -> None:
        """Detach from FAZA 27/27.5 Optimizer"""
        self.faza27_optimizer = None
        self.integrations["faza27"] = False
        logger.info("FAZA 27/27.5 Optimizer detached")

    def get_graph_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 27/27.5 Graph Optimizer.

        Returns:
            Graph metrics or empty dict
        """
        if not self.faza27_optimizer:
            return {}

        try:
            self.stats["faza27_queries"] += 1

            # Try to get graph health metrics
            if hasattr(self.faza27_optimizer, 'get_health_metrics'):
                return self.faza27_optimizer.get_health_metrics()

            # Try to get analyzer
            if hasattr(self.faza27_optimizer, 'analyzer'):
                analyzer = self.faza27_optimizer.analyzer
                if hasattr(analyzer, 'calculate_graph_health'):
                    return analyzer.calculate_graph_health()

            return {}

        except Exception as e:
            logger.error(f"Failed to get graph metrics: {e}")
            return {}

    # ==================== FAZA 28.5 Integration ====================

    def attach_faza28_5_meta_layer(self, meta_layer: Any) -> None:
        """
        Attach to FAZA 28.5 Meta-Layer.

        Args:
            meta_layer: FAZA 28.5 Meta-Layer instance
        """
        self.faza28_5_meta_layer = meta_layer
        self.integrations["faza28_5"] = True
        logger.info("FAZA 28.5 Meta-Layer attached")

    def detach_faza28_5_meta_layer(self) -> None:
        """Detach from FAZA 28.5 Meta-Layer"""
        self.faza28_5_meta_layer = None
        self.integrations["faza28_5"] = False
        logger.info("FAZA 28.5 Meta-Layer detached")

    def get_meta_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 28.5 Meta-Layer.

        Returns:
            Meta-layer metrics or empty dict
        """
        if not self.faza28_5_meta_layer:
            return {}

        try:
            self.stats["faza28_5_queries"] += 1

            # Try to get agent scores
            if hasattr(self.faza28_5_meta_layer, 'get_agent_scores'):
                return self.faza28_5_meta_layer.get_agent_scores()

            # Try to get system risk
            if hasattr(self.faza28_5_meta_layer, 'get_system_risk'):
                return self.faza28_5_meta_layer.get_system_risk()

            return {}

        except Exception as e:
            logger.error(f"Failed to get meta metrics: {e}")
            return {}

    def get_stability_metrics(self) -> Dict[str, Any]:
        """
        Get stability metrics from FAZA 28.5.

        Returns:
            Stability metrics or empty dict
        """
        if not self.faza28_5_meta_layer:
            return {}

        try:
            if hasattr(self.faza28_5_meta_layer, 'get_stability_summary'):
                return self.faza28_5_meta_layer.get_stability_summary()

            return {}

        except Exception as e:
            logger.error(f"Failed to get stability metrics: {e}")
            return {}

    # ==================== Callback Management ====================

    def register_governance_callback(self, callback: Callable) -> None:
        """Register callback for governance events"""
        self.governance_callbacks.append(callback)

    def register_takeover_callback(self, callback: Callable) -> None:
        """Register callback for takeover events"""
        self.takeover_callbacks.append(callback)

    def register_override_callback(self, callback: Callable) -> None:
        """Register callback for override events"""
        self.override_callbacks.append(callback)

    def trigger_governance_callbacks(self, decision: str, context: Dict[str, Any]) -> None:
        """Trigger governance callbacks"""
        for callback in self.governance_callbacks:
            try:
                callback(decision, context)
            except Exception as e:
                logger.error(f"Governance callback error: {e}")

    def trigger_takeover_callbacks(self, state: str, reason: str) -> None:
        """Trigger takeover callbacks"""
        for callback in self.takeover_callbacks:
            try:
                callback(state, reason)
            except Exception as e:
                logger.error(f"Takeover callback error: {e}")

    def trigger_override_callbacks(self, override_id: str, override_type: str) -> None:
        """Trigger override callbacks"""
        for callback in self.override_callbacks:
            try:
                callback(override_id, override_type)
            except Exception as e:
                logger.error(f"Override callback error: {e}")

    # ==================== Status and Statistics ====================

    def get_integration_status(self) -> Dict[str, bool]:
        """Get integration status"""
        return self.integrations.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            "faza28_events_sent": self.stats["faza28_events_sent"],
            "faza25_hooks_called": self.stats["faza25_hooks_called"],
            "faza27_queries": self.stats["faza27_queries"],
            "faza28_5_queries": self.stats["faza28_5_queries"],
            "governance_events": self.stats["governance_events"],
            "takeover_events": self.stats["takeover_events"],
            "override_events": self.stats["override_events"],
            "total_callbacks": (len(self.governance_callbacks) +
                              len(self.takeover_callbacks) +
                              len(self.override_callbacks))
        }

    def is_fully_integrated(self) -> bool:
        """Check if all integrations are active"""
        return all(self.integrations.values())


def create_integration_layer() -> IntegrationLayer:
    """
    Factory function to create IntegrationLayer instance.

    Returns:
        IntegrationLayer instance
    """
    return IntegrationLayer()

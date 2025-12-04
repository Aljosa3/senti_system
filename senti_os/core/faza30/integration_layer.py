"""
FAZA 30 – Integration Layer

Non-intrusive integration with all FAZA layers.

Provides:
- FAZA 25 (Orchestrator) integration
- FAZA 27/27.5 (Task Graph) integration
- FAZA 28 (Agent Loop) integration
- FAZA 28.5 (Meta Layer) integration
- FAZA 29 (Governance) integration
- Metric collection from all layers
- Event notifications

Architecture:
    IntegrationLayer - Main integration coordinator
    Integration points for each FAZA layer

Usage:
    from senti_os.core.faza30.integration_layer import IntegrationLayer

    layer = IntegrationLayer(
        faza25_orchestrator=orchestrator,
        faza27_task_graph=task_graph,
        faza28_agent_loop=agent_loop,
        faza28_5_meta_layer=meta_layer,
        faza29_governance=governance
    )

    metrics = layer.get_all_metrics()
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime


class IntegrationLayer:
    """
    Integration layer for all FAZA phases.

    Features:
    - Non-intrusive integration (other layers work without FAZA 30)
    - Metric collection from all layers
    - Optional integration (graceful degradation)
    - Callback system for repair actions
    - Integration health monitoring

    Integrates with:
    - FAZA 25: Orchestrator (task queue, scheduler)
    - FAZA 27/27.5: Task Graph (topology, optimization)
    - FAZA 28: Agent Loop (agents, execution)
    - FAZA 28.5: Meta Layer (stability, policies)
    - FAZA 29: Governance (risk, rules, overrides)
    """

    def __init__(
        self,
        faza25_orchestrator: Optional[Any] = None,
        faza27_task_graph: Optional[Any] = None,
        faza27_5_optimizer: Optional[Any] = None,
        faza28_agent_loop: Optional[Any] = None,
        faza28_5_meta_layer: Optional[Any] = None,
        faza29_governance: Optional[Any] = None,
        event_bus: Optional[Any] = None
    ):
        """
        Initialize integration layer.

        Args:
            faza25_orchestrator: Optional FAZA 25 Orchestrator
            faza27_task_graph: Optional FAZA 27 TaskGraph
            faza27_5_optimizer: Optional FAZA 27.5 Optimizer
            faza28_agent_loop: Optional FAZA 28 AgentLoop
            faza28_5_meta_layer: Optional FAZA 28.5 MetaLayer
            faza29_governance: Optional FAZA 29 Governance
            event_bus: Optional FAZA 28 EventBus
        """
        # Store references (all optional)
        self.faza25_orchestrator = faza25_orchestrator
        self.faza27_task_graph = faza27_task_graph
        self.faza27_5_optimizer = faza27_5_optimizer
        self.faza28_agent_loop = faza28_agent_loop
        self.faza28_5_meta_layer = faza28_5_meta_layer
        self.faza29_governance = faza29_governance
        self.event_bus = event_bus

        # Repair action callbacks
        self._repair_callbacks: Dict[str, List[Callable]] = {
            "graph_repair": [],
            "agent_repair": [],
            "scheduler_repair": [],
            "governance_repair": []
        }

        # Integration statistics
        self._stats = {
            "faza25_queries": 0,
            "faza27_queries": 0,
            "faza28_queries": 0,
            "faza28_5_queries": 0,
            "faza29_queries": 0,
            "total_metrics_collected": 0,
            "repair_actions_executed": 0
        }

    # ======================
    # FAZA 25 Integration
    # ======================

    def get_faza25_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 25 Orchestrator.

        Returns:
            Dict with orchestrator metrics
        """
        if not self.faza25_orchestrator:
            return {}

        self._stats["faza25_queries"] += 1

        try:
            metrics = {}

            # Queue metrics
            if hasattr(self.faza25_orchestrator, 'get_queue_size'):
                metrics['queue_size'] = self.faza25_orchestrator.get_queue_size()

            if hasattr(self.faza25_orchestrator, 'get_queue_metrics'):
                queue_metrics = self.faza25_orchestrator.get_queue_metrics()
                metrics.update(queue_metrics)

            # Scheduler metrics
            if hasattr(self.faza25_orchestrator, 'get_scheduler_stats'):
                scheduler_stats = self.faza25_orchestrator.get_scheduler_stats()
                metrics['scheduler_efficiency'] = scheduler_stats.get('efficiency', 1.0)
                metrics['task_success_rate'] = scheduler_stats.get('success_rate', 1.0)

            # System resource metrics
            if hasattr(self.faza25_orchestrator, 'get_resource_usage'):
                resources = self.faza25_orchestrator.get_resource_usage()
                metrics['cpu_usage'] = resources.get('cpu', 0.0)
                metrics['memory_usage'] = resources.get('memory', 0.0)

            self._stats["total_metrics_collected"] += len(metrics)
            return metrics

        except Exception:
            return {}

    def trigger_faza25_action(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Trigger action in FAZA 25.

        Args:
            action: Action to perform (e.g., "throttle", "reschedule")
            params: Action parameters

        Returns:
            True if action executed, False otherwise
        """
        if not self.faza25_orchestrator:
            return False

        try:
            if action == "throttle" and hasattr(self.faza25_orchestrator, 'throttle_queue'):
                self.faza25_orchestrator.throttle_queue(params.get('rate', 0.5))
                self._stats["repair_actions_executed"] += 1
                return True

            elif action == "reschedule" and hasattr(self.faza25_orchestrator, 'reschedule_task'):
                task_id = params.get('task_id')
                self.faza25_orchestrator.reschedule_task(task_id)
                self._stats["repair_actions_executed"] += 1
                return True

            return False

        except Exception:
            return False

    # ======================
    # FAZA 27 Integration
    # ======================

    def get_faza27_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 27 Task Graph.

        Returns:
            Dict with task graph metrics
        """
        metrics = {}

        # FAZA 27 (TaskGraph)
        if self.faza27_task_graph:
            self._stats["faza27_queries"] += 1

            try:
                if hasattr(self.faza27_task_graph, 'get_complexity'):
                    metrics['graph_complexity'] = self.faza27_task_graph.get_complexity()

                if hasattr(self.faza27_task_graph, 'detect_cycles'):
                    cycles = self.faza27_task_graph.detect_cycles()
                    metrics['cycle_count'] = len(cycles) if cycles else 0

                if hasattr(self.faza27_task_graph, 'get_stats'):
                    stats = self.faza27_task_graph.get_stats()
                    metrics.update(stats)

            except Exception:
                pass

        # FAZA 27.5 (Optimizer)
        if self.faza27_5_optimizer:
            try:
                if hasattr(self.faza27_5_optimizer, 'get_optimization_score'):
                    metrics['optimization_score'] = self.faza27_5_optimizer.get_optimization_score()

                if hasattr(self.faza27_5_optimizer, 'detect_bottlenecks'):
                    bottlenecks = self.faza27_5_optimizer.detect_bottlenecks()
                    metrics['bottleneck_detected'] = len(bottlenecks) > 0 if bottlenecks else False

            except Exception:
                pass

        self._stats["total_metrics_collected"] += len(metrics)
        return metrics

    def trigger_faza27_action(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Trigger action in FAZA 27.

        Args:
            action: Action to perform (e.g., "break_cycle", "optimize")
            params: Action parameters

        Returns:
            True if action executed, False otherwise
        """
        if not self.faza27_task_graph:
            return False

        try:
            if action == "break_cycle" and hasattr(self.faza27_task_graph, 'break_cycle'):
                cycle = params.get('cycle')
                self.faza27_task_graph.break_cycle(cycle)
                self._stats["repair_actions_executed"] += 1
                return True

            elif action == "optimize" and self.faza27_5_optimizer:
                if hasattr(self.faza27_5_optimizer, 'optimize'):
                    self.faza27_5_optimizer.optimize()
                    self._stats["repair_actions_executed"] += 1
                    return True

            return False

        except Exception:
            return False

    # ======================
    # FAZA 28 Integration
    # ======================

    def get_faza28_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 28 Agent Loop.

        Returns:
            Dict with agent loop metrics
        """
        if not self.faza28_agent_loop:
            return {}

        self._stats["faza28_queries"] += 1

        try:
            metrics = {}

            if hasattr(self.faza28_agent_loop, 'get_agent_stats'):
                agent_stats = self.faza28_agent_loop.get_agent_stats()
                metrics['agent_failure_rate'] = agent_stats.get('failure_rate', 0.0)
                metrics['agent_performance'] = agent_stats.get('performance', 1.0)
                metrics['cooperation_score'] = agent_stats.get('cooperation_score', 1.0)

            if hasattr(self.faza28_agent_loop, 'get_communication_health'):
                metrics['communication_health'] = self.faza28_agent_loop.get_communication_health()

            if hasattr(self.faza28_agent_loop, 'get_active_agents'):
                agents = self.faza28_agent_loop.get_active_agents()
                metrics['active_agent_count'] = len(agents) if agents else 0

            self._stats["total_metrics_collected"] += len(metrics)
            return metrics

        except Exception:
            return {}

    def trigger_faza28_action(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Trigger action in FAZA 28.

        Args:
            action: Action to perform (e.g., "restart_agent", "reset_cooperation")
            params: Action parameters

        Returns:
            True if action executed, False otherwise
        """
        if not self.faza28_agent_loop:
            return False

        try:
            if action == "restart_agent" and hasattr(self.faza28_agent_loop, 'restart_agent'):
                agent_id = params.get('agent_id')
                self.faza28_agent_loop.restart_agent(agent_id)
                self._stats["repair_actions_executed"] += 1
                return True

            elif action == "reset_cooperation" and hasattr(self.faza28_agent_loop, 'reset_cooperation'):
                self.faza28_agent_loop.reset_cooperation()
                self._stats["repair_actions_executed"] += 1
                return True

            return False

        except Exception:
            return False

    # ======================
    # FAZA 28.5 Integration
    # ======================

    def get_faza28_5_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 28.5 Meta Layer.

        Returns:
            Dict with meta layer metrics
        """
        if not self.faza28_5_meta_layer:
            return {}

        self._stats["faza28_5_queries"] += 1

        try:
            metrics = {}

            if hasattr(self.faza28_5_meta_layer, 'get_stability_score'):
                metrics['stability_score'] = self.faza28_5_meta_layer.get_stability_score()

            if hasattr(self.faza28_5_meta_layer, 'get_policy_effectiveness'):
                metrics['policy_effectiveness'] = self.faza28_5_meta_layer.get_policy_effectiveness()

            if hasattr(self.faza28_5_meta_layer, 'get_anomaly_count'):
                metrics['anomaly_count'] = self.faza28_5_meta_layer.get_anomaly_count()

            if hasattr(self.faza28_5_meta_layer, 'get_feedback_health'):
                metrics['feedback_health'] = self.faza28_5_meta_layer.get_feedback_health()

            self._stats["total_metrics_collected"] += len(metrics)
            return metrics

        except Exception:
            return {}

    # ======================
    # FAZA 29 Integration
    # ======================

    def get_faza29_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from FAZA 29 Governance.

        Returns:
            Dict with governance metrics
        """
        if not self.faza29_governance:
            return {}

        self._stats["faza29_queries"] += 1

        try:
            metrics = {}

            if hasattr(self.faza29_governance, 'get_risk'):
                risk = self.faza29_governance.get_risk()
                metrics['risk_score'] = risk.get('overall_score', 0) if isinstance(risk, dict) else 0

            if hasattr(self.faza29_governance, 'get_status'):
                status = self.faza29_governance.get_status()
                metrics['governance_violations'] = status.get('violations', 0) if isinstance(status, dict) else 0
                metrics['override_count'] = status.get('override_count', 0) if isinstance(status, dict) else 0

            if hasattr(self.faza29_governance, 'get_takeover_state'):
                takeover_state = self.faza29_governance.get_takeover_state()
                metrics['takeover_active'] = takeover_state != 'normal' if takeover_state else False

            self._stats["total_metrics_collected"] += len(metrics)
            return metrics

        except Exception:
            return {}

    # ======================
    # Unified Integration
    # ======================

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics from all FAZA layers.

        Returns:
            Dict with metrics organized by layer
        """
        return {
            "faza25": self.get_faza25_metrics(),
            "faza27": self.get_faza27_metrics(),
            "faza28": self.get_faza28_metrics(),
            "faza28_5": self.get_faza28_5_metrics(),
            "faza29": self.get_faza29_metrics()
        }

    def register_repair_callback(self, repair_type: str, callback: Callable) -> None:
        """
        Register callback for repair actions.

        Args:
            repair_type: Type of repair (graph_repair, agent_repair, etc.)
            callback: Callback function
        """
        if repair_type in self._repair_callbacks:
            self._repair_callbacks[repair_type].append(callback)

    def execute_repair_callbacks(self, repair_type: str, params: Dict[str, Any]) -> None:
        """
        Execute registered callbacks for repair type.

        Args:
            repair_type: Type of repair
            params: Repair parameters
        """
        if repair_type in self._repair_callbacks:
            for callback in self._repair_callbacks[repair_type]:
                try:
                    callback(params)
                except Exception:
                    # Ignore callback errors
                    pass

    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish event to FAZA 28 EventBus.

        Args:
            event_type: Event type
            event_data: Event data
        """
        if self.event_bus and hasattr(self.event_bus, 'publish'):
            try:
                self.event_bus.publish(f"faza30.{event_type}", event_data)
            except Exception:
                pass

    def get_integration_status(self) -> Dict[str, bool]:
        """
        Get integration status for each layer.

        Returns:
            Dict showing which layers are integrated
        """
        return {
            "faza25_integrated": self.faza25_orchestrator is not None,
            "faza27_integrated": self.faza27_task_graph is not None,
            "faza27_5_integrated": self.faza27_5_optimizer is not None,
            "faza28_integrated": self.faza28_agent_loop is not None,
            "faza28_5_integrated": self.faza28_5_meta_layer is not None,
            "faza29_integrated": self.faza29_governance is not None,
            "event_bus_integrated": self.event_bus is not None
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get integration layer statistics."""
        integration_status = self.get_integration_status()
        integrated_count = sum(1 for v in integration_status.values() if v)

        return {
            **self._stats,
            "integrated_layers": integrated_count,
            "integration_status": integration_status
        }


def create_integration_layer(
    faza25_orchestrator: Optional[Any] = None,
    faza27_task_graph: Optional[Any] = None,
    faza27_5_optimizer: Optional[Any] = None,
    faza28_agent_loop: Optional[Any] = None,
    faza28_5_meta_layer: Optional[Any] = None,
    faza29_governance: Optional[Any] = None,
    event_bus: Optional[Any] = None
) -> IntegrationLayer:
    """
    Factory function to create IntegrationLayer.

    Args:
        faza25_orchestrator: Optional FAZA 25 Orchestrator
        faza27_task_graph: Optional FAZA 27 TaskGraph
        faza27_5_optimizer: Optional FAZA 27.5 Optimizer
        faza28_agent_loop: Optional FAZA 28 AgentLoop
        faza28_5_meta_layer: Optional FAZA 28.5 MetaLayer
        faza29_governance: Optional FAZA 29 Governance
        event_bus: Optional FAZA 28 EventBus

    Returns:
        Initialized IntegrationLayer instance
    """
    return IntegrationLayer(
        faza25_orchestrator=faza25_orchestrator,
        faza27_task_graph=faza27_task_graph,
        faza27_5_optimizer=faza27_5_optimizer,
        faza28_agent_loop=faza28_agent_loop,
        faza28_5_meta_layer=faza28_5_meta_layer,
        faza29_governance=faza29_governance,
        event_bus=event_bus
    )

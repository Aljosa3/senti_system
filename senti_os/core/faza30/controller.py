"""
FAZA 30 – Self-Healing Controller

High-level API and main controller for FAZA 30 Self-Healing Engine.

Provides:
- Unified self-healing API
- Component initialization
- Lifecycle management
- Global singleton support
- Comprehensive status and statistics

Architecture:
    HealingController - Main controller
    Global singleton instance

Usage:
    from senti_os.core.faza30 import get_healing_controller

    # Get controller
    controller = get_healing_controller()

    # Start auto-repair
    await controller.start()

    # Get status
    status = controller.get_status()
    health = controller.get_health()

    # Stop
    await controller.stop()
"""

from typing import Dict, Optional, Any
from datetime import datetime


# Import all FAZA 30 components
from senti_os.core.faza30.detection_engine import create_detection_engine
from senti_os.core.faza30.classification_engine import create_classification_engine
from senti_os.core.faza30.repair_strategies import (
    create_graph_repair_engine,
    create_agent_repair_engine,
    create_scheduler_repair_engine,
    create_governance_repair_engine
)
from senti_os.core.faza30.healing_pipeline import create_healing_pipeline
from senti_os.core.faza30.snapshot_manager import create_snapshot_manager
from senti_os.core.faza30.health_engine import create_health_engine
from senti_os.core.faza30.autorepair_engine import create_autorepair_engine, AutorepairConfig, AutorepairMode
from senti_os.core.faza30.integration_layer import create_integration_layer
from senti_os.core.faza30.event_hooks import create_event_hooks


class HealingController:
    """
    Main controller for FAZA 30 Self-Healing Engine.

    Coordinates all self-healing subsystems:
    - Detection engine
    - Classification engine
    - Repair engines (4 types)
    - Healing pipeline
    - Snapshot manager
    - Health engine
    - Autorepair engine
    - Integration layer
    - Event hooks

    Features:
    - Unified API
    - Component lifecycle management
    - Automatic initialization
    - Status monitoring
    - Statistics aggregation
    """

    def __init__(
        self,
        faza25_orchestrator: Optional[Any] = None,
        faza27_task_graph: Optional[Any] = None,
        faza27_5_optimizer: Optional[Any] = None,
        faza28_agent_loop: Optional[Any] = None,
        faza28_5_meta_layer: Optional[Any] = None,
        faza29_governance: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        autorepair_config: Optional[AutorepairConfig] = None
    ):
        """
        Initialize healing controller.

        Args:
            faza25_orchestrator: Optional FAZA 25 Orchestrator
            faza27_task_graph: Optional FAZA 27 TaskGraph
            faza27_5_optimizer: Optional FAZA 27.5 Optimizer
            faza28_agent_loop: Optional FAZA 28 AgentLoop
            faza28_5_meta_layer: Optional FAZA 28.5 MetaLayer
            faza29_governance: Optional FAZA 29 Governance
            event_bus: Optional FAZA 28 EventBus
            autorepair_config: Optional autorepair configuration
        """
        self._initialized = False
        self._running = False
        self._init_time = datetime.now()

        # Create event hooks
        self.event_hooks = create_event_hooks(event_bus)

        # Create integration layer
        self.integration_layer = create_integration_layer(
            faza25_orchestrator=faza25_orchestrator,
            faza27_task_graph=faza27_task_graph,
            faza27_5_optimizer=faza27_5_optimizer,
            faza28_agent_loop=faza28_agent_loop,
            faza28_5_meta_layer=faza28_5_meta_layer,
            faza29_governance=faza29_governance,
            event_bus=event_bus
        )

        # Create detection engine
        self.detection_engine = create_detection_engine()

        # Create classification engine
        self.classification_engine = create_classification_engine()

        # Create repair engines
        self.graph_repair_engine = create_graph_repair_engine()
        self.agent_repair_engine = create_agent_repair_engine()
        self.scheduler_repair_engine = create_scheduler_repair_engine()
        self.governance_repair_engine = create_governance_repair_engine()

        self.repair_engines = {
            "graph": self.graph_repair_engine,
            "agent": self.agent_repair_engine,
            "scheduler": self.scheduler_repair_engine,
            "governance": self.governance_repair_engine
        }

        # Create snapshot manager
        self.snapshot_manager = create_snapshot_manager()

        # Create health engine
        self.health_engine = create_health_engine()

        # Create healing pipeline
        self.healing_pipeline = create_healing_pipeline(
            detection_engine=self.detection_engine,
            classification_engine=self.classification_engine,
            repair_engines=self.repair_engines,
            snapshot_manager=self.snapshot_manager,
            health_engine=self.health_engine
        )

        # Create autorepair engine
        self.autorepair_engine = create_autorepair_engine(
            healing_pipeline=self.healing_pipeline,
            integration_layer=self.integration_layer,
            event_hooks=self.event_hooks,
            config=autorepair_config
        )

        self._initialized = True

        # Publish initialization event
        self.event_hooks.publish_event(
            "controller_initialized",
            {"timestamp": self._init_time.isoformat()}
        )

    async def start(self) -> None:
        """Start the self-healing controller (enables autorepair)."""
        if self._running:
            return

        await self.autorepair_engine.start()
        self._running = True

        self.event_hooks.publish_event(
            "controller_started",
            {"mode": self.autorepair_engine.config.mode.value}
        )

    async def stop(self) -> None:
        """Stop the self-healing controller."""
        if not self._running:
            return

        await self.autorepair_engine.stop()
        self._running = False

        self.event_hooks.publish_event(
            "controller_stopped",
            {"uptime_seconds": self.get_uptime()}
        )

    def is_running(self) -> bool:
        """Check if controller is running."""
        return self._running

    def get_uptime(self) -> float:
        """Get controller uptime in seconds."""
        return (datetime.now() - self._init_time).total_seconds()

    # ======================
    # Component Access
    # ======================

    def get_detection_engine(self):
        """Get detection engine instance."""
        return self.detection_engine

    def get_classification_engine(self):
        """Get classification engine instance."""
        return self.classification_engine

    def get_repair_engines(self) -> Dict[str, Any]:
        """Get all repair engines."""
        return self.repair_engines

    def get_healing_pipeline(self):
        """Get healing pipeline instance."""
        return self.healing_pipeline

    def get_snapshot_manager(self):
        """Get snapshot manager instance."""
        return self.snapshot_manager

    def get_health_engine(self):
        """Get health engine instance."""
        return self.health_engine

    def get_autorepair_engine(self):
        """Get autorepair engine instance."""
        return self.autorepair_engine

    def get_integration_layer(self):
        """Get integration layer instance."""
        return self.integration_layer

    def get_event_hooks(self):
        """Get event hooks instance."""
        return self.event_hooks

    # ======================
    # High-Level API
    # ======================

    def get_health(self) -> Dict[str, Any]:
        """
        Get current system health.

        Returns:
            Dict with health score and breakdown
        """
        # Collect metrics
        metrics = self.integration_layer.get_all_metrics()

        # Compute health
        health_score = self.health_engine.compute_health_score(
            faza25_metrics=metrics.get("faza25"),
            faza27_metrics=metrics.get("faza27"),
            faza28_metrics=metrics.get("faza28"),
            faza28_5_metrics=metrics.get("faza28_5"),
            faza29_metrics=metrics.get("faza29")
        )

        # Analyze trend
        trend = self.health_engine.analyze_trend()

        return {
            "overall_score": health_score.overall_score,
            "level": health_score.level.value,
            "components": [
                {
                    "name": c.name,
                    "score": c.score,
                    "weight": c.weight
                }
                for c in health_score.components
            ],
            "trend": {
                "direction": trend.direction.value,
                "slope": trend.slope,
                "confidence": trend.confidence,
                "prediction": trend.prediction
            },
            "timestamp": health_score.timestamp.isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.

        Returns:
            Dict with status from all components
        """
        # Get active faults
        active_faults = self.detection_engine.get_active_faults()

        # Get recent healing cycles
        recent_cycles = self.healing_pipeline.get_recent_cycles(limit=5)

        # Get autorepair status
        autorepair_stats = self.autorepair_engine.get_statistics()

        # Get integration status
        integration_status = self.integration_layer.get_integration_status()

        return {
            "running": self._running,
            "uptime_seconds": self.get_uptime(),
            "autorepair_mode": self.autorepair_engine.config.mode.value,
            "throttle_state": self.autorepair_engine.get_throttle_state().value,
            "active_faults": len(active_faults),
            "critical_faults": len([f for f in active_faults if 'critical' in str(getattr(f, 'severity', '')).lower()]),
            "recent_healing_cycles": len(recent_cycles),
            "last_healing_success": recent_cycles[0].outcome.value if recent_cycles else None,
            "integration_status": integration_status,
            "timestamp": datetime.now().isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics from all components.

        Returns:
            Dict with statistics from all subsystems
        """
        return {
            "controller": {
                "initialized": self._initialized,
                "running": self._running,
                "uptime_seconds": self.get_uptime()
            },
            "detection": self.detection_engine.get_statistics(),
            "classification": self.classification_engine.get_statistics(),
            "repair": {
                "graph": self.graph_repair_engine.get_statistics(),
                "agent": self.agent_repair_engine.get_statistics(),
                "scheduler": self.scheduler_repair_engine.get_statistics(),
                "governance": self.governance_repair_engine.get_statistics()
            },
            "pipeline": self.healing_pipeline.get_statistics(),
            "snapshots": self.snapshot_manager.get_statistics(),
            "health": self.health_engine.get_statistics(),
            "autorepair": self.autorepair_engine.get_statistics(),
            "integration": self.integration_layer.get_statistics(),
            "events": self.event_hooks.get_statistics()
        }

    def force_healing_cycle(self) -> Dict[str, Any]:
        """
        Force an immediate healing cycle.

        Returns:
            Healing result
        """
        self.autorepair_engine.force_healing_cycle()

        # Wait a moment for cycle to execute
        import time
        time.sleep(0.5)

        recent_cycles = self.healing_pipeline.get_recent_cycles(limit=1)
        if recent_cycles:
            cycle = recent_cycles[0]
            return {
                "cycle_id": cycle.cycle_id,
                "outcome": cycle.outcome.value,
                "faults_detected": cycle.faults_detected,
                "faults_repaired": cycle.faults_repaired,
                "health_improvement": cycle.health_improvement
            }

        return {"error": "No healing cycle executed"}

    def create_snapshot(self, snapshot_type: str = "manual") -> str:
        """
        Create a system snapshot.

        Args:
            snapshot_type: Type of snapshot

        Returns:
            Snapshot ID
        """
        return self.snapshot_manager.create_snapshot(
            snapshot_type=snapshot_type,
            metadata={"controller": "faza30"}
        )

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore from snapshot.

        Args:
            snapshot_id: Snapshot to restore

        Returns:
            True if restore successful
        """
        return self.snapshot_manager.restore_snapshot(snapshot_id)

    def set_autorepair_mode(self, mode: str) -> None:
        """
        Change autorepair mode.

        Args:
            mode: New mode (aggressive/balanced/conservative/disabled)
        """
        self.autorepair_engine.set_mode(AutorepairMode(mode))

    def get_faults(self, include_resolved: bool = False) -> Dict[str, Any]:
        """
        Get current faults.

        Args:
            include_resolved: Include resolved faults

        Returns:
            Dict with fault information
        """
        active_faults = self.detection_engine.get_active_faults()
        critical_faults = self.detection_engine.get_critical_faults()

        return {
            "active_faults": len(active_faults),
            "critical_faults": len(critical_faults),
            "faults": [
                {
                    "fault_id": getattr(f, 'fault_id', 'unknown'),
                    "source": str(getattr(f, 'source', 'unknown')),
                    "severity": str(getattr(f, 'severity', 'unknown')),
                    "fault_type": getattr(f, 'fault_type', 'unknown'),
                    "description": getattr(f, 'description', '')
                }
                for f in active_faults
            ]
        }


# Global singleton instance
_global_controller: Optional[HealingController] = None


def get_healing_controller(
    faza25_orchestrator: Optional[Any] = None,
    faza27_task_graph: Optional[Any] = None,
    faza27_5_optimizer: Optional[Any] = None,
    faza28_agent_loop: Optional[Any] = None,
    faza28_5_meta_layer: Optional[Any] = None,
    faza29_governance: Optional[Any] = None,
    event_bus: Optional[Any] = None,
    autorepair_config: Optional[AutorepairConfig] = None,
    force_new: bool = False
) -> HealingController:
    """
    Get global healing controller instance.

    Args:
        faza25_orchestrator: Optional FAZA 25 Orchestrator
        faza27_task_graph: Optional FAZA 27 TaskGraph
        faza27_5_optimizer: Optional FAZA 27.5 Optimizer
        faza28_agent_loop: Optional FAZA 28 AgentLoop
        faza28_5_meta_layer: Optional FAZA 28.5 MetaLayer
        faza29_governance: Optional FAZA 29 Governance
        event_bus: Optional FAZA 28 EventBus
        autorepair_config: Optional autorepair configuration
        force_new: Force creation of new instance

    Returns:
        HealingController instance
    """
    global _global_controller

    if _global_controller is None or force_new:
        _global_controller = HealingController(
            faza25_orchestrator=faza25_orchestrator,
            faza27_task_graph=faza27_task_graph,
            faza27_5_optimizer=faza27_5_optimizer,
            faza28_agent_loop=faza28_agent_loop,
            faza28_5_meta_layer=faza28_5_meta_layer,
            faza29_governance=faza29_governance,
            event_bus=event_bus,
            autorepair_config=autorepair_config
        )

    return _global_controller


def create_healing_controller(
    faza25_orchestrator: Optional[Any] = None,
    faza27_task_graph: Optional[Any] = None,
    faza27_5_optimizer: Optional[Any] = None,
    faza28_agent_loop: Optional[Any] = None,
    faza28_5_meta_layer: Optional[Any] = None,
    faza29_governance: Optional[Any] = None,
    event_bus: Optional[Any] = None,
    autorepair_config: Optional[AutorepairConfig] = None
) -> HealingController:
    """
    Create new healing controller instance (non-singleton).

    Args:
        faza25_orchestrator: Optional FAZA 25 Orchestrator
        faza27_task_graph: Optional FAZA 27 TaskGraph
        faza27_5_optimizer: Optional FAZA 27.5 Optimizer
        faza28_agent_loop: Optional FAZA 28 AgentLoop
        faza28_5_meta_layer: Optional FAZA 28.5 MetaLayer
        faza29_governance: Optional FAZA 29 Governance
        event_bus: Optional FAZA 28 EventBus
        autorepair_config: Optional autorepair configuration

    Returns:
        New HealingController instance
    """
    return HealingController(
        faza25_orchestrator=faza25_orchestrator,
        faza27_task_graph=faza27_task_graph,
        faza27_5_optimizer=faza27_5_optimizer,
        faza28_agent_loop=faza28_agent_loop,
        faza28_5_meta_layer=faza28_5_meta_layer,
        faza29_governance=faza29_governance,
        event_bus=event_bus,
        autorepair_config=autorepair_config
    )

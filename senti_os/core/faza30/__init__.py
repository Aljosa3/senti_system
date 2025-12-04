"""
FAZA 30 – Enterprise Self-Healing Engine

Comprehensive self-healing and fault recovery system for Senti OS.

Provides:
- Fault detection from all FAZA layers
- Fault classification (5 categories)
- Automated repair strategies (4 repair engines)
- 12-step healing pipeline
- Snapshot/rollback capability
- Health scoring (0-100) and trend analysis
- Continuous autorepair loop with throttling
- Integration with FAZA 25/27/27.5/28/28.5/29

Architecture:
    Detection Engine    - Fault detection from all layers
    Classification      - 5-category fault taxonomy
    Repair Engines      - Graph, Agent, Scheduler, Governance
    Healing Pipeline    - 12-step orchestrated healing
    Snapshot Manager    - State capture and rollback
    Health Engine       - Health scoring and trends
    Autorepair Engine   - Continuous self-healing loop
    Integration Layer   - Non-intrusive FAZA integration
    Controller          - High-level unified API

Usage:
    from senti_os.core.faza30 import get_healing_controller

    # Get controller
    controller = get_healing_controller(
        faza25_orchestrator=orchestrator,
        faza27_task_graph=task_graph,
        faza29_governance=governance
    )

    # Start autorepair
    await controller.start()

    # Get health and status
    health = controller.get_health()
    status = controller.get_status()

    # Force manual healing
    result = controller.force_healing_cycle()

    # Stop
    await controller.stop()

Enterprise Features:
- Real-time fault detection
- Automatic repair execution
- System health monitoring
- Snapshot-based rollback
- Healing throttle (prevent repair storms)
- Multi-layer integration
- Type-safe event system
"""

# Main controller
from senti_os.core.faza30.controller import (
    HealingController,
    get_healing_controller,
    create_healing_controller
)

# Detection engine
from senti_os.core.faza30.detection_engine import (
    DetectionEngine,
    DetectedFault,
    FaultSeverity,
    FaultSource,
    create_detection_engine
)

# Classification engine
from senti_os.core.faza30.classification_engine import (
    ClassificationEngine,
    ClassificationResult,
    FaultCategory,
    RepairPriority,
    create_classification_engine
)

# Repair strategies
from senti_os.core.faza30.repair_strategies import (
    GraphRepairEngine,
    AgentRepairEngine,
    SchedulerRepairEngine,
    GovernanceRepairEngine,
    RepairResult,
    RepairStatus,
    create_graph_repair_engine,
    create_agent_repair_engine,
    create_scheduler_repair_engine,
    create_governance_repair_engine
)

# Healing pipeline
from senti_os.core.faza30.healing_pipeline import (
    HealingPipeline,
    HealingStage,
    HealingOutcome,
    HealingResult,
    HealingContext,
    create_healing_pipeline
)

# Snapshot manager
from senti_os.core.faza30.snapshot_manager import (
    SnapshotManager,
    Snapshot,
    SnapshotType,
    create_snapshot_manager
)

# Health engine
from senti_os.core.faza30.health_engine import (
    HealthEngine,
    HealthScore,
    HealthTrend,
    HealthLevel,
    TrendDirection,
    create_health_engine
)

# Autorepair engine
from senti_os.core.faza30.autorepair_engine import (
    AutorepairEngine,
    AutorepairConfig,
    AutorepairMode,
    ThrottleState,
    create_autorepair_engine,
    start_autorepair
)

# Integration layer
from senti_os.core.faza30.integration_layer import (
    IntegrationLayer,
    create_integration_layer
)

# Event hooks
from senti_os.core.faza30.event_hooks import (
    EventHooks,
    FazaEvent,
    EventType,
    create_event_hooks
)


__all__ = [
    # Main controller
    "HealingController",
    "get_healing_controller",
    "create_healing_controller",

    # Detection engine
    "DetectionEngine",
    "DetectedFault",
    "FaultSeverity",
    "FaultSource",
    "create_detection_engine",

    # Classification engine
    "ClassificationEngine",
    "ClassificationResult",
    "FaultCategory",
    "RepairPriority",
    "create_classification_engine",

    # Repair strategies
    "GraphRepairEngine",
    "AgentRepairEngine",
    "SchedulerRepairEngine",
    "GovernanceRepairEngine",
    "RepairResult",
    "RepairStatus",
    "create_graph_repair_engine",
    "create_agent_repair_engine",
    "create_scheduler_repair_engine",
    "create_governance_repair_engine",

    # Healing pipeline
    "HealingPipeline",
    "HealingStage",
    "HealingOutcome",
    "HealingResult",
    "HealingContext",
    "create_healing_pipeline",

    # Snapshot manager
    "SnapshotManager",
    "Snapshot",
    "SnapshotType",
    "create_snapshot_manager",

    # Health engine
    "HealthEngine",
    "HealthScore",
    "HealthTrend",
    "HealthLevel",
    "TrendDirection",
    "create_health_engine",

    # Autorepair engine
    "AutorepairEngine",
    "AutorepairConfig",
    "AutorepairMode",
    "ThrottleState",
    "create_autorepair_engine",
    "start_autorepair",

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
__author__ = "Senti System - FAZA 30 Enterprise Edition"
__description__ = "FAZA 30 - Enterprise Self-Healing Engine"

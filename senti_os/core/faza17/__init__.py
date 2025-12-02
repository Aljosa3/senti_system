"""
FAZA 17 - Multi-Model Orchestration Layer

This module provides comprehensive multi-model orchestration capabilities for SENTI OS.

Main Components:
- Orchestration Manager: Main coordinator for complex tasks
- Step Planner: Task decomposition and planning
- Priority Queue: Task scheduling and prioritization
- Model Ensemble Engine: Multi-model output combination
- Pipeline Manager: Execution flow control
- Reliability Feedback: Learning from outcomes
- Explainability Engine: Transparent decision logging

Usage:
    from senti_os.core.faza17 import create_orchestration_manager, OrchestrationRequest, Priority

    manager = create_orchestration_manager()

    request = OrchestrationRequest(
        request_id="req_001",
        task_description="Analyze data and generate report",
        priority=Priority.HIGH,
    )

    request_id = manager.submit_task(request)
    result = manager.process_next_task()
"""

__version__ = "1.0.0"
__author__ = "SENTI OS Team"

from senti_os.core.faza17.orchestration_manager import (
    OrchestrationManager,
    create_orchestration_manager,
    OrchestrationRequest,
    OrchestrationResult,
    OrchestrationStatus,
)

from senti_os.core.faza17.step_planner import (
    StepPlanner,
    create_planner,
    Step,
    StepType,
    ExecutionMode,
    PlanningResult,
)

from senti_os.core.faza17.priority_queue import (
    PriorityQueue,
    create_queue,
    QueuedTask,
    Priority,
    QueueStatistics,
)

from senti_os.core.faza17.model_ensemble_engine import (
    ModelEnsembleEngine,
    create_ensemble_engine,
    ModelOutput,
    EnsembleStrategy,
    EnsembleResult,
    ConflictResolution,
)

from senti_os.core.faza17.pipeline_manager import (
    PipelineManager,
    create_pipeline_manager,
    PipelineStrategy,
    PipelineStage,
    PipelineResult,
    StageStatus,
)

from senti_os.core.faza17.reliability_feedback import (
    ReliabilityFeedbackLoop,
    create_feedback_loop,
    FeedbackEntry,
    ModelMetrics,
    OutcomeType,
)

from senti_os.core.faza17.explainability_engine import (
    ExplainabilityEngine,
    create_explainability_engine,
    ExplanationEntry,
    DecisionType,
    DecisionFactor,
)


__all__ = [
    # Orchestration Manager
    "OrchestrationManager",
    "create_orchestration_manager",
    "OrchestrationRequest",
    "OrchestrationResult",
    "OrchestrationStatus",

    # Step Planner
    "StepPlanner",
    "create_planner",
    "Step",
    "StepType",
    "ExecutionMode",
    "PlanningResult",

    # Priority Queue
    "PriorityQueue",
    "create_queue",
    "QueuedTask",
    "Priority",
    "QueueStatistics",

    # Model Ensemble Engine
    "ModelEnsembleEngine",
    "create_ensemble_engine",
    "ModelOutput",
    "EnsembleStrategy",
    "EnsembleResult",
    "ConflictResolution",

    # Pipeline Manager
    "PipelineManager",
    "create_pipeline_manager",
    "PipelineStrategy",
    "PipelineStage",
    "PipelineResult",
    "StageStatus",

    # Reliability Feedback
    "ReliabilityFeedbackLoop",
    "create_feedback_loop",
    "FeedbackEntry",
    "ModelMetrics",
    "OutcomeType",

    # Explainability Engine
    "ExplainabilityEngine",
    "create_explainability_engine",
    "ExplanationEntry",
    "DecisionType",
    "DecisionFactor",
]


def get_version() -> str:
    """
    Get FAZA 17 version.

    Returns:
        Version string
    """
    return __version__


def get_info() -> dict:
    """
    Get FAZA 17 module information.

    Returns:
        Dictionary with module information
    """
    return {
        "name": "FAZA 17 - Multi-Model Orchestration Layer",
        "version": __version__,
        "author": __author__,
        "components": [
            "Orchestration Manager",
            "Step Planner",
            "Priority Queue",
            "Model Ensemble Engine",
            "Pipeline Manager",
            "Reliability Feedback Loop",
            "Explainability Engine",
        ],
    }

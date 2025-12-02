"""
Orchestration Manager for SENTI OS FAZA 17

Main coordinator for multi-model orchestration:
- Receives complex tasks
- Plans execution steps
- Routes to optimal models via FAZA 16
- Executes with pipeline management
- Combines results via ensemble
- Provides full explainability
- Learns from outcomes

Integrates all FAZA 17 components into a cohesive orchestration system.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from senti_os.core.faza17.step_planner import StepPlanner, create_planner, StepType
from senti_os.core.faza17.priority_queue import PriorityQueue, QueuedTask, Priority, create_queue
from senti_os.core.faza17.model_ensemble_engine import ModelEnsembleEngine, ModelOutput, EnsembleStrategy, create_ensemble_engine
from senti_os.core.faza17.reliability_feedback import ReliabilityFeedbackLoop, OutcomeType, create_feedback_loop
from senti_os.core.faza17.explainability_engine import ExplainabilityEngine, create_explainability_engine
from senti_os.core.faza17.pipeline_manager import PipelineManager, PipelineStrategy, create_pipeline_manager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationStatus(Enum):
    """Status of orchestration tasks."""
    QUEUED = "queued"
    PLANNING = "planning"
    EXECUTING = "executing"
    ENSEMBLING = "ensembling"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrchestrationRequest:
    """Request for orchestration."""
    request_id: str
    task_description: str
    priority: Priority = Priority.NORMAL
    max_cost: float = 5.0
    max_time: int = 300
    require_ensemble: bool = False
    user_consent: bool = False
    context: Dict = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Result of orchestration."""
    request_id: str
    status: OrchestrationStatus
    final_output: str
    confidence_score: float
    total_cost: float
    total_duration: float
    steps_executed: int
    models_used: List[str]
    explanation: str
    quality_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class OrchestrationManager:
    """
    Main orchestration manager for FAZA 17.

    This manager coordinates all orchestration components to execute
    complex multi-model tasks with full transparency and learning.
    """

    def __init__(self, faza16_manager=None):
        """
        Initialize the orchestration manager.

        Args:
            faza16_manager: Optional FAZA 16 LLM Manager for integration
        """
        self.faza16_manager = faza16_manager

        self.planner = create_planner()
        self.queue = create_queue()
        self.ensemble_engine = create_ensemble_engine()
        self.feedback_loop = create_feedback_loop()
        self.explainability = create_explainability_engine()
        self.pipeline_manager = create_pipeline_manager()

        self.orchestration_history: List[OrchestrationResult] = []

        logger.info("Orchestration Manager initialized")

    def submit_task(self, request: OrchestrationRequest) -> str:
        """
        Submit a task for orchestration.

        Args:
            request: OrchestrationRequest to process

        Returns:
            Request ID for tracking
        """
        queued_task = QueuedTask(
            task_id=request.request_id,
            priority=request.priority,
            submission_time=datetime.now(),
            estimated_duration=request.max_time,
            max_cost=request.max_cost,
            metadata={
                "description": request.task_description,
                "require_ensemble": request.require_ensemble,
                "user_consent": request.user_consent,
                "context": request.context,
            },
        )

        success = self.queue.enqueue(queued_task)

        if success:
            logger.info(f"Task {request.request_id} submitted with priority {request.priority.value}")
            return request.request_id
        else:
            logger.error(f"Failed to submit task {request.request_id}: queue full")
            raise RuntimeError("Task queue is full")

    def process_next_task(self) -> Optional[OrchestrationResult]:
        """
        Process the next task from the queue.

        Returns:
            OrchestrationResult if task processed, None if queue empty
        """
        task = self.queue.dequeue()

        if not task:
            return None

        try:
            result = self._orchestrate_task(task)
            self.queue.mark_completed(task.task_id)

            return result

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            self.queue.mark_failed(task.task_id, retry=True)

            return OrchestrationResult(
                request_id=task.task_id,
                status=OrchestrationStatus.FAILED,
                final_output="",
                confidence_score=0.0,
                total_cost=0.0,
                total_duration=0.0,
                steps_executed=0,
                models_used=[],
                explanation=f"Orchestration failed: {str(e)}",
                quality_score=0.0,
            )

    def _orchestrate_task(self, task: QueuedTask) -> OrchestrationResult:
        """
        Orchestrate a single task through the full pipeline.

        Args:
            task: QueuedTask to orchestrate

        Returns:
            OrchestrationResult with execution details
        """
        start_time = datetime.now()

        task_description = task.metadata.get("description", "")
        context = task.metadata.get("context", {})
        require_ensemble = task.metadata.get("require_ensemble", False)

        planning_result = self.planner.plan_task(
            task_description=task_description,
            context=context,
            max_steps=10,
        )

        self.explainability.explain_step_planning(
            decision_id=f"{task.task_id}_planning",
            num_steps=len(planning_result.steps),
            execution_mode=planning_result.execution_mode.value,
            estimated_cost=planning_result.total_estimated_cost,
            estimated_time=planning_result.total_estimated_time,
            safety_checks_passed=planning_result.safety_checks_passed,
        )

        if not planning_result.safety_checks_passed:
            return OrchestrationResult(
                request_id=task.task_id,
                status=OrchestrationStatus.FAILED,
                final_output="",
                confidence_score=0.0,
                total_cost=0.0,
                total_duration=0.0,
                steps_executed=0,
                models_used=[],
                explanation="Safety checks failed during planning",
                quality_score=0.0,
            )

        pipeline_stages = [
            {
                "name": step.description,
                "model_id": f"model_{i}",
            }
            for i, step in enumerate(planning_result.steps)
        ]

        pipeline_result = self.pipeline_manager.execute_pipeline(
            pipeline_id=task.task_id,
            strategy=PipelineStrategy.LOCAL_FAST_PRECISE,
            stages=pipeline_stages,
            max_time=task.estimated_duration,
            max_cost=task.max_cost,
        )

        if require_ensemble and len(pipeline_result.stages) > 1:
            model_outputs = [
                ModelOutput(
                    model_id=stage.model_id or f"model_{i}",
                    content=stage.output or "",
                    confidence=stage.confidence,
                    reliability_score=0.8,
                    processing_time=stage.duration,
                    cost=stage.cost,
                )
                for i, stage in enumerate(pipeline_result.stages)
                if stage.output
            ]

            ensemble_result = self.ensemble_engine.combine_outputs(
                outputs=model_outputs,
                strategy=EnsembleStrategy.WEIGHTED_AVERAGE,
            )

            self.explainability.explain_ensemble_strategy(
                decision_id=f"{task.task_id}_ensemble",
                strategy=EnsembleStrategy.WEIGHTED_AVERAGE.value,
                num_models=len(model_outputs),
                conflicts_detected=ensemble_result.conflicts_detected,
                final_confidence=ensemble_result.confidence_score,
            )

            final_output = ensemble_result.final_output
            confidence = ensemble_result.confidence_score
            quality_score = ensemble_result.quality_score
        else:
            final_output = pipeline_result.final_output
            confidence = pipeline_result.quality_score
            quality_score = pipeline_result.quality_score

        models_used = list(set(
            stage.model_id for stage in pipeline_result.stages
            if stage.model_id
        ))

        for model_id in models_used:
            self.feedback_loop.record_outcome(
                model_id=model_id,
                task_id=task.task_id,
                outcome=OutcomeType.SUCCESS if pipeline_result.success else OutcomeType.FAILURE,
                confidence_claimed=confidence,
                actual_quality=quality_score,
                processing_time=pipeline_result.total_duration,
                cost=pipeline_result.total_cost,
            )

        duration = (datetime.now() - start_time).total_seconds()

        result = OrchestrationResult(
            request_id=task.task_id,
            status=OrchestrationStatus.COMPLETED if pipeline_result.success else OrchestrationStatus.FAILED,
            final_output=final_output,
            confidence_score=confidence,
            total_cost=pipeline_result.total_cost,
            total_duration=duration,
            steps_executed=len(planning_result.steps),
            models_used=models_used,
            explanation=f"Orchestrated {len(planning_result.steps)} steps using {len(models_used)} models",
            quality_score=quality_score,
        )

        self.orchestration_history.append(result)

        logger.info(f"Orchestration completed: {task.task_id}, quality: {quality_score:.2f}")

        return result

    def get_queue_status(self) -> Dict:
        """
        Get current queue status.

        Returns:
            Dictionary with queue information
        """
        stats = self.queue.get_statistics()

        return {
            "queue_size": stats.current_size,
            "total_enqueued": stats.total_enqueued,
            "total_completed": stats.total_completed,
            "total_failed": stats.total_failed,
            "average_wait_time": stats.average_wait_time,
            "tasks_by_priority": stats.tasks_by_priority,
        }

    def get_statistics(self) -> Dict:
        """
        Get comprehensive orchestration statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.orchestration_history:
            return {
                "total_orchestrations": 0,
                "success_rate": 0.0,
                "average_cost": 0.0,
                "average_duration": 0.0,
                "average_quality": 0.0,
            }

        total = len(self.orchestration_history)
        successful = sum(1 for r in self.orchestration_history if r.status == OrchestrationStatus.COMPLETED)

        return {
            "total_orchestrations": total,
            "success_rate": round(successful / total, 3),
            "average_cost": round(sum(r.total_cost for r in self.orchestration_history) / total, 2),
            "average_duration": round(sum(r.total_duration for r in self.orchestration_history) / total, 2),
            "average_quality": round(sum(r.quality_score for r in self.orchestration_history) / total, 3),
            "total_models_used": len(set(m for r in self.orchestration_history for m in r.models_used)),
            "queue_stats": self.get_queue_status(),
            "feedback_stats": self.feedback_loop.get_statistics(),
            "ensemble_stats": self.ensemble_engine.get_statistics(),
        }

    def update_model_reliability(self) -> Dict[str, float]:
        """
        Update model reliability scores based on feedback.

        Returns:
            Dictionary of updated scores
        """
        return self.feedback_loop.update_reliability_scores()

    def get_audit_report(self) -> Dict:
        """
        Generate comprehensive audit report.

        Returns:
            Audit report dictionary
        """
        return {
            "orchestration_stats": self.get_statistics(),
            "explainability_report": self.explainability.generate_audit_report(),
            "feedback_stats": self.feedback_loop.get_statistics(),
            "pipeline_stats": self.pipeline_manager.get_statistics(),
            "ensemble_stats": self.ensemble_engine.get_statistics(),
        }


def create_orchestration_manager(faza16_manager=None) -> OrchestrationManager:
    """
    Create and return an orchestration manager.

    Args:
        faza16_manager: Optional FAZA 16 manager for integration

    Returns:
        Configured OrchestrationManager instance
    """
    manager = OrchestrationManager(faza16_manager)
    logger.info("Orchestration Manager created")
    return manager

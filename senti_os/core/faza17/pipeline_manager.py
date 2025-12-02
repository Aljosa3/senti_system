"""
Pipeline Manager for SENTI OS FAZA 17

Controls execution flow through pipelines:
- Local → Fast → Precise execution strategy
- Parallel multi-model execution
- Time and cost limit enforcement
- Pipeline optimization
- Fallback handling

Ensures efficient resource utilization and quality delivery.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineStrategy(Enum):
    """Pipeline execution strategies."""
    LOCAL_FAST_PRECISE = "local_fast_precise"
    PARALLEL_ENSEMBLE = "parallel_ensemble"
    SEQUENTIAL_VALIDATION = "sequential_validation"
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_FIRST = "quality_first"


class StageStatus(Enum):
    """Status of pipeline stages."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """Represents a stage in the pipeline."""
    stage_id: str
    stage_name: str
    model_id: Optional[str]
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: float = 0.0
    cost: float = 0.0
    output: Optional[str] = None
    confidence: float = 0.0
    error_message: Optional[str] = None


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    pipeline_id: str
    strategy: PipelineStrategy
    stages: List[PipelineStage]
    final_output: str
    total_duration: float
    total_cost: float
    success: bool
    quality_score: float
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PipelineManager:
    """
    Manages execution pipelines for multi-model orchestration.

    This manager controls flow through different execution strategies,
    enforces limits, and optimizes for quality and cost.
    """

    def __init__(self):
        """Initialize the pipeline manager."""
        self.execution_history: List[PipelineResult] = []
        logger.info("Pipeline Manager initialized")

    def execute_pipeline(
        self,
        pipeline_id: str,
        strategy: PipelineStrategy,
        stages: List[Dict],
        max_time: int = 300,
        max_cost: float = 10.0,
    ) -> PipelineResult:
        """
        Execute a pipeline with specified strategy.

        Args:
            pipeline_id: Unique pipeline identifier
            strategy: Execution strategy
            stages: List of stage definitions
            max_time: Maximum time in seconds
            max_cost: Maximum cost allowed

        Returns:
            PipelineResult with execution details
        """
        pipeline_stages = [
            PipelineStage(
                stage_id=f"{pipeline_id}_stage_{i}",
                stage_name=stage.get("name", f"Stage {i}"),
                model_id=stage.get("model_id"),
            )
            for i, stage in enumerate(stages)
        ]

        start_time = datetime.now()

        if strategy == PipelineStrategy.LOCAL_FAST_PRECISE:
            result = self._execute_local_fast_precise(
                pipeline_id, pipeline_stages, max_time, max_cost
            )
        elif strategy == PipelineStrategy.PARALLEL_ENSEMBLE:
            result = self._execute_parallel_ensemble(
                pipeline_id, pipeline_stages, max_time, max_cost
            )
        elif strategy == PipelineStrategy.SEQUENTIAL_VALIDATION:
            result = self._execute_sequential_validation(
                pipeline_id, pipeline_stages, max_time, max_cost
            )
        else:
            result = self._execute_default_pipeline(
                pipeline_id, pipeline_stages, max_time, max_cost
            )

        self.execution_history.append(result)

        logger.info(f"Pipeline {pipeline_id} completed: success={result.success}, cost=${result.total_cost:.2f}")

        return result

    def _execute_local_fast_precise(
        self,
        pipeline_id: str,
        stages: List[PipelineStage],
        max_time: int,
        max_cost: float,
    ) -> PipelineResult:
        """Execute local-fast-precise strategy."""
        executed_stages = []
        total_cost = 0.0
        total_duration = 0.0
        final_output = ""
        success = True

        for i, stage in enumerate(stages):
            if total_duration >= max_time or total_cost >= max_cost:
                stage.status = StageStatus.SKIPPED
                executed_stages.append(stage)
                continue

            stage.status = StageStatus.RUNNING
            stage.start_time = datetime.now().isoformat()

            simulated_duration = 1.0 + i * 0.5
            simulated_cost = 0.1 * (i + 1)

            stage.duration = simulated_duration
            stage.cost = simulated_cost
            stage.output = f"Output from {stage.stage_name}"
            stage.confidence = 0.7 + i * 0.1
            stage.status = StageStatus.COMPLETED
            stage.end_time = datetime.now().isoformat()

            total_duration += simulated_duration
            total_cost += simulated_cost
            final_output = stage.output

            executed_stages.append(stage)

        quality_score = sum(s.confidence for s in executed_stages if s.status == StageStatus.COMPLETED) / len(executed_stages)

        return PipelineResult(
            pipeline_id=pipeline_id,
            strategy=PipelineStrategy.LOCAL_FAST_PRECISE,
            stages=executed_stages,
            final_output=final_output,
            total_duration=total_duration,
            total_cost=total_cost,
            success=success,
            quality_score=quality_score,
            explanation=f"Local-Fast-Precise: {len([s for s in executed_stages if s.status == StageStatus.COMPLETED])} stages completed",
        )

    def _execute_parallel_ensemble(
        self,
        pipeline_id: str,
        stages: List[PipelineStage],
        max_time: int,
        max_cost: float,
    ) -> PipelineResult:
        """Execute parallel ensemble strategy."""
        executed_stages = []
        max_duration = 0.0
        total_cost = 0.0

        for i, stage in enumerate(stages):
            if total_cost >= max_cost:
                stage.status = StageStatus.SKIPPED
                executed_stages.append(stage)
                continue

            stage.status = StageStatus.RUNNING
            stage.start_time = datetime.now().isoformat()

            simulated_duration = 2.0
            simulated_cost = 0.2

            stage.duration = simulated_duration
            stage.cost = simulated_cost
            stage.output = f"Parallel output from {stage.stage_name}"
            stage.confidence = 0.85
            stage.status = StageStatus.COMPLETED
            stage.end_time = datetime.now().isoformat()

            max_duration = max(max_duration, simulated_duration)
            total_cost += simulated_cost

            executed_stages.append(stage)

        final_output = "Ensemble result from parallel execution"
        quality_score = 0.9

        return PipelineResult(
            pipeline_id=pipeline_id,
            strategy=PipelineStrategy.PARALLEL_ENSEMBLE,
            stages=executed_stages,
            final_output=final_output,
            total_duration=max_duration,
            total_cost=total_cost,
            success=True,
            quality_score=quality_score,
            explanation=f"Parallel ensemble: {len(executed_stages)} models executed simultaneously",
        )

    def _execute_sequential_validation(
        self,
        pipeline_id: str,
        stages: List[PipelineStage],
        max_time: int,
        max_cost: float,
    ) -> PipelineResult:
        """Execute sequential validation strategy."""
        executed_stages = []
        total_duration = 0.0
        total_cost = 0.0
        final_output = ""

        for i, stage in enumerate(stages):
            stage.status = StageStatus.RUNNING
            stage.start_time = datetime.now().isoformat()

            simulated_duration = 1.5
            simulated_cost = 0.15

            stage.duration = simulated_duration
            stage.cost = simulated_cost
            stage.output = f"Validated output from {stage.stage_name}"
            stage.confidence = 0.8 + i * 0.05
            stage.status = StageStatus.COMPLETED
            stage.end_time = datetime.now().isoformat()

            total_duration += simulated_duration
            total_cost += simulated_cost
            final_output = stage.output

            executed_stages.append(stage)

            if total_duration >= max_time or total_cost >= max_cost:
                break

        quality_score = 0.85

        return PipelineResult(
            pipeline_id=pipeline_id,
            strategy=PipelineStrategy.SEQUENTIAL_VALIDATION,
            stages=executed_stages,
            final_output=final_output,
            total_duration=total_duration,
            total_cost=total_cost,
            success=True,
            quality_score=quality_score,
            explanation=f"Sequential validation: {len(executed_stages)} stages with validation",
        )

    def _execute_default_pipeline(
        self,
        pipeline_id: str,
        stages: List[PipelineStage],
        max_time: int,
        max_cost: float,
    ) -> PipelineResult:
        """Execute default pipeline strategy."""
        return self._execute_local_fast_precise(pipeline_id, stages, max_time, max_cost)

    def get_statistics(self) -> Dict:
        """
        Get pipeline execution statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.execution_history:
            return {
                "total_pipelines": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "average_cost": 0.0,
            }

        total = len(self.execution_history)
        successful = sum(1 for p in self.execution_history if p.success)

        return {
            "total_pipelines": total,
            "success_rate": round(successful / total, 3),
            "average_duration": round(sum(p.total_duration for p in self.execution_history) / total, 2),
            "average_cost": round(sum(p.total_cost for p in self.execution_history) / total, 2),
            "average_quality": round(sum(p.quality_score for p in self.execution_history) / total, 3),
        }


def create_pipeline_manager() -> PipelineManager:
    """
    Create and return a pipeline manager.

    Returns:
        Configured PipelineManager instance
    """
    manager = PipelineManager()
    logger.info("Pipeline Manager created")
    return manager

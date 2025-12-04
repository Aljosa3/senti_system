"""
FAZA 25 - Pipeline Integration Module

Integrates FAZA 17 Pipeline Manager with FAZA 25 Orchestration Engine.
Allows pipelines to be executed as orchestrated tasks.
"""

import logging
from typing import Dict, Any, List

from senti_os.core.faza25.task_model import Task
from senti_os.core.faza25.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)


class PipelineTaskExecutor:
    """
    Wrapper that executes FAZA 17 pipelines as FAZA 25 tasks.
    """

    def __init__(self, pipeline_manager=None):
        """
        Initialize pipeline task executor.

        Args:
            pipeline_manager: FAZA 17 PipelineManager instance (optional)
        """
        self.pipeline_manager = pipeline_manager
        logger.info("PipelineTaskExecutor initialized")

    async def execute_pipeline_task(self, task: Task) -> Any:
        """
        Execute a pipeline as a task.

        Task context should contain:
        - pipeline_id: str
        - strategy: PipelineStrategy (or string)
        - stages: List[Dict]
        - max_time: int (optional, default: 300)
        - max_cost: float (optional, default: 10.0)

        Args:
            task: Task with pipeline configuration in context

        Returns:
            PipelineResult from FAZA 17
        """
        if not self.pipeline_manager:
            # Lazy import to avoid circular dependencies
            from senti_os.core.faza17.pipeline_manager import create_pipeline_manager
            self.pipeline_manager = create_pipeline_manager()

        # Extract pipeline parameters from task context
        pipeline_id = task.context.get("pipeline_id", task.id)
        strategy = task.context.get("strategy")
        stages = task.context.get("stages", [])
        max_time = task.context.get("max_time", 300)
        max_cost = task.context.get("max_cost", 10.0)

        if not stages:
            raise ValueError("Pipeline task requires 'stages' in context")

        if not strategy:
            # Import PipelineStrategy
            from senti_os.core.faza17.pipeline_manager import PipelineStrategy
            strategy = PipelineStrategy.LOCAL_FAST_PRECISE
        elif isinstance(strategy, str):
            # Convert string to enum
            from senti_os.core.faza17.pipeline_manager import PipelineStrategy
            strategy = PipelineStrategy[strategy.upper()]

        logger.info(f"Executing pipeline {pipeline_id} with strategy {strategy.value}")

        # Execute pipeline (synchronous call)
        result = self.pipeline_manager.execute_pipeline(
            pipeline_id=pipeline_id,
            strategy=strategy,
            stages=stages,
            max_time=max_time,
            max_cost=max_cost
        )

        logger.info(f"Pipeline {pipeline_id} completed: success={result.success}")

        return result


def submit_pipeline_task(
    pipeline_id: str,
    stages: List[Dict],
    strategy: str = "LOCAL_FAST_PRECISE",
    max_time: int = 300,
    max_cost: float = 10.0,
    priority: int = 5
) -> str:
    """
    Submit a FAZA 17 pipeline as a FAZA 25 orchestrated task.

    Args:
        pipeline_id: Unique pipeline identifier
        stages: List of pipeline stage definitions
        strategy: Execution strategy name (default: LOCAL_FAST_PRECISE)
        max_time: Maximum execution time in seconds
        max_cost: Maximum cost allowed
        priority: Task priority (0-10)

    Returns:
        Task ID

    Example:
        task_id = submit_pipeline_task(
            pipeline_id="my_pipeline",
            stages=[
                {"name": "Stage 1", "model_id": "model1"},
                {"name": "Stage 2", "model_id": "model2"}
            ],
            strategy="PARALLEL_ENSEMBLE",
            priority=8
        )
    """
    orchestrator = get_orchestrator()

    # Create pipeline executor
    executor_instance = PipelineTaskExecutor()

    # Submit task
    task_id = orchestrator.submit_task(
        name=f"Pipeline: {pipeline_id}",
        executor=executor_instance.execute_pipeline_task,
        priority=priority,
        task_type="pipeline",
        context={
            "pipeline_id": pipeline_id,
            "strategy": strategy,
            "stages": stages,
            "max_time": max_time,
            "max_cost": max_cost
        }
    )

    logger.info(f"Pipeline task submitted: {task_id} for pipeline {pipeline_id}")
    return task_id


def get_pipeline_task_result(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a pipeline task.

    Args:
        task_id: Task ID returned from submit_pipeline_task

    Returns:
        Dictionary with task status and pipeline result (if completed)
    """
    orchestrator = get_orchestrator()
    task_status = orchestrator.get_task_status(task_id)

    if not task_status:
        return {"error": "Task not found"}

    return task_status

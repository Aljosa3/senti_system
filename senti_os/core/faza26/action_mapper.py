"""
FAZA 26 - Intelligent Action Layer
Action Mapper

Maps planned tasks to FAZA 25 Orchestrator tasks.
Provides integration layer between FAZA 26 and FAZA 25.
"""

import asyncio
import logging
from typing import Dict, Any, List

from senti_os.core.faza25 import get_orchestrator, Task

logger = logging.getLogger(__name__)


class ActionMapper:
    """
    Maps semantic task plans to FAZA 25 orchestrator tasks.

    Responsibilities:
    - Convert FAZA 26 task specs to FAZA 25 Task objects
    - Submit tasks to FAZA 25 orchestrator
    - Track task submission and provide status
    """

    def __init__(self, orchestrator=None):
        """
        Initialize action mapper.

        Args:
            orchestrator: FAZA 25 OrchestratorManager instance (optional)
                         If not provided, will use get_orchestrator()
        """
        self.orchestrator = orchestrator or get_orchestrator()
        logger.info("ActionMapper initialized")

    async def map_and_submit(self, planned_tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Map planned tasks to orchestrator tasks and submit them.

        Args:
            planned_tasks: List of task specifications from SemanticPlanner

        Returns:
            List of FAZA 25 task IDs

        Raises:
            RuntimeError: If orchestrator is not running
            ValueError: If task mapping fails
        """
        if not self.orchestrator._is_running:
            raise RuntimeError("FAZA 25 Orchestrator is not running. Call start() first.")

        if not planned_tasks:
            logger.warning("No tasks to submit")
            return []

        task_ids = []

        for task_spec in planned_tasks:
            try:
                # Map task spec to executor
                executor = self._create_executor(task_spec)

                # Submit to FAZA 25
                task_id = self.orchestrator.submit_task(
                    name=task_spec["task"],
                    executor=executor,
                    priority=task_spec["priority"],
                    task_type=task_spec.get("metadata", {}).get("task_type", "generic"),
                    context=task_spec.get("metadata", {})
                )

                task_ids.append(task_id)
                logger.info(f"Submitted task: {task_spec['task']} (ID: {task_id[:8]})")

            except Exception as e:
                logger.error(f"Failed to map and submit task {task_spec.get('task', 'unknown')}: {e}")
                raise ValueError(f"Task mapping failed: {e}")

        logger.info(f"Successfully submitted {len(task_ids)} tasks to FAZA 25")
        return task_ids

    def _create_executor(self, task_spec: Dict[str, Any]) -> callable:
        """
        Create an async executor function for the task.

        Args:
            task_spec: Task specification

        Returns:
            Async executor function
        """
        task_name = task_spec["task"]
        metadata = task_spec.get("metadata", {})

        # Map task names to executor functions
        executor_map = {
            'fetch_data': self._executor_fetch_data,
            'compute_sentiment': self._executor_compute_sentiment,
            'aggregate_results': self._executor_aggregate_results,
            'generate_plot': self._executor_generate_plot,
            'compute': self._executor_compute,
            'load_data': self._executor_load_data,
            'transform_data': self._executor_transform_data,
            'validate_data': self._executor_validate_data,
            'save_data': self._executor_save_data,
            'load_model': self._executor_load_model,
            'preprocess_input': self._executor_preprocess_input,
            'run_inference': self._executor_run_inference,
            'postprocess_output': self._executor_postprocess_output,
            'execute_pipeline': self._executor_execute_pipeline,
        }

        executor_func = executor_map.get(task_name, self._executor_generic)

        # Return a closure that captures metadata
        async def executor(task: Task):
            return await executor_func(task)

        return executor

    # Executor implementations
    # These are placeholder implementations that can be replaced with actual logic

    async def _executor_fetch_data(self, task: Task) -> Dict[str, Any]:
        """Fetch data executor."""
        logger.info(f"Executing: fetch_data for {task.context.get('dataset', 'unknown')}")
        await asyncio.sleep(0.1)  # Simulate work
        return {
            "status": "success",
            "records_fetched": task.context.get("count", 100),
            "dataset": task.context.get("dataset", "default")
        }

    async def _executor_compute_sentiment(self, task: Task) -> Dict[str, Any]:
        """Compute sentiment executor."""
        logger.info(f"Executing: compute_sentiment with {task.context.get('algorithm', 'default')}")
        await asyncio.sleep(0.2)  # Simulate computation
        return {
            "status": "success",
            "sentiment_scores": [0.8, 0.6, 0.9],
            "algorithm": task.context.get("algorithm", "default")
        }

    async def _executor_aggregate_results(self, task: Task) -> Dict[str, Any]:
        """Aggregate results executor."""
        logger.info(f"Executing: aggregate_results using {task.context.get('aggregation_method', 'mean')}")
        await asyncio.sleep(0.05)
        return {
            "status": "success",
            "mean_sentiment": 0.75,
            "method": task.context.get("aggregation_method", "mean")
        }

    async def _executor_generate_plot(self, task: Task) -> Dict[str, Any]:
        """Generate plot executor."""
        logger.info(f"Executing: generate_plot type={task.context.get('plot_type', 'line')}")
        await asyncio.sleep(0.15)
        return {
            "status": "success",
            "plot_file": task.context.get("output", "plot.png"),
            "plot_type": task.context.get("plot_type", "line")
        }

    async def _executor_compute(self, task: Task) -> Dict[str, Any]:
        """Generic compute executor."""
        logger.info(f"Executing: compute type={task.context.get('compute_type', 'general')}")
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "result": 42,
            "compute_type": task.context.get("compute_type", "general")
        }

    async def _executor_load_data(self, task: Task) -> Dict[str, Any]:
        """Load data executor."""
        logger.info(f"Executing: load_data from {task.context.get('dataset', 'default')}")
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "dataset": task.context.get("dataset", "default"),
            "records": 1000
        }

    async def _executor_transform_data(self, task: Task) -> Dict[str, Any]:
        """Transform data executor."""
        logger.info(f"Executing: transform_data")
        await asyncio.sleep(0.15)
        return {
            "status": "success",
            "transformations": task.context.get("transformations", []),
            "records_transformed": 1000
        }

    async def _executor_validate_data(self, task: Task) -> Dict[str, Any]:
        """Validate data executor."""
        logger.info(f"Executing: validate_data")
        await asyncio.sleep(0.05)
        return {
            "status": "success",
            "validation_passed": True,
            "errors": 0
        }

    async def _executor_save_data(self, task: Task) -> Dict[str, Any]:
        """Save data executor."""
        logger.info(f"Executing: save_data to {task.context.get('output', 'output.csv')}")
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "output_file": task.context.get("output", "output.csv"),
            "records_saved": 1000
        }

    async def _executor_load_model(self, task: Task) -> Dict[str, Any]:
        """Load model executor."""
        logger.info(f"Executing: load_model {task.context.get('model_name', 'default')}")
        await asyncio.sleep(0.2)
        return {
            "status": "success",
            "model_name": task.context.get("model_name", "default"),
            "model_loaded": True
        }

    async def _executor_preprocess_input(self, task: Task) -> Dict[str, Any]:
        """Preprocess input executor."""
        logger.info(f"Executing: preprocess_input")
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "preprocessing_steps": task.context.get("preprocessing", []),
            "inputs_processed": 100
        }

    async def _executor_run_inference(self, task: Task) -> Dict[str, Any]:
        """Run inference executor."""
        logger.info(f"Executing: run_inference with {task.context.get('model_name', 'default')}")
        await asyncio.sleep(0.3)
        return {
            "status": "success",
            "model": task.context.get("model_name", "default"),
            "predictions": 100,
            "confidence": 0.92
        }

    async def _executor_postprocess_output(self, task: Task) -> Dict[str, Any]:
        """Postprocess output executor."""
        logger.info(f"Executing: postprocess_output")
        await asyncio.sleep(0.05)
        return {
            "status": "success",
            "postprocessing_steps": task.context.get("postprocessing", []),
            "outputs_processed": 100
        }

    async def _executor_execute_pipeline(self, task: Task) -> Dict[str, Any]:
        """Execute pipeline executor (integrates with FAZA 17)."""
        logger.info(f"Executing: pipeline {task.context.get('pipeline_id', 'unknown')}")

        # Import FAZA 17 integration
        from senti_os.core.faza25.pipeline_integration import submit_pipeline_task

        pipeline_id = task.context.get("pipeline_id", "default_pipeline")
        strategy = task.context.get("strategy", "LOCAL_FAST_PRECISE")

        # Submit to FAZA 17 via FAZA 25
        pipeline_task_id = submit_pipeline_task(
            pipeline_id=pipeline_id,
            stages=[
                {"name": "Stage 1", "model_id": "model1"},
                {"name": "Stage 2", "model_id": "model2"}
            ],
            strategy=strategy,
            priority=task.priority
        )

        await asyncio.sleep(0.5)  # Wait for pipeline

        return {
            "status": "success",
            "pipeline_id": pipeline_id,
            "pipeline_task_id": pipeline_task_id
        }

    async def _executor_generic(self, task: Task) -> Dict[str, Any]:
        """Generic task executor."""
        logger.info(f"Executing: generic task {task.name}")
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "task": task.name,
            "executed": True
        }


def create_action_mapper(orchestrator=None) -> ActionMapper:
    """
    Factory function to create an ActionMapper instance.

    Args:
        orchestrator: Optional FAZA 25 orchestrator instance

    Returns:
        ActionMapper instance
    """
    return ActionMapper(orchestrator=orchestrator)

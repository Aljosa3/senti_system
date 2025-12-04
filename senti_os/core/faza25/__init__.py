"""
FAZA 25 - Orchestration Execution Engine (OEE)

Provides task orchestration, execution, and management capabilities for Senti OS.

Key Components:
- Task Model: Task data structure with status tracking
- Priority Queue: Thread-safe task queue with priority ordering
- Workers: Asynchronous task execution workers
- Orchestrator: Main API for task management

Usage:
    from senti_os.core.faza25 import get_orchestrator

    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Start orchestrator
    await orchestrator.start()

    # Define task executor
    async def my_task_executor(task):
        print(f"Executing {task.name}")
        # Do work here
        return "result"

    # Submit task
    task_id = orchestrator.submit_task(
        name="My Task",
        executor=my_task_executor,
        priority=7
    )

    # Get task status
    status = orchestrator.get_task_status(task_id)
    print(status)

    # Stop orchestrator
    await orchestrator.stop()
"""

from senti_os.core.faza25.task_model import Task, TaskStatus
from senti_os.core.faza25.task_queue import PriorityTaskQueue
from senti_os.core.faza25.worker import TaskWorker, WorkerPool
from senti_os.core.faza25.orchestrator import OrchestratorManager, get_orchestrator
from senti_os.core.faza25.pipeline_integration import (
    PipelineTaskExecutor,
    submit_pipeline_task,
    get_pipeline_task_result
)


__all__ = [
    # Task Model
    "Task",
    "TaskStatus",

    # Queue
    "PriorityTaskQueue",

    # Workers
    "TaskWorker",
    "WorkerPool",

    # Orchestrator (main API)
    "OrchestratorManager",
    "get_orchestrator",

    # Pipeline Integration (FAZA 17)
    "PipelineTaskExecutor",
    "submit_pipeline_task",
    "get_pipeline_task_result",
]


__version__ = "1.0.0"
__author__ = "Senti System"
__description__ = "FAZA 25 - Orchestration Execution Engine"

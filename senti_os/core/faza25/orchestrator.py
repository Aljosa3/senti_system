"""
FAZA 25 - Orchestration Execution Engine
Orchestrator Manager

Main API for task orchestration, submission, and management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable

from senti_os.core.faza25.task_model import Task, TaskStatus
from senti_os.core.faza25.task_queue import PriorityTaskQueue
from senti_os.core.faza25.worker import WorkerPool


logger = logging.getLogger(__name__)


class OrchestratorManager:
    """
    Central orchestration manager for FAZA 25.

    Manages task submission, execution, cancellation, and status tracking.
    Coordinates workers and task queue.
    """

    def __init__(self, num_workers: int = 3):
        """
        Initialize orchestrator manager.

        Args:
            num_workers: Number of worker tasks to create (default: 3)
        """
        self.num_workers = num_workers
        self.task_queue = PriorityTaskQueue()
        self.worker_pool = WorkerPool(num_workers=num_workers, task_queue=self.task_queue)

        # Task registry: track all tasks by ID
        self.tasks: Dict[str, Task] = {}
        self._is_running = False
        self._lock = asyncio.Lock()

        logger.info(f"OrchestratorManager initialized with {num_workers} workers")

    async def start(self) -> None:
        """
        Start the orchestrator and all workers.
        """
        async with self._lock:
            if self._is_running:
                logger.warning("OrchestratorManager is already running")
                return

            logger.info("Starting OrchestratorManager")
            await self.worker_pool.start()
            self._is_running = True
            logger.info("OrchestratorManager started successfully")

    async def stop(self) -> None:
        """
        Stop the orchestrator and all workers.
        Waits for current tasks to complete.
        """
        async with self._lock:
            if not self._is_running:
                return

            logger.info("Stopping OrchestratorManager")
            await self.worker_pool.stop()
            self._is_running = False
            logger.info("OrchestratorManager stopped")

    def submit_task(
        self,
        name: str,
        executor: Callable[[Task], Awaitable[Any]],
        priority: int = 5,
        task_type: str = "generic",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a new task for execution.

        Args:
            name: Human-readable task name
            executor: Async function that executes the task
            priority: Priority level (0-10, higher = more important)
            task_type: Type of task (e.g., "pipeline", "generic", "service")
            context: Additional parameters for task execution

        Returns:
            Task ID
        """
        if not self._is_running:
            raise RuntimeError("OrchestratorManager is not running. Call start() first.")

        task = Task(
            name=name,
            executor=executor,
            priority=priority,
            task_type=task_type,
            context=context or {}
        )

        # Register task
        self.tasks[task.id] = task

        # Add to queue
        self.task_queue.put(task)

        logger.info(f"Task submitted: {task.id} ({task.name}) with priority {priority}")
        return task.id

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task by ID.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if task was cancelled, False if not found or already completed
        """
        task = self.tasks.get(task_id)

        if not task:
            logger.warning(f"Cannot cancel task {task_id}: not found")
            return False

        # If task is queued, remove from queue
        if task.status == TaskStatus.QUEUED:
            removed = self.task_queue.remove_task(task_id)
            if removed:
                logger.info(f"Task {task_id} cancelled (was in queue)")
                return True

        # If task is running, we can't cancel it directly
        # (would need more sophisticated cancellation mechanism)
        if task.status == TaskStatus.RUNNING:
            logger.warning(f"Task {task_id} is currently running and cannot be cancelled")
            return False

        # Already completed or cancelled
        logger.info(f"Task {task_id} is already in state {task.status.value}")
        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific task.

        Args:
            task_id: ID of task to query

        Returns:
            Task status dictionary or None if not found
        """
        task = self.tasks.get(task_id)
        if not task:
            return None

        return task.to_dict()

    def list_tasks(
        self,
        status_filter: Optional[TaskStatus] = None,
        task_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all tasks, optionally filtered by status or type.

        Args:
            status_filter: Filter by task status (optional)
            task_type_filter: Filter by task type (optional)

        Returns:
            List of task status dictionaries
        """
        tasks = list(self.tasks.values())

        # Apply filters
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]

        if task_type_filter:
            tasks = [t for t in tasks if t.task_type == task_type_filter]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return [task.to_dict() for task in tasks]

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.

        Returns:
            Dictionary with queue information
        """
        return {
            "queue_size": self.task_queue.size(),
            "is_empty": self.task_queue.is_empty(),
            "total_tasks": len(self.tasks),
            "tasks_by_status": {
                "queued": len([t for t in self.tasks.values() if t.status == TaskStatus.QUEUED]),
                "running": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
                "done": len([t for t in self.tasks.values() if t.status == TaskStatus.DONE]),
                "error": len([t for t in self.tasks.values() if t.status == TaskStatus.ERROR]),
                "cancelled": len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED])
            }
        }

    def get_worker_status(self) -> Dict[str, Any]:
        """
        Get current worker pool status.

        Returns:
            Dictionary with worker pool information
        """
        return self.worker_pool.get_status()

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get complete system status.

        Returns:
            Dictionary with orchestrator, queue, and worker status
        """
        return {
            "is_running": self._is_running,
            "num_workers": self.num_workers,
            "queue": self.get_queue_status(),
            "workers": self.get_worker_status()
        }

    def clear_completed_tasks(self, keep_recent: int = 100) -> int:
        """
        Clear completed/cancelled/error tasks from registry.
        Keeps the most recent N tasks for historical reference.

        Args:
            keep_recent: Number of recent tasks to keep

        Returns:
            Number of tasks cleared
        """
        completed_tasks = [
            t for t in self.tasks.values()
            if t.status in (TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED)
        ]

        # Sort by completion time
        completed_tasks.sort(key=lambda t: t.completed_at or t.created_at, reverse=True)

        # Remove old tasks
        to_remove = completed_tasks[keep_recent:]
        for task in to_remove:
            del self.tasks[task.id]

        if to_remove:
            logger.info(f"Cleared {len(to_remove)} completed tasks from registry")

        return len(to_remove)


# Global instance (singleton pattern)
_orchestrator_instance: Optional[OrchestratorManager] = None


def get_orchestrator() -> OrchestratorManager:
    """
    Get global orchestrator instance (singleton).

    Returns:
        OrchestratorManager instance
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorManager()

    return _orchestrator_instance

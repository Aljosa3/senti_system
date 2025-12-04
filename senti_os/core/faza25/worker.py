"""
FAZA 25 - Orchestration Execution Engine
Task Workers

Asynchronous worker implementation for task execution.
"""

import asyncio
import logging
from typing import Optional

from senti_os.core.faza25.task_model import Task, TaskStatus
from senti_os.core.faza25.task_queue import PriorityTaskQueue


logger = logging.getLogger(__name__)


class TaskWorker:
    """
    Asynchronous task worker that processes tasks from the priority queue.

    Each worker runs in its own asyncio task and continuously processes
    tasks from the queue until stopped.
    """

    def __init__(self, worker_id: int, task_queue: PriorityTaskQueue):
        """
        Initialize worker.

        Args:
            worker_id: Unique identifier for this worker
            task_queue: Priority queue to get tasks from
        """
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.is_running = False
        self.current_task: Optional[Task] = None
        self._task_handle: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """
        Start the worker.
        Creates an asyncio task that continuously processes tasks.
        """
        if self.is_running:
            logger.warning(f"Worker {self.worker_id} is already running")
            return

        self.is_running = True
        self._task_handle = asyncio.create_task(self._worker_loop())
        logger.info(f"Worker {self.worker_id} started")

    async def stop(self) -> None:
        """
        Stop the worker gracefully.
        Waits for current task to complete.
        """
        if not self.is_running:
            return

        self.is_running = False

        if self._task_handle and not self._task_handle.done():
            # Cancel the worker task
            self._task_handle.cancel()
            try:
                await self._task_handle
            except asyncio.CancelledError:
                pass

        logger.info(f"Worker {self.worker_id} stopped")

    async def _worker_loop(self) -> None:
        """
        Main worker loop.
        Continuously gets tasks from queue and executes them.
        """
        logger.debug(f"Worker {self.worker_id} entered main loop")

        while self.is_running:
            try:
                # Get next task from queue (waits if queue is empty)
                task = await self.task_queue.get()

                # Check if task was cancelled while in queue
                if task.status == TaskStatus.CANCELLED:
                    logger.info(f"Worker {self.worker_id}: Task {task.id} was cancelled")
                    continue

                # Execute the task
                await self._execute_task(task)

            except asyncio.CancelledError:
                logger.info(f"Worker {self.worker_id} was cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {self.worker_id} loop error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Prevent tight error loop

    async def _execute_task(self, task: Task) -> None:
        """
        Execute a single task.

        Args:
            task: Task to execute
        """
        self.current_task = task

        try:
            logger.info(f"Worker {self.worker_id}: Starting task {task.id} ({task.name})")

            # Mark task as running
            task.mark_running()

            # Execute the task
            result = await task.run()

            # Mark task as done
            task.mark_done(result)

            logger.info(f"Worker {self.worker_id}: Task {task.id} completed successfully")

        except asyncio.CancelledError:
            # Task was cancelled during execution
            task.mark_cancelled()
            logger.warning(f"Worker {self.worker_id}: Task {task.id} was cancelled during execution")
            raise

        except Exception as e:
            # Task execution failed
            error_msg = f"{type(e).__name__}: {str(e)}"
            task.mark_error(error_msg)
            logger.error(f"Worker {self.worker_id}: Task {task.id} failed: {error_msg}", exc_info=True)

        finally:
            self.current_task = None

    def get_status(self) -> dict:
        """
        Get current worker status.

        Returns:
            Dictionary with worker status information
        """
        return {
            "worker_id": self.worker_id,
            "is_running": self.is_running,
            "current_task": self.current_task.to_dict() if self.current_task else None
        }


class WorkerPool:
    """
    Pool of task workers.
    Manages multiple workers and their lifecycle.
    """

    def __init__(self, num_workers: int, task_queue: PriorityTaskQueue):
        """
        Initialize worker pool.

        Args:
            num_workers: Number of workers to create
            task_queue: Priority queue for tasks
        """
        self.num_workers = num_workers
        self.task_queue = task_queue
        self.workers: list[TaskWorker] = []

    async def start(self) -> None:
        """
        Start all workers in the pool.
        """
        logger.info(f"Starting worker pool with {self.num_workers} workers")

        for i in range(self.num_workers):
            worker = TaskWorker(worker_id=i, task_queue=self.task_queue)
            await worker.start()
            self.workers.append(worker)

        logger.info(f"Worker pool started with {len(self.workers)} workers")

    async def stop(self) -> None:
        """
        Stop all workers in the pool.
        """
        logger.info("Stopping worker pool")

        stop_tasks = [worker.stop() for worker in self.workers]
        await asyncio.gather(*stop_tasks, return_exceptions=True)

        self.workers.clear()
        logger.info("Worker pool stopped")

    def get_status(self) -> dict:
        """
        Get status of all workers.

        Returns:
            Dictionary with worker pool status
        """
        return {
            "num_workers": len(self.workers),
            "workers": [worker.get_status() for worker in self.workers]
        }

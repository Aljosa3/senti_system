"""
FAZA 25 - Orchestration Execution Engine
Priority Task Queue

Thread-safe priority queue implementation using heapq.
Higher priority tasks are executed first.
"""

import asyncio
import heapq
import threading
from typing import Optional

from senti_os.core.faza25.task_model import Task, TaskStatus


class PriorityTaskQueue:
    """
    Thread-safe priority queue for tasks.

    Uses heapq to maintain priority ordering.
    Higher priority values (e.g., 10) are executed before lower values (e.g., 1).
    """

    def __init__(self):
        self._heap = []
        self._lock = threading.Lock()
        self._condition = asyncio.Condition()
        self._counter = 0  # Tie-breaker for tasks with same priority

    def put(self, task: Task) -> None:
        """
        Add a task to the priority queue.
        Thread-safe operation.

        Args:
            task: Task to add to queue
        """
        with self._lock:
            # heapq is a min-heap, but we want max priority first
            # Task.__lt__ handles priority inversion
            # Counter ensures FIFO for same-priority tasks
            heapq.heappush(self._heap, (task, self._counter))
            self._counter += 1

    def get_nowait(self) -> Optional[Task]:
        """
        Get highest priority task from queue without waiting.
        Thread-safe operation.

        Returns:
            Highest priority task or None if queue is empty
        """
        with self._lock:
            if not self._heap:
                return None
            task, _ = heapq.heappop(self._heap)
            return task

    async def get(self) -> Task:
        """
        Get highest priority task from queue.
        Waits asynchronously if queue is empty.

        Returns:
            Highest priority task
        """
        while True:
            task = self.get_nowait()
            if task is not None:
                return task
            # Wait a bit before checking again
            await asyncio.sleep(0.1)

    def size(self) -> int:
        """
        Get current queue size.
        Thread-safe operation.

        Returns:
            Number of tasks in queue
        """
        with self._lock:
            return len(self._heap)

    def is_empty(self) -> bool:
        """
        Check if queue is empty.
        Thread-safe operation.

        Returns:
            True if queue is empty
        """
        with self._lock:
            return len(self._heap) == 0

    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the queue by ID.
        Thread-safe operation.

        Args:
            task_id: ID of task to remove

        Returns:
            True if task was found and removed, False otherwise
        """
        with self._lock:
            for i, (task, counter) in enumerate(self._heap):
                if task.id == task_id:
                    # Mark task as cancelled
                    task.mark_cancelled()
                    # Remove from heap and re-heapify
                    self._heap.pop(i)
                    heapq.heapify(self._heap)
                    return True
            return False

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks currently in queue (for inspection).
        Thread-safe operation.

        Returns:
            List of all tasks in queue
        """
        with self._lock:
            return [task for task, _ in self._heap]

    def clear(self) -> None:
        """
        Clear all tasks from queue.
        Thread-safe operation.
        """
        with self._lock:
            # Mark all tasks as cancelled
            for task, _ in self._heap:
                if task.status == TaskStatus.QUEUED:
                    task.mark_cancelled()
            self._heap.clear()
            self._counter = 0

"""
Priority Queue for SENTI OS FAZA 17

This module manages task prioritization and scheduling:
- Three priority levels: HIGH, NORMAL, LOW
- Resource allocation based on priority
- Fair scheduling with starvation prevention
- Queue statistics and monitoring

Ensures critical tasks are processed first while preventing task starvation.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import heapq


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Priority levels for tasks."""
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class QueuedTask:
    """Represents a task in the queue."""
    task_id: str
    priority: Priority
    submission_time: datetime
    estimated_duration: int
    max_cost: float
    metadata: Dict = field(default_factory=dict)
    retries: int = 0
    max_retries: int = 3

    def __lt__(self, other):
        """Compare tasks for heap ordering."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value

        return self.submission_time < other.submission_time


@dataclass
class QueueStatistics:
    """Statistics about the queue."""
    total_enqueued: int
    total_dequeued: int
    total_completed: int
    total_failed: int
    current_size: int
    average_wait_time: float
    tasks_by_priority: Dict[str, int]


class PriorityQueue:
    """
    Priority-based task queue for SENTI OS orchestration.

    This queue ensures high-priority tasks are processed first while
    preventing low-priority task starvation through aging mechanisms.
    """

    STARVATION_THRESHOLD_SECONDS = 300
    MAX_QUEUE_SIZE = 1000

    def __init__(self):
        """Initialize the priority queue."""
        self.queue: List[QueuedTask] = []
        self.in_progress: Dict[str, QueuedTask] = {}
        self.completed: List[QueuedTask] = []
        self.failed: List[QueuedTask] = []

        self.total_enqueued = 0
        self.total_dequeued = 0

        logger.info("Priority Queue initialized")

    def enqueue(self, task: QueuedTask) -> bool:
        """
        Add a task to the queue.

        Args:
            task: QueuedTask to add

        Returns:
            True if enqueued, False if queue is full
        """
        if len(self.queue) >= self.MAX_QUEUE_SIZE:
            logger.warning(f"Queue full, cannot enqueue task {task.task_id}")
            return False

        heapq.heappush(self.queue, task)
        self.total_enqueued += 1

        logger.debug(f"Task {task.task_id} enqueued with priority {task.priority.value}")
        return True

    def dequeue(self) -> Optional[QueuedTask]:
        """
        Remove and return the highest priority task.

        Returns:
            QueuedTask if available, None if queue is empty
        """
        self._apply_aging()

        if not self.queue:
            return None

        task = heapq.heappop(self.queue)
        self.in_progress[task.task_id] = task
        self.total_dequeued += 1

        logger.debug(f"Task {task.task_id} dequeued")
        return task

    def mark_completed(self, task_id: str) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of completed task

        Returns:
            True if marked, False if not found
        """
        if task_id in self.in_progress:
            task = self.in_progress.pop(task_id)
            self.completed.append(task)
            logger.info(f"Task {task_id} marked as completed")
            return True

        logger.warning(f"Task {task_id} not found in progress")
        return False

    def mark_failed(self, task_id: str, retry: bool = True) -> bool:
        """
        Mark a task as failed.

        Args:
            task_id: ID of failed task
            retry: Whether to retry the task

        Returns:
            True if marked, False if not found
        """
        if task_id not in self.in_progress:
            logger.warning(f"Task {task_id} not found in progress")
            return False

        task = self.in_progress.pop(task_id)

        if retry and task.retries < task.max_retries:
            task.retries += 1
            logger.info(f"Task {task_id} failed, retry {task.retries}/{task.max_retries}")
            self.enqueue(task)
        else:
            self.failed.append(task)
            logger.warning(f"Task {task_id} failed permanently")

        return True

    def _apply_aging(self) -> None:
        """
        Apply priority aging to prevent starvation.

        Low-priority tasks that have waited too long get priority boost.
        """
        current_time = datetime.now()
        threshold = timedelta(seconds=self.STARVATION_THRESHOLD_SECONDS)

        aged_tasks = []

        for task in self.queue:
            wait_time = current_time - task.submission_time

            if wait_time > threshold and task.priority != Priority.HIGH:
                if task.priority == Priority.LOW:
                    task.priority = Priority.NORMAL
                    logger.debug(f"Task {task.task_id} priority boosted: LOW -> NORMAL")
                elif task.priority == Priority.NORMAL:
                    task.priority = Priority.HIGH
                    logger.debug(f"Task {task.task_id} priority boosted: NORMAL -> HIGH")

        if aged_tasks:
            heapq.heapify(self.queue)

    def get_position(self, task_id: str) -> Optional[int]:
        """
        Get position of a task in the queue.

        Args:
            task_id: ID of task

        Returns:
            Position (0-indexed) or None if not found
        """
        for i, task in enumerate(sorted(self.queue)):
            if task.task_id == task_id:
                return i

        return None

    def get_task(self, task_id: str) -> Optional[QueuedTask]:
        """
        Get a task by ID from any collection.

        Args:
            task_id: ID of task

        Returns:
            QueuedTask if found, None otherwise
        """
        for task in self.queue:
            if task.task_id == task_id:
                return task

        if task_id in self.in_progress:
            return self.in_progress[task_id]

        for task in self.completed:
            if task.task_id == task_id:
                return task

        for task in self.failed:
            if task.task_id == task_id:
                return task

        return None

    def peek(self) -> Optional[QueuedTask]:
        """
        View the next task without removing it.

        Returns:
            Next QueuedTask or None if empty
        """
        if not self.queue:
            return None

        return min(self.queue)

    def size(self) -> int:
        """
        Get current queue size.

        Returns:
            Number of tasks in queue
        """
        return len(self.queue)

    def is_empty(self) -> bool:
        """
        Check if queue is empty.

        Returns:
            True if empty, False otherwise
        """
        return len(self.queue) == 0

    def clear(self) -> None:
        """Clear all tasks from the queue."""
        self.queue.clear()
        logger.info("Queue cleared")

    def get_statistics(self) -> QueueStatistics:
        """
        Get queue statistics.

        Returns:
            QueueStatistics instance
        """
        tasks_by_priority = {
            "high": sum(1 for t in self.queue if t.priority == Priority.HIGH),
            "normal": sum(1 for t in self.queue if t.priority == Priority.NORMAL),
            "low": sum(1 for t in self.queue if t.priority == Priority.LOW),
        }

        wait_times = [
            (datetime.now() - task.submission_time).total_seconds()
            for task in self.queue
        ]
        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0

        return QueueStatistics(
            total_enqueued=self.total_enqueued,
            total_dequeued=self.total_dequeued,
            total_completed=len(self.completed),
            total_failed=len(self.failed),
            current_size=len(self.queue),
            average_wait_time=round(avg_wait, 2),
            tasks_by_priority=tasks_by_priority,
        )

    def get_tasks_by_priority(self, priority: Priority) -> List[QueuedTask]:
        """
        Get all tasks with specific priority.

        Args:
            priority: Priority level to filter

        Returns:
            List of matching tasks
        """
        return [task for task in self.queue if task.priority == priority]

    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the queue.

        Args:
            task_id: ID of task to remove

        Returns:
            True if removed, False if not found
        """
        for i, task in enumerate(self.queue):
            if task.task_id == task_id:
                self.queue.pop(i)
                heapq.heapify(self.queue)
                logger.info(f"Task {task_id} removed from queue")
                return True

        return False

    def update_priority(self, task_id: str, new_priority: Priority) -> bool:
        """
        Update priority of a queued task.

        Args:
            task_id: ID of task
            new_priority: New priority level

        Returns:
            True if updated, False if not found
        """
        for task in self.queue:
            if task.task_id == task_id:
                old_priority = task.priority
                task.priority = new_priority
                heapq.heapify(self.queue)
                logger.info(f"Task {task_id} priority updated: {old_priority.value} -> {new_priority.value}")
                return True

        return False


def create_queue() -> PriorityQueue:
    """
    Create and return a priority queue.

    Returns:
        Configured PriorityQueue instance
    """
    queue = PriorityQueue()
    logger.info("Priority Queue created")
    return queue

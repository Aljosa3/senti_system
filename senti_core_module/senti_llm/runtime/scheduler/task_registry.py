"""
FAZA 43 — Task Registry
------------------------
Manages all scheduled tasks in the Senti OS Runtime.

Responsibilities:
- Register and unregister tasks
- Query tasks by ID or type
- List event handlers
- Maintain task state

Design:
- Thread-safe operations (with lock)
- Fast lookups by ID
- Event handler indexing
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from .task import Task, TaskType


class TaskRegistry:
    """
    Registry for managing scheduled tasks.

    Maintains:
    - tasks_by_id: Fast ID lookup
    - event_handlers: Index of event -> tasks
    """

    def __init__(self):
        """Initialize task registry."""
        self._tasks_by_id: Dict[str, Task] = {}
        self._event_handlers: Dict[str, List[Task]] = {}
        self._lock = threading.Lock()

    def register(self, task: Task) -> None:
        """
        Register a task.

        Args:
            task: Task to register
        """
        try:
            with self._lock:
                # Store in main registry
                self._tasks_by_id[task.id] = task

                # Index event handlers
                if task.type == TaskType.EVENT and task.event_type:
                    if task.event_type not in self._event_handlers:
                        self._event_handlers[task.event_type] = []

                    self._event_handlers[task.event_type].append(task)

        except Exception:
            # Never throw from registry operations
            pass

    def unregister(self, task_id: str) -> bool:
        """
        Unregister a task by ID.

        Args:
            task_id: Task ID to remove

        Returns:
            True if task was removed
        """
        try:
            with self._lock:
                task = self._tasks_by_id.get(task_id)

                if not task:
                    return False

                # Remove from main registry
                del self._tasks_by_id[task_id]

                # Remove from event handler index
                if task.type == TaskType.EVENT and task.event_type:
                    if task.event_type in self._event_handlers:
                        self._event_handlers[task.event_type] = [
                            t for t in self._event_handlers[task.event_type]
                            if t.id != task_id
                        ]

                        # Clean up empty lists
                        if not self._event_handlers[task.event_type]:
                            del self._event_handlers[task.event_type]

                return True

        except Exception:
            return False

    def get(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task instance or None
        """
        try:
            with self._lock:
                return self._tasks_by_id.get(task_id)
        except Exception:
            return None

    def list(self) -> List[Task]:
        """
        List all tasks.

        Returns:
            List of all registered tasks
        """
        try:
            with self._lock:
                return list(self._tasks_by_id.values())
        except Exception:
            return []

    def list_due_tasks(self, now_timestamp: float) -> List[Task]:
        """
        List all tasks due for execution.

        Args:
            now_timestamp: Current timestamp

        Returns:
            List of tasks that should execute
        """
        try:
            with self._lock:
                return [
                    task for task in self._tasks_by_id.values()
                    if task.due(now_timestamp)
                ]
        except Exception:
            return []

    def list_event_handlers(self, event_type: str) -> List[Task]:
        """
        List all event handlers for an event type.

        Args:
            event_type: Event type identifier

        Returns:
            List of tasks registered for this event
        """
        try:
            with self._lock:
                handlers = self._event_handlers.get(event_type, [])
                # Only return enabled handlers
                return [task for task in handlers if task.enabled]
        except Exception:
            return []

    def count(self) -> int:
        """
        Count total registered tasks.

        Returns:
            Number of tasks
        """
        try:
            with self._lock:
                return len(self._tasks_by_id)
        except Exception:
            return 0

    def count_enabled(self) -> int:
        """
        Count enabled tasks.

        Returns:
            Number of enabled tasks
        """
        try:
            with self._lock:
                return sum(1 for task in self._tasks_by_id.values() if task.enabled)
        except Exception:
            return 0

    def clear(self):
        """Clear all tasks (use with caution)."""
        try:
            with self._lock:
                self._tasks_by_id.clear()
                self._event_handlers.clear()
        except Exception:
            pass

    def get_stats(self) -> Dict[str, any]:
        """
        Get registry statistics.

        Returns:
            Stats dict
        """
        try:
            with self._lock:
                return {
                    "total_tasks": len(self._tasks_by_id),
                    "enabled_tasks": sum(1 for t in self._tasks_by_id.values() if t.enabled),
                    "event_types": len(self._event_handlers),
                    "failed_tasks": sum(1 for t in self._tasks_by_id.values() if t.failure_count > 0)
                }
        except Exception:
            return {}

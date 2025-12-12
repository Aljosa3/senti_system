"""
FAZA 43 — Task Definition
--------------------------
Represents a schedulable task in the Senti OS Runtime.

Task Types:
- interval: Repeating task at fixed intervals
- oneshot: Single execution after delay
- event: Triggered by event publication
- system: Internal system tasks

Design:
- Immutable after creation (except enabled flag)
- Serializable to/from dict
- UUID-based identification
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Dict, Optional
from enum import Enum


class TaskType(Enum):
    """Task type enumeration."""
    INTERVAL = "interval"
    ONESHOT = "oneshot"
    EVENT = "event"
    SYSTEM = "system"


class Task:
    """
    Represents a schedulable task.

    Attributes:
        id: Unique task identifier (UUID)
        type: Task type (interval, oneshot, event, system)
        callable: Python function to execute
        interval: Time interval for repeating tasks (seconds)
        event_type: Event type for event-triggered tasks
        next_run: Timestamp of next execution
        enabled: Whether task is active
        metadata: Additional task metadata
        failure_count: Number of consecutive failures
        last_error: Last error message (if any)
    """

    def __init__(
        self,
        task_type: TaskType,
        callable_fn: Callable,
        interval: Optional[float] = None,
        event_type: Optional[str] = None,
        next_run: Optional[float] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a task.

        Args:
            task_type: Type of task
            callable_fn: Function to execute
            interval: Interval for repeating tasks (seconds)
            event_type: Event type for event-triggered tasks
            next_run: Scheduled execution time (timestamp)
            task_id: Optional custom task ID
            metadata: Optional metadata dict
        """
        self.id = task_id or str(uuid.uuid4())
        self.type = task_type
        self.callable = callable_fn
        self.interval = interval
        self.event_type = event_type
        self.next_run = next_run if next_run is not None else time.time()
        self.enabled = True
        self.metadata = metadata or {}
        self.failure_count = 0
        self.last_error: Optional[str] = None

        # Validation
        if self.type == TaskType.INTERVAL and self.interval is None:
            raise ValueError("Interval tasks require interval parameter")

        if self.type == TaskType.EVENT and self.event_type is None:
            raise ValueError("Event tasks require event_type parameter")

    def due(self, now_timestamp: float) -> bool:
        """
        Check if task is due for execution.

        Args:
            now_timestamp: Current timestamp

        Returns:
            True if task should be executed
        """
        if not self.enabled:
            return False

        # Event tasks are not time-based
        if self.type == TaskType.EVENT:
            return False

        return now_timestamp >= self.next_run

    def reschedule(self, now_timestamp: float):
        """
        Reschedule task for next execution.

        Args:
            now_timestamp: Current timestamp
        """
        if self.type == TaskType.INTERVAL and self.interval:
            # Schedule next interval
            self.next_run = now_timestamp + self.interval

        elif self.type == TaskType.ONESHOT:
            # Oneshot tasks disable after execution
            self.enabled = False

    def mark_success(self):
        """Mark task execution as successful."""
        self.failure_count = 0
        self.last_error = None

    def mark_failure(self, error: str):
        """
        Mark task execution as failed.

        Args:
            error: Error message
        """
        self.failure_count += 1
        self.last_error = error

        # Auto-disable after 3 consecutive failures
        if self.failure_count >= 3:
            self.enabled = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dict.

        Returns:
            Dict representation (callable not included)
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "interval": self.interval,
            "event_type": self.event_type,
            "next_run": self.next_run,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "failure_count": self.failure_count,
            "last_error": self.last_error
        }

    @staticmethod
    def from_dict(data: Dict[str, Any], callable_fn: Callable) -> Task:
        """
        Deserialize task from dict.

        Args:
            data: Dict representation
            callable_fn: Callable to attach to task

        Returns:
            Task instance
        """
        task_type = TaskType(data["type"])

        task = Task(
            task_type=task_type,
            callable_fn=callable_fn,
            interval=data.get("interval"),
            event_type=data.get("event_type"),
            next_run=data.get("next_run"),
            task_id=data.get("id"),
            metadata=data.get("metadata", {})
        )

        task.enabled = data.get("enabled", True)
        task.failure_count = data.get("failure_count", 0)
        task.last_error = data.get("last_error")

        return task

    def __repr__(self) -> str:
        """String representation."""
        return f"<Task id={self.id[:8]} type={self.type.value} enabled={self.enabled}>"

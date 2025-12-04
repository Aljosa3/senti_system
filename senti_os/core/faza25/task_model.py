"""
FAZA 25 - Orchestration Execution Engine
Task Model Definition

Defines the Task data structure and status enumeration.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Callable, Awaitable


class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    Task model for orchestration execution.

    Attributes:
        id: Unique task identifier
        name: Human-readable task name
        status: Current execution status
        priority: Priority level (0-10, higher = more important)
        created_at: Task creation timestamp
        started_at: Task execution start timestamp
        completed_at: Task completion timestamp
        error_message: Error description if status is ERROR
        context: Additional parameters and data for task execution
        task_type: Type of task (e.g., "pipeline", "generic", "service")
        executor: Async function to execute the task
    """
    name: str
    executor: Callable[['Task'], Awaitable[Any]]
    priority: int = 5
    task_type: str = "generic"
    context: Dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = field(default=TaskStatus.QUEUED)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Any = None

    def __lt__(self, other: 'Task') -> bool:
        """
        Comparison for priority queue (heapq).
        Higher priority = lower number in heap (inverted priority).
        """
        return self.priority > other.priority

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority,
            "task_type": self.task_type,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "context": self.context,
            "has_result": self.result is not None
        }

    def mark_running(self) -> None:
        """Mark task as running"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

    def mark_done(self, result: Any = None) -> None:
        """Mark task as successfully completed"""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.result = result

    def mark_error(self, error_message: str) -> None:
        """Mark task as failed with error"""
        self.status = TaskStatus.ERROR
        self.completed_at = datetime.now()
        self.error_message = error_message

    def mark_cancelled(self) -> None:
        """Mark task as cancelled"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()

    async def run(self) -> Any:
        """
        Execute the task.
        Calls the executor function with self as parameter.
        """
        return await self.executor(self)

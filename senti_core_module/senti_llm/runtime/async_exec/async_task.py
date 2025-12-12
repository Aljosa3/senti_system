"""
FAZA 44 — Async Task Definition
--------------------------------
Represents an asynchronous task in the Senti OS Runtime.

Features:
- AsyncTaskStatus enum for task lifecycle
- Coroutine execution with local asyncio loop
- Step-based execution (cooperative)
- Result/error tracking
- Serialization support

Design:
- Never crashes runtime (all exceptions caught)
- Cooperative execution (step() method)
- Cancellable at any time
- Serializable state
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Callable, Coroutine, Dict, Optional
from enum import Enum


class AsyncTaskStatus(Enum):
    """Async task status enumeration."""
    PENDING = "pending"      # Task created, not started
    RUNNING = "running"      # Task is executing
    COMPLETED = "completed"  # Task finished successfully
    FAILED = "failed"        # Task failed with error
    CANCELLED = "cancelled"  # Task was cancelled


class AsyncTask:
    """
    Represents an asynchronous task.

    Attributes:
        id: Unique task identifier (UUID)
        status: Current task status
        coroutine: Python coroutine to execute
        result: Task result (if completed)
        error: Error message (if failed)
        metadata: Additional task metadata
        created_at: Task creation timestamp
        started_at: Task start timestamp
        completed_at: Task completion timestamp
    """

    def __init__(
        self,
        coroutine: Coroutine,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an async task.

        Args:
            coroutine: Coroutine to execute
            task_id: Optional custom task ID
            metadata: Optional metadata dict
        """
        self.id = task_id or str(uuid.uuid4())
        self.status = AsyncTaskStatus.PENDING
        self.coroutine = coroutine
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.metadata = metadata or {}

        # Timestamps
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

        # Asyncio internals
        self._asyncio_task: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        Start the async task execution.

        Args:
            loop: Asyncio event loop to use (creates new if None)
        """
        try:
            if self.status != AsyncTaskStatus.PENDING:
                return

            # Get or create event loop
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    # No running loop, create new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

            self._loop = loop

            # Create asyncio task
            self._asyncio_task = loop.create_task(self.coroutine)

            # Update status
            self.status = AsyncTaskStatus.RUNNING
            self.started_at = time.time()

        except Exception as e:
            self.mark_failure(str(e))

    def step(self) -> bool:
        """
        Execute one step of the async task (cooperative).

        Returns:
            True if task is still running, False if done
        """
        try:
            # Check if task started
            if self.status == AsyncTaskStatus.PENDING:
                return True  # Still pending, not started

            if self.status in [AsyncTaskStatus.COMPLETED, AsyncTaskStatus.FAILED, AsyncTaskStatus.CANCELLED]:
                return False  # Task already finished

            # Check if asyncio task exists
            if not self._asyncio_task:
                self.mark_failure("AsyncIO task not initialized")
                return False

            # Check if task is done
            if self._asyncio_task.done():
                try:
                    result = self._asyncio_task.result()
                    self.mark_success(result)
                except asyncio.CancelledError:
                    self.status = AsyncTaskStatus.CANCELLED
                    self.completed_at = time.time()
                except Exception as e:
                    self.mark_failure(str(e))

                return False

            # Task still running
            return True

        except Exception as e:
            self.mark_failure(f"Step error: {e}")
            return False

    def cancel(self) -> bool:
        """
        Cancel the async task.

        Returns:
            True if task was cancelled
        """
        try:
            if self.status in [AsyncTaskStatus.COMPLETED, AsyncTaskStatus.FAILED, AsyncTaskStatus.CANCELLED]:
                return False  # Already finished

            # Cancel asyncio task
            if self._asyncio_task and not self._asyncio_task.done():
                self._asyncio_task.cancel()

            self.status = AsyncTaskStatus.CANCELLED
            self.completed_at = time.time()
            return True

        except Exception:
            return False

    def mark_success(self, result: Any = None):
        """
        Mark task as successfully completed.

        Args:
            result: Task result
        """
        self.status = AsyncTaskStatus.COMPLETED
        self.result = result
        self.completed_at = time.time()

    def mark_failure(self, error: str):
        """
        Mark task as failed.

        Args:
            error: Error message
        """
        self.status = AsyncTaskStatus.FAILED
        self.error = error
        self.completed_at = time.time()

    def is_done(self) -> bool:
        """
        Check if task is finished (completed, failed, or cancelled).

        Returns:
            True if task is done
        """
        return self.status in [
            AsyncTaskStatus.COMPLETED,
            AsyncTaskStatus.FAILED,
            AsyncTaskStatus.CANCELLED
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dict.

        Returns:
            Dict representation (coroutine not included)
        """
        return {
            "id": self.id,
            "status": self.status.value,
            "result": self.result if self.status == AsyncTaskStatus.COMPLETED else None,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "is_done": self.is_done()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any], coroutine: Coroutine) -> AsyncTask:
        """
        Deserialize task from dict.

        Args:
            data: Dict representation
            coroutine: Coroutine to attach to task

        Returns:
            AsyncTask instance
        """
        task = AsyncTask(
            coroutine=coroutine,
            task_id=data.get("id"),
            metadata=data.get("metadata", {})
        )

        task.status = AsyncTaskStatus(data.get("status", "pending"))
        task.result = data.get("result")
        task.error = data.get("error")
        task.created_at = data.get("created_at", time.time())
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")

        return task

    def __repr__(self) -> str:
        """String representation."""
        return f"<AsyncTask id={self.id[:8]} status={self.status.value}>"

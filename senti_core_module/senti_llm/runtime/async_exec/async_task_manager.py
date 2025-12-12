"""
FAZA 44 — Async Task Manager
-----------------------------
Manages execution of asynchronous tasks in the Senti OS Runtime.

Features:
- Local asyncio event loop management
- Task registry (pending/running/completed)
- Concurrency limits (16 running, 128 pending)
- Cooperative tick() execution
- Event-triggered async tasks
- Never crashes runtime

Design:
- MAX_TASKS_PER_TICK = 10 (safety limit)
- Automatic task cleanup on completion
- EventBus integration for async events
- All exceptions caught
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any, Coroutine, Dict, List, Optional, TYPE_CHECKING

from .async_task import AsyncTask, AsyncTaskStatus

if TYPE_CHECKING:
    from ..event_bus import EventBus


class AsyncTaskManager:
    """
    Manager for asynchronous task execution.

    Maintains:
    - tasks_by_id: Fast ID lookup
    - pending_tasks: Queue of tasks waiting to start
    - running_tasks: Currently executing tasks
    - event_handlers: Async event handler registry
    """

    # Safety and concurrency limits
    MAX_TASKS_PER_TICK = 10
    MAX_RUNNING_TASKS = 16
    MAX_PENDING_TASKS = 128

    def __init__(self, event_bus: Optional['EventBus'] = None):
        """
        Initialize async task manager.

        Args:
            event_bus: Optional EventBus for publishing async events
        """
        # Task storage
        self._tasks_by_id: Dict[str, AsyncTask] = {}
        self._pending_tasks: List[AsyncTask] = []
        self._running_tasks: List[AsyncTask] = []
        self._event_handlers: Dict[str, List[Coroutine]] = {}

        # Thread safety
        self._lock = threading.Lock()

        # EventBus integration
        self.event_bus = event_bus

        # Asyncio loop (lazy-initialized)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._tick_count = 0

    def _ensure_loop(self):
        """Ensure asyncio event loop exists."""
        try:
            if self._loop is None:
                try:
                    self._loop = asyncio.get_running_loop()
                except RuntimeError:
                    # No running loop, create new one
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
        except Exception:
            # Fallback: create new loop
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    def create_task(
        self,
        coroutine: Coroutine,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new async task.

        Args:
            coroutine: Coroutine to execute
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            with self._lock:
                # Check pending queue limit
                if len(self._pending_tasks) >= self.MAX_PENDING_TASKS:
                    # Reject task if queue is full
                    return ""

                # Create task
                task = AsyncTask(coroutine=coroutine, metadata=metadata)

                # Add to registry and pending queue
                self._tasks_by_id[task.id] = task
                self._pending_tasks.append(task)

                return task.id

        except Exception:
            return ""

    def tick(self, now_timestamp: Optional[float] = None):
        """
        Execute async task manager tick.

        Processes:
        1. Start pending tasks (up to concurrency limit)
        2. Step running tasks (up to MAX_TASKS_PER_TICK)
        3. Clean up completed tasks
        4. Publish system events

        Args:
            now_timestamp: Current timestamp (defaults to time.time())
        """
        try:
            if now_timestamp is None:
                now_timestamp = time.time()

            self._tick_count += 1

            # Ensure event loop exists
            self._ensure_loop()

            with self._lock:
                # 1) Start pending tasks (up to concurrency limit)
                while (
                    len(self._running_tasks) < self.MAX_RUNNING_TASKS
                    and len(self._pending_tasks) > 0
                ):
                    task = self._pending_tasks.pop(0)
                    task.start(self._loop)
                    self._running_tasks.append(task)

                # 2) Step running tasks (up to MAX_TASKS_PER_TICK)
                tasks_to_step = self._running_tasks[:self.MAX_TASKS_PER_TICK]

                # Process asyncio loop events (non-blocking)
                if self._loop:
                    try:
                        self._loop.stop()
                        self._loop.run_until_complete(asyncio.sleep(0))
                    except Exception:
                        pass

                # Step each task
                for task in tasks_to_step:
                    try:
                        still_running = task.step()

                        if not still_running:
                            # Task finished, remove from running
                            if task in self._running_tasks:
                                self._running_tasks.remove(task)

                            # Publish completion event
                            self._publish_task_event(task)

                    except Exception:
                        # Task step failed, mark as failed
                        task.mark_failure("Task step exception")
                        if task in self._running_tasks:
                            self._running_tasks.remove(task)

                # 3) Cleanup: remove old completed tasks (keep last 100)
                self._cleanup_old_tasks()

            # Publish tick event
            self._publish_tick_event(now_timestamp)

        except Exception:
            # Never crash on tick
            pass

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task by ID.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled
        """
        try:
            with self._lock:
                task = self._tasks_by_id.get(task_id)

                if not task:
                    return False

                # Remove from pending queue if present
                if task in self._pending_tasks:
                    self._pending_tasks.remove(task)

                # Remove from running list if present
                if task in self._running_tasks:
                    self._running_tasks.remove(task)

                # Cancel the task
                return task.cancel()

        except Exception:
            return False

    def get(self, task_id: str) -> Optional[AsyncTask]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            AsyncTask instance or None
        """
        try:
            with self._lock:
                return self._tasks_by_id.get(task_id)
        except Exception:
            return None

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tasks (serialized).

        Args:
            status: Optional status filter

        Returns:
            List of task dicts
        """
        try:
            with self._lock:
                tasks = list(self._tasks_by_id.values())

                if status:
                    tasks = [t for t in tasks if t.status.value == status]

                return [task.to_dict() for task in tasks]

        except Exception:
            return []

    def trigger_event(self, event_type: str, event_context: Any):
        """
        Trigger async event handlers for an event.

        Args:
            event_type: Event type
            event_context: Event context object
        """
        try:
            with self._lock:
                handlers = self._event_handlers.get(event_type, [])

                for coroutine_fn in handlers:
                    try:
                        # Create coroutine with event context
                        coroutine = coroutine_fn(event_context)

                        # Create async task for handler
                        self.create_task(
                            coroutine,
                            metadata={
                                "type": "event_handler",
                                "event_type": event_type
                            }
                        )

                    except Exception:
                        # Handler creation failed, skip
                        pass

        except Exception:
            # Never crash on event trigger
            pass

    def register_event_handler(self, event_type: str, coroutine_fn: Coroutine):
        """
        Register an async event handler.

        Args:
            event_type: Event type to listen for
            coroutine_fn: Async function that receives event_context
        """
        try:
            with self._lock:
                if event_type not in self._event_handlers:
                    self._event_handlers[event_type] = []

                self._event_handlers[event_type].append(coroutine_fn)

        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get async task manager statistics.

        Returns:
            Stats dict
        """
        try:
            with self._lock:
                return {
                    "tick_count": self._tick_count,
                    "total_tasks": len(self._tasks_by_id),
                    "pending_tasks": len(self._pending_tasks),
                    "running_tasks": len(self._running_tasks),
                    "completed_tasks": sum(
                        1 for t in self._tasks_by_id.values()
                        if t.status == AsyncTaskStatus.COMPLETED
                    ),
                    "failed_tasks": sum(
                        1 for t in self._tasks_by_id.values()
                        if t.status == AsyncTaskStatus.FAILED
                    ),
                    "event_types": len(self._event_handlers)
                }
        except Exception:
            return {}

    def _cleanup_old_tasks(self):
        """
        Remove old completed tasks (keep last 100).

        Internal method, called from tick().
        """
        try:
            # Get all completed tasks
            completed = [
                t for t in self._tasks_by_id.values()
                if t.status in [
                    AsyncTaskStatus.COMPLETED,
                    AsyncTaskStatus.FAILED,
                    AsyncTaskStatus.CANCELLED
                ]
            ]

            # If more than 100, remove oldest
            if len(completed) > 100:
                # Sort by completion time
                completed.sort(key=lambda t: t.completed_at or 0)

                # Remove oldest
                to_remove = completed[:-100]
                for task in to_remove:
                    if task.id in self._tasks_by_id:
                        del self._tasks_by_id[task.id]

        except Exception:
            pass

    def _publish_task_event(self, task: AsyncTask):
        """
        Publish task completion event.

        Args:
            task: Completed task
        """
        try:
            if self.event_bus:
                from ..event_context import EventContext

                event_ctx = EventContext(
                    event_type="system.async.done",
                    source="async_manager",
                    payload={
                        "task_id": task.id,
                        "status": task.status.value,
                        "result": task.result if task.status == AsyncTaskStatus.COMPLETED else None,
                        "error": task.error,
                        "metadata": task.metadata
                    },
                    category="system"
                )

                self.event_bus.publish("system.async.done", event_ctx)

        except Exception:
            # Never crash on event publishing
            pass

    def _publish_tick_event(self, timestamp: float):
        """
        Publish tick event.

        Args:
            timestamp: Current timestamp
        """
        try:
            if self.event_bus:
                from ..event_context import EventContext

                event_ctx = EventContext(
                    event_type="system.async.tick",
                    source="async_manager",
                    payload={
                        "tick_count": self._tick_count,
                        "timestamp": timestamp,
                        "pending": len(self._pending_tasks),
                        "running": len(self._running_tasks)
                    },
                    category="system"
                )

                self.event_bus.publish("system.async.tick", event_ctx)

        except Exception:
            pass

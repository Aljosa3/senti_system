"""
FAZA 43 — Scheduler
-------------------
Cooperative task scheduler for Senti OS Runtime.

Features:
- Interval tasks (repeating)
- Oneshot tasks (single execution)
- Event-triggered tasks
- System tasks

Design Principles:
- Cooperative (no threading)
- tick() called explicitly
- Max 10 tasks per tick (safety limit)
- Auto-disable failed tasks
- EventBus integration
- Never crashes runtime

Safety:
- All exceptions caught
- Failures logged but don't propagate
- Tasks auto-disable after 3 failures
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from .task import Task, TaskType
from .task_registry import TaskRegistry

if TYPE_CHECKING:
    from ..event_bus import EventBus
    from ..event_context import EventContext


class Scheduler:
    """
    Cooperative task scheduler.

    Manages execution of interval, oneshot, event, and system tasks.
    """

    # Safety limits
    MAX_TASKS_PER_TICK = 10

    def __init__(self, event_bus: Optional['EventBus'] = None):
        """
        Initialize scheduler.

        Args:
            event_bus: Optional EventBus for publishing scheduler events
        """
        self.registry = TaskRegistry()
        self.event_bus = event_bus
        self._last_tick = time.time()
        self._tick_count = 0

    def schedule_interval(
        self,
        callable_fn: Callable,
        interval: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a repeating interval task.

        Args:
            callable_fn: Function to execute
            interval: Interval in seconds
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            task = Task(
                task_type=TaskType.INTERVAL,
                callable_fn=callable_fn,
                interval=interval,
                next_run=time.time() + interval,
                metadata=metadata
            )

            self.registry.register(task)
            return task.id

        except Exception:
            # Return empty ID on failure
            return ""

    def schedule_oneshot(
        self,
        callable_fn: Callable,
        delay: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a one-time task after delay.

        Args:
            callable_fn: Function to execute
            delay: Delay in seconds
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            task = Task(
                task_type=TaskType.ONESHOT,
                callable_fn=callable_fn,
                next_run=time.time() + delay,
                metadata=metadata
            )

            self.registry.register(task)
            return task.id

        except Exception:
            return ""

    def schedule_event(
        self,
        event_type: str,
        callable_fn: Callable,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule an event-triggered task.

        Args:
            event_type: Event type to listen for
            callable_fn: Function to execute (receives event_context)
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        try:
            task = Task(
                task_type=TaskType.EVENT,
                callable_fn=callable_fn,
                event_type=event_type,
                metadata=metadata
            )

            self.registry.register(task)
            return task.id

        except Exception:
            return ""

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled
        """
        try:
            return self.registry.unregister(task_id)
        except Exception:
            return False

    def tick(self, now_timestamp: Optional[float] = None):
        """
        Execute scheduler tick.

        Processes due tasks up to MAX_TASKS_PER_TICK limit.

        Args:
            now_timestamp: Current timestamp (defaults to time.time())
        """
        try:
            if now_timestamp is None:
                now_timestamp = time.time()

            self._tick_count += 1
            self._last_tick = now_timestamp

            # Publish tick event
            self._publish_event("system.scheduler.tick", {
                "tick_count": self._tick_count,
                "timestamp": now_timestamp
            })

            # Get due tasks
            due_tasks = self.registry.list_due_tasks(now_timestamp)

            # Safety limit: max 10 tasks per tick
            if len(due_tasks) > self.MAX_TASKS_PER_TICK:
                due_tasks = due_tasks[:self.MAX_TASKS_PER_TICK]

            # Execute tasks
            for task in due_tasks:
                self._execute_task(task, now_timestamp)

        except Exception:
            # Never crash on tick failure
            pass

    def trigger_event(self, event_type: str, event_context: 'EventContext'):
        """
        Trigger event handlers for an event.

        Args:
            event_type: Event type
            event_context: Event context object
        """
        try:
            handlers = self.registry.list_event_handlers(event_type)

            for task in handlers:
                try:
                    # Execute handler with event context
                    task.callable(event_context)
                    task.mark_success()

                    # Publish execution event
                    self._publish_event("system.scheduler.executed", {
                        "task_id": task.id,
                        "task_type": "event",
                        "event_type": event_type,
                        "success": True
                    })

                except Exception as e:
                    task.mark_failure(str(e))

                    # Publish failure event
                    self._publish_event("system.scheduler.executed", {
                        "task_id": task.id,
                        "task_type": "event",
                        "event_type": event_type,
                        "success": False,
                        "error": str(e)
                    })

        except Exception:
            # Never crash on event trigger
            pass

    def _execute_task(self, task: Task, now_timestamp: float):
        """
        Execute a single task.

        Args:
            task: Task to execute
            now_timestamp: Current timestamp
        """
        try:
            # Execute callable
            task.callable()
            task.mark_success()

            # Reschedule if needed
            task.reschedule(now_timestamp)

            # Publish execution event
            self._publish_event("system.scheduler.executed", {
                "task_id": task.id,
                "task_type": task.type.value,
                "success": True,
                "next_run": task.next_run if task.enabled else None
            })

        except Exception as e:
            task.mark_failure(str(e))

            # Publish failure event
            self._publish_event("system.scheduler.executed", {
                "task_id": task.id,
                "task_type": task.type.value,
                "success": False,
                "error": str(e),
                "failure_count": task.failure_count,
                "disabled": not task.enabled
            })

    def _publish_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Publish event to EventBus (if available).

        Args:
            event_type: Event type
            payload: Event payload
        """
        try:
            if self.event_bus:
                from ..event_context import EventContext

                event_ctx = EventContext(
                    event_type=event_type,
                    source="scheduler",
                    payload=payload,
                    category="system"
                )

                self.event_bus.publish(event_type, event_ctx)

        except Exception:
            # Never crash on event publishing
            pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.

        Returns:
            Stats dict
        """
        try:
            registry_stats = self.registry.get_stats()

            return {
                "tick_count": self._tick_count,
                "last_tick": self._last_tick,
                **registry_stats
            }

        except Exception:
            return {}

    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all tasks (serialized).

        Returns:
            List of task dicts
        """
        try:
            return [task.to_dict() for task in self.registry.list()]
        except Exception:
            return []

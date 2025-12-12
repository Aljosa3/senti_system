"""
FAZA 44 — Async Capabilities
-----------------------------
Capability proxies for asynchronous execution.

Capabilities:
- AsyncScheduleCapability: Schedule async coroutines
- AsyncAwaitCapability: Poll async task results

Design:
- Safe proxy pattern
- Never crashes runtime
- Integrates with AsyncTaskManager
"""

from __future__ import annotations
from typing import Any, Coroutine, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .async_task_manager import AsyncTaskManager


class AsyncScheduleCapability:
    """
    FAZA 44: Async scheduling capability.

    Allows modules to schedule async coroutines for execution.
    """

    def __init__(self, async_manager: 'AsyncTaskManager'):
        self.async_manager = async_manager

    def schedule(self, coroutine: Coroutine, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Schedule an async coroutine for execution.

        Args:
            coroutine: Async coroutine to execute
            metadata: Optional task metadata

        Returns:
            Task ID (empty string on failure)
        """
        try:
            return self.async_manager.create_task(coroutine, metadata)
        except Exception:
            return ""

    def __repr__(self):
        return "<Capability:async.schedule>"


class AsyncAwaitCapability:
    """
    FAZA 44: Async result polling capability.

    Allows modules to poll async task results.
    """

    def __init__(self, async_manager: 'AsyncTaskManager'):
        self.async_manager = async_manager

    def poll(self, task_id: str) -> Dict[str, Any]:
        """
        Poll async task status and result.

        Args:
            task_id: Task ID to poll

        Returns:
            Dict with task status, result, and error
        """
        try:
            task = self.async_manager.get(task_id)

            if not task:
                return {
                    "ok": False,
                    "error": "Task not found"
                }

            task_dict = task.to_dict()

            return {
                "ok": True,
                "task_id": task.id,
                "status": task.status.value,
                "is_done": task.is_done(),
                "result": task_dict.get("result"),
                "error": task_dict.get("error"),
                "metadata": task_dict.get("metadata")
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    def wait(self, task_id: str, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Wait for async task to complete (blocking).

        WARNING: This is a blocking operation and should be used sparingly.

        Args:
            task_id: Task ID to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Dict with task result
        """
        try:
            import time

            start_time = time.time()

            while time.time() - start_time < timeout:
                task = self.async_manager.get(task_id)

                if not task:
                    return {
                        "ok": False,
                        "error": "Task not found"
                    }

                if task.is_done():
                    return self.poll(task_id)

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.1)

            # Timeout reached
            return {
                "ok": False,
                "error": "Timeout waiting for task",
                "status": "timeout"
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    def cancel(self, task_id: str) -> bool:
        """
        Cancel an async task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled
        """
        try:
            return self.async_manager.cancel(task_id)
        except Exception:
            return False

    def __repr__(self):
        return "<Capability:async.await>"

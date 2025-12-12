"""
FAZA 44 — Event Bus System
---------------------------
This module implements the central Event Bus used for:
- Publishing events
- Subscribing module handlers
- Delivering full EventContext objects
- Managing event categories and namespaces
- Isolated per-module event routing
- FAZA 43: Integration with Scheduler for event-triggered tasks
- FAZA 44: Integration with AsyncTaskManager for async event handlers

This is the foundational component for FAZA 41, extended in FAZA 43 and 44.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Callable, Any, List, Optional, TYPE_CHECKING
import threading
import asyncio
import inspect

if TYPE_CHECKING:
    from .scheduler import Scheduler
    from .async_exec import AsyncTaskManager


class EventBus:
    """
    Central event dispatcher for Senti OS modules.

    Responsibilities:
    - Register handlers for event types
    - Dispatch events to subscribed handlers
    - Maintain event namespaces
    - Guarantee module isolation (no cross-module corruption)
    - FAZA 43: Trigger scheduler event handlers
    - FAZA 44: Support async event handlers
    """

    def __init__(self, scheduler: Optional['Scheduler'] = None, async_manager: Optional['AsyncTaskManager'] = None):
        # event_type → list of handler functions
        self._subscribers: Dict[str, List[Callable]] = {}

        # thread lock for safe registration and dispatching
        self._lock = threading.Lock()

        # FAZA 43: Scheduler integration
        self._scheduler = scheduler

        # FAZA 44: Async task manager integration
        self._async_manager = async_manager

    # ----------------------------------------------------------------------
    # FAZA 43: Scheduler Integration
    # ----------------------------------------------------------------------

    def set_scheduler(self, scheduler: 'Scheduler') -> None:
        """
        Set the scheduler instance for event-triggered tasks.

        Args:
            scheduler: Scheduler instance
        """
        self._scheduler = scheduler

    # ----------------------------------------------------------------------
    # FAZA 44: Async Task Manager Integration
    # ----------------------------------------------------------------------

    def set_async_manager(self, async_manager: 'AsyncTaskManager') -> None:
        """
        Set the async task manager instance for async event handlers.

        Args:
            async_manager: AsyncTaskManager instance
        """
        self._async_manager = async_manager

    # ----------------------------------------------------------------------
    # Subscription API
    # ----------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe a module handler to a specific event type.

        handler signature:
            def handler(event_context)

        Args:
            event_type: Name of the event, e.g. "system.lifecycle.change"
            handler: Callable that receives an EventContext instance
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Remove a handler from a given event subscription list.
        """
        with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)

    # ----------------------------------------------------------------------
    # Event Publishing
    # ----------------------------------------------------------------------

    def publish(self, event_type: str, event_context: Any) -> List[Any]:
        """
        Publish an event to all subscribed handlers.

        Args:
            event_type: Name of the event
            event_context: EventContext object containing metadata + payload

        Returns:
            List of handler return values
        """
        results = []

        with self._lock:
            handlers = list(self._subscribers.get(event_type, []))

        # Dispatch to regular subscribers
        for handler in handlers:
            try:
                # FAZA 44: Check if handler is async (coroutine function)
                if inspect.iscoroutinefunction(handler):
                    # Async handler: create async task
                    if self._async_manager:
                        try:
                            coroutine = handler(event_context)
                            task_id = self._async_manager.create_task(
                                coroutine,
                                metadata={
                                    "type": "event_handler",
                                    "event_type": event_type,
                                    "source": "event_bus"
                                }
                            )
                            results.append({
                                "async": True,
                                "task_id": task_id
                            })
                        except Exception as e:
                            results.append({"error": f"Async handler error: {e}"})
                    else:
                        # No async_manager, skip async handler
                        results.append({"error": "Async handler but no async_manager"})
                else:
                    # Regular synchronous handler
                    result = handler(event_context)
                    results.append(result)
            except Exception as e:
                # Event handlers must never crash the runtime
                results.append({"error": str(e)})

        # FAZA 43: Trigger scheduler event-triggered tasks
        if self._scheduler:
            try:
                self._scheduler.trigger_event(event_type, event_context)
            except Exception:
                # Scheduler errors must not crash event publishing
                pass

        return results

    # ----------------------------------------------------------------------
    # Introspection
    # ----------------------------------------------------------------------

    def list_event_types(self) -> List[str]:
        """
        Return all registered event types.
        """
        with self._lock:
            return sorted(list(self._subscribers.keys()))

    def list_handlers(self, event_type: str) -> List[str]:
        """
        Return a list of handler names for a given event.
        """
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
            return [h.__name__ for h in handlers]

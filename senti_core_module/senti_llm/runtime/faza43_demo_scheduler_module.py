"""
FAZA 43 Demo — Scheduler Module
--------------------------------
Demonstrates task scheduling capabilities:
- Interval tasks (repeating)
- Oneshot tasks (single execution)
- Event-triggered tasks
"""

# Shared state for demo
demo_state = {
    "interval_count": 0,
    "oneshot_executed": False,
    "event_count": 0,
    "task_ids": []
}


MODULE_MANIFEST = {
    "name": "faza43_demo_scheduler",
    "version": "1.0.0",
    "phase": 43,
    "description": "Demo module showcasing task scheduling capabilities",
    "entrypoint": "SchedulerDemoModule",

    "capabilities": {
        "requires": [
            "log.advanced",
            "task.schedule.interval",
            "task.schedule.oneshot",
            "task.schedule.event",
            "task.cancel",
            "event.publish"
        ]
    },

    "hooks": {
        "init": True,
        "pre_run": False,
        "post_run": False,
        "on_error": False
    }
}


class SchedulerDemoModule:
    """
    Demo module for FAZA 43 task scheduling.

    Demonstrates:
    - Interval tasks that repeat every N seconds
    - Oneshot tasks that execute once after delay
    - Event-triggered tasks that respond to events
    """

    def __init__(self, context, capabilities, state=None):
        self.context = context
        self.capabilities = capabilities
        self.state = state

        # Get capability references
        self.log = capabilities.get("log.advanced")
        self.schedule_interval = capabilities.get("task.schedule.interval")
        self.schedule_oneshot = capabilities.get("task.schedule.oneshot")
        self.schedule_event = capabilities.get("task.schedule.event")
        self.task_cancel = capabilities.get("task.cancel")
        self.event_publish = capabilities.get("event.publish")

    def init(self):
        """
        Initialize module and schedule demo tasks.
        """
        if self.log:
            self.log.info("Initializing FAZA 43 Scheduler Demo Module")

        # 1) Schedule interval task (repeats every 5 seconds)
        if self.schedule_interval:
            task_id = self.schedule_interval.schedule(
                callable_fn=self._interval_task,
                interval=5.0,
                metadata={"name": "demo_interval"}
            )
            demo_state["task_ids"].append(task_id)

            if self.log:
                self.log.info(f"Scheduled interval task: {task_id}")

        # 2) Schedule oneshot task (executes once after 3 seconds)
        if self.schedule_oneshot:
            task_id = self.schedule_oneshot.schedule(
                callable_fn=self._oneshot_task,
                delay=3.0,
                metadata={"name": "demo_oneshot"}
            )
            demo_state["task_ids"].append(task_id)

            if self.log:
                self.log.info(f"Scheduled oneshot task: {task_id}")

        # 3) Schedule event-triggered task
        if self.schedule_event:
            task_id = self.schedule_event.schedule(
                event_type="demo.trigger",
                callable_fn=self._event_task,
                metadata={"name": "demo_event"}
            )
            demo_state["task_ids"].append(task_id)

            if self.log:
                self.log.info(f"Scheduled event-triggered task: {task_id}")

    def _interval_task(self):
        """
        Interval task handler (repeats every 5 seconds).
        """
        demo_state["interval_count"] += 1

        if self.log:
            self.log.info(f"Interval task executed (count: {demo_state['interval_count']})")

    def _oneshot_task(self):
        """
        Oneshot task handler (executes once).
        """
        demo_state["oneshot_executed"] = True

        if self.log:
            self.log.info("Oneshot task executed")

    def _event_task(self, event_context):
        """
        Event-triggered task handler.

        Args:
            event_context: EventContext object
        """
        demo_state["event_count"] += 1

        if self.log:
            self.log.info(
                f"Event-triggered task executed (event: {event_context.event_type}, count: {demo_state['event_count']})",
                event_type=event_context.event_type,
                source=event_context.source
            )

    def run(self, payload: dict):
        """
        Run method to demonstrate module execution.

        Payload options:
        - action: "trigger_event" - publishes demo.trigger event
        - action: "cancel_task" - cancels first scheduled task
        - action: "status" - returns current demo state
        """
        action = payload.get("action", "status")

        if self.log:
            self.log.info(f"Demo module run with action: {action}")

        if action == "trigger_event":
            # Publish demo.trigger event to test event-triggered tasks
            if self.event_publish:
                results = self.event_publish.publish(
                    event_type="demo.trigger",
                    payload={"message": "Demo event triggered"},
                    category="demo",
                    priority=5
                )

                if self.log:
                    self.log.info(f"Published demo.trigger event, {len(results)} handlers executed")

                return {
                    "ok": True,
                    "message": "Event published",
                    "handler_results": results
                }

        elif action == "cancel_task":
            # Cancel first scheduled task
            if demo_state["task_ids"] and self.task_cancel:
                task_id = demo_state["task_ids"][0]
                success = self.task_cancel.cancel(task_id)

                if self.log:
                    self.log.info(f"Cancelled task {task_id}: {success}")

                return {
                    "ok": True,
                    "message": f"Cancelled task: {task_id}",
                    "success": success
                }

        elif action == "status":
            # Return current demo state
            return {
                "ok": True,
                "demo_state": {
                    "interval_count": demo_state["interval_count"],
                    "oneshot_executed": demo_state["oneshot_executed"],
                    "event_count": demo_state["event_count"],
                    "scheduled_tasks": len(demo_state["task_ids"])
                }
            }

        return {
            "ok": False,
            "error": f"Unknown action: {action}"
        }

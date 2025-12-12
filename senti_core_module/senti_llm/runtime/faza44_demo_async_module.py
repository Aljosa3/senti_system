"""
FAZA 44 Demo — Async Module
----------------------------
Demonstrates async execution capabilities:
- Async run method
- Async event handlers (reactive)
- Async task scheduling
- Async task polling (await)
"""

import asyncio

# Shared state for demo
demo_state = {
    "async_run_count": 0,
    "async_event_count": 0,
    "task_ids": [],
    "results": []
}


MODULE_MANIFEST = {
    "name": "faza44_demo_async",
    "version": "1.0.0",
    "phase": 44,
    "description": "Demo module showcasing async execution capabilities",
    "entrypoint": "AsyncDemoModule",

    "capabilities": {
        "requires": [
            "log.advanced",
            "async.schedule",
            "async.await",
            "event.publish",
            "event.subscribe"
        ]
    },

    "hooks": {
        "init": True,
        "pre_run": False,
        "post_run": False,
        "on_error": False
    },

    # FAZA 42: Reactive handlers (async event handlers)
    "reactive": {
        "demo.async.trigger": "handle_async_event"
    }
}


class AsyncDemoModule:
    """
    Demo module for FAZA 44 async execution.

    Demonstrates:
    - Async run method
    - Async event handlers
    - Async task scheduling
    - Task result polling
    """

    def __init__(self, context, capabilities, state=None):
        self.context = context
        self.capabilities = capabilities
        self.state = state

        # Get capability references
        self.log = capabilities.get("log.advanced")
        self.async_schedule = capabilities.get("async.schedule")
        self.async_await = capabilities.get("async.await")
        self.event_publish = capabilities.get("event.publish")
        self.event_subscribe = capabilities.get("event.subscribe")

    def init(self):
        """
        Initialize module.
        """
        if self.log:
            self.log.info("Initializing FAZA 44 Async Demo Module")

    async def run(self, payload: dict):
        """
        Async run method.

        Payload options:
        - action: "async_work" - performs async work
        - action: "schedule_async" - schedules async task
        - action: "poll_task" - polls async task result
        - action: "trigger_event" - publishes async trigger event
        - action: "chain_async" - creates async event chain
        - action: "status" - returns current demo state
        """
        action = payload.get("action", "async_work")

        if self.log:
            self.log.info(f"Async demo module run with action: {action}")

        if action == "async_work":
            # Perform async work
            await asyncio.sleep(0.1)  # Simulate async work
            demo_state["async_run_count"] += 1

            if self.log:
                self.log.info(f"Async work completed (count: {demo_state['async_run_count']})")

            return {
                "ok": True,
                "message": "Async work completed",
                "count": demo_state["async_run_count"]
            }

        elif action == "schedule_async":
            # Schedule async task
            if self.async_schedule:
                task_id = self.async_schedule.schedule(
                    coroutine=self._async_task_worker(payload.get("delay", 1.0)),
                    metadata={"name": "demo_async_task"}
                )

                demo_state["task_ids"].append(task_id)

                if self.log:
                    self.log.info(f"Scheduled async task: {task_id}")

                return {
                    "ok": True,
                    "message": "Async task scheduled",
                    "task_id": task_id
                }

        elif action == "poll_task":
            # Poll async task result
            task_id = payload.get("task_id")

            if not task_id:
                return {
                    "ok": False,
                    "error": "Missing task_id"
                }

            if self.async_await:
                result = self.async_await.poll(task_id)

                if self.log:
                    self.log.info(f"Polled task {task_id}: {result.get('status')}")

                return result

        elif action == "trigger_event":
            # Publish async trigger event
            if self.event_publish:
                results = self.event_publish.publish(
                    event_type="demo.async.trigger",
                    payload={"message": "Async event triggered"},
                    category="demo",
                    priority=5
                )

                if self.log:
                    self.log.info(f"Published demo.async.trigger event")

                return {
                    "ok": True,
                    "message": "Event published",
                    "handler_results": results
                }

        elif action == "chain_async":
            # Create async event chain
            if self.log:
                self.log.info("Creating async event chain")

            # Step 1: Schedule async task
            if self.async_schedule:
                task_id_1 = self.async_schedule.schedule(
                    coroutine=self._async_chain_step_1(),
                    metadata={"step": 1}
                )

                # Step 2: Another async task
                task_id_2 = self.async_schedule.schedule(
                    coroutine=self._async_chain_step_2(),
                    metadata={"step": 2}
                )

                demo_state["task_ids"].extend([task_id_1, task_id_2])

                return {
                    "ok": True,
                    "message": "Async chain created",
                    "task_ids": [task_id_1, task_id_2]
                }

        elif action == "status":
            # Return current demo state
            return {
                "ok": True,
                "demo_state": {
                    "async_run_count": demo_state["async_run_count"],
                    "async_event_count": demo_state["async_event_count"],
                    "task_ids": demo_state["task_ids"],
                    "results": demo_state["results"]
                }
            }

        return {
            "ok": False,
            "error": f"Unknown action: {action}"
        }

    async def handle_async_event(self, event_context):
        """
        Async event handler (reactive).

        This is an async function that will be executed as an async task
        when demo.async.trigger event is published.
        """
        demo_state["async_event_count"] += 1

        if self.log:
            self.log.info(
                f"Async event handler executed (event: {event_context.event_type}, count: {demo_state['async_event_count']})",
                event_type=event_context.event_type,
                source=event_context.source
            )

        # Simulate async work
        await asyncio.sleep(0.1)

        # Store result
        demo_state["results"].append({
            "type": "async_event",
            "event_type": event_context.event_type,
            "count": demo_state["async_event_count"]
        })

    async def _async_task_worker(self, delay: float):
        """
        Async task worker coroutine.

        Args:
            delay: Delay in seconds
        """
        if self.log:
            self.log.info(f"Async task worker starting (delay: {delay}s)")

        await asyncio.sleep(delay)

        if self.log:
            self.log.info("Async task worker completed")

        return {
            "ok": True,
            "message": "Async task completed",
            "delay": delay
        }

    async def _async_chain_step_1(self):
        """Async chain step 1."""
        if self.log:
            self.log.info("Async chain step 1 starting")

        await asyncio.sleep(0.5)

        if self.log:
            self.log.info("Async chain step 1 completed")

        return {"step": 1, "completed": True}

    async def _async_chain_step_2(self):
        """Async chain step 2."""
        if self.log:
            self.log.info("Async chain step 2 starting")

        await asyncio.sleep(0.5)

        # Publish event after completion
        if self.event_publish:
            self.event_publish.publish(
                event_type="demo.async.chain.complete",
                payload={"step": 2},
                category="demo"
            )

        if self.log:
            self.log.info("Async chain step 2 completed")

        return {"step": 2, "completed": True}

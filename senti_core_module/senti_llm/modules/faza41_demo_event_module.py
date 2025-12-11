"""
FAZA 41 — Event Bus Demo Module
--------------------------------
Demonstrates EventBus publish/subscribe functionality:
- Publishes custom events
- Subscribes to system events
- Shows inter-module communication patterns
- Tracks received events

MODULE_MANIFEST includes event capabilities.
"""

from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
import time

MODULE_MANIFEST = {
    "name": "event_demo",
    "version": "1.0.0",
    "phase": 41,
    "entrypoint": "EventDemoModule",
    "description": "FAZA 41 demo module for Event Bus pub/sub",
    "capabilities": {
        "requires": ["event.publish", "event.subscribe", "log.basic", "module.run"],
        "optional": ["storage.write"]
    },
    "hooks": {
        "init": True,
        "pre_run": False,
        "post_run": False,
        "on_error": False
    },
    "default_state": {
        "published_count": 0,
        "received_events": []
    }
}


class EventDemoModule:
    """
    Demo module showing EventBus publish/subscribe patterns.

    Capabilities used:
    - event.publish: Publish custom events
    - event.subscribe: Subscribe to system/custom events
    - log.basic: Logging
    - module.run: Execution permission
    """

    def __init__(self, context: RuntimeContext, capabilities: dict, state):
        self.context = context
        self.capabilities = capabilities
        self.state = state

        # Get capabilities
        self.event_publish = capabilities.get("event.publish")
        self.event_subscribe = capabilities.get("event.subscribe")
        self.log = capabilities.get("log.basic")

        # Track received events
        self.received_events = []

    # ================================================================
    # FAZA 39: LIFECYCLE HOOKS
    # ================================================================

    def init(self):
        """
        Hook called on module load.
        Subscribe to events we're interested in.
        """
        if self.log:
            self.log.log("[LIFECYCLE] init() - Setting up event subscriptions")

        # Subscribe to system lifecycle events
        if self.event_subscribe:
            self.event_subscribe.subscribe("module.loaded", self._on_module_loaded)
            self.event_subscribe.subscribe("custom.test", self._on_custom_test)

            if self.log:
                self.log.log("[EVENT] Subscribed to: module.loaded, custom.test")

        print("  → EventDemoModule: initialized with event subscriptions")

    # ================================================================
    # EVENT HANDLERS
    # ================================================================

    def _on_module_loaded(self, event_context):
        """
        Handler for module.loaded events.

        Called whenever any module is loaded in the system.
        """
        payload = event_context.payload
        module_name = payload.get("module_name", "unknown")

        if self.log:
            self.log.log(f"[EVENT RECEIVED] module.loaded: {module_name}")

        # Track in state
        received = self.state.get("received_events", [])
        received.append({
            "event_type": "module.loaded",
            "module": module_name,
            "timestamp": event_context.timestamp
        })
        self.state.set("received_events", received)

        self.received_events.append(event_context)

        return {"handled": True, "handler": "event_demo._on_module_loaded"}

    def _on_custom_test(self, event_context):
        """
        Handler for custom.test events.

        Demonstrates custom event handling.
        """
        if self.log:
            self.log.log(f"[EVENT RECEIVED] custom.test: {event_context.payload}")

        self.received_events.append(event_context)

        return {"handled": True, "handler": "event_demo._on_custom_test"}

    # ================================================================
    # MAIN MODULE LOGIC
    # ================================================================

    def run(self, payload: dict) -> dict:
        """
        Main module execution.

        Payload modes:
        - mode=publish: Publish a custom event
        - mode=status: Return event stats
        - mode=list_subscriptions: List active subscriptions
        """
        mode = payload.get("mode", "status")

        if mode == "publish":
            # Publish a custom event
            if not self.event_publish:
                return {"ok": False, "error": "event.publish capability not available"}

            event_data = payload.get("event_data", {"message": "test event"})
            event_type = payload.get("event_type", "custom.test")

            results = self.event_publish.publish(
                event_type=event_type,
                payload=event_data,
                category="demo",
                priority=5
            )

            # Update state
            count = self.state.get("published_count", 0)
            self.state.set("published_count", count + 1)

            return {
                "ok": True,
                "action": "published",
                "event_type": event_type,
                "handlers_called": len(results),
                "results": results,
                "total_published": count + 1
            }

        elif mode == "status":
            # Return event statistics
            return {
                "ok": True,
                "stats": {
                    "published_count": self.state.get("published_count", 0),
                    "received_count": len(self.received_events),
                    "received_events": [
                        {
                            "type": evt.event_type,
                            "source": evt.source,
                            "timestamp": evt.timestamp
                        }
                        for evt in self.received_events[-5:]  # Last 5 events
                    ]
                }
            }

        elif mode == "list_subscriptions":
            # List active subscriptions
            if not self.event_subscribe:
                return {"ok": False, "error": "event.subscribe capability not available"}

            subs = self.event_subscribe.list_subscriptions()

            return {
                "ok": True,
                "subscriptions": subs,
                "count": len(subs)
            }

        else:
            return {
                "ok": False,
                "error": f"Unknown mode: {mode}",
                "valid_modes": ["publish", "status", "list_subscriptions"]
            }

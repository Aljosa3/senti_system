"""
FAZA 42 — Reactive Module Demo
-------------------------------
Demonstrates reactive module patterns:
- Declarative handler registration via manifest
- Automatic EventBus subscription on load
- Multiple reactive handlers
- State updates in reactive handlers
- Event chaining (handlers publishing new events)
- Handler introspection

REACTIVE vs MANUAL SUBSCRIPTION:
- FAZA 41: Manual subscription in init() hook using event.subscribe capability
- FAZA 42: Declarative subscription in manifest.reactive.handlers (automatic registration)
"""

from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
import time

MODULE_MANIFEST = {
    "name": "reactive_demo",
    "version": "1.0.0",
    "phase": 42,
    "entrypoint": "ReactiveDemoModule",
    "description": "FAZA 42 demo module for reactive handlers",
    "capabilities": {
        "requires": ["event.publish", "log.basic", "module.run"],
        "optional": ["storage.write"]
    },
    "hooks": {
        "init": True,
        "pre_run": False,
        "post_run": False,
        "on_error": False
    },
    "default_state": {
        "events_handled": 0,
        "custom_event_count": 0,
        "module_loaded_count": 0,
        "reactive_handler_calls": []
    },
    "reactive": {
        "enabled": True,
        "handlers": {
            "module.loaded": "on_module_loaded_reactive",
            "custom.test": "on_custom_test_reactive",
            "reactive.ping": "on_ping",
            "reactive.chain": "on_chain_start"
        }
    }
}


class ReactiveDemoModule:
    """
    Demo module showing FAZA 42 reactive handler patterns.

    Reactive handlers are declared in manifest.reactive.handlers
    and automatically registered to EventBus on module load.

    Capabilities used:
    - event.publish: Publish events from reactive handlers
    - log.basic: Logging
    - module.run: Execution permission
    """

    def __init__(self, context: RuntimeContext, capabilities: dict, state):
        self.context = context
        self.capabilities = capabilities
        self.state = state

        # Get capabilities
        self.event_publish = capabilities.get("event.publish")
        self.log = capabilities.get("log.basic")

        # Track handler calls in memory (for introspection)
        self.handler_calls = []

    # ================================================================
    # FAZA 39: LIFECYCLE HOOKS
    # ================================================================

    def init(self):
        """
        Hook called on module load.

        NOTE: In FAZA 42, reactive handlers are auto-registered
        BEFORE init() is called. We don't need to manually subscribe.
        """
        if self.log:
            self.log.log("[LIFECYCLE] init() - Reactive handlers already registered")

        print("  → ReactiveDemoModule: initialized with FAZA 42 reactive handlers")

    # ================================================================
    # FAZA 42: REACTIVE EVENT HANDLERS
    # ================================================================

    def on_module_loaded_reactive(self, event_context):
        """
        REACTIVE handler for module.loaded events.

        Declared in manifest.reactive.handlers.
        Auto-registered to EventBus on module load.
        """
        payload = event_context.payload
        module_name = payload.get("module_name", "unknown")

        if self.log:
            self.log.log(f"[REACTIVE] module.loaded: {module_name}")

        # Update state
        count = self.state.get("module_loaded_count", 0)
        self.state.set("module_loaded_count", count + 1)

        total = self.state.get("events_handled", 0)
        self.state.set("events_handled", total + 1)

        # Save state (reactive handlers must manually save)
        self.state.save()

        # Track call
        self.handler_calls.append({
            "handler": "on_module_loaded_reactive",
            "event_type": "module.loaded",
            "timestamp": event_context.timestamp
        })

        return {"handled": True, "handler": "reactive_demo.on_module_loaded_reactive"}

    def on_custom_test_reactive(self, event_context):
        """
        REACTIVE handler for custom.test events.

        Demonstrates state updates and event chaining.
        """
        if self.log:
            self.log.log(f"[REACTIVE] custom.test: {event_context.payload}")

        # Update state
        count = self.state.get("custom_event_count", 0)
        self.state.set("custom_event_count", count + 1)

        total = self.state.get("events_handled", 0)
        self.state.set("events_handled", total + 1)

        # Save state (reactive handlers must manually save)
        self.state.save()

        # Track call
        self.handler_calls.append({
            "handler": "on_custom_test_reactive",
            "event_type": "custom.test",
            "timestamp": event_context.timestamp
        })

        return {"handled": True, "handler": "reactive_demo.on_custom_test_reactive"}

    def on_ping(self, event_context):
        """
        REACTIVE handler for reactive.ping events.

        Demonstrates simple event acknowledgment pattern.
        """
        if self.log:
            self.log.log("[REACTIVE] reactive.ping received")

        # Respond with pong event
        if self.event_publish:
            self.event_publish.publish(
                event_type="reactive.pong",
                payload={"reply_to": event_context.source},
                category="demo"
            )

        total = self.state.get("events_handled", 0)
        self.state.set("events_handled", total + 1)

        # Save state (reactive handlers must manually save)
        self.state.save()

        self.handler_calls.append({
            "handler": "on_ping",
            "event_type": "reactive.ping",
            "timestamp": event_context.timestamp
        })

        return {"handled": True, "handler": "reactive_demo.on_ping", "action": "sent_pong"}

    def on_chain_start(self, event_context):
        """
        REACTIVE handler for reactive.chain events.

        Demonstrates event chaining - handler publishes new events.
        """
        if self.log:
            self.log.log("[REACTIVE] reactive.chain - starting chain reaction")

        # Publish chain continuation event
        if self.event_publish:
            chain_level = event_context.payload.get("level", 0)

            # Only chain if level < 3 (prevent infinite loops)
            if chain_level < 3:
                self.event_publish.publish(
                    event_type="reactive.chain",
                    payload={"level": chain_level + 1},
                    category="demo"
                )

        total = self.state.get("events_handled", 0)
        self.state.set("events_handled", total + 1)

        # Save state (reactive handlers must manually save)
        self.state.save()

        self.handler_calls.append({
            "handler": "on_chain_start",
            "event_type": "reactive.chain",
            "timestamp": event_context.timestamp,
            "chain_level": event_context.payload.get("level", 0)
        })

        return {"handled": True, "handler": "reactive_demo.on_chain_start"}

    # ================================================================
    # MAIN MODULE LOGIC
    # ================================================================

    def run(self, payload: dict) -> dict:
        """
        Main module execution.

        Payload modes:
        - mode=publish: Publish an event (manual trigger)
        - mode=status: Return reactive handler stats
        - mode=list_handlers: List registered reactive handlers
        - mode=trigger_ping: Trigger ping/pong pattern
        - mode=trigger_chain: Trigger event chain
        """
        mode = payload.get("mode", "status")

        if mode == "publish":
            # Manually publish an event
            if not self.event_publish:
                return {"ok": False, "error": "event.publish capability not available"}

            event_data = payload.get("event_data", {})
            event_type = payload.get("event_type", "custom.test")

            results = self.event_publish.publish(
                event_type=event_type,
                payload=event_data,
                category="demo",
                priority=5
            )

            return {
                "ok": True,
                "action": "published",
                "event_type": event_type,
                "handlers_called": len(results)
            }

        elif mode == "status":
            # Return reactive handler statistics
            return {
                "ok": True,
                "stats": {
                    "total_events_handled": self.state.get("events_handled", 0),
                    "module_loaded_count": self.state.get("module_loaded_count", 0),
                    "custom_event_count": self.state.get("custom_event_count", 0),
                    "handler_calls": len(self.handler_calls),
                    "recent_calls": self.handler_calls[-5:]  # Last 5 calls
                }
            }

        elif mode == "list_handlers":
            # List reactive handlers from manifest
            manifest_handlers = MODULE_MANIFEST["reactive"]["handlers"]

            return {
                "ok": True,
                "reactive_handlers": manifest_handlers,
                "handler_count": len(manifest_handlers),
                "enabled": MODULE_MANIFEST["reactive"]["enabled"]
            }

        elif mode == "trigger_ping":
            # Trigger ping/pong pattern
            if not self.event_publish:
                return {"ok": False, "error": "event.publish capability not available"}

            results = self.event_publish.publish(
                event_type="reactive.ping",
                payload={"from": "reactive_demo"},
                category="demo"
            )

            return {
                "ok": True,
                "action": "triggered_ping",
                "handlers_called": len(results)
            }

        elif mode == "trigger_chain":
            # Trigger event chain
            if not self.event_publish:
                return {"ok": False, "error": "event.publish capability not available"}

            # Convert level to int (may come as string from command parsing)
            initial_level = payload.get("level", 0)
            if isinstance(initial_level, str):
                initial_level = int(initial_level)

            results = self.event_publish.publish(
                event_type="reactive.chain",
                payload={"level": initial_level},
                category="demo"
            )

            # Wait a bit for chain to complete
            time.sleep(0.1)

            return {
                "ok": True,
                "action": "triggered_chain",
                "initial_level": initial_level,
                "handlers_called": len(results),
                "total_chain_calls": sum(
                    1 for call in self.handler_calls
                    if call["handler"] == "on_chain_start"
                )
            }

        else:
            return {
                "ok": False,
                "error": f"Unknown mode: {mode}",
                "valid_modes": [
                    "publish", "status", "list_handlers",
                    "trigger_ping", "trigger_chain"
                ]
            }

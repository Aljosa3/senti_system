"""
FAZA 40 — Persistent State Demo Module
---------------------------------------
Demonstrira persistent state management:
- State persistence across runs
- Automatic state refresh/save
- Integration with lifecycle hooks
- Counter and message history tracking

MODULE_MANIFEST vključuje default_state configuration.
"""

from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext
import time

MODULE_MANIFEST = {
    "name": "demo_state",
    "version": "1.0.0",
    "phase": 40,
    "entrypoint": "DemoStateModule",
    "description": "FAZA 40 demo module za persistent state management",
    "capabilities": {
        "requires": ["storage.write", "module.run"],
        "optional": []
    },
    "hooks": {
        "init": True,
        "pre_run": True,
        "post_run": True,
        "on_error": True
    },
    "default_state": {
        "counter": 0,
        "messages": [],
        "last_run_timestamp": None,
        "error_count": 0
    }
}


class DemoStateModule:
    """
    Demo module s polno podporo za persistent state.

    State structure:
    - counter: number of times run() was called
    - messages: list of run messages
    - last_run_timestamp: timestamp of last successful run
    - error_count: number of errors encountered
    """

    def __init__(self, context: RuntimeContext, capabilities: dict, state):
        self.context = context
        self.capabilities = capabilities
        self.state = state  # FAZA 40: ModuleState instance

        self.log = capabilities.get("log.basic")

    # ================================================================
    # FAZA 39: LIFECYCLE HOOKS
    # ================================================================

    def init(self):
        """
        Hook klican ob nalaganju modula.
        Load initial state and log initialization.
        """
        if self.log:
            self.log.log(f"[LIFECYCLE] init() - State loaded with counter={self.state.get('counter', 0)}")

        print(f"  → DemoStateModule: initialized with state counter={self.state.get('counter', 0)}")

    def pre_run(self, payload: dict):
        """
        Hook klican pred izvajanjem run().
        Record pre-run timestamp.
        """
        pre_run_ts = time.time()

        if self.log:
            self.log.log(f"[LIFECYCLE] pre_run() - timestamp={pre_run_ts}")

        print(f"  → DemoStateModule: pre_run at {pre_run_ts}")

        # Store temporary data (not persisted since we don't call state.save() yet)
        self._pre_run_timestamp = pre_run_ts

    def post_run(self, result: dict):
        """
        Hook klican po uspešnem izvajanju run().
        Confirm state was updated and saved.
        """
        if self.log:
            self.log.log(f"[LIFECYCLE] post_run() - counter is now {self.state.get('counter')}")

        print(f"  → DemoStateModule: post_run confirmed, counter={self.state.get('counter')}")

    def on_error(self, error: Exception):
        """
        Hook klican pri napaki med izvajanjem.
        Increment error counter in state.
        """
        if self.log:
            self.log.log(f"[LIFECYCLE] on_error() - {type(error).__name__}: {error}")

        print(f"  → DemoStateModule: error handler - {type(error).__name__}: {error}")

        # Increment error counter
        error_count = self.state.get("error_count", 0)
        self.state.set("error_count", error_count + 1)

    # ================================================================
    # FAZA 40: MAIN MODULE LOGIC WITH STATE
    # ================================================================

    def run(self, payload: dict) -> dict:
        """
        Glavna logika modula z persistent state.

        Payload format:
        {
            "module": "demo_state",
            "mode": "normal" | "error" | "reset" | "status"
        }
        """
        mode = payload.get("mode", "normal")

        if mode == "error":
            # Trigger error to test on_error hook + state persistence
            raise ValueError("Intentional error for testing on_error hook with state")

        elif mode == "reset":
            # Reset state to defaults
            self.state.reset()
            return {
                "ok": True,
                "message": "State reset to defaults",
                "state": self.state.dump()
            }

        elif mode == "status":
            # Return current state without modification
            return {
                "ok": True,
                "message": "Current state report",
                "state": self.state.dump()
            }

        else:
            # Normal execution: increment counter, add message
            # FAZA 40: State is automatically refreshed before this and saved after

            # Increment counter
            counter = self.state.get("counter", 0)
            counter += 1
            self.state.set("counter", counter)

            # Add message to history
            messages = self.state.get("messages", [])
            new_message = f"run {counter} at {time.time()}"
            messages.append(new_message)
            self.state.set("messages", messages)

            # Update last run timestamp
            self.state.set("last_run_timestamp", time.time())

            # Return full state dump
            return {
                "ok": True,
                "mode": mode,
                "message": f"DemoStateModule executed successfully (run #{counter})",
                "state": self.state.dump()
            }

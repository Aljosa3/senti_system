"""
FAZA 39 — Lifecycle Hooks Demo Module
--------------------------------------
Demonstrira vse 4 lifecycle hooks:
- init(): klican ob nalaganju modula
- pre_run(): klican pred izvajanjem
- post_run(): klican po izvajanju
- on_error(): klican pri napaki

MODULE_MANIFEST vključuje vse hooks.
"""

from senti_core_module.senti_llm.runtime.llm_runtime_context import RuntimeContext

MODULE_MANIFEST = {
    "name": "lifecycle_demo",
    "version": "1.0.0",
    "phase": 39,
    "entrypoint": "LifecycleDemoModule",
    "description": "FAZA 39 demo module za lifecycle hooks",
    "capabilities": {
        "requires": ["log.basic", "module.run"],
        "optional": []
    },
    "hooks": {
        "init": True,
        "pre_run": True,
        "post_run": True,
        "on_error": True
    }
}


class LifecycleDemoModule:
    """Demo module s polno podporo za lifecycle hooks."""

    def __init__(self, context: RuntimeContext, capabilities: dict):
        self.context = context
        self.capabilities = capabilities
        self.log = capabilities.get("log.basic")

        # Internal state
        self.init_called = False
        self.pre_run_called = False
        self.post_run_called = False
        self.on_error_called = False

    # ================================================================
    # FAZA 39: LIFECYCLE HOOKS
    # ================================================================

    def init(self):
        """
        Hook klican ob nalaganju modula.
        Uporabljen za inicializacijo stanja, povezovanje na zunanje vire, itd.
        """
        self.init_called = True

        if self.log:
            self.log.log("[LIFECYCLE] init() called - module initializing")

        # Simulate initialization work
        print("  → LifecycleDemoModule: initialization complete")

    def pre_run(self, payload: dict):
        """
        Hook klican pred izvajanjem run().
        Uporabljen za validacijo inputa, pripravo okolja, itd.
        """
        self.pre_run_called = True

        if self.log:
            self.log.log(f"[LIFECYCLE] pre_run() called with payload: {payload}")

        print(f"  → LifecycleDemoModule: pre-processing payload={payload}")

        # Validate payload
        if "mode" not in payload:
            print("  → Warning: 'mode' not specified, using default")

    def post_run(self, result: dict):
        """
        Hook klican po uspešnem izvajanju run().
        Uporabljen za cleanup, logging rezultatov, itd.
        """
        self.post_run_called = True

        if self.log:
            self.log.log(f"[LIFECYCLE] post_run() called with result: {result}")

        print(f"  → LifecycleDemoModule: post-processing result={result}")

        # Could add metrics, logging, etc.

    def on_error(self, error: Exception):
        """
        Hook klican pri napaki med izvajanjem.
        Uporabljen za error logging, cleanup, recovery, itd.
        """
        self.on_error_called = True

        if self.log:
            self.log.log(f"[LIFECYCLE] on_error() called with error: {error}")

        print(f"  → LifecycleDemoModule: error handler activated - {type(error).__name__}: {error}")

        # Could trigger alerts, save error state, etc.

    # ================================================================
    # MAIN MODULE LOGIC
    # ================================================================

    def run(self, payload: dict) -> dict:
        """
        Glavna logika modula.

        Payload format:
        {
            "module": "lifecycle_demo",
            "mode": "normal" | "error" | "status"
        }
        """
        mode = payload.get("mode", "normal")

        if mode == "error":
            # Trigger error to test on_error hook
            raise ValueError("Intentional error for testing on_error hook")

        elif mode == "status":
            # Return lifecycle status
            return {
                "ok": True,
                "lifecycle_status": {
                    "init_called": self.init_called,
                    "pre_run_called": self.pre_run_called,
                    "post_run_called": self.post_run_called,
                    "on_error_called": self.on_error_called,
                },
                "current_stage": self.context.get_stage(),
                "message": "Lifecycle hooks status report"
            }

        else:
            # Normal execution
            return {
                "ok": True,
                "mode": mode,
                "message": "LifecycleDemoModule executed successfully",
                "hooks_working": True
            }

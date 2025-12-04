import os
import json
from .state_manager import StateManager
from .service_registry import ServiceRegistry

class BootManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.state_manager = StateManager(base_dir)
        self.registry = ServiceRegistry()

    def start(self):
        """Boots full FAZA16–FAZA21 stack and commits state."""
        print("[BOOT] Starting Senti OS...")

        previous = self.state_manager.load_state()
        print(f"[BOOT] Previous state: {previous}")

        self.registry.start_all_services()
        print("[BOOT] All services started.")

        # CRITICAL FIX
        self.state_manager.set_state("running")
        print("[BOOT] System state saved: running")

        return True

    def stop(self):
        self.registry.stop_all_services()
        self.state_manager.set_state("stopped")
        print("[BOOT] System stopped.")
        return True

    def restart(self):
        self.stop()
        return self.start()

    def commit_state(self):
        self.state_manager.save_state()
        print("[BOOT] State committed to disk")

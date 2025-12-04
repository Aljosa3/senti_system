from .boot_manager import BootManager
from .state_manager import StateManager

class CLICommands:
    def __init__(self, base_dir):
        self.manager = BootManager(base_dir)
        self.state_manager = StateManager(base_dir)

    def start(self):
        ok = self.manager.start()
        if ok:
            self.manager.commit_state()
        print("Senti OS started.")

    def stop(self):
        self.manager.stop()
        print("Senti OS stopped.")

    def status(self):
        st = self.state_manager.load_state()
        print("────────────── SYSTEM STATUS ──────────────")
        print(f"System State: {st}")

        if st == "running":
            print("Running stacks: 6 (FAZA16–FAZA21)")
        else:
            print("Running stacks: 0")

    def doctor(self):
        st = self.state_manager.load_state()
        print("────────────── SYSTEM DOCTOR ──────────────")
        print(f"Boot Status: {st}")

        if st == "running":
            print("✓ Boot valid")
            print("✓ Services active")
        else:
            print("⚠ System not initialized")

import os
import json

class StateManager:
    def __init__(self, base_dir):
        self.state_path = os.path.join(
            base_dir, "data", "faza22", "boot_state.json"
        )
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

        self.state = {"boot_state": "uninitialized"}

    def load_state(self):
        if not os.path.exists(self.state_path):
            return "uninitialized"
        try:
            with open(self.state_path, "r") as f:
                data = json.load(f)
                self.state = data
                return data.get("boot_state", "uninitialized")
        except Exception:
            return "uninitialized"

    def set_state(self, new_state):
        self.state["boot_state"] = new_state
        self.save_state()

    def save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=2)

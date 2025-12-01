"""
FAZA 11 — Refactor Rules
Security and integrity validation for refactor patches.
"""

class RefactorRules:
    VALID_ACTIONS = ["rename_function"]

    def __init__(self, project_root):
        self.project_root = project_root

    def validate_patch(self, patch: dict):
        if "action" not in patch:
            raise ValueError("Patch missing 'action'")

        if patch["action"] not in self.VALID_ACTIONS:
            raise ValueError(f"Invalid patch action: {patch['action']}")

        if patch["action"] == "rename_function":
            if "old" not in patch or "new" not in patch:
                raise ValueError("rename_function requires 'old' and 'new'")

"""
FAZA 10 — Expansion Rules
Security and integrity rules for dynamic system expansion.
"""

import re
from pathlib import Path


class ExpansionRules:
    """
    Enforces safe and controlled expansion.
    """

    VALID_NAME_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    def __init__(self, project_root: Path):
        self.project_root = project_root

    # -------------------------
    # VALIDATION RULES
    # -------------------------

    def validate_module_name(self, name: str):
        if not re.match(self.VALID_NAME_PATTERN, name):
            raise ValueError(f"Invalid module name: {name}")

    def validate_target_directory(self, target_dir: str):
        forbidden = ["senti_core", "senti_os", "senti_core_module"]
        if target_dir in forbidden:
            raise PermissionError(
                f"Target directory '{target_dir}' is protected and cannot be modified."
            )

"""
FAZA 10 — Expansion Engine
Main engine responsible for AI-driven system expansion.

This engine:
- generates new modules
- creates directories and files safely
- validates expansion rules
- registers modules into the OS

FAZA 59.5: Respects CORE lock state - disabled when CORE is locked.
"""

import os
import json
import sys
from pathlib import Path

from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_expansion.expansion_rules import ExpansionRules
from senti_core_module.senti_expansion.module_template import ModuleTemplate
from senti_core_module.senti_expansion.expansion_events import ExpansionEvent

# Add path for CORE lock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from senti_os.security.core_lock_state import get_core_lock_manager, CoreMutationError


class ExpansionEngine:
    """
    Core FAZA 10 engine that allows Senti OS to expand itself.
    """

    def __init__(self, project_root: Path, event_bus: EventBus):
        self.project_root = project_root
        self.event_bus = event_bus
        self.rules = ExpansionRules(project_root)
        self.template = ModuleTemplate()

    def expand(self, module_name: str, target_dir: str = "modules"):
        """
        Create a new module dynamically in the system.

        Raises:
            CoreMutationError: If CORE is locked (expansion disabled post-lock)
        """
        # FAZA 59.5: Check CORE lock state
        lock_manager = get_core_lock_manager(str(self.project_root))
        if lock_manager.is_locked():
            raise CoreMutationError(
                "CORE LOCK VIOLATION: Expansion Engine is disabled when CORE is locked.\n"
                "Module expansion is prohibited post-lock.\n"
                "CORE modifications require CORE UPGRADE procedure."
            )

        module_path = self.project_root / target_dir / module_name

        # Check safety rules
        self.rules.validate_module_name(module_name)
        self.rules.validate_target_directory(target_dir)

        # Create directory
        module_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_path = module_path / "__init__.py"
        init_path.write_text(f'"""Auto-generated module: {module_name}"""')

        # Generate module implementation file
        code_path = module_path / f"{module_name}.py"
        code_path.write_text(self.template.generate(module_name))

        # Publish event
        self.event_bus.publish(
            event_type="MODULE_CREATED",
            payload={"name": module_name, "path": str(module_path)}
        )

        return {
            "status": "success",
            "module": module_name,
            "directory": str(module_path),
        }

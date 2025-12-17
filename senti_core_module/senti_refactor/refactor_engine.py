"""
FAZA 11 — Refactor Engine
Core engine for AI-driven self-refactor operations using AST manipulation.

FAZA 59.5: DISABLED when CORE is locked.
Code modification of CORE requires CORE UPGRADE procedure.
"""

import ast
import sys
from pathlib import Path
from senti_core_module.senti_refactor.refactor_rules import RefactorRules
from senti_core_module.senti_refactor.refactor_events import RefactorEvent
from senti_core_module.senti_core.services.event_bus import EventBus

# Add path for CORE lock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from senti_os.security.core_lock_state import get_core_lock_manager, CoreMutationError

class RefactorEngine:
    """
    Executes controlled AST-level code transformations.
    """

    def __init__(self, project_root: Path, event_bus: EventBus):
        self.project_root = project_root
        self.rules = RefactorRules(project_root)
        self.event_bus = event_bus

    def apply_patch(self, file_path: Path, patch: dict):
        """
        Apply an AST transformation patch to a python source file.
        Patch example:
        {
            "action": "rename_function",
            "old": "foo",
            "new": "foo_new"
        }

        Raises:
            CoreMutationError: If CORE is locked (refactoring disabled post-lock)
        """
        # FAZA 59.5: Check CORE lock state FIRST
        lock_manager = get_core_lock_manager(str(self.project_root))
        if lock_manager.is_locked():
            raise CoreMutationError(
                "CORE LOCK VIOLATION: Refactor Engine is DISABLED when CORE is locked.\n"
                "Code refactoring is prohibited post-lock.\n"
                "CORE modifications require CORE UPGRADE procedure."
            )

        # Also check if target file is a CORE file
        if lock_manager.is_core_path(str(file_path)):
            # Even if CORE isn't locked, warn about CORE modification
            print(f"WARNING: Modifying CORE file: {file_path}", file=sys.stderr)

        self.rules.validate_patch(patch)

        if not file_path.exists():
            raise FileNotFoundError(str(file_path))

        tree = ast.parse(file_path.read_text())

        # apply transformation
        if patch["action"] == "rename_function":
            tree = self._rename_function(tree, patch["old"], patch["new"])

        # write result (using Python 3.9+ ast.unparse)
        new_source = ast.unparse(tree)
        file_path.write_text(new_source)

        # publish event
        self.event_bus.publish(
            "REFACTOR_APPLIED",
            {"file": str(file_path), "patch": patch}
        )

        return {
            "status": "ok",
            "file": str(file_path),
            "patch": patch
        }

    # -------------------------------
    # AST TRANSFORMERS
    # -------------------------------
    def _rename_function(self, tree, old, new):
        class Renamer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == old:
                    node.name = new
                return node
        return Renamer().visit(tree)

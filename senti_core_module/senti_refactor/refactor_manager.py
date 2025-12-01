"""
FAZA 11 — Refactor Manager
High-level orchestrator for self-refactor operations.
"""

from pathlib import Path
from senti_core_module.senti_refactor.refactor_engine import RefactorEngine
from senti_core_module.senti_core.services.event_bus import EventBus

class RefactorManager:
    def __init__(self, project_root: Path, event_bus: EventBus):
        self.engine = RefactorEngine(project_root, event_bus)
        self.project_root = project_root

    def apply_refactor(self, file: str, patch: dict):
        file_path = self.project_root / file
        return self.engine.apply_patch(file_path, patch)

    def suggest_refactor(self, file: str):
        """
        Placeholder – FAZA 15 will add AI suggestions.
        """
        return {
            "status": "suggestion",
            "file": file,
            "message": "AI suggestions coming in FAZA 15."
        }

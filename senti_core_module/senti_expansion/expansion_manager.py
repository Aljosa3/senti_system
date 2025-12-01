"""
FAZA 10 — Expansion Manager
High-level orchestrator controlling AI expansion operations.
"""

from pathlib import Path
from senti_core_module.senti_expansion.expansion_engine import ExpansionEngine
from senti_core_module.senti_core.services.event_bus import EventBus


class ExpansionManager:
    """
    Coordinates expansion requests from AI agents or the OS.
    """

    def __init__(self, project_root: Path, event_bus: EventBus):
        self.project_root = project_root
        self.event_bus = event_bus
        self.engine = ExpansionEngine(project_root, event_bus)

    def create_module(self, name: str, directory="modules"):
        """
        Public API for module creation.
        """
        return self.engine.expand(name, directory)

    def handle_ai_request(self, request: dict):
        """
        Handle complex expansion requests from AI orchestration layers.
        """
        action = request.get("action")

        if action == "create_module":
            name = request.get("name")
            directory = request.get("directory", "modules")
            return self.create_module(name, directory)

        return {"status": "error", "message": "Unknown expansion request"}

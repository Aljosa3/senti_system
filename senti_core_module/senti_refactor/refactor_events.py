"""
FAZA 11 — Refactor Events
EventBus events for refactor operations.
"""

from dataclasses import dataclass

@dataclass
class RefactorEvent:
    event_type: str
    payload: dict

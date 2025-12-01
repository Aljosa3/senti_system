"""
FAZA 10 — Expansion Events
EventBus integration for system expansion operations.
"""

from dataclasses import dataclass


@dataclass
class ExpansionEvent:
    event_type: str
    payload: dict

from __future__ import annotations

"""
senti_core.task_orchestration
=============================

Razširjeni Task Orchestration Engine za FAZA 5 — AI Operational Layer.

- Centralno mesto za planiranje, razvrščanje in sledenje taskom
- Integracijska točka med:
    - AICommandProcessor (AI Operational Layer)
    - EventBus / Reasoning / Validator (senti_core)
    - OS Kernel / Services (senti_os)
"""

from .engine import TaskOrchestrationEngine, TaskStatus, TaskRecord

__all__ = [
    "TaskOrchestrationEngine",
    "TaskStatus",
    "TaskRecord",
]

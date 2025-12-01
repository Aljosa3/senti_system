"""
FAZA 11 — Self-Refactor Engine

Code refactoring and optimization utilities.
"""

from .refactor_engine import RefactorEngine
from .refactor_manager import RefactorManager
from .refactor_rules import RefactorRules
from .refactor_events import RefactorEvent
from .ast_patch_template import ASTPatchTemplate

__version__ = "1.0.0"

__all__ = [
    "RefactorEngine",
    "RefactorManager",
    "RefactorRules",
    "RefactorEvent",
    "ASTPatchTemplate"
]

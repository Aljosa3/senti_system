"""
Senti Expansion - AI Expansion Engine (FAZA 10)

This module contains the FAZA 10 AI Expansion Engine components.

Main Components:
- ExpansionManager: High-level orchestrator for expansion operations
- ExpansionEngine: Core engine for AI-driven system expansion
- ExpansionRules: Security and integrity rules for expansion
- ModuleTemplate: Template generator for new modules
- ExpansionEvent: Event bus integration for expansion operations
"""

__version__ = "1.0.0"

from senti_core_module.senti_expansion.expansion_manager import ExpansionManager
from senti_core_module.senti_expansion.expansion_engine import ExpansionEngine
from senti_core_module.senti_expansion.expansion_rules import ExpansionRules
from senti_core_module.senti_expansion.module_template import ModuleTemplate
from senti_core_module.senti_expansion.expansion_events import ExpansionEvent

__all__ = [
    "ExpansionManager",
    "ExpansionEngine",
    "ExpansionRules",
    "ModuleTemplate",
    "ExpansionEvent",
]

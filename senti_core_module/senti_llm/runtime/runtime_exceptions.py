"""
FAZA 34–35 — Custom LLM Runtime Exceptions
"""


class RouterError(Exception):
    """Napaka v Execution Router plasti."""


class OrchestratorError(Exception):
    """Napaka v Execution Orchestrator plasti."""


class InvalidActionError(Exception):
    """Ko akcija ni v pravilnem formatu ali ne obstaja handler."""

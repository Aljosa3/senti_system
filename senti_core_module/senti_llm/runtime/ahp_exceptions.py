"""
FAZA 46 — AHP Exceptions
FILE 6/8: ahp_exceptions.py

Typed exception definitions for Anti-Hallucination Protocol (AHP).
No logic, no validation, no I/O, no imports, no side effects.
Pure semantic layer.
"""


class AHPError(Exception):
    """Base exception for Anti-Hallucination Protocol."""


class AHPStructureError(AHPError):
    """Raised when generated output violates required structure."""


class AHPForbiddenOperationError(AHPError):
    """Raised when forbidden operations are detected."""


class AHPForbiddenImportError(AHPError):
    """Raised when forbidden imports are detected."""


class AHPForbiddenCallError(AHPError):
    """Raised when forbidden function calls are detected."""


class AHPLogicalInconsistencyError(AHPError):
    """Raised when logical contradictions are detected."""


class AHPFactValidationError(AHPError):
    """Raised when unverifiable or false claims are detected."""

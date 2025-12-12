"""
FAZA 46 — Name Resolution Guard
FILE 2/8: name_resolution_guard.py

Deterministic guard layer for canonical name enforcement.
Uses canonical_name.py (FILE 1/8) to prevent use of non-canonical names.

Purpose:
- Runtime security layer for name validation
- Prevent non-canonical name usage
- Read-only validation (no normalization)

Rules:
- No I/O
- No print/log
- No heuristics
- No global state
- No input mutation
- No imports outside FILE 1/8
- No fallback logic
- Deterministic execution
- Validation + exceptions only
"""

from senti_core_module.senti_llm.runtime.canonical_name import (
    CANONICAL_NAME,
    resolve_name,
)


class NameResolutionError(Exception):
    """Raised when name resolution fails."""


class NameResolutionGuard:
    """Guard layer for canonical name enforcement."""

    def __init__(self):
        """Initialize name resolution guard."""
        pass

    def require_canonical(self, name: str) -> str:
        """
        Require a valid canonical name.

        Args:
            name (str): Name to validate.

        Returns:
            str: Canonical name ("senti") if valid.

        Raises:
            NameResolutionError: If resolution fails or result is not canonical.
        """
        try:
            resolved = resolve_name(name)
        except Exception as exc:
            raise NameResolutionError(f"Name resolution failed: {exc}")

        if resolved != CANONICAL_NAME:
            raise NameResolutionError(f"Resolved name '{resolved}' does not match canonical name '{CANONICAL_NAME}'")

        return CANONICAL_NAME

    def validate_optional(self, name: str | None) -> str | None:
        """
        Validate optional name (allows None).

        Args:
            name (str | None): Name to validate, or None.

        Returns:
            str | None: Canonical name if valid, None if input is None.

        Raises:
            NameResolutionError: If name is provided but resolution fails.
        """
        if name is None:
            return None
        return self.require_canonical(name)

    def is_allowed(self, name: str) -> bool:
        """
        Check if name is allowed (non-throwing).

        Args:
            name (str): Name to check.

        Returns:
            bool: True if name resolves to canonical name, False otherwise.
        """
        try:
            resolved = resolve_name(name)
            return resolved == CANONICAL_NAME
        except Exception:
            return False

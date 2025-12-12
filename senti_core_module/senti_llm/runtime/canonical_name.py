"""
FAZA 46 — Canonical Naming Layer
FILE 1/8: canonical_name.py

This module defines the canonical system name and the strict rules
for resolving aliases into the canonical identifier.

Purpose:
- Enforce a single immutable system identity
- Prevent name drift, ambiguity, and spoofing
- Serve as the root of name governance for the entire runtime

Rules:
- Deterministic
- No I/O
- No side effects
- No external dependencies
"""


# =====================================================================
# Canonical System Name
# =====================================================================

CANONICAL_NAME: str = "senti"


# =====================================================================
# Alias Recognition Table (ART)
# =====================================================================

_ALIAS_TABLE: dict[str, str] = {
    "senti": CANONICAL_NAME,
    "senti_os": CANONICAL_NAME,
    "senti-system": CANONICAL_NAME,
    "senti_system": CANONICAL_NAME,
    "senti-core": CANONICAL_NAME,
    "senti.core": CANONICAL_NAME,
    "senti-ai": CANONICAL_NAME,
}


# =====================================================================
# Exceptions
# =====================================================================

class InvalidCanonicalNameError(ValueError):
    """Raised when canonical name is invalid or immutable rules are violated."""


class UnknownAliasError(ValueError):
    """Raised when an unknown or disallowed alias is provided."""


# =====================================================================
# Core Resolution Functions
# =====================================================================

def resolve_name(name: str) -> str:
    """
    Resolve a given name or alias to the canonical system name.

    Args:
        name (str): Input name or alias.

    Returns:
        str: Canonical system name.

    Raises:
        InvalidCanonicalNameError: If input is not a valid string.
        UnknownAliasError: If alias is not recognized.
    """
    if not isinstance(name, str):
        raise InvalidCanonicalNameError("Name must be a string.")

    normalized = name.strip().lower()

    if not normalized:
        raise InvalidCanonicalNameError("Name cannot be empty.")

    if normalized == CANONICAL_NAME:
        return CANONICAL_NAME

    if normalized in _ALIAS_TABLE:
        return _ALIAS_TABLE[normalized]

    raise UnknownAliasError(f"Unknown or disallowed alias: '{name}'")


# =====================================================================
# Helper Functions (Non-Throwing)
# =====================================================================

def is_valid_alias(name: str) -> bool:
    """
    Check whether a name is a valid alias or canonical name.

    Args:
        name (str): Name to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(name, str):
        return False

    normalized = name.strip().lower()
    return normalized == CANONICAL_NAME or normalized in _ALIAS_TABLE


def get_canonical_name() -> str:
    """
    Return the canonical system name.

    Returns:
        str: Canonical name.
    """
    return CANONICAL_NAME


def get_all_aliases() -> tuple[str, ...]:
    """
    Return all recognized aliases (excluding canonical name).

    Returns:
        tuple[str, ...]: All allowed aliases.
    """
    return tuple(sorted(_ALIAS_TABLE.keys()))

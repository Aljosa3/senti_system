"""
Mandate → Intent binding logic — Phase II.3

Purpose:
- Deterministically bind a valid mandate to an intent
- Explain the binding
- Never allow execution

This module performs NO actions.
"""

# Static mandate → intent mapping (Phase II.3)
MANDATE_INTENT_MAP = {
    "ANALYZE": "QUESTION",
    "DESCRIBE": "META",
    "EXPLAIN": "QUESTION",
    "SUMMARIZE": "META",
    "CLASSIFY": "META",
    "REFLECT": "META",
}

def bind_mandate_to_intent(mandate: str) -> dict:
    """
    Bind a mandate to an intent deterministically.

    Args:
        mandate: Normalized mandate string

    Returns:
        dict describing the binding result
    """

    if not mandate or not mandate.strip():
        return {
            "mandate": None,
            "intent": "NO_BINDING",
            "binding": "NONE",
            "reason": "Empty mandate",
            "execution_allowed": False,
        }

    normalized = mandate.strip().upper()

    if normalized in MANDATE_INTENT_MAP:
        return {
            "mandate": normalized,
            "intent": MANDATE_INTENT_MAP[normalized],
            "binding": "STATIC",
            "reason": "Mandate bound using static Phase II.3 mapping",
            "execution_allowed": False,
        }

    return {
        "mandate": normalized,
        "intent": "NO_BINDING",
        "binding": "NONE",
        "reason": "Mandate not eligible for intent binding",
        "execution_allowed": False,
    }

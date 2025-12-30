"""
Mandate validation logic — Phase II.2

Purpose:
- Deterministically validate mandate vocabulary
- Explain acceptance or rejection
- Never grant execution authority

This module performs NO actions.
"""

# Mandate vocabulary (Phase II.1)
MANDATE_VOCABULARY = {
    "ANALYZE",
    "DESCRIBE",
    "EXPLAIN",
    "SUMMARIZE",
    "CLASSIFY",
    "REFLECT",
}

def validate_mandate(mandate: str) -> dict:
    """
    Validate a mandate string against allowed vocabulary.

    Args:
        mandate: Raw mandate input

    Returns:
        dict with validation result
    """

    if not mandate or not mandate.strip():
        return {
            "valid": False,
            "mandate": None,
            "reason": "Empty mandate",
            "execution_allowed": False,
        }

    normalized = mandate.strip().upper()

    if normalized in MANDATE_VOCABULARY:
        return {
            "valid": True,
            "mandate": normalized,
            "reason": "Mandate is defined in approved vocabulary",
            "execution_allowed": False,
        }

    return {
        "valid": False,
        "mandate": normalized,
        "reason": "Mandate not recognized",
        "execution_allowed": False,
    }

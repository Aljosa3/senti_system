"""
Intent → Advisory Response Policy — Phase II.4

Purpose:
- Define what kind of response is allowed per intent
- Preserve strict advisory-only guarantees
- Prevent execution or instruction leakage

This module performs NO actions.
"""

INTENT_RESPONSE_POLICY = {
    "QUESTION": {
        "allowed": "EXPLANATORY",
        "forbidden": [
            "INSTRUCTIONS",
            "STEPS",
            "ACTIONS",
            "EXECUTION",
        ],
        "description": "High-level explanation only. No steps or conclusions."
    },
    "META": {
        "allowed": "DESCRIPTIVE",
        "forbidden": [
            "ANALYSIS",
            "EXECUTION",
            "DECISION",
        ],
        "description": "Descriptive or reflective information only."
    },
    "PLAN": {
        "allowed": "STRUCTURAL",
        "forbidden": [
            "STEPS",
            "TASKS",
            "EXECUTION",
        ],
        "description": "Abstract structure only. No actionable planning."
    },
    "NO_INTENT": {
        "allowed": "ACKNOWLEDGEMENT",
        "forbidden": [
            "ASSUMPTIONS",
            "EXECUTION",
        ],
        "description": "Acknowledge uncertainty without inference."
    },
}

def get_response_policy(intent: str) -> dict:
    """
    Return the advisory response policy for a given intent.

    Args:
        intent: Intent string

    Returns:
        dict describing allowed response boundaries
    """

    if not intent or not intent.strip():
        return INTENT_RESPONSE_POLICY["NO_INTENT"]

    normalized = intent.strip().upper()

    return INTENT_RESPONSE_POLICY.get(
        normalized,
        INTENT_RESPONSE_POLICY["NO_INTENT"]
    )

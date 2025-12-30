"""
Execution Attempt Classification — Phase III.2

Purpose:
- Classify potential execution attempts
- Describe the nature of the attempt
- Never allow execution

Authority: NONE
Execution: FORBIDDEN

This module performs NO actions.
"""

EXECUTION_ATTEMPT_TYPES = [
    "NONE",
    "INSTRUCTION",
    "ACTION_REQUEST",
    "SYSTEM_MODIFICATION",
    "UNKNOWN",
]

def classify_execution_attempt(intent: str | None) -> dict:
    """
    Classify a potential execution attempt based on intent.

    Args:
        intent: Intent identifier string

    Returns:
        dict describing execution attempt classification
    """

    if not intent or not intent.strip():
        return _result("UNKNOWN", "No intent provided")

    normalized = intent.strip().upper()

    if normalized in ["QUESTION", "META"]:
        return _result("NONE", "Intent does not imply execution")

    if normalized in ["REQUEST"]:
        return _result("ACTION_REQUEST", "Intent implies a request for action")

    if normalized in ["PLAN"]:
        return _result("INSTRUCTION", "Intent implies procedural guidance")

    return _result("UNKNOWN", "Intent could not be classified safely")


def _result(attempt_type: str, reason: str) -> dict:
    return {
        "attempt_type": attempt_type,
        "execution_allowed": False,
        "reason": reason,
        "phase": "III.2",
        "governance": "PHASE_III2_LOCK",
    }

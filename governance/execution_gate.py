"""
Phase 61.4 — Execution Gate

Passive pre-execution permission check.
Evaluates lifecycle and decision results to determine execution permission.
"""


def check_execution(lifecycle_result, decision_result):
    """
    Check if execution is permitted based on lifecycle and decision results.

    Args:
        lifecycle_result: Result from lifecycle enforcement check
        decision_result: Result from decision gate check

    Returns:
        "EXECUTION_ALLOWED" if both lifecycle is ALLOWED and decision is APPROVED
        "EXECUTION_DENIED" if either lifecycle or decision is DENIED
        "EXECUTION_UNKNOWN" in all other cases
    """
    if lifecycle_result == "ALLOWED" and decision_result == "APPROVED":
        return "EXECUTION_ALLOWED"

    if lifecycle_result == "DENIED" or decision_result == "DENIED":
        return "EXECUTION_DENIED"

    return "EXECUTION_UNKNOWN"

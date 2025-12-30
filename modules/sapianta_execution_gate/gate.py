"""
Execution Gate — Phase III.1

Purpose:
- Provide a formal execution boundary
- Explicitly deny all execution attempts
- Explain why execution is forbidden

Authority: NONE
Execution: FORBIDDEN

This module performs NO actions.
"""

def check_execution_allowed(context: dict | None = None) -> dict:
    """
    Determine whether execution is allowed.

    Args:
        context: Optional execution context (ignored in Phase III.1)

    Returns:
        dict describing execution permission status
    """

    return {
        "execution_allowed": False,
        "reason": "Execution is not permitted in Phase III.1",
        "phase": "III.1",
        "governance": "PHASE_III1_LOCK",
    }

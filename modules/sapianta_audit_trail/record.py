"""
Audit Trail — Phase III.3

Purpose:
- Describe system decisions without side effects
- Provide a structured audit record
- Never store or transmit data

Authority: NONE
Execution: FORBIDDEN

This module performs NO actions.
"""

def create_audit_record(
    intent: str,
    execution_attempt_type: str,
    execution_allowed: bool,
    reason: str,
    phase: str,
) -> dict:
    """
    Create an immutable audit record describing a system decision.

    Args:
        intent: Detected intent
        execution_attempt_type: Classified execution attempt type
        execution_allowed: Whether execution was allowed
        reason: Explanation for the decision
        phase: Phase identifier

    Returns:
        dict representing an audit record
    """

    return {
        "intent": intent,
        "execution_attempt_type": execution_attempt_type,
        "execution_allowed": execution_allowed,
        "reason": reason,
        "phase": phase,
    }

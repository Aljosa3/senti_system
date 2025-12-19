"""
Phase 63.3 — Decision Revocation

Passive, read-only Decision Revocation record structure.
Provides deterministic access to revocation facts.
"""

# Internal placeholder data source (empty by default)
_DECISION_REVOCATIONS = {}


def is_decision_revoked(decision_id):
    """
    Check if a decision has been revoked.

    Args:
        decision_id: The decision identifier to check

    Returns:
        True if a revocation record exists
        False otherwise
    """
    if decision_id in _DECISION_REVOCATIONS:
        return True
    else:
        return False


def get_decision_revocation(decision_id):
    """
    Retrieve the revocation record for the given decision.

    Args:
        decision_id: The decision identifier to retrieve

    Returns:
        Revocation record dictionary if it exists
        None if no revocation record exists
    """
    if decision_id in _DECISION_REVOCATIONS:
        return _DECISION_REVOCATIONS[decision_id]
    else:
        return None

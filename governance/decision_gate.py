"""
Phase 61.3 — Decision Gate

Passive decision existence check.
Returns decision status based on in-memory decision source.
"""

# Internal decision source (explicitly empty by default)
_DECISIONS = {}


def check_decision(module_id):
    """
    Check if a decision exists for the given module.

    Args:
        module_id: The module identifier to check

    Returns:
        "APPROVED" if decision exists and is True
        "DENIED" if decision exists and is False
        "UNKNOWN" if no decision exists
    """
    if module_id in _DECISIONS:
        if _DECISIONS[module_id] is True:
            return "APPROVED"
        else:
            return "DENIED"
    else:
        return "UNKNOWN"

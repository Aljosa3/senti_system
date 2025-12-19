"""
Phase 62.1 — Execution Request

Passive check for the existence of an execution request.
Returns request presence status based on in-memory request source.
"""

# Internal request source (explicitly empty by default)
_EXECUTION_REQUESTS = {}


def check_execution_request(module_id):
    """
    Check if an execution request exists for the given module.

    Args:
        module_id: The module identifier to check

    Returns:
        "REQUEST_PRESENT" if execution request exists
        "REQUEST_ABSENT" if no execution request exists
    """
    if module_id in _EXECUTION_REQUESTS:
        return "REQUEST_PRESENT"
    else:
        return "REQUEST_ABSENT"

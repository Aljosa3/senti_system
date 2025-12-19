"""
Phase 62.2 — Execution Context

Passive check for the validity of an execution context.
Returns context validity status based on in-memory context source.
"""

# Internal context source (explicitly empty by default)
_EXECUTION_CONTEXTS = {}


def check_execution_context(module_id):
    """
    Check if a valid execution context exists for the given module.

    Args:
        module_id: The module identifier to check

    Returns:
        "CONTEXT_VALID" if execution context exists
        "CONTEXT_INVALID" if no execution context exists
    """
    if module_id in _EXECUTION_CONTEXTS:
        return "CONTEXT_VALID"
    else:
        return "CONTEXT_INVALID"

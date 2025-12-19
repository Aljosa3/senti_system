"""
Phase 64.3 — Execution Invocation

First real execution touchpoint.
Orchestrates a single execution attempt with safety checks.
"""

from governance.execution_binding import get_execution_binding
from governance.execution_constraints import check_execution_constraints


def invoke_execution(module_id):
    """
    Invoke execution for the given module if all conditions are met.

    Args:
        module_id: The module identifier to execute

    Returns:
        "EXECUTION_TRIGGERED" if execution is triggered
        "INVOCATION_ABORTED" if any condition is not met
    """
    # Retrieve binding
    binding = get_execution_binding(module_id)
    if binding is None:
        return "INVOCATION_ABORTED"

    # Check binding enabled
    if binding.get("enabled") is not True:
        return "INVOCATION_ABORTED"

    # Check safety constraints
    if check_execution_constraints(module_id) != "CONSTRAINTS_SATISFIED":
        return "INVOCATION_ABORTED"

    # Trigger execution
    return _trigger_execution(binding)


def _trigger_execution(binding):
    """
    Placeholder for triggering actual execution.

    Args:
        binding: The execution binding

    Returns:
        "EXECUTION_TRIGGERED"
    """
    return "EXECUTION_TRIGGERED"

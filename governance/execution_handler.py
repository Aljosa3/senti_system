"""
Phase 62.3 — Execution Handler

Orchestrates all governance checks and triggers a single execution if permitted.
This is NOT an agent, scheduler, or supervisor.
"""

from governance.lifecycle_enforcement import check_lifecycle
from governance.decision_gate import check_decision
from governance.execution_gate import check_execution
from governance.execution_request import check_execution_request
from governance.execution_context import check_execution_context


def handle_execution(module_id):
    """
    Handle execution request by performing all governance checks in order.
    Triggers execution only if all checks pass.

    Args:
        module_id: The module identifier to execute

    Returns:
        "EXECUTION_STARTED" if all checks pass and execution is triggered
        "EXECUTION_ABORTED" if any check fails
    """
    # Check lifecycle
    lifecycle_result = check_lifecycle(module_id)
    if lifecycle_result != "ALLOWED":
        return "EXECUTION_ABORTED"

    # Check decision
    decision_result = check_decision(module_id)
    if decision_result != "APPROVED":
        return "EXECUTION_ABORTED"

    # Check execution gate
    execution_permission = check_execution(lifecycle_result, decision_result)
    if execution_permission != "EXECUTION_ALLOWED":
        return "EXECUTION_ABORTED"

    # Check execution request
    request_status = check_execution_request(module_id)
    if request_status != "REQUEST_PRESENT":
        return "EXECUTION_ABORTED"

    # Check execution context
    context_status = check_execution_context(module_id)
    if context_status != "CONTEXT_VALID":
        return "EXECUTION_ABORTED"

    # All checks passed - trigger execution
    _trigger_execution(module_id)
    return "EXECUTION_STARTED"


def _trigger_execution(module_id):
    """
    Placeholder for triggering actual execution.
    """
    pass

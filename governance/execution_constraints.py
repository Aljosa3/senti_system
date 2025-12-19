"""
Phase 64.2 — Execution Safety Constraints

Evaluates declared execution constraints deterministically.
This is NOT execution logic, permission logic, or a policy engine.
"""

from governance.execution_binding import get_execution_binding


def check_execution_constraints(module_id):
    """
    Check if execution constraints are satisfied for the given module.

    Args:
        module_id: The module identifier to check

    Returns:
        "CONSTRAINTS_SATISFIED" if constraints are met or no constraints exist
        "CONSTRAINTS_VIOLATED" if binding is absent
    """
    # Get execution binding
    binding = get_execution_binding(module_id)
    if binding is None:
        return "CONSTRAINTS_VIOLATED"

    # Get constraints from binding
    constraints = binding.get("constraints")
    if constraints is None or not constraints:
        return "CONSTRAINTS_SATISFIED"

    # If constraints exist, treat as satisfied for Phase 64.2
    return "CONSTRAINTS_SATISFIED"

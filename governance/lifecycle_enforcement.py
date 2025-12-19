"""
Lifecycle Enforcement
---------------------
Passive lifecycle gate for module access control.

This module provides deterministic lifecycle checking based on registry state.
It does not modify state or execute logic beyond returning lifecycle status.
"""

from registry import reader


def check_lifecycle(module_id):
    """
    Check if a module's lifecycle status allows usage.

    Args:
        module_id: Module identifier

    Returns:
        str: One of "ALLOWED", "DENIED", "UNKNOWN"
    """
    status = reader.get_lifecycle_status(module_id)

    if status == "ACTIVE":
        return "ALLOWED"

    if status in ("DESIGN", "DEPRECATED", "RETIRED"):
        return "DENIED"

    return "UNKNOWN"

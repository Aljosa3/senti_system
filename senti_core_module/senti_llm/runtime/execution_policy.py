"""
FAZA 48 — Execution Policy
FILE 3/6: execution_policy.py

Deterministic allow/deny rules for execution layer.
Pure policy enforcement — no execution, no state.
"""

# =====================================================================
# Exceptions
# =====================================================================

class ExecutionPolicyError(Exception):
    """Base exception for execution policy violations."""


class ActionDeniedError(ExecutionPolicyError):
    """Raised when an action is explicitly denied by policy."""


# =====================================================================
# Policy Rules
# =====================================================================

ALLOWED_ACTIONS = (
    "read",
    "query.status",
    "list.modules",
)

DENIED_ACTIONS = (
    "write",
    "delete",
    "rm",
    "execute.shell",
)


# =====================================================================
# Policy Functions
# =====================================================================

def is_action_allowed(action: str) -> bool:
    """
    Check whether an action is allowed by execution policy.

    Args:
        action (str): Action name.

    Returns:
        bool: True if allowed, False otherwise.
    """
    if not isinstance(action, str):
        return False

    if action in DENIED_ACTIONS:
        return False

    if action in ALLOWED_ACTIONS:
        return True

    return False


def enforce_policy(action: str) -> None:
    """
    Enforce execution policy for a given action.

    Args:
        action (str): Action name.

    Raises:
        ActionDeniedError: If action is not allowed.
    """
    if not isinstance(action, str):
        raise ActionDeniedError(f"Action must be str, got: {type(action)}")

    if action in DENIED_ACTIONS:
        raise ActionDeniedError(f"Action explicitly denied: {action}")

    if action not in ALLOWED_ACTIONS:
        raise ActionDeniedError(f"Action not allowed by policy: {action}")

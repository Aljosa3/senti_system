"""
FAZA 47 — Execution Routing Layer
FILE 3/5: execution_policy_guard.py

Execution Policy Guard.
Validates whether a normalized command is allowed to be routed
to an execution layer.

Purpose:
- Enforce routing-level security
- Block forbidden actions early
- Ensure action is explicitly allowed
- No execution, no routing, no side effects

Rules:
- No I/O
- No print/log
- Deterministic
- Validation + exceptions only
"""

from senti_core_module.senti_llm.runtime.execution_routes import (
    EXECUTION_ROUTES,
    ALLOWED_ACTIONS,
    BLOCKED_ACTIONS,
)


# =====================================================================
# Exceptions
# =====================================================================

class ExecutionPolicyError(Exception):
    """Base exception for execution policy violations."""


class BlockedActionError(ExecutionPolicyError):
    """Raised when an action is explicitly blocked."""


class UnknownActionError(ExecutionPolicyError):
    """Raised when action is not defined in execution routes."""


# =====================================================================
# Execution Policy Guard
# =====================================================================

class ExecutionPolicyGuard:
    """Policy guard for execution routing layer."""

    def __init__(self):
        """Initialize execution policy guard."""
        pass

    def validate(self, command: dict) -> None:
        """
        Validate normalized command against execution policy.

        Args:
            command (dict): Normalized command.

        Raises:
            ExecutionPolicyError: If command violates execution policy.
        """
        if not isinstance(command, dict):
            raise ExecutionPolicyError("Command must be dict")

        if "action" not in command:
            raise ExecutionPolicyError("Command missing required field: action")

        action = command["action"]

        if not isinstance(action, str):
            raise ExecutionPolicyError("Action must be string")

        if action in BLOCKED_ACTIONS:
            raise BlockedActionError(f"Action is blocked: {action}")

        if action not in ALLOWED_ACTIONS:
            raise UnknownActionError(f"Action is not allowed: {action}")

        if action not in EXECUTION_ROUTES:
            raise UnknownActionError(f"No execution route defined for action: {action}")

"""
FAZA 47 — Execution Routing Layer
FILE 4/5: execution_dispatcher.py

Execution Dispatcher.
Routes validated, normalized commands to execution routes.

This layer:
- Does NOT parse strings
- Does NOT normalize input
- Does NOT execute anything
- Does NOT call handlers
- Only resolves execution route identifiers

Rules:
- No I/O
- No print/log
- No try/except
- Deterministic
"""

from senti_core_module.senti_llm.runtime.execution_routes import EXECUTION_ROUTES
from senti_core_module.senti_llm.runtime.execution_policy_guard import ExecutionPolicyGuard


# =====================================================================
# Exceptions
# =====================================================================

class ExecutionDispatchError(Exception):
    """Raised when execution dispatch fails."""


# =====================================================================
# Execution Dispatcher
# =====================================================================

class ExecutionDispatcher:
    """Dispatches normalized commands to execution route identifiers."""

    def __init__(self, policy_guard: ExecutionPolicyGuard):
        self.policy_guard = policy_guard

    def dispatch(self, command: dict) -> str:
        """
        Resolve execution route for a normalized command.

        Args:
            command (dict): Normalized + validated command.

        Returns:
            str: Execution route identifier (e.g. 'file_executor').

        Raises:
            ExecutionDispatchError
        """
        if not isinstance(command, dict):
            raise ExecutionDispatchError("Command must be dict")

        # Enforce execution policy (allow/deny)
        self.policy_guard.validate(command)

        action = command.get("action")
        if not action:
            raise ExecutionDispatchError("Missing action field")

        if action not in EXECUTION_ROUTES:
            raise ExecutionDispatchError(f"No execution route for action: {action}")

        route = EXECUTION_ROUTES[action]

        if not isinstance(route, str):
            raise ExecutionDispatchError(
                f"Invalid execution route definition for action '{action}'"
            )

        return route

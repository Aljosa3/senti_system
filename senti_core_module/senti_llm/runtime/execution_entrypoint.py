"""
FAZA 47 — Execution Entrypoint
FILE 5/5: execution_entrypoint.py

Single, safe entry point for executing runtime commands.
Pure orchestration layer — no logic, no validation, no routing rules.
"""

from senti_core_module.senti_llm.runtime.execution_dispatcher import ExecutionDispatcher
from senti_core_module.senti_llm.runtime.execution_policy_guard import ExecutionPolicyGuard


class ExecutionEntrypoint:
    """Safe execution entry point for runtime commands."""

    def __init__(self):
        """Initialize execution entrypoint with policy guard and dispatcher."""
        policy = ExecutionPolicyGuard()
        self.dispatcher = ExecutionDispatcher(policy)

    def execute(self, command: dict):
        """
        Execute a validated and normalized command.

        Args:
            command (dict): Normalized, validated runtime command.

        Returns:
            Any: Result returned by the resolved executor handler.
        """
        handler = self.dispatcher.dispatch(command)
        return handler(command)

"""
FAZA 48 — Execution Budget
FILE 2/6: execution_budget.py

Deterministic execution budget definition.
Defines hard limits for execution steps and runtime.
Pure policy — no timing, no execution.
"""

from dataclasses import dataclass


class ExecutionBudgetExceededError(Exception):
    """Raised when execution budget is exceeded."""


@dataclass(frozen=True)
class ExecutionBudget:
    """Immutable execution budget limits."""

    max_steps: int
    max_runtime_ms: int

    def validate_steps(self, used_steps: int) -> None:
        """Validate step usage against budget."""
        if not isinstance(used_steps, int):
            raise TypeError(f"used_steps must be int, got: {type(used_steps)}")

        if used_steps > self.max_steps:
            raise ExecutionBudgetExceededError(
                f"Step budget exceeded: {used_steps} > {self.max_steps}"
            )

    def validate_runtime(self, runtime_ms: int) -> None:
        """Validate runtime usage against budget."""
        if not isinstance(runtime_ms, int):
            raise TypeError(f"runtime_ms must be int, got: {type(runtime_ms)}")

        if runtime_ms > self.max_runtime_ms:
            raise ExecutionBudgetExceededError(
                f"Runtime budget exceeded: {runtime_ms}ms > {self.max_runtime_ms}ms"
            )

    def is_within_budget(self, used_steps: int, runtime_ms: int) -> bool:
        """Check budget without raising."""
        try:
            self.validate_steps(used_steps)
            self.validate_runtime(runtime_ms)
            return True
        except Exception:
            return False

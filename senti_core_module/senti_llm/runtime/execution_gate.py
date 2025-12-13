"""
FAZA 48 — Execution Gate
FILE 6/6: execution_gate.py

Final safety gate before execution.
Combines:
- SandboxContext
- ExecutionBudget
- ExecutionPolicy

No execution, no routing, no I/O.
Pure validation and blocking layer.
"""

from senti_core_module.senti_llm.runtime.sandbox_context import SandboxContext
from senti_core_module.senti_llm.runtime.execution_budget import ExecutionBudget
from senti_core_module.senti_llm.runtime.execution_policy import enforce_policy
from senti_core_module.senti_llm.runtime.execution_context_validator import (
    validate_execution_context,
)


# =====================================================================
# Exceptions
# =====================================================================

class ExecutionGateError(Exception):
    """Raised when execution gate validation fails."""


# =====================================================================
# Execution Gate
# =====================================================================

def execution_gate(
    context: SandboxContext,
    budget: ExecutionBudget,
    steps: int,
    runtime_ms: int,
) -> None:
    """
    Final execution safety gate.

    Args:
        context (SandboxContext): Immutable execution context.
        budget (ExecutionBudget): Execution limits.
        steps (int): Planned execution steps.
        runtime_ms (int): Planned runtime in milliseconds.

    Raises:
        ExecutionGateError: If any validation fails.
    """
    if not isinstance(context, SandboxContext):
        raise ExecutionGateError(f"Invalid context type: {type(context)}")

    if not isinstance(budget, ExecutionBudget):
        raise ExecutionGateError(f"Invalid budget type: {type(budget)}")

    # Policy enforcement (action-level)
    enforce_policy(context.action)

    # ⬇️ POZICIJSKI klic (pravilno)
    validate_execution_context(
        context,
        budget,
        steps,
        runtime_ms,
    )

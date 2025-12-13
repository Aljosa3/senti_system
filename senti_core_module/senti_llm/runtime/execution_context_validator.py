"""
FAZA 48 — Execution Context Validator
FILE 4/6: execution_context_validator.py

Final validation layer before execution.
Validates sandbox context, execution budget, policy, and limits.

Pure validation:
- No execution
- No I/O
- No state
- Deterministic
"""

from senti_core_module.senti_llm.runtime.sandbox_context import SandboxContext
from senti_core_module.senti_llm.runtime.execution_policy import enforce_policy
from senti_core_module.senti_llm.runtime.execution_budget import ExecutionBudget


# =====================================================================
# Exceptions
# =====================================================================

class ExecutionContextError(Exception):
    """Base exception for execution context validation errors."""


class InvalidContextError(ExecutionContextError):
    """Raised when execution context is invalid."""


# =====================================================================
# Validation Function
# =====================================================================

def validate_execution_context(
    ctx: SandboxContext,
    budget: ExecutionBudget,
    steps: int,
    runtime_ms: int,
) -> None:
    """
    Validate execution context before execution.

    Args:
        ctx (SandboxContext): Immutable execution context.
        budget (ExecutionBudget): Execution limits.
        steps (int): Planned execution steps.
        runtime_ms (int): Planned runtime in milliseconds.

    Raises:
        InvalidContextError: If context or parameters are invalid.
        ActionDeniedError: If action is denied by execution policy.
        ExecutionBudgetExceededError: If limits are exceeded.
    """

    # 1️⃣ Validate context type
    if not isinstance(ctx, SandboxContext):
        raise InvalidContextError(f"ctx must be SandboxContext, got: {type(ctx)}")

    # 2️⃣ Validate budget type
    if not isinstance(budget, ExecutionBudget):
        raise InvalidContextError(f"budget must be ExecutionBudget, got: {type(budget)}")

    # 3️⃣ Validate steps
    if not isinstance(steps, int) or steps < 0:
        raise InvalidContextError(f"steps must be int >= 0, got: {steps}")

    # 4️⃣ Validate runtime
    if not isinstance(runtime_ms, int) or runtime_ms < 0:
        raise InvalidContextError(f"runtime_ms must be int >= 0, got: {runtime_ms}")

    # 5️⃣ Enforce execution policy
    enforce_policy(ctx.action)

    # 6️⃣ Enforce execution budget
    budget.validate_steps(steps)
    budget.validate_runtime(runtime_ms)

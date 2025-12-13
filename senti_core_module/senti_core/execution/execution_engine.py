"""
Senti OS — Execution Layer
FAZA 50 — FILE 3/?

Resolver guard & executor contract validation
---------------------------------------------

Namen:
    - Validira rezultat executor_resolver.resolve().
    - Executor mora biti callable in sprejeti keyword-only argument `context`.
    - V primeru kršitve se execution zaključi z FAILED.
"""

from __future__ import annotations

import inspect
from typing import Any, Mapping, Optional, Callable

from .execution_result import ExecutionResult
from .execution_report import ExecutionReport
from .execution_hooks import ExecutionLifecycleHooks, NoOpExecutionLifecycleHooks
from .executor_invocation import invoke_executor_safely


class ExecutionEngine:
    """
    ExecutionEngine z:
        - guarded lifecycle hooki
        - resolver guardom (FAZA 50 — FILE 3/?)
    """

    def __init__(
        self,
        *,
        executor_resolver,
        hooks: Optional[ExecutionLifecycleHooks] = None,
    ) -> None:
        self._executor_resolver = executor_resolver
        self._hooks: ExecutionLifecycleHooks = (
            hooks if hooks is not None else NoOpExecutionLifecycleHooks()
        )

    def _validate_executor(self, executor: Any) -> Optional[str]:
        """
        Validira executor contract.
        Vrne None, če je OK, sicer error string.
        """
        if not callable(executor):
            return "resolver returned non-callable executor"

        try:
            sig = inspect.signature(executor)
        except (TypeError, ValueError):
            return "executor signature not introspectable"

        params = sig.parameters

        if "context" not in params:
            return "executor must accept keyword-only argument 'context'"

        param = params["context"]
        if param.kind is not inspect.Parameter.KEYWORD_ONLY:
            return "executor 'context' must be keyword-only"

        return None

    def execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
    ) -> ExecutionReport:
        """
        Izvede en execution turn z:
            - guarded hooki
            - resolver guardom
        """

        # 1) pre-execute hook
        try:
            self._hooks.pre_execute(execution_context, execution_budget)
        except BaseException as exc:
            return ExecutionReport.from_execution(
                execution_context,
                execution_budget,
                ExecutionResult.failed(
                    error=f"pre_execute hook failed: {exc.__class__.__name__}: {exc}"
                ),
            )

        # 2) resolve executor
        try:
            executor = self._executor_resolver.resolve(execution_context)
        except BaseException as exc:
            return ExecutionReport.from_execution(
                execution_context,
                execution_budget,
                ExecutionResult.failed(
                    error=f"resolver failed: {exc.__class__.__name__}: {exc}"
                ),
            )

        # 3) validate executor contract
        error = self._validate_executor(executor)
        if error is not None:
            return ExecutionReport.from_execution(
                execution_context,
                execution_budget,
                ExecutionResult.failed(error=error),
            )

        # 4) invoke executor safely
        result = invoke_executor_safely(
            executor=executor,
            execution_context=execution_context,
        )

        # 5) post-execute hook
        try:
            self._hooks.post_execute(execution_context, execution_budget, result)
        except BaseException as exc:
            result = ExecutionResult.failed(
                error=f"post_execute hook failed: {exc.__class__.__name__}: {exc}"
            )

        # 6) report
        return ExecutionReport.from_execution(
            execution_context,
            execution_budget,
            result,
        )

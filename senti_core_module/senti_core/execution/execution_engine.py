"""
Senti OS — Execution Layer
FAZA 50 — FILE 2/?

Guarded lifecycle hooks
----------------------

Namen:
    - Ojača minimalni execution tok z zaščito pred napakami v hookih.
    - Če hook pade, se execution deterministično zaključi z FAILED.
    - Brez dodajanja novih sposobnosti ali avtonomije.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .execution_result import ExecutionResult
from .execution_report import ExecutionReport
from .execution_hooks import ExecutionLifecycleHooks, NoOpExecutionLifecycleHooks
from .executor_invocation import invoke_executor_safely


class ExecutionEngine:
    """
    ExecutionEngine z guardi za lifecycle hooke (FAZA 50 — FILE 2/?).
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

    def execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
    ) -> ExecutionReport:
        """
        Izvede en execution turn z zaščitenimi hooki.

        Pravila:
            - Če pre_execute hook pade → execution FAILED, executor se ne kliče.
            - Executor se kliče natanko enkrat.
            - Če post_execute hook pade → execution FAILED.
            - Vedno vrne ExecutionReport.
        """

        # 1) pre-execute hook (guarded)
        try:
            self._hooks.pre_execute(execution_context, execution_budget)
        except BaseException as exc:
            failed = ExecutionResult.failed(
                error=f"pre_execute hook failed: {exc.__class__.__name__}: {exc}"
            )
            return ExecutionReport.from_execution(
                execution_context=execution_context,
                execution_budget=execution_budget,
                result=failed,
            )

        # 2) resolve executor (ne guardamo – resolver je del core toka)
        executor = self._executor_resolver.resolve(execution_context)

        # 3) invoke executor safely (že normalizira napake)
        result: ExecutionResult = invoke_executor_safely(
            executor=executor,
            execution_context=execution_context,
        )

        # 4) post-execute hook (guarded)
        try:
            self._hooks.post_execute(
                execution_context,
                execution_budget,
                result,
            )
        except BaseException as exc:
            result = ExecutionResult.failed(
                error=f"post_execute hook failed: {exc.__class__.__name__}: {exc}"
            )

        # 5) build execution report
        return ExecutionReport.from_execution(
            execution_context=execution_context,
            execution_budget=execution_budget,
            result=result,
        )

"""
Senti OS — Execution Layer
FAZA 49 — FILE 4/?

Safe Executor Invocation
------------------------

Namen:
    - Definira edino dovoljeno točko za klic executor-ja.
    - Zagotavlja, da se:
        * executor pokliče natanko enkrat,
        * vse napake zajamejo,
        * rezultat normalizira v ExecutionResult.

Pomembno:
    - Ta modul NE izvaja I/O.
    - NE izvaja logiranja.
    - NE vsebuje fallback logike.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .execution_result import ExecutionResult


# ---------------------------------------------------------------------------
# Executor Protocol (lokalna varnostna kopija tipa)
# ---------------------------------------------------------------------------


class ExecutorCallable(Protocol):
    """
    Protokol za executor.

    Executor:
        - sprejme execution_context kot keyword-only argument
        - vrne poljuben rezultat (NE ExecutionResult)
    """

    def __call__(self, *, context: Mapping[str, Any]) -> Any:
        ...


# ---------------------------------------------------------------------------
# Safe invocation
# ---------------------------------------------------------------------------


def invoke_executor_safely(
    *,
    executor: ExecutorCallable,
    execution_context: Mapping[str, Any],
) -> ExecutionResult:
    """
    Varno pokliče executor in normalizira rezultat.

    Pravila:
        - executor se pokliče natanko enkrat,
        - nobena izjema ne uide iz te funkcije,
        - vsi izhodi se pretvorijo v ExecutionResult.

    :param executor:
        Konkreten executor (že resolvan).

    :param execution_context:
        Validiran execution context.

    :returns:
        ExecutionResult.success(...) ali ExecutionResult.failed(...)
    """
    try:
        result = executor(context=execution_context)
        return ExecutionResult.success(value=result)
    except BaseException as exc:
        return ExecutionResult.failed(
            error=f"{exc.__class__.__name__}: {exc}"
        )

"""
Senti OS — Execution Layer
FAZA 49 — FILE 5/?

Execution Report
----------------

Namen:
    - Definira strukturiran povzetek enega execution turn-a.
    - Report je popolnoma deklarativen.
    - Ne vsebuje I/O, logiranja ali stranskih učinkov.

ExecutionReport:
    - se gradi iz obstoječih podatkov,
    - ne vpliva na execution flow,
    - je primeren za UI / CLI / audit sloje.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from types import MappingProxyType

from .execution_result import ExecutionResult


# ---------------------------------------------------------------------------
# Execution Report (immutabilen)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionReport:
    """
    Immutabilen povzetek enega execution turn-a.

    Polja:
        execution_context:
            Execution context, ki je bil uporabljen.
            (referenčni snapshot; ne sme se spreminjati)

        execution_budget:
            Budget, ki je veljal za ta execution.

        result:
            Normaliziran ExecutionResult.
    """

    execution_context: Mapping[str, Any]
    execution_budget: Mapping[str, Any]
    result: ExecutionResult

    # ------------------------------------------------------------------
    # Tovarniška metoda
    # ------------------------------------------------------------------

    @staticmethod
    def from_execution(
        *,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
        result: ExecutionResult,
    ) -> "ExecutionReport":
        """
        Ustvari ExecutionReport iz že obstoječih podatkov.

        Metoda:
            - zamrzne context in budget v immutabilno obliko,
            - ne izvaja nobene logike nad rezultatom.
        """
        return ExecutionReport(
            execution_context=_freeze_mapping(execution_context),
            execution_budget=_freeze_mapping(execution_budget),
            result=result,
        )


# ---------------------------------------------------------------------------
# Interni helper
# ---------------------------------------------------------------------------


def _freeze_mapping(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Pretvori mapping v immutabilno obliko.

    Vedno vrne MappingProxyType.
    """
    return MappingProxyType(dict(mapping))

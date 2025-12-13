"""
Senti OS — Execution Layer
FAZA 49 — FILE 2/?

ExecutionResult Model
---------------------

Namen:
    - Definira standardiziran izhod ExecutionEngine-a.
    - Model je popolnoma deklarativen in immutabilen.
    - Ne vsebuje I/O, logiranja ali stranskih učinkov.

Ta model:
    - normalizira izhod iz različnih executorjev,
    - omogoča enotno obravnavo uspeha, napak in blokad,
    - služi kot pogodba (contract) za vse nadaljnje faze.

Pomembno:
    - ExecutionResult NE odloča o politiki ali validaciji.
    - ExecutionResult NE vsebuje runtime logike.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional
from types import MappingProxyType


# ---------------------------------------------------------------------------
# Execution Status
# ---------------------------------------------------------------------------


class ExecutionStatus(str, Enum):
    """
    Dovoljeni statusi izvajanja.

    Statusi so definirani zgodaj (že v FAZA 49),
    da se API kasneje ne širi nekontrolirano.
    """

    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


# ---------------------------------------------------------------------------
# Execution Result (immutabilen)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutabilen rezultat enega execution turn-a.

    Polja:
        status:
            Končni status izvajanja (ExecutionStatus).

        value:
            Rezultat uspešnega izvajanja.
            Dovoljeno samo, če je status == SUCCESS.

        error:
            Opis napake v primeru FAILED.
            String (ne exception), da ostane serializable.

        metadata:
            Dodatni podatki za audit / UI / debug.
            Vedno immutabilen Mapping.
    """

    status: ExecutionStatus
    value: Optional[Any] = None
    error: Optional[str] = None
    metadata: Mapping[str, Any] = MappingProxyType({})

    # ------------------------------------------------------------------
    # Tovarniške metode (eksplicitne, brez čarovnije)
    # ------------------------------------------------------------------

    @staticmethod
    def success(
        value: Any = None,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "ExecutionResult":
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            value=value,
            error=None,
            metadata=_freeze_metadata(metadata),
        )

    @staticmethod
    def failed(
        error: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "ExecutionResult":
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            value=None,
            error=error,
            metadata=_freeze_metadata(metadata),
        )

    @staticmethod
    def blocked(
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "ExecutionResult":
        return ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            value=None,
            error=None,
            metadata=_freeze_metadata(metadata),
        )

    @staticmethod
    def skipped(
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "ExecutionResult":
        return ExecutionResult(
            status=ExecutionStatus.SKIPPED,
            value=None,
            error=None,
            metadata=_freeze_metadata(metadata),
        )


# ---------------------------------------------------------------------------
# Interni helper
# ---------------------------------------------------------------------------


def _freeze_metadata(
    metadata: Optional[Mapping[str, Any]]
) -> Mapping[str, Any]:
    """
    Pretvori metadata v immutabilno obliko.

    Če metadata ni podana, vrne prazen MappingProxyType.
    """
    if not metadata:
        return MappingProxyType({})
    return MappingProxyType(dict(metadata))

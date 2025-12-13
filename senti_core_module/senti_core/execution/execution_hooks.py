"""
Senti OS — Execution Layer
FAZA 49 — FILE 3/?

Execution Lifecycle Hooks
-------------------------

Namen:
    - Definira lifecycle hooke za ExecutionEngine.
    - Hooki omogočajo opazovanje poteka izvajanja brez vpliva nanj.
    - V tej fazi so hooki popolnoma pasivni (brez I/O, brez logike).

Pomembno:
    - Hooki NISO namenjeni odločanju.
    - Hooki NISO namenjeni spreminjanju rezultata.
    - Hooki NISO namenjeni izvajanja kode.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .execution_result import ExecutionResult


# ---------------------------------------------------------------------------
# Lifecycle Hooks Protocol
# ---------------------------------------------------------------------------


class ExecutionLifecycleHooks(Protocol):
    """
    Protokol lifecycle hook-ov za ExecutionEngine.

    Implementacije tega protokola lahko:
        - beležijo potek (v prihodnjih fazah),
        - zbirajo metapodatke,
        - omogočajo audit in observability.

    V FAZA 49:
        - metode ne vračajo ničesar,
        - ne smejo sprožiti side-effectov,
        - ne vplivajo na execution flow.
    """

    def pre_execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
    ) -> None:
        ...

    def post_execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
        result: ExecutionResult,
    ) -> None:
        ...

    def on_error(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
        error: BaseException,
    ) -> None:
        ...


# ---------------------------------------------------------------------------
# No-op privzeta implementacija
# ---------------------------------------------------------------------------


class NoOpExecutionLifecycleHooks:
    """
    Privzeta (no-op) implementacija ExecutionLifecycleHooks.

    Namen:
        - ExecutionEngine vedno dobi veljavne hooke.
        - Ni potrebe po None-checkih.
        - Brez vpliva na potek izvajanja.

    Ta razred:
        - ne izvaja nobene logike,
        - ne dela I/O,
        - ne spreminja stanja.
    """

    def pre_execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
    ) -> None:
        return None

    def post_execute(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
        result: ExecutionResult,
    ) -> None:
        return None

    def on_error(
        self,
        execution_context: Mapping[str, Any],
        execution_budget: Mapping[str, Any],
        error: BaseException,
    ) -> None:
        return None

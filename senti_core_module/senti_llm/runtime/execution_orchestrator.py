"""
FAZA 35 — Execution Orchestrator (LLM Runtime)
Centraliziran izvrševalni mehanizem, ki obdeluje RuntimeAction objekte
in vrača strukturiran rezultat.
"""

from typing import Any, Dict

from senti_llm.runtime.action_model import RuntimeAction
from senti_llm.runtime.runtime_exceptions import OrchestratorError


class ExecutionOrchestrator:
    """Glavni runtime executor za LLM runtime plast."""

    def __init__(self) -> None:
        self.handlers: Dict[str, callable] = {
            "run.module": self._handle_run_module,
            "query.status": self._handle_query_status,
            "execute.task": self._handle_execute_task,
        }

    # ----------------------------
    # PUBLIC API
    # ----------------------------

    def execute(self, action: RuntimeAction) -> Dict[str, Any]:
        """
        Sprejme RuntimeAction, orchestratira izvajanje in vrne rezultat.

        Struktura rezultata:
        {
            "ok": True/False,
            "action_type": ...,
            "data": ... ali "error": ...
        }
        """

        if action.action_type not in self.handlers:
            raise OrchestratorError(f"Ni handlerja za action: {action.action_type}")

        handler = self.handlers[action.action_type]

        # 1) Predpriprava / logging
        self._log_action(action)

        # 2) Izvedba
        try:
            result = handler(action)
            return {
                "ok": True,
                "action_type": action.action_type,
                "data": result,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "action_type": action.action_type,
                "error": str(exc),
            }

    # ----------------------------
    # HANDLERS
    # ----------------------------

    def _handle_run_module(self, action: RuntimeAction) -> Dict[str, Any]:
        """
        Primer:
        action.payload = { "module": "trading" }
        """

        module_name = action.payload.get("module")
        if not module_name:
            raise OrchestratorError("Manjka 'module' v payload.")

        # V tej fazi samo simulacija — kasneje: dejanski module loader / manager
        return {
            "message": f"Modul '{module_name}' uspešno inicializiran.",
            "status": "started",
        }

    def _handle_query_status(self, action: RuntimeAction) -> Dict[str, Any]:
        # Minimalen health-check za LLM runtime
        return {
            "runtime": "Senti LLM Runtime",
            "status": "OK",
            "phase": "FAZA 35",
            "source": action.source,
        }

    def _handle_execute_task(self, action: RuntimeAction) -> Dict[str, Any]:
        task = action.payload.get("task_name", "unknown")
        # Kasneje: povezava na task orchestration / job queue
        return {
            "message": f"Izvedena naloga: {task}",
            "result": "success",
        }

    # ----------------------------
    # INTERNALS
    # ----------------------------

    def _log_action(self, action: RuntimeAction) -> None:
        # TODO: kasneje zapis v strukturo logov ali event bus
        print(f"[LLM Runtime] Executing: {action.action_type} from {action.source} -> payload={action.payload}")

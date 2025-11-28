"""
Cognitive Controller — Senti Core Runtime
Location: senti_core/runtime/cognitive_controller.py

Upravlja Cognitive Loop:
- upravlja naloge
- upravlja globalni kontekst
- omogoča centralizirano UI → Core → AI → Memory komunikacijo
- skrbi za event-driven orkestracijo
"""

from pathlib import Path
from datetime import datetime

from senti_core.runtime.cognitive_loop import CognitiveLoop
from senti_core.system.logger import SentiLogger


class CognitiveController:
    """
    Centralni upravljalec AI delovanja v Senti Core.
    """

    def __init__(self, logger=None):
        self.logger = logger if logger else SentiLogger()
        self.loop = CognitiveLoop(logger=self.logger)
        self.global_context = {}
        self.task_handlers = {}

        self._log("info", "CognitiveController initialized.")

    # =====================================================
    # REGISTRACIJA HANDLERJEV
    # =====================================================

    def register_task_handler(self, task_type: str, handler):
        """
        Omogoča registracijo funkcij, ki obdelujejo specifične tipe nalog.
        Primer:
            controller.register_task_handler("trading", trading_handler)
        """
        self.task_handlers[task_type] = handler
        self._log("info", f"Registered task handler for type '{task_type}'")

    # =====================================================
    # GLAVNI TASK DISPATCHER
    # =====================================================

    def dispatch_task(self, task_type: str, payload: dict) -> dict:
        """
        Preusmeri nalogo ustreznemu handlerju, če obstaja.
        Če handler ni registriran, pošlje nalogo direktno Cognitive Loop-u.
        """

        self._log("debug", f"Dispatching task: {task_type} with payload keys: {list(payload.keys())}")

        handler = self.task_handlers.get(task_type)

        if handler:
            try:
                prepared = handler(payload)
                task = prepared.get("task")
                context = prepared.get("context", {})
                return self.loop.cycle(task, context)
            except Exception as e:
                self._log("error", f"Handler for '{task_type}' failed: {str(e)}")
                return {"status": "error", "error": str(e)}

        # fallback: directly execute
        if "task" not in payload:
            return {"status": "error", "error": "Payload must contain 'task'."}

        return self.loop.cycle(payload["task"], payload.get("context", {}))

    # =====================================================
    # ROČNO ZAGON CIKLA
    # =====================================================

    def run_cycle(self, task: str, context: dict = None) -> dict:
        """
        Ročno zažene miselni cikel z dodatnim združevanjem globalnega konteksta.
        """
        ctx = context if context else {}
        merged_context = {**self.global_context, **ctx}

        self._log("info", f"Manual cognitive cycle started for task '{task}'")

        return self.loop.cycle(task, merged_context)

    # =====================================================
    # GLOBALNI KONTEXT
    # =====================================================

    def update_context(self, key: str, value):
        """
        Globalni kontekst, ki ga Cognitive Loop uporablja ob vsaki nalogi.
        """
        self.global_context[key] = value
        self._log("debug", f"Context updated: {key} = {value}")

    def get_context(self) -> dict:
        return dict(self.global_context)

    # =====================================================
    # EVENT EMITTER (PRIPRAVLJENO ZA Senti OS)
    # =====================================================

    def emit_event(self, event_type: str, payload: dict):
        """
        Pripravljeno za prihodnji EventBus.
        Trenutno samo log.
        """
        self._log("info", f"[EVENT] {event_type}: {payload}")

    # =====================================================
    # LOGGING
    # =====================================================

    def _log(self, level: str, message: str):
        if hasattr(self.logger, "log"):
            self.logger.log(level, message)
        else:
            print(f"[{level.upper()}] {message}")

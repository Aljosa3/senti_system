"""
Cognitive Loop — Senti Core Runtime
Location: senti_core/runtime/cognitive_loop.py

Glavni “možganski krog” Senti Systema.
Orkestrira:
- Senti Reasoning (analiza, koraki, odločitev)
- Senti Validator (preverjanje vsake faze)
- Senti Memory (varno shranjevanje znanja)

Ta modul:
✔ ne piše v modules/
✔ ne posega v senti_os/
✔ deluje znotraj pravil Project Rules
✔ uporablja absolutne importe
"""

from pathlib import Path
from datetime import datetime

from senti_validator.senti_validator import SentiValidator
from modules.processing.senti_reasoning.senti_reasoning import SentiReasoning
from modules.processing.senti_memory.senti_memory import SentiMemory


class CognitiveLoop:
    """
    Cognitive Loop predstavlja varno zaporedje:
        1. analiza
        2. plan korakov
        3. odločitev
        4. validacija vsake faze
        5. shranjevanje v spomin
    """

    def __init__(self, logger):
        self.reasoning = SentiReasoning()
        self.validator = SentiValidator()
        self.memory = SentiMemory()
        self.logger = logger

    # =====================================================
    # GLAVNI CIKEL
    # =====================================================

    def cycle(self, task: str, context: dict) -> dict:
        """
        Izvede en miselni cikel nad nalogo.
        """

        self._log("info", f"=== Cognitive Loop START: {task} ===")

        # 1) ANALYSIS
        analysis = self._safe_call(self.reasoning._analyze, task, context)
        if not self._validate_stage("analysis", analysis):
            return self._fail("analysis_failed", analysis)

        # 2) PLAN
        steps = self._safe_call(self.reasoning._plan, task, context)
        if not self._validate_stage("plan", steps):
            return self._fail("plan_failed", steps)

        # 3) DECISION
        decision = self._safe_call(self.reasoning._decide, task, analysis, steps)
        if not self._validate_stage("decision", decision):
            return self._fail("decision_failed", decision)

        # 4) MEMORY STORE (varno)
        memory_result = self._safe_call(
            self.memory.store,
            {
                "analysis": analysis,
                "steps": steps,
                "decision": decision
            },
            "system",
            {"module": "cognitive_loop"}
        )

        self._log("info", "Cognitive Loop memory store completed.")

        return {
            "status": "ok",
            "analysis": analysis,
            "steps": steps,
            "decision": decision,
            "memory": memory_result
        }

    # =====================================================
    # VALIDACIJA
    # =====================================================

    def _validate_stage(self, stage: str, output: dict) -> bool:
        """
        Preveri vsako fazo reasoning cikla.
        """
        self._log("debug", f"Validating stage: {stage}")

        validation = self.validator.validate(
            output,
            {"module": "cognitive_loop", "stage": stage}
        )

        if validation["status"] == "error":
            self._log("error", f"Validation failed at stage {stage}: {validation['errors']}")
            return False

        if validation["warnings"]:
            self._log("warning", f"Stage {stage} warnings: {validation['warnings']}")

        return True

    # =====================================================
    # VARNI KLICI
    # =====================================================

    def _safe_call(self, func, *args, **kwargs):
        """
        Izvede funkcijo z varnostno zaščito (try/except).
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._log("error", f"Error in safe_call: {str(e)}")
            return {"error": str(e)}

    # =====================================================
    # FALLBACK
    # =====================================================

    def _fail(self, stage: str, data):
        """
        Vrne varno poročilo v primeru napake.
        """
        return {
            "status": "error",
            "stage": stage,
            "data": data
        }

    # =====================================================
    # LOGGING
    # =====================================================

    def _log(self, level: str, message: str):
        """
        Pošlje log v Senti Core logger.
        """
        if hasattr(self.logger, "log"):
            self.logger.log(level, message)
        else:
            print(f"[{level.upper()}] {message}")

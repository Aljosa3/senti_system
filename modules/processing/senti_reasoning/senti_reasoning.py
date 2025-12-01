"""
Senti Reasoning Module
Location: modules/processing/senti_reasoning/senti_reasoning.py

A structured reasoning engine that:
- analyzes tasks
- generates multi-step plans
- evaluates possible solutions
- produces controlled, safe, auditable reasoning outputs
"""

from senti_core.utils.validator import Validator
from modules.senti_validator.senti_validator import SentiValidator  # from module system
import json


class SentiReasoning:
    """
    Senti Reasoning — structured AI planning engine.
    Produces deterministic, validator-friendly reasoning objects.
    """

    def __init__(self):
        self.name = "senti_reasoning"
        self.validator = SentiValidator()

    # =====================================================
    # MAIN ENTRYPOINT
    # =====================================================
    def reason(self, task: str, context: dict, metadata: dict) -> dict:
        """
        Performs full reasoning cycle:
        - analyze problem
        - plan steps
        - evaluate and choose decision
        - validate result (via Senti Validator)
        """

        analysis = self._analyze(task, context)
        steps = self._plan(task, context)
        decision = self._decide(task, analysis, steps)

        output = {
            "analysis": analysis,
            "steps": steps,
            "decision": decision["result"],
            "confidence": decision["confidence"]
        }

        # Validate output using Senti Validator
        validation = self.validator.validate(output, metadata)

        if validation["status"] == "error":
            return {
                "status": "error",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "validated_output": None
            }

        return {
            "status": validation["status"],
            "validated_output": output,
            "warnings": validation["warnings"],
            "errors": []
        }

    # =====================================================
    # REASONING STAGES
    # =====================================================

    def _analyze(self, task: str, context: dict) -> str:
        """
        High-level structured analysis.
        No chain-of-thought, only safe summarization.
        """
        task_summary = f"Razčlenitev naloge: '{task}' z upoštevanjem trenutnega konteksta."
        context_part = f"Vključeni parametri konteksta: {list(context.keys())}"
        return f"{task_summary} {context_part}"

    def _plan(self, task: str, context: dict) -> list:
        """
        Breaks the task into steps.
        Steps must be deterministic, checkable and validator-friendly.
        """
        return [
            {
                "step": 1,
                "action": "Preveri vhodne podatke",
                "details": "Preveri obliko, nujne parametre in format naloge."
            },
            {
                "step": 2,
                "action": "Ustvari analizo problema",
                "details": "Formalno oceni cilje naloge glede na kontekst."
            },
            {
                "step": 3,
                "action": "Generiraj odločitev",
                "details": "Izberi najboljšo možno rešitev, skladno z varnostjo."
            }
        ]

    def _decide(self, task: str, analysis: str, steps: list) -> dict:
        """
        Produce a safe and structured decision.
        """
        decision_text = f"Modul predlaga rešitev naloge '{task}' na podlagi analiziranih podatkov."
        confidence_score = 0.90

        return {
            "result": decision_text,
            "confidence": confidence_score
        }

    # =====================================================
    # REQUIRED SYSTEM METHODS
    # =====================================================

    def load(self):
        return True

    def start(self):
        return True

    def stop(self):
        return True

    def metadata(self):
        return {
            "name": "senti_reasoning",
            "type": "processing",
            "version": "1.0.0"
        }

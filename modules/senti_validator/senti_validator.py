"""
Senti Validator Module
Location: modules/processing/senti_validator/senti_validator.py

This module performs multi-layer validation of AI outputs from other Senti modules.
It checks logical consistency, rule compliance, metadata structure, 
forbidden patterns, and semantic integrity.
"""

from senti_core.utils.validator import Validator
from senti_core.runtime.integrity_checker import IntegrityChecker
import json


class SentiValidator:
    """
    Critical AI validation engine.
    Used by Senti Core to confirm or reject outputs from other modules.
    """

    def __init__(self):
        self.name = "senti_validator"

    # ===================================================
    # MAIN ENTRYPOINT
    # ===================================================
    def validate(self, raw_output: dict, metadata: dict) -> dict:
        """
        Entry point called by Core.
        Returns:
            {
              "status": "pass" | "warning" | "error",
              "validated_output": <dict or None>,
              "warnings": [...],
              "errors": [...]
            }
        """
        errors = []
        warnings = []

        # 1) Validate metadata exists
        meta_result = self._validate_metadata(metadata)
        errors.extend(meta_result["errors"])
        warnings.extend(meta_result["warnings"])

        # 2) Check logical structural consistency
        logical_result = self._validate_logical_consistency(raw_output)
        errors.extend(logical_result["errors"])
        warnings.extend(logical_result["warnings"])

        # 3) Rule compliance check (PROJECT_RULES, AI_RULES, Module Schema)
        rules_result = self._validate_rules(raw_output)
        errors.extend(rules_result["errors"])
        warnings.extend(rules_result["warnings"])

        # 4) Semantic safety (forbidden patterns, OS bypass, harmful intent)
        semantic_result = self._validate_semantic(raw_output)
        errors.extend(semantic_result["errors"])
        warnings.extend(semantic_result["warnings"])

        # FINAL DECISION
        if len(errors) > 0:
            return {
                "status": "error",
                "validated_output": None,
                "warnings": warnings,
                "errors": errors
            }

        if len(warnings) > 0:
            return {
                "status": "warning",
                "validated_output": raw_output,
                "warnings": warnings,
                "errors": []
            }

        return {
            "status": "pass",
            "validated_output": raw_output,
            "warnings": [],
            "errors": []
        }

    # ===================================================
    # VALIDATION STAGES
    # ===================================================

    def _validate_metadata(self, metadata: dict) -> dict:
        errors = []
        warnings = []

        if not isinstance(metadata, dict):
            errors.append("Metadata must be a dictionary.")
            return {"errors": errors, "warnings": warnings}

        required = ["module", "timestamp"]

        for key in required:
            if key not in metadata:
                errors.append(f"Missing required metadata key: {key}")

        return {"errors": errors, "warnings": warnings}

    def _validate_logical_consistency(self, output: dict) -> dict:
        errors = []
        warnings = []

        if not isinstance(output, dict):
            errors.append("Module output must be a dictionary.")
            return {"errors": errors, "warnings": warnings}

        # JSON serialize check (detect circular references)
        try:
            json.dumps(output)
        except Exception as e:
            errors.append(f"Output is not JSON-serializable: {e}")

        return {"errors": errors, "warnings": warnings}

    def _validate_rules(self, output: dict) -> dict:
        errors = []
        warnings = []

        # Use Validator to validate against module schema structure if required
        try:
            Validator.validate_runtime_output(output)
        except Exception as e:
            errors.append(f"Rule compliance error: {e}")

        return {"errors": errors, "warnings": warnings}

    def _validate_semantic(self, output: dict) -> dict:
        errors = []
        warnings = []

        text = json.dumps(output)

        forbidden = [
            "os.system(",
            "subprocess.",
            "../",
            "eval(",
            "exec("
        ]

        for f in forbidden:
            if f in text:
                errors.append(f"Forbidden pattern detected in output: {f}")

        return {"errors": errors, "warnings": warnings}


# ===================================================
# MODULE EXPORT
# ===================================================
def load():
    return SentiValidator()


def start():
    # Validator requires no background task
    return True


def stop():
    return True


def metadata():
    return {
        "name": "senti_validator",
        "type": "processing",
        "version": "1.0.0"
    }

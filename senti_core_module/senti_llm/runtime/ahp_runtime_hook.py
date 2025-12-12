"""
FAZA 46 — AHP Runtime Hook
FILE 8/8: ahp_runtime_hook.py

Integration layer for Anti-Hallucination Protocol (AHP).
Connects AHPValidator to runtime pipeline.
No new logic, no intelligence, only orchestration.

Purpose:
- Connect AHPValidator (FILE 7/8) to runtime pipeline
- Provide single, deterministic entry point
- Allow runtime to call AHP without knowing its internals

Rules:
- No I/O
- No print/log
- No try/except (except where explicitly required)
- No state
- No new rules
- No validations that aren't AHP
- Only call AHP validator
"""

from senti_core_module.senti_llm.runtime.ahp_validator import AHPValidator


class AHPRuntimeHook:
    """Integration hook for AHP in runtime pipeline."""

    def __init__(self, validator: AHPValidator):
        """
        Initialize runtime hook with AHP validator.

        Args:
            validator (AHPValidator): AHP validator instance.
        """
        self.validator = validator

    def audit(self, output: str) -> None:
        """
        Audit output using AHP validator.

        Args:
            output (str): Generated output to audit.

        Raises:
            TypeError: If output is not a string.
            AHPError: If any AHP audit fails.
        """
        if not isinstance(output, str):
            raise TypeError(f"Output must be str, got: {type(output)}")

        self.validator.run_post_generation_audit(output)

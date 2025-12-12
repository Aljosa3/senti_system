"""
FAZA 46 — AHP Validator
FILE 7/8: ahp_validator.py

Core audit engine for Anti-Hallucination Protocol (AHP).
Post-generation audit over output string.
No fixing, no generation, no I/O.
Only analysis + exceptions.
"""

from senti_core_module.senti_llm.runtime.ahp_governance import (
    FORBIDDEN_SYSTEM_COMMANDS,
    FORBIDDEN_IMPORTS,
    FORBIDDEN_PYTHON_CALLS,
)

from senti_core_module.senti_llm.runtime.ahp_exceptions import (
    AHPStructureError,
    AHPForbiddenOperationError,
    AHPForbiddenImportError,
    AHPForbiddenCallError,
    AHPLogicalInconsistencyError,
    AHPFactValidationError,
)


class AHPValidator:
    """Core audit engine for Anti-Hallucination Protocol."""

    def __init__(self):
        """Initialize AHP validator."""
        pass

    def audit_structure(self, output: str) -> None:
        """
        Audit output structure for violations.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPStructureError: If output structure is invalid.
        """
        if not isinstance(output, str):
            raise AHPStructureError(f"Output must be str, got: {type(output)}")

        if not output.strip():
            raise AHPStructureError("Output cannot be empty")

        lines = output.split("\n")
        if len(lines) > 10000:
            raise AHPStructureError(f"Output exceeds maximum lines: {len(lines)}")

    def audit_forbidden_operations(self, output: str) -> None:
        """
        Audit output for forbidden system operations.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPForbiddenOperationError: If forbidden operations detected.
        """
        for forbidden_cmd in FORBIDDEN_SYSTEM_COMMANDS:
            if forbidden_cmd in output:
                raise AHPForbiddenOperationError(
                    f"Forbidden system command detected: {forbidden_cmd}"
                )

    def audit_forbidden_imports(self, output: str) -> None:
        """
        Audit output for forbidden imports.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPForbiddenImportError: If forbidden imports detected.
        """
        for forbidden_import in FORBIDDEN_IMPORTS:
            if f"import {forbidden_import}" in output or f"from {forbidden_import}" in output:
                raise AHPForbiddenImportError(
                    f"Forbidden import detected: {forbidden_import}"
                )

    def audit_forbidden_calls(self, output: str) -> None:
        """
        Audit output for forbidden function calls.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPForbiddenCallError: If forbidden calls detected.
        """
        for forbidden_call in FORBIDDEN_PYTHON_CALLS:
            if f"{forbidden_call}(" in output:
                raise AHPForbiddenCallError(
                    f"Forbidden function call detected: {forbidden_call}()"
                )

    def audit_logical_consistency(self, output: str) -> None:
        """
        Audit output for logical contradictions.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPLogicalInconsistencyError: If logical contradictions detected.
        """
        lines = output.split("\n")

        for i, line in enumerate(lines):
            if "#" in line:
                comment = line.split("#", 1)[1].strip().lower()
                code = line.split("#", 1)[0].strip().lower()

                if "return true" in comment and "return false" in code:
                    raise AHPLogicalInconsistencyError(
                        f"Contradiction at line {i+1}: comment says 'return true', code returns false"
                    )

                if "return false" in comment and "return true" in code:
                    raise AHPLogicalInconsistencyError(
                        f"Contradiction at line {i+1}: comment says 'return false', code returns true"
                    )

    def audit_fact_validity(self, output: str) -> None:
        """
        Audit output for unverifiable or false claims.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPFactValidationError: If false claims detected.
        """
        suspicious_claims = [
            "guaranteed to work",
            "always correct",
            "never fails",
            "100% accurate",
            "perfectly safe",
        ]

        lines = output.split("\n")

        for i, line in enumerate(lines):
            lower_line = line.lower()
            for claim in suspicious_claims:
                if claim in lower_line:
                    raise AHPFactValidationError(
                        f"Unverifiable absolute claim at line {i+1}: '{claim}'"
                    )

    def run_post_generation_audit(self, output: str) -> None:
        """
        Run all AHP audits in sequence.

        Args:
            output (str): Generated output to audit.

        Raises:
            AHPError: If any audit fails.
        """
        self.audit_structure(output)
        self.audit_forbidden_operations(output)
        self.audit_forbidden_imports(output)
        self.audit_forbidden_calls(output)
        self.audit_logical_consistency(output)
        self.audit_fact_validity(output)

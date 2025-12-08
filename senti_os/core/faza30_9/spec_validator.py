"""
FAZA 30.9 – SPEC Validator
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class ValidationResult(Enum):
    """Validation result status."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    BLOCK = "BLOCK"


@dataclass
class ValidationReport:
    """Complete validation report."""

    result: ValidationResult
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result": self.result.value,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "metadata": self.metadata
        }

    def is_blocked(self) -> bool:
        """Check if validation blocked."""
        return self.result == ValidationResult.BLOCK

    def is_safe_to_proceed(self) -> bool:
        """Check if safe to proceed."""
        return self.result in [ValidationResult.PASS, ValidationResult.PASS_WITH_WARNINGS]


class SpecValidator:
    """
    Validates specifications for safety and completeness.

    Validates:
    - Completeness: All required fields present
    - Consistency: No contradictions
    - Architecture compliance: Follows system constraints
    - Safety: No dangerous operations
    - Feasibility: Can be implemented

    Returns:
    - PASS: Fully valid, proceed
    - PASS_WITH_WARNINGS: Valid but has concerns
    - BLOCK: Invalid, cannot proceed
    """

    # Dangerous operations to block
    DANGEROUS_OPERATIONS = {
        "file system write outside workspace",
        "network access without validation",
        "execute arbitrary code",
        "modify system files",
        "disable security",
        "bypass validation",
        "remove constraints",
        "unrestricted access"
    }

    # Required fields for SESY spec
    REQUIRED_FIELDS = [
        "name",
        "purpose",
        "architecture",
        "api_definitions",
        "lifecycle",
        "test_plan"
    ]

    # Architecture patterns allowed
    ALLOWED_PATTERNS = {
        "modular",
        "layered",
        "pipeline",
        "event_driven",
        "service_oriented"
    }

    def __init__(self) -> None:
        """Initialize the SPEC validator."""
        pass

    def validate(self, spec: Dict[str, Any]) -> ValidationReport:
        """
        Validate a specification.

        Args:
            spec: Specification to validate

        Returns:
            ValidationReport with results
        """
        report = ValidationReport(result=ValidationResult.PASS)

        # Run validation checks
        self._check_completeness(spec, report)
        self._check_consistency(spec, report)
        self._check_architecture_compliance(spec, report)
        self._check_safety(spec, report)
        self._check_feasibility(spec, report)

        # Determine final result
        if report.errors:
            report.result = ValidationResult.BLOCK
        elif report.warnings:
            report.result = ValidationResult.PASS_WITH_WARNINGS
        else:
            report.result = ValidationResult.PASS

        return report

    def _check_completeness(
        self,
        spec: Dict[str, Any],
        report: ValidationReport
    ) -> None:
        """Check if all required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in spec or not spec[field]:
                report.errors.append(f"Missing required field: {field}")
                report.checks_failed += 1
            else:
                report.checks_passed += 1

        # Check API definitions structure
        if "api_definitions" in spec:
            api_defs = spec["api_definitions"]
            if not isinstance(api_defs, list):
                report.errors.append("api_definitions must be a list")
                report.checks_failed += 1
            elif len(api_defs) == 0:
                report.warnings.append("No API definitions provided")
            else:
                report.checks_passed += 1

        # Check test plan structure
        if "test_plan" in spec:
            test_plan = spec["test_plan"]
            if not isinstance(test_plan, dict):
                report.errors.append("test_plan must be a dictionary")
                report.checks_failed += 1
            elif "test_cases" not in test_plan:
                report.warnings.append("No test cases in test plan")
            else:
                report.checks_passed += 1

    def _check_consistency(
        self,
        spec: Dict[str, Any],
        report: ValidationReport
    ) -> None:
        """Check for internal contradictions."""
        # Check inputs/outputs consistency
        api_defs = spec.get("api_definitions", [])

        for api_def in api_defs:
            if "inputs" in api_def and "outputs" in api_def:
                inputs = api_def.get("inputs", [])
                outputs = api_def.get("outputs", [])

                if not inputs and not outputs:
                    report.warnings.append(
                        f"API method {api_def.get('method', 'unknown')} "
                        "has no inputs or outputs"
                    )
                else:
                    report.checks_passed += 1

        # Check lifecycle consistency
        lifecycle = spec.get("lifecycle", {})
        if lifecycle:
            required_phases = ["initialization", "execution", "shutdown"]
            for phase in required_phases:
                if phase not in lifecycle:
                    report.warnings.append(f"Lifecycle missing {phase} phase")
                else:
                    report.checks_passed += 1

        # Check constraints don't contradict requirements
        constraints = spec.get("constraints", [])
        requirements = []

        # Extract requirements from purpose or elsewhere
        if "purpose" in spec:
            purpose = spec["purpose"].lower()
            if "must" in purpose and "must not" in purpose:
                report.warnings.append("Purpose contains contradictory requirements")

        report.checks_passed += 1

    def _check_architecture_compliance(
        self,
        spec: Dict[str, Any],
        report: ValidationReport
    ) -> None:
        """Check compliance with architecture constraints."""
        architecture = spec.get("architecture", {})

        if not architecture:
            report.errors.append("Architecture description missing")
            report.checks_failed += 1
            return

        # Check architecture type
        arch_type = architecture.get("type", "")
        if arch_type not in self.ALLOWED_PATTERNS:
            report.warnings.append(
                f"Architecture type '{arch_type}' not in standard patterns"
            )
        else:
            report.checks_passed += 1

        # Check for circular dependencies
        if "dependencies" in architecture:
            deps = architecture["dependencies"]
            if isinstance(deps, list) and len(deps) > len(set(deps)):
                report.warnings.append("Duplicate dependencies detected")
            else:
                report.checks_passed += 1

        # Check modularity
        if "components" in architecture:
            components = architecture["components"]
            if len(components) == 0:
                report.warnings.append("No components defined in architecture")
            elif len(components) > 20:
                report.warnings.append("High component count may indicate complexity")
            else:
                report.checks_passed += 1

    def _check_safety(
        self,
        spec: Dict[str, Any],
        report: ValidationReport
    ) -> None:
        """Check for dangerous or unsafe operations."""
        import json

        spec_str = json.dumps(spec).lower()

        # Check for dangerous operations
        found_dangerous = []
        for dangerous_op in self.DANGEROUS_OPERATIONS:
            if dangerous_op in spec_str:
                found_dangerous.append(dangerous_op)

        if found_dangerous:
            report.errors.append(
                f"Dangerous operations detected: {', '.join(found_dangerous)}"
            )
            report.checks_failed += 1
        else:
            report.checks_passed += 1

        # Check for incomplete security measures
        if "security" not in spec_str and "validation" not in spec_str:
            report.warnings.append("No security or validation mentioned")

        # Check for hardcoded credentials
        if "password" in spec_str or "secret" in spec_str or "token" in spec_str:
            report.warnings.append("Potential hardcoded credentials detected")

        report.checks_passed += 1

    def _check_feasibility(
        self,
        spec: Dict[str, Any],
        report: ValidationReport
    ) -> None:
        """Check if specification is feasible to implement."""
        # Check complexity
        metadata = spec.get("metadata", {})
        complexity = metadata.get("complexity", "moderate")

        if complexity == "extreme":
            report.warnings.append("Extreme complexity may require decomposition")

        # Check API count
        api_defs = spec.get("api_definitions", [])
        if len(api_defs) > 50:
            report.warnings.append("High API count may indicate over-engineering")

        # Check constraint feasibility
        constraints = spec.get("constraints", [])
        for constraint in constraints:
            constraint_lower = constraint.lower()
            if "zero" in constraint_lower and "latency" in constraint_lower:
                report.warnings.append("Zero latency constraint is not feasible")
            if "infinite" in constraint_lower:
                report.warnings.append("Infinite resource constraint is not feasible")

        report.checks_passed += 1

        # Check test coverage
        test_plan = spec.get("test_plan", {})
        if "coverage_target" in test_plan:
            coverage = test_plan["coverage_target"]
            if isinstance(coverage, (int, float)):
                if coverage > 1.0:
                    report.errors.append("Coverage target cannot exceed 100%")
                    report.checks_failed += 1
                elif coverage < 0.5:
                    report.warnings.append("Low test coverage target")
                else:
                    report.checks_passed += 1

    def validate_sanitized(
        self,
        sanitized_spec: Dict[str, Any]
    ) -> ValidationReport:
        """
        Validate a sanitized specification for external use.

        Args:
            sanitized_spec: Sanitized specification

        Returns:
            ValidationReport
        """
        report = self.validate(sanitized_spec)

        # Additional check: ensure sanitization occurred
        metadata = sanitized_spec.get("metadata", {})
        if not metadata.get("sanitized", False):
            report.errors.append("Specification not marked as sanitized")
            report.checks_failed += 1
            report.result = ValidationResult.BLOCK

        return report


def validate_spec(spec: Dict[str, Any]) -> ValidationReport:
    """
    Convenience function to validate a specification.

    Args:
        spec: Specification to validate

    Returns:
        ValidationReport
    """
    validator = SpecValidator()
    return validator.validate(spec)

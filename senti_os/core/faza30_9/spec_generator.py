"""
FAZA 30.9 – SPEC Generator
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class SESYSpec:
    """
    SESY (Senti Specification) format specification.

    A complete, structured specification for component development.
    """

    name: str
    purpose: str
    architecture: Dict[str, Any]
    api_definitions: List[Dict[str, Any]]
    lifecycle: Dict[str, Any]
    integration_points: List[Dict[str, Any]]
    constraints: List[str]
    test_plan: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "purpose": self.purpose,
            "architecture": self.architecture,
            "api_definitions": self.api_definitions,
            "lifecycle": self.lifecycle,
            "integration_points": self.integration_points,
            "constraints": self.constraints,
            "test_plan": self.test_plan,
            "metadata": self.metadata,
            "format": "SESY",
            "version": "1.0"
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class SpecGenerator:
    """
    Generates SESY-format specifications from extracted data.

    Takes extracted specification data and produces a complete,
    structured SESY specification suitable for validation and
    code generation.
    """

    def __init__(self) -> None:
        """Initialize the SPEC generator."""
        pass

    def generate(
        self,
        extracted_spec: Dict[str, Any],
        component_name: Optional[str] = None
    ) -> SESYSpec:
        """
        Generate SESY specification from extracted data.

        Args:
            extracted_spec: Dictionary from ExtractedSpec
            component_name: Optional override for component name

        Returns:
            Complete SESYSpec
        """
        # Determine component name
        name = self._determine_name(extracted_spec, component_name)

        # Generate purpose statement
        purpose = self._generate_purpose(extracted_spec)

        # Generate architecture description
        architecture = self._generate_architecture(extracted_spec)

        # Generate API definitions
        api_definitions = self._generate_api_definitions(extracted_spec)

        # Generate lifecycle specification
        lifecycle = self._generate_lifecycle(extracted_spec)

        # Generate integration points
        integration_points = self._generate_integration_points(extracted_spec)

        # Extract constraints
        constraints = extracted_spec.get("constraints", [])

        # Generate test plan
        test_plan = self._generate_test_plan(extracted_spec)

        # Generate metadata
        metadata = self._generate_metadata(extracted_spec)

        return SESYSpec(
            name=name,
            purpose=purpose,
            architecture=architecture,
            api_definitions=api_definitions,
            lifecycle=lifecycle,
            integration_points=integration_points,
            constraints=constraints,
            test_plan=test_plan,
            metadata=metadata
        )

    def _determine_name(
        self,
        extracted_spec: Dict[str, Any],
        override: Optional[str]
    ) -> str:
        """Determine component name."""
        if override:
            return override

        metadata = extracted_spec.get("metadata", {})
        if "suggested_name" in metadata:
            return metadata["suggested_name"]

        # Generate generic name
        return f"component_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_purpose(self, extracted_spec: Dict[str, Any]) -> str:
        """Generate purpose statement."""
        goals = extracted_spec.get("goals", [])
        requirements = extracted_spec.get("requirements", [])

        if goals:
            return f"Purpose: {goals[0]}"
        elif requirements:
            return f"Purpose: {requirements[0]}"
        else:
            return "Purpose: Component for system functionality"

    def _generate_architecture(self, extracted_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture description."""
        metadata = extracted_spec.get("metadata", {})
        complexity = metadata.get("complexity", "moderate")

        architecture = {
            "type": "modular",
            "complexity": complexity,
            "components": [],
            "patterns": ["single_responsibility", "dependency_injection"]
        }

        # Infer components from requirements
        requirements = extracted_spec.get("requirements", [])
        if requirements:
            architecture["components"] = [
                {"name": "core", "responsibility": "primary_logic"},
                {"name": "interface", "responsibility": "external_api"}
            ]

        return architecture

    def _generate_api_definitions(
        self,
        extracted_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate API definitions."""
        api_defs = []

        inputs = extracted_spec.get("inputs", [])
        outputs = extracted_spec.get("outputs", [])

        # Generate primary method
        api_defs.append({
            "method": "execute",
            "description": "Primary execution method",
            "inputs": [{"name": "data", "type": "Any", "description": inp}
                      for inp in inputs[:3]],
            "outputs": [{"name": "result", "type": "Any", "description": out}
                       for out in outputs[:3]],
            "errors": ["ValidationError", "ProcessingError"]
        })

        return api_defs

    def _generate_lifecycle(self, extracted_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lifecycle specification."""
        return {
            "initialization": {
                "steps": ["validate_config", "setup_resources"],
                "requirements": ["configuration_available"]
            },
            "execution": {
                "steps": ["validate_input", "process", "return_output"],
                "behavior": "deterministic"
            },
            "shutdown": {
                "steps": ["cleanup_resources", "finalize"],
                "requirements": ["graceful_termination"]
            }
        }

    def _generate_integration_points(
        self,
        extracted_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate integration points."""
        integration_points = []

        # Extract from integration_points field
        for integration in extracted_spec.get("integration_points", []):
            integration_points.append({
                "description": integration,
                "type": "external",
                "protocol": "api"
            })

        return integration_points

    def _generate_test_plan(self, extracted_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test plan."""
        requirements = extracted_spec.get("requirements", [])

        test_cases = []
        for idx, req in enumerate(requirements[:5]):
            test_cases.append({
                "id": f"TC{idx+1:03d}",
                "description": f"Test: {req[:50]}",
                "type": "functional"
            })

        return {
            "test_cases": test_cases,
            "coverage_target": 0.9,
            "frameworks": ["unittest"],
            "test_types": ["unit", "integration"]
        }

    def _generate_metadata(self, extracted_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata."""
        original_metadata = extracted_spec.get("metadata", {})

        return {
            **original_metadata,
            "generated_at": datetime.now().isoformat(),
            "generator": "FAZA_30_9",
            "format_version": "1.0"
        }

    def validate_spec(self, spec: SESYSpec) -> tuple[bool, List[str]]:
        """
        Validate generated SESY specification.

        Args:
            spec: Generated SESY specification

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Required field validation
        if not spec.name:
            errors.append("Missing component name")

        if not spec.purpose:
            errors.append("Missing purpose statement")

        if not spec.api_definitions:
            errors.append("No API definitions provided")

        if not spec.architecture:
            errors.append("Missing architecture description")

        if not spec.lifecycle:
            errors.append("Missing lifecycle specification")

        if not spec.test_plan:
            errors.append("Missing test plan")

        is_valid = len(errors) == 0

        return is_valid, errors

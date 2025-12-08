"""
FAZA 30.9 – Plan Builder
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class BuildPlan:
    """Complete build plan for code generation."""

    compile_plan: Dict[str, Any]
    build_context: Dict[str, Any]
    safety_constraints: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "compile_plan": self.compile_plan,
            "build_context": self.build_context,
            "safety_constraints": self.safety_constraints,
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_files(self, output_dir: str) -> List[str]:
        """
        Save plan components to separate JSON files.

        Args:
            output_dir: Directory to save files

        Returns:
            List of created file paths
        """
        import os

        files = []

        # Save compile plan
        compile_plan_path = os.path.join(output_dir, "compile_plan.json")
        with open(compile_plan_path, "w") as f:
            json.dump(self.compile_plan, f, indent=2)
        files.append(compile_plan_path)

        # Save build context
        build_context_path = os.path.join(output_dir, "build_context.json")
        with open(build_context_path, "w") as f:
            json.dump(self.build_context, f, indent=2)
        files.append(build_context_path)

        # Save safety constraints
        safety_path = os.path.join(output_dir, "safety_constraints.json")
        with open(safety_path, "w") as f:
            json.dump(self.safety_constraints, f, indent=2)
        files.append(safety_path)

        return files


class PlanBuilder:
    """
    Builds compilation and build plans from specifications.

    Generates structured plans used by subsequent build phases:
    - compile_plan.json: Compilation steps and dependencies
    - build_context.json: Context for code generation
    - safety_constraints.json: Safety rules and restrictions
    """

    def __init__(self) -> None:
        """Initialize the plan builder."""
        pass

    def build(
        self,
        spec: Dict[str, Any],
        sanitized_spec: Dict[str, Any]
    ) -> BuildPlan:
        """
        Build complete build plan from specifications.

        Args:
            spec: Original specification
            sanitized_spec: Sanitized specification

        Returns:
            Complete BuildPlan
        """
        compile_plan = self._build_compile_plan(spec)
        build_context = self._build_build_context(sanitized_spec)
        safety_constraints = self._build_safety_constraints(spec)
        metadata = self._build_metadata(spec)

        return BuildPlan(
            compile_plan=compile_plan,
            build_context=build_context,
            safety_constraints=safety_constraints,
            metadata=metadata
        )

    def _build_compile_plan(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build compilation plan."""
        name = spec.get("name", "component")
        architecture = spec.get("architecture", {})
        api_definitions = spec.get("api_definitions", [])

        compile_plan = {
            "component_name": name,
            "compilation_steps": self._generate_compilation_steps(spec),
            "dependencies": self._extract_dependencies(spec),
            "build_order": self._determine_build_order(architecture),
            "output_artifacts": self._determine_artifacts(spec),
            "validation_steps": self._generate_validation_steps(spec)
        }

        return compile_plan

    def _generate_compilation_steps(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ordered compilation steps."""
        steps = []

        # Step 1: Setup
        steps.append({
            "step": 1,
            "phase": "setup",
            "action": "validate_specification",
            "description": "Validate input specification",
            "required": True
        })

        # Step 2: Code generation
        steps.append({
            "step": 2,
            "phase": "generation",
            "action": "generate_code",
            "description": "Generate component code from specification",
            "required": True
        })

        # Step 3: Validation
        steps.append({
            "step": 3,
            "phase": "validation",
            "action": "validate_code",
            "description": "Validate generated code for safety and correctness",
            "required": True
        })

        # Step 4: Testing
        steps.append({
            "step": 4,
            "phase": "testing",
            "action": "run_tests",
            "description": "Execute test suite",
            "required": True
        })

        # Step 5: Integration
        steps.append({
            "step": 5,
            "phase": "integration",
            "action": "integrate_component",
            "description": "Integrate with existing system",
            "required": False
        })

        return steps

    def _extract_dependencies(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract component dependencies."""
        dependencies = []

        # Extract from integration points
        integration_points = spec.get("integration_points", [])
        for integration in integration_points:
            dependencies.append({
                "type": "integration",
                "description": integration.get("description", ""),
                "required": integration.get("type") != "optional"
            })

        # Python standard library
        dependencies.append({
            "type": "stdlib",
            "name": "python",
            "version": "3.12+",
            "required": True
        })

        return dependencies

    def _determine_build_order(self, architecture: Dict[str, Any]) -> List[str]:
        """Determine build order for components."""
        build_order = []

        components = architecture.get("components", [])
        if not components:
            build_order = ["main"]
        else:
            # Build core components first
            for comp in components:
                name = comp.get("name", "")
                if "core" in name.lower() or "base" in name.lower():
                    build_order.append(name)

            # Then interface components
            for comp in components:
                name = comp.get("name", "")
                if name not in build_order:
                    build_order.append(name)

        return build_order

    def _determine_artifacts(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine output artifacts."""
        artifacts = []

        name = spec.get("name", "component")

        # Main module
        artifacts.append({
            "type": "module",
            "name": f"{name}.py",
            "description": "Primary module file"
        })

        # Test file
        artifacts.append({
            "type": "test",
            "name": f"test_{name}.py",
            "description": "Test suite"
        })

        # Documentation
        artifacts.append({
            "type": "documentation",
            "name": f"{name}_README.md",
            "description": "Usage documentation"
        })

        return artifacts

    def _generate_validation_steps(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate validation steps."""
        return [
            {
                "step": "syntax_check",
                "description": "Validate Python syntax",
                "blocking": True
            },
            {
                "step": "type_check",
                "description": "Validate type annotations",
                "blocking": True
            },
            {
                "step": "safety_check",
                "description": "Validate safety constraints",
                "blocking": True
            },
            {
                "step": "test_execution",
                "description": "Run test suite",
                "blocking": True
            },
            {
                "step": "coverage_check",
                "description": "Check test coverage",
                "blocking": False
            }
        ]

    def _build_build_context(self, sanitized_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for code generation."""
        return {
            "specification": sanitized_spec,
            "language": "python",
            "language_version": "3.12",
            "target_platform": "linux",
            "dependency_policy": "stdlib_only",
            "code_style": "pep8",
            "documentation_format": "google",
            "test_framework": "unittest",
            "type_checking": "enabled",
            "build_timestamp": datetime.now().isoformat()
        }

    def _build_safety_constraints(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build safety constraints."""
        constraints = spec.get("constraints", [])

        safety_constraints = {
            "file_system": {
                "read_allowed": ["workspace"],
                "write_allowed": ["workspace/output"],
                "forbidden_paths": ["/etc", "/sys", "/proc", "/dev"]
            },
            "network": {
                "allowed": False,
                "exceptions": []
            },
            "execution": {
                "eval_allowed": False,
                "exec_allowed": False,
                "subprocess_allowed": False
            },
            "resources": {
                "max_memory_mb": 512,
                "max_execution_time_seconds": 300
            },
            "custom_constraints": constraints
        }

        return safety_constraints

    def _build_metadata(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build plan metadata."""
        return {
            "plan_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "spec_name": spec.get("name", "unknown"),
            "builder": "FAZA_30_9_PlanBuilder"
        }

    def validate_plan(self, plan: BuildPlan) -> tuple[bool, List[str]]:
        """
        Validate build plan.

        Args:
            plan: Build plan to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check compile plan
        if not plan.compile_plan:
            errors.append("Missing compile plan")
        else:
            if "compilation_steps" not in plan.compile_plan:
                errors.append("Compile plan missing compilation_steps")
            if "dependencies" not in plan.compile_plan:
                errors.append("Compile plan missing dependencies")

        # Check build context
        if not plan.build_context:
            errors.append("Missing build context")
        else:
            if "specification" not in plan.build_context:
                errors.append("Build context missing specification")

        # Check safety constraints
        if not plan.safety_constraints:
            errors.append("Missing safety constraints")
        else:
            required_sections = ["file_system", "network", "execution"]
            for section in required_sections:
                if section not in plan.safety_constraints:
                    errors.append(f"Safety constraints missing {section}")

        is_valid = len(errors) == 0

        return is_valid, errors


def build_plan(
    spec: Dict[str, Any],
    sanitized_spec: Dict[str, Any]
) -> BuildPlan:
    """
    Convenience function to build plan.

    Args:
        spec: Original specification
        sanitized_spec: Sanitized specification

    Returns:
        BuildPlan
    """
    builder = PlanBuilder()
    return builder.build(spec, sanitized_spec)

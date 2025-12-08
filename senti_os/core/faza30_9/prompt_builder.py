"""
FAZA 30.9 – Prompt Builder
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
import json


class PromptBuilder:
    """
    Builds safe LLM code-generation prompts from sanitized specifications.

    Converts sanitized SESY specifications into structured prompts
    that can be safely sent to external LLMs for code generation.

    All prompts include:
    - Clear instructions
    - Format requirements
    - Safety restrictions
    - No internal architecture leakage
    """

    PROMPT_TEMPLATE = """# Code Generation Request

## Component Overview
**Name:** {name}
**Purpose:** {purpose}

## Requirements

{requirements}

## Architecture

{architecture}

## API Specification

{api_spec}

## Constraints

{constraints}

## Test Requirements

{test_requirements}

## Implementation Instructions

1. **Language:** Python 3.12+
2. **Dependencies:** Standard library only (no external packages)
3. **Type Annotations:** Fully type-annotated code required
4. **Documentation:** Include docstrings for all public APIs
5. **Error Handling:** Implement proper exception handling
6. **Testing:** Include unit tests using unittest framework

## Code Quality Requirements

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Keep functions focused and single-purpose
- Avoid magic numbers and hardcoded values
- Include input validation

## Safety Constraints

- NO file system access outside designated workspace
- NO network operations without explicit validation
- NO execution of arbitrary code
- NO access to system resources
- NO hardcoded credentials or secrets

## Output Format

Provide complete, production-ready Python code organized as:

1. Main module file(s)
2. Test file(s)
3. Brief usage documentation

Ensure all code is self-contained and executable.
"""

    def __init__(self) -> None:
        """Initialize the prompt builder."""
        pass

    def build(self, sanitized_spec: Dict[str, Any]) -> str:
        """
        Build LLM prompt from sanitized specification.

        Args:
            sanitized_spec: Sanitized SESY specification

        Returns:
            Complete LLM prompt string
        """
        # Extract components
        name = sanitized_spec.get("name", "Component")
        purpose = sanitized_spec.get("purpose", "")
        architecture = sanitized_spec.get("architecture", {})
        api_definitions = sanitized_spec.get("api_definitions", [])
        constraints = sanitized_spec.get("constraints", [])
        test_plan = sanitized_spec.get("test_plan", {})

        # Build sections
        requirements_section = self._build_requirements_section(sanitized_spec)
        architecture_section = self._build_architecture_section(architecture)
        api_section = self._build_api_section(api_definitions)
        constraints_section = self._build_constraints_section(constraints)
        test_section = self._build_test_section(test_plan)

        # Fill template
        prompt = self.PROMPT_TEMPLATE.format(
            name=name,
            purpose=purpose,
            requirements=requirements_section,
            architecture=architecture_section,
            api_spec=api_section,
            constraints=constraints_section,
            test_requirements=test_section
        )

        return prompt

    def _build_requirements_section(self, spec: Dict[str, Any]) -> str:
        """Build requirements section."""
        lines = []

        # Extract from purpose
        purpose = spec.get("purpose", "")
        if purpose:
            lines.append(f"- {purpose}")

        # Add from API definitions
        api_defs = spec.get("api_definitions", [])
        for api_def in api_defs[:5]:  # Limit to top 5
            if "description" in api_def:
                lines.append(f"- {api_def['description']}")

        if not lines:
            lines.append("- Implement component as specified")

        return "\n".join(lines)

    def _build_architecture_section(self, architecture: Dict[str, Any]) -> str:
        """Build architecture section."""
        lines = []

        # Architecture type
        arch_type = architecture.get("type", "modular")
        lines.append(f"**Type:** {arch_type}")

        # Complexity
        complexity = architecture.get("complexity", "moderate")
        lines.append(f"**Complexity:** {complexity}")

        # Components
        components = architecture.get("components", [])
        if components:
            lines.append("\n**Components:**")
            for comp in components:
                name = comp.get("name", "unknown")
                responsibility = comp.get("responsibility", "")
                lines.append(f"- {name}: {responsibility}")

        # Patterns
        patterns = architecture.get("patterns", [])
        if patterns:
            lines.append(f"\n**Patterns:** {', '.join(patterns)}")

        return "\n".join(lines)

    def _build_api_section(self, api_definitions: List[Dict[str, Any]]) -> str:
        """Build API specification section."""
        lines = []

        for api_def in api_definitions:
            method = api_def.get("method", "unknown")
            description = api_def.get("description", "")

            lines.append(f"### {method}")
            if description:
                lines.append(f"{description}\n")

            # Inputs
            inputs = api_def.get("inputs", [])
            if inputs:
                lines.append("**Inputs:**")
                for inp in inputs:
                    name = inp.get("name", "param")
                    type_hint = inp.get("type", "Any")
                    desc = inp.get("description", "")
                    lines.append(f"- {name}: {type_hint} - {desc}")

            # Outputs
            outputs = api_def.get("outputs", [])
            if outputs:
                lines.append("\n**Outputs:**")
                for out in outputs:
                    name = out.get("name", "result")
                    type_hint = out.get("type", "Any")
                    desc = out.get("description", "")
                    lines.append(f"- {name}: {type_hint} - {desc}")

            # Errors
            errors = api_def.get("errors", [])
            if errors:
                lines.append(f"\n**Errors:** {', '.join(errors)}")

            lines.append("")  # Blank line between methods

        if not lines:
            lines.append("*No specific API defined - implement as appropriate*")

        return "\n".join(lines)

    def _build_constraints_section(self, constraints: List[str]) -> str:
        """Build constraints section."""
        if not constraints:
            return "- Follow standard best practices"

        lines = []
        for constraint in constraints:
            lines.append(f"- {constraint}")

        return "\n".join(lines)

    def _build_test_section(self, test_plan: Dict[str, Any]) -> str:
        """Build test requirements section."""
        lines = []

        # Coverage target
        coverage = test_plan.get("coverage_target", 0.8)
        lines.append(f"**Coverage Target:** {coverage * 100:.0f}%")

        # Test types
        test_types = test_plan.get("test_types", ["unit"])
        lines.append(f"**Test Types:** {', '.join(test_types)}")

        # Test cases
        test_cases = test_plan.get("test_cases", [])
        if test_cases:
            lines.append("\n**Test Cases:**")
            for tc in test_cases[:10]:  # Limit to top 10
                tc_id = tc.get("id", "TC")
                description = tc.get("description", "")
                lines.append(f"- {tc_id}: {description}")

        return "\n".join(lines)

    def build_with_context(
        self,
        sanitized_spec: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt with additional context.

        Args:
            sanitized_spec: Sanitized specification
            additional_context: Additional safe context to include

        Returns:
            Enhanced prompt
        """
        base_prompt = self.build(sanitized_spec)

        if not additional_context:
            return base_prompt

        # Add context section
        context_section = "\n\n## Additional Context\n\n"

        for key, value in additional_context.items():
            context_section += f"**{key}:** {value}\n"

        return base_prompt + context_section

    def validate_prompt(self, prompt: str) -> tuple[bool, List[str]]:
        """
        Validate that prompt is safe.

        Args:
            prompt: Generated prompt

        Returns:
            Tuple of (is_safe, list of issues)
        """
        issues = []

        # Check for sensitive patterns (should not be in sanitized prompt)
        sensitive_patterns = [
            "faza", "phase", "senti_os", "senti_core",
            "kernel", "governance", "agent", "meta"
        ]

        prompt_lower = prompt.lower()
        for pattern in sensitive_patterns:
            if pattern in prompt_lower:
                issues.append(f"Sensitive term found: {pattern}")

        # Check for file paths
        if "/" in prompt and ".py" in prompt:
            issues.append("Potential file path found in prompt")

        is_safe = len(issues) == 0

        return is_safe, issues


def build_prompt(sanitized_spec: Dict[str, Any]) -> str:
    """
    Convenience function to build LLM prompt.

    Args:
        sanitized_spec: Sanitized specification

    Returns:
        LLM prompt string
    """
    builder = PromptBuilder()
    return builder.build(sanitized_spec)

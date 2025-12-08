"""
FAZA 30.9 – Controller
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

from .spec_extractor import SpecExtractor, ExtractedSpec
from .spec_generator import SpecGenerator, SESYSpec
from .spec_sanitizer import SpecSanitizer
from .spec_validator import SpecValidator, ValidationResult, ValidationReport
from .prompt_builder import PromptBuilder
from .plan_builder import PlanBuilder, BuildPlan


class PipelineStage(Enum):
    """Pipeline execution stages."""
    EXTRACTION = "extraction"
    GENERATION = "generation"
    SANITIZATION = "sanitization"
    VALIDATION = "validation"
    PROMPT_BUILD = "prompt_build"
    PLAN_BUILD = "plan_build"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineResult:
    """Result of pipeline execution."""

    success: bool
    stage: PipelineStage
    extracted_spec: Optional[ExtractedSpec] = None
    generated_spec: Optional[SESYSpec] = None
    sanitized_spec: Optional[Dict[str, Any]] = None
    validation_report: Optional[ValidationReport] = None
    llm_prompt: Optional[str] = None
    build_plan: Optional[BuildPlan] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "stage": self.stage.value,
            "extracted_spec": self.extracted_spec.to_dict() if self.extracted_spec else None,
            "generated_spec": self.generated_spec.to_dict() if self.generated_spec else None,
            "sanitized_spec": self.sanitized_spec,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "llm_prompt": self.llm_prompt,
            "build_plan": self.build_plan.to_dict() if self.build_plan else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class SpecEngineController:
    """
    Main controller for FAZA 30.9 SPEC Engine.

    Orchestrates the complete pipeline:
    1. Extract specification from natural language
    2. Generate structured SESY specification
    3. Sanitize for external use
    4. Validate for safety and completeness
    5. Build LLM prompt
    6. Generate build plan

    Provides safety gating at each stage.
    """

    def __init__(self) -> None:
        """Initialize the controller."""
        self.extractor = SpecExtractor()
        self.generator = SpecGenerator()
        self.sanitizer = SpecSanitizer()
        self.validator = SpecValidator()
        self.prompt_builder = PromptBuilder()
        self.plan_builder = PlanBuilder()

    def process(
        self,
        natural_language: str,
        component_name: Optional[str] = None,
        strict_validation: bool = True
    ) -> PipelineResult:
        """
        Process natural language input through complete pipeline.

        Args:
            natural_language: User input describing desired component
            component_name: Optional name for component
            strict_validation: If True, block on any validation errors

        Returns:
            PipelineResult with all outputs
        """
        result = PipelineResult(success=False, stage=PipelineStage.EXTRACTION)

        try:
            # Stage 1: Extract
            extracted_spec = self._run_extraction(natural_language, result)
            if not extracted_spec:
                return result

            result.extracted_spec = extracted_spec
            result.stage = PipelineStage.GENERATION

            # Stage 2: Generate
            generated_spec = self._run_generation(extracted_spec, component_name, result)
            if not generated_spec:
                return result

            result.generated_spec = generated_spec
            result.stage = PipelineStage.SANITIZATION

            # Stage 3: Sanitize
            sanitized_spec = self._run_sanitization(generated_spec, result)
            if not sanitized_spec:
                return result

            result.sanitized_spec = sanitized_spec
            result.stage = PipelineStage.VALIDATION

            # Stage 4: Validate
            validation_report = self._run_validation(
                generated_spec,
                sanitized_spec,
                strict_validation,
                result
            )
            if not validation_report:
                return result

            result.validation_report = validation_report

            # Check if validation blocks
            if validation_report.is_blocked():
                result.stage = PipelineStage.FAILED
                result.errors.append("Validation blocked pipeline")
                return result

            result.stage = PipelineStage.PROMPT_BUILD

            # Stage 5: Build LLM prompt
            llm_prompt = self._run_prompt_building(sanitized_spec, result)
            if not llm_prompt:
                return result

            result.llm_prompt = llm_prompt
            result.stage = PipelineStage.PLAN_BUILD

            # Stage 6: Build plan
            build_plan = self._run_plan_building(
                generated_spec.to_dict(),
                sanitized_spec,
                result
            )
            if not build_plan:
                return result

            result.build_plan = build_plan
            result.stage = PipelineStage.COMPLETE
            result.success = True

            return result

        except Exception as e:
            result.stage = PipelineStage.FAILED
            result.errors.append(f"Pipeline exception: {str(e)}")
            result.success = False
            return result

    def _run_extraction(
        self,
        natural_language: str,
        result: PipelineResult
    ) -> Optional[ExtractedSpec]:
        """Run extraction stage."""
        try:
            extracted = self.extractor.extract(natural_language)

            # Validate extraction
            is_valid, warnings = self.extractor.validate_extraction(extracted)
            result.warnings.extend(warnings)

            if not is_valid:
                result.errors.append("Extraction validation failed")
                return None

            return extracted

        except Exception as e:
            result.errors.append(f"Extraction failed: {str(e)}")
            return None

    def _run_generation(
        self,
        extracted_spec: ExtractedSpec,
        component_name: Optional[str],
        result: PipelineResult
    ) -> Optional[SESYSpec]:
        """Run generation stage."""
        try:
            generated = self.generator.generate(
                extracted_spec.to_dict(),
                component_name
            )

            # Validate generated spec
            is_valid, errors = self.generator.validate_spec(generated)
            if not is_valid:
                result.errors.extend(errors)
                return None

            return generated

        except Exception as e:
            result.errors.append(f"Generation failed: {str(e)}")
            return None

    def _run_sanitization(
        self,
        generated_spec: SESYSpec,
        result: PipelineResult
    ) -> Optional[Dict[str, Any]]:
        """Run sanitization stage."""
        try:
            sanitized = self.sanitizer.sanitize(generated_spec.to_dict())

            # Validate sanitization
            is_safe, found_sensitive = self.sanitizer.validate_sanitization(sanitized)
            if not is_safe:
                result.errors.append(
                    f"Sanitization incomplete: {', '.join(found_sensitive)}"
                )
                return None

            return sanitized

        except Exception as e:
            result.errors.append(f"Sanitization failed: {str(e)}")
            return None

    def _run_validation(
        self,
        generated_spec: SESYSpec,
        sanitized_spec: Dict[str, Any],
        strict: bool,
        result: PipelineResult
    ) -> Optional[ValidationReport]:
        """Run validation stage."""
        try:
            # Validate original spec
            validation_report = self.validator.validate(generated_spec.to_dict())

            # Add warnings to result
            result.warnings.extend(validation_report.warnings)

            # If strict mode and has errors, fail
            if strict and validation_report.errors:
                result.errors.extend(validation_report.errors)

            # Also validate sanitized version
            sanitized_validation = self.validator.validate_sanitized(sanitized_spec)

            if sanitized_validation.is_blocked():
                result.errors.extend(sanitized_validation.errors)
                return None

            return validation_report

        except Exception as e:
            result.errors.append(f"Validation failed: {str(e)}")
            return None

    def _run_prompt_building(
        self,
        sanitized_spec: Dict[str, Any],
        result: PipelineResult
    ) -> Optional[str]:
        """Run prompt building stage."""
        try:
            prompt = self.prompt_builder.build(sanitized_spec)

            # Validate prompt
            is_safe, issues = self.prompt_builder.validate_prompt(prompt)
            if not is_safe:
                result.errors.append(f"Prompt validation failed: {', '.join(issues)}")
                return None

            return prompt

        except Exception as e:
            result.errors.append(f"Prompt building failed: {str(e)}")
            return None

    def _run_plan_building(
        self,
        spec: Dict[str, Any],
        sanitized_spec: Dict[str, Any],
        result: PipelineResult
    ) -> Optional[BuildPlan]:
        """Run plan building stage."""
        try:
            plan = self.plan_builder.build(spec, sanitized_spec)

            # Validate plan
            is_valid, errors = self.plan_builder.validate_plan(plan)
            if not is_valid:
                result.errors.extend(errors)
                return None

            return plan

        except Exception as e:
            result.errors.append(f"Plan building failed: {str(e)}")
            return None

    def process_with_hooks(
        self,
        natural_language: str,
        component_name: Optional[str] = None,
        hooks: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Process with integration hooks.

        Args:
            natural_language: User input
            component_name: Optional component name
            hooks: Optional hooks for integration

        Returns:
            PipelineResult
        """
        # Run normal pipeline
        result = self.process(natural_language, component_name)

        # Apply hooks if provided
        if hooks and result.success:
            self._apply_hooks(result, hooks)

        return result

    def _apply_hooks(
        self,
        result: PipelineResult,
        hooks: Dict[str, Any]
    ) -> None:
        """Apply integration hooks."""
        # This is a placeholder for integration with other FAZA phases
        # Actual implementation would call integration_layer
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get controller status."""
        return {
            "controller": "FAZA_30_9_SpecEngine",
            "version": "1.0",
            "components": {
                "extractor": "ready",
                "generator": "ready",
                "sanitizer": "ready",
                "validator": "ready",
                "prompt_builder": "ready",
                "plan_builder": "ready"
            }
        }


def process_natural_language(
    natural_language: str,
    component_name: Optional[str] = None
) -> PipelineResult:
    """
    Convenience function to process natural language input.

    Args:
        natural_language: User input
        component_name: Optional component name

    Returns:
        PipelineResult
    """
    controller = SpecEngineController()
    return controller.process(natural_language, component_name)

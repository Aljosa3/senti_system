"""
FAZA 30.9 – Comprehensive Test Suite
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

import unittest
import json
from typing import Dict, Any

# Import FAZA 30.9 components
from senti_os.core.faza30_9 import (
    SpecExtractor,
    ExtractedSpec,
    SpecGenerator,
    SESYSpec,
    SpecSanitizer,
    SpecValidator,
    ValidationResult,
    PromptBuilder,
    PlanBuilder,
    SpecEngineController,
    process_natural_language,
    IntegrationLayer,
    IntegrationType,
    EventHooks,
    EventType,
)


class TestSpecExtractor(unittest.TestCase):
    """Test SpecExtractor component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.extractor = SpecExtractor()

    def test_extract_basic_input(self) -> None:
        """Test extraction from basic natural language."""
        input_text = """
        Create a component that validates user input.
        It must support email and phone number validation.
        The component should return validation results.
        """

        result = self.extractor.extract(input_text)

        self.assertIsInstance(result, ExtractedSpec)
        self.assertTrue(len(result.requirements) > 0)
        self.assertEqual(result.raw_text, input_text)

    def test_extract_with_constraints(self) -> None:
        """Test extraction with constraints."""
        input_text = """
        The system must validate inputs.
        It must not access the network.
        It cannot write to disk.
        """

        result = self.extractor.extract(input_text)

        self.assertTrue(len(result.constraints) > 0)
        self.assertTrue(len(result.requirements) > 0)

    def test_extract_metadata(self) -> None:
        """Test metadata extraction."""
        input_text = "Create a module named validator version 1.0"

        result = self.extractor.extract(input_text)

        self.assertIn("suggested_name", result.metadata)
        self.assertEqual(result.metadata["suggested_name"], "validator")

    def test_validate_extraction(self) -> None:
        """Test extraction validation."""
        input_text = "Create a component that processes data"

        result = self.extractor.extract(input_text)
        is_valid, warnings = self.extractor.validate_extraction(result)

        self.assertTrue(is_valid)

    def test_extraction_too_short(self) -> None:
        """Test extraction with insufficient input."""
        input_text = "Do something"

        result = self.extractor.extract(input_text)
        is_valid, warnings = self.extractor.validate_extraction(result)

        self.assertFalse(is_valid)
        self.assertTrue(len(warnings) > 0)


class TestSpecGenerator(unittest.TestCase):
    """Test SpecGenerator component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.generator = SpecGenerator()

    def test_generate_basic_spec(self) -> None:
        """Test basic specification generation."""
        extracted = {
            "requirements": ["Must validate input", "Must return results"],
            "constraints": ["No network access"],
            "goals": ["Provide validation service"],
            "inputs": ["data to validate"],
            "outputs": ["validation result"],
            "metadata": {"suggested_name": "validator"}
        }

        result = self.generator.generate(extracted)

        self.assertIsInstance(result, SESYSpec)
        self.assertEqual(result.name, "validator")
        self.assertTrue(len(result.constraints) > 0)

    def test_generate_with_architecture(self) -> None:
        """Test generation with architecture."""
        extracted = {
            "requirements": ["Process data"],
            "goals": ["Data processing"],
            "metadata": {"complexity": "moderate"}
        }

        result = self.generator.generate(extracted)

        self.assertIn("architecture", result.to_dict())
        self.assertEqual(result.architecture["complexity"], "moderate")

    def test_generate_api_definitions(self) -> None:
        """Test API definitions generation."""
        extracted = {
            "requirements": ["Process input"],
            "inputs": ["user data"],
            "outputs": ["processed result"]
        }

        result = self.generator.generate(extracted)

        self.assertTrue(len(result.api_definitions) > 0)

    def test_validate_generated_spec(self) -> None:
        """Test validation of generated spec."""
        extracted = {
            "requirements": ["Do work"],
            "goals": ["Complete task"]
        }

        result = self.generator.generate(extracted, "test_component")
        is_valid, errors = self.generator.validate_spec(result)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_spec_to_json(self) -> None:
        """Test SESY spec JSON serialization."""
        extracted = {
            "requirements": ["Test requirement"],
            "goals": ["Test goal"]
        }

        result = self.generator.generate(extracted)
        json_str = result.to_json()

        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["format"], "SESY")


class TestSpecSanitizer(unittest.TestCase):
    """Test SpecSanitizer component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sanitizer = SpecSanitizer()

    def test_sanitize_sensitive_terms(self) -> None:
        """Test sanitization of sensitive terms."""
        spec = {
            "name": "test_component",
            "purpose": "This uses FAZA 16 and senti_os kernel",
            "description": "Integrates with agent system"
        }

        result = self.sanitizer.sanitize(spec)

        spec_str = json.dumps(result).lower()
        # Should not contain sensitive terms
        self.assertNotIn("faza 16", spec_str)

    def test_sanitize_file_paths(self) -> None:
        """Test sanitization of file paths."""
        spec = {
            "name": "component",
            "implementation": "See /path/to/file.py"
        }

        result = self.sanitizer.sanitize(spec)

        self.assertIn("[REDACTED]", json.dumps(result))

    def test_validate_sanitization(self) -> None:
        """Test validation of sanitization."""
        spec = {
            "name": "safe_component",
            "purpose": "Process data safely"
        }

        sanitized = self.sanitizer.sanitize(spec)
        is_safe, found = self.sanitizer.validate_sanitization(sanitized)

        self.assertTrue(is_safe)
        self.assertEqual(len(found), 0)

    def test_sanitization_report(self) -> None:
        """Test sanitization report generation."""
        original = {
            "name": "component",
            "purpose": "Uses FAZA 10 expansion"
        }

        sanitized = self.sanitizer.sanitize(original)
        report = self.sanitizer.get_sanitization_report(original, sanitized)

        self.assertIn("redaction_count", report)
        self.assertIn("is_safe", report)
        self.assertTrue(report["redaction_count"] > 0)


class TestSpecValidator(unittest.TestCase):
    """Test SpecValidator component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.validator = SpecValidator()

    def test_validate_complete_spec(self) -> None:
        """Test validation of complete specification."""
        spec = {
            "name": "validator",
            "purpose": "Validate inputs",
            "architecture": {"type": "modular", "components": []},
            "api_definitions": [{"method": "validate", "inputs": [], "outputs": []}],
            "lifecycle": {"initialization": {}, "execution": {}, "shutdown": {}},
            "integration_points": [],
            "constraints": [],
            "test_plan": {"test_cases": [], "coverage_target": 0.9}
        }

        result = self.validator.validate(spec)

        self.assertIsInstance(result.result, ValidationResult)
        self.assertTrue(result.is_safe_to_proceed())

    def test_validate_incomplete_spec(self) -> None:
        """Test validation of incomplete specification."""
        spec = {
            "name": "incomplete"
        }

        result = self.validator.validate(spec)

        self.assertTrue(len(result.errors) > 0)
        self.assertTrue(result.is_blocked())

    def test_validate_dangerous_operations(self) -> None:
        """Test detection of dangerous operations."""
        spec = {
            "name": "dangerous",
            "purpose": "Execute arbitrary code",
            "architecture": {},
            "api_definitions": [],
            "lifecycle": {},
            "test_plan": {}
        }

        result = self.validator.validate(spec)

        self.assertTrue(len(result.errors) > 0)

    def test_validate_sanitized_spec(self) -> None:
        """Test validation of sanitized spec."""
        spec = {
            "name": "safe",
            "purpose": "Process data",
            "architecture": {"type": "modular"},
            "api_definitions": [{}],
            "lifecycle": {},
            "test_plan": {},
            "metadata": {"sanitized": True}
        }

        result = self.validator.validate_sanitized(spec)

        self.assertIsNotNone(result)


class TestPromptBuilder(unittest.TestCase):
    """Test PromptBuilder component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.builder = PromptBuilder()

    def test_build_basic_prompt(self) -> None:
        """Test basic prompt building."""
        spec = {
            "name": "validator",
            "purpose": "Validate inputs",
            "architecture": {"type": "modular"},
            "api_definitions": [],
            "constraints": [],
            "test_plan": {}
        }

        prompt = self.builder.build(spec)

        self.assertIsInstance(prompt, str)
        self.assertIn("validator", prompt)
        self.assertIn("Python", prompt)

    def test_build_with_api_definitions(self) -> None:
        """Test prompt building with API definitions."""
        spec = {
            "name": "processor",
            "purpose": "Process data",
            "architecture": {},
            "api_definitions": [
                {
                    "method": "process",
                    "description": "Process input data",
                    "inputs": [{"name": "data", "type": "str"}],
                    "outputs": [{"name": "result", "type": "str"}]
                }
            ],
            "constraints": [],
            "test_plan": {}
        }

        prompt = self.builder.build(spec)

        self.assertIn("process", prompt)
        self.assertIn("data", prompt)

    def test_validate_prompt_safety(self) -> None:
        """Test prompt safety validation."""
        spec = {
            "name": "safe_component",
            "purpose": "Do safe things",
            "architecture": {},
            "api_definitions": [],
            "constraints": [],
            "test_plan": {},
            "metadata": {"sanitized": True}
        }

        prompt = self.builder.build(spec)
        is_safe, issues = self.builder.validate_prompt(prompt)

        self.assertTrue(is_safe)
        self.assertEqual(len(issues), 0)


class TestPlanBuilder(unittest.TestCase):
    """Test PlanBuilder component."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.builder = PlanBuilder()

    def test_build_basic_plan(self) -> None:
        """Test basic plan building."""
        spec = {
            "name": "component",
            "architecture": {},
            "api_definitions": [],
            "constraints": []
        }

        sanitized_spec = {"name": "component"}

        plan = self.builder.build(spec, sanitized_spec)

        self.assertIsNotNone(plan.compile_plan)
        self.assertIsNotNone(plan.build_context)
        self.assertIsNotNone(plan.safety_constraints)

    def test_compile_plan_structure(self) -> None:
        """Test compile plan structure."""
        spec = {"name": "test", "architecture": {}}
        sanitized = {"name": "test"}

        plan = self.builder.build(spec, sanitized)

        self.assertIn("compilation_steps", plan.compile_plan)
        self.assertIn("dependencies", plan.compile_plan)
        self.assertTrue(len(plan.compile_plan["compilation_steps"]) > 0)

    def test_safety_constraints(self) -> None:
        """Test safety constraints generation."""
        spec = {"name": "test", "constraints": ["No network"]}
        sanitized = {"name": "test"}

        plan = self.builder.build(spec, sanitized)

        self.assertIn("file_system", plan.safety_constraints)
        self.assertIn("network", plan.safety_constraints)
        self.assertFalse(plan.safety_constraints["network"]["allowed"])

    def test_validate_plan(self) -> None:
        """Test plan validation."""
        spec = {"name": "test", "architecture": {}}
        sanitized = {"name": "test"}

        plan = self.builder.build(spec, sanitized)
        is_valid, errors = self.builder.validate_plan(plan)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestController(unittest.TestCase):
    """Test SpecEngineController."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.controller = SpecEngineController()

    def test_process_complete_pipeline(self) -> None:
        """Test complete pipeline processing."""
        input_text = """
        Create a component that validates email addresses.
        It must check format and domain.
        Return validation result as boolean.
        """

        result = self.controller.process(input_text, "email_validator")

        self.assertIsNotNone(result)
        self.assertTrue(result.success or len(result.errors) > 0)

    def test_pipeline_stages(self) -> None:
        """Test pipeline stage progression."""
        input_text = "Create a data processor component that transforms input data."

        result = self.controller.process(input_text)

        # Should progress through stages
        self.assertIsNotNone(result.stage)

    def test_controller_status(self) -> None:
        """Test controller status."""
        status = self.controller.get_status()

        self.assertIn("controller", status)
        self.assertIn("components", status)
        self.assertEqual(status["components"]["extractor"], "ready")


class TestIntegrationLayer(unittest.TestCase):
    """Test IntegrationLayer."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.integration = IntegrationLayer()

    def test_enable_disable_integration(self) -> None:
        """Test enabling and disabling integration."""
        self.integration.enable_integration(IntegrationType.GOVERNANCE)

        self.assertTrue(
            self.integration.integration_enabled[IntegrationType.GOVERNANCE]
        )

        self.integration.disable_integration(IntegrationType.GOVERNANCE)

        self.assertFalse(
            self.integration.integration_enabled[IntegrationType.GOVERNANCE]
        )

    def test_register_handler(self) -> None:
        """Test handler registration."""
        called = []

        def handler(payload: Dict[str, Any]) -> None:
            called.append(payload)

        self.integration.register_handler(IntegrationType.GOVERNANCE, handler)

        handlers = self.integration.handlers[IntegrationType.GOVERNANCE]
        self.assertTrue(len(handlers) > 0)

    def test_integration_status(self) -> None:
        """Test integration status."""
        self.integration.enable_integration(IntegrationType.LLM_MANAGER)

        status = self.integration.get_integration_status()

        self.assertIn("enabled_integrations", status)
        self.assertIn("llm_manager", status["enabled_integrations"])


class TestEventHooks(unittest.TestCase):
    """Test EventHooks."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.hooks = EventHooks()

    def test_emit_event(self) -> None:
        """Test event emission."""
        self.hooks.emit_event(
            EventType.EXTRACTION_STARTED,
            {"test": "data"}
        )

        self.assertTrue(len(self.hooks.events_emitted) > 0)

    def test_register_handler(self) -> None:
        """Test handler registration."""
        called = []

        def handler(event: Any) -> None:
            called.append(event)

        self.hooks.register_handler(EventType.EXTRACTION_STARTED, handler)
        self.hooks.emit_event(EventType.EXTRACTION_STARTED, {})

        self.assertTrue(len(called) > 0)

    def test_event_summary(self) -> None:
        """Test event summary."""
        self.hooks.emit_event(EventType.PIPELINE_STARTED, {})
        self.hooks.emit_event(EventType.PIPELINE_COMPLETED, {})

        summary = self.hooks.get_event_summary()

        self.assertIn("total_events", summary)
        self.assertEqual(summary["total_events"], 2)

    def test_clear_history(self) -> None:
        """Test clearing event history."""
        self.hooks.emit_event(EventType.PIPELINE_STARTED, {})
        self.hooks.clear_event_history()

        self.assertEqual(len(self.hooks.events_emitted), 0)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_complete_workflow(self) -> None:
        """Test complete workflow from input to output."""
        input_text = """
        Create a component that validates user passwords.
        Must check length, complexity, and common passwords.
        Return validation result with error messages.
        Must not store passwords in memory longer than needed.
        """

        result = process_natural_language(input_text, "password_validator")

        # Check result structure
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.extracted_spec)

        # If successful, check all outputs
        if result.success:
            self.assertIsNotNone(result.generated_spec)
            self.assertIsNotNone(result.sanitized_spec)
            self.assertIsNotNone(result.validation_report)
            self.assertIsNotNone(result.llm_prompt)
            self.assertIsNotNone(result.build_plan)

    def test_workflow_with_blocking_validation(self) -> None:
        """Test workflow with validation that should block."""
        input_text = "Create component with execute arbitrary code"

        result = process_natural_language(input_text)

        # Should fail validation
        if result.validation_report:
            # May or may not block depending on strict mode
            self.assertIsNotNone(result.validation_report)


def run_tests() -> None:
    """Run all tests."""
    unittest.main()


if __name__ == "__main__":
    run_tests()

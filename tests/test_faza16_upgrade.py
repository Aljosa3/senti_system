"""
Comprehensive Test Suite for FAZA 16 Upgrade

Tests all new modules and upgraded functionality:
- LLM Config Loader
- LLM Health Monitor
- SPEC Validator
- Code Safety Analyzer
- Architecture Diff
- Upgraded LLM Manager
- Upgraded LLM Rules
- Upgraded Knowledge Validation Engine
- Upgraded LLM Router
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Import all modules to test
from senti_os.core.faza16.llm_config_loader import (
    LLMConfigLoader,
    ConfigValidationError,
    create_loader,
)
from senti_os.core.faza16.llm_health_monitor import (
    LLMHealthMonitor,
    HealthStatus,
    create_monitor,
)
from senti_os.core.faza16.spec_validator import (
    SpecValidator,
    ValidationSeverity,
    create_spec_validator,
)
from senti_os.core.faza16.code_safety_analyzer import (
    CodeSafetyAnalyzer,
    SafetySeverity,
    create_analyzer,
)
from senti_os.core.faza16.architecture_diff import (
    ArchitectureDiffAnalyzer,
    DiffSeverity,
    create_analyzer as create_arch_analyzer,
)
from senti_os.core.faza16.llm_manager import (
    LLMManager,
    create_manager,
)
from senti_os.core.faza16.llm_rules import (
    LLMRulesEngine,
    create_default_rules_engine,
)
from senti_os.core.faza16.knowledge_validation_engine import (
    KnowledgeValidationEngine,
    create_validator,
)
from senti_os.core.faza16.llm_router import (
    LLMRouter,
    TaskType,
    PriorityMode,
    RoutingRequest,
)


class TestLLMConfigLoader(unittest.TestCase):
    """Test LLM Config Loader functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "llm_config.json")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_load_valid_config(self):
        """Test loading a valid configuration."""
        config_data = {
            "models": [
                {
                    "model_id": "test_model",
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "max_tokens": 4096,
                }
            ],
            "default_model": "test_model",
        }

        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)

        loader = LLMConfigLoader(self.config_path)
        config = loader.load_config()

        self.assertEqual(len(config.models), 1)
        self.assertEqual(config.models[0].model_id, "test_model")
        self.assertEqual(config.default_model, "test_model")

    def test_missing_config_file(self):
        """Test handling of missing config file."""
        loader = LLMConfigLoader("/nonexistent/path.json")
        config = loader.load_config()

        # Should create default config
        self.assertIsNotNone(config)
        self.assertEqual(len(config.models), 1)

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        with open(self.config_path, 'w') as f:
            f.write("{ invalid json }")

        loader = LLMConfigLoader(self.config_path)

        with self.assertRaises(ConfigValidationError):
            loader.load_config()

    def test_missing_required_field(self):
        """Test validation of required fields."""
        config_data = {
            "models": [
                {
                    "model_id": "test_model",
                    # Missing provider and model_name
                }
            ]
        }

        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)

        loader = LLMConfigLoader(self.config_path)

        with self.assertRaises(ConfigValidationError):
            loader.load_config()


class TestLLMHealthMonitor(unittest.TestCase):
    """Test LLM Health Monitor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = create_monitor()

    def test_record_successful_interaction(self):
        """Test recording a successful interaction."""
        self.monitor.record_interaction(
            model_id="test_model",
            latency_ms=500.0,
            success=True,
        )

        report = self.monitor.get_health_report("test_model")

        self.assertEqual(report.total_interactions, 1)
        self.assertEqual(report.error_rate, 0.0)
        self.assertGreater(report.health_score, 50.0)

    def test_record_failed_interaction(self):
        """Test recording a failed interaction."""
        self.monitor.record_interaction(
            model_id="test_model",
            latency_ms=1000.0,
            success=False,
            error_type="timeout",
        )

        report = self.monitor.get_health_report("test_model")

        self.assertEqual(report.total_interactions, 1)
        self.assertEqual(report.error_rate, 1.0)
        self.assertLess(report.health_score, 50.0)

    def test_health_score_calculation(self):
        """Test health score calculation with mixed results."""
        # Record 7 successes and 3 failures
        for i in range(7):
            self.monitor.record_interaction(
                model_id="test_model",
                latency_ms=300.0,
                success=True,
            )

        for i in range(3):
            self.monitor.record_interaction(
                model_id="test_model",
                latency_ms=2000.0,
                success=False,
            )

        score = self.monitor.compute_health_score("test_model")

        # With 70% success rate, score should be moderate
        self.assertGreater(score, 30.0)
        self.assertLess(score, 90.0)

    def test_health_status_mapping(self):
        """Test health status mapping."""
        # Record excellent interaction
        for i in range(10):
            self.monitor.record_interaction(
                model_id="excellent_model",
                latency_ms=200.0,
                success=True,
                hallucination_score=0.0,
            )

        report = self.monitor.get_health_report("excellent_model")
        self.assertIn(report.health_status, [HealthStatus.EXCELLENT, HealthStatus.GOOD])


class TestSPECValidator(unittest.TestCase):
    """Test SPEC Validator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = create_spec_validator()

    def test_valid_spec(self):
        """Test validation of a valid SPEC."""
        spec = """
# Objective
Build a new sensor module

## Architecture
Three-layer design with API, logic, and storage

## Implementation
1. Create sensor class
2. Implement data collection
3. Add error handling

## Testing
Unit tests and integration tests
"""

        result = self.validator.validate_spec(spec, "test_spec")

        self.assertTrue(result.is_valid)
        self.assertGreater(result.score, 80.0)

    def test_empty_spec(self):
        """Test validation of empty SPEC."""
        result = self.validator.validate_spec("", "empty_spec")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.score, 0.0)
        self.assertTrue(any(i.severity == ValidationSeverity.CRITICAL for i in result.issues))

    def test_missing_required_sections(self):
        """Test detection of missing required sections."""
        spec = """
# Some Random Title
Just some text without proper sections
"""

        result = self.validator.validate_spec(spec, "incomplete_spec")

        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.issues) > 0)

    def test_dangerous_pattern_detection(self):
        """Test detection of dangerous patterns in SPEC."""
        spec = """
# Objective
Use eval() to execute dynamic code

## Architecture
Standard design

## Implementation
Call eval(user_input)

## Testing
Basic tests
"""

        result = self.validator.validate_spec(spec, "dangerous_spec")

        self.assertFalse(result.is_valid)
        # Should detect eval() as dangerous
        self.assertTrue(any(
            "eval" in i.message.lower()
            for i in result.issues
        ))


class TestCodeSafetyAnalyzer(unittest.TestCase):
    """Test Code Safety Analyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = create_analyzer()

    def test_safe_code(self):
        """Test analysis of safe code."""
        code = """
def add_numbers(a, b):
    '''Add two numbers.'''
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
"""

        report = self.analyzer.analyze_code(code)

        self.assertTrue(report.is_safe)
        self.assertGreater(report.safety_score, 80.0)

    def test_dangerous_eval(self):
        """Test detection of eval()."""
        code = """
def dangerous_function(user_input):
    return eval(user_input)
"""

        report = self.analyzer.analyze_code(code)

        self.assertFalse(report.is_safe)
        self.assertTrue(any(
            "eval" in i.message.lower()
            for i in report.issues
        ))

    def test_dangerous_exec(self):
        """Test detection of exec()."""
        code = """
def dangerous_function(code_str):
    exec(code_str)
"""

        report = self.analyzer.analyze_code(code)

        self.assertFalse(report.is_safe)
        self.assertTrue(any(
            "exec" in i.message.lower()
            for i in report.issues
        ))

    def test_syntax_error(self):
        """Test handling of syntax errors."""
        code = "def invalid_syntax("

        report = self.analyzer.analyze_code(code)

        self.assertFalse(report.is_safe)
        self.assertEqual(report.safety_score, 0.0)

    def test_empty_function_detection(self):
        """Test detection of empty/stub functions."""
        code = """
def stub_function():
    pass
"""

        report = self.analyzer.analyze_code(code)

        # Should warn about stub function
        self.assertTrue(len(report.warnings) > 0)


class TestArchitectureDiff(unittest.TestCase):
    """Test Architecture Diff Analyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = create_arch_analyzer()

    def test_valid_module_location(self):
        """Test validation of valid module location."""
        module_spec = {
            "name": "test_module",
            "imports": [],
            "files": ["__init__.py"],
        }

        module_path = "/home/pisarna/senti_system/senti_os/core/faza99"

        analysis = self.analyzer.analyze_new_module(module_spec, module_path)

        # Should have some warnings but be generally compatible
        self.assertIsNotNone(analysis)

    def test_protected_directory_access(self):
        """Test detection of protected directory access."""
        module_spec = {
            "name": "test_module",
            "imports": [],
            "files": ["__init__.py"],
        }

        module_path = "/home/pisarna/senti_system/senti_os/boot/test_module"

        analysis = self.analyzer.analyze_new_module(module_spec, module_path)

        self.assertFalse(analysis.is_compatible)
        self.assertTrue(any(
            d.severity == DiffSeverity.CRITICAL
            for d in analysis.diffs
        ))

    def test_illegal_import_detection(self):
        """Test detection of illegal imports from protected paths."""
        module_spec = {
            "name": "test_module",
            "imports": ["senti_os.boot.secret_module"],
            "files": ["__init__.py"],
        }

        module_path = "/home/pisarna/senti_system/modules/sensors/test"

        analysis = self.analyzer.analyze_new_module(module_spec, module_path)

        self.assertFalse(analysis.is_compatible)


class TestUpgradedLLMManager(unittest.TestCase):
    """Test upgraded LLM Manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = create_manager()

    def test_model_selection(self):
        """Test model selection with task profile."""
        task_profile = {
            "task_type": TaskType.CODE_GENERATION,
            "priority_mode": PriorityMode.QUALITY,
            "max_cost": 1.0,
        }

        model_id = self.manager.select_model(task_profile)

        # May be None if no models available, but should not raise
        self.assertIsInstance(model_id, (str, type(None)))

    def test_output_scoring(self):
        """Test model output scoring."""
        good_output = "This is a complete and detailed response."
        score = self.manager.score_model_output("test_model", good_output)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_model_comparison(self):
        """Test model output comparison."""
        output_a = "Detailed response A"
        output_b = "Response B"

        comparison = self.manager.compare_models(
            output_a, output_b,
            "model_a", "model_b"
        )

        self.assertIn("model_a", comparison)
        self.assertIn("model_b", comparison)
        self.assertIn("recommendation", comparison)


class TestUpgradedLLMRules(unittest.TestCase):
    """Test upgraded LLM Rules Engine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules_engine = create_default_rules_engine()

    def test_spec_validation_integration(self):
        """Test SPEC validation through rules engine."""
        spec = """
# Objective
Test objective

## Architecture
Test architecture

## Implementation
Test implementation

## Testing
Test testing
"""

        result = self.rules_engine.validate_spec(spec)

        self.assertTrue(result.is_valid)

    def test_code_validation_integration(self):
        """Test code validation through rules engine."""
        code = """
def safe_function():
    return "safe"
"""

        result = self.rules_engine.validate_code(code)

        self.assertTrue(result.is_safe)

    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        from senti_os.core.faza16.spec_validator import SpecValidationResult
        from senti_os.core.faza16.code_safety_analyzer import CodeSafetyReport

        spec_result = SpecValidationResult(
            is_valid=True,
            spec_name="test",
            score=90.0,
        )

        code_result = CodeSafetyReport(
            is_safe=True,
            safety_score=85.0,
        )

        risk = self.rules_engine.calculate_risk_score(
            spec_result=spec_result,
            code_result=code_result,
        )

        self.assertIn("risk_score", risk)
        self.assertIn("risk_level", risk)
        self.assertLess(risk["risk_score"], 30.0)  # Should be low risk


class TestUpgradedKnowledgeValidation(unittest.TestCase):
    """Test upgraded Knowledge Validation Engine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_validator()

    def test_full_validation_pipeline(self):
        """Test full validation pipeline."""
        spec = """
# Objective
Test

## Architecture
Test

## Implementation
Test

## Testing
Test
"""

        code = """
def test_function():
    pass
"""

        module_spec = {
            "name": "test_module",
            "imports": [],
            "files": ["__init__.py"],
        }

        report = self.engine.run_full_validation(
            spec_text=spec,
            code_text=code,
            module_spec=module_spec,
            module_path="/home/pisarna/senti_system/modules/test",
        )

        self.assertIn("overall_status", report)
        self.assertIn("validations_performed", report)
        self.assertGreater(len(report["validations_performed"]), 0)


class TestFAZA31APIIntegration(unittest.TestCase):
    """Test FAZA 31 API integration points."""

    def test_select_model_api(self):
        """Test select_model API function."""
        from senti_os.core.faza16 import select_model

        task_profile = {
            "task_type": TaskType.GENERAL_QUERY,
        }

        # Should not raise
        result = select_model(task_profile)
        self.assertIsInstance(result, (str, type(None)))

    def test_run_full_validation_api(self):
        """Test run_full_validation API function."""
        from senti_os.core.faza16 import run_full_validation

        report = run_full_validation(
            spec_text="# Test",
            code_text="pass",
        )

        self.assertIsInstance(report, dict)
        self.assertIn("overall_status", report)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

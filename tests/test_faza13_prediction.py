"""
FAZA 13 - Prediction Engine Tests
Tests for prediction system integration

Tests:
- Basic prediction output
- Confidence and risk_score boundaries
- Event emission (PREDICTION_GENERATED)
- Episodic memory integration
- Rules validation
- Prediction service periodic operation
"""

import unittest
import time
from datetime import datetime
from pathlib import Path

from senti_core_module.senti_prediction import (
    PredictionEngine,
    PredictionManager,
    PredictionRules,
    PredictionService,
    PredictionResult,
    PredictionEvent
)


class MockMemoryManager:
    """Mock memory manager for testing."""

    def __init__(self):
        self.working_memory_data = []
        self.episodic_memory_data = []
        self.semantic_memory_data = []

    @property
    def working_memory(self):
        return self

    @property
    def episodic_memory(self):
        return self

    @property
    def semantic_memory(self):
        return self

    def get_all(self):
        """Mock working memory get_all."""
        return self.working_memory_data

    def recall_by_tags(self, tags):
        """Mock episodic memory recall."""
        return [item for item in self.episodic_memory_data if any(t in item.get("tags", []) for t in tags)]

    def query(self, query_str):
        """Mock semantic memory query."""
        return [item for item in self.semantic_memory_data if query_str.lower() in str(item).lower()]

    def store(self, event_type, data, tags):
        """Mock episodic memory store."""
        self.episodic_memory_data.append({
            "event_type": event_type,
            "data": data,
            "tags": tags
        })


class MockEventBus:
    """Mock event bus for testing."""

    def __init__(self):
        self.events = []

    def emit(self, event_type, payload):
        """Store emitted events."""
        self.events.append({
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        })

    def get_events_by_type(self, event_type):
        """Get events by type."""
        return [e for e in self.events if e["type"] == event_type]


class TestPredictionEngine(unittest.TestCase):
    """Test PredictionEngine low-level mechanism."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.engine = PredictionEngine(self.memory_manager)

    def test_predict_state_basic(self):
        """Test basic state prediction."""
        result = self.engine.predict_state({})

        self.assertIsInstance(result, PredictionResult)
        self.assertIn("state", result.prediction.lower())
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertGreaterEqual(result.risk_score, 0)
        self.assertLessEqual(result.risk_score, 100)
        self.assertEqual(result.source, "working")

    def test_predict_failure_no_patterns(self):
        """Test failure prediction with no patterns."""
        result = self.engine.predict_failure()

        self.assertIsInstance(result, PredictionResult)
        self.assertIn("failure", result.prediction.lower())
        self.assertEqual(result.source, "episodic")
        self.assertLess(result.risk_score, 20)

    def test_predict_failure_with_patterns(self):
        """Test failure prediction with error patterns."""
        # Add error patterns to memory
        self.memory_manager.episodic_memory_data = [
            {"tags": ["error"]},
            {"tags": ["failure"]},
            {"tags": ["error"]},
            {"tags": ["failure"]},
            {"tags": ["error"]},
            {"tags": ["failure"]},
            {"tags": ["error"]},
        ]

        result = self.engine.predict_failure()

        self.assertGreater(result.risk_score, 50)
        self.assertIn("high risk", result.prediction.lower())

    def test_predict_action(self):
        """Test action prediction."""
        result = self.engine.predict_action({"task": "test"})

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.source, "semantic")
        self.assertIsNotNone(result.prediction)

    def test_predict_user_behavior(self):
        """Test user behavior prediction."""
        actions = ["commit", "push", "commit", "push", "commit"]
        result = self.engine.predict_user_behavior(actions)

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.source, "hybrid")
        self.assertIn("commit", result.prediction.lower())

    def test_full_system_assessment(self):
        """Test comprehensive system assessment."""
        results = self.engine.full_system_assessment()

        self.assertIn("state", results)
        self.assertIn("failure", results)
        self.assertIn("action", results)
        self.assertIn("user", results)

        for result in results.values():
            self.assertIsInstance(result, PredictionResult)

    def test_confidence_boundaries(self):
        """Test that confidence is always in [0.0, 1.0]."""
        for _ in range(10):
            result = self.engine.predict_state({})
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

    def test_risk_score_boundaries(self):
        """Test that risk_score is always in [0, 100]."""
        for _ in range(10):
            result = self.engine.predict_failure()
            self.assertGreaterEqual(result.risk_score, 0)
            self.assertLessEqual(result.risk_score, 100)

    def test_prediction_stats(self):
        """Test prediction statistics."""
        # Generate some predictions
        self.engine.predict_state({})
        self.engine.predict_failure()
        self.engine.predict_action({"task": "test"})

        stats = self.engine.get_prediction_stats()

        self.assertEqual(stats["total_predictions"], 3)
        self.assertGreater(stats["avg_confidence"], 0.0)
        self.assertGreater(stats["avg_risk_score"], 0)
        self.assertIn("sources", stats)


class TestPredictionManager(unittest.TestCase):
    """Test PredictionManager high-level orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.manager = PredictionManager(self.memory_manager, self.event_bus)

    def test_predict_context(self):
        """Test context prediction."""
        result = self.manager.predict_context({"test": "data"})

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(self.manager.prediction_count, 1)

    def test_predict_failures(self):
        """Test failure prediction."""
        result = self.manager.predict_failures()

        self.assertIsInstance(result, PredictionResult)
        self.assertIsNotNone(self.manager.last_predictions.get("failure"))

    def test_predict_actions(self):
        """Test action prediction."""
        result = self.manager.predict_actions({"task": "optimize"})

        self.assertIsInstance(result, PredictionResult)
        self.assertIsNotNone(self.manager.last_predictions.get("action"))

    def test_full_system_prediction(self):
        """Test full system prediction."""
        results = self.manager.full_system_prediction()

        self.assertEqual(len(results), 4)
        self.assertIn("state", results)
        self.assertIn("failure", results)
        self.assertIn("action", results)
        self.assertIn("user", results)

    def test_event_emission(self):
        """Test PREDICTION_GENERATED event emission."""
        self.manager.predict_context({})

        events = self.event_bus.get_events_by_type("PREDICTION_GENERATED")
        self.assertEqual(len(events), 1)
        self.assertIn("category", events[0]["payload"])
        self.assertIn("prediction", events[0]["payload"])

    def test_episodic_memory_storage(self):
        """Test predictions are stored in episodic memory."""
        self.manager.predict_context({"test": "data"})

        stored = self.memory_manager.episodic_memory_data
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["event_type"], "PREDICTION")
        self.assertIn("prediction", stored[0]["tags"])

    def test_high_risk_storage(self):
        """Test high-risk predictions get special tag."""
        # Create high-risk scenario
        for _ in range(10):
            self.memory_manager.episodic_memory_data.append({"tags": ["error"]})

        self.manager.predict_failures()

        stored = self.memory_manager.episodic_memory_data
        high_risk_items = [item for item in stored if "high_risk" in item.get("tags", [])]
        self.assertGreater(len(high_risk_items), 0)

    def test_enable_disable(self):
        """Test enable/disable functionality."""
        self.manager.disable()
        self.assertFalse(self.manager.enabled)

        result = self.manager.predict_context({})
        self.assertEqual(result.prediction, "Prediction system disabled")

        self.manager.enable()
        self.assertTrue(self.manager.enabled)

    def test_trigger_handling(self):
        """Test trigger handling."""
        # Time tick trigger
        self.manager.handle_trigger("time_tick", {})
        self.assertGreater(self.manager.prediction_count, 0)

        # Event trigger
        count_before = self.manager.prediction_count
        self.manager.handle_trigger("event_trigger", {"event_type": "ERROR"})
        self.assertGreater(self.manager.prediction_count, count_before)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        self.manager.predict_context({})
        self.manager.predict_failures()

        stats = self.manager.get_statistics()

        self.assertEqual(stats["total_predictions"], 2)
        self.assertTrue(stats["enabled"])
        self.assertIn("engine_stats", stats)


class TestPredictionRules(unittest.TestCase):
    """Test PredictionRules validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules = PredictionRules()

    def test_validate_prediction_mode(self):
        """Test prediction mode validation."""
        self.assertTrue(self.rules.validate_prediction_mode("state"))
        self.assertTrue(self.rules.validate_prediction_mode("failure"))
        self.assertFalse(self.rules.validate_prediction_mode("invalid_mode"))

    def test_validate_context_data_size(self):
        """Test context data size validation."""
        small_context = {"test": "data"}
        self.assertTrue(self.rules.validate_context_data(small_context))

        # Create oversized context
        large_context = {"data": "x" * 2000}
        self.assertFalse(self.rules.validate_context_data(large_context))

    def test_validate_sensitive_data(self):
        """Test sensitive data detection."""
        sensitive_context = {"password": "secret123"}
        self.assertFalse(self.rules.validate_context_data(sensitive_context))

        safe_context = {"user": "test"}
        self.assertTrue(self.rules.validate_context_data(safe_context))

    def test_validate_prediction_result(self):
        """Test prediction result validation."""
        valid_result = PredictionResult(
            prediction="Test prediction",
            confidence=0.75,
            risk_score=50,
            source="working"
        )
        self.assertTrue(self.rules.validate_prediction_result(valid_result))

        # Invalid confidence
        invalid_confidence = PredictionResult(
            prediction="Test",
            confidence=1.5,
            risk_score=50,
            source="working"
        )
        self.assertFalse(self.rules.validate_prediction_result(invalid_confidence))

        # Invalid risk score
        invalid_risk = PredictionResult(
            prediction="Test",
            confidence=0.5,
            risk_score=150,
            source="working"
        )
        self.assertFalse(self.rules.validate_prediction_result(invalid_risk))

    def test_validate_full_operation(self):
        """Test comprehensive operation validation."""
        result = PredictionResult(
            prediction="Test",
            confidence=0.8,
            risk_score=30,
            source="working"
        )

        valid = self.rules.validate_full_operation(
            mode="state",
            context={"test": "data"},
            result=result
        )

        self.assertTrue(valid)
        self.assertEqual(len(self.rules.violations), 0)

    def test_get_validation_report(self):
        """Test validation report generation."""
        self.rules.validate_prediction_mode("invalid")

        report = self.rules.get_validation_report()

        self.assertTrue(report["has_violations"])
        self.assertEqual(report["violation_count"], 1)
        self.assertIn("allowed_modes", report)


class TestPredictionService(unittest.TestCase):
    """Test PredictionService OS-level service."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.prediction_manager = PredictionManager(self.memory_manager, self.event_bus)
        self.service = PredictionService(
            prediction_manager=self.prediction_manager,
            event_bus=self.event_bus,
            interval=1  # Short interval for testing
        )

    def test_service_start_stop(self):
        """Test service lifecycle."""
        self.assertFalse(self.service.is_running())

        self.service.start()
        self.assertTrue(self.service.is_running())

        self.service.stop()
        self.assertFalse(self.service.is_running())

    def test_manual_prediction(self):
        """Test manual prediction trigger."""
        result = self.service.manual_prediction("failure")

        self.assertIn("failure", result)
        self.assertIsInstance(result["failure"], PredictionResult)

    def test_get_statistics(self):
        """Test service statistics."""
        stats = self.service.get_statistics()

        self.assertIn("service", stats)
        self.assertIn("manager", stats)
        self.assertEqual(stats["service"]["running"], False)

    def test_set_interval(self):
        """Test interval modification."""
        self.service.set_interval(30)
        self.assertEqual(self.service.interval, 30)

        # Test minimum interval
        self.service.set_interval(5)
        self.assertEqual(self.service.interval, 10)  # Minimum is 10

    def test_reset_statistics(self):
        """Test statistics reset."""
        self.service.manual_prediction()
        self.service.reset_statistics()

        stats = self.service.get_statistics()
        self.assertEqual(stats["service"]["total_runs"], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for FAZA 13."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.prediction_manager = PredictionManager(self.memory_manager, self.event_bus)
        self.rules = PredictionRules()

    def test_full_prediction_workflow(self):
        """Test complete prediction workflow."""
        # Validate mode
        self.assertTrue(self.rules.validate_prediction_mode("state"))

        # Perform prediction
        result = self.prediction_manager.predict_context({"test": "workflow"})

        # Validate result
        self.assertTrue(self.rules.validate_prediction_result(result))

        # Check event emission
        events = self.event_bus.get_events_by_type("PREDICTION_GENERATED")
        self.assertEqual(len(events), 1)

        # Check memory storage
        stored = self.memory_manager.episodic_memory_data
        self.assertEqual(len(stored), 1)

    def test_high_risk_workflow(self):
        """Test high-risk prediction workflow."""
        # Create high-risk scenario
        for _ in range(10):
            self.memory_manager.episodic_memory_data.append({"tags": ["error"]})

        result = self.prediction_manager.predict_failures()

        # Should be high risk
        self.assertGreater(result.risk_score, 70)

        # Check for high_risk tag in storage
        stored = self.memory_manager.episodic_memory_data
        high_risk = [item for item in stored if "high_risk" in item.get("tags", [])]
        self.assertGreater(len(high_risk), 0)


if __name__ == "__main__":
    unittest.main()

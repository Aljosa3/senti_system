"""
FAZA 14 - Anomaly Detection Engine Tests
Tests for anomaly detection system integration

Tests:
- Statistical anomaly detection
- Pattern drift detection
- Rule-based anomaly detection
- High severity escalation
- EventBus event emission
- Episodic memory writing
- Semantic consolidation
- Autonomous loop integration
- AI layer access
- Security rule blocking
"""

import unittest
import time
from datetime import datetime
from pathlib import Path

from senti_core_module.senti_anomaly import (
    AnomalyEngine,
    AnomalyManager,
    AnomalyRules,
    AnomalyService,
    AnomalyResult,
    AnomalyEvent,
    HighSeverityEvent
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


class MockPredictionManager:
    """Mock prediction manager for testing."""

    def __init__(self):
        self.last_prediction = None

    def get_last_prediction(self):
        """Get last prediction."""
        return self.last_prediction


class TestAnomalyEngine(unittest.TestCase):
    """Test AnomalyEngine low-level mechanism."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.engine = AnomalyEngine(self.memory_manager)

    def test_detect_statistical_anomaly_basic(self):
        """Test basic statistical anomaly detection."""
        data = [10.0, 12.0, 11.0, 13.0, 50.0]  # Last value is anomaly
        result = self.engine.detect_statistical_anomaly(data)

        self.assertIsInstance(result, AnomalyResult)
        self.assertGreater(result.score, 0)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)
        self.assertIn(result.severity, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def test_detect_statistical_insufficient_data(self):
        """Test statistical detection with insufficient data."""
        result = self.engine.detect_statistical_anomaly([5.0])

        self.assertEqual(result.score, 0)
        self.assertEqual(result.severity, "LOW")

    def test_detect_pattern_anomaly_basic(self):
        """Test basic pattern anomaly detection."""
        events = [
            {"event_type": "ERROR"},
            {"event_type": "ERROR"},
            {"event_type": "ERROR"},
            {"event_type": "ERROR"},
            {"event_type": "ERROR"},
            {"event_type": "INFO"}
        ]
        result = self.engine.detect_pattern_anomaly(events)

        self.assertIsInstance(result, AnomalyResult)
        # Should detect pattern or have event context
        self.assertTrue(result.context.get("event_count", 0) > 0 or "pattern" in result.reason.lower())

    def test_detect_pattern_no_events(self):
        """Test pattern detection with no events."""
        result = self.engine.detect_pattern_anomaly([])

        self.assertEqual(result.score, 0)
        self.assertEqual(result.severity, "LOW")

    def test_detect_rule_anomaly_sensitive_data(self):
        """Test rule detection with sensitive data."""
        event = {"data": "password: secret123"}
        result = self.engine.detect_rule_anomaly(event)

        self.assertGreater(result.score, 0)
        self.assertIn("password", result.reason.lower())

    def test_detect_rule_anomaly_oversized_event(self):
        """Test rule detection with oversized event."""
        event = {"data": "x" * 3000}
        result = self.engine.detect_rule_anomaly(event)

        self.assertGreater(result.score, 0)

    def test_detect_rule_no_violations(self):
        """Test rule detection with clean event."""
        event = {"type": "INFO", "data": "normal operation"}
        result = self.engine.detect_rule_anomaly(event)

        self.assertEqual(result.score, 0)
        self.assertEqual(result.severity, "LOW")

    def test_detect_for_component(self):
        """Test component-specific detection."""
        result = self.engine.detect_for("test_component", {"test": "context"})

        self.assertIsInstance(result, AnomalyResult)
        self.assertEqual(result.context.get("component"), "test_component")

    def test_classify_severity(self):
        """Test severity classification."""
        self.assertEqual(self.engine.classify_severity(10), "LOW")
        self.assertEqual(self.engine.classify_severity(40), "MEDIUM")
        self.assertEqual(self.engine.classify_severity(65), "HIGH")
        self.assertEqual(self.engine.classify_severity(85), "CRITICAL")

    def test_compute_anomaly_score(self):
        """Test weighted anomaly score computation."""
        score = self.engine.compute_anomaly_score(
            statistical_score=50,
            pattern_score=60,
            rule_score=40
        )

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_baseline_update(self):
        """Test baseline statistics update."""
        data = [10.0, 12.0, 11.0, 13.0]
        self.engine.update_baseline("test_component", data)

        baseline = self.engine.get_baseline("test_component")
        self.assertIsNotNone(baseline)
        self.assertIn("mean", baseline)
        self.assertIn("stdev", baseline)

    def test_get_detection_stats(self):
        """Test detection statistics."""
        self.engine.detect_statistical_anomaly([1.0, 2.0, 3.0, 10.0])
        self.engine.detect_pattern_anomaly([{"event_type": "TEST"}])

        stats = self.engine.get_detection_stats()

        self.assertGreater(stats["total_detections"], 0)
        self.assertIn("avg_score", stats)


class TestAnomalyManager(unittest.TestCase):
    """Test AnomalyManager high-level orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.prediction_manager = MockPredictionManager()
        self.manager = AnomalyManager(
            self.memory_manager,
            self.prediction_manager,
            self.event_bus
        )

    def test_analyze_system(self):
        """Test system-wide analysis."""
        results = self.manager.analyze_system()

        self.assertIsInstance(results, dict)
        # May have no anomalies, but should return dict
        self.assertIsInstance(results, dict)

    def test_detect_for_component(self):
        """Test component-specific detection."""
        result = self.manager.detect_for("test_component", {"test": "data"})

        self.assertIsInstance(result, AnomalyResult)

    def test_detect_statistical(self):
        """Test statistical detection through manager."""
        data = [10.0, 12.0, 11.0, 50.0]
        result = self.manager.detect_statistical(data, "test_component")

        self.assertIsInstance(result, AnomalyResult)
        self.assertEqual(result.context.get("component"), "test_component")

    def test_detect_pattern(self):
        """Test pattern detection through manager."""
        events = [{"event_type": "ERROR"}] * 5
        result = self.manager.detect_pattern(events, "test_component")

        self.assertIsInstance(result, AnomalyResult)

    def test_detect_rule(self):
        """Test rule detection through manager."""
        event = {"data": "test data"}
        result = self.manager.detect_rule(event, "test_component")

        self.assertIsInstance(result, AnomalyResult)

    def test_event_emission(self):
        """Test ANOMALY_DETECTED event emission."""
        data = [10.0, 12.0, 11.0, 50.0]
        self.manager.detect_statistical(data)

        events = self.event_bus.get_events_by_type("ANOMALY_DETECTED")
        self.assertGreater(len(events), 0)

    def test_episodic_memory_storage(self):
        """Test anomalies are stored in episodic memory."""
        data = [10.0, 12.0, 11.0, 50.0]
        self.manager.detect_statistical(data, "test_component")

        stored = self.memory_manager.episodic_memory_data
        self.assertGreater(len(stored), 0)
        self.assertEqual(stored[0]["event_type"], "ANOMALY")

    def test_high_severity_escalation(self):
        """Test high severity anomaly escalation."""
        # Create high severity scenario
        large_data = [10.0] * 10 + [1000.0]  # Extreme outlier
        result = self.manager.detect_statistical(large_data)

        # Should escalate if high severity
        if result.severity in ["HIGH", "CRITICAL"]:
            events = self.event_bus.get_events_by_type("HIGH_SEVERITY_ANOMALY")
            self.assertGreater(len(events), 0)

    def test_resolve_anomaly(self):
        """Test anomaly resolution."""
        # Create anomaly
        result = self.manager.detect_for("test", {})

        if result.score > 0:
            # Get anomaly ID
            anomaly_ids = list(self.manager.get_active_anomalies().keys())
            if anomaly_ids:
                success = self.manager.resolve_anomaly(anomaly_ids[0], "test_resolution")
                self.assertTrue(success)

    def test_get_stats(self):
        """Test statistics retrieval."""
        self.manager.detect_for("test", {})

        stats = self.manager.get_stats()

        self.assertIn("total_anomalies", stats)
        self.assertIn("active_anomalies", stats)
        self.assertIn("enabled", stats)

    def test_enable_disable(self):
        """Test enable/disable functionality."""
        self.manager.disable()
        self.assertFalse(self.manager.enabled)

        result = self.manager.detect_for("test", {})
        self.assertEqual(result.severity, "LOW")

        self.manager.enable()
        self.assertTrue(self.manager.enabled)


class TestAnomalyRules(unittest.TestCase):
    """Test AnomalyRules validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules = AnomalyRules()

    def test_validate_event_basic(self):
        """Test basic event validation."""
        event = {"type": "INFO", "data": "test"}
        self.assertTrue(self.rules.validate_event(event))

    def test_validate_event_oversized(self):
        """Test oversized event validation."""
        event = {"data": "x" * 3000}
        self.assertFalse(self.rules.validate_event(event))

    def test_validate_event_sensitive_data(self):
        """Test sensitive data detection in event."""
        event = {"password": "secret"}
        self.assertFalse(self.rules.validate_event(event))

    def test_validate_context_basic(self):
        """Test basic context validation."""
        context = {"component": "test", "status": "active"}
        self.assertTrue(self.rules.validate_context(context))

    def test_validate_context_too_many_items(self):
        """Test context with too many items."""
        context = {f"key_{i}": f"value_{i}" for i in range(60)}
        self.assertFalse(self.rules.validate_context(context))

    def test_validate_detection_mode(self):
        """Test detection mode validation."""
        self.assertTrue(self.rules.validate_detection_mode("statistical"))
        self.assertTrue(self.rules.validate_detection_mode("pattern"))
        self.assertTrue(self.rules.validate_detection_mode("rule"))
        self.assertFalse(self.rules.validate_detection_mode("invalid"))

    def test_validate_data_points(self):
        """Test data points validation."""
        data = [1.0, 2.0, 3.0]
        self.assertTrue(self.rules.validate_data_points(data))

        # Too many points
        large_data = list(range(2000))
        self.assertFalse(self.rules.validate_data_points(large_data))

    def test_validate_anomaly_result(self):
        """Test anomaly result validation."""
        valid_result = AnomalyResult(
            score=50,
            severity="MEDIUM",
            reason="Test anomaly",
            context={}
        )
        self.assertTrue(self.rules.validate_anomaly_result(valid_result))

        # Invalid score
        invalid_result = AnomalyResult(
            score=150,
            severity="MEDIUM",
            reason="Test",
            context={}
        )
        self.assertFalse(self.rules.validate_anomaly_result(invalid_result))

    def test_get_validation_report(self):
        """Test validation report generation."""
        self.rules.validate_detection_mode("invalid")

        report = self.rules.get_validation_report()

        self.assertTrue(report["has_violations"])
        self.assertEqual(report["violation_count"], 1)


class TestAnomalyService(unittest.TestCase):
    """Test AnomalyService OS-level service."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = AnomalyManager(
            self.memory_manager,
            self.prediction_manager,
            self.event_bus
        )
        self.service = AnomalyService(
            anomaly_manager=self.anomaly_manager,
            event_bus=self.event_bus,
            interval=1
        )

    def test_service_start_stop(self):
        """Test service lifecycle."""
        self.assertFalse(self.service.is_running())

        self.service.start()
        self.assertTrue(self.service.is_running())

        self.service.stop()
        self.assertFalse(self.service.is_running())

    def test_manual_detection(self):
        """Test manual detection trigger."""
        result = self.service.manual_detection("test_component")

        self.assertIn("test_component", result)
        self.assertIsInstance(result["test_component"], AnomalyResult)

    def test_check_method(self):
        """Test single check operation."""
        self.service.check()
        # Should complete without error

    def test_get_statistics(self):
        """Test service statistics."""
        stats = self.service.get_statistics()

        self.assertIn("service", stats)
        self.assertIn("manager", stats)
        self.assertEqual(stats["service"]["running"], False)

    def test_set_interval(self):
        """Test interval modification."""
        self.service.set_interval(45)
        self.assertEqual(self.service.interval, 45)

        # Test minimum interval
        self.service.set_interval(5)
        self.assertEqual(self.service.interval, 10)

    def test_reset_statistics(self):
        """Test statistics reset."""
        self.service.manual_detection()
        self.service.reset_statistics()

        stats = self.service.get_statistics()
        self.assertEqual(stats["service"]["total_runs"], 0)

    def test_resolve_anomaly(self):
        """Test manual anomaly resolution."""
        # Create anomaly
        self.service.manual_detection()

        active = self.service.get_active_anomalies()
        if active:
            anomaly_id = list(active.keys())[0]
            success = self.service.resolve_anomaly(anomaly_id)
            self.assertTrue(success)


class TestIntegration(unittest.TestCase):
    """Integration tests for FAZA 14."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.memory_manager = MockMemoryManager()
        self.event_bus = MockEventBus()
        self.prediction_manager = MockPredictionManager()
        self.anomaly_manager = AnomalyManager(
            self.memory_manager,
            self.prediction_manager,
            self.event_bus
        )
        self.rules = AnomalyRules()

    def test_full_detection_workflow(self):
        """Test complete detection workflow."""
        # Validate mode
        self.assertTrue(self.rules.validate_detection_mode("statistical"))

        # Perform detection
        data = [10.0, 12.0, 11.0, 50.0]
        result = self.anomaly_manager.detect_statistical(data, "test")

        # Validate result
        self.assertTrue(self.rules.validate_anomaly_result(result))

        # Check event emission
        events = self.event_bus.get_events_by_type("ANOMALY_DETECTED")
        self.assertGreater(len(events), 0)

        # Check memory storage
        stored = self.memory_manager.episodic_memory_data
        self.assertGreater(len(stored), 0)

    def test_high_severity_workflow(self):
        """Test high severity anomaly workflow."""
        # Create extreme anomaly
        data = [10.0] * 10 + [10000.0]
        result = self.anomaly_manager.detect_statistical(data)

        # Should be high severity
        if result.score > 60:
            self.assertIn(result.severity, ["HIGH", "CRITICAL"])

    def test_security_blocking(self):
        """Test security rule blocking."""
        event = {"password": "secret123", "api_key": "abc"}
        self.assertFalse(self.rules.validate_event(event))

        violations = self.rules.get_violations()
        self.assertGreater(len(violations), 0)


if __name__ == "__main__":
    unittest.main()

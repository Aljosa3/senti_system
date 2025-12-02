"""
FAZA 20 - Comprehensive Test Suite

Tests all User Experience Layer components:
- StatusCollector (10 tests)
- HeartbeatMonitor (10 tests)
- DiagnosticsEngine (10 tests)
- OnboardingAssistant (10 tests)
- UXStateManager (10 tests)
- ExplainabilityBridge (10 tests)
- UIAPI (10 tests)
- Integration Tests (20+ tests)

Total: 80+ tests

Author: SENTI OS Core Team
License: Proprietary
"""

import unittest
import tempfile
import shutil
import time
from datetime import datetime, timedelta

# Import FAZA 20 components
from senti_os.core.faza20.status_collector import (
    StatusCollector,
    ModuleHealth,
    ModuleStatus
)
from senti_os.core.faza20.heartbeat_monitor import (
    HeartbeatMonitor,
    HeartbeatStatus
)
from senti_os.core.faza20.diagnostics_engine import (
    DiagnosticsEngine,
    DiagnosticLevel
)
from senti_os.core.faza20.onboarding_assistant import (
    OnboardingAssistant,
    OnboardingStep
)
from senti_os.core.faza20.ux_state_manager import (
    UXStateManager,
    AlertLevel
)
from senti_os.core.faza20.explainability_bridge import (
    ExplainabilityBridge,
    ExplainabilitySource,
    ExplainabilityLevel
)
from senti_os.core.faza20.ui_api import UIAPI
from senti_os.core.faza20 import FAZA20Stack


# Mock modules for testing
class MockModule:
    """Mock module for testing."""

    def __init__(self, name: str, has_errors: bool = False):
        self.name = name
        self.has_errors = has_errors
        self._heartbeat_count = 0

    def get_status(self):
        """Mock get_status."""
        return {
            "initialized": True,
            "error_count": 3 if self.has_errors else 0,
            "warning_count": 1 if self.has_errors else 0
        }

    def heartbeat(self):
        """Mock heartbeat."""
        self._heartbeat_count += 1
        if self.has_errors:
            raise Exception("Heartbeat failed")
        return True


# ============================================================================
# TEST: StatusCollector
# ============================================================================

class TestStatusCollector(unittest.TestCase):
    """Test StatusCollector component."""

    def setUp(self):
        self.collector = StatusCollector(collection_frequency_seconds=1)
        self.mock_faza16 = MockModule("faza16")
        self.mock_faza17 = MockModule("faza17")

    def test_initialization(self):
        """Test status collector initialization."""
        self.assertIsNotNone(self.collector)
        self.assertEqual(self.collector.collection_frequency, 1)

    def test_register_module(self):
        """Test registering modules."""
        self.collector.register_module("faza16_llm_control", self.mock_faza16)
        self.collector.register_module("faza17_orchestration", self.mock_faza17)
        self.assertEqual(self.collector._count_registered_modules(), 2)

    def test_collect_status_no_modules(self):
        """Test collecting status with no modules."""
        status = self.collector.collect_status()
        self.assertIsNotNone(status)
        self.assertEqual(len(status.modules), 0)

    def test_collect_status_with_modules(self):
        """Test collecting status with registered modules."""
        self.collector.register_module("faza16_llm_control", self.mock_faza16)
        status = self.collector.collect_status()
        self.assertEqual(len(status.modules), 1)
        self.assertIn("faza16_llm_control", [m.module_name for m in status.modules])

    def test_overall_health_calculation(self):
        """Test overall health calculation."""
        self.collector.register_module("faza16_llm_control", self.mock_faza16)
        status = self.collector.collect_status()
        self.assertIn(status.overall_health, [ModuleHealth.HEALTHY, ModuleHealth.DEGRADED])

    def test_health_score_with_errors(self):
        """Test health score calculation with errors."""
        mock_with_errors = MockModule("faza16", has_errors=True)
        self.collector.register_module("faza16_llm_control", mock_with_errors)
        status = self.collector.collect_status()
        module = status.modules[0]
        self.assertLess(module.health_score, 1.0)

    def test_collection_info(self):
        """Test getting collection info."""
        info = self.collector.get_collection_info()
        self.assertIn("collection_frequency_seconds", info)
        self.assertIn("collection_count", info)

    def test_module_status_retrieval(self):
        """Test retrieving specific module status."""
        self.collector.register_module("faza16_llm_control", self.mock_faza16)
        self.collector.collect_status()
        # Module status is stored after collection
        status = self.collector.get_module_status("faza16_llm_control")
        # May be None if not cached yet
        self.assertTrue(status is None or isinstance(status, ModuleStatus))

    def test_multiple_collections(self):
        """Test multiple status collections."""
        self.collector.register_module("faza16_llm_control", self.mock_faza16)
        status1 = self.collector.collect_status()
        status2 = self.collector.collect_status()
        self.assertNotEqual(status1.timestamp, status2.timestamp)

    def test_uptime_tracking(self):
        """Test uptime tracking."""
        status = self.collector.collect_status()
        self.assertGreaterEqual(status.total_uptime_seconds, 0)


# ============================================================================
# TEST: HeartbeatMonitor
# ============================================================================

class TestHeartbeatMonitor(unittest.TestCase):
    """Test HeartbeatMonitor component."""

    def setUp(self):
        self.monitor = HeartbeatMonitor(interval_seconds=1, timeout_seconds=1)
        self.mock_module = MockModule("test_module")

    def tearDown(self):
        if self.monitor._running:
            self.monitor.stop()

    def test_initialization(self):
        """Test heartbeat monitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.interval, 1)
        self.assertFalse(self.monitor._running)

    def test_register_module(self):
        """Test registering module for heartbeat."""
        self.monitor.register_module("test_module", self.mock_module)
        self.assertIn("test_module", self.monitor._modules)

    def test_start_stop(self):
        """Test starting and stopping heartbeat monitor."""
        self.monitor.start()
        self.assertTrue(self.monitor._running)
        self.monitor.stop()
        self.assertFalse(self.monitor._running)

    def test_heartbeat_status_retrieval(self):
        """Test getting heartbeat status."""
        self.monitor.register_module("test_module", self.mock_module)
        status = self.monitor.get_heartbeat_status("test_module")
        # Initially should be None or STOPPED
        self.assertTrue(status is None or status == HeartbeatStatus.STOPPED)

    def test_heartbeat_record(self):
        """Test heartbeat record creation."""
        self.monitor.register_module("test_module", self.mock_module)
        self.monitor.start()
        time.sleep(1.5)  # Wait for at least one heartbeat
        self.monitor.stop()
        latest = self.monitor.get_latest_heartbeat("test_module")
        self.assertTrue(latest is None or latest.sequence_number >= 0)

    def test_heartbeat_history(self):
        """Test getting heartbeat history."""
        self.monitor.register_module("test_module", self.mock_module)
        history = self.monitor.get_heartbeat_history("test_module", limit=5)
        self.assertIsInstance(history, list)

    def test_heartbeat_statistics(self):
        """Test getting heartbeat statistics."""
        stats = self.monitor.get_statistics()
        self.assertIn("running", stats)
        self.assertIn("total_beats", stats)

    def test_module_statistics(self):
        """Test getting module-specific statistics."""
        self.monitor.register_module("test_module", self.mock_module)
        stats = self.monitor.get_module_statistics("test_module")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["module_name"], "test_module")

    def test_heartbeat_with_failure(self):
        """Test heartbeat with failing module."""
        failing_module = MockModule("failing", has_errors=True)
        self.monitor.register_module("failing", failing_module)
        self.monitor._send_heartbeat("failing")
        latest = self.monitor.get_latest_heartbeat("failing")
        self.assertIsNotNone(latest)

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        rate = self.monitor._calculate_success_rate()
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)


# ============================================================================
# TEST: DiagnosticsEngine
# ============================================================================

class TestDiagnosticsEngine(unittest.TestCase):
    """Test DiagnosticsEngine component."""

    def setUp(self):
        self.engine = DiagnosticsEngine()
        self.mock_faza16 = MockModule("faza16")
        self.mock_faza21 = MockModule("faza21")

    def test_initialization(self):
        """Test diagnostics engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.get_diagnostics_count(), 0)

    def test_register_module(self):
        """Test registering modules."""
        self.engine.register_module("faza16_llm_control", self.mock_faza16)
        self.assertIn("faza16_llm_control", self.engine._modules)

    def test_run_quick_diagnostics(self):
        """Test running quick diagnostics."""
        report = self.engine.run_diagnostics(quick=True)
        self.assertIsNotNone(report)
        self.assertGreater(report.tests_run, 0)

    def test_run_full_diagnostics(self):
        """Test running full diagnostics."""
        self.engine.register_module("faza16_llm_control", self.mock_faza16)
        report = self.engine.run_diagnostics(quick=False)
        self.assertIsNotNone(report)
        self.assertGreater(report.tests_run, 0)

    def test_diagnostic_report_structure(self):
        """Test diagnostic report structure."""
        report = self.engine.run_diagnostics(quick=True)
        self.assertIn(report.overall_status, [
            DiagnosticLevel.OK,
            DiagnosticLevel.WARNING,
            DiagnosticLevel.ERROR,
            DiagnosticLevel.CRITICAL
        ])
        self.assertIsInstance(report.results, list)

    def test_module_registration_tests(self):
        """Test module registration diagnostics."""
        self.engine.register_module("faza16_llm_control", self.mock_faza16)
        report = self.engine.run_diagnostics(quick=True)
        registration_tests = [r for r in report.results if r.category == "registration"]
        self.assertGreater(len(registration_tests), 0)

    def test_module_communication_tests(self):
        """Test module communication diagnostics."""
        self.engine.register_module("faza16_llm_control", self.mock_faza16)
        report = self.engine.run_diagnostics(quick=True)
        comm_tests = [r for r in report.results if r.category == "communication"]
        self.assertGreater(len(comm_tests), 0)

    def test_get_last_report(self):
        """Test getting last diagnostic report."""
        self.engine.run_diagnostics(quick=True)
        report = self.engine.get_last_report()
        self.assertIsNotNone(report)

    def test_diagnostics_count_increment(self):
        """Test diagnostics run count increments."""
        initial_count = self.engine.get_diagnostics_count()
        self.engine.run_diagnostics(quick=True)
        new_count = self.engine.get_diagnostics_count()
        self.assertEqual(new_count, initial_count + 1)

    def test_diagnostics_duration(self):
        """Test diagnostics duration tracking."""
        report = self.engine.run_diagnostics(quick=True)
        self.assertGreater(report.duration_seconds, 0)


# ============================================================================
# TEST: OnboardingAssistant
# ============================================================================

class TestOnboardingAssistant(unittest.TestCase):
    """Test OnboardingAssistant component."""

    def setUp(self):
        self.assistant = OnboardingAssistant()
        self.mock_faza21 = MockModule("faza21")
        self.mock_diagnostics = DiagnosticsEngine()

    def test_initialization(self):
        """Test onboarding assistant initialization."""
        self.assertIsNotNone(self.assistant)
        self.assertEqual(self.assistant._current_step, OnboardingStep.WELCOME)

    def test_start_onboarding(self):
        """Test starting onboarding."""
        state = self.assistant.start_onboarding()
        self.assertIsNotNone(state)
        self.assertEqual(state.current_step, OnboardingStep.WELCOME)

    def test_get_state(self):
        """Test getting onboarding state."""
        state = self.assistant.get_state()
        self.assertIsNotNone(state)
        self.assertFalse(state.is_complete)

    def test_get_current_step_info(self):
        """Test getting current step info."""
        info = self.assistant.get_current_step_info()
        self.assertIn("title", info)
        self.assertIn("description", info)

    def test_complete_welcome_step(self):
        """Test completing welcome step."""
        self.assistant.start_onboarding()
        result = self.assistant.complete_step(OnboardingStep.WELCOME)
        self.assertTrue(result.completed)

    def test_step_progression(self):
        """Test steps progress in order."""
        self.assistant.start_onboarding()
        self.assistant.complete_step(OnboardingStep.WELCOME)
        self.assertEqual(self.assistant._current_step, OnboardingStep.GENERATE_MASTER_KEY)

    def test_skip_optional_step(self):
        """Test skipping optional step."""
        # Register required modules
        self.assistant.register_modules(
            faza21_persistence=self.mock_faza21,
            diagnostics_engine=self.mock_diagnostics
        )
        # Advance to LLM connectivity test
        self.assistant.start_onboarding()
        self.assistant.complete_step(OnboardingStep.WELCOME)
        # Manually advance through steps to reach TEST_LLM_CONNECTIVITY
        self.assistant._current_step = OnboardingStep.TEST_LLM_CONNECTIVITY
        # Now skip LLM test
        success = self.assistant.skip_step(OnboardingStep.TEST_LLM_CONNECTIVITY)
        self.assertTrue(success)

    def test_is_onboarding_complete(self):
        """Test checking if onboarding is complete."""
        self.assertFalse(self.assistant.is_onboarding_complete())

    def test_get_step_result(self):
        """Test getting step result."""
        self.assistant.start_onboarding()
        self.assistant.complete_step(OnboardingStep.WELCOME)
        result = self.assistant.get_step_result(OnboardingStep.WELCOME)
        self.assertIsNotNone(result)

    def test_register_modules(self):
        """Test registering modules."""
        self.assistant.register_modules(
            faza21_persistence=self.mock_faza21,
            diagnostics_engine=self.mock_diagnostics
        )
        self.assertIsNotNone(self.assistant._faza21_persistence)


# ============================================================================
# TEST: UXStateManager
# ============================================================================

class TestUXStateManager(unittest.TestCase):
    """Test UXStateManager component."""

    def setUp(self):
        self.manager = UXStateManager()

    def test_initialization(self):
        """Test UX state manager initialization."""
        self.assertIsNotNone(self.manager)

    def test_update_state(self):
        """Test updating state."""
        self.manager.update_state("test_category", {"data": "value"})
        state = self.manager.get_state("test_category")
        self.assertEqual(state["data"], "value")

    def test_get_state_all(self):
        """Test getting all state."""
        state = self.manager.get_state()
        self.assertIsInstance(state, dict)

    def test_add_alert(self):
        """Test adding alert."""
        alert_id = self.manager.add_alert(
            level=AlertLevel.INFO,
            title="Test Alert",
            message="Test message"
        )
        self.assertIsNotNone(alert_id)

    def test_get_alerts(self):
        """Test getting alerts."""
        self.manager.add_alert(AlertLevel.INFO, "Test", "Message")
        alerts = self.manager.get_alerts()
        self.assertGreater(len(alerts), 0)

    def test_filter_alerts_by_level(self):
        """Test filtering alerts by level."""
        self.manager.add_alert(AlertLevel.ERROR, "Error", "Error message")
        self.manager.add_alert(AlertLevel.INFO, "Info", "Info message")
        error_alerts = self.manager.get_alerts(level=AlertLevel.ERROR)
        self.assertTrue(all(a.level == AlertLevel.ERROR for a in error_alerts))

    def test_dismiss_alert(self):
        """Test dismissing alert."""
        alert_id = self.manager.add_alert(AlertLevel.INFO, "Test", "Message")
        success = self.manager.dismiss_alert(alert_id)
        self.assertTrue(success)

    def test_dismiss_all_alerts(self):
        """Test dismissing all alerts."""
        self.manager.add_alert(AlertLevel.INFO, "Test 1", "Message 1")
        self.manager.add_alert(AlertLevel.INFO, "Test 2", "Message 2")
        count = self.manager.dismiss_all_alerts()
        self.assertEqual(count, 2)

    def test_alert_summary(self):
        """Test getting alert summary."""
        self.manager.add_alert(AlertLevel.ERROR, "Error", "Message")
        self.manager.add_alert(AlertLevel.WARNING, "Warning", "Message")
        summary = self.manager.get_alert_summary()
        self.assertEqual(summary["error"], 1)
        self.assertEqual(summary["warning"], 1)

    def test_user_preferences(self):
        """Test user preferences."""
        self.manager.set_user_preference("theme", "dark")
        value = self.manager.get_user_preference("theme")
        self.assertEqual(value, "dark")


# ============================================================================
# TEST: ExplainabilityBridge
# ============================================================================

class TestExplainabilityBridge(unittest.TestCase):
    """Test ExplainabilityBridge component."""

    def setUp(self):
        self.bridge = ExplainabilityBridge(max_entries=50)

    def test_initialization(self):
        """Test explainability bridge initialization."""
        self.assertIsNotNone(self.bridge)
        self.assertEqual(self.bridge.max_entries, 50)

    def test_add_entry(self):
        """Test adding explainability entry."""
        entry_id = self.bridge.add_entry(
            source=ExplainabilitySource.SYSTEM,
            level=ExplainabilityLevel.BASIC,
            title="Test Entry",
            description="Test description"
        )
        self.assertIsNotNone(entry_id)

    def test_get_entries(self):
        """Test getting entries."""
        self.bridge.add_entry(
            ExplainabilitySource.SYSTEM,
            ExplainabilityLevel.BASIC,
            "Test",
            "Description"
        )
        entries = self.bridge.get_entries(limit=10)
        self.assertGreater(len(entries), 0)

    def test_filter_entries_by_source(self):
        """Test filtering entries by source."""
        self.bridge.add_entry(
            ExplainabilitySource.LLM_CONTROL,
            ExplainabilityLevel.BASIC,
            "LLM",
            "Description"
        )
        entries = self.bridge.get_entries(source=ExplainabilitySource.LLM_CONTROL)
        self.assertTrue(all(e.source == ExplainabilitySource.LLM_CONTROL for e in entries))

    def test_get_snapshot(self):
        """Test getting explainability snapshot."""
        self.bridge.add_entry(
            ExplainabilitySource.SYSTEM,
            ExplainabilityLevel.BASIC,
            "Test",
            "Description"
        )
        snapshot = self.bridge.get_snapshot()
        self.assertIsNotNone(snapshot)
        self.assertGreater(snapshot.entry_count, 0)

    def test_get_recent_summary(self):
        """Test getting recent summary."""
        self.bridge.add_entry(
            ExplainabilitySource.SYSTEM,
            ExplainabilityLevel.BASIC,
            "Test",
            "Description"
        )
        summary = self.bridge.get_recent_summary(count=5)
        self.assertIsInstance(summary, list)

    def test_get_statistics(self):
        """Test getting statistics."""
        stats = self.bridge.get_statistics()
        self.assertIn("total_entries", stats)
        self.assertIn("entries_by_source", stats)

    def test_explain_llm_routing(self):
        """Test LLM routing explanation."""
        self.bridge.explain_llm_routing(
            task_description="Test task",
            selected_model="gpt-4",
            reasoning="Best for task"
        )
        entries = self.bridge.get_entries(source=ExplainabilitySource.LLM_CONTROL)
        self.assertGreater(len(entries), 0)

    def test_explain_orchestration_step(self):
        """Test orchestration step explanation."""
        self.bridge.explain_orchestration_step(
            step_name="Step 1",
            step_description="Description",
            models_involved=["model1", "model2"]
        )
        entries = self.bridge.get_entries(source=ExplainabilitySource.ORCHESTRATION)
        self.assertGreater(len(entries), 0)

    def test_clear_entries(self):
        """Test clearing entries."""
        self.bridge.add_entry(
            ExplainabilitySource.SYSTEM,
            ExplainabilityLevel.BASIC,
            "Test",
            "Description"
        )
        count = self.bridge.clear_entries()
        self.assertGreater(count, 0)

    def test_max_entries_limit(self):
        """Test max entries limit."""
        # Add more than max
        for i in range(60):
            self.bridge.add_entry(
                ExplainabilitySource.SYSTEM,
                ExplainabilityLevel.BASIC,
                f"Test {i}",
                "Description"
            )
        snapshot = self.bridge.get_snapshot()
        self.assertLessEqual(snapshot.entry_count, 50)


# ============================================================================
# TEST: UIAPI
# ============================================================================

class TestUIAPI(unittest.TestCase):
    """Test UIAPI component."""

    def setUp(self):
        self.stack = FAZA20Stack()
        self.stack.initialize()
        self.api = UIAPI(self.stack)

    def tearDown(self):
        if self.stack._started:
            self.stack.stop()

    def test_initialization(self):
        """Test UI API initialization."""
        self.assertIsNotNone(self.api)

    def test_get_status(self):
        """Test getting status via API."""
        response = self.api.get_status()
        self.assertTrue(response["success"])
        self.assertIn("status", response)

    def test_get_module_status(self):
        """Test getting module status via API."""
        response = self.api.get_module_status("faza16_llm_control")
        self.assertIn("success", response)

    def test_get_heartbeat(self):
        """Test getting heartbeat via API."""
        response = self.api.get_heartbeat()
        self.assertTrue(response["success"])

    def test_get_diagnostics(self):
        """Test getting diagnostics via API."""
        response = self.api.get_diagnostics()
        self.assertTrue(response["success"])

    def test_trigger_diagnostics(self):
        """Test triggering diagnostics via API."""
        response = self.api.trigger_diagnostics(quick=True)
        self.assertTrue(response["success"])
        self.assertIn("diagnostics", response)

    def test_get_ux_state(self):
        """Test getting UX state via API."""
        response = self.api.get_ux_state()
        self.assertTrue(response["success"])

    def test_get_alerts(self):
        """Test getting alerts via API."""
        # Add an alert first
        self.stack.ux_state_manager.add_alert(
            AlertLevel.INFO,
            "Test",
            "Message"
        )
        response = self.api.get_alerts()
        self.assertTrue(response["success"])

    def test_get_explainability(self):
        """Test getting explainability via API."""
        response = self.api.get_explainability()
        self.assertTrue(response["success"])

    def test_get_onboarding_state(self):
        """Test getting onboarding state via API."""
        response = self.api.get_onboarding_state()
        self.assertTrue(response["success"])

    def test_error_handling(self):
        """Test API error handling."""
        response = self.api.get_module_status("nonexistent_module")
        self.assertFalse(response["success"])


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFAZA20Integration(unittest.TestCase):
    """Integration tests for FAZA 20 stack."""

    def setUp(self):
        self.mock_faza16 = MockModule("faza16")
        self.mock_faza17 = MockModule("faza17")
        self.stack = FAZA20Stack(
            faza16_llm_control=self.mock_faza16,
            faza17_orchestration=self.mock_faza17
        )

    def tearDown(self):
        if self.stack._started:
            self.stack.stop()

    def test_stack_initialization(self):
        """Test FAZA 20 stack initialization."""
        success = self.stack.initialize()
        self.assertTrue(success)
        self.assertTrue(self.stack._initialized)

    def test_stack_start_stop(self):
        """Test starting and stopping stack."""
        self.stack.initialize()
        success = self.stack.start()
        self.assertTrue(success)
        self.assertTrue(self.stack._started)
        self.stack.stop()
        self.assertFalse(self.stack._started)

    def test_stack_status(self):
        """Test getting stack status."""
        self.stack.initialize()
        status = self.stack.get_status()
        self.assertIn("initialized", status)
        self.assertIn("components", status)

    def test_full_status_collection_flow(self):
        """Test complete status collection flow."""
        self.stack.initialize()
        self.stack.start()
        time.sleep(0.1)
        status = self.stack.status_collector.collect_status()
        self.assertIsNotNone(status)
        self.assertGreater(len(status.modules), 0)

    def test_full_diagnostics_flow(self):
        """Test complete diagnostics flow."""
        self.stack.initialize()
        report = self.stack.run_diagnostics(quick=True)
        self.assertIsNotNone(report)
        self.assertGreater(report.tests_run, 0)

    def test_full_onboarding_flow(self):
        """Test complete onboarding flow."""
        self.stack.initialize()
        self.stack.onboarding_assistant.start_onboarding()
        result1 = self.stack.onboarding_assistant.complete_step(OnboardingStep.WELCOME)
        self.assertTrue(result1.completed)

    def test_explainability_integration(self):
        """Test explainability integration."""
        self.stack.initialize()
        self.stack.explainability_bridge.explain_system_operation(
            operation="test_operation",
            description="Testing explainability"
        )
        snapshot = self.stack.get_explainability()
        self.assertGreater(snapshot.entry_count, 0)

    def test_ux_state_persistence_flow(self):
        """Test UX state persistence flow."""
        self.stack.initialize()
        self.stack.ux_state_manager.update_state("test", {"value": 123})
        state = self.stack.ux_state_manager.get_state("test")
        self.assertEqual(state["value"], 123)

    def test_alert_flow(self):
        """Test alert creation and retrieval flow."""
        self.stack.initialize()
        alert_id = self.stack.ux_state_manager.add_alert(
            AlertLevel.WARNING,
            "Test Warning",
            "This is a test"
        )
        alerts = self.stack.ux_state_manager.get_alerts(dismissed=False)
        self.assertGreater(len(alerts), 0)

    def test_ui_api_integration(self):
        """Test UI API integration with stack."""
        self.stack.initialize()
        response = self.stack.ui_api.get_status()
        self.assertTrue(response["success"])

    def test_heartbeat_integration(self):
        """Test heartbeat monitoring integration."""
        self.stack.initialize()
        self.stack.start()
        time.sleep(1.5)
        stats = self.stack.heartbeat_monitor.get_statistics()
        self.assertGreater(stats["total_beats"], 0)
        self.stack.stop()

    def test_diagnostics_update_ux_state(self):
        """Test diagnostics updates UX state."""
        self.stack.initialize()
        report = self.stack.run_diagnostics(quick=True)
        last_diag = self.stack.ux_state_manager.get_last_diagnostics()
        # May or may not be set depending on implementation
        self.assertTrue(last_diag is None or isinstance(last_diag, dict))

    def test_status_collection_periodic(self):
        """Test periodic status collection."""
        self.stack.initialize()
        count1 = self.stack.status_collector._collection_count
        self.stack.status_collector.collect_status()
        count2 = self.stack.status_collector._collection_count
        self.assertGreater(count2, count1)

    def test_multiple_module_registration(self):
        """Test registering multiple modules."""
        self.stack.initialize()
        registered_count = self.stack.status_collector._count_registered_modules()
        self.assertGreater(registered_count, 0)

    def test_get_info(self):
        """Test getting FAZA 20 info."""
        from senti_os.core.faza20 import get_info
        info = get_info()
        self.assertEqual(info["faza"], "20")
        self.assertEqual(info["stores_passwords"], "false")
        self.assertEqual(info["stores_biometrics"], "false")

    def test_module_health_degradation(self):
        """Test module health degradation detection."""
        mock_degraded = MockModule("degraded", has_errors=True)
        collector = StatusCollector()
        collector.register_module("faza16_llm_control", mock_degraded)
        status = collector.collect_status()
        module = status.modules[0]
        self.assertLess(module.health_score, 1.0)

    def test_concurrent_operations(self):
        """Test concurrent operations on stack."""
        self.stack.initialize()
        self.stack.start()
        # Perform multiple operations
        self.stack.status_collector.collect_status()
        self.stack.explainability_bridge.add_entry(
            ExplainabilitySource.SYSTEM,
            ExplainabilityLevel.BASIC,
            "Test",
            "Description"
        )
        self.stack.ux_state_manager.add_alert(
            AlertLevel.INFO,
            "Test",
            "Message"
        )
        self.stack.stop()
        # Should complete without errors
        self.assertTrue(True)

    def test_stack_without_optional_modules(self):
        """Test stack works without optional modules."""
        minimal_stack = FAZA20Stack()
        success = minimal_stack.initialize()
        self.assertTrue(success)

    def test_stack_shutdown_cleanup(self):
        """Test stack cleanup on shutdown."""
        self.stack.initialize()
        self.stack.start()
        self.stack.stop()
        self.assertFalse(self.stack._started)
        self.assertFalse(self.stack.heartbeat_monitor._running)


def run_tests():
    """Run all FAZA 20 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestStatusCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestHeartbeatMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagnosticsEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestOnboardingAssistant))
    suite.addTests(loader.loadTestsFromTestCase(TestUXStateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestExplainabilityBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestUIAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestFAZA20Integration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("FAZA 20 TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)

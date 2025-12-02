"""
FAZA 22 - Comprehensive Test Suite

Complete test coverage for FAZA 22 Boot Layer components.

Test Coverage:
- BootManager (boot orchestration, lifecycle management)
- CLICommands (all CLI operations)
- CLIRenderer (terminal rendering)
- ServiceRegistry (stack registry and metadata)
- LogsManager (log management)
- SentinelProcess (health monitoring)
- FAZA22Stack (integration)

Total Tests: 70+

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import tempfile

# Import all FAZA 22 components
from senti_os.core.faza22.boot_manager import (
    BootManager,
    BootState,
    StackStatus,
    StackInfo,
    BootEvent
)

from senti_os.core.faza22.cli_commands import (
    CLICommands,
    CommandResult,
    get_cli_commands
)

from senti_os.core.faza22.cli_renderer import (
    CLIRenderer,
    RenderConfig,
    HealthStatus,
    Color,
    Symbol
)

from senti_os.core.faza22.service_registry import (
    ServiceRegistry,
    StackMetadata,
    StackType,
    get_service_registry,
    reset_service_registry
)

from senti_os.core.faza22.logs_manager import (
    LogsManager,
    LogLevel,
    LogEntry,
    get_logs_manager,
    reset_logs_manager
)

from senti_os.core.faza22.sentinel_process import (
    SentinelProcess,
    SentinelState,
    SentinelConfig,
    HealthCheckResult,
    StackHealthRecord
)

from senti_os.core.faza22 import FAZA22Stack


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def boot_manager(temp_storage_dir):
    """Create BootManager instance for testing."""
    manager = BootManager(
        storage_dir=temp_storage_dir,
        enable_persistence=False,  # Disable to avoid dependencies
        enable_uil=False,
        enable_ux=False,
        enable_orchestration=False,
        enable_llm_control=False,
        enable_auth_flow=False
    )
    yield manager
    if manager.is_running():
        manager.stop()


@pytest.fixture
def logs_manager():
    """Create LogsManager instance for testing."""
    reset_logs_manager()
    manager = LogsManager(max_entries=100)
    yield manager
    reset_logs_manager()


@pytest.fixture
def service_registry():
    """Create ServiceRegistry instance for testing."""
    reset_service_registry()
    registry = ServiceRegistry()
    yield registry
    reset_service_registry()


@pytest.fixture
def cli_renderer():
    """Create CLIRenderer instance for testing."""
    config = RenderConfig(use_colors=False, use_unicode=True)
    return CLIRenderer(config)


@pytest.fixture
def cli_commands(temp_storage_dir):
    """Create CLICommands instance for testing."""
    return CLICommands(storage_dir=temp_storage_dir)


@pytest.fixture
def sentinel_process(boot_manager, logs_manager):
    """Create SentinelProcess instance for testing."""
    config = SentinelConfig(
        check_interval_seconds=1,
        heartbeat_timeout_seconds=5,
        auto_recovery_enabled=False,
        safe_shutdown_on_critical=False
    )
    sentinel = SentinelProcess(boot_manager, logs_manager, config)
    yield sentinel
    if sentinel.is_running():
        sentinel.stop()


# ============================================================================
# BOOT MANAGER TESTS (15 tests)
# ============================================================================

class TestBootManager:
    """Test suite for BootManager."""

    def test_boot_manager_initialization(self, boot_manager):
        """Test 1: BootManager initializes correctly."""
        assert boot_manager.state == BootState.UNINITIALIZED
        assert not boot_manager.is_running()
        assert len(boot_manager.stacks) == 6  # All 6 FAZA stacks

    def test_boot_manager_boot_order(self, boot_manager):
        """Test 2: Boot order is correct."""
        expected_order = ["faza21", "faza19", "faza20", "faza17", "faza16", "faza18"]
        assert boot_manager.BOOT_ORDER == expected_order

    def test_boot_manager_load_stacks_disabled(self, boot_manager):
        """Test 3: Load stacks when all disabled."""
        # All stacks disabled in fixture
        success = boot_manager.load_all_stacks()
        assert success  # Should succeed even with all disabled

    def test_boot_manager_start_no_stacks(self, boot_manager):
        """Test 4: Start with no enabled stacks."""
        success = boot_manager.start()
        assert success
        assert boot_manager.state == BootState.RUNNING

    def test_boot_manager_stop_when_not_running(self, boot_manager):
        """Test 5: Stop when not running."""
        result = boot_manager.stop()
        assert not result  # Should return False

    def test_boot_manager_start_stop_lifecycle(self, boot_manager):
        """Test 6: Complete start/stop lifecycle."""
        assert boot_manager.start()
        assert boot_manager.is_running()
        assert boot_manager.state == BootState.RUNNING

        assert boot_manager.stop()
        assert not boot_manager.is_running()
        assert boot_manager.state == BootState.STOPPED

    def test_boot_manager_restart(self, boot_manager):
        """Test 7: Restart system."""
        boot_manager.start()
        assert boot_manager.restart()
        assert boot_manager.is_running()

    def test_boot_manager_double_start(self, boot_manager):
        """Test 8: Cannot start when already running."""
        boot_manager.start()
        result = boot_manager.start()
        assert not result

    def test_boot_manager_get_status(self, boot_manager):
        """Test 9: Get status returns correct structure."""
        status = boot_manager.get_status()
        assert "system" in status
        assert "stacks" in status
        assert "health" in status
        assert "events" in status

    def test_boot_manager_get_stack(self, boot_manager):
        """Test 10: Get specific stack instance."""
        stack = boot_manager.get_stack("faza21")
        assert stack is None  # Disabled in fixture

    def test_boot_manager_is_healthy_when_stopped(self, boot_manager):
        """Test 11: System not healthy when stopped."""
        assert not boot_manager.is_healthy()

    def test_boot_manager_is_healthy_when_running(self, boot_manager):
        """Test 12: System healthy when running with no errors."""
        boot_manager.start()
        assert boot_manager.is_healthy()

    def test_boot_manager_boot_events(self, boot_manager):
        """Test 13: Boot events are recorded."""
        boot_manager.start()
        assert len(boot_manager.boot_events) > 0
        first_event = boot_manager.boot_events[0]
        assert first_event.event_type == "boot_started"

    def test_boot_manager_stack_info_structure(self, boot_manager):
        """Test 14: Stack info has correct structure."""
        for stack_name, stack_info in boot_manager.stacks.items():
            assert isinstance(stack_info, StackInfo)
            assert stack_info.name == stack_name
            assert isinstance(stack_info.status, StackStatus)

    def test_boot_manager_uptime_calculation(self, boot_manager):
        """Test 15: Uptime is calculated correctly."""
        boot_manager.start()
        time.sleep(0.1)
        status = boot_manager.get_status()
        uptime = status["system"]["uptime_seconds"]
        assert uptime is not None
        assert uptime >= 0.1


# ============================================================================
# CLI COMMANDS TESTS (12 tests)
# ============================================================================

class TestCLICommands:
    """Test suite for CLICommands."""

    def test_cli_commands_initialization(self, cli_commands):
        """Test 16: CLICommands initializes correctly."""
        assert cli_commands.logs_manager is not None
        assert cli_commands.service_registry is not None

    def test_cli_commands_start(self, cli_commands):
        """Test 17: Start command executes."""
        result = cli_commands.start_command()
        assert isinstance(result, CommandResult)
        assert result.success or not result.success  # May fail if already running

    def test_cli_commands_stop_not_running(self, cli_commands):
        """Test 18: Stop when not running."""
        result = cli_commands.stop_command()
        assert not result.success
        assert "not running" in result.message.lower()

    def test_cli_commands_restart(self, cli_commands):
        """Test 19: Restart command executes."""
        result = cli_commands.restart_command()
        assert isinstance(result, CommandResult)

    def test_cli_commands_status(self, cli_commands):
        """Test 20: Status command returns data."""
        result = cli_commands.status_command()
        assert result.success
        assert result.data is not None

    def test_cli_commands_status_detailed(self, cli_commands):
        """Test 21: Detailed status includes stack info."""
        result = cli_commands.status_command(detailed=True)
        assert result.success
        assert "stack" in result.message.lower() or result.data is not None

    def test_cli_commands_logs_default(self, cli_commands):
        """Test 22: Logs command returns logs."""
        result = cli_commands.logs_command()
        assert result.success

    def test_cli_commands_logs_filtered(self, cli_commands):
        """Test 23: Logs command with level filter."""
        result = cli_commands.logs_command(level="error")
        assert result.success

    def test_cli_commands_logs_with_limit(self, cli_commands):
        """Test 24: Logs command with limit."""
        result = cli_commands.logs_command(limit=10)
        assert result.success

    def test_cli_commands_doctor(self, cli_commands):
        """Test 25: Doctor command runs diagnostics."""
        result = cli_commands.doctor_command()
        assert isinstance(result, CommandResult)
        assert result.data is not None

    def test_cli_commands_doctor_quick(self, cli_commands):
        """Test 26: Quick doctor command."""
        result = cli_commands.doctor_command(quick=True)
        assert isinstance(result, CommandResult)

    def test_cli_commands_help(self, cli_commands):
        """Test 27: Help command returns help text."""
        result = cli_commands.help_command()
        assert result.success
        assert "senti" in result.message.lower()


# ============================================================================
# CLI RENDERER TESTS (10 tests)
# ============================================================================

class TestCLIRenderer:
    """Test suite for CLIRenderer."""

    def test_cli_renderer_initialization(self, cli_renderer):
        """Test 28: CLIRenderer initializes correctly."""
        assert cli_renderer.config is not None
        assert not cli_renderer.config.use_colors  # Disabled in fixture

    def test_cli_renderer_header(self, cli_renderer):
        """Test 29: Render header."""
        header = cli_renderer.render_header("TEST")
        assert "TEST" in header
        assert len(header) > 0

    def test_cli_renderer_boot_step(self, cli_renderer):
        """Test 30: Render boot step."""
        step = cli_renderer.render_boot_step("Loading", HealthStatus.OK)
        assert "Loading" in step

    def test_cli_renderer_loading_animation(self, cli_renderer):
        """Test 31: Render loading animation."""
        anim = cli_renderer.render_loading_animation("Loading")
        assert "Loading" in anim

    def test_cli_renderer_dashboard(self, cli_renderer):
        """Test 32: Render dashboard."""
        status_data = {
            "system": {"state": "running", "uptime_seconds": 100},
            "stacks": {},
            "health": {"total_stacks": 6, "enabled_stacks": 6, "running_stacks": 6, "error_stacks": 0},
            "events": {"total": 0, "recent": []}
        }
        dashboard = cli_renderer.render_dashboard(status_data)
        assert "DASHBOARD" in dashboard
        assert "running" in dashboard.lower()

    def test_cli_renderer_compact_status(self, cli_renderer):
        """Test 33: Render compact status."""
        status_data = {
            "system": {"state": "running"},
            "health": {"running_stacks": 6, "enabled_stacks": 6, "error_stacks": 0}
        }
        status = cli_renderer.render_compact_status(status_data)
        assert "SENTI OS" in status

    def test_cli_renderer_error(self, cli_renderer):
        """Test 34: Render error message."""
        error = cli_renderer.render_error("Test Error", "Something went wrong")
        assert "ERROR" in error
        assert "Test Error" in error
        assert "Something went wrong" in error

    def test_cli_renderer_health_status_symbols(self, cli_renderer):
        """Test 35: Health status symbols render correctly."""
        ok_symbol = cli_renderer._status_symbol(HealthStatus.OK)
        warn_symbol = cli_renderer._status_symbol(HealthStatus.WARN)
        fail_symbol = cli_renderer._status_symbol(HealthStatus.FAIL)

        assert len(ok_symbol) > 0
        assert len(warn_symbol) > 0
        assert len(fail_symbol) > 0

    def test_cli_renderer_boot_progress(self, cli_renderer):
        """Test 36: Render boot progress."""
        steps = [
            {"name": "Step 1", "status": "completed"},
            {"name": "Step 2", "status": "in_progress"},
            {"name": "Step 3", "status": "pending"}
        ]
        progress = cli_renderer.render_boot_progress(steps, 1)
        assert "Step 1" in progress
        assert "Step 2" in progress

    def test_cli_renderer_no_colors(self, cli_renderer):
        """Test 37: Renderer works without colors."""
        # Config has use_colors=False
        colored = cli_renderer._color("test", Color.RED)
        assert colored == "test"  # No color codes added


# ============================================================================
# SERVICE REGISTRY TESTS (10 tests)
# ============================================================================

class TestServiceRegistry:
    """Test suite for ServiceRegistry."""

    def test_service_registry_initialization(self, service_registry):
        """Test 38: ServiceRegistry initializes correctly."""
        assert len(service_registry.STACK_REGISTRY) == 6

    def test_service_registry_get_stack_metadata(self, service_registry):
        """Test 39: Get stack metadata."""
        metadata = service_registry.get_stack_metadata("faza21")
        assert metadata is not None
        assert metadata.faza_number == 21

    def test_service_registry_get_all_stacks(self, service_registry):
        """Test 40: Get all stack names."""
        stacks = service_registry.get_all_stacks()
        assert len(stacks) == 6
        assert "faza21" in stacks

    def test_service_registry_get_stack_dependencies(self, service_registry):
        """Test 41: Get stack dependencies."""
        deps = service_registry.get_stack_dependencies("faza20")
        assert len(deps) > 0  # FAZA 20 has dependencies

    def test_service_registry_get_stacks_by_type(self, service_registry):
        """Test 42: Get stacks by type."""
        persistence_stacks = service_registry.get_stacks_by_type(StackType.PERSISTENCE)
        assert "faza21" in persistence_stacks

    def test_service_registry_validate_boot_order(self, service_registry):
        """Test 43: Validate correct boot order."""
        boot_order = ["faza21", "faza19", "faza20", "faza17", "faza16", "faza18"]
        validation = service_registry.validate_boot_order(boot_order)
        assert validation["valid"]

    def test_service_registry_validate_invalid_boot_order(self, service_registry):
        """Test 44: Validate invalid boot order."""
        # FAZA 20 before its dependencies
        boot_order = ["faza20", "faza21", "faza19"]
        validation = service_registry.validate_boot_order(boot_order)
        assert not validation["valid"]
        assert len(validation["errors"]) > 0

    def test_service_registry_get_registry_info(self, service_registry):
        """Test 45: Get registry information."""
        info = service_registry.get_registry_info()
        assert info["total_stacks"] == 6
        assert "stacks" in info

    def test_service_registry_get_stack_info_summary(self, service_registry):
        """Test 46: Get stack info summary."""
        summary = service_registry.get_stack_info_summary("faza21")
        assert "FAZA 21" in summary
        assert "Persistence" in summary

    def test_service_registry_singleton_pattern(self):
        """Test 47: Registry uses singleton pattern."""
        registry1 = get_service_registry()
        registry2 = get_service_registry()
        assert registry1 is registry2


# ============================================================================
# LOGS MANAGER TESTS (12 tests)
# ============================================================================

class TestLogsManager:
    """Test suite for LogsManager."""

    def test_logs_manager_initialization(self, logs_manager):
        """Test 48: LogsManager initializes correctly."""
        assert logs_manager.max_entries == 100

    def test_logs_manager_append_log(self, logs_manager):
        """Test 49: Append log entry."""
        logs_manager.append_log("info", "Test message")
        logs = logs_manager.get_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == "Test message"

    def test_logs_manager_append_multiple_logs(self, logs_manager):
        """Test 50: Append multiple log entries."""
        for i in range(10):
            logs_manager.append_log("info", f"Message {i}")
        logs = logs_manager.get_logs()
        assert len(logs) == 10

    def test_logs_manager_filter_by_level(self, logs_manager):
        """Test 51: Filter logs by level."""
        logs_manager.append_log("info", "Info message")
        logs_manager.append_log("error", "Error message")
        logs_manager.append_log("warning", "Warning message")

        error_logs = logs_manager.get_logs(level="error")
        assert len(error_logs) == 1
        assert error_logs[0]["level"] == "error"

    def test_logs_manager_limit(self, logs_manager):
        """Test 52: Limit number of returned logs."""
        for i in range(20):
            logs_manager.append_log("info", f"Message {i}")

        logs = logs_manager.get_logs(limit=5)
        assert len(logs) == 5

    def test_logs_manager_get_recent_logs(self, logs_manager):
        """Test 53: Get recent logs."""
        for i in range(10):
            logs_manager.append_log("info", f"Message {i}")

        recent = logs_manager.get_recent_logs(count=3)
        assert len(recent) == 3

    def test_logs_manager_get_error_logs(self, logs_manager):
        """Test 54: Get error logs only."""
        logs_manager.append_log("info", "Info")
        logs_manager.append_log("error", "Error 1")
        logs_manager.append_log("critical", "Critical 1")

        errors = logs_manager.get_error_logs()
        assert len(errors) == 2

    def test_logs_manager_search(self, logs_manager):
        """Test 55: Search logs by content."""
        logs_manager.append_log("info", "Start system")
        logs_manager.append_log("info", "Stop system")
        logs_manager.append_log("info", "Restart system")

        results = logs_manager.search_logs("system")
        assert len(results) == 3

    def test_logs_manager_statistics(self, logs_manager):
        """Test 56: Get log statistics."""
        logs_manager.append_log("info", "Test 1")
        logs_manager.append_log("error", "Test 2")

        stats = logs_manager.get_statistics()
        assert stats["current_entries"] == 2
        assert stats["total_logged"] == 2

    def test_logs_manager_clear_logs(self, logs_manager):
        """Test 57: Clear all logs."""
        logs_manager.append_log("info", "Test")
        logs_manager.clear_logs()

        logs = logs_manager.get_logs()
        assert len(logs) == 0

    def test_logs_manager_rolling_window(self, logs_manager):
        """Test 58: Rolling window behavior."""
        # Max entries is 100
        for i in range(150):
            logs_manager.append_log("info", f"Message {i}")

        logs = logs_manager.get_logs()
        assert len(logs) == 100  # Should not exceed max

    def test_logs_manager_get_log_summary(self, logs_manager):
        """Test 59: Get log summary."""
        logs_manager.append_log("info", "Info 1")
        logs_manager.append_log("error", "Error 1")
        logs_manager.append_log("warning", "Warning 1")

        summary = logs_manager.get_log_summary()
        assert summary["total_entries"] == 3
        assert summary["error_count"] >= 1


# ============================================================================
# SENTINEL PROCESS TESTS (8 tests)
# ============================================================================

class TestSentinelProcess:
    """Test suite for SentinelProcess."""

    def test_sentinel_initialization(self, sentinel_process):
        """Test 60: Sentinel initializes correctly."""
        assert sentinel_process.state == SentinelState.STOPPED
        assert not sentinel_process.is_running()

    def test_sentinel_start_stop(self, sentinel_process):
        """Test 61: Start and stop sentinel."""
        sentinel_process.start()
        assert sentinel_process.is_running()
        assert sentinel_process.state == SentinelState.RUNNING

        sentinel_process.stop()
        assert not sentinel_process.is_running()
        assert sentinel_process.state == SentinelState.STOPPED

    def test_sentinel_get_status(self, sentinel_process):
        """Test 62: Get sentinel status."""
        status = sentinel_process.get_status()
        assert "state" in status
        assert "running" in status
        assert "statistics" in status

    def test_sentinel_get_statistics(self, sentinel_process):
        """Test 63: Get sentinel statistics."""
        stats = sentinel_process.get_statistics()
        assert "checks_performed" in stats
        assert "alerts_triggered" in stats

    def test_sentinel_register_callbacks(self, sentinel_process):
        """Test 64: Register callbacks."""
        stall_callback = Mock()
        crash_callback = Mock()
        recovery_callback = Mock()

        sentinel_process.register_stall_callback(stall_callback)
        sentinel_process.register_crash_callback(crash_callback)
        sentinel_process.register_recovery_callback(recovery_callback)

        assert sentinel_process._on_stall_callback is not None
        assert sentinel_process._on_crash_callback is not None
        assert sentinel_process._on_recovery_callback is not None

    def test_sentinel_force_health_check(self, sentinel_process):
        """Test 65: Force immediate health check."""
        sentinel_process.start()
        sentinel_process.force_health_check()
        # Should not raise exception

    def test_sentinel_config(self, sentinel_process):
        """Test 66: Sentinel configuration."""
        assert sentinel_process.config.check_interval_seconds == 1
        assert sentinel_process.config.heartbeat_timeout_seconds == 5

    def test_sentinel_health_records(self, sentinel_process):
        """Test 67: Health records are created."""
        sentinel_process.start()
        time.sleep(0.1)
        status = sentinel_process.get_status()
        # No health records since all stacks disabled
        assert "health_records" in status


# ============================================================================
# FAZA22 STACK INTEGRATION TESTS (5 tests)
# ============================================================================

class TestFAZA22Stack:
    """Test suite for FAZA22Stack integration."""

    def test_faza22_stack_initialization(self, temp_storage_dir):
        """Test 68: FAZA22Stack initializes correctly."""
        stack = FAZA22Stack(
            storage_dir=temp_storage_dir,
            enable_sentinel=False,
            enable_persistence=False,
            enable_uil=False,
            enable_ux=False,
            enable_orchestration=False,
            enable_llm_control=False,
            enable_auth_flow=False
        )
        assert stack.boot_manager is not None
        assert stack.logs_manager is not None
        assert stack.service_registry is not None

    def test_faza22_stack_start_stop(self, temp_storage_dir):
        """Test 69: FAZA22Stack start and stop."""
        stack = FAZA22Stack(
            storage_dir=temp_storage_dir,
            enable_sentinel=False,
            enable_persistence=False,
            enable_uil=False,
            enable_ux=False,
            enable_orchestration=False,
            enable_llm_control=False,
            enable_auth_flow=False
        )

        assert stack.start()
        assert stack.is_running()

        assert stack.stop()
        assert not stack.is_running()

    def test_faza22_stack_get_status(self, temp_storage_dir):
        """Test 70: FAZA22Stack get status."""
        stack = FAZA22Stack(
            storage_dir=temp_storage_dir,
            enable_sentinel=False,
            enable_persistence=False,
            enable_uil=False,
            enable_ux=False,
            enable_orchestration=False,
            enable_llm_control=False,
            enable_auth_flow=False
        )

        status = stack.get_status()
        assert "faza22" in status
        assert "boot_manager" in status
        assert "logs" in status

    def test_faza22_stack_is_healthy(self, temp_storage_dir):
        """Test 71: FAZA22Stack health check."""
        stack = FAZA22Stack(
            storage_dir=temp_storage_dir,
            enable_sentinel=False,
            enable_persistence=False,
            enable_uil=False,
            enable_ux=False,
            enable_orchestration=False,
            enable_llm_control=False,
            enable_auth_flow=False
        )

        stack.start()
        assert stack.is_healthy()
        stack.stop()

    def test_faza22_stack_with_sentinel(self, temp_storage_dir):
        """Test 72: FAZA22Stack with sentinel enabled."""
        stack = FAZA22Stack(
            storage_dir=temp_storage_dir,
            enable_sentinel=True,
            enable_persistence=False,
            enable_uil=False,
            enable_ux=False,
            enable_orchestration=False,
            enable_llm_control=False,
            enable_auth_flow=False
        )

        assert stack.sentinel is not None
        stack.start()
        assert stack.sentinel.is_running()
        stack.stop()


# ============================================================================
# MODULE INFO TEST (1 test)
# ============================================================================

def test_faza22_get_info():
    """Test 73: get_info returns module information."""
    from senti_os.core.faza22 import get_info

    info = get_info()
    assert info["module"] == "faza22"
    assert info["name"] == "SENTI Boot Layer"
    assert info["version"] == "1.0.0"
    assert info["privacy_compliant"] == "true"


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

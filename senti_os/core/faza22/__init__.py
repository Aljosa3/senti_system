"""
FAZA 22 - SENTI Boot Layer

Unified Boot Manager, CLI, Lifecycle Handler, and Startup UX for SENTI OS.

This module provides complete system lifecycle management including:
- Boot orchestration across all FAZA stacks
- Command-line interface (CLI)
- Background health monitoring (Sentinel)
- System logging and diagnostics
- Visual terminal rendering

Components:
- BootManager: Main boot orchestrator
- CLICommands: Command implementations (start, stop, status, etc.)
- CLIRenderer: ASCII terminal renderer with dashboard
- ServiceRegistry: Central registry for all FAZA stacks
- LogsManager: Unified log management
- SentinelProcess: Background watchdog daemon
- CLIEntrypoint: Main CLI entry point

Boot Order:
    FAZA 21 (Persistence) →
    FAZA 19 (UIL) →
    FAZA 20 (UX Layer) →
    FAZA 17 (Orchestration) →
    FAZA 16 (LLM Control) →
    FAZA 18 (Auth Flow)

Privacy Guarantee:
- NO passwords stored
- NO biometric data collected
- NO external network calls
- All diagnostics are safe
- GDPR/ZVOP/EU AI Act compliant

Usage:
    from senti_os.core.faza22 import FAZA22Stack

    # Create and start FAZA 22 stack
    faza22 = FAZA22Stack()
    faza22.start()

    # Check status
    status = faza22.get_status()

    # Stop system
    faza22.stop()

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional

# Import all components
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
    get_cli_renderer
)

from senti_os.core.faza22.service_registry import (
    ServiceRegistry,
    StackMetadata,
    StackType,
    get_service_registry
)

from senti_os.core.faza22.logs_manager import (
    LogsManager,
    LogLevel,
    LogEntry,
    get_logs_manager
)

from senti_os.core.faza22.sentinel_process import (
    SentinelProcess,
    SentinelState,
    SentinelConfig,
    HealthCheckResult,
    StackHealthRecord
)

# CLI Entrypoint is not typically imported but included for completeness
from senti_os.core.faza22.cli_entrypoint import main as cli_main


# Module exports
__all__ = [
    # Main Stack Class
    "FAZA22Stack",

    # Boot Manager
    "BootManager",
    "BootState",
    "StackStatus",
    "StackInfo",
    "BootEvent",

    # CLI Commands
    "CLICommands",
    "CommandResult",
    "get_cli_commands",

    # CLI Renderer
    "CLIRenderer",
    "RenderConfig",
    "HealthStatus",
    "get_cli_renderer",

    # Service Registry
    "ServiceRegistry",
    "StackMetadata",
    "StackType",
    "get_service_registry",

    # Logs Manager
    "LogsManager",
    "LogLevel",
    "LogEntry",
    "get_logs_manager",

    # Sentinel Process
    "SentinelProcess",
    "SentinelState",
    "SentinelConfig",
    "HealthCheckResult",
    "StackHealthRecord",

    # CLI Entrypoint
    "cli_main",

    # Module info
    "get_info"
]


class FAZA22Stack:
    """
    Complete FAZA 22 Boot Layer stack.

    Provides unified interface for system lifecycle management,
    CLI operations, monitoring, and diagnostics.
    """

    def __init__(
        self,
        storage_dir: str = "/home/pisarna/senti_system/data/faza21",
        enable_sentinel: bool = True,
        enable_persistence: bool = True,
        enable_uil: bool = True,
        enable_ux: bool = True,
        enable_orchestration: bool = True,
        enable_llm_control: bool = True,
        enable_auth_flow: bool = True,
    ):
        """
        Initialize FAZA 22 stack.

        Args:
            storage_dir: Directory for FAZA 21 persistent storage.
            enable_sentinel: Enable background sentinel monitoring.
            enable_persistence: Enable FAZA 21.
            enable_uil: Enable FAZA 19.
            enable_ux: Enable FAZA 20.
            enable_orchestration: Enable FAZA 17.
            enable_llm_control: Enable FAZA 16.
            enable_auth_flow: Enable FAZA 18.
        """
        self.storage_dir = storage_dir

        # Initialize components
        self.boot_manager = BootManager(
            storage_dir=storage_dir,
            enable_persistence=enable_persistence,
            enable_uil=enable_uil,
            enable_ux=enable_ux,
            enable_orchestration=enable_orchestration,
            enable_llm_control=enable_llm_control,
            enable_auth_flow=enable_auth_flow
        )

        self.logs_manager = get_logs_manager()
        self.service_registry = get_service_registry()
        self.cli_renderer = get_cli_renderer()

        # Initialize sentinel if enabled
        self.sentinel_enabled = enable_sentinel
        self.sentinel: Optional[SentinelProcess] = None

        if enable_sentinel:
            self.sentinel = SentinelProcess(
                boot_manager=self.boot_manager,
                logs_manager=self.logs_manager
            )

        self._initialized = False

    def start(self) -> bool:
        """
        Start SENTI OS.

        Returns:
            True if started successfully.
        """
        # Start boot manager
        success = self.boot_manager.start()

        if not success:
            return False

        # Start sentinel if enabled
        if self.sentinel_enabled and self.sentinel:
            self.sentinel.start()

        self._initialized = True
        return True

    def stop(self) -> bool:
        """
        Stop SENTI OS.

        Returns:
            True if stopped successfully.
        """
        # Stop sentinel first
        if self.sentinel:
            self.sentinel.stop()

        # Stop boot manager
        return self.boot_manager.stop()

    def restart(self) -> bool:
        """
        Restart SENTI OS.

        Returns:
            True if restarted successfully.
        """
        # Stop first
        if not self.stop():
            return False

        # Start again
        return self.start()

    def get_status(self) -> Dict[str, Any]:
        """
        Get complete FAZA 22 status.

        Returns:
            Dictionary with comprehensive status.
        """
        status = {
            "faza22": {
                "initialized": self._initialized,
                "sentinel_enabled": self.sentinel_enabled
            },
            "boot_manager": self.boot_manager.get_status(),
            "logs": self.logs_manager.get_statistics(),
            "service_registry": self.service_registry.get_registry_info()
        }

        if self.sentinel:
            status["sentinel"] = self.sentinel.get_status()

        return status

    def get_boot_manager(self) -> BootManager:
        """Get boot manager instance."""
        return self.boot_manager

    def get_logs_manager(self) -> LogsManager:
        """Get logs manager instance."""
        return self.logs_manager

    def get_sentinel(self) -> Optional[SentinelProcess]:
        """Get sentinel process instance."""
        return self.sentinel

    def is_running(self) -> bool:
        """Check if system is running."""
        return self.boot_manager.is_running()

    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.boot_manager.is_healthy()


def get_info() -> Dict[str, str]:
    """
    Get FAZA 22 module information.

    Returns:
        Dictionary with comprehensive module metadata.
    """
    return {
        "module": "faza22",
        "name": "SENTI Boot Layer",
        "version": "1.0.0",
        "faza": "22",
        "description": "Unified Boot Manager, CLI, Lifecycle Handler, and Startup UX",

        # Privacy Guarantees
        "privacy_compliant": "true",
        "gdpr_compliant": "true",
        "zvop_compliant": "true",
        "eu_ai_act_compliant": "true",

        # Critical Security Rules
        "stores_passwords": "false",
        "stores_biometrics": "false",
        "makes_external_calls": "false",

        # What it DOES
        "orchestrates_boot": "true",
        "provides_cli": "true",
        "monitors_health": "true",
        "manages_logs": "true",
        "provides_diagnostics": "true",

        # Capabilities
        "supports_start_stop_restart": "true",
        "supports_status_monitoring": "true",
        "supports_log_management": "true",
        "supports_diagnostics": "true",
        "supports_sentinel_watchdog": "true",
        "supports_cli_interface": "true",
        "supports_visual_dashboard": "true",

        # Components
        "components": {
            "boot_manager": "Main boot orchestrator for all FAZA stacks",
            "cli_commands": "CLI command implementations (start/stop/status/logs/doctor)",
            "cli_renderer": "ASCII terminal renderer with animated dashboard",
            "service_registry": "Central registry for all FAZA stack metadata",
            "logs_manager": "Unified log management (max 10,000 entries)",
            "sentinel_process": "Background watchdog with auto-recovery",
            "cli_entrypoint": "Main CLI entry point for /usr/local/bin/senti"
        },

        # Boot Order
        "boot_order": [
            "FAZA 21 - Persistence Layer",
            "FAZA 19 - UIL & Multi-Device Communication",
            "FAZA 20 - User Experience Layer",
            "FAZA 17 - Multi-Model Orchestration",
            "FAZA 16 - LLM Control Layer",
            "FAZA 18 - Auth Flow Handler"
        ],

        # CLI Commands
        "cli_commands": [
            "senti start - Start SENTI OS",
            "senti stop - Stop SENTI OS",
            "senti restart - Restart SENTI OS",
            "senti status - Show system status",
            "senti logs - Show system logs",
            "senti doctor - Run diagnostics",
            "senti help - Show help"
        ],

        # Architecture
        "architecture": "unified_boot_lifecycle",
        "approach": "orchestrated_dependency_resolution",

        # Contact
        "author": "SENTI OS Core Team",
        "license": "Proprietary"
    }


# Version info
__version__ = "1.0.0"
__author__ = "SENTI OS Core Team"
__license__ = "Proprietary"

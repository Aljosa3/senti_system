"""
FAZA 22 - CLI Commands

Implements all CLI command actions for SENTI OS.

Available Commands:
- start: Start SENTI OS
- stop: Stop SENTI OS
- restart: Restart SENTI OS
- status: Show system status
- logs: Show system logs
- doctor: Run diagnostics
- help: Show help information

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import os
import json
from pathlib import Path

from senti_os.core.faza22.boot_manager import BootManager, BootState
from senti_os.core.faza22.logs_manager import LogsManager
from senti_os.core.faza22.service_registry import ServiceRegistry


@dataclass
class CommandResult:
    """Result of a CLI command execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    exit_code: int = 0


class CLICommands:
    """
    CLI command implementations for SENTI OS.

    Provides all command logic for the CLI interface.
    """

    def __init__(
        self,
        storage_dir: str = "/home/pisarna/senti_system/data/faza21",
        state_file: str = "/home/pisarna/senti_system/data/faza22/boot_state.json"
    ):
        """
        Initialize CLI commands.

        Args:
            storage_dir: Directory for FAZA 21 persistent storage.
            state_file: File to persist boot manager state.
        """
        self.storage_dir = storage_dir
        self.state_file = state_file
        self.logs_manager = LogsManager()
        self.service_registry = ServiceRegistry()

        # Ensure state directory exists
        Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)

    def _get_boot_manager(self) -> Optional[BootManager]:
        """
        Get or create boot manager instance.

        Returns:
            BootManager instance or None if cannot be created.
        """
        try:
            manager = self.service_registry.get_boot_manager(
                storage_dir=self.storage_dir
            )
            return manager
        except Exception as e:
            self.logs_manager.append_log(
                "error",
                f"Failed to get boot manager: {str(e)}"
            )
            return None

    def _save_state(self, manager: BootManager):
        """
        Save boot manager state to disk.

        Args:
            manager: BootManager instance to save.
        """
        try:
            state = {
                "state": manager.state.value,
                "enabled_stacks": manager.enabled_stacks,
                "storage_dir": manager.storage_dir
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logs_manager.append_log(
                "warning",
                f"Failed to save state: {str(e)}"
            )

    def start_command(self) -> CommandResult:
        """
        Start SENTI OS.

        Returns:
            CommandResult with start status.
        """
        self.logs_manager.append_log("info", "Start command initiated")

        manager = self._get_boot_manager()
        if not manager:
            return CommandResult(
                success=False,
                message="Failed to initialize boot manager",
                exit_code=1
            )

        # Check if already running
        if manager.is_running():
            return CommandResult(
                success=False,
                message="SENTI OS is already running",
                data={"state": manager.state.value},
                exit_code=1
            )

        # Start the system
        self.logs_manager.append_log("info", "Starting SENTI OS...")

        try:
            success = manager.start()

            if success:
                self._save_state(manager)
                self.logs_manager.append_log("info", "SENTI OS started successfully")

                status = manager.get_status()
                boot_time = status["system"].get("uptime_seconds", 0)

                return CommandResult(
                    success=True,
                    message=f"SENTI OS started successfully (boot time: {boot_time:.2f}s)",
                    data=status
                )
            else:
                self.logs_manager.append_log("error", "SENTI OS failed to start")
                return CommandResult(
                    success=False,
                    message="Failed to start SENTI OS. Check logs for details.",
                    data=manager.get_status(),
                    exit_code=1
                )
        except Exception as e:
            self.logs_manager.append_log("error", f"Start failed with exception: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Start failed: {str(e)}",
                exit_code=1
            )

    def stop_command(self) -> CommandResult:
        """
        Stop SENTI OS.

        Returns:
            CommandResult with stop status.
        """
        self.logs_manager.append_log("info", "Stop command initiated")

        manager = self._get_boot_manager()
        if not manager:
            return CommandResult(
                success=False,
                message="Failed to initialize boot manager",
                exit_code=1
            )

        # Check if not running
        if not manager.is_running():
            return CommandResult(
                success=False,
                message="SENTI OS is not running",
                data={"state": manager.state.value},
                exit_code=1
            )

        # Stop the system
        self.logs_manager.append_log("info", "Stopping SENTI OS...")

        try:
            success = manager.stop()

            if success:
                self._save_state(manager)
                self.logs_manager.append_log("info", "SENTI OS stopped successfully")

                return CommandResult(
                    success=True,
                    message="SENTI OS stopped successfully",
                    data=manager.get_status()
                )
            else:
                self.logs_manager.append_log("error", "SENTI OS failed to stop cleanly")
                return CommandResult(
                    success=False,
                    message="Failed to stop SENTI OS cleanly. Some services may still be running.",
                    data=manager.get_status(),
                    exit_code=1
                )
        except Exception as e:
            self.logs_manager.append_log("error", f"Stop failed with exception: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Stop failed: {str(e)}",
                exit_code=1
            )

    def restart_command(self) -> CommandResult:
        """
        Restart SENTI OS.

        Returns:
            CommandResult with restart status.
        """
        self.logs_manager.append_log("info", "Restart command initiated")

        manager = self._get_boot_manager()
        if not manager:
            return CommandResult(
                success=False,
                message="Failed to initialize boot manager",
                exit_code=1
            )

        # Restart the system
        self.logs_manager.append_log("info", "Restarting SENTI OS...")

        try:
            success = manager.restart()

            if success:
                self._save_state(manager)
                self.logs_manager.append_log("info", "SENTI OS restarted successfully")

                status = manager.get_status()
                boot_time = status["system"].get("uptime_seconds", 0)

                return CommandResult(
                    success=True,
                    message=f"SENTI OS restarted successfully (boot time: {boot_time:.2f}s)",
                    data=status
                )
            else:
                self.logs_manager.append_log("error", "SENTI OS failed to restart")
                return CommandResult(
                    success=False,
                    message="Failed to restart SENTI OS. Check logs for details.",
                    data=manager.get_status(),
                    exit_code=1
                )
        except Exception as e:
            self.logs_manager.append_log("error", f"Restart failed with exception: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Restart failed: {str(e)}",
                exit_code=1
            )

    def status_command(self, detailed: bool = False) -> CommandResult:
        """
        Show SENTI OS status.

        Args:
            detailed: If True, show detailed status information.

        Returns:
            CommandResult with status information.
        """
        manager = self._get_boot_manager()
        if not manager:
            return CommandResult(
                success=False,
                message="Failed to initialize boot manager",
                exit_code=1
            )

        try:
            status = manager.get_status()

            # Build status message
            system_state = status["system"]["state"]
            health = status["health"]

            message_lines = [
                f"SENTI OS Status: {system_state.upper()}"
            ]

            if system_state == "running":
                uptime = status["system"].get("uptime_seconds", 0)
                message_lines.append(f"Uptime: {uptime:.0f} seconds")

            message_lines.extend([
                f"Enabled Stacks: {health['enabled_stacks']}/{health['total_stacks']}",
                f"Running Stacks: {health['running_stacks']}",
                f"Error Stacks: {health['error_stacks']}"
            ])

            if detailed:
                message_lines.append("\nStack Details:")
                for stack_name, stack_info in status["stacks"].items():
                    if stack_info["enabled"]:
                        status_str = stack_info["status"]
                        error_str = f" - {stack_info['error']}" if stack_info["error"] else ""
                        message_lines.append(f"  {stack_name}: {status_str}{error_str}")

            return CommandResult(
                success=True,
                message="\n".join(message_lines),
                data=status
            )
        except Exception as e:
            self.logs_manager.append_log("error", f"Status failed with exception: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Failed to get status: {str(e)}",
                exit_code=1
            )

    def logs_command(
        self,
        level: Optional[str] = None,
        limit: int = 50,
        follow: bool = False
    ) -> CommandResult:
        """
        Show system logs.

        Args:
            level: Filter by log level (info, warning, error).
            limit: Maximum number of log entries to show.
            follow: If True, continuously show new logs (not implemented in CLI).

        Returns:
            CommandResult with log entries.
        """
        try:
            logs = self.logs_manager.get_logs(
                level=level,
                limit=limit
            )

            if not logs:
                return CommandResult(
                    success=True,
                    message="No logs available",
                    data={"logs": []}
                )

            # Format logs
            log_lines = []
            for log_entry in logs:
                timestamp = log_entry["timestamp"][:19]  # Trim microseconds
                level_str = log_entry["level"].upper()
                message = log_entry["message"]
                log_lines.append(f"[{timestamp}] {level_str:7} {message}")

            message = "\n".join(log_lines)

            return CommandResult(
                success=True,
                message=message,
                data={"logs": logs, "count": len(logs)}
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to get logs: {str(e)}",
                exit_code=1
            )

    def doctor_command(self, quick: bool = False) -> CommandResult:
        """
        Run system diagnostics.

        Args:
            quick: If True, run only essential checks.

        Returns:
            CommandResult with diagnostic results.
        """
        self.logs_manager.append_log("info", "Running system diagnostics...")

        manager = self._get_boot_manager()
        if not manager:
            return CommandResult(
                success=False,
                message="Failed to initialize boot manager",
                exit_code=1
            )

        try:
            # Get FAZA 20 stack for diagnostics
            faza20 = manager.get_stack("faza20")

            diagnostic_results = {
                "system_state": manager.state.value,
                "is_running": manager.is_running(),
                "is_healthy": manager.is_healthy(),
                "checks": []
            }

            # Basic health checks
            status = manager.get_status()
            health = status["health"]

            # Check 1: System state
            if manager.state == BootState.RUNNING:
                diagnostic_results["checks"].append({
                    "name": "System State",
                    "status": "PASS",
                    "message": "System is running"
                })
            else:
                diagnostic_results["checks"].append({
                    "name": "System State",
                    "status": "FAIL",
                    "message": f"System is not running (state: {manager.state.value})"
                })

            # Check 2: Stack health
            if health["error_stacks"] == 0:
                diagnostic_results["checks"].append({
                    "name": "Stack Health",
                    "status": "PASS",
                    "message": f"All {health['running_stacks']} stacks are healthy"
                })
            else:
                diagnostic_results["checks"].append({
                    "name": "Stack Health",
                    "status": "WARN",
                    "message": f"{health['error_stacks']} stack(s) have errors"
                })

            # Check 3: FAZA 21 Persistence
            faza21 = manager.get_stack("faza21")
            if faza21:
                try:
                    faza21_status = faza21.get_status()
                    if faza21_status.get("initialized"):
                        diagnostic_results["checks"].append({
                            "name": "Persistence Layer",
                            "status": "PASS",
                            "message": "FAZA 21 initialized"
                        })
                    else:
                        diagnostic_results["checks"].append({
                            "name": "Persistence Layer",
                            "status": "WARN",
                            "message": "FAZA 21 not initialized"
                        })
                except Exception as e:
                    diagnostic_results["checks"].append({
                        "name": "Persistence Layer",
                        "status": "FAIL",
                        "message": f"FAZA 21 check failed: {str(e)}"
                    })

            # Check 4: FAZA 19 UIL
            faza19 = manager.get_stack("faza19")
            if faza19:
                try:
                    faza19_status = faza19.get_stack_status()
                    diagnostic_results["checks"].append({
                        "name": "UIL Communication",
                        "status": "PASS",
                        "message": f"FAZA 19 active ({faza19_status['event_bus']['event_count']} events)"
                    })
                except Exception as e:
                    diagnostic_results["checks"].append({
                        "name": "UIL Communication",
                        "status": "WARN",
                        "message": f"FAZA 19 check failed: {str(e)}"
                    })

            # Check 5: Storage directory
            if os.path.exists(self.storage_dir):
                diagnostic_results["checks"].append({
                    "name": "Storage Directory",
                    "status": "PASS",
                    "message": f"Storage directory exists: {self.storage_dir}"
                })
            else:
                diagnostic_results["checks"].append({
                    "name": "Storage Directory",
                    "status": "WARN",
                    "message": f"Storage directory not found: {self.storage_dir}"
                })

            # Run FAZA 20 diagnostics if available and not quick mode
            if faza20 and not quick:
                try:
                    faza20_diagnostics = faza20.run_diagnostics(quick=quick)
                    if hasattr(faza20_diagnostics, 'checks'):
                        for check in faza20_diagnostics.checks[:5]:  # Limit to 5
                            diagnostic_results["checks"].append({
                                "name": f"FAZA20: {check.name}",
                                "status": check.level.value.upper(),
                                "message": check.message
                            })
                except Exception as e:
                    diagnostic_results["checks"].append({
                        "name": "FAZA 20 Diagnostics",
                        "status": "WARN",
                        "message": f"Could not run FAZA 20 diagnostics: {str(e)}"
                    })

            # Determine overall status
            pass_count = sum(1 for c in diagnostic_results["checks"] if c["status"] == "PASS")
            warn_count = sum(1 for c in diagnostic_results["checks"] if c["status"] == "WARN")
            fail_count = sum(1 for c in diagnostic_results["checks"] if c["status"] == "FAIL")

            total_checks = len(diagnostic_results["checks"])

            # Format message
            message_lines = [
                f"Diagnostic Results ({total_checks} checks):",
                f"  PASS: {pass_count}",
                f"  WARN: {warn_count}",
                f"  FAIL: {fail_count}",
                ""
            ]

            for check in diagnostic_results["checks"]:
                status_icon = {
                    "PASS": "✓",
                    "WARN": "⚠",
                    "FAIL": "✗"
                }.get(check["status"], "?")

                message_lines.append(
                    f"{status_icon} {check['name']}: {check['message']}"
                )

            overall_success = fail_count == 0

            self.logs_manager.append_log(
                "info",
                f"Diagnostics completed: {pass_count} passed, {warn_count} warnings, {fail_count} failed"
            )

            return CommandResult(
                success=overall_success,
                message="\n".join(message_lines),
                data=diagnostic_results,
                exit_code=0 if overall_success else 1
            )

        except Exception as e:
            self.logs_manager.append_log("error", f"Diagnostics failed: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Diagnostics failed: {str(e)}",
                exit_code=1
            )

    def help_command(self) -> CommandResult:
        """
        Show help information.

        Returns:
            CommandResult with help text.
        """
        help_text = """
SENTI OS - Command Line Interface

USAGE:
    senti <command> [options]

COMMANDS:
    start              Start SENTI OS
    stop               Stop SENTI OS
    restart            Restart SENTI OS
    status             Show system status
    status --detailed  Show detailed status with stack information
    logs               Show recent system logs (last 50 entries)
    logs --level=error Show logs filtered by level (info/warning/error)
    logs --limit=100   Show specific number of log entries
    doctor             Run comprehensive system diagnostics
    doctor --quick     Run quick diagnostic checks only
    help               Show this help message

EXAMPLES:
    senti start                  # Start SENTI OS
    senti status --detailed      # Show detailed status
    senti logs --level=error     # Show only error logs
    senti doctor                 # Run full diagnostics

SYSTEM INFORMATION:
    Storage Directory: /home/pisarna/senti_system/data/faza21
    State File: /home/pisarna/senti_system/data/faza22/boot_state.json

FAZA STACK ORDER:
    1. FAZA 21 - Persistence Layer
    2. FAZA 19 - UIL & Multi-Device Communication
    3. FAZA 20 - User Experience Layer
    4. FAZA 17 - Multi-Model Orchestration
    5. FAZA 16 - LLM Control Layer
    6. FAZA 18 - Auth Flow Handler

For more information, visit: https://github.com/senti-os
"""
        return CommandResult(
            success=True,
            message=help_text.strip()
        )


# Global instance for singleton pattern
_cli_commands_instance: Optional[CLICommands] = None


def get_cli_commands(
    storage_dir: str = "/home/pisarna/senti_system/data/faza21",
    state_file: str = "/home/pisarna/senti_system/data/faza22/boot_state.json"
) -> CLICommands:
    """
    Get or create CLI commands singleton instance.

    Args:
        storage_dir: Directory for FAZA 21 persistent storage.
        state_file: File to persist boot manager state.

    Returns:
        CLICommands instance.
    """
    global _cli_commands_instance

    if _cli_commands_instance is None:
        _cli_commands_instance = CLICommands(
            storage_dir=storage_dir,
            state_file=state_file
        )

    return _cli_commands_instance

"""
FAZA 22 - CLI Renderer

ASCII terminal renderer for SENTI OS boot and status display.

Features:
- Animated loading steps
- Health indicators (OK / WARN / FAIL)
- Real-time dashboard display
- FAZA-level status visualization
- Heartbeat monitoring display
- Snapshot information
- Storage integrity indicators
- Module health overview

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
import time
import sys


class HealthStatus(Enum):
    """Health status indicators."""
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    UNKNOWN = "unknown"


class Color:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class Symbol:
    """ASCII symbols for status indicators."""
    OK = "✓"
    WARN = "⚠"
    FAIL = "✗"
    INFO = "ℹ"
    ARROW = "→"
    DOT = "•"
    SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


@dataclass
class RenderConfig:
    """Configuration for renderer."""
    use_colors: bool = True
    use_unicode: bool = True
    terminal_width: int = 80


class CLIRenderer:
    """
    ASCII terminal renderer for SENTI OS.

    Provides rich visual feedback for boot process, status display,
    and system health monitoring.
    """

    def __init__(self, config: Optional[RenderConfig] = None):
        """
        Initialize CLI renderer.

        Args:
            config: Optional render configuration.
        """
        self.config = config or RenderConfig()
        self._spinner_state = 0

    def _color(self, text: str, color: str) -> str:
        """
        Apply color to text.

        Args:
            text: Text to colorize.
            color: Color code.

        Returns:
            Colored text if colors enabled, otherwise plain text.
        """
        if self.config.use_colors:
            return f"{color}{text}{Color.RESET}"
        return text

    def _status_symbol(self, status: HealthStatus) -> str:
        """
        Get symbol for health status.

        Args:
            status: Health status.

        Returns:
            Status symbol with color.
        """
        if not self.config.use_unicode:
            symbols = {
                HealthStatus.OK: "[OK]",
                HealthStatus.WARN: "[WARN]",
                HealthStatus.FAIL: "[FAIL]",
                HealthStatus.UNKNOWN: "[?]"
            }
            return symbols[status]

        symbols = {
            HealthStatus.OK: (Symbol.OK, Color.GREEN),
            HealthStatus.WARN: (Symbol.WARN, Color.YELLOW),
            HealthStatus.FAIL: (Symbol.FAIL, Color.RED),
            HealthStatus.UNKNOWN: (Symbol.INFO, Color.BRIGHT_BLACK)
        }

        symbol, color = symbols[status]
        return self._color(symbol, color)

    def render_header(self, title: str = "SENTI OS") -> str:
        """
        Render header banner.

        Args:
            title: Title to display.

        Returns:
            Formatted header string.
        """
        width = self.config.terminal_width
        lines = []

        # Top border
        lines.append(self._color("═" * width, Color.CYAN))

        # Title
        padding = (width - len(title) - 4) // 2
        title_line = " " * padding + f"  {title}  " + " " * padding
        lines.append(self._color(title_line, Color.BOLD + Color.CYAN))

        # Bottom border
        lines.append(self._color("═" * width, Color.CYAN))

        return "\n".join(lines)

    def render_boot_step(
        self,
        step_name: str,
        status: HealthStatus,
        message: Optional[str] = None
    ) -> str:
        """
        Render a boot step with status.

        Args:
            step_name: Name of boot step.
            status: Status of the step.
            message: Optional additional message.

        Returns:
            Formatted boot step string.
        """
        status_icon = self._status_symbol(status)

        if message:
            return f"{status_icon} {step_name}: {message}"
        else:
            return f"{status_icon} {step_name}"

    def render_loading_animation(
        self,
        message: str = "Loading"
    ) -> str:
        """
        Render animated loading spinner.

        Args:
            message: Loading message.

        Returns:
            Formatted loading string with spinner.
        """
        if not self.config.use_unicode:
            return f"[...] {message}"

        spinner_char = Symbol.SPINNER[self._spinner_state]
        self._spinner_state = (self._spinner_state + 1) % len(Symbol.SPINNER)

        return f"{self._color(spinner_char, Color.CYAN)} {message}"

    def render_dashboard(self, status_data: Dict[str, Any]) -> str:
        """
        Render real-time system dashboard.

        Args:
            status_data: System status data from boot_manager.

        Returns:
            Formatted dashboard string.
        """
        lines = []
        width = self.config.terminal_width

        # Header
        lines.append(self.render_header("SENTI OS DASHBOARD"))
        lines.append("")

        # System state
        system = status_data.get("system", {})
        state = system.get("state", "unknown").upper()

        state_color = Color.GREEN if state == "RUNNING" else Color.YELLOW
        lines.append(self._color(f"System State: {state}", Color.BOLD + state_color))

        # Uptime if running
        uptime = system.get("uptime_seconds")
        if uptime is not None:
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            lines.append(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")

        lines.append("")

        # FAZA Stacks Status
        lines.append(self._color("FAZA STACKS", Color.BOLD + Color.CYAN))
        lines.append(self._color("─" * 40, Color.CYAN))

        stacks = status_data.get("stacks", {})
        stack_order = ["faza21", "faza19", "faza20", "faza17", "faza16", "faza18"]

        for stack_name in stack_order:
            stack_info = stacks.get(stack_name, {})
            if not stack_info.get("enabled", False):
                continue

            stack_status = stack_info.get("status", "unknown")
            error = stack_info.get("error")

            # Determine health status
            if stack_status == "running":
                health = HealthStatus.OK
            elif stack_status == "error":
                health = HealthStatus.FAIL
            elif stack_status in ["stopped", "not_loaded"]:
                health = HealthStatus.WARN
            else:
                health = HealthStatus.UNKNOWN

            status_icon = self._status_symbol(health)

            # Stack display name
            display_names = {
                "faza21": "FAZA 21 - Persistence",
                "faza19": "FAZA 19 - UIL",
                "faza20": "FAZA 20 - UX Layer",
                "faza17": "FAZA 17 - Orchestration",
                "faza16": "FAZA 16 - LLM Control",
                "faza18": "FAZA 18 - Auth Flow"
            }
            display_name = display_names.get(stack_name, stack_name)

            line = f"  {status_icon} {display_name:<30} {stack_status}"
            if error:
                line += f"\n     {self._color('Error:', Color.RED)} {error[:50]}"

            lines.append(line)

        lines.append("")

        # Health Summary
        health = status_data.get("health", {})
        lines.append(self._color("HEALTH SUMMARY", Color.BOLD + Color.CYAN))
        lines.append(self._color("─" * 40, Color.CYAN))

        total_stacks = health.get("total_stacks", 0)
        enabled_stacks = health.get("enabled_stacks", 0)
        running_stacks = health.get("running_stacks", 0)
        error_stacks = health.get("error_stacks", 0)

        lines.append(f"  Total Stacks: {total_stacks}")
        lines.append(f"  Enabled: {enabled_stacks}")

        running_color = Color.GREEN if running_stacks == enabled_stacks else Color.YELLOW
        lines.append(f"  Running: {self._color(str(running_stacks), running_color)}")

        if error_stacks > 0:
            lines.append(f"  Errors: {self._color(str(error_stacks), Color.RED)}")

        lines.append("")

        # Recent Events
        events = status_data.get("events", {})
        recent_events = events.get("recent", [])

        if recent_events:
            lines.append(self._color("RECENT EVENTS", Color.BOLD + Color.CYAN))
            lines.append(self._color("─" * 40, Color.CYAN))

            for event in recent_events[-5:]:  # Last 5 events
                event_type = event.get("type", "unknown")
                message = event.get("message", "")
                timestamp = event.get("timestamp", "")[:19]  # Trim microseconds

                # Color code event types
                if "error" in event_type or "failed" in event_type:
                    type_color = Color.RED
                elif "completed" in event_type or "started" in event_type:
                    type_color = Color.GREEN
                else:
                    type_color = Color.YELLOW

                lines.append(
                    f"  {self._color(timestamp, Color.DIM)} "
                    f"{self._color(event_type, type_color)}: {message[:40]}"
                )

        lines.append("")
        lines.append(self._color("─" * width, Color.CYAN))

        return "\n".join(lines)

    def render_heartbeat_status(
        self,
        heartbeat_data: Dict[str, Any]
    ) -> str:
        """
        Render heartbeat monitoring status.

        Args:
            heartbeat_data: Heartbeat data from FAZA 20.

        Returns:
            Formatted heartbeat status string.
        """
        lines = []

        lines.append(self._color("HEARTBEAT MONITOR", Color.BOLD + Color.CYAN))
        lines.append(self._color("─" * 40, Color.CYAN))

        status = heartbeat_data.get("status", "unknown")
        interval = heartbeat_data.get("interval_seconds", 0)
        last_beat = heartbeat_data.get("last_beat", "never")

        # Status indicator
        health = HealthStatus.OK if status == "healthy" else HealthStatus.WARN
        status_icon = self._status_symbol(health)

        lines.append(f"  {status_icon} Status: {status}")
        lines.append(f"  Interval: {interval}s")
        lines.append(f"  Last Beat: {last_beat}")

        # Module heartbeats
        modules = heartbeat_data.get("modules", {})
        if modules:
            lines.append("")
            lines.append("  Module Heartbeats:")
            for module_name, module_status in modules.items():
                module_health = HealthStatus.OK if module_status == "ok" else HealthStatus.FAIL
                module_icon = self._status_symbol(module_health)
                lines.append(f"    {module_icon} {module_name}")

        return "\n".join(lines)

    def render_storage_status(
        self,
        storage_data: Dict[str, Any]
    ) -> str:
        """
        Render storage integrity status.

        Args:
            storage_data: Storage data from FAZA 21.

        Returns:
            Formatted storage status string.
        """
        lines = []

        lines.append(self._color("STORAGE INTEGRITY", Color.BOLD + Color.CYAN))
        lines.append(self._color("─" * 40, Color.CYAN))

        initialized = storage_data.get("initialized", False)
        encrypted = storage_data.get("encrypted", False)
        integrity_ok = storage_data.get("integrity_check_passed", False)

        # Status indicators
        init_status = HealthStatus.OK if initialized else HealthStatus.FAIL
        encrypt_status = HealthStatus.OK if encrypted else HealthStatus.WARN
        integrity_status = HealthStatus.OK if integrity_ok else HealthStatus.FAIL

        lines.append(f"  {self._status_symbol(init_status)} Initialized")
        lines.append(f"  {self._status_symbol(encrypt_status)} Encrypted")
        lines.append(f"  {self._status_symbol(integrity_status)} Integrity Check")

        # Snapshot info
        snapshots = storage_data.get("snapshots", [])
        lines.append(f"  Snapshots: {len(snapshots)}")

        if snapshots:
            latest = snapshots[-1]
            snapshot_id = latest.get("id", "unknown")[:8]
            snapshot_time = latest.get("timestamp", "unknown")[:19]
            lines.append(f"  Latest: {snapshot_id} ({snapshot_time})")

        return "\n".join(lines)

    def render_module_health(
        self,
        modules_data: Dict[str, Any]
    ) -> str:
        """
        Render module health overview.

        Args:
            modules_data: Module health data.

        Returns:
            Formatted module health string.
        """
        lines = []

        lines.append(self._color("MODULE HEALTH", Color.BOLD + Color.CYAN))
        lines.append(self._color("─" * 40, Color.CYAN))

        for module_name, module_info in modules_data.items():
            status = module_info.get("status", "unknown")
            health = module_info.get("health", "unknown")

            # Determine health status
            if health == "healthy" or status == "running":
                health_status = HealthStatus.OK
            elif health == "degraded" or status == "error":
                health_status = HealthStatus.WARN
            elif health == "failed":
                health_status = HealthStatus.FAIL
            else:
                health_status = HealthStatus.UNKNOWN

            status_icon = self._status_symbol(health_status)
            lines.append(f"  {status_icon} {module_name:<20} {status}")

        return "\n".join(lines)

    def render_compact_status(self, status_data: Dict[str, Any]) -> str:
        """
        Render compact one-line status.

        Args:
            status_data: System status data.

        Returns:
            Formatted compact status string.
        """
        system = status_data.get("system", {})
        state = system.get("state", "unknown").upper()

        health = status_data.get("health", {})
        running = health.get("running_stacks", 0)
        enabled = health.get("enabled_stacks", 0)
        errors = health.get("error_stacks", 0)

        state_icon = self._status_symbol(
            HealthStatus.OK if state == "RUNNING" else HealthStatus.WARN
        )

        status_str = f"{state_icon} SENTI OS: {state} | Stacks: {running}/{enabled}"

        if errors > 0:
            status_str += f" | {self._color(f'Errors: {errors}', Color.RED)}"

        return status_str

    def render_boot_progress(
        self,
        steps: List[Dict[str, Any]],
        current_step: int
    ) -> str:
        """
        Render boot progress visualization.

        Args:
            steps: List of boot steps with status.
            current_step: Index of current step.

        Returns:
            Formatted boot progress string.
        """
        lines = []

        lines.append(self.render_header("SENTI OS BOOT"))
        lines.append("")

        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i+1}")
            step_status = step.get("status", "pending")

            if i < current_step:
                # Completed step
                status = HealthStatus.OK
            elif i == current_step:
                # Current step
                if step_status == "error":
                    status = HealthStatus.FAIL
                else:
                    status = HealthStatus.UNKNOWN
                    step_name = self.render_loading_animation(step_name)
            else:
                # Pending step
                status = HealthStatus.UNKNOWN

            if i != current_step:
                lines.append(self.render_boot_step(step_name, status))
            else:
                lines.append(step_name)

        lines.append("")
        progress = int((current_step / len(steps)) * 100) if steps else 0
        lines.append(f"Progress: {progress}%")

        return "\n".join(lines)

    def render_error(self, title: str, message: str, details: Optional[str] = None) -> str:
        """
        Render error message.

        Args:
            title: Error title.
            message: Error message.
            details: Optional error details.

        Returns:
            Formatted error string.
        """
        lines = []

        lines.append(self._color("═" * self.config.terminal_width, Color.RED))
        lines.append(self._color(f"  ERROR: {title}", Color.BOLD + Color.RED))
        lines.append(self._color("═" * self.config.terminal_width, Color.RED))
        lines.append("")
        lines.append(f"  {message}")

        if details:
            lines.append("")
            lines.append(self._color("  Details:", Color.DIM))
            for line in details.split("\n"):
                lines.append(f"    {self._color(line, Color.DIM)}")

        lines.append("")

        return "\n".join(lines)

    def clear_screen(self):
        """Clear terminal screen (for animated updates)."""
        if sys.platform == "win32":
            import os
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")


# Global renderer instance
_cli_renderer_instance: Optional[CLIRenderer] = None


def get_cli_renderer(config: Optional[RenderConfig] = None) -> CLIRenderer:
    """
    Get or create CLI renderer singleton.

    Args:
        config: Optional render configuration.

    Returns:
        CLIRenderer instance.
    """
    global _cli_renderer_instance

    if _cli_renderer_instance is None:
        _cli_renderer_instance = CLIRenderer(config)

    return _cli_renderer_instance

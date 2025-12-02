"""
FAZA 22 - Sentinel Process

Background watchdog daemon for SENTI OS health monitoring.

Responsibilities:
- Monitor heartbeat from all FAZA stacks
- Detect system stalls (no heartbeat)
- Detect crashes and errors
- Auto-emit status events to FAZA 19
- Trigger safe shutdown if needed
- Optional auto-recovery
- Performance monitoring

Privacy Guarantee:
- NO collection of sensitive data
- Only internal system metrics
- GDPR/ZVOP compliant

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import time


class SentinelState(Enum):
    """Sentinel process states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class HealthCheckResult(Enum):
    """Health check results."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STALLED = "stalled"
    CRASHED = "crashed"
    UNKNOWN = "unknown"


@dataclass
class StackHealthRecord:
    """Health record for a FAZA stack."""
    stack_name: str
    last_heartbeat: datetime
    heartbeat_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    status: HealthCheckResult = HealthCheckResult.UNKNOWN


@dataclass
class SentinelConfig:
    """Configuration for sentinel process."""
    check_interval_seconds: int = 5
    heartbeat_timeout_seconds: int = 30
    max_errors_before_alert: int = 3
    auto_recovery_enabled: bool = False
    safe_shutdown_on_critical: bool = True
    emit_events: bool = True


class SentinelProcess:
    """
    Background watchdog daemon for SENTI OS.

    Monitors system health, detects failures, and can trigger
    recovery or safe shutdown procedures.
    """

    def __init__(
        self,
        boot_manager: Any,
        logs_manager: Any,
        config: Optional[SentinelConfig] = None
    ):
        """
        Initialize sentinel process.

        Args:
            boot_manager: BootManager instance to monitor.
            logs_manager: LogsManager instance for logging.
            config: Optional configuration.
        """
        self.boot_manager = boot_manager
        self.logs_manager = logs_manager
        self.config = config or SentinelConfig()

        # State
        self.state = SentinelState.STOPPED
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Health tracking
        self._health_records: Dict[str, StackHealthRecord] = {}
        self._system_start_time: Optional[datetime] = None
        self._last_check_time: Optional[datetime] = None

        # Statistics
        self._checks_performed = 0
        self._alerts_triggered = 0
        self._recoveries_attempted = 0

        # Callbacks
        self._on_stall_callback: Optional[Callable] = None
        self._on_crash_callback: Optional[Callable] = None
        self._on_recovery_callback: Optional[Callable] = None

    def start(self):
        """Start sentinel process."""
        if self.state in [SentinelState.RUNNING, SentinelState.STARTING]:
            self.logs_manager.append_log(
                "warning",
                "Sentinel already running",
                component="sentinel"
            )
            return

        self.state = SentinelState.STARTING
        self.logs_manager.append_log(
            "info",
            "Starting sentinel process",
            component="sentinel"
        )

        # Initialize health records for all enabled stacks
        for stack_name in self.boot_manager.BOOT_ORDER:
            if self.boot_manager.enabled_stacks.get(stack_name, False):
                self._health_records[stack_name] = StackHealthRecord(
                    stack_name=stack_name,
                    last_heartbeat=datetime.now()
                )

        self._system_start_time = datetime.now()
        self._stop_event.clear()

        # Start monitoring thread
        self._thread = threading.Thread(
            target=self._monitoring_loop,
            name="SentinelProcess",
            daemon=True
        )
        self._thread.start()

        self.state = SentinelState.RUNNING
        self.logs_manager.append_log(
            "info",
            "Sentinel process started",
            component="sentinel"
        )

        self._emit_event("sentinel_started", "Sentinel monitoring active")

    def stop(self):
        """Stop sentinel process."""
        if self.state != SentinelState.RUNNING:
            return

        self.state = SentinelState.STOPPING
        self.logs_manager.append_log(
            "info",
            "Stopping sentinel process",
            component="sentinel"
        )

        # Signal thread to stop
        self._stop_event.set()

        # Wait for thread to finish (with timeout)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        self.state = SentinelState.STOPPED
        self.logs_manager.append_log(
            "info",
            "Sentinel process stopped",
            component="sentinel"
        )

        self._emit_event("sentinel_stopped", "Sentinel monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop (runs in background thread)."""
        while not self._stop_event.is_set():
            try:
                self._perform_health_check()
                self._last_check_time = datetime.now()
                self._checks_performed += 1

                # Sleep with interruptible wait
                self._stop_event.wait(self.config.check_interval_seconds)

            except Exception as e:
                self.logs_manager.append_log(
                    "error",
                    f"Sentinel monitoring error: {str(e)}",
                    component="sentinel"
                )
                # Continue monitoring even if check fails
                time.sleep(self.config.check_interval_seconds)

    def _perform_health_check(self):
        """Perform health check on all stacks."""
        if not self.boot_manager.is_running():
            # System not running, skip check
            return

        current_time = datetime.now()

        # Check each stack
        for stack_name, health_record in self._health_records.items():
            result = self._check_stack_health(stack_name, health_record, current_time)

            # Take action based on result
            if result == HealthCheckResult.STALLED:
                self._handle_stalled_stack(stack_name, health_record)
            elif result == HealthCheckResult.CRASHED:
                self._handle_crashed_stack(stack_name, health_record)
            elif result == HealthCheckResult.DEGRADED:
                self._handle_degraded_stack(stack_name, health_record)

        # Check overall system health
        self._check_system_health()

    def _check_stack_health(
        self,
        stack_name: str,
        health_record: StackHealthRecord,
        current_time: datetime
    ) -> HealthCheckResult:
        """
        Check health of a specific stack.

        Args:
            stack_name: Name of stack to check.
            health_record: Health record for the stack.
            current_time: Current timestamp.

        Returns:
            Health check result.
        """
        # Get stack instance
        stack_info = self.boot_manager.stacks.get(stack_name)
        if not stack_info:
            return HealthCheckResult.UNKNOWN

        # Check if stack has error status
        if stack_info.status.value == "error":
            health_record.status = HealthCheckResult.CRASHED
            health_record.error_count += 1
            health_record.last_error = stack_info.error
            health_record.last_error_time = current_time
            return HealthCheckResult.CRASHED

        # Check heartbeat timeout
        time_since_heartbeat = current_time - health_record.last_heartbeat
        if time_since_heartbeat.total_seconds() > self.config.heartbeat_timeout_seconds:
            health_record.status = HealthCheckResult.STALLED
            return HealthCheckResult.STALLED

        # Check if stack is running
        if stack_info.status.value != "running":
            health_record.status = HealthCheckResult.DEGRADED
            return HealthCheckResult.DEGRADED

        # Update heartbeat
        health_record.last_heartbeat = current_time
        health_record.heartbeat_count += 1
        health_record.status = HealthCheckResult.HEALTHY

        return HealthCheckResult.HEALTHY

    def _handle_stalled_stack(self, stack_name: str, health_record: StackHealthRecord):
        """
        Handle stalled stack detection.

        Args:
            stack_name: Name of stalled stack.
            health_record: Health record for the stack.
        """
        self.logs_manager.append_log(
            "warning",
            f"Stack {stack_name} appears stalled (no heartbeat)",
            component="sentinel",
            details={"stack": stack_name, "last_heartbeat": health_record.last_heartbeat.isoformat()}
        )

        self._alerts_triggered += 1

        self._emit_event(
            "stack_stalled",
            f"Stack {stack_name} stalled",
            stack_name=stack_name
        )

        # Trigger callback if registered
        if self._on_stall_callback:
            try:
                self._on_stall_callback(stack_name, health_record)
            except Exception as e:
                self.logs_manager.append_log(
                    "error",
                    f"Stall callback error: {str(e)}",
                    component="sentinel"
                )

        # Attempt recovery if enabled
        if self.config.auto_recovery_enabled:
            self._attempt_recovery(stack_name)

    def _handle_crashed_stack(self, stack_name: str, health_record: StackHealthRecord):
        """
        Handle crashed stack detection.

        Args:
            stack_name: Name of crashed stack.
            health_record: Health record for the stack.
        """
        # Only log once per error to avoid spam
        if health_record.error_count == 1:
            self.logs_manager.append_log(
                "error",
                f"Stack {stack_name} crashed: {health_record.last_error}",
                component="sentinel",
                details={"stack": stack_name, "error": health_record.last_error}
            )

            self._alerts_triggered += 1

            self._emit_event(
                "stack_crashed",
                f"Stack {stack_name} crashed",
                stack_name=stack_name,
                error=health_record.last_error
            )

            # Trigger callback if registered
            if self._on_crash_callback:
                try:
                    self._on_crash_callback(stack_name, health_record)
                except Exception as e:
                    self.logs_manager.append_log(
                        "error",
                        f"Crash callback error: {str(e)}",
                        component="sentinel"
                    )

        # Check if critical errors warrant shutdown
        if (health_record.error_count >= self.config.max_errors_before_alert and
            self.config.safe_shutdown_on_critical):
            self._trigger_safe_shutdown(f"Stack {stack_name} critical failure")

    def _handle_degraded_stack(self, stack_name: str, health_record: StackHealthRecord):
        """
        Handle degraded stack detection.

        Args:
            stack_name: Name of degraded stack.
            health_record: Health record for the stack.
        """
        # Log degraded status (less severe than crash)
        self.logs_manager.append_log(
            "warning",
            f"Stack {stack_name} in degraded state",
            component="sentinel",
            details={"stack": stack_name}
        )

        self._emit_event(
            "stack_degraded",
            f"Stack {stack_name} degraded",
            stack_name=stack_name
        )

    def _check_system_health(self):
        """Check overall system health."""
        # Count stacks by health status
        health_counts = {
            HealthCheckResult.HEALTHY: 0,
            HealthCheckResult.DEGRADED: 0,
            HealthCheckResult.STALLED: 0,
            HealthCheckResult.CRASHED: 0,
            HealthCheckResult.UNKNOWN: 0
        }

        for health_record in self._health_records.values():
            health_counts[health_record.status] += 1

        # Check if system is critically unhealthy
        total_stacks = len(self._health_records)
        unhealthy_stacks = (
            health_counts[HealthCheckResult.CRASHED] +
            health_counts[HealthCheckResult.STALLED]
        )

        if total_stacks > 0 and unhealthy_stacks >= (total_stacks * 0.5):
            # More than 50% of stacks are unhealthy
            self.logs_manager.append_log(
                "error",
                f"Critical: {unhealthy_stacks}/{total_stacks} stacks unhealthy",
                component="sentinel"
            )

            if self.config.safe_shutdown_on_critical:
                self._trigger_safe_shutdown("System critically unhealthy")

    def _attempt_recovery(self, stack_name: str):
        """
        Attempt to recover a failed stack.

        Args:
            stack_name: Name of stack to recover.
        """
        self.logs_manager.append_log(
            "info",
            f"Attempting recovery for stack {stack_name}",
            component="sentinel"
        )

        self._recoveries_attempted += 1

        # Trigger recovery callback if registered
        if self._on_recovery_callback:
            try:
                self._on_recovery_callback(stack_name)
            except Exception as e:
                self.logs_manager.append_log(
                    "error",
                    f"Recovery callback error: {str(e)}",
                    component="sentinel"
                )

        # Note: Actual recovery logic would be implemented here
        # For now, just log the attempt

    def _trigger_safe_shutdown(self, reason: str):
        """
        Trigger safe system shutdown.

        Args:
            reason: Reason for shutdown.
        """
        self.logs_manager.append_log(
            "critical",
            f"Triggering safe shutdown: {reason}",
            component="sentinel"
        )

        self._emit_event(
            "safe_shutdown_triggered",
            f"Safe shutdown: {reason}"
        )

        # Initiate shutdown through boot manager
        try:
            self.boot_manager.stop()
        except Exception as e:
            self.logs_manager.append_log(
                "error",
                f"Shutdown failed: {str(e)}",
                component="sentinel"
            )

    def _emit_event(
        self,
        event_type: str,
        message: str,
        stack_name: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Emit event to FAZA 19 event bus.

        Args:
            event_type: Type of event.
            message: Event message.
            stack_name: Optional stack name.
            error: Optional error message.
        """
        if not self.config.emit_events:
            return

        # Try to emit to FAZA 19 event bus
        try:
            faza19 = self.boot_manager.get_stack("faza19")
            if faza19 and hasattr(faza19, 'event_bus'):
                faza19.event_bus.publish(
                    category="sentinel",
                    event_type=event_type,
                    data={
                        "message": message,
                        "stack_name": stack_name,
                        "error": error,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        except Exception:
            # Silently ignore event bus errors
            pass

    def register_stall_callback(self, callback: Callable):
        """
        Register callback for stall detection.

        Args:
            callback: Callback function(stack_name, health_record).
        """
        self._on_stall_callback = callback

    def register_crash_callback(self, callback: Callable):
        """
        Register callback for crash detection.

        Args:
            callback: Callback function(stack_name, health_record).
        """
        self._on_crash_callback = callback

    def register_recovery_callback(self, callback: Callable):
        """
        Register callback for recovery attempts.

        Args:
            callback: Callback function(stack_name).
        """
        self._on_recovery_callback = callback

    def get_status(self) -> Dict[str, Any]:
        """
        Get sentinel status.

        Returns:
            Dictionary with sentinel status.
        """
        return {
            "state": self.state.value,
            "running": self.state == SentinelState.RUNNING,
            "system_start_time": (
                self._system_start_time.isoformat()
                if self._system_start_time else None
            ),
            "last_check_time": (
                self._last_check_time.isoformat()
                if self._last_check_time else None
            ),
            "statistics": {
                "checks_performed": self._checks_performed,
                "alerts_triggered": self._alerts_triggered,
                "recoveries_attempted": self._recoveries_attempted
            },
            "config": {
                "check_interval_seconds": self.config.check_interval_seconds,
                "heartbeat_timeout_seconds": self.config.heartbeat_timeout_seconds,
                "auto_recovery_enabled": self.config.auto_recovery_enabled,
                "safe_shutdown_on_critical": self.config.safe_shutdown_on_critical
            },
            "health_records": {
                name: {
                    "status": record.status.value,
                    "last_heartbeat": record.last_heartbeat.isoformat(),
                    "heartbeat_count": record.heartbeat_count,
                    "error_count": record.error_count,
                    "last_error": record.last_error
                }
                for name, record in self._health_records.items()
            }
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get sentinel statistics.

        Returns:
            Dictionary with statistics.
        """
        uptime_seconds = 0
        if self._system_start_time:
            uptime_seconds = (datetime.now() - self._system_start_time).total_seconds()

        return {
            "uptime_seconds": uptime_seconds,
            "checks_performed": self._checks_performed,
            "alerts_triggered": self._alerts_triggered,
            "recoveries_attempted": self._recoveries_attempted,
            "stacks_monitored": len(self._health_records),
            "healthy_stacks": sum(
                1 for r in self._health_records.values()
                if r.status == HealthCheckResult.HEALTHY
            ),
            "degraded_stacks": sum(
                1 for r in self._health_records.values()
                if r.status == HealthCheckResult.DEGRADED
            ),
            "stalled_stacks": sum(
                1 for r in self._health_records.values()
                if r.status == HealthCheckResult.STALLED
            ),
            "crashed_stacks": sum(
                1 for r in self._health_records.values()
                if r.status == HealthCheckResult.CRASHED
            )
        }

    def is_running(self) -> bool:
        """Check if sentinel is running."""
        return self.state == SentinelState.RUNNING

    def force_health_check(self):
        """Force immediate health check (useful for testing)."""
        if self.state == SentinelState.RUNNING:
            self._perform_health_check()

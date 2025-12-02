"""
FAZA 20 - Heartbeat Monitor

Generates periodic heartbeats, checks module responsiveness,
emits status events to FAZA 19 event bus, and detects failures.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
import time


class HeartbeatStatus(Enum):
    """Heartbeat status."""
    BEATING = "beating"
    DELAYED = "delayed"
    MISSED = "missed"
    STOPPED = "stopped"


@dataclass
class HeartbeatRecord:
    """Record of a single heartbeat."""
    module_name: str
    timestamp: datetime
    sequence_number: int
    response_time_ms: float
    status: HeartbeatStatus
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HeartbeatMonitor:
    """
    Monitors module health via periodic heartbeats.

    Features:
    - Configurable heartbeat interval
    - Response time tracking
    - Failure detection
    - Event emission to FAZA 19 event bus
    - Warning/error generation
    """

    def __init__(
        self,
        interval_seconds: int = 10,
        timeout_seconds: int = 5,
        missed_threshold: int = 3
    ):
        """
        Initialize heartbeat monitor.

        Args:
            interval_seconds: Time between heartbeats.
            timeout_seconds: Timeout for heartbeat response.
            missed_threshold: Number of missed beats before ERROR.
        """
        self.interval = interval_seconds
        self.timeout = timeout_seconds
        self.missed_threshold = missed_threshold

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._heartbeat_records: Dict[str, List[HeartbeatRecord]] = {}
        self._sequence_numbers: Dict[str, int] = {}
        self._missed_counts: Dict[str, int] = {}
        self._event_bus = None
        self._modules: Dict[str, Any] = {}

        # Statistics
        self._total_beats = 0
        self._total_missed = 0
        self._start_time: Optional[datetime] = None

    def register_event_bus(self, event_bus: Any):
        """
        Register FAZA 19 event bus for status events.

        Args:
            event_bus: FAZA 19 UILEventBus instance.
        """
        self._event_bus = event_bus

    def register_module(self, module_name: str, module_ref: Any):
        """
        Register module for heartbeat monitoring.

        Args:
            module_name: Module identifier.
            module_ref: Reference to module object.
        """
        self._modules[module_name] = module_ref
        self._sequence_numbers[module_name] = 0
        self._missed_counts[module_name] = 0
        self._heartbeat_records[module_name] = []

    def start(self):
        """Start heartbeat monitoring."""
        if self._running:
            return

        self._running = True
        self._start_time = datetime.utcnow()
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop heartbeat monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.timeout + 1)
            self._thread = None

    def get_heartbeat_status(self, module_name: str) -> Optional[HeartbeatStatus]:
        """
        Get current heartbeat status for module.

        Args:
            module_name: Module identifier.

        Returns:
            HeartbeatStatus if module registered, None otherwise.
        """
        if module_name not in self._heartbeat_records:
            return None

        records = self._heartbeat_records[module_name]
        if not records:
            return HeartbeatStatus.STOPPED

        latest = records[-1]
        return latest.status

    def get_latest_heartbeat(self, module_name: str) -> Optional[HeartbeatRecord]:
        """
        Get latest heartbeat record for module.

        Args:
            module_name: Module identifier.

        Returns:
            Latest HeartbeatRecord if available.
        """
        records = self._heartbeat_records.get(module_name, [])
        return records[-1] if records else None

    def get_heartbeat_history(
        self,
        module_name: str,
        limit: int = 10
    ) -> List[HeartbeatRecord]:
        """
        Get recent heartbeat history.

        Args:
            module_name: Module identifier.
            limit: Maximum number of records to return.

        Returns:
            List of recent HeartbeatRecords.
        """
        records = self._heartbeat_records.get(module_name, [])
        return records[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get heartbeat monitoring statistics."""
        uptime = 0
        if self._start_time:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return {
            "running": self._running,
            "uptime_seconds": uptime,
            "total_beats": self._total_beats,
            "total_missed": self._total_missed,
            "success_rate": self._calculate_success_rate(),
            "modules_monitored": len(self._modules),
            "interval_seconds": self.interval,
            "timeout_seconds": self.timeout,
            "missed_threshold": self.missed_threshold
        }

    def get_module_statistics(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific module."""
        if module_name not in self._heartbeat_records:
            return None

        records = self._heartbeat_records[module_name]
        if not records:
            return {
                "module_name": module_name,
                "total_beats": 0,
                "missed_count": 0,
                "avg_response_time_ms": 0.0,
                "last_heartbeat": None
            }

        total = len(records)
        missed = sum(1 for r in records if r.status == HeartbeatStatus.MISSED)
        avg_response = sum(r.response_time_ms for r in records) / total

        return {
            "module_name": module_name,
            "total_beats": total,
            "missed_count": missed,
            "avg_response_time_ms": avg_response,
            "last_heartbeat": records[-1].timestamp.isoformat(),
            "current_status": records[-1].status.value
        }

    def _heartbeat_loop(self):
        """Main heartbeat monitoring loop."""
        while self._running:
            # Send heartbeats to all modules
            for module_name in self._modules.keys():
                self._send_heartbeat(module_name)

            # Sleep until next interval
            time.sleep(self.interval)

    def _send_heartbeat(self, module_name: str):
        """
        Send heartbeat to module and record result.

        Args:
            module_name: Module to send heartbeat to.
        """
        module_ref = self._modules[module_name]
        sequence = self._sequence_numbers[module_name]
        self._sequence_numbers[module_name] += 1

        start_time = time.time()
        status = HeartbeatStatus.BEATING
        response_time_ms = 0.0

        try:
            # Check if module has heartbeat method
            if hasattr(module_ref, 'heartbeat'):
                # Call heartbeat with timeout
                result = self._call_with_timeout(
                    module_ref.heartbeat,
                    timeout=self.timeout
                )

                response_time_ms = (time.time() - start_time) * 1000

                if result is None:
                    # Timeout
                    status = HeartbeatStatus.DELAYED
                    self._missed_counts[module_name] += 1
                else:
                    # Success
                    status = HeartbeatStatus.BEATING
                    self._missed_counts[module_name] = 0
            else:
                # Module doesn't support heartbeat, check if alive
                if hasattr(module_ref, 'get_status'):
                    module_ref.get_status()
                    response_time_ms = (time.time() - start_time) * 1000
                    status = HeartbeatStatus.BEATING
                    self._missed_counts[module_name] = 0
                else:
                    status = HeartbeatStatus.STOPPED
                    self._missed_counts[module_name] += 1

        except Exception:
            status = HeartbeatStatus.MISSED
            self._missed_counts[module_name] += 1
            response_time_ms = (time.time() - start_time) * 1000

        # Check if exceeded missed threshold
        if self._missed_counts[module_name] >= self.missed_threshold:
            status = HeartbeatStatus.STOPPED

        # Create heartbeat record
        record = HeartbeatRecord(
            module_name=module_name,
            timestamp=datetime.utcnow(),
            sequence_number=sequence,
            response_time_ms=response_time_ms,
            status=status,
            metadata={
                "missed_count": self._missed_counts[module_name],
                "threshold": self.missed_threshold
            }
        )

        # Store record
        self._heartbeat_records[module_name].append(record)

        # Keep only last 100 records per module
        if len(self._heartbeat_records[module_name]) > 100:
            self._heartbeat_records[module_name] = self._heartbeat_records[module_name][-100:]

        # Update statistics
        self._total_beats += 1
        if status in [HeartbeatStatus.MISSED, HeartbeatStatus.STOPPED]:
            self._total_missed += 1

        # Emit event to event bus
        self._emit_heartbeat_event(record)

    def _call_with_timeout(self, func: Callable, timeout: int) -> Optional[Any]:
        """
        Call function with timeout.

        Args:
            func: Function to call.
            timeout: Timeout in seconds.

        Returns:
            Function result or None if timeout.
        """
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            # Timeout
            return None

        if exception[0]:
            raise exception[0]

        return result[0]

    def _emit_heartbeat_event(self, record: HeartbeatRecord):
        """Emit heartbeat event to FAZA 19 event bus."""
        if not self._event_bus:
            return

        event_category = "OS_STATUS"

        if record.status == HeartbeatStatus.STOPPED:
            event_category = "ERROR"
        elif record.status in [HeartbeatStatus.DELAYED, HeartbeatStatus.MISSED]:
            event_category = "WARNING"

        event_data = {
            "type": "heartbeat",
            "module": record.module_name,
            "status": record.status.value,
            "sequence": record.sequence_number,
            "response_time_ms": record.response_time_ms,
            "timestamp": record.timestamp.isoformat()
        }

        try:
            if hasattr(self._event_bus, 'publish'):
                self._event_bus.publish(event_category, event_data)
        except Exception:
            # Silently fail if event bus not available
            pass

    def _calculate_success_rate(self) -> float:
        """Calculate heartbeat success rate."""
        if self._total_beats == 0:
            return 1.0
        return 1.0 - (self._total_missed / self._total_beats)


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "heartbeat_monitor",
        "faza": "20",
        "version": "1.0.0",
        "description": "Periodic heartbeat monitoring with failure detection"
    }

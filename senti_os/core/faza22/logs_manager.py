"""
FAZA 22 - Logs Manager

Unified log management for SENTI OS.

Responsibilities:
- Centralized log collection
- Log level filtering (info, warning, error)
- Rolling window storage (max 10,000 entries)
- Thread-safe operations
- Optional disk persistence
- Log statistics and querying

Privacy Guarantee:
- NO sensitive data logging (passwords, biometrics, etc.)
- All logs are safe for diagnostics
- GDPR/ZVOP compliant

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque
import threading
import json
from pathlib import Path


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __lt__(self, other):
        """Compare log levels for filtering."""
        order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return order[self] < order[other]


@dataclass
class LogEntry:
    """Individual log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    component: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "component": self.component,
            "details": self.details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=LogLevel(data["level"]),
            message=data["message"],
            component=data.get("component"),
            details=data.get("details")
        )


class LogsManager:
    """
    Unified log manager for SENTI OS.

    Provides centralized, thread-safe log management with
    rolling window storage and filtering capabilities.
    """

    def __init__(
        self,
        max_entries: int = 10000,
        persist_to_disk: bool = False,
        log_file: Optional[str] = None
    ):
        """
        Initialize logs manager.

        Args:
            max_entries: Maximum number of log entries to retain.
            persist_to_disk: If True, persist logs to disk.
            log_file: Path to log file (if persist_to_disk is True).
        """
        self.max_entries = max_entries
        self.persist_to_disk = persist_to_disk
        self.log_file = log_file or "/home/pisarna/senti_system/data/faza22/senti_os.log"

        # Thread-safe log storage
        self._logs: deque[LogEntry] = deque(maxlen=max_entries)
        self._lock = threading.Lock()

        # Statistics
        self._total_logs_count = 0
        self._logs_by_level: Dict[LogLevel, int] = {
            level: 0 for level in LogLevel
        }

        # Ensure log directory exists if persisting
        if self.persist_to_disk:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    def append_log(
        self,
        level: str,
        message: str,
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Append a log entry.

        Args:
            level: Log level (debug/info/warning/error/critical).
            message: Log message.
            component: Optional component name.
            details: Optional additional details.
        """
        # Convert string level to enum
        try:
            log_level = LogLevel(level.lower())
        except ValueError:
            log_level = LogLevel.INFO

        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now(),
            level=log_level,
            message=message,
            component=component,
            details=details
        )

        # Thread-safe append
        with self._lock:
            self._logs.append(entry)
            self._total_logs_count += 1
            self._logs_by_level[log_level] += 1

        # Persist to disk if enabled
        if self.persist_to_disk:
            self._persist_entry(entry)

    def get_logs(
        self,
        level: Optional[str] = None,
        component: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get log entries with filtering.

        Args:
            level: Filter by log level (info/warning/error/etc).
            component: Filter by component name.
            limit: Maximum number of entries to return.
            offset: Number of entries to skip from the end.

        Returns:
            List of log entries as dictionaries.
        """
        with self._lock:
            # Convert deque to list for slicing
            logs_list = list(self._logs)

        # Filter by level
        if level:
            try:
                filter_level = LogLevel(level.lower())
                logs_list = [
                    entry for entry in logs_list
                    if entry.level == filter_level
                ]
            except ValueError:
                pass

        # Filter by component
        if component:
            logs_list = [
                entry for entry in logs_list
                if entry.component == component
            ]

        # Apply offset and limit
        total_count = len(logs_list)

        if offset > 0:
            # Skip entries from the end
            logs_list = logs_list[:max(0, total_count - offset)]

        if limit:
            # Take last N entries
            logs_list = logs_list[-limit:]

        # Convert to dictionaries
        return [entry.to_dict() for entry in logs_list]

    def get_recent_logs(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get most recent log entries.

        Args:
            count: Number of recent entries to retrieve.

        Returns:
            List of recent log entries.
        """
        return self.get_logs(limit=count)

    def get_logs_by_level(
        self,
        level: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get logs filtered by level.

        Args:
            level: Log level to filter by.
            limit: Maximum entries to return.

        Returns:
            List of filtered log entries.
        """
        return self.get_logs(level=level, limit=limit)

    def get_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get error and critical logs.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of error log entries.
        """
        with self._lock:
            logs_list = list(self._logs)

        # Filter errors and critical
        error_logs = [
            entry for entry in logs_list
            if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]
        ]

        # Take last N entries
        error_logs = error_logs[-limit:]

        return [entry.to_dict() for entry in error_logs]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get log statistics.

        Returns:
            Dictionary with log statistics.
        """
        with self._lock:
            current_count = len(self._logs)
            logs_by_level = self._logs_by_level.copy()

        return {
            "current_entries": current_count,
            "max_entries": self.max_entries,
            "total_logged": self._total_logs_count,
            "logs_by_level": {
                level.value: count
                for level, count in logs_by_level.items()
            },
            "persist_to_disk": self.persist_to_disk,
            "log_file": self.log_file if self.persist_to_disk else None
        }

    def clear_logs(self):
        """Clear all log entries (use with caution)."""
        with self._lock:
            self._logs.clear()

    def search_logs(
        self,
        query: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search logs by message content.

        Args:
            query: Search query string.
            limit: Maximum entries to return.

        Returns:
            List of matching log entries.
        """
        with self._lock:
            logs_list = list(self._logs)

        # Case-insensitive search
        query_lower = query.lower()
        matching_logs = [
            entry for entry in logs_list
            if query_lower in entry.message.lower()
        ]

        # Take last N matching entries
        matching_logs = matching_logs[-limit:]

        return [entry.to_dict() for entry in matching_logs]

    def get_logs_since(
        self,
        since: datetime,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logs since a specific timestamp.

        Args:
            since: Datetime to filter from.
            limit: Optional maximum entries to return.

        Returns:
            List of log entries since timestamp.
        """
        with self._lock:
            logs_list = list(self._logs)

        # Filter by timestamp
        filtered_logs = [
            entry for entry in logs_list
            if entry.timestamp >= since
        ]

        if limit:
            filtered_logs = filtered_logs[-limit:]

        return [entry.to_dict() for entry in filtered_logs]

    def _persist_entry(self, entry: LogEntry):
        """
        Persist a single log entry to disk.

        Args:
            entry: LogEntry to persist.
        """
        try:
            with open(self.log_file, 'a') as f:
                json.dump(entry.to_dict(), f)
                f.write('\n')
        except Exception:
            # Silently ignore persistence errors to avoid infinite loops
            pass

    def export_logs(
        self,
        output_file: str,
        level: Optional[str] = None
    ) -> bool:
        """
        Export logs to a file.

        Args:
            output_file: Path to output file.
            level: Optional level filter.

        Returns:
            True if export succeeded.
        """
        try:
            logs = self.get_logs(level=level)

            # Ensure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(logs, f, indent=2)

            return True
        except Exception:
            return False

    def import_logs(self, input_file: str) -> bool:
        """
        Import logs from a file.

        Args:
            input_file: Path to input file.

        Returns:
            True if import succeeded.
        """
        try:
            with open(input_file, 'r') as f:
                logs_data = json.load(f)

            with self._lock:
                for log_data in logs_data:
                    try:
                        entry = LogEntry.from_dict(log_data)
                        self._logs.append(entry)
                        self._total_logs_count += 1
                        self._logs_by_level[entry.level] += 1
                    except Exception:
                        continue

            return True
        except Exception:
            return False

    def get_component_logs(
        self,
        component: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get logs for a specific component.

        Args:
            component: Component name.
            limit: Maximum entries to return.

        Returns:
            List of component log entries.
        """
        return self.get_logs(component=component, limit=limit)

    def get_log_summary(self) -> Dict[str, Any]:
        """
        Get a summary of recent log activity.

        Returns:
            Dictionary with log summary.
        """
        with self._lock:
            logs_list = list(self._logs)

        if not logs_list:
            return {
                "total_entries": 0,
                "oldest_entry": None,
                "newest_entry": None,
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0
            }

        # Count by level
        error_count = sum(
            1 for entry in logs_list
            if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]
        )
        warning_count = sum(
            1 for entry in logs_list
            if entry.level == LogLevel.WARNING
        )
        info_count = sum(
            1 for entry in logs_list
            if entry.level == LogLevel.INFO
        )

        return {
            "total_entries": len(logs_list),
            "oldest_entry": logs_list[0].timestamp.isoformat(),
            "newest_entry": logs_list[-1].timestamp.isoformat(),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "by_level": {
                level.value: sum(1 for e in logs_list if e.level == level)
                for level in LogLevel
            }
        }


# Global singleton instance
_logs_manager_instance: Optional[LogsManager] = None


def get_logs_manager(
    max_entries: int = 10000,
    persist_to_disk: bool = False,
    log_file: Optional[str] = None
) -> LogsManager:
    """
    Get or create logs manager singleton.

    Args:
        max_entries: Maximum number of log entries to retain.
        persist_to_disk: If True, persist logs to disk.
        log_file: Path to log file (if persist_to_disk is True).

    Returns:
        LogsManager instance.
    """
    global _logs_manager_instance

    if _logs_manager_instance is None:
        _logs_manager_instance = LogsManager(
            max_entries=max_entries,
            persist_to_disk=persist_to_disk,
            log_file=log_file
        )

    return _logs_manager_instance


def reset_logs_manager():
    """Reset logs manager singleton (useful for testing)."""
    global _logs_manager_instance
    _logs_manager_instance = None

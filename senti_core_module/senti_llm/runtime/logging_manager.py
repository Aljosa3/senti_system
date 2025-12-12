"""
FAZA D.1.1 — Logging Manager
-----------------------------
Centralized, thread-safe logging system for Senti OS Runtime.

Features:
- Multiple log levels (DEBUG, INFO, WARN, ERROR)
- Per-module loggers
- File logging support
- Thread-safe operations
- Non-blocking (never throws)
- Context enrichment (timestamp, module, phase)

Design Philosophy:
- NEVER throw exceptions from logging code
- All operations must be thread-safe
- Logging must not affect runtime performance
"""

from __future__ import annotations

import os
import time
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import IntEnum


class LogLevel(IntEnum):
    """Log level enumeration."""
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class LogRecord:
    """
    Represents a single log entry.

    Enriched with metadata for structured logging.
    """

    def __init__(
        self,
        level: LogLevel,
        message: str,
        module_name: str = "system",
        phase: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ):
        self.level = level
        self.message = message
        self.module_name = module_name
        self.phase = phase
        self.context = context or {}
        self.timestamp = time.time()
        self.datetime = datetime.now()

    def format(self) -> str:
        """
        Format log record as string.

        Format: [TIMESTAMP] [LEVEL] [MODULE] message

        Returns:
            Formatted log string
        """
        timestamp_str = self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        level_str = self.level.name.ljust(5)
        module_str = self.module_name.ljust(20)

        return f"[{timestamp_str}] [{level_str}] [{module_str}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert log record to dict.

        Returns:
            Dict representation
        """
        return {
            "timestamp": self.timestamp,
            "datetime": self.datetime.isoformat(),
            "level": self.level.name,
            "module": self.module_name,
            "phase": self.phase,
            "message": self.message,
            "context": self.context
        }


class LogSink:
    """
    Base class for log output destinations.
    """

    def write(self, record: LogRecord):
        """Write log record to sink."""
        raise NotImplementedError


class FileSink(LogSink):
    """
    File-based log sink.

    Writes logs to specified file path.
    Thread-safe with file locking.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._lock = threading.Lock()

        # Ensure directory exists
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        except Exception:
            # Never throw from logging
            pass

    def write(self, record: LogRecord):
        """Write log record to file."""
        try:
            with self._lock:
                with open(self.filepath, "a", encoding="utf-8") as f:
                    f.write(record.format() + "\n")
        except Exception:
            # Never throw from logging
            pass


class ConsoleSink(LogSink):
    """
    Console-based log sink.

    Writes logs to stdout.
    """

    def write(self, record: LogRecord):
        """Write log record to console."""
        try:
            print(record.format())
        except Exception:
            # Never throw from logging
            pass


class Logger:
    """
    Per-module logger instance.

    Provides logging methods for different levels.
    Automatically enriches logs with context.
    """

    def __init__(
        self,
        module_name: str,
        manager: 'LoggingManager',
        phase: str = "unknown"
    ):
        self.module_name = module_name
        self.manager = manager
        self.phase = phase
        self._context: Dict[str, Any] = {}

    def set_context(self, key: str, value: Any):
        """
        Add context to logger.

        Args:
            key: Context key
            value: Context value
        """
        try:
            self._context[key] = value
        except Exception:
            pass

    def clear_context(self):
        """Clear logger context."""
        try:
            self._context = {}
        except Exception:
            pass

    def debug(self, message: str, **kwargs):
        """Log DEBUG level message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log INFO level message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warn(self, message: str, **kwargs):
        """Log WARN level message."""
        self.log(LogLevel.WARN, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log ERROR level message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def log(self, level: LogLevel, message: str, **kwargs):
        """
        Log message at specified level.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context
        """
        try:
            # Check if level is enabled
            if level < self.manager.global_level:
                return

            # Merge context
            context = {**self._context, **kwargs}

            # Create log record
            record = LogRecord(
                level=level,
                message=message,
                module_name=self.module_name,
                phase=self.phase,
                context=context
            )

            # Write to manager
            self.manager._write_record(record)

        except Exception:
            # Never throw from logging
            pass


class LoggingManager:
    """
    Centralized logging manager.

    Manages:
    - Global log level
    - Per-module loggers
    - Log sinks (file, console)
    - Thread-safe operations

    Usage:
        manager = LoggingManager()
        logger = manager.get_logger("my_module")
        logger.info("Hello world")
    """

    def __init__(
        self,
        global_level: LogLevel = LogLevel.INFO,
        enable_console: bool = False
    ):
        self.global_level = global_level
        self._loggers: Dict[str, Logger] = {}
        self._sinks: List[LogSink] = []
        self._lock = threading.Lock()

        # Add console sink if enabled
        if enable_console:
            self.add_sink(ConsoleSink())

    def get_logger(self, module_name: str, phase: str = "unknown") -> Logger:
        """
        Get or create logger for module.

        Args:
            module_name: Module name
            phase: Runtime phase (e.g., "FAZA 42")

        Returns:
            Logger instance
        """
        try:
            with self._lock:
                if module_name not in self._loggers:
                    self._loggers[module_name] = Logger(
                        module_name=module_name,
                        manager=self,
                        phase=phase
                    )

                return self._loggers[module_name]
        except Exception:
            # Fallback: return no-op logger
            return Logger("error", self, "unknown")

    def set_log_level(self, level: LogLevel):
        """
        Set global log level.

        Args:
            level: New log level
        """
        try:
            self.global_level = level
        except Exception:
            pass

    def enable_file_logging(
        self,
        filepath: str = "senti_data/logs/system.log"
    ):
        """
        Enable file logging.

        Args:
            filepath: Path to log file
        """
        try:
            # Make path absolute if relative
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)

            sink = FileSink(filepath)
            self.add_sink(sink)
        except Exception:
            # Never throw from logging
            pass

    def add_sink(self, sink: LogSink):
        """
        Add log sink.

        Args:
            sink: LogSink instance
        """
        try:
            with self._lock:
                self._sinks.append(sink)
        except Exception:
            pass

    def _write_record(self, record: LogRecord):
        """
        Write log record to all sinks.

        Args:
            record: LogRecord to write
        """
        try:
            with self._lock:
                for sink in self._sinks:
                    try:
                        sink.write(record)
                    except Exception:
                        # Never let sink error break logging
                        pass
        except Exception:
            # Never throw from logging
            pass

    def flush(self):
        """Flush all sinks (no-op for now)."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.

        Returns:
            Stats dict
        """
        try:
            with self._lock:
                return {
                    "global_level": self.global_level.name,
                    "logger_count": len(self._loggers),
                    "sink_count": len(self._sinks),
                    "modules": list(self._loggers.keys())
                }
        except Exception:
            return {}


# Global singleton instance (lazy-initialized)
_global_logging_manager: Optional[LoggingManager] = None


def get_global_logging_manager() -> LoggingManager:
    """
    Get global logging manager singleton.

    Lazy-initializes on first access.

    Returns:
        Global LoggingManager instance
    """
    global _global_logging_manager

    if _global_logging_manager is None:
        _global_logging_manager = LoggingManager(
            global_level=LogLevel.INFO,
            enable_console=False
        )

        # Enable file logging by default
        _global_logging_manager.enable_file_logging()

    return _global_logging_manager

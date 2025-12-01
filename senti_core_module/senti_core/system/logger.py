"""
Senti Logger
Location: senti_core/system/logger.py

Simple logging utility for Senti System.
"""

import sys
from datetime import datetime


class SentiLogger:
    """
    Simple logger for Senti System.
    """

    def __init__(self, name: str = "senti"):
        self.name = name

    def log(self, level: str, message: str):
        """
        Log a message with the specified level.

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_upper = level.upper()
        log_message = f"[{timestamp}] [{level_upper}] {self.name}: {message}"

        if level in ("error", "critical"):
            print(log_message, file=sys.stderr)
        else:
            print(log_message)

    def debug(self, message: str):
        """Log debug message"""
        self.log("debug", message)

    def info(self, message: str):
        """Log info message"""
        self.log("info", message)

    def warning(self, message: str):
        """Log warning message"""
        self.log("warning", message)

    def error(self, message: str):
        """Log error message"""
        self.log("error", message)

    def critical(self, message: str):
        """Log critical message"""
        self.log("critical", message)

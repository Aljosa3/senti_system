"""
CORE Lock Violation Logger
---------------------------
Centralized logging for CORE lock violations and security events.

All violations are logged with:
- Timestamp
- Violation type
- Context (file, operation, etc.)
- Stack trace (if applicable)
- Session information (if available)
"""

import json
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class ViolationRecord:
    """Record of a CORE lock or security violation."""
    timestamp: str
    violation_type: str  # "CORE_MUTATION", "UNAUTHORIZED_ACCESS", "SESSION_EXPIRED", etc.
    severity: str  # "CRITICAL", "ERROR", "WARNING"
    message: str
    context: Dict[str, Any]
    stack_trace: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


class ViolationLogger:
    """
    Centralized logger for CORE lock violations and security events.

    Provides append-only, immutable audit trail of all violations.
    """

    def __init__(self, repo_root: str):
        """
        Initialize violation logger.

        Args:
            repo_root: Absolute path to repository root
        """
        self.repo_root = Path(repo_root)
        self.violation_log = self.repo_root / ".core_violations.jsonl"

        # Ensure log exists
        if not self.violation_log.exists():
            self.violation_log.touch()

    def log_violation(
        self,
        violation_type: str,
        severity: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        include_stack: bool = True
    ) -> None:
        """
        Log a violation to the audit trail.

        Args:
            violation_type: Type of violation
            severity: Severity level
            message: Human-readable description
            context: Additional context information
            include_stack: Include stack trace if True
        """
        # Get stack trace if requested
        stack_trace = None
        if include_stack:
            stack_trace = traceback.format_exc()
            if stack_trace == "NoneType: None\n":
                stack_trace = None  # No actual exception

        # Create record
        record = ViolationRecord(
            timestamp=datetime.utcnow().isoformat() + "Z",
            violation_type=violation_type,
            severity=severity,
            message=message,
            context=context or {},
            stack_trace=stack_trace
        )

        # Append to log (fail-closed: if logging fails, raise exception)
        try:
            with open(self.violation_log, 'a') as f:
                f.write(record.to_json() + "\n")
        except IOError as e:
            # If we can't log violations, fail loudly
            raise RuntimeError(
                f"CRITICAL: Failed to log security violation to {self.violation_log}.\n"
                f"Violation: {violation_type}\n"
                f"Error: {e}\n"
                "System cannot proceed without violation logging."
            ) from e

    def log_core_mutation_attempt(
        self,
        file_path: str,
        operation: str,
        **context
    ) -> None:
        """Log attempted CORE mutation when locked."""
        self.log_violation(
            violation_type="CORE_MUTATION_ATTEMPT",
            severity="CRITICAL",
            message=f"Attempted to {operation} CORE file when locked: {file_path}",
            context={"file_path": file_path, "operation": operation, **context}
        )

    def log_unauthorized_operation(
        self,
        operation: str,
        reason: str,
        **context
    ) -> None:
        """Log unauthorized operation attempt."""
        self.log_violation(
            violation_type="UNAUTHORIZED_OPERATION",
            severity="ERROR",
            message=f"Unauthorized operation attempted: {operation}. Reason: {reason}",
            context={"operation": operation, "reason": reason, **context}
        )

    def log_session_violation(
        self,
        violation: str,
        **context
    ) -> None:
        """Log session-related violation."""
        self.log_violation(
            violation_type="SESSION_VIOLATION",
            severity="ERROR",
            message=f"Session violation: {violation}",
            context=context
        )

    def log_integrity_violation(
        self,
        file_path: str,
        expected_hash: str,
        actual_hash: str,
        **context
    ) -> None:
        """Log file integrity violation."""
        self.log_violation(
            violation_type="INTEGRITY_VIOLATION",
            severity="CRITICAL",
            message=f"File integrity violation detected: {file_path}",
            context={
                "file_path": file_path,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                **context
            }
        )

    def get_recent_violations(self, count: int = 10) -> list:
        """
        Get most recent violations.

        Args:
            count: Number of violations to retrieve

        Returns:
            List of violation records (most recent first)
        """
        if not self.violation_log.exists():
            return []

        try:
            with open(self.violation_log, 'r') as f:
                lines = f.readlines()

            # Get last N lines
            recent_lines = lines[-count:]

            # Parse JSON
            violations = []
            for line in recent_lines:
                try:
                    violations.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

            return list(reversed(violations))  # Most recent first

        except IOError:
            return []


def get_violation_logger(repo_root: Optional[str] = None) -> ViolationLogger:
    """
    Get singleton violation logger.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        ViolationLogger instance
    """
    if repo_root is None:
        # Auto-detect repo root
        repo_root = Path(__file__).parent.parent.parent

    return ViolationLogger(str(repo_root))

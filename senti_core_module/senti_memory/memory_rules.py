"""
Memory Rules - FAZA 12 (integrates with FAZA 8)
Location: senti_core_module/senti_memory/memory_rules.py

Security validations for memory operations:
- Size limits
- Sensitive data detection
- Action whitelisting
- Privacy guards
"""

import re
from typing import Any, Dict, List


class MemoryRules:
    """
    Security and validation rules for memory operations.
    Integrates with FAZA 8 Security Manager.
    """

    # Size limits (bytes)
    MAX_WORKING_MEMORY_SIZE = 1024 * 1024  # 1 MB per item
    MAX_EPISODIC_EVENT_SIZE = 512 * 1024   # 512 KB per event
    MAX_SEMANTIC_FACT_SIZE = 2 * 1024 * 1024  # 2 MB per fact
    MAX_EPISODIC_EVENTS_COUNT = 100000  # 100k events max
    MAX_SEMANTIC_FACTS_COUNT = 50000    # 50k facts max

    # Sensitive data patterns
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (may be allowed)
        r'password\s*[:=is]\s*[\'"]?([^\'"]+)[\'"]?',  # Password in text
        r'api[_-]?key\s*[:=]\s*[\'"]?([^\'"]+)[\'"]?',  # API key
        r'secret\s*[:=]\s*[\'"]?([^\'"]+)[\'"]?',  # Secret
    ]

    # Allowed memory action types
    ALLOWED_ACTIONS = {
        "add", "get", "remove", "update", "clear",
        "record", "retrieve", "save_fact", "search",
        "consolidate", "prune", "cleanup"
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize memory rules.

        Args:
            strict_mode: Enable strict security validations
        """
        self.strict_mode = strict_mode

    # =====================================================
    # SIZE VALIDATIONS
    # =====================================================

    def validate_size(self, data: Any, memory_type: str) -> tuple[bool, str]:
        """
        Validate data size limits.

        Args:
            data: Data to validate
            memory_type: Type of memory (working, episodic, semantic)

        Returns:
            (is_valid, error_message)
        """
        try:
            import sys
            size = sys.getsizeof(str(data))

            limits = {
                "working": self.MAX_WORKING_MEMORY_SIZE,
                "episodic": self.MAX_EPISODIC_EVENT_SIZE,
                "semantic": self.MAX_SEMANTIC_FACT_SIZE
            }

            max_size = limits.get(memory_type, self.MAX_WORKING_MEMORY_SIZE)

            if size > max_size:
                return False, f"Data size ({size} bytes) exceeds limit ({max_size} bytes)"

            return True, ""
        except Exception as e:
            return False, f"Size validation error: {e}"

    def validate_count_limit(self, current_count: int, memory_type: str) -> tuple[bool, str]:
        """
        Validate memory item count limits.

        Args:
            current_count: Current number of items
            memory_type: Type of memory (episodic, semantic)

        Returns:
            (is_valid, error_message)
        """
        limits = {
            "episodic": self.MAX_EPISODIC_EVENTS_COUNT,
            "semantic": self.MAX_SEMANTIC_FACTS_COUNT
        }

        max_count = limits.get(memory_type, self.MAX_EPISODIC_EVENTS_COUNT)

        if current_count >= max_count:
            return False, f"Memory count ({current_count}) exceeds limit ({max_count})"

        return True, ""

    # =====================================================
    # SENSITIVE DATA DETECTION
    # =====================================================

    def contains_sensitive_data(self, data: Any) -> tuple[bool, List[str]]:
        """
        Check if data contains sensitive information.

        Args:
            data: Data to check

        Returns:
            (has_sensitive, list_of_patterns_matched)
        """
        if not self.strict_mode:
            return False, []

        try:
            data_str = str(data)
            matches = []

            for pattern in self.SENSITIVE_PATTERNS:
                if re.search(pattern, data_str, re.IGNORECASE):
                    matches.append(pattern)

            return len(matches) > 0, matches
        except Exception as e:
            print(f"[MemoryRules] Sensitive data check error: {e}")
            return False, []

    def sanitize_data(self, data: Any) -> Any:
        """
        Remove sensitive data patterns.

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data
        """
        if isinstance(data, str):
            sanitized = data

            # Replace sensitive patterns
            for pattern in self.SENSITIVE_PATTERNS:
                sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

            return sanitized
        elif isinstance(data, dict):
            return {k: self.sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        else:
            return data

    # =====================================================
    # ACTION VALIDATION
    # =====================================================

    def validate_action(self, action: str) -> tuple[bool, str]:
        """
        Validate memory action is allowed.

        Args:
            action: Action name

        Returns:
            (is_valid, error_message)
        """
        if action not in self.ALLOWED_ACTIONS:
            return False, f"Action '{action}' is not whitelisted"

        return True, ""

    # =====================================================
    # KEY VALIDATION
    # =====================================================

    def validate_key(self, key: str) -> tuple[bool, str]:
        """
        Validate memory key format.

        Args:
            key: Key to validate

        Returns:
            (is_valid, error_message)
        """
        if not key or not isinstance(key, str):
            return False, "Key must be non-empty string"

        if len(key) > 256:
            return False, "Key too long (max 256 characters)"

        # Check for path traversal attempts
        if ".." in key or "/" in key or "\\" in key:
            return False, "Key contains invalid characters"

        return True, ""

    # =====================================================
    # COMPREHENSIVE VALIDATION
    # =====================================================

    def validate_memory_operation(
        self,
        action: str,
        memory_type: str,
        key: str = None,
        data: Any = None,
        current_count: int = 0
    ) -> tuple[bool, str]:
        """
        Comprehensive validation for memory operation.

        Args:
            action: Memory action (add, get, etc.)
            memory_type: Type of memory (working, episodic, semantic)
            key: Optional key
            data: Optional data
            current_count: Current item count

        Returns:
            (is_valid, error_message)
        """
        # Validate action
        is_valid, error = self.validate_action(action)
        if not is_valid:
            return False, f"Action validation failed: {error}"

        # Validate key if provided
        if key:
            is_valid, error = self.validate_key(key)
            if not is_valid:
                return False, f"Key validation failed: {error}"

        # Validate data size if provided
        if data is not None:
            is_valid, error = self.validate_size(data, memory_type)
            if not is_valid:
                return False, f"Size validation failed: {error}"

            # Check for sensitive data
            if self.strict_mode:
                has_sensitive, patterns = self.contains_sensitive_data(data)
                if has_sensitive:
                    return False, f"Sensitive data detected (patterns: {len(patterns)})"

        # Validate count limits
        if current_count > 0:
            is_valid, error = self.validate_count_limit(current_count, memory_type)
            if not is_valid:
                return False, f"Count validation failed: {error}"

        return True, ""

    # =====================================================
    # PRIVACY GUARDS
    # =====================================================

    def should_allow_external_access(self, requester: str) -> bool:
        """
        Check if external entity should have memory access.

        Args:
            requester: Identifier of requesting entity

        Returns:
            True if access allowed
        """
        # Whitelist internal components
        allowed_requesters = {
            "ai_agent",
            "autonomous_loop",
            "memory_engine",
            "consolidation_service",
            "memory_manager"
        }

        return requester in allowed_requesters

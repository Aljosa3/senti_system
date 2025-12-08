"""
FAZA 30.9 – SPEC Sanitizer
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Set
import re
import json


class SpecSanitizer:
    """
    Sanitizes specifications to remove sensitive information.

    Removes all references to:
    - Internal architecture
    - Module names
    - Directory structures
    - Phase names
    - Filenames
    - Agent references
    - Governance mechanisms
    - Self-healing internals

    Output is safe to send to external LLMs.
    """

    # Sensitive patterns to detect and remove
    SENSITIVE_PATTERNS = [
        # FAZA references
        r'\bFAZA\s*\d+(?:\.\d+)?\b',
        r'\bfaza\s*\d+(?:\.\d+)?\b',
        r'\bphase\s*\d+\b',

        # Directory/file references
        r'\bsenti_os\b',
        r'\bsenti_core\b',
        r'\bsenti_kernel\b',
        r'\bsenti_security\b',
        r'\bsenti_memory\b',
        r'\bsenti_expansion\b',
        r'\bsenti_refactor\b',
        r'[\w/]+\.py\b',
        r'[\w/]+\.json\b',
        r'/[\w/]+/',

        # Agent references
        r'\bagent\s+\w+\b',
        r'\bmeta[-_]agent\b',
        r'\bsuper[-_]agent\b',

        # Architecture terms
        r'\bgovernance\s+layer\b',
        r'\bself[-_]healing\b',
        r'\bkernel\s+layer\b',
        r'\bboot\s+sequence\b',

        # Internal component names
        r'\bEventBus\b',
        r'\bExpansionManager\b',
        r'\bSecurityManager\b',
        r'\bMemoryManager\b',
    ]

    # Sensitive keywords (case-insensitive)
    SENSITIVE_KEYWORDS = {
        "faza", "phase", "agent", "governance", "kernel",
        "boot", "driver", "expansion", "meta", "supervisor",
        "orchestrator", "coordinator", "self-healing",
        "senti_os", "senti_core", "senti_kernel"
    }

    # Safe replacements
    SAFE_REPLACEMENTS = {
        "internal component": "component",
        "internal module": "module",
        "internal service": "service",
        "system layer": "layer",
        "governance": "coordination",
        "self-healing": "automatic recovery",
        "agent": "worker",
        "kernel": "core system"
    }

    def __init__(self) -> None:
        """Initialize the SPEC sanitizer."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SENSITIVE_PATTERNS
        ]

    def sanitize(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a specification dictionary.

        Args:
            spec: Original specification

        Returns:
            Sanitized specification safe for external use
        """
        sanitized = json.loads(json.dumps(spec))  # Deep copy

        # Sanitize all string fields recursively
        self._sanitize_recursive(sanitized)

        # Add sanitization metadata
        if "metadata" not in sanitized:
            sanitized["metadata"] = {}

        sanitized["metadata"]["sanitized"] = True
        sanitized["metadata"]["sanitization_level"] = "strict"

        return sanitized

    def _sanitize_recursive(self, obj: Any) -> Any:
        """Recursively sanitize an object."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._sanitize_recursive(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._sanitize_recursive(item)
        elif isinstance(obj, str):
            return self._sanitize_string(obj)

        return obj

    def _sanitize_string(self, text: str) -> str:
        """Sanitize a string by removing sensitive patterns."""
        sanitized = text

        # Remove sensitive patterns
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)

        # Replace sensitive keywords
        words = sanitized.split()
        sanitized_words = []

        for word in words:
            word_lower = word.lower().strip(".,;:!?()")
            if word_lower in self.SENSITIVE_KEYWORDS:
                sanitized_words.append("[REDACTED]")
            else:
                sanitized_words.append(word)

        sanitized = " ".join(sanitized_words)

        # Apply safe replacements
        for sensitive, safe in self.SAFE_REPLACEMENTS.items():
            sanitized = re.sub(
                r'\b' + re.escape(sensitive) + r'\b',
                safe,
                sanitized,
                flags=re.IGNORECASE
            )

        # Clean up multiple redactions
        sanitized = re.sub(r'\[REDACTED\](\s*\[REDACTED\])+', '[REDACTED]', sanitized)

        return sanitized

    def validate_sanitization(self, sanitized: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that sanitization was successful.

        Args:
            sanitized: Sanitized specification

        Returns:
            Tuple of (is_safe, list of found sensitive terms)
        """
        found_sensitive = []

        # Convert to string for comprehensive check
        spec_str = json.dumps(sanitized, indent=2).lower()

        # Check for sensitive keywords
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in spec_str and keyword != "[redacted]":
                found_sensitive.append(keyword)

        # Check for file paths
        if re.search(r'/[\w/]+\.py', spec_str):
            found_sensitive.append("file_path_detected")

        # Check for phase references
        if re.search(r'phase\s*\d+', spec_str, re.IGNORECASE):
            found_sensitive.append("phase_reference_detected")

        is_safe = len(found_sensitive) == 0

        return is_safe, found_sensitive

    def get_sanitization_report(
        self,
        original: Dict[str, Any],
        sanitized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a report of sanitization changes.

        Args:
            original: Original specification
            sanitized: Sanitized specification

        Returns:
            Report dictionary
        """
        original_str = json.dumps(original)
        sanitized_str = json.dumps(sanitized)

        redaction_count = sanitized_str.count("[REDACTED]")

        is_safe, found_sensitive = self.validate_sanitization(sanitized)

        return {
            "redaction_count": redaction_count,
            "is_safe": is_safe,
            "found_sensitive_terms": found_sensitive,
            "size_reduction": len(original_str) - len(sanitized_str),
            "sanitization_timestamp": self._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def sanitize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to sanitize a specification.

    Args:
        spec: Original specification

    Returns:
        Sanitized specification
    """
    sanitizer = SpecSanitizer()
    return sanitizer.sanitize(spec)

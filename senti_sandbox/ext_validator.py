"""
Validation Utilities - FAZA 31 Extended Preflight
"""


def is_positive(n):
    """Check if number is positive."""
    return n > 0


def is_even(n):
    """Check if number is even."""
    return n % 2 == 0


def is_in_range(n, min_val, max_val):
    """Check if number is in range [min_val, max_val]."""
    return min_val <= n <= max_val


def is_valid_string(s):
    """Check if s is a non-empty string."""
    return isinstance(s, str) and len(s) > 0


def validate_number(n, min_val=None, max_val=None):
    """
    Validate number with optional range check.
    Returns tuple (bool, string) with result and reason.
    """
    if not isinstance(n, (int, float)):
        return (False, "Not a number")

    if min_val is not None and n < min_val:
        return (False, f"Below minimum {min_val}")

    if max_val is not None and n > max_val:
        return (False, f"Above maximum {max_val}")

    return (True, "Valid")
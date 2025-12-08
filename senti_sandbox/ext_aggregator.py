"""
Module Aggregator - FAZA 31 Extended Preflight
Tests inter-module imports
"""

from senti_sandbox import ext_math_utils
from senti_sandbox import ext_validator


def safe_divide(a, b):
    """
    Safe division using validator and math_utils.
    Returns result or None if invalid.
    """
    if not ext_validator.is_positive(b):
        return None
    return ext_math_utils.divide(a, b)


def validated_add(a, b):
    """
    Validated addition - checks if both are numbers.
    Returns result or None if invalid.
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None
    return ext_math_utils.add(a, b)


def get_available_operations():
    """Return list of available operation names."""
    return [
        'safe_divide',
        'validated_add',
        'add',
        'subtract',
        'multiply',
        'divide',
        'power',
        'factorial'
    ]
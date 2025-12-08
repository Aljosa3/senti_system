"""
Extended Math Utils - FAZA 31 Extended Preflight
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b. Returns None if b is 0."""
    if b == 0:
        return None
    return a / b


def power(base, exp):
    """Raise base to exp power."""
    return base ** exp


def factorial(n):
    """Calculate factorial of n using recursion."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
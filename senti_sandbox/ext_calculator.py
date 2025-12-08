"""
Calculator with History - FAZA 31 Extended Preflight
"""


class Calculator:
    """Calculator that tracks operation history."""

    def __init__(self):
        """Initialize calculator with empty history."""
        self._history = []

    def add(self, a, b):
        """Add two numbers and record operation."""
        result = a + b
        self._history.append(f"add({a},{b})={result}")
        return result

    def subtract(self, a, b):
        """Subtract b from a and record operation."""
        result = a - b
        self._history.append(f"subtract({a},{b})={result}")
        return result

    def multiply(self, a, b):
        """Multiply two numbers and record operation."""
        result = a * b
        self._history.append(f"multiply({a},{b})={result}")
        return result

    def divide(self, a, b):
        """Divide a by b. Returns None if b is 0."""
        if b == 0:
            self._history.append(f"divide({a},{b})=ERROR")
            return None
        result = a / b
        self._history.append(f"divide({a},{b})={result}")
        return result

    def power(self, base, exp):
        """Raise base to exp power and record operation."""
        result = base ** exp
        self._history.append(f"power({base},{exp})={result}")
        return result

    def sqrt(self, n):
        """
        Calculate square root using Newton's method approximation.
        No math library imports.
        """
        if n < 0:
            self._history.append(f"sqrt({n})=ERROR")
            return None
        if n == 0:
            return 0

        x = n
        tolerance = 0.00001
        while True:
            root = 0.5 * (x + n / x)
            if abs(root - x) < tolerance:
                break
            x = root

        self._history.append(f"sqrt({n})={root}")
        return root

    def get_history(self):
        """Return list of all operations."""
        return self._history.copy()

    def clear_history(self):
        """Clear operation history."""
        self._history = []
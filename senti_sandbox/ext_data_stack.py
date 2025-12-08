"""
Stack Data Structure - FAZA 31 Extended Preflight
"""


class Stack:
    """Stack implementation using list."""

    def __init__(self):
        """Initialize empty stack."""
        self._items = []

    def push(self, item):
        """Push item onto stack."""
        self._items.append(item)

    def pop(self):
        """Pop item from stack. Returns None if empty."""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self):
        """Return top item without removing. Returns None if empty."""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self):
        """Check if stack is empty."""
        return len(self._items) == 0

    def size(self):
        """Return number of items in stack."""
        return len(self._items)

    def clear(self):
        """Remove all items from stack."""
        self._items = []

    def __str__(self):
        """String representation of stack."""
        return f"Stack({self._items})"
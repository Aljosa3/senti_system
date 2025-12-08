"""
Queue Data Structure - FAZA 31 Extended Preflight
"""


class Queue:
    """Queue implementation using list."""

    def __init__(self):
        """Initialize empty queue."""
        self._items = []

    def enqueue(self, item):
        """Add item to rear of queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return front item. Returns None if empty."""
        if self.is_empty():
            return None
        return self._items.pop(0)

    def front(self):
        """Return front item without removing. Returns None if empty."""
        if self.is_empty():
            return None
        return self._items[0]

    def is_empty(self):
        """Check if queue is empty."""
        return len(self._items) == 0

    def size(self):
        """Return number of items in queue."""
        return len(self._items)

    def __str__(self):
        """String representation of queue."""
        return f"Queue({self._items})"
"""
FAZA 28 – Agent Execution Loop (AEL)
State Context

Shared state management for agent coordination.
Provides thread-safe state access across agents.
"""

import logging
from typing import Any, Dict, Optional, List
from threading import Lock
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class StateContext:
    """
    Shared state context for agent coordination.

    Provides:
    - Thread-safe state storage
    - Key-value state access
    - State persistence (optional)
    - State history tracking

    TODO: Add state versioning
    TODO: Add state rollback/undo
    TODO: Add state change notifications
    TODO: Add distributed state sync
    """

    def __init__(self, name: str = "global"):
        """
        Initialize state context.

        Args:
            name: Context name identifier
        """
        self.name = name
        self._state: Dict[str, Any] = {}
        self._lock = Lock()
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100
        logger.info(f"StateContext initialized: {name}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state value by key.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default

        Thread-safe.
        """
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set state value.

        Args:
            key: State key
            value: State value

        Thread-safe.

        TODO: Emit state_changed event
        TODO: Add value validation
        TODO: Add state constraints
        """
        with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value

            # Record change in history
            self._record_change(key, old_value, value)

            logger.debug(f"State updated: {key} = {value}")

    def delete(self, key: str) -> bool:
        """
        Delete state key.

        Args:
            key: State key to delete

        Returns:
            True if key existed and was deleted

        Thread-safe.

        TODO: Emit state_deleted event
        """
        with self._lock:
            if key in self._state:
                old_value = self._state.pop(key)
                self._record_change(key, old_value, None, operation="delete")
                logger.debug(f"State deleted: {key}")
                return True
            return False

    def has(self, key: str) -> bool:
        """
        Check if state key exists.

        Args:
            key: State key

        Returns:
            True if key exists

        Thread-safe.
        """
        with self._lock:
            return key in self._state

    def get_all(self) -> Dict[str, Any]:
        """
        Get all state as dictionary.

        Returns:
            Copy of entire state

        Thread-safe.
        """
        with self._lock:
            return dict(self._state)

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple state values at once.

        Args:
            updates: Dictionary of key-value pairs to update

        Thread-safe.

        TODO: Add atomic transaction support
        """
        with self._lock:
            for key, value in updates.items():
                old_value = self._state.get(key)
                self._state[key] = value
                self._record_change(key, old_value, value)
            logger.debug(f"State bulk update: {len(updates)} keys")

    def clear(self) -> None:
        """
        Clear all state.

        Thread-safe.

        TODO: Add confirmation mechanism
        TODO: Emit state_cleared event
        """
        with self._lock:
            self._state.clear()
            self._record_change(None, None, None, operation="clear")
            logger.info(f"State cleared: {self.name}")

    def _record_change(
        self,
        key: Optional[str],
        old_value: Any,
        new_value: Any,
        operation: str = "set"
    ) -> None:
        """
        Record state change in history.

        Args:
            key: Changed key
            old_value: Previous value
            new_value: New value
            operation: Operation type ('set', 'delete', 'clear')

        Internal method (not thread-safe, assumes lock is held).
        """
        change = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "key": key,
            "old_value": old_value,
            "new_value": new_value
        }

        self._history.append(change)

        # Limit history size
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def get_history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get state change history.

        Args:
            key: Filter by specific key (None = all changes)

        Returns:
            List of change records

        Thread-safe.
        """
        with self._lock:
            if key is None:
                return list(self._history)
            return [h for h in self._history if h.get("key") == key]

    def to_json(self) -> str:
        """
        Export state to JSON string.

        Returns:
            JSON representation of state

        TODO: Handle non-serializable objects
        """
        with self._lock:
            return json.dumps(self._state, indent=2, default=str)

    def from_json(self, json_str: str) -> None:
        """
        Import state from JSON string.

        Args:
            json_str: JSON string

        TODO: Add validation
        TODO: Add merge option
        """
        data = json.loads(json_str)
        with self._lock:
            self._state.update(data)
            logger.info(f"State loaded from JSON: {len(data)} keys")

    def save_to_file(self, filepath: str) -> None:
        """
        Save state to file.

        Args:
            filepath: Path to save file

        TODO: Add encryption support
        TODO: Add compression option
        """
        with open(filepath, 'w') as f:
            f.write(self.to_json())
        logger.info(f"State saved to: {filepath}")

    def load_from_file(self, filepath: str) -> None:
        """
        Load state from file.

        Args:
            filepath: Path to load file

        TODO: Add validation
        TODO: Add backup before overwrite
        """
        with open(filepath, 'r') as f:
            json_str = f.read()
        self.from_json(json_str)
        logger.info(f"State loaded from: {filepath}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get state context statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            return {
                "name": self.name,
                "total_keys": len(self._state),
                "history_size": len(self._history),
                "max_history": self._max_history
            }

    def __repr__(self) -> str:
        return f"<StateContext: {self.name}, {len(self._state)} keys>"


# Singleton instance
_state_context_instance: Optional[StateContext] = None


def get_state_context() -> StateContext:
    """
    Get singleton StateContext instance.

    Returns:
        Global StateContext instance
    """
    global _state_context_instance
    if _state_context_instance is None:
        _state_context_instance = StateContext(name="global")
    return _state_context_instance


def create_state_context(name: str = "global") -> StateContext:
    """
    Factory function: create new StateContext instance.

    Args:
        name: Context name

    Returns:
        New StateContext instance
    """
    return StateContext(name=name)

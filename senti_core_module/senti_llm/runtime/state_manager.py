"""
FAZA 40 — Persistent Module State Engine
-----------------------------------------
Enables modules to persist state across executions.

Features:
- Automatic state loading from storage
- Default state initialization from manifest
- Atomic writes with rollback on failure
- State versioning support
- Read-only state dumps
- Automatic refresh/save lifecycle integration

Architecture:
- ModuleState: Per-module state container with CRUD operations
- StateManager: Factory for creating and managing ModuleState instances
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import json
import copy

from .module_storage import ModuleStorage


class ModuleState:
    """
    Per-module persistent state container.

    Provides safe access to module state with automatic persistence.
    All state modifications are tracked and can be saved atomically.
    """

    def __init__(self, module_name: str, storage: ModuleStorage, default_state: Optional[Dict[str, Any]] = None):
        """
        Initialize module state.

        Args:
            module_name: Name of the module
            storage: ModuleStorage instance for this module
            default_state: Default state dict if no saved state exists
        """
        self.module_name = module_name
        self.storage = storage
        self.default_state = default_state or {}

        # Internal state
        self._state: Dict[str, Any] = {}
        self._modified = False
        self._last_snapshot: Dict[str, Any] = {}

        # State file path
        self.state_file = "state.json"

        # Load existing state or initialize with defaults
        self._load()

    def _load(self) -> None:
        """Load state from storage or initialize with defaults."""
        try:
            if self.storage.exists(self.state_file):
                # Load existing state
                data = self.storage.read_json(self.state_file)

                # Validate structure
                if not isinstance(data, dict):
                    raise ValueError("State file must contain a JSON object")

                # Extract state data (ignore metadata for now)
                self._state = data.get("state", {})

                # Create snapshot for rollback
                self._last_snapshot = copy.deepcopy(self._state)
                self._modified = False
            else:
                # Initialize with default state
                self._state = copy.deepcopy(self.default_state)
                self._last_snapshot = copy.deepcopy(self._state)
                self._modified = True  # Will trigger initial save
        except Exception as e:
            # On any error, fall back to default state
            self._state = copy.deepcopy(self.default_state)
            self._last_snapshot = copy.deepcopy(self._state)
            self._modified = True

    def refresh(self) -> None:
        """
        Reload state from storage.

        Useful for getting latest state before execution.
        Discards any unsaved local modifications.
        """
        self._load()

    def save(self) -> bool:
        """
        Save current state to storage atomically.

        Returns:
            True if save succeeded, False otherwise
        """
        if not self._modified:
            # No changes, skip save
            return True

        try:
            # Prepare state file with metadata
            state_data = {
                "module": self.module_name,
                "version": 1,  # State format version
                "state": self._state
            }

            # Atomic write via storage layer
            self.storage.write_json(self.state_file, state_data)

            # Update snapshot
            self._last_snapshot = copy.deepcopy(self._state)
            self._modified = False

            return True

        except Exception as e:
            # Save failed, state remains modified
            return False

    def rollback(self) -> None:
        """
        Rollback to last saved state.

        Discards all modifications since last successful save.
        """
        self._state = copy.deepcopy(self._last_snapshot)
        self._modified = False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from state.

        Args:
            key: State key
            default: Default value if key doesn't exist

        Returns:
            Value or default
        """
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set value in state.

        Args:
            key: State key
            value: Value to set (must be JSON-serializable)
        """
        # Validate JSON serializability
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"State value must be JSON-serializable: {e}")

        self._state[key] = value
        self._modified = True

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update multiple state values at once.

        Args:
            data: Dictionary of key-value pairs to update
        """
        # Validate all values are JSON-serializable
        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"State values must be JSON-serializable: {e}")

        self._state.update(data)
        self._modified = True

    def delete(self, key: str) -> bool:
        """
        Delete key from state.

        Args:
            key: State key to delete

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._state:
            del self._state[key]
            self._modified = True
            return True
        return False

    def reset(self) -> None:
        """
        Reset state to default values.

        This marks state as modified and requires save() to persist.
        """
        self._state = copy.deepcopy(self.default_state)
        self._modified = True

    def dump(self) -> Dict[str, Any]:
        """
        Get read-only copy of entire state.

        Returns:
            Deep copy of current state
        """
        return copy.deepcopy(self._state)

    def has(self, key: str) -> bool:
        """
        Check if key exists in state.

        Args:
            key: State key

        Returns:
            True if key exists
        """
        return key in self._state

    def is_modified(self) -> bool:
        """
        Check if state has unsaved modifications.

        Returns:
            True if state was modified since last save
        """
        return self._modified


class StateManager:
    """
    Factory and manager for ModuleState instances.

    Creates and initializes state objects for modules,
    integrating with the module storage system.
    """

    def __init__(self):
        """Initialize state manager."""
        pass

    def load_state(self, module_name: str, manifest: Dict[str, Any], storage: ModuleStorage) -> ModuleState:
        """
        Load or initialize state for a module.

        Args:
            module_name: Module name
            manifest: Module manifest dict
            storage: ModuleStorage instance for this module

        Returns:
            ModuleState instance
        """
        # Extract default state from manifest if provided
        default_state = manifest.get("default_state", {})

        # Validate default_state is a dict
        if not isinstance(default_state, dict):
            raise ValueError(f"Module '{module_name}': default_state must be a dict")

        # Create and return state instance
        return ModuleState(module_name, storage, default_state)

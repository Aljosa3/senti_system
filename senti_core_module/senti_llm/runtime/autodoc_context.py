"""
FAZA D.1 — AutoDoc Context
---------------------------
Context manager for AutoDoc system state.

Stores:
- Root path
- Runtime version (FAZA 42)
- Module list
- Capability registry snapshot
- Event registry snapshot
- Timestamp metadata
- Path management helpers
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime


class AutoDocContext:
    """
    Context manager for AutoDoc system.

    Stores runtime state snapshots for documentation generation.
    """

    def __init__(self, root_path: Optional[str] = None):
        """
        Initialize AutoDoc context.

        Args:
            root_path: Root path for senti_system (defaults to cwd)
        """
        self.root_path = root_path or os.getcwd()
        self.runtime_version = "FAZA 42"
        self.timestamp = time.time()
        self.created_at = datetime.now().isoformat()

        # Snapshots
        self.modules: List[Dict[str, Any]] = []
        self.capabilities: Dict[str, Any] = {}
        self.events: Dict[str, Any] = {}
        self.runtime_info: Dict[str, Any] = {}

        # Metadata
        self.metadata: Dict[str, Any] = {
            "generator": "AutoDocBuilder",
            "version": "FAZA D.1",
            "created_at": self.created_at,
            "root_path": self.root_path
        }

    # ================================================================
    # PATH MANAGEMENT
    # ================================================================

    def get_data_path(self) -> str:
        """
        Get path to senti_data/autodoc directory.

        Returns:
            Absolute path to autodoc data directory
        """
        return os.path.join(self.root_path, "senti_data", "autodoc")

    def get_docs_path(self) -> str:
        """
        Get path to docs/generated directory.

        Returns:
            Absolute path to generated docs directory
        """
        return os.path.join(self.root_path, "docs", "generated")

    def get_schemas_path(self) -> str:
        """
        Get path to docs/schemas directory.

        Returns:
            Absolute path to schemas directory
        """
        return os.path.join(self.root_path, "docs", "schemas")

    def get_module_path(self, module_name: str) -> str:
        """
        Get expected path for a module file.

        Args:
            module_name: Module name

        Returns:
            Expected module path
        """
        return os.path.join(
            self.root_path,
            "senti_core_module",
            "senti_llm",
            "modules",
            f"{module_name}.py"
        )

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        for path in [self.get_data_path(), self.get_docs_path(), self.get_schemas_path()]:
            os.makedirs(path, exist_ok=True)

    # ================================================================
    # SNAPSHOT MANAGEMENT
    # ================================================================

    def set_runtime_snapshot(self, runtime_info: Dict[str, Any]):
        """
        Store runtime information snapshot.

        Args:
            runtime_info: Runtime metadata dict
        """
        self.runtime_info = runtime_info

    def set_capabilities_snapshot(self, capabilities: Dict[str, Any]):
        """
        Store capability registry snapshot.

        Args:
            capabilities: Capability definitions dict
        """
        self.capabilities = capabilities

    def set_events_snapshot(self, events: Dict[str, Any]):
        """
        Store event bus snapshot.

        Args:
            events: Event subscriptions dict
        """
        self.events = events

    def add_module(self, module_def: Dict[str, Any]):
        """
        Add module to context.

        Args:
            module_def: Module definition dict
        """
        # Check if module already exists
        existing = next((m for m in self.modules if m["name"] == module_def["name"]), None)

        if existing:
            # Update existing
            self.modules.remove(existing)

        self.modules.append(module_def)

    def get_module(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get module definition by name.

        Args:
            name: Module name

        Returns:
            Module definition dict or None
        """
        return next((m for m in self.modules if m["name"] == name), None)

    def list_modules(self) -> List[str]:
        """
        List all module names in context.

        Returns:
            List of module names
        """
        return [m["name"] for m in self.modules]

    # ================================================================
    # EXPORT
    # ================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Export context to dict.

        Returns:
            Complete context dict
        """
        return {
            "runtime": self.runtime_info,
            "capabilities": self.capabilities,
            "events": self.events,
            "modules": self.modules,
            "metadata": {
                **self.metadata,
                "timestamp": self.timestamp,
                "runtime_version": self.runtime_version
            }
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics.

        Returns:
            Summary dict
        """
        return {
            "runtime_version": self.runtime_version,
            "module_count": len(self.modules),
            "capability_count": len(self.capabilities),
            "event_type_count": len(self.events.get("registered_types", [])),
            "created_at": self.created_at
        }

    # ================================================================
    # VALIDATION
    # ================================================================

    def validate(self) -> bool:
        """
        Validate context integrity.

        Returns:
            True if context is valid
        """
        # Check required fields
        if not self.runtime_version:
            return False

        if not self.root_path or not os.path.exists(self.root_path):
            return False

        # Check snapshots are dicts/lists
        if not isinstance(self.runtime_info, dict):
            return False

        if not isinstance(self.capabilities, dict):
            return False

        if not isinstance(self.events, dict):
            return False

        if not isinstance(self.modules, list):
            return False

        return True

    def __repr__(self) -> str:
        """String representation."""
        return f"<AutoDocContext runtime={self.runtime_version} modules={len(self.modules)}>"

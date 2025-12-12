"""
FAZA 44 — Capability Registry
------------------------------
Centralni register vseh veljavnih capabilities v Senti OS runtime.

Definira:
- Core capabilities (log, storage, network, crypto, time)
- Event capabilities (event.publish, event.subscribe) - FAZA 41
- Task scheduling capabilities (task.schedule.*, task.cancel) - FAZA 43
- Async execution capabilities (async.schedule, async.await) - FAZA 44
- Restricted capabilities (cannot be granted to modules)
- Validation methods
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional


class CapabilityRegistry:
    """
    Registry vseh capabilities, ki jih lahko moduli zahtevajo.
    """

    def __init__(self):
        # Core capabilities available to modules
        self.capabilities: Dict[str, Dict] = {
            # Logging capabilities
            "log.basic": {
                "description": "Basic logging capability",
                "level": "safe"
            },
            "log.advanced": {
                "description": "Advanced logging with metadata",
                "level": "safe"
            },

            # Storage capabilities
            "storage.read": {
                "description": "Read from module storage",
                "level": "safe"
            },
            "storage.write": {
                "description": "Write to module storage",
                "level": "moderate"
            },

            # Network capability
            "network": {
                "description": "Network access for HTTP/HTTPS requests",
                "level": "moderate"
            },

            # Crypto capability
            "crypto": {
                "description": "Cryptographic operations",
                "level": "safe"
            },

            # Time capability
            "time": {
                "description": "Time and date operations",
                "level": "safe"
            },

            # Module execution capability
            "module.run": {
                "description": "Permission to execute module",
                "level": "safe"
            },

            # FAZA 41: Event capabilities
            "event.publish": {
                "description": "Publish events to EventBus",
                "level": "safe"
            },
            "event.subscribe": {
                "description": "Subscribe to events from EventBus",
                "level": "safe"
            },

            # FAZA 43: Task scheduling capabilities
            "task.schedule.interval": {
                "description": "Schedule repeating interval tasks",
                "level": "safe"
            },
            "task.schedule.oneshot": {
                "description": "Schedule one-time tasks after delay",
                "level": "safe"
            },
            "task.schedule.event": {
                "description": "Schedule event-triggered tasks",
                "level": "safe"
            },
            "task.cancel": {
                "description": "Cancel scheduled tasks",
                "level": "safe"
            },

            # FAZA 44: Async execution capabilities
            "async.schedule": {
                "description": "Schedule async coroutines for execution",
                "level": "safe"
            },
            "async.await": {
                "description": "Poll async task results",
                "level": "safe"
            },
        }

        # Restricted capabilities that cannot be granted
        self.restricted: Set[str] = {
            "network.raw",      # Raw socket access
            "os.exec",          # OS command execution
            "fs.root",          # Root filesystem access
        }

    def get_capability(self, name: str) -> Optional[Dict]:
        """
        Vrne capability definicijo, če obstaja.
        """
        return self.capabilities.get(name)

    def has_capability(self, name: str) -> bool:
        """
        Preveri, ali capability obstaja in ni restricted.
        """
        if name in self.restricted:
            return False
        return name in self.capabilities

    def is_restricted(self, name: str) -> bool:
        """
        Preveri, ali je capability restricted.
        """
        return name in self.restricted

    def list_capabilities(self) -> List[str]:
        """
        Vrne seznam vseh razpoložljivih capabilities.
        """
        return list(self.capabilities.keys())

    def validate_capability_list(self, cap_list: List[str]) -> tuple[bool, str]:
        """
        Validira seznam capabilities.

        Returns:
            (success: bool, message: str)
        """
        if not isinstance(cap_list, list):
            return False, "Capability list must be a list."

        for cap in cap_list:
            if not isinstance(cap, str):
                return False, f"Capability must be string: {cap}"

            if self.is_restricted(cap):
                return False, f"Capability '{cap}' is restricted and cannot be granted."

            if not self.has_capability(cap):
                return False, f"Unknown capability: '{cap}'"

        return True, "All capabilities valid."

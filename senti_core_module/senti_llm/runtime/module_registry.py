"""
FAZA 45 — Module Registry (STRICT ONLY INTEGRITY MODE)
------------------------------------------------------
STRICT ONLY MODE:
- Shrani integrity_status za vsak modul
- Modul je 'loaded' SAMO če je integrity_status == "verified"
- ExecutionOrchestrator blokira izvajanje modulov, ki niso "verified"
- BREZ auto-baseline: manjkajoča integriteta → modul blocked

FAZA 37 — Capabilities storage
FAZA 40 — Persistent ModuleState storage
"""

from __future__ import annotations
from typing import Dict, Any, Optional


class ModuleRegistry:
    def __init__(self):
        # Structure:
        # modules = {
        #     "<name>": {
        #         "manifest": dict,
        #         "instance": object,
        #         "status": "loaded" | "blocked",
        #         "capabilities": Dict[str, Any],
        #         "state": ModuleState,
        #         "integrity_status": "verified" | "failed" | None,  # STRICT: only "verified" → loaded
        #     }
        # }
        self.modules: Dict[str, Dict[str, Any]] = {}

    # ================================================================
    # REGISTER MODULE
    # ================================================================
    def register(
        self,
        name: str,
        manifest: dict,
        instance: Any,
        capabilities: Dict[str, Any] = None,
        state: Any = None,
        integrity_status: str = "verified",
    ):
        """
        Register module in registry.

        Args:
            name: module name
            manifest: manifest structure
            instance: module instance
            capabilities: module capabilities (FAZA 37)
            state: module state (FAZA 40)
            integrity_status: FAZA 45 integrity status
        """

        if capabilities is None:
            capabilities = {}

        # STRICT ONLY: module is loaded ONLY if integrity_status == "verified"
        self.modules[name] = {
            "manifest": manifest,
            "instance": instance,
            "status": "loaded" if integrity_status == "verified" else "blocked",
            "capabilities": capabilities,
            "state": state,
            "integrity_status": integrity_status,
        }

    # ================================================================
    # GET MODULE DATA
    # ================================================================
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self.modules.get(name)

    def list_modules(self):
        return list(self.modules.keys())

    # ================================================================
    # CAPABILITY HELPERS
    # ================================================================
    def get_module_capabilities(self, name: str) -> Optional[Dict[str, Any]]:
        mod_data = self.modules.get(name)
        if mod_data:
            return mod_data.get("capabilities", {})
        return None

    def has_capability(self, name: str, capability: str) -> bool:
        caps = self.get_module_capabilities(name)
        if caps:
            return capability in caps
        return False

    # ================================================================
    # STATE HELPERS
    # ================================================================
    def get_module_state(self, name: str) -> Optional[Any]:
        mod_data = self.modules.get(name)
        if mod_data:
            return mod_data.get("state")
        return None

    # ================================================================
    # INTEGRITY HELPERS (FAZA 45)
    # ================================================================
    def set_integrity_status(self, name: str, status: str):
        """Update integrity status for module (STRICT ONLY MODE)."""
        # STRICT ONLY: block module unless fully verified
        if name in self.modules:
            self.modules[name]["integrity_status"] = status
            self.modules[name]["status"] = (
                "loaded" if status == "verified" else "blocked"
            )

    def get_integrity_status(self, name: str) -> Optional[str]:
        mod_data = self.modules.get(name)
        if mod_data:
            return mod_data.get("integrity_status")
        return None

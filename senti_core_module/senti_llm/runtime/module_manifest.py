"""
FAZA 42 — Module Manifest
-------------------------
Extended manifest system including:
- FAZA 36 core manifest schema
- FAZA 39 lifecycle hooks
- FAZA 40 default_state + state_version
- FAZA 41 event subscriptions
- FAZA 42 REACTIVE MODULE DEFINITIONS
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List


class ModuleManifest:
    """
    Represents a parsed module manifest structure.

    Manifest example:

    {
        "name": "demo",
        "version": "1.0.0",
        "phase": 42,
        "entrypoint": "DemoModule",
        "capabilities": {
            "requires": ["module.run", "event.publish", "event.subscribe"]
        },
        "hooks": { "init": true, "pre_run": true, "post_run": true, "on_error": true },
        "default_state": { "counter": 0 },
        "state_version": 1,
        "event_subscriptions": {
            "module.loaded": "on_loaded"
        },
        "reactive": {
            "enabled": true,
            "handlers": {
                "custom.test": "handle_custom_event"
            }
        }
    }
    """

    REQUIRED_FIELDS = ["name", "version", "phase", "entrypoint"]
    OPTIONAL_FIELDS = [
        "capabilities",
        "description",
        "author",
        "dependencies",
        "hooks",
        "default_state",
        "state_version",
        "event_subscriptions",
        "reactive"  # FAZA 42
    ]

    def __init__(self, manifest_dict: Dict[str, Any]):
        self.manifest = manifest_dict
        self._data = manifest_dict  # Alias for compatibility

        # Basic validation of required fields
        for key in self.REQUIRED_FIELDS:
            if key not in self.manifest:
                raise ValueError(f"Manifest missing required field: {key}")

    # ----------------------------------------------------------------------
    # BASIC ACCESSORS
    # ----------------------------------------------------------------------
    def validate_structure(self) -> bool:
        """Preveri, ali manifest vsebuje obvezna polja."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.manifest:
                return False
        return True

    def get(self, key: str, default: Any = None) -> Any:
        return self.manifest.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.manifest[key]

    # ================================================================
    # FAZA 37: CAPABILITIES METHODS
    # ================================================================

    def has_capabilities(self) -> bool:
        """Preveri, ali manifest vsebuje capabilities field."""
        return "capabilities" in self.manifest

    def get_required_capabilities(self) -> List[str]:
        """Vrne seznam required capabilities."""
        if not self.has_capabilities():
            return []

        cap_spec = self.manifest.get("capabilities", {})
        return cap_spec.get("requires", [])

    def get_optional_capabilities(self) -> List[str]:
        """Vrne seznam optional capabilities."""
        if not self.has_capabilities():
            return []

        cap_spec = self.manifest.get("capabilities", {})
        return cap_spec.get("optional", [])

    def get_all_capabilities(self) -> List[str]:
        """Vrne vse capabilities (required + optional)."""
        return self.get_required_capabilities() + self.get_optional_capabilities()

    def get_capabilities_required(self) -> List[str]:
        """Alias for get_required_capabilities (compatibility)."""
        return self.get_required_capabilities()

    # ================================================================
    # FAZA 39: LIFECYCLE HOOKS METHODS
    # ================================================================

    def has_hooks(self) -> bool:
        """Preveri, ali manifest vsebuje hooks field."""
        return "hooks" in self.manifest

    def get_hooks(self) -> Dict[str, bool]:
        """
        Vrne hooks configuration iz manifesta.

        Returns:
            Dict z lifecycle hooks enabled/disabled status.
            Default: all False if hooks not specified.
        """
        if not self.has_hooks():
            return {
                "init": False,
                "pre_run": False,
                "post_run": False,
                "on_error": False
            }

        hooks_spec = self.manifest.get("hooks", {})

        # Merge with defaults
        return {
            "init": hooks_spec.get("init", False),
            "pre_run": hooks_spec.get("pre_run", False),
            "post_run": hooks_spec.get("post_run", False),
            "on_error": hooks_spec.get("on_error", False)
        }

    # ================================================================
    # FAZA 40: STATE MANAGEMENT METHODS
    # ================================================================

    def has_default_state(self) -> bool:
        """
        Preveri, ali manifest vsebuje default_state field.

        Returns:
            True če manifest ima default_state
        """
        return "default_state" in self.manifest

    def get_default_state(self) -> Dict[str, Any]:
        """
        Vrne default state configuration iz manifesta.

        Returns:
            Dict z default state vrednostmi.
            Default: prazen dict če default_state ni specificiran.
        """
        if not self.has_default_state():
            return {}

        default_state = self.manifest.get("default_state", {})

        # Validate it's a dict
        if not isinstance(default_state, dict):
            return {}

        return default_state

    def has_state_version(self) -> bool:
        """
        Preveri, ali manifest vsebuje state_version field.

        Returns:
            True če manifest ima state_version
        """
        return "state_version" in self.manifest

    def get_state_version(self) -> int:
        """
        Vrne state version iz manifesta.

        Returns:
            State version number (default: 1)
        """
        if not self.has_state_version():
            return 1

        version = self.manifest.get("state_version", 1)

        # Validate it's an integer
        if not isinstance(version, int):
            return 1

        return version

    # ================================================================
    # FAZA 41: EVENT SUBSCRIPTIONS
    # ================================================================

    def has_event_subscriptions(self) -> bool:
        """
        Preveri, ali manifest vsebuje event_subscriptions field.

        Returns:
            True če manifest ima event subscriptions
        """
        return "event_subscriptions" in self.manifest

    def get_event_subscriptions(self) -> Dict[str, str]:
        """
        Returns mapping: event_type -> handler_method

        Returns:
            Dict mapiranja dogodek -> handler metoda
            Default: prazen dict
        """
        return self.manifest.get("event_subscriptions", {})

    # ================================================================
    # FAZA 42: REACTIVE MODULE DEFINITIONS
    # ================================================================

    def has_reactive(self) -> bool:
        """
        True if manifest defines:
        "reactive": { "enabled": true, ... }

        Returns:
            True če je reactive mode enabled
        """
        reactive = self.manifest.get("reactive", {})
        return bool(reactive.get("enabled", False))

    def get_reactive_config(self) -> Dict[str, Any]:
        """
        Returns the entire reactive section.

        Returns:
            Complete reactive configuration dict
        """
        return self.manifest.get("reactive", {})

    def get_reactive_handlers(self) -> Dict[str, str]:
        """
        Returns mapping: event_type -> handler_method_name

        Example:
          "custom.test": "on_custom_event"

        Returns:
            Dict mapiranja dogodek -> reactive handler metoda
        """
        reactive = self.manifest.get("reactive", {})
        return reactive.get("handlers", {})

    # ================================================================
    # META ACCESSORS
    # ================================================================

    def get_module_name(self) -> str:
        """Returns module name."""
        return self.manifest["name"]

    def get_entrypoint(self) -> str:
        """Returns entrypoint class name."""
        return self.manifest["entrypoint"]

    def get_phase(self) -> int:
        """Returns FAZA phase number."""
        return int(self.manifest["phase"])

    def get_version(self) -> str:
        """Returns module version."""
        return str(self.manifest["version"])

    def to_dict(self) -> Dict[str, Any]:
        """Returns complete manifest as dict."""
        return dict(self.manifest)

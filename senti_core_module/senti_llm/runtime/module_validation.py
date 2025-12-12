"""
FAZA 42 — Module Validation
---------------------------
Validira module na osnovi:
- manifest strukture
- fazne kompatibilnosti
- obstoja vstopnega razreda
- capabilities (FAZA 37)
- lifecycle hooks (FAZA 39)
- default_state (FAZA 40)
- event_subscriptions (FAZA 41)
- reactive handlers (FAZA 42)
"""

from __future__ import annotations
from typing import Any, Dict, Tuple
import importlib.util
import os
import json

from .module_manifest import ModuleManifest
from .capability_manager import CapabilityManager


class ModuleValidation:
    MIN_PHASE = 36

    def __init__(self):
        self.capability_manager = CapabilityManager()

    def validate_manifest(self, path: str, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        m = ModuleManifest(manifest)

        if not m.validate_structure():
            return False, "Manifest struktura ni veljavna."

        if manifest["phase"] < self.MIN_PHASE:
            return False, f"Modul ni kompatibilen (FAZA < {self.MIN_PHASE})."

        return True, "Manifest OK."

    def validate_entrypoint(self, module_path: str, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """Preveri, ali datoteka definira vstopni razred."""
        entrypoint = manifest["entrypoint"]

        if not os.path.isfile(module_path):
            return False, f"Modul '{module_path}' ne obstaja."

        module_name = os.path.splitext(os.path.basename(module_path))[0]

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            return False, f"Napaka pri nalaganju modula: {e}"

        if not hasattr(module, entrypoint):
            return False, f"Entrypoint '{entrypoint}' ne obstaja v modulu."

        return True, "Entrypoint OK."

    def validate_capabilities(self, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        FAZA 37: Validira capabilities iz manifesta.

        Preveri:
        - Ali so vsi required capabilities veljavni
        - Ali so vsi optional capabilities veljavni
        - Ali capabilities niso restricted

        Returns:
            (success: bool, message: str)
        """
        success, msg = self.capability_manager.validate_manifest_capabilities(manifest)
        return success, msg

    def validate_hooks(self, module_path: str, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        FAZA 39: Validira lifecycle hooks iz manifesta.

        Če manifest pravi, da hook obstaja, mora biti definiran v modulu.
        Če hook ni v manifestu, ga ignoriramo.

        Returns:
            (success: bool, message: str)
        """
        m = ModuleManifest(manifest)
        hooks = m.get_hooks()

        # Če noben hook ni enabled, validation je OK
        if not any(hooks.values()):
            return True, "No hooks declared."

        # Naloži modul da lahko preverjamo metode
        module_name = os.path.splitext(os.path.basename(module_path))[0]

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            return False, f"Cannot load module for hook validation: {e}"

        # Pridobi entry class
        entrypoint = manifest["entrypoint"]
        if not hasattr(module, entrypoint):
            return False, f"Entrypoint '{entrypoint}' not found."

        entry_class = getattr(module, entrypoint)

        # Preveri vsak enabled hook
        for hook_name, enabled in hooks.items():
            if enabled:
                # Preveri, ali metoda obstaja v class
                if not hasattr(entry_class, hook_name):
                    return False, f"Hook '{hook_name}' declared in manifest but method not found in class."

        return True, "Hooks validated OK."

    def validate_default_state(self, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        FAZA 40: Validira default_state iz manifesta.

        Preveri:
        - Ali je default_state dict (če obstaja)
        - Ali so vse vrednosti JSON-serializabilne
        - Ali ne vsebuje prepovedanih ključev

        Returns:
            (success: bool, message: str)
        """
        m = ModuleManifest(manifest)

        # Če default_state ni definiran, je to OK
        if not m.has_default_state():
            return True, "No default_state declared."

        default_state = m.get_default_state()

        # Validate it's a dict
        if not isinstance(default_state, dict):
            return False, "default_state must be a dict."

        # Validate JSON serializability
        try:
            json.dumps(default_state)
        except (TypeError, ValueError) as e:
            return False, f"default_state must be JSON-serializable: {e}"

        # Check for forbidden keys (internal state keys)
        forbidden_keys = ["__internal__", "_state", "_snapshot"]
        for key in forbidden_keys:
            if key in default_state:
                return False, f"Forbidden key '{key}' in default_state."

        return True, "default_state validated OK."

    def validate_reactive_handlers(self, module_path: str, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        FAZA 42: Validira reactive handlers iz manifesta.

        Preveri:
        - Ali je reactive.enabled boolean (če obstaja)
        - Ali je handlers dict strukture event_type -> handler_method
        - Ali vse handler metode obstajajo v entry class

        Returns:
            (success: bool, message: str)
        """
        m = ModuleManifest(manifest)

        # Če reactive ni enabled, validation je OK
        if not m.has_reactive():
            return True, "No reactive handlers declared."

        reactive_config = m.get_reactive_config()

        # Validate reactive.enabled is bool
        enabled = reactive_config.get("enabled", False)
        if not isinstance(enabled, bool):
            return False, "reactive.enabled must be a boolean."

        # Če je disabled, ni potrebe validirati handlers
        if not enabled:
            return True, "Reactive mode disabled."

        # Get handlers mapping
        handlers = m.get_reactive_handlers()

        # Validate handlers is dict
        if not isinstance(handlers, dict):
            return False, "reactive.handlers must be a dict."

        # Če ni handlers, je to OK (reactive enabled but no handlers yet)
        if not handlers:
            return True, "No reactive handlers defined."

        # Naloži modul da lahko preverjamo metode
        module_name = os.path.splitext(os.path.basename(module_path))[0]

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            return False, f"Cannot load module for reactive validation: {e}"

        # Pridobi entry class
        entrypoint = manifest["entrypoint"]
        if not hasattr(module, entrypoint):
            return False, f"Entrypoint '{entrypoint}' not found."

        entry_class = getattr(module, entrypoint)

        # Preveri vsak handler
        for event_type, handler_method in handlers.items():
            # Validate event_type is string
            if not isinstance(event_type, str):
                return False, f"Event type must be string, got: {type(event_type)}"

            # Validate handler_method is string
            if not isinstance(handler_method, str):
                return False, f"Handler method name must be string, got: {type(handler_method)}"

            # Validate handler method exists in class
            if not hasattr(entry_class, handler_method):
                return False, f"Reactive handler '{handler_method}' for event '{event_type}' not found in class."

        return True, f"Reactive handlers validated OK ({len(handlers)} handlers)."

"""
FAZA D.1 — AutoDoc Builder
---------------------------
Automatic documentation generation system using runtime introspection.

Capabilities:
- Scans runtime state (FAZA 36-42)
- Extracts capability definitions (FAZA 37)
- Extracts event subscriptions (FAZA 41)
- Extracts reactive handlers (FAZA 42)
- Extracts state schemas (FAZA 40)
- Generates JSON model
- Generates Markdown documentation

Design Philosophy:
- Non-blocking: failures must never affect runtime
- Introspective: uses importlib and inspect
- Hermetic: no external dependencies beyond stdlib + runtime
"""

from __future__ import annotations

import os
import json
import importlib.util
import inspect
import time
from typing import Any, Dict, List, Optional
from datetime import datetime


class AutoDocBuilder:
    """
    Main AutoDoc system for generating documentation from runtime introspection.

    Usage:
        builder = AutoDocBuilder()
        builder.scan_runtime()
        builder.generate_json_model()
        builder.write_json_model()
        builder.generate_docs()
    """

    def __init__(self, root_path: Optional[str] = None):
        """
        Initialize AutoDoc builder.

        Args:
            root_path: Root path for senti_system (defaults to current working directory)
        """
        self.root_path = root_path or os.getcwd()
        self.data_path = os.path.join(self.root_path, "senti_data", "autodoc")
        self.docs_path = os.path.join(self.root_path, "docs", "generated")
        self.schemas_path = os.path.join(self.root_path, "docs", "schemas")

        # Ensure directories exist
        self._ensure_directories()

        # Model storage
        self.model: Dict[str, Any] = {
            "runtime": {},
            "capabilities": {},
            "events": {},
            "modules": [],
            "metadata": {}
        }

        # Registry for loaded modules (for incremental updates)
        self.loaded_modules: Dict[str, Dict[str, Any]] = {}

    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        for path in [self.data_path, self.docs_path, self.schemas_path]:
            os.makedirs(path, exist_ok=True)

    # ================================================================
    # REGISTRATION HOOKS (called from module_loader)
    # ================================================================

    def register_loaded_module(self, name: str, manifest: Dict[str, Any]):
        """
        Register a loaded module for documentation.
        Called by module_loader after successful load.

        Args:
            name: Module name
            manifest: Module manifest dict
        """
        try:
            self.loaded_modules[name] = {
                "name": name,
                "manifest": manifest,
                "registered_at": time.time()
            }
        except Exception:
            # Must never fail
            pass

    # ================================================================
    # RUNTIME SCANNING
    # ================================================================

    def scan_runtime(self) -> Dict[str, Any]:
        """
        Scan runtime system state.

        Returns:
            Runtime metadata dict
        """
        try:
            from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

            # Try to get runtime instance
            manager = LLMRuntimeManager()

            runtime_info = {
                "name": "Senti LLM Runtime",
                "phase": "FAZA 42",
                "features": [
                    "FAZA 36: Module Loading",
                    "FAZA 37: Capability System",
                    "FAZA 38: Module Storage",
                    "FAZA 39: Lifecycle Hooks",
                    "FAZA 40: State Management",
                    "FAZA 41: Event Bus",
                    "FAZA 42: Reactive Modules"
                ],
                "components": [
                    "LLMRuntimeManager",
                    "ExecutionOrchestrator",
                    "ModuleLoader",
                    "CapabilityManager",
                    "EventBus",
                    "StateManager"
                ]
            }

            self.model["runtime"] = runtime_info
            return runtime_info

        except Exception as e:
            # Fallback if runtime not available
            self.model["runtime"] = {
                "name": "Senti LLM Runtime",
                "phase": "FAZA 42",
                "error": f"Could not scan runtime: {e}"
            }
            return self.model["runtime"]

    def scan_capabilities(self) -> Dict[str, Any]:
        """
        Scan capability registry.

        Returns:
            Capability definitions dict
        """
        try:
            from senti_core_module.senti_llm.runtime.capability_registry import CAPABILITY_REGISTRY

            capabilities = {}

            for cap_name, cap_def in CAPABILITY_REGISTRY.items():
                capabilities[cap_name] = {
                    "name": cap_name,
                    "description": cap_def.get("description", "No description"),
                    "level": cap_def.get("level", "unknown"),
                    "category": self._categorize_capability(cap_name)
                }

            self.model["capabilities"] = capabilities
            return capabilities

        except Exception as e:
            self.model["capabilities"] = {
                "error": f"Could not scan capabilities: {e}"
            }
            return self.model["capabilities"]

    def _categorize_capability(self, cap_name: str) -> str:
        """Categorize capability by prefix."""
        if cap_name.startswith("log."):
            return "logging"
        elif cap_name.startswith("storage."):
            return "storage"
        elif cap_name.startswith("event."):
            return "events"
        elif cap_name.startswith("module."):
            return "module"
        else:
            return "other"

    def scan_events(self) -> Dict[str, Any]:
        """
        Scan event bus state.

        Returns:
            Event subscriptions dict
        """
        try:
            from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

            manager = LLMRuntimeManager()
            event_bus = manager.exec_orchestrator.module_loader.event_bus

            event_types = event_bus.list_event_types()

            events = {
                "system_events": [
                    "module.loaded",
                    "module.unloaded",
                    "runtime.init",
                    "runtime.shutdown"
                ],
                "registered_types": event_types,
                "subscriptions": {}
            }

            # Get handler counts for each event type
            for event_type in event_types:
                handlers = event_bus.list_handlers(event_type)
                events["subscriptions"][event_type] = {
                    "handler_count": len(handlers)
                }

            self.model["events"] = events
            return events

        except Exception as e:
            self.model["events"] = {
                "error": f"Could not scan events: {e}"
            }
            return self.model["events"]

    def scan_modules(self) -> List[Dict[str, Any]]:
        """
        Scan loaded modules from registry or loaded_modules cache.

        Returns:
            List of module definitions
        """
        modules = []

        try:
            # Try to get from runtime
            from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

            manager = LLMRuntimeManager()
            registry = manager.exec_orchestrator.module_loader.registry

            for mod_name in registry.list_modules():
                mod_data = registry.get(mod_name)
                if mod_data:
                    manifest = mod_data["manifest"]

                    module_doc = {
                        "name": mod_name,
                        "version": manifest.get("version", "unknown"),
                        "phase": manifest.get("phase", 0),
                        "description": manifest.get("description", "No description"),
                        "entrypoint": manifest.get("entrypoint", "unknown"),
                        "capabilities": manifest.get("capabilities", {}),
                        "hooks": manifest.get("hooks", {}),
                        "default_state": manifest.get("default_state", {}),
                        "state_version": manifest.get("state_version", 1),
                        "event_subscriptions": manifest.get("event_subscriptions", {}),
                        "reactive": manifest.get("reactive", {})
                    }

                    modules.append(module_doc)

        except Exception:
            # Fallback: use loaded_modules cache
            for mod_name, mod_info in self.loaded_modules.items():
                manifest = mod_info["manifest"]

                module_doc = {
                    "name": mod_name,
                    "version": manifest.get("version", "unknown"),
                    "phase": manifest.get("phase", 0),
                    "description": manifest.get("description", "No description"),
                    "entrypoint": manifest.get("entrypoint", "unknown"),
                    "capabilities": manifest.get("capabilities", {}),
                    "hooks": manifest.get("hooks", {}),
                    "default_state": manifest.get("default_state", {}),
                    "state_version": manifest.get("state_version", 1),
                    "event_subscriptions": manifest.get("event_subscriptions", {}),
                    "reactive": manifest.get("reactive", {})
                }

                modules.append(module_doc)

        self.model["modules"] = modules
        return modules

    def scan_manifest(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Scan MODULE_MANIFEST from a file.

        Args:
            path: Path to module .py file

        Returns:
            Manifest dict or None if not found/error
        """
        try:
            module_name = os.path.splitext(os.path.basename(path))[0]

            spec = importlib.util.spec_from_file_location(module_name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if hasattr(mod, "MODULE_MANIFEST"):
                return mod.MODULE_MANIFEST
            else:
                return None

        except Exception:
            return None

    def scan_reactive_handlers(self, entry_class: type, manifest: Dict[str, Any]) -> Dict[str, str]:
        """
        Scan reactive handlers from entry class.

        Args:
            entry_class: Module entrypoint class
            manifest: Module manifest

        Returns:
            Dict mapping event_type -> handler_method_name
        """
        try:
            from senti_core_module.senti_llm.runtime.module_manifest import ModuleManifest

            m = ModuleManifest(manifest)

            if not m.has_reactive():
                return {}

            return m.get_reactive_handlers()

        except Exception:
            return {}

    def scan_state_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan state schema from manifest.

        Args:
            manifest: Module manifest

        Returns:
            State schema dict
        """
        try:
            from senti_core_module.senti_llm.runtime.module_manifest import ModuleManifest

            m = ModuleManifest(manifest)

            return {
                "has_state": m.has_default_state(),
                "default_state": m.get_default_state(),
                "state_version": m.get_state_version()
            }

        except Exception:
            return {}

    # ================================================================
    # JSON MODEL GENERATION
    # ================================================================

    def generate_json_model(self) -> Dict[str, Any]:
        """
        Generate complete JSON model from scanned data.

        Returns:
            Complete JSON model dict
        """
        # Scan all components
        self.scan_runtime()
        self.scan_capabilities()
        self.scan_events()
        self.scan_modules()

        # Add metadata
        self.model["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "generator": "AutoDocBuilder",
            "version": "FAZA D.1",
            "root_path": self.root_path
        }

        return self.model

    def write_json_model(self, filename: str = "autodoc.json") -> str:
        """
        Write JSON model to disk.

        Args:
            filename: Output filename

        Returns:
            Path to written file
        """
        output_path = os.path.join(self.data_path, filename)

        try:
            with open(output_path, "w") as f:
                json.dump(self.model, f, indent=2)

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to write JSON model: {e}")

    # ================================================================
    # DOCUMENTATION GENERATION
    # ================================================================

    def generate_docs(self):
        """
        Generate all Markdown documentation.

        This delegates to AutoDocWriter for rendering.
        """
        try:
            from senti_core_module.senti_llm.runtime.autodoc_writer import AutoDocWriter

            writer = AutoDocWriter(self.model, self.docs_path, self.schemas_path)
            writer.clean_docs_dir()
            writer.create_docs_structure()
            writer.render_overview_md()
            writer.render_runtime_api_md()
            writer.render_capabilities_md()
            writer.render_events_md()
            writer.render_reactive_md()
            writer.render_state_md()
            writer.render_module_api_md()

            # Generate JSON schemas
            writer.save_schema("runtime_schema.json", self._generate_runtime_schema())
            writer.save_schema("module_schema.json", self._generate_module_schema())
            writer.save_schema("event_schema.json", self._generate_event_schema())
            writer.save_schema("state_schema.json", self._generate_state_schema())

        except Exception as e:
            raise RuntimeError(f"Failed to generate docs: {e}")

    # ================================================================
    # JSON SCHEMA GENERATION
    # ================================================================

    def _generate_runtime_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for runtime structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Senti Runtime Schema",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "phase": {"type": "string"},
                "features": {"type": "array", "items": {"type": "string"}},
                "components": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["name", "phase"]
        }

    def _generate_module_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for module structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Module Manifest Schema",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "phase": {"type": "integer"},
                "entrypoint": {"type": "string"},
                "description": {"type": "string"},
                "capabilities": {"type": "object"},
                "hooks": {"type": "object"},
                "default_state": {"type": "object"},
                "state_version": {"type": "integer"},
                "event_subscriptions": {"type": "object"},
                "reactive": {"type": "object"}
            },
            "required": ["name", "version", "phase", "entrypoint"]
        }

    def _generate_event_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for event structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Event Context Schema",
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "source": {"type": "string"},
                "payload": {"type": "object"},
                "category": {"type": "string"},
                "priority": {"type": "integer"},
                "timestamp": {"type": "number"}
            },
            "required": ["event_type", "source", "payload"]
        }

    def _generate_state_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for state structure."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Module State Schema",
            "type": "object",
            "properties": {
                "module": {"type": "string"},
                "version": {"type": "integer"},
                "state": {"type": "object"}
            },
            "required": ["module", "version", "state"]
        }

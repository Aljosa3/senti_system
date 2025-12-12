"""
FAZA 45 — Module Loader (STRICT + AUTO-BASELINE)
------------------------------------------------
NADGRAJENO ZA INTEGRITETO:
- Pred nalaganjem modula preveri integriteto (IntegrityManager)
- STRICT MODE: Če integriteta ne ustreza → modul SE NE naloži
- AUTO-BASELINE: Če baseline ne obstaja → baseline SE USTVARI
- Po uspešni verifikaciji se integrity_status shrani v Registry

Vključuje FAZA 36–44:
- Manifest validation
- Entrypoint validation
- Capability enforcement
- Persistent Module State
- EventBus integration
- Scheduler system
- Async execution
- Lifecycle hooks
- Reactive handlers
"""

from __future__ import annotations
import os
import importlib.util
import inspect
from typing import Any, Dict

# FAZA 36–44 imports
from .module_validation import ModuleValidation
from .module_registry import ModuleRegistry
from .module_manifest import ModuleManifest
from .llm_runtime_context import RuntimeContext
from .capability_manager import CapabilityManager
from .state_manager import StateManager
from .event_bus import EventBus
from .event_context import EventContext
from .logging_manager import get_global_logging_manager
from .scheduler import Scheduler
from .async_exec import AsyncTaskManager

# FAZA 45 — Integrity Layer
from senti_core_module.senti_llm.runtime.integrity_singleton import get_global_integrity_manager
from senti_core_module.senti_core.integrity.integrity_exceptions import (
    IntegrityViolation,
    MissingIntegrityData,
)


class ModuleLoader:
    """Module Loader z integriteto FAZA 45."""

    def __init__(self, context: RuntimeContext):
        self.context = context
        self.registry = ModuleRegistry()
        self.validator = ModuleValidation()
        self.state_manager = StateManager()

        # FAZA 41 — EventBus
        self.event_bus = EventBus()

        # FAZA 43 — Scheduler
        self.scheduler = Scheduler(event_bus=self.event_bus)
        self.context.set_scheduler(self.scheduler)
        self.event_bus.set_scheduler(self.scheduler)

        # FAZA 44 — Async Manager
        self.async_manager = AsyncTaskManager(event_bus=self.event_bus)
        self.context.set_async_manager(self.async_manager)
        self.event_bus.set_async_manager(self.async_manager)

        # Capability Manager
        self.capability_manager = CapabilityManager(
            context,
            event_bus=self.event_bus,
            scheduler=self.scheduler,
            async_manager=self.async_manager,
        )

        # Logging
        self._logging_manager = get_global_logging_manager()
        self.logger = self._logging_manager.get_logger("module_loader", "FAZA 45")

        # Integrity Manager reference
        self.integrity_manager = get_global_integrity_manager()

    # ==================================================================
    # LOAD MODULE — STRICT INTEGRITY
    # ==================================================================

    def load(self, module_path: str) -> Dict[str, Any]:
        """Load module from .py file with FAZA 45 strict integrity enforcement."""

        self.logger.info(f"Loading module from: {module_path}")

        if not os.path.isfile(module_path):
            return {"ok": False, "error": "Module file does not exist."}

        module_name = os.path.splitext(os.path.basename(module_path))[0]
        module_dir = os.path.dirname(module_path)

        # ==============================================================
        # 1) IMPORT RAW MODULE
        # ==============================================================

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            return {"ok": False, "error": f"Module import failed: {e}", "module": module_name}

        # ==============================================================
        # 2) LOAD MANIFEST
        # ==============================================================

        if not hasattr(mod, "MODULE_MANIFEST"):
            return {"ok": False, "error": f"MODULE_MANIFEST missing in {module_name}"}

        manifest = mod.MODULE_MANIFEST
        manifest_obj = ModuleManifest(manifest)

        # ==============================================================
        # 3) FAZA 45 — INTEGRITY CHECK (STRICT + AUTO-BASELINE)
        # ==============================================================

        integrity_status = None  # we will fill this for register()

        try:
            integrity_result = self.integrity_manager.ensure_integrity_compliance(
                module_name,
                module_path,
                module_dir,
            )

            integrity_status = "verified"
            self.logger.info(f"Integrity verified for {module_name}")

        except MissingIntegrityData:
            # AUTO-BASELINE: create baseline
            try:
                self.integrity_manager.update_integrity(module_name, module_path, module_dir)
                integrity_status = "baseline_created"
                self.logger.info(f"Baseline created for {module_name}")
            except Exception as e:
                return {
                    "ok": False,
                    "error": f"Integrity baseline creation failed: {e}",
                    "module": module_name,
                }

        except IntegrityViolation as e:
            self.logger.error(f"INTEGRITY VIOLATION for {module_name}: {e}")
            return {
                "ok": False,
                "error": "INTEGRITY VIOLATION — module load blocked",
                "details": str(e),
                "module": module_name,
            }

        except Exception as e:
            self.logger.error(f"Integrity check error: {e}")
            return {"ok": False, "error": f"Integrity error: {e}", "module": module_name}

        # ==============================================================
        # 4) VALIDATE MODULE (FAZA 36–44)
        # ==============================================================

        ok, msg = self.validator.validate_manifest(module_path, manifest)
        if not ok:
            return {"ok": False, "error": msg}

        ok, msg = self.validator.validate_entrypoint(module_path, manifest)
        if not ok:
            return {"ok": False, "error": msg}

        ok, msg = self.validator.validate_capabilities(manifest)
        if not ok:
            return {"ok": False, "error": f"Capability validation failed: {msg}"}

        ok, msg = self.validator.validate_hooks(module_path, manifest)
        if not ok:
            return {"ok": False, "error": f"Hook validation failed: {msg}"}

        ok, msg = self.validator.validate_default_state(manifest)
        if not ok:
            return {"ok": False, "error": f"State validation failed: {msg}"}

        ok, msg = self.validator.validate_reactive_handlers(module_path, manifest)
        if not ok:
            return {"ok": False, "error": f"Reactive handler validation failed: {msg}"}

        # ==============================================================
        # 5) CREATE CAPABILITIES MAP
        # ==============================================================

        capabilities = self.capability_manager.create_capability_map(
            manifest,
            manifest_obj.name,
            self.event_bus,
            self.scheduler,
            self.async_manager,
        )

        # ==============================================================
        # 6) LOAD MODULE STATE (FAZA 40)
        # ==============================================================

        storage_cap = capabilities.get("storage.write")
        if storage_cap:
            storage = storage_cap.storage
            state = self.state_manager.load_state(manifest_obj.name, manifest, storage)
        else:
            from .module_storage import ModuleStorage
            storage = ModuleStorage(manifest_obj.name)
            state = self.state_manager.load_state(manifest_obj.name, manifest, storage)

        # ==============================================================
        # 7) CREATE MODULE INSTANCE
        # ==============================================================

        entry_class = getattr(mod, manifest["entrypoint"])

        try:
            sig = inspect.signature(entry_class.__init__)
            param_count = len(sig.parameters) - 1

            if param_count >= 3:
                instance = entry_class(self.context, capabilities, state)
            elif param_count == 2:
                instance = entry_class(self.context, capabilities)
                instance.state = state
            else:
                instance = entry_class(self.context)
                instance.capabilities = capabilities
                instance.state = state

        except TypeError:
            instance = entry_class(self.context)
            instance.capabilities = capabilities
            instance.state = state

        # ==============================================================
        # 8) INIT HOOK
        # ==============================================================

        hooks = manifest_obj.get_hooks()

        if hooks.get("init") and hasattr(instance, "init"):
            self.context.set_stage("init")
            try:
                instance.init()
            except Exception as e:
                return {"ok": False, "error": f"init() hook failed: {e}"}

        self.context.set_stage("idle")

        # ==============================================================
        # 9) REACTIVE HANDLERS
        # ==============================================================

        reactive_registered = 0

        if manifest_obj.has_reactive():
            for event_type, method_name in manifest_obj.get_reactive_handlers().items():
                if hasattr(instance, method_name):
                    self.event_bus.subscribe(event_type, getattr(instance, method_name))
                    reactive_registered += 1

        # ==============================================================
        # 10) REGISTER MODULE — WITH integrity_status (FAZA 45)
        # ==============================================================

        self.registry.register(
            manifest_obj.name,
            manifest,
            instance,
            capabilities,
            state,
            integrity_status=integrity_status,  # <-- 🔥 KLJUČNI POPRAVEK
        )

        # ==============================================================
        # 11) Publish module.loaded event
        # ==============================================================

        try:
            event_ctx = EventContext(
                event_type="module.loaded",
                source="module_loader",
                payload={
                    "module_name": manifest_obj.name,
                    "version": manifest.get("version", "unknown"),
                    "phase": manifest.get("phase", "unknown"),
                },
                category="lifecycle",
            )
            self.event_bus.publish("module.loaded", event_ctx)
        except Exception:
            pass

        # ==============================================================
        # END RESPONSE
        # ==============================================================

        return {
            "ok": True,
            "message": f"Module '{manifest_obj.name}' loaded successfully.",
            "module": manifest_obj.name,
            "capabilities_granted": list(capabilities.keys()),
            "reactive_handlers_registered": reactive_registered,
            "state_initialized": True,
            "integrity_status": integrity_status,
        }

    # ==================================================================
    # RUN MODULE DIRECTLY (rarely used)
    # ==================================================================

    def run_module(self, name: str, payload: dict):
        mod_data = self.registry.get(name)
        if not mod_data:
            return {"ok": False, "error": f"Module '{name}' is not loaded."}
        return mod_data["instance"].run(payload)

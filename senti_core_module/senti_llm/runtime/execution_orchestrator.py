"""
FAZA 44 — Execution Orchestrator (LLM Runtime)
Stabilna verzija, popolnoma kompatibilna z:
FAZA 36–Module Loading
FAZA 37–Capability Enforcement
FAZA 38–Module Storage
FAZA 39–Lifecycle Hooks
FAZA 40–Persistent State
FAZA 41–Event Bus
FAZA 42–Reactive Modules
FAZA 43–Internal Scheduler System
FAZA 44–Async Execution Layer
FAZA D.1–AutoDoc
FAZA D.1.1–Logging Layer

Ne spreminja oblike rezultatov, ne lomi testov, in je popolnoma
neinvazivna ter skladna s Senti arhitekturo.
"""

from typing import Any, Dict, Optional
from .action_model import RuntimeAction
from .runtime_exceptions import OrchestratorError
from .module_loader import ModuleLoader
from .llm_runtime_context import RuntimeContext
from .module_manifest import ModuleManifest
from .logging_manager import get_global_logging_manager


class ExecutionOrchestrator:
    """Glavni execution orchestrator za Senti LLM Runtime."""

    def __init__(self, context: Optional[RuntimeContext] = None) -> None:
        if context is None:
            context = RuntimeContext(prompt="", capability="execution")

        self.context = context
        self.module_loader = ModuleLoader(context)

        # Register action handlers
        self.handlers: Dict[str, callable] = {
            "run.module": self._handle_run_module,
            "query.status": self._handle_query_status,
            "execute.task": self._handle_execute_task,
            "load.module": self._handle_load_module,
            "list.modules": self._handle_list_modules,
        }

        # Initialize logging (safe)
        try:
            logging_mgr = get_global_logging_manager()
            self.logger = logging_mgr.get_logger("execution_orchestrator", "FAZA D.1.1")
        except Exception:
            self.logger = None

    # ---------------------------------------------------------
    # PUBLIC EXECUTE ENTRYPOINT
    # ---------------------------------------------------------

    def execute(self, action: RuntimeAction) -> Dict[str, Any]:
        """Universal action executor with strict result format."""

        if action.action_type not in self.handlers:
            raise OrchestratorError(f"Unknown action: {action.action_type}")

        handler = self.handlers[action.action_type]

        # Logging (always safe)
        self._log_action(action)

        # FAZA 43: Tick scheduler on every execute (cooperative scheduling)
        try:
            if hasattr(self.module_loader, 'scheduler') and self.module_loader.scheduler:
                self.module_loader.scheduler.tick()
        except Exception:
            # Scheduler errors must never crash execution
            pass

        # FAZA 44: Tick async_manager on every execute (cooperative async scheduling)
        try:
            if hasattr(self.module_loader, 'async_manager') and self.module_loader.async_manager:
                self.module_loader.async_manager.tick()
        except Exception:
            # Async manager errors must never crash execution
            pass

        try:
            result = handler(action)

            # FAZA 44: Check if result is an awaitable (coroutine)
            import inspect
            if inspect.iscoroutine(result):
                # Handler returned coroutine, create async task
                if hasattr(self.module_loader, 'async_manager') and self.module_loader.async_manager:
                    task_id = self.module_loader.async_manager.create_task(
                        result,
                        metadata={
                            "action_type": action.action_type,
                            "source": action.source
                        }
                    )
                    return {
                        "ok": True,
                        "action_type": action.action_type,
                        "status": "pending",
                        "task_id": task_id,
                        "message": "Async task created"
                    }
                else:
                    return {
                        "ok": False,
                        "action_type": action.action_type,
                        "error": "Handler returned coroutine but no async_manager available"
                    }

            return {
                "ok": True,
                "action_type": action.action_type,
                "data": result,
            }

        except Exception as exc:
            if self.logger:
                try:
                    self.logger.error(f"Execution error in {action.action_type}: {exc}")
                except Exception:
                    pass

            return {
                "ok": False,
                "action_type": action.action_type,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # ACTION HANDLERS
    # ---------------------------------------------------------

    def _handle_run_module(self, action: RuntimeAction) -> Dict[str, Any]:
        """Executes a loaded module with lifecycle hooks & persistent state."""

        module_name = action.payload.get("module")
        if not module_name:
            raise OrchestratorError("Missing 'module' in payload")

        if self.logger:
            try:
                self.logger.info(f"Running module: {module_name}")
            except Exception:
                pass

        # Capability enforcement
        if not self.module_loader.registry.has_capability(module_name, "module.run"):
            if self.logger:
                try:
                    self.logger.warning(f"Execution denied for {module_name}: missing module.run")
                except Exception:
                    pass

            return {
                "ok": False,
                "error": f"Module '{module_name}' lacks module.run capability",
                "status": "capability_denied",
                "module": module_name,
            }

        # Pull module metadata
        mod_data = self.module_loader.registry.get(module_name)
        if not mod_data:
            return {
                "ok": False,
                "message": f"Module '{module_name}' not loaded.",
                "status": "not_loaded",
                "module": module_name,
            }

        instance = mod_data["instance"]
        manifest = mod_data["manifest"]
        state = mod_data.get("state")

        manifest_obj = ModuleManifest(manifest)
        hooks = manifest_obj.get_hooks()

        # Load latest state
        if state:
            state.refresh()

        try:
            # PRE_RUN
            if hooks.get("pre_run") and hasattr(instance, "pre_run"):
                self.context.set_stage("pre_run")
                instance.pre_run(action.payload)

            # RUN
            self.context.set_stage("run")
            result = instance.run(action.payload)

            # POST_RUN
            if hooks.get("post_run") and hasattr(instance, "post_run"):
                self.context.set_stage("post_run")
                instance.post_run(result)

            # Persist state
            if state:
                state.save()

            self.context.set_stage("idle")

            if self.logger:
                try:
                    self.logger.info(f"Module executed successfully: {module_name}")
                except Exception:
                    pass

            return result

        except Exception as exc:
            # Log
            if self.logger:
                try:
                    self.logger.error(f"Module {module_name} failed: {exc}")
                except Exception:
                    pass

            # ON_ERROR hook
            if hooks.get("on_error") and hasattr(instance, "on_error"):
                self.context.set_stage("on_error")
                try:
                    instance.on_error(exc)
                except Exception:
                    pass

            # Persist state changes from on_error
            if state:
                state.save()

            self.context.set_stage("idle")
            raise

    # ---------------------------------------------------------
    # QUERY HANDLERS
    # ---------------------------------------------------------

    def _handle_query_status(self, action: RuntimeAction) -> Dict[str, Any]:
        if self.logger:
            try:
                self.logger.debug(f"Status query by {action.source}")
            except Exception:
                pass

        loaded_modules = self.module_loader.registry.list_modules()

        return {
            "runtime": "Senti LLM Runtime",
            "status": "OK",
            "phase": "FAZA 42",
            "source": action.source,
            "loaded_modules": loaded_modules,
            "module_count": len(loaded_modules),
            "event_bus_active": hasattr(self.module_loader, "event_bus"),
        }

    def _handle_execute_task(self, action: RuntimeAction) -> Dict[str, Any]:
        if self.logger:
            try:
                self.logger.info(f"Executing task: {action.payload.get('task_name')}")
            except Exception:
                pass

        return {
            "message": f"Izvedena naloga: {action.payload.get('task_name')}",
            "result": "success",
        }

    # ---------------------------------------------------------
    # MODULE LOADING HANDLERS
    # ---------------------------------------------------------

    def _handle_load_module(self, action: RuntimeAction) -> Dict[str, Any]:
        path = action.payload.get("path")
        if not path:
            raise OrchestratorError("Missing 'path' in payload")

        if self.logger:
            try:
                self.logger.info(f"Loading module from path: {path}")
            except Exception:
                pass

        return self.module_loader.load(path)

    def _handle_list_modules(self, action: RuntimeAction) -> Dict[str, Any]:
        mods = self.module_loader.registry.list_modules()

        detailed = []
        for name in mods:
            m = self.module_loader.registry.get(name)
            if m:
                caps = m.get("capabilities", {})
                detailed.append({
                    "name": name,
                    "status": m["status"],
                    "version": m["manifest"].get("version", "unknown"),
                    "phase": m["manifest"].get("phase", "unknown"),
                    "capabilities": list(caps.keys()),
                })

        if self.logger:
            try:
                self.logger.debug(f"Listing modules: {len(mods)} found")
            except Exception:
                pass

        return {
            "count": len(mods),
            "modules": detailed,
        }

    # ---------------------------------------------------------
    # INTERNAL LOGGING
    # ---------------------------------------------------------

    def _log_action(self, action: RuntimeAction) -> None:
        """Safe hybrid logging: console + logging layer."""
        print(f"[LLM Runtime] Executing: {action.action_type} from {action.source} -> payload={action.payload}")

        if self.logger:
            try:
                payload_str = str(action.payload)[:200]
                self.logger.info(f"Action {action.action_type} from {action.source} payload={payload_str}")
            except Exception:
                pass

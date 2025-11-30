"""
Senti Core Loader — FAZA 7 (Data Integrity Integration)
Location: senti_core/runtime/loader.py

Namen:
- inicializira Senti Core
- integrira DataIntegrityEngine
- preveri globalna pravila podatkov preden se Senti Core sploh zažene
- registrira minimalne task-e
- pripravi Cognitive Controller
"""

from senti_core.services.event_bus import EventBus
from senti_core.runtime.task_routing_map import task_router
from senti_core.runtime.cognitive_controller import CognitiveController
from senti_core.system.logger import SentiLogger

# FAZA 7 — Data Integrity
from senti_os.security.data_integrity_engine import DataIntegrityEngine, DataIntegrityViolation


class CoreLoader:
    """
    Centralni inicializator Senti Core.
    """

    def __init__(self):
        self.logger = SentiLogger()
        self.event_bus = EventBus()
        self.controller = None

        # FAZA 7 — global Data Integrity Guard
        self.integrity = DataIntegrityEngine(logger=self.logger)

        # FAZA 7 — global flag
        self._hard_blocked = False

    # =====================================================
    # INTERNAL — HARD BLOCK
    # =====================================================

    def _enter_hard_block_state(self, reason: str):
        """
        Kritična varnostna blokada. Senti Core se ustavi.
        """
        self._hard_blocked = True
        self.logger.log("critical", f"SENTI CORE HARD BLOCKED: {reason}")

    def is_hard_blocked(self) -> bool:
        return self._hard_blocked

    # =====================================================
    # PRE-LAUNCH INTEGRITY CHECK
    # =====================================================

    def _preflight_integrity_check(self):
        """
        Preveri, da Senti Core ni zagnan na synthetic ali manjkajočih podatkih.
        """
        try:
            self.integrity.verify_real_data({
                "type": "core_boot",
                "origin": "senti_core.loader",
                "is_real": True,
                "notes": "Core boot sanity check"
            })
        except DataIntegrityViolation as exc:
            self._enter_hard_block_state(str(exc))
            raise

    # =====================================================
    # LOAD CORE SERVICES
    # =====================================================

    def load_services(self):
        """
        Inicializira osnovne core storitve.
        """
        self.logger.log("info", "Loading core services...")

        if self.is_hard_blocked():
            return False

        # EventBus je že pripravljen
        return True

    # =====================================================
    # LOAD COGNITIVE SYSTEM
    # =====================================================

    def load_cognitive_system(self):
        """
        Inicializira Cognitive Controller in Cognitive Loop.
        """
        self.logger.log("info", "Loading cognitive system...")

        if self.is_hard_blocked():
            return False

        self.controller = CognitiveController(logger=self.logger)
        self.logger.log("info", "Cognitive system initialized.")

        return True

    # =====================================================
    # REGISTER CORE TASKS
    # =====================================================

    def register_core_tasks(self):
        """
        Registrira OS-level + core-level osnovne naloge.
        """

        if self.is_hard_blocked():
            self.logger.log("warning", "Skipping task registration — hard block active.")
            return False

        self.logger.log("info", "Registering core tasks...")

        # Primeri minimalnih osnovnih taskov
        def handle_system_health(payload):
            return {"task": "Preveri sistemsko stanje", "context": payload}

        def handle_memory_query(payload):
            return {"task": "Pridobi podatke iz spomina", "context": payload}

        def handle_core_status(payload):
            return {"task": "Prikazi status Senti Core", "context": payload}

        task_router.register("system_health", handle_system_health)
        task_router.register("memory_query", handle_memory_query)
        task_router.register("core_status", handle_core_status)

        self.logger.log(
            "info", f"Registered tasks: {list(task_router.list_tasks().keys())}"
        )

        return True

    # =====================================================
    # MODULE LOADING (FUTURE)
    # =====================================================

    def load_modules(self):
        """
        Prihodnja razširitev. Trenutno preskočeno.
        """
        if self.is_hard_blocked():
            self.logger.log("warning", "Module loading skipped — hard block active.")
            return False

        self.logger.log("debug", "Module loading skipped.")
        return True

    # =====================================================
    # START CORE
    # =====================================================

    def start(self):
        """
        Glavni inicializacijski postopek Senti Core.
        """

        self.logger.log("info", "==== Senti Core Loader START ====")

        # FAZA 7 — kritični preflight check
        try:
            self._preflight_integrity_check()
        except DataIntegrityViolation as exc:
            self.logger.log("critical", f"Preflight integrity check failed: {exc}")
            return {
                "status": "failed",
                "reason": "data_integrity_violation",
                "error": str(exc)
            }

        # Load core services
        if not self.load_services():
            return {"status": "failed", "reason": "services_load_failed"}

        # Load cognitive system
        if not self.load_cognitive_system():
            return {"status": "failed", "reason": "cognitive_system_load_failed"}

        # Register core tasks
        if not self.register_core_tasks():
            return {"status": "failed", "reason": "task_registration_failed"}

        # Load modules (future)
        if not self.load_modules():
            return {"status": "failed", "reason": "module_loading_failed"}

        self.logger.log("info", "==== Senti Core Loader SUCCESS ====")

        return {
            "status": "ok",
            "event_bus": self.event_bus,
            "cognitive_controller": self.controller,
            "integrity_engine": self.integrity
        }

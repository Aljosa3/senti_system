"""
Senti OS Boot Loader
Location: senti_os/boot/boot.py

Glavni vstopni del Senti OS:
- naloži konfiguracijo
- preveri integriteto sistema
- inicializira Senti Core
- inicializira Kernel
- zažene OS servise (KernelLoop, Diagnostics, Watchdog, MemoryCleanup)
- FAZA 5 → Inicializira AI Operational Layer
- FAZA 6 → Inicializira Autonomous Task Loop
- FAZA 7 → Inicializira Data Integrity Engine
- FAZA 8 → Inicializira Security Manager + Security Policy
"""

from pathlib import Path
import json
import logging

# ============================================================
# Senti Core
# ============================================================

from senti_core_module.senti_core.runtime.loader import CoreLoader
from senti_core_module.senti_core.runtime.integrity_checker import IntegrityChecker
from senti_core_module.senti_core.system.logger import SentiLogger

# ============================================================
# Senti OS – Kernel + Services
# ============================================================

from senti_os.kernel.core import SentiKernel
from senti_os.kernel.kernel_loop_service import KernelLoopService

from senti_os.system.service_manager import ServiceManager
from senti_os.system.system_events import SystemEvents
from senti_os.system.system_diagnostics_service import SystemDiagnosticsService
from senti_os.system.watchdog_service import WatchdogService
from senti_os.system.memory_cleanup_service import MemoryCleanupService

# ============================================================
# FAZA 5 – AI Operational Layer
# ============================================================

from senti_os.ai.os_ai_bootstrap import setup_ai_operational_layer

# ============================================================
# FAZA 6 – Autonomous Task Loop
# ============================================================

from senti_os.system.autonomous_task_loop_service import AutonomousTaskLoopService
from senti_os.ai.ai_system_observer import AIStaticSensors

# ============================================================
# FAZA 7 + 8 – Security Layer
# ============================================================

from senti_os.security.security_manager_service import SecurityManagerService
from senti_os.security.security_policy import SecurityPolicy
from senti_os.security.data_integrity_engine import DataIntegrityEngine

# ============================================================
# FAZA 11 – Self-Refactor Engine
# ============================================================

from senti_core_module.senti_refactor import RefactorManager

# ============================================================
# FAZA 12 – Adaptive Memory Engine
# ============================================================

from senti_core_module.senti_memory import MemoryManager

# ============================================================
# FAZA 13 – Prediction Engine
# ============================================================

from senti_core_module.senti_prediction import PredictionManager

# ============================================================
# FAZA 14 – Anomaly Detection Engine
# ============================================================

from senti_core_module.senti_anomaly import AnomalyManager


class SentiBoot:
    """
    Glavni boot loader za Senti OS.
    """

    def __init__(self):
        self.logger = SentiLogger()
        self.project_root = Path(__file__).resolve().parents[2]

        self.config_path = self.project_root / "config" / "system" / "config.yaml"

        # OS-level components
        self.core_loader = CoreLoader()
        self.kernel = SentiKernel()
        self.services = ServiceManager()
        self.events = SystemEvents()

        # === FAZA 7 + FAZA 8 ===
        self.security_policy = SecurityPolicy()
        self.data_integrity = DataIntegrityEngine(logger=self.logger)
        self.security_manager = SecurityManagerService(
            policy=self.security_policy,
            logger=self.logger,
            events=self.events
        )

        # === FAZA 11 ===
        self.refactor_manager = None  # Initialized after core

        # === FAZA 12 ===
        self.memory_manager = None  # Initialized after core

        # === FAZA 13 ===
        self.prediction_manager = None  # Initialized after memory

        # === FAZA 14 ===
        self.anomaly_manager = None  # Initialized after prediction

        self.logger.log("info", "SentiBoot initialized (Security + Integrity + Memory + Prediction + Anomaly Layer enabled).")

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def load_config(self):
        if not self.config_path.exists():
            self.logger.log("warning", "System config not found. Using defaults.")
            return {}

        try:
            import yaml
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                self.logger.log("info", "System config loaded.")
                return config
        except Exception as e:
            self.logger.log("error", f"Failed to load config: {str(e)}")
            return {}

    # =====================================================
    # VERIFY SYSTEM INTEGRITY
    # =====================================================

    def verify_system(self):
        self.logger.log("info", "Verifying system integrity...")

        checker = IntegrityChecker(self.project_root)
        result = checker.run()

        if result.get("status") != "ok":
            self.logger.log("error", "System integrity verification FAILED.")
            self.logger.log("error", json.dumps(result, indent=2))
            return False

        self.logger.log("info", "System integrity verification OK.")
        return True

    # =====================================================
    # CORE INIT
    # =====================================================

    def initialize_core(self):
        self.logger.log("info", "Initializing Senti Core...")

        try:
            core_result = self.core_loader.start()
            if core_result.get("status") == "ok":
                # Store the core's event_bus for use by AI layer
                self.core_event_bus = core_result.get("event_bus")
                self.logger.log("info", "Senti Core initialized.")

                # === FAZA 11 ===
                # Initialize Refactor Manager with event_bus
                self.refactor_manager = RefactorManager(self.project_root, self.core_event_bus)
                self.logger.log("info", "FAZA 11 Refactor Engine initialized.")

                # === FAZA 12 ===
                # Initialize Memory Manager with event_bus
                self.memory_manager = MemoryManager(self.project_root, self.core_event_bus, self.logger)
                memory_init_result = self.memory_manager.start()
                if memory_init_result.get("status") == "ok" or memory_init_result.get("status") == "success":
                    self.logger.log("info", "FAZA 12 Memory Engine initialized.")
                else:
                    self.logger.log("error", f"FAZA 12 Memory Engine initialization failed: {memory_init_result}")

                # === FAZA 13 ===
                # Initialize Prediction Manager with memory_manager and event_bus
                self.prediction_manager = PredictionManager(
                    memory_manager=self.memory_manager,
                    event_bus=self.core_event_bus
                )
                self.logger.log("info", "FAZA 13 Prediction Engine initialized.")

                # === FAZA 14 ===
                # Initialize Anomaly Manager with memory, prediction, event_bus, and security
                self.anomaly_manager = AnomalyManager(
                    memory_manager=self.memory_manager,
                    prediction_manager=self.prediction_manager,
                    event_bus=self.core_event_bus,
                    security_manager=self.security_manager
                )
                self.logger.log("info", "FAZA 14 Anomaly Detection Engine initialized.")

                return True
            else:
                self.logger.log("error", f"Core initialization failed: {core_result}")
                return False
        except Exception as e:
            self.logger.log("error", f"Core initialization failed: {str(e)}")
            return False

    # =====================================================
    # KERNEL INIT
    # =====================================================

    def initialize_kernel(self):
        self.logger.log("info", "Initializing Senti Kernel...")
        self.kernel.start()
        return True

    # =====================================================
    # INITIALIZE SERVICES
    # =====================================================

    def initialize_services(self):
        """
        Registrira in zažene vse ključne OS servise
        """

        self.logger.log("info", "Setting up OS services...")

        # 1) Kernel Loop Service
        kernel_loop_service = KernelLoopService(
            kernel=self.kernel,
            cycles=999999,
            tick_interval=1.0
        )
        self.services.register_service("kernel_loop", kernel_loop_service)
        self.services.start_service("kernel_loop")

        # 2) System Diagnostics Service
        diagnostics_service = SystemDiagnosticsService()
        self.services.register_service("system_diagnostics", diagnostics_service)
        self.services.start_service("system_diagnostics")

        # 3) Watchdog Service
        watchdog_service = WatchdogService(self.services)
        self.services.register_service("watchdog", watchdog_service)
        self.services.start_service("watchdog")

        # 4) Memory Cleanup Service
        cleanup_service = MemoryCleanupService()
        self.services.register_service("memory_cleanup", cleanup_service)
        self.services.start_service("memory_cleanup")

        # 5) Data Integrity Engine
        self.services.register_service("data_integrity_engine", self.data_integrity)

        # 6) Security Manager
        self.services.register_service("security_manager", self.security_manager)

        # 7) Refactor Manager (FAZA 11)
        if self.refactor_manager:
            self.services.register_service("refactor_manager", self.refactor_manager)

        # 8) Memory Manager (FAZA 12)
        if self.memory_manager:
            self.services.register_service("memory_manager", self.memory_manager)

        # 9) Prediction Manager (FAZA 13)
        if self.prediction_manager:
            self.services.register_service("prediction_manager", self.prediction_manager)

        # 10) Anomaly Manager (FAZA 14)
        if self.anomaly_manager:
            self.services.register_service("anomaly_manager", self.anomaly_manager)

        self.logger.log("info", "All OS services initialized.")
        return True

    # =====================================================
    # AI LAYER INIT (FAZA 5 + FAZA 7 + FAZA 8)
    # =====================================================

    def initialize_ai_layer(self):
        """
        FAZA 5 – aktivacija AI Operational Layer.
        """

        self.logger.log("info", "Initializing AI Operational Layer (FAZA 5)...")

        ai_layer = setup_ai_operational_layer(
            kernel=self.kernel,
            event_bus=self.core_event_bus,  # Use core's EventBus instead of SystemEvents
            ai_core_client=None,
            logger=logging.getLogger("SentiAI"),
            integrity_engine=self.data_integrity,      # FAZA 7
            security_manager=self.security_manager,    # FAZA 8
            refactor_manager=self.refactor_manager,    # FAZA 11
            memory_manager=self.memory_manager,        # FAZA 12
            prediction_manager=self.prediction_manager,# FAZA 13
            anomaly_manager=self.anomaly_manager       # FAZA 14
        )

        self.logger.log("info", "AI Operational Layer initialized.")
        return ai_layer

    # =====================================================
    # AUTONOMOUS TASK LOOP INIT (FAZA 6)
    # =====================================================

    def initialize_autonomous_loop(self, ai_layer):
        """
        FAZA 6 – Autonomous Task Loop

        Note: The autonomous loop has access to FAZA 11 Refactor Manager,
        FAZA 12 Memory Manager, FAZA 13 Prediction Manager, and FAZA 14 Anomaly Manager
        through ai_layer for self-healing, memory maintenance, predictive capabilities,
        and anomaly detection.
        """

        self.logger.log("info", "Initializing Autonomous Task Loop Service (FAZA 6)...")

        sensors = AIStaticSensors(
            kernel=self.kernel,
            services=self.services,
            task_engine=ai_layer["task_engine"],
            logger=self.logger
        )

        autonomous_service = AutonomousTaskLoopService(
            ai_os_agent=ai_layer["ai_agent"],
            sensors=sensors,
            tick_interval=5.0,
            logger=self.logger,
            memory_manager=ai_layer.get("memory_manager"),        # FAZA 12
            prediction_manager=ai_layer.get("prediction_manager"),# FAZA 13
            anomaly_manager=ai_layer.get("anomaly_manager")       # FAZA 14
        )

        self.services.register_service("autonomous_task_loop", autonomous_service)
        self.services.start_service("autonomous_task_loop")

        self.logger.log("info", "Autonomous Task Loop activated (with FAZA 11 + FAZA 12 access).")
        return autonomous_service

    # =====================================================
    # BOOT START
    # =====================================================

    def start(self):
        """
        Glavni vstopni klic Senti OS Boot.
        """

        self.logger.log("info", "==== SENTI OS BOOT START ====")

        self.load_config()

        # FAZA 7 – preveri, da boot podatki niso synthetic
        try:
            self.data_integrity.verify_real_data({
                "type": "os_boot",
                "origin": "boot.py",
                "is_real": True,
                "notes": "OS boot integrity check"
            })
        except Exception as exc:
            self.logger.log("critical", f"OS boot blocked by Data Integrity Engine: {exc}")
            return {"status": "error", "message": "Security integrity failure"}

        if not self.verify_system():
            return {"status": "error", "message": "Integrity check failed"}

        if not self.initialize_core():
            return {"status": "error", "message": "Core failed to load"}

        self.initialize_kernel()
        self.initialize_services()

        # FAZA 5
        ai_layer = self.initialize_ai_layer()

        # FAZA 6
        self.initialize_autonomous_loop(ai_layer)

        self.events.info("Data Integrity Engine initialized and active.")
        self.events.os_ready()

        self.logger.log("info", "==== SENTI OS READY ====")

        return {
            "status": "ok",
            "message": "Senti OS successfully started (Security + Integrity Layer active)",
            "kernel": self.kernel,
            "services": self.services,
            "ai_layer": ai_layer,
        }


if __name__ == "__main__":
    SentiBoot().start()

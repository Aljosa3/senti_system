"""
Senti OS Kernel Core
Location: senti_os/kernel/core.py

Naloga Kernel-a:
- upravlja sistemske signale (OS-level events)
- pripravlja globalni OS context
- posreduje dogodke v EventBus
- ponuja osnovno infrastrukturo za OS procesni sistem (prihodnost)
- služi kot centralna točka komunikacije med Senti OS in Senti Core Runtime
"""

from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_core.system.logger import SentiLogger


class SentiKernel:
    """
    Jedro Senti OS.
    """

    def __init__(self):
        self.logger = SentiLogger()
        self.event_bus = EventBus()
        self.global_state = {}

        self.logger.log("info", "SentiKernel initialized.")

    # =====================================================
    # SISTEMSKI SIGNALI
    # =====================================================

    def emit_signal(self, signal_type: str, payload: dict = None):
        """
        Ustvari OS-level signal in ga posreduje EventBus-u.
        """
        payload = payload if payload else {}

        self.logger.log("debug", f"[OS SIGNAL] {signal_type} : {payload}")

        self.event_bus.publish(signal_type, payload)

    # =====================================================
    # KONTEKST
    # =====================================================

    def update_state(self, key: str, value):
        """
        Posodobi OS globalno stanje (npr. baterija, zdravje sistema, uptime).
        """
        self.global_state[key] = value
        self.logger.log("debug", f"[OS STATE] {key} = {value}")

    def get_state(self):
        """
        Vrne kopijo globalnega OS stanja.
        """
        return dict(self.global_state)

    # =====================================================
    # TASK ENGINE ATTACHMENT
    # =====================================================

    def attach_task_engine(self, task_engine):
        """
        Pritrdi TaskOrchestrationEngine na kernel za AI layer integration.
        """
        self.task_engine = task_engine
        self.logger.log("info", "TaskOrchestrationEngine attached to kernel.")

    # =====================================================
    # KERNEL LOOP (placeholder — FAZA 3.4)
    # =====================================================

    def run(self):
        """
        OS-level procesna zanka.
        Pripravljeno za prihodnjo integracijo.
        """
        self.logger.log("info", "Kernel run loop start (not implemented).")

    # =====================================================
    # INTEGRACIJA Z BOOT LOADERJEM
    # =====================================================

    def start(self):
        """
        Inicializira Kernel po boot sekvenci.
        """
        self.logger.log("info", "Starting Senti Kernel...")
        self.emit_signal("kernel_started", {"status": "ok"})
        return True

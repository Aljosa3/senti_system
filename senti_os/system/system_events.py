"""
Senti OS System Events
Location: senti_os/system/system_events.py

Naloga:
- Standardiziran API za OS-level dogodke
- Pošiljanje sistemskih signalov v EventBus
- Integracija med Kernel → EventBus → Cognitive Controller
"""

from datetime import datetime
from senti_core.services.event_bus import EventBus
from senti_core.system.logger import SentiLogger


class SystemEvents:
    """
    Centralna točka za generiranje OS-level dogodkov.
    """

    def __init__(self):
        self.event_bus = EventBus()
        self.logger = SentiLogger()
        self.logger.log("info", "SystemEvents ready.")

    # =====================================================
    # HELPER: STANDARD PAYLOAD SHAPE
    # =====================================================

    def to_payload(self, event_type: str, data: dict):
        """
        Ustvari standardiziran payload za OS dogodke.
        """
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "data": data
        }

    # =====================================================
    # GENERIC EVENTS
    # =====================================================

    def emit(self, event_type: str, data: dict = None):
        """
        Pošlje generični OS dogodek v EventBus.
        """
        payload = self.to_payload(event_type, data or {})
        self.logger.log("debug", f"[OS EVENT] {event_type}: {payload}")
        self.event_bus.publish(event_type, payload)

    def info(self, message: str):
        self.emit("os_info", {"message": message})

    def warn(self, message: str):
        self.emit("os_warning", {"message": message})

    def critical(self, message: str):
        self.emit("os_critical", {"message": message})

    # =====================================================
    # PREDEFINED SYSTEM EVENTS
    # =====================================================

    def system_health(self, status: str, metrics: dict = None):
        """
        Standardiziran dogodek za poročanje o zdravju OS sistema.
        """
        data = {
            "status": status,
            "metrics": metrics or {}
        }
        self.emit("system_health", data)

    def kernel_started(self):
        """
        Emit OS signal ob zagonu jedra.
        """
        self.emit("kernel_started", {"status": "ok"})

    def os_ready(self):
        """
        Emit OS signal, da je OS pripravljen za delovanje.
        """
        self.emit("os_ready", {"message": "Senti OS successfully initialized."})

    # =====================================================
    # FAZA 7 — DATA INTEGRITY VIOLATION EVENT
    # =====================================================

    def data_integrity_violation(self, details: dict):
        """
        Emit kritični OS-level dogodek, ko Data Integrity Engine
        zazna kršitev (nerealni podatki, manjkajoči realni podatki, itd.).
        """
        payload = {
            "details": details,
            "severity": "critical"
        }
        self.emit("DATA_INTEGRITY_VIOLATION", payload)

"""
System Diagnostics Service
Location: senti_os/system/system_diagnostics_service.py

Naloga:
- posluša health metrike od driverjev
- analizira obremenitve
- pošilja opozorila in diagnostične evente
- deluje kot OS service (start/stop/status)
"""

from senti_core_module.senti_core.system.logger import SentiLogger
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_os.system.system_events import SystemEvents


class SystemDiagnosticsService:
    """
    Analizira sistemske metrike in oddaja opozorila ter diagnostične signale.
    """

    def __init__(self):
        self.logger = SentiLogger()
        self.event_bus = EventBus()
        self.events = SystemEvents()

        self.running = False

        # pragovi
        self.THRESHOLD_CPU = 90
        self.THRESHOLD_RAM = 90
        self.THRESHOLD_DISK = 90

        # registracija event listenerja
        self.event_bus.subscribe("system_health_metric", self.handle_metric_event)

        self.logger.log("info", "SystemDiagnosticsService created.")

    # =====================================================
    # OS SERVICE START/STOP
    # =====================================================

    def start(self):
        self.logger.log("info", "[DIAGNOSTICS] Service started.")
        self.running = True
        return True

    def stop(self):
        self.logger.log("info", "[DIAGNOSTICS] Service stopped.")
        self.running = False
        return True

    # =====================================================
    # METRIK DOGODKI
    # =====================================================

    def handle_metric_event(self, payload: dict):
        """
        Prejme sistemske health metrike iz health_monitor_driver.
        """
        if not self.running:
            return

        data = payload.get("data", {})

        cpu = data.get("cpu_percent", 0)
        ram = data.get("ram_percent", 0)
        disk = data.get("disk_percent", 0)

        # -----------------------------------------
        # CPU
        # -----------------------------------------
        if cpu > self.THRESHOLD_CPU:
            self.events.warn(f"High CPU usage: {cpu}%")
            self.emit_diagnostic("cpu_overload", {"value": cpu})

        # -----------------------------------------
        # RAM
        # -----------------------------------------
        if ram > self.THRESHOLD_RAM:
            self.events.warn(f"High RAM usage: {ram}%")
            self.emit_diagnostic("ram_overload", {"value": ram})

        # -----------------------------------------
        # DISK
        # -----------------------------------------
        if disk > self.THRESHOLD_DISK:
            self.events.critical(f"Critical Disk usage: {disk}%")
            self.emit_diagnostic("disk_critical", {"value": disk})

    # =====================================================
    # EMIT DIAGNOSTIC EVENT
    # =====================================================

    def emit_diagnostic(self, event_type: str, data: dict):
        """
        Odda OS-level diagnostični dogodek.
        """
        self.event_bus.publish("system_diagnostic_event", {
            "diagnostic_type": event_type,
            "data": data
        })

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):
        return {
            "service": "system_diagnostics",
            "running": self.running,
            "cpu_threshold": self.THRESHOLD_CPU,
            "ram_threshold": self.THRESHOLD_RAM,
            "disk_threshold": self.THRESHOLD_DISK
        }

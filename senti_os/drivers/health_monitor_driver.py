"""
Health Monitor Driver
Location: senti_os/drivers/health_monitor_driver.py

Naloga:
- nadzor CPU, RAM, DISK in sistemske obremenitve
- pošiljanje OS health metrik v EventBus
- integracija s KernelLoop (vsak tick)

"""

import psutil
from senti_os.drivers.driver_base import DriverBase
from senti_core_module.senti_core.system.logger import SentiLogger


class HealthMonitorDriver(DriverBase):
    """
    Driver za spremljanje sistemskih metrik.
    """

    def __init__(self):
        super().__init__(
            name="health_monitor",
            driver_type="sensor",
            metadata={"description": "CPU/RAM/Disk health monitor driver"}
        )
        self.logger = SentiLogger()

    # =====================================================
    # LOAD / START
    # =====================================================

    def load(self):
        self.logger.log("info", "[HEALTH MONITOR] Loading...")
        self.loaded = True
        return True

    def start(self):
        if not self.loaded:
            self.logger.log("error", "Cannot start HealthMonitorDriver – not loaded.")
            return False

        self.active = True
        self.logger.log("info", "[HEALTH MONITOR] Started.")
        return True

    # =====================================================
    # TICK — CALLED FROM KernelLoop
    # =====================================================

    def tick(self):
        """
        Prebere trenutno stanje sistema in odda health event.
        """

        if not self.active:
            return

        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        metrics = {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_mb": round(ram.used / 1024 / 1024, 2),
            "ram_total_mb": round(ram.total / 1024 / 1024, 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
            "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
        }

        # Pošlji OS driver event
        self.emit_event("system_health_metric", metrics)

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):
        base = super().status()
        base["health_monitor_active"] = self.active
        return base

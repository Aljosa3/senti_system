"""
Senti OS Kernel Loop
Location: senti_os/kernel/kernel_loop.py

Naloga:
- glavni OS-level procesni cikel
- upravljanje uptime, health, driver polling
- integracija z SystemEvents in SentiKernel
"""

import time
from datetime import datetime

from senti_os.system.system_events import SystemEvents
from senti_os.kernel.core import SentiKernel
from senti_core.system.logger import SentiLogger


class KernelLoop:
    """
    Glavni OS procesni cikel.
    """

    def __init__(self, kernel: SentiKernel, tick_interval: float = 1.0):
        self.kernel = kernel
        self.tick_interval = tick_interval  # koliko sekund med cikli
        self.events = SystemEvents()
        self.logger = SentiLogger()

        self.start_time = datetime.utcnow()

        # seznam driverjev (doda se v prihodnjih fazah)
        self.drivers = []

        self.logger.log("info", "KernelLoop initialized.")

    # =====================================================
    # HELPER: UPTIME
    # =====================================================

    def update_uptime(self):
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        self.kernel.update_state("uptime_seconds", uptime_seconds)

    # =====================================================
    # HELPER: POLL DRIVERS
    # =====================================================

    def poll_drivers(self):
        for driver in self.drivers:
            try:
                if hasattr(driver, "tick"):
                    driver.tick()
            except Exception as e:
                self.logger.log("error", f"Driver tick failed ({driver.name}): {str(e)}")

    # =====================================================
    # OS HEALTH BROADCAST
    # =====================================================

    def broadcast_health(self):
        uptime = self.kernel.get_state().get("uptime_seconds", 0)

        # Minimalni health metrics
        metrics = {
            "uptime_seconds": uptime,
            "drivers_loaded": len(self.drivers)
        }

        self.events.system_health("ok", metrics)

    # =====================================================
    # SINGLE TICK
    # =====================================================

    def tick(self):
        """
        Izvede en OS cikel.
        """
        try:
            self.update_uptime()
            self.poll_drivers()
            self.broadcast_health()
        except Exception as e:
            self.logger.log("error", f"Kernel tick failed: {str(e)}")

    # =====================================================
    # CONTINUOUS LOOP (SAFE)
    # =====================================================

    def run(self, cycles: int = 10):
        """
        Zažene kontinuiran OS loop za določeno število ciklov.
        (Brez neskončnih while True – skladno s Senti varnostjo)
        """
        self.logger.log("info", f"KernelLoop run start for {cycles} cycles...")

        for _ in range(cycles):
            self.tick()
            time.sleep(self.tick_interval)

        self.logger.log("info", "KernelLoop run complete.")

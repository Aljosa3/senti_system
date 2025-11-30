"""
Watchdog Service
Location: senti_os/system/watchdog_service.py

Naloga:
- nadzira OS servise
- preverja ali tečejo (running + thread_alive)
- oddaja opozorila / critical signale
- samodejno restartuje servise
- integracija z EventBus in SystemEvents
"""

import time
from senti_core.system.logger import SentiLogger
from senti_core.services.event_bus import EventBus
from senti_os.system.system_events import SystemEvents


class WatchdogService:
    """
    OS-level proces, ki nadzira stabilnost sistemskih servisov.
    """

    def __init__(self, service_manager, check_interval: float = 3.0):
        self.logger = SentiLogger()
        self.event_bus = EventBus()
        self.events = SystemEvents()
        self.services = service_manager
        self.check_interval = check_interval

        self.running = False
        self.last_check = 0

        self.logger.log("info", "WatchdogService initialized.")

    # =====================================================
    # SERVICE LIFECYCLE
    # =====================================================

    def start(self):
        self.logger.log("info", "[WATCHDOG] Service started.")
        self.running = True
        return True

    def stop(self):
        self.logger.log("info", "[WATCHDOG] Service stopped.")
        self.running = False
        return True

    # =====================================================
    # TICK — KLIČE GA KernelLoop
    # =====================================================

    def tick(self):
        if not self.running:
            return

        now = time.time()
        if now - self.last_check < self.check_interval:
            return  # še ni čas

        self.last_check = now

        # preveri vse servise
        service_list = self.services.list_services()

        for name in service_list:
            status = self.services.service_status(name)

            if "error" in status:
                # storitev nima status() implementiran
                self.events.warn(f"Watchdog: unable to read status for {name}.")
                continue

            running = status.get("running", True)
            thread_alive = status.get("thread_alive", True)

            # ============================
            # 1) PREVERI, ALI SE JE USTAVIL
            # ============================
            if not running or not thread_alive:
                self.events.critical(
                    f"Watchdog: Service '{name}' stopped unexpectedly."
                )

                self.event_bus.publish("watchdog_event", {
                    "service": name,
                    "action": "unexpected_stop",
                    "status": status
                })

                # Poskusi restart
                self.logger.log("warning", f"[WATCHDOG] Restarting service '{name}'...")
                self.services.restart_service(name)

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):
        return {
            "service": "watchdog",
            "running": self.running,
            "check_interval": self.check_interval
        }

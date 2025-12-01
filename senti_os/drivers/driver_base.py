"""
Driver Base Class
Location: senti_os/drivers/driver_base.py

Naloga:
- uvesti standardiziran OS driver model
- zagotoviti varnost OS-level driverjev
- poenotiti dostop do senzorjev, aktuatorjev in IO sistemov
"""

from senti_core.services.event_bus import EventBus
from senti_core.system.logger import SentiLogger


class DriverBase:
    """
    Osnovna klasa za vse driverje v Senti OS.
    """

    def __init__(self, name: str, driver_type: str, metadata: dict = None):
        self.name = name
        self.driver_type = driver_type  # sensor, actuator, io, virtual
        self.metadata = metadata or {}
        self.loaded = False
        self.active = False

        self.event_bus = EventBus()
        self.logger = SentiLogger()

        self.logger.log("info", f"Driver created: {name} [{driver_type}]")

    # =====================================================
    # CORE DRIVER OPERATIONS
    # =====================================================

    def load(self) -> bool:
        """
        Inicializira driver.
        Override v podrazredih.
        """
        self.logger.log("info", f"[DRIVER] Loading {self.name}...")
        self.loaded = True
        return True

    def start(self) -> bool:
        """
        Začne obratovanje driverja.
        Override v podrazredih.
        """
        if not self.loaded:
            self.logger.log("error", f"Cannot start driver {self.name} – not loaded.")
            return False

        self.active = True
        self.logger.log("info", f"[DRIVER] Started {self.name}")
        return True

    def stop(self) -> bool:
        """
        Ustavi driver.
        """
        if not self.active:
            self.logger.log("warning", f"Driver {self.name} is not active.")
            return False

        self.active = False
        self.logger.log("info", f"[DRIVER] Stopped {self.name}")
        return True

    # =====================================================
    # SENSOR/ACTUATOR INTERFACE (override v podrazredih)
    # =====================================================

    def read(self):
        """
        Za senzorje: vrne podatke.
        Override v podrazredih.
        """
        self.logger.log("warning", f"[DRIVER] read() not implemented for {self.name}.")
        return None

    def write(self, data):
        """
        Za aktuatorje: spreminja stanje.
        Override v podrazredih.
        """
        self.logger.log("warning", f"[DRIVER] write() not implemented for {self.name}.")
        return False

    # =====================================================
    # DRIVER INFO
    # =====================================================

    def status(self) -> dict:
        """
        Vrne stanje driverja.
        """
        return {
            "name": self.name,
            "type": self.driver_type,
            "loaded": self.loaded,
            "active": self.active,
            "metadata": self.metadata
        }

    # =====================================================
    # EVENT EMIT
    # =====================================================

    def emit_event(self, event_type: str, data: dict = None):
        """
        Pošlje OS driver dogodek v EventBus.
        """
        payload = {
            "driver": self.name,
            "type": self.driver_type,
            "data": data or {}
        }

        self.logger.log("debug", f"[DRIVER EVENT] {event_type}: {payload}")
        self.event_bus.publish(event_type, payload)

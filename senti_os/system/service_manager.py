"""
Senti OS Service Manager
Location: senti_os/system/service_manager.py

Naloga:
- upravljanje OS servisov (nalaganje, zagon, ustavljanje)
- registracija servisov
- integracija z Kernel in EventBus
- zagotavljanje OS-level modularnosti
- (FAZA 7) globalni data-integrity hook
"""

from senti_core_module.senti_core.system.logger import SentiLogger
from senti_core_module.senti_core.services.event_bus import EventBus


class ServiceManager:
    """
    Centralni upravljalec servisov za Senti OS.
    """

    def __init__(self):
        self.logger = SentiLogger()
        self.event_bus = EventBus()

        # mapa: ime → instanca servisa
        self.services = {}

        self.logger.log("info", "ServiceManager initialized.")

    # =====================================================
    # REGISTRACIJA
    # =====================================================

    def register_service(self, name: str, instance):
        """
        Registrira nov OS servis.
        Servisi morajo imeti metode:
        - start()
        - stop()
        - status()
        """
        if name in self.services:
            self.logger.log("warning", f"Service '{name}' already registered.")
            return False

        self.services[name] = instance
        self.logger.log("info", f"Service '{name}' registered.")
        return True

    # =====================================================
    # ZAŽENI SERVIS
    # =====================================================

    def start_service(self, name: str):
        if name not in self.services:
            self.logger.log("error", f"Service '{name}' not found.")
            return False

        service = self.services[name]

        try:
            service.start()
            self.event_bus.publish("service_started", {"service": name})
            self.logger.log("info", f"Service '{name}' started.")
            return True
        except Exception as e:
            self.logger.log("error", f"Failed to start service '{name}': {str(e)}")
            return False

    # =====================================================
    # USTAVI SERVIS
    # =====================================================

    def stop_service(self, name: str):
        if name not in self.services:
            self.logger.log("error", f"Service '{name}' not found.")
            return False

        service = self.services[name]

        try:
            service.stop()
            self.event_bus.publish("service_stopped", {"service": name})
            self.logger.log("info", f"Service '{name}' stopped.")
            return True
        except Exception as e:
            self.logger.log("error", f"Failed to stop service '{name}': {str(e)}")
            return False

    # =====================================================
    # PONOVEN ZAGON
    # =====================================================

    def restart_service(self, name: str):
        """
        Uporablja stop → start sekvenco.
        """
        self.logger.log("info", f"Restarting service '{name}'...")

        if not self.stop_service(name):
            return False
        return self.start_service(name)

    # =====================================================
    # STATUS
    # =====================================================

    def service_status(self, name: str):
        if name not in self.services:
            return {"error": "not_found"}

        service = self.services[name]
        try:
            return service.status()
        except Exception as e:
            self.logger.log("error", f"Failed to get status for '{name}': {str(e)}")
            return {"error": "status_failed"}

    # =====================================================
    # SEZNAM SERVISOV
    # =====================================================

    def list_services(self):
        return list(self.services.keys())

    # =====================================================
    # (FAZA 7) GLOBALNI DATA INTEGRITY HOOK
    # =====================================================

    def check_data_source(self, source_metadata: dict):
        """
        OS-level zaščita podatkov.
        
        Pokliče DataIntegrityEngine, če je registriran.
        Uporablja se v vseh modulih, ki nalagajo podatke.
        
        source_metadata primer:
        {
            "type": "api",
            "origin": "kraken_spot",
            "is_real": True,
            "missing": False
        }
        """

        engine = self.services.get("data_integrity", None)

        if not engine:
            # Integrity engine ni naložen (ne bi se smelo zgoditi)
            self.logger.log("warning", "DataIntegrityEngine ni registriran.")
            return True

        # 1 — blokiraj, če podatki manjkajo
        if source_metadata.get("missing", False):
            self.logger.log("critical", "Realni podatki manjkajo — blokiram servis.")
            raise Exception("Realni podatki manjkajo — zagotovite realen vir.")

        # 2 — blokiraj, če podatki niso realni
        try:
            engine.verify_real_data(source_metadata)
        except Exception as e:
            self.logger.log("critical", f"DATA INTEGRITY VIOLATION: {str(e)}")
            raise

        return True

"""
Memory Cleanup Service
Location: senti_os/system/memory_cleanup_service.py

Naloga:
- rotira loge
- čisti temp direktorije
- čisti event cache
- omejuje rast OS datotek
- periodično oddaja diagnostic events
"""

import os
import time
from pathlib import Path

from senti_core.system.logger import SentiLogger
from senti_core.services.event_bus import EventBus
from senti_os.system.system_events import SystemEvents


class MemoryCleanupService:
    """
    OS-level servis za avtomatsko čiščenje spomina,
    rotacijo logov in nadzor rasti začasnih datotek.
    """

    def __init__(self, cleanup_interval: float = 30.0):
        self.logger = SentiLogger()
        self.event_bus = EventBus()
        self.events = SystemEvents()

        self.running = False
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = 0

        self.project_root = Path(__file__).resolve().parents[2]

        # dovoljene mape za čiščenje
        self.logs_dir = self.project_root / "logs"
        self.temp_dir = self.project_root / "_temp"
        self.cache_dir = self.project_root / "cache"

        self.logger.log("info", "MemoryCleanupService initialized.")

    # =====================================================
    # START / STOP
    # =====================================================

    def start(self):
        self.running = True
        self.logger.log("info", "[CLEANUP] Service started.")
        return True

    def stop(self):
        self.running = False
        self.logger.log("info", "[CLEANUP] Service stopped.")
        return True

    # =====================================================
    # TICK — periodično čiščenje
    # =====================================================

    def tick(self):
        if not self.running:
            return

        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        self.last_cleanup = now

        self.cleanup_logs()
        self.cleanup_temp()
        self.cleanup_cache()

    # =====================================================
    # LOG ROTATION
    # =====================================================

    def cleanup_logs(self):
        if not self.logs_dir.exists():
            return

        total_size_mb = 0

        for file in self.logs_dir.glob("*.log"):
            try:
                size_mb = file.stat().st_size / 1024 / 1024
                total_size_mb += size_mb

                # rotiraj datoteke nad 20 MB
                if size_mb > 20:
                    rotated = file.with_suffix(f".log.old")
                    file.rename(rotated)
                    self.events.warn(f"Rotated large log: {file.name}")
            except Exception as e:
                self.logger.log("error", f"Log cleanup error: {str(e)}")

        if total_size_mb > 100:
            self.events.warn("Log directory exceeds 100MB.")

    # =====================================================
    # TEMP CLEANUP
    # =====================================================

    def cleanup_temp(self):
        if not self.temp_dir.exists():
            return

        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except:
                continue

        self.events.info("Temp directory cleaned.")

    # =====================================================
    # CACHE CLEANUP
    # =====================================================

    def cleanup_cache(self):
        if not self.cache_dir.exists():
            return

        for file in self.cache_dir.glob("*"):
            try:
                file.unlink()
            except:
                continue

        self.event_bus.publish("cleanup_event", {
            "type": "cache_cleanup",
            "message": "Cache directory cleaned."
        })

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):
        return {
            "service": "memory_cleanup",
            "running": self.running,
            "cleanup_interval": self.cleanup_interval
        }

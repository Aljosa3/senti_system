from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class SystemSnapshot:
    """
    Canonical sistemski 'posnetek'.

    Vključuje podatke relevantne za:
    - AI Maintenance Planner
    - AI Recovery Planner
    - AI Agent

    Minimalna neodvisna struktura, skladna s PROJECT_RULES.
    """

    timestamp: float
    cpu_load: float
    memory_used_percent: float
    task_engine_stats: Dict[str, Any]
    service_status: Dict[str, Any]


class AIStaticSensors:
    """
    Minimalni modularni senzorji (brez neposrednega dostopa do OS).
    Kernel/Services injicirajo informacije preko abstraktnih callbackov.
    """

    def __init__(self, kernel, services, task_engine, logger=None):
        self._kernel = kernel
        self._services = services
        self._task_engine = task_engine
        self._log = logger or logging.getLogger(__name__)

    def read_cpu_load(self) -> float:
        load = self._kernel.get_cpu_load()
        return float(load)

    def read_memory_usage(self) -> float:
        usage = self._kernel.get_memory_usage_percent()
        return float(usage)

    def read_task_engine(self) -> Dict[str, Any]:
        return self._task_engine.snapshot_state()

    def read_service_status(self) -> Dict[str, Any]:
        status = {}
        for name, service in self._services.services.items():
            status[name] = service.get_status() if hasattr(service, "get_status") else "unknown"
        return status


class AISystemObserver:
    """
    Periodični AI opazovalec sistema (FAZA 6).
    Generira SystemSnapshot, ki ga uporablja:
        - AI Maintenance Planner
        - AI OS Agent (preko eventov)
    """

    def __init__(self, sensors: AIStaticSensors, logger=None):
        self._sensors = sensors
        self._log = logger or logging.getLogger(__name__)

    def capture_snapshot(self) -> SystemSnapshot:
        """Zbere celotne sistemske metrike."""
        snapshot = SystemSnapshot(
            timestamp=time.time(),
            cpu_load=self._sensors.read_cpu_load(),
            memory_used_percent=self._sensors.read_memory_usage(),
            task_engine_stats=self._sensors.read_task_engine(),
            service_status=self._sensors.read_service_status(),
        )

        self._log.debug("AISystemObserver snapshot: %s", snapshot)
        return snapshot

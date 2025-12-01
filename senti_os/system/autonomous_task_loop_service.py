from __future__ import annotations

import time
import threading
import logging

from senti_os.system.base_service import BaseService
from senti_os.ai.ai_system_observer import AISystemObserver
from senti_os.ai.ai_maintenance_planner import AIMaintenancePlanner


class AutonomousTaskLoopService(BaseService):
    """
    FAZA 6 — glavni AI background service.
    Teče kot stalna zanka.
    """

    def __init__(
        self,
        ai_os_agent,
        sensors,
        tick_interval: float = 5.0,
        logger=None
    ):
        super().__init__("autonomous_task_loop")
        self._ai_agent = ai_os_agent
        self._tick = tick_interval
        self._log = logger or logging.getLogger(__name__)

        self._observer = AISystemObserver(sensors, logger=self._log)
        self._planner = AIMaintenancePlanner(logger=self._log)

        self._thread = None
        self._running = False

    # -------------------------------------------------------
    # Service lifecycle
    # -------------------------------------------------------

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log.info("AutonomousTaskLoopService started.")

    def stop(self):
        self._running = False
        self._log.info("AutonomousTaskLoopService stopped.")

    # -------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------

    def _loop(self):
        while self._running:
            try:
                snapshot = self._observer.capture_snapshot()
                cmds = self._planner.plan_maintenance(snapshot)

                # Pošlji AI OS Agentu
                for cmd in cmds:
                    self._ai_agent.process_command(cmd)

            except Exception as e:
                self._log.exception("AutonomousTaskLoopService error: %s", e)

            time.sleep(self._tick)

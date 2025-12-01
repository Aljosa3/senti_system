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
    Integrates with FAZA 12 Memory Manager for periodic maintenance.
    Integrates with FAZA 13 Prediction Manager for predictive capabilities.
    Integrates with FAZA 14 Anomaly Manager for anomaly detection.
    """

    def __init__(
        self,
        ai_os_agent,
        sensors,
        tick_interval: float = 5.0,
        logger=None,
        memory_manager=None,
        prediction_manager=None,
        anomaly_manager=None
    ):
        super().__init__("autonomous_task_loop")
        self._ai_agent = ai_os_agent
        self._tick = tick_interval
        self._log = logger or logging.getLogger(__name__)
        self._memory_manager = memory_manager
        self._prediction_manager = prediction_manager
        self._anomaly_manager = anomaly_manager

        self._observer = AISystemObserver(sensors, logger=self._log)
        self._planner = AIMaintenancePlanner(logger=self._log)

        self._thread = None
        self._running = False
        self._loop_count = 0  # Track iterations for memory maintenance

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

                # FAZA 12 — Memory maintenance (every 12 iterations, ~1 minute with 5s tick)
                self._loop_count += 1
                if self._memory_manager and self._loop_count % 12 == 0:
                    self._perform_memory_maintenance()

                # FAZA 13 — Prediction (every 12 iterations, ~1 minute with 5s tick)
                if self._prediction_manager and self._loop_count % 12 == 0:
                    self._perform_prediction()

                # FAZA 14 — Anomaly Detection (every 6 iterations, ~30 seconds with 5s tick)
                if self._anomaly_manager and self._loop_count % 6 == 0:
                    self._perform_anomaly_detection()

            except Exception as e:
                self._log.exception("AutonomousTaskLoopService error: %s", e)

            time.sleep(self._tick)

    def _perform_memory_maintenance(self):
        """
        Perform FAZA 12 memory maintenance tasks.
        Called periodically by autonomous loop.
        """
        try:
            self._log.info("Performing FAZA 12 memory maintenance...")
            result = self._memory_manager.perform_maintenance()

            if result.get("status") == "success":
                self._log.info("Memory maintenance completed successfully")
            else:
                self._log.warning(f"Memory maintenance had issues: {result}")

        except Exception as e:
            self._log.exception("Memory maintenance failed: %s", e)

    def _perform_prediction(self):
        """
        Perform FAZA 13 prediction operations.
        Called periodically by autonomous loop.
        """
        try:
            self._log.info("Performing FAZA 13 system prediction...")
            results = self._prediction_manager.full_system_prediction()

            # Log high-risk predictions
            for category, result in results.items():
                if result.risk_score > 70:
                    self._log.warning(
                        f"HIGH RISK prediction in {category}: {result.prediction} "
                        f"(risk={result.risk_score}, confidence={result.confidence})"
                    )

            self._log.info("System prediction completed successfully")

        except Exception as e:
            self._log.exception("System prediction failed: %s", e)

    def _perform_anomaly_detection(self):
        """
        Perform FAZA 14 anomaly detection operations.
        Called periodically by autonomous loop.
        """
        try:
            self._log.info("Performing FAZA 14 anomaly detection...")
            results = self._anomaly_manager.analyze_system()

            # Log anomalies
            for component, anomaly in results.items():
                if anomaly.severity in ["HIGH", "CRITICAL"]:
                    self._log.warning(
                        f"HIGH SEVERITY anomaly in {component}: {anomaly.reason} "
                        f"(score={anomaly.score}, severity={anomaly.severity})"
                    )
                elif anomaly.score > 30:
                    self._log.info(
                        f"Anomaly detected in {component}: {anomaly.reason} "
                        f"(score={anomaly.score}, severity={anomaly.severity})"
                    )

            self._log.info("Anomaly detection completed successfully")

        except Exception as e:
            self._log.exception("Anomaly detection failed: %s", e)

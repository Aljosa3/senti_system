from __future__ import annotations

import logging
from typing import List, Dict, Any

from senti_os.ai.ai_command_processor import AICommand, AICommandPriority, AICommandSource


class AIMaintenancePlanner:
    """
    FAZA 6 – proaktivni AI planer, ki predlaga maintenance korake,
    še preden pride do degradacije (ne kot FAZA 5 Recovery Planner).

    Preverja:
        - memory usage
        - cpu load
        - task queue backlog
        - status servisov
    """

    def __init__(self, logger=None):
        self._log = logger or logging.getLogger(__name__)

    # ----------------------------------------------------------
    # Glavna metoda
    # ----------------------------------------------------------

    def plan_maintenance(self, snapshot) -> List[AICommand]:
        cmds: List[AICommand] = []

        # 1) Memory optimizacija
        if snapshot.memory_used_percent >= 80:
            cmds.append(
                AICommand(
                    action="cleanup_memory",
                    params={"mode": "safe"},
                    priority=AICommandPriority.HIGH,
                    source=AICommandSource.SYSTEM_INTERNAL,
                )
            )

        # 2) CPU protection
        if snapshot.cpu_load >= 85:
            cmds.append(
                AICommand(
                    action="throttle_module",
                    params={"reason": "high_cpu"},
                    priority=AICommandPriority.NORMAL,
                    source=AICommandSource.SYSTEM_INTERNAL,
                )
            )

        # 3) Task queue protection
        backlog = snapshot.task_engine_stats.get("pending", 0)
        if backlog >= 50:
            cmds.append(
                AICommand(
                    action="run_diagnostics",
                    params={"scope": "task_engine"},
                    priority=AICommandPriority.NORMAL,
                    source=AICommandSource.SYSTEM_INTERNAL,
                )
            )

        # 4) Service anomalies
        for svc, status in snapshot.service_status.items():
            if status in ("degraded", "warning"):
                cmds.append(
                    AICommand(
                        action="run_diagnostics",
                        params={"scope": "service", "service_name": svc},
                        priority=AICommandPriority.NORMAL,
                        source=AICommandSource.SYSTEM_INTERNAL,
                    )
                )

        return cmds

"""
Senti Core — Task Routing Engine (FAZA 8.4 Security Integration)
Location: senti_core/task_routing.py

Nadgradnje FAZA 8:
- integracija Security Managerja
- preverjanje capability zahtev
- preverjanje Data Integrity
- preprečevanje synthetic taskov
- aktivacija SECURITY_VIOLATION in SECURITY_HARD_BLOCK eventov
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import logging

from senti_os.security.security_manager_service import SecurityManagerService, SecurityHardBlock
from senti_os.security.security_policy import security_policy


class TaskRoutingError(Exception):
    """Critical dispatch error."""


class TaskRoutingEngine:
    """
    Task Routing Engine — FAZA 8 Security Enhanced
    """

    def __init__(
        self,
        orchestration_engine: Any,
        data_integrity_engine: Any,
        logger: Optional[logging.Logger] = None,
        subject: str = "ai_agent",
    ):
        """
        :param orchestration_engine:
            objekt, ki implementira:
                - submit_task(task_type, payload, priority, correlation_id, tags)

        :param data_integrity_engine:
            globalni FAZA 7 Data Integrity Engine

        :param subject:
            identiteta subjekta, ki oddaja taske (ai_agent, modul:xyz, os_service)
        """

        self._engine = orchestration_engine
        self._integrity = data_integrity_engine
        self._log = logger or logging.getLogger(__name__)

        # FAZA 8 — Security Manager
        self._security = SecurityManagerService(logger=self._log)

        # subjekt, ki oddaja taske
        self._subject = subject

        self._log.info(f"TaskRoutingEngine initialized for subject '{self._subject}'.")

    # ============================================================
    # PUBLIC API — centralni entrypoint za vse taske
    # ============================================================

    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: int,
        correlation_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Canonical entrypoint za oddajo taska s FAZA 8 varnostjo.
        """

        # 1) HARD BLOCK check
        if self._security.is_hard_blocked():
            raise TaskRoutingError("Task routing blocked by HARD BLOCK state.")

        # 2) RAZNI NEVELJAVNI VNOSI
        if not isinstance(task_type, str) or not task_type.strip():
            raise TaskRoutingError("Invalid or empty task_type.")

        # prepoved synthetic ali fake taskov
        if any(x in task_type.lower() for x in ["synthetic", "fake", "mock"]):
            raise TaskRoutingError("Synthetic task types are forbidden (FAZA 7/8).")

        if not isinstance(payload, dict):
            raise TaskRoutingError("Payload must be of type dict.")

        if not isinstance(priority, int) or priority < 1 or priority > 99:
            raise TaskRoutingError("Invalid priority — must be 1–99.")

        # 3) DATA INTEGRITY CHECK (FAZA 7)
        self._security.check_data_integrity({
            "type": "task",
            "origin": self._subject,
            "is_real": True,
            "notes": "Task routing integrity check"
        })

        # 4) SECURITY POLICY CHECK (FAZA 8)
        try:
            self._security.check_task_permission(
                subject=self._subject,
                task_type=task_type,
                payload=payload,
            )
        except SecurityHardBlock:
            # Security Manager already triggered the event
            raise TaskRoutingError("Hard Block activated due to security violation.")
        except PermissionError as exc:
            raise TaskRoutingError(str(exc)) from exc

        # 5) CANONICAL DISPATCH
        try:
            task_id = self._engine.submit_task(
                task_type=task_type,
                payload=dict(payload),
                priority=priority,
                correlation_id=correlation_id,
                tags=dict(tags or {}),
            )
            self._log.debug(f"Task routed → {task_id}")
            return task_id

        except Exception as exc:
            self._log.exception("Task dispatch failed: %s", exc)
            raise TaskRoutingError(str(exc)) from exc

    # ============================================================
    # FUTURE HOOKS (FAZA 8.5 / FAZA 9)
    # ============================================================

    def validate_task_security(self, task_type: str, payload: Dict[str, Any]):
        """
        Placeholder za prihodnjo razširitev (module-level sandboxing).
        """
        return None

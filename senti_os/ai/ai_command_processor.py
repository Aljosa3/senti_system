from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class AICommandPriority(Enum):
    """Prioriteta AI ukaza, uporabljeno za orkestracijo taskov."""

    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


class AICommandSource(Enum):
    """Izvor AI ukaza (za auditing, debug, varnost)."""

    USER_INTENT = auto()
    AI_CORE_PLANNING = auto()
    RECOVERY_PLANNER = auto()
    SYSTEM_INTERNAL = auto()


@dataclass
class AICommand:
    """
    Normalizirana reprezentacija AI ukaza, preden gre v TaskOrchestrationEngine.
    """

    action: str
    target: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    priority: AICommandPriority = AICommandPriority.NORMAL
    source: AICommandSource = AICommandSource.SYSTEM_INTERNAL
    correlation_id: Optional[str] = None
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class AICommandProcessor:
    """
    AI Command Processor
    ====================

    FAZA 7 DODATKI:
    - globalni AI_HARD_BLOCK state
    - blokada sprejemanja AI ukazov ob DATA_INTEGRITY_VIOLATION
    - zahteva realne podatke pred odblokiranjem
    - garantira, da AI ne generira ali ne izvaja synthetic/logical fallback ukazov
    """

    def __init__(
        self,
        task_engine: Any,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._task_engine = task_engine
        self._log = logger or logging.getLogger(__name__)

        # (FAZA 7) Hard block state
        self._hard_block_active: bool = False
        self._hard_block_reason: Optional[str] = None
        self._hard_block_details: Dict[str, Any] = {}

    # ============================================================
    # FAZA 7 — HARD BLOCK API
    # ============================================================

    def enter_hard_block_state(
        self,
        reason: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Aktivira totalno blokado AI procesiranja.
        To se zgodi, kadar sistem izgubi zaupanje v podatke.

        NI reboot, NI fallback, NI AI auto-correct.
        """

        self._hard_block_active = True
        self._hard_block_reason = reason
        self._hard_block_details = details

        self._log.critical(
            "AI Command Processor entered HARD BLOCK state: reason=%s details=%s",
            reason,
            details,
        )

        # Logiramo v Task Engine kot poseben "meta-event"
        try:
            self._task_engine.submit_task(
                task_type="system.hard_block_activated",
                payload={
                    "reason": reason,
                    "details": details,
                },
                priority=1,
                correlation_id=correlation_id,
                tags={"system_event": "DATA_INTEGRITY_VIOLATION"},
            )
        except Exception as exc:
            self._log.exception("Failed to log hard block activation: %s", exc)

    def exit_hard_block_state(self) -> None:
        """
        Odblokira AI, vendar samo v primeru, ko so zagotovljeni realni podatki.
        Kliče se iz Recovery sistema ali iz OS-level kontrol.
        """

        if not self._hard_block_active:
            return

        self._log.warning("AI Command Processor exiting HARD BLOCK state.")

        self._hard_block_active = False
        self._hard_block_reason = None
        self._hard_block_details = {}

    def is_blocked(self) -> bool:
        """Vračamo True, če sistem trenutno NE sme procesirati AI ukazov."""
        return self._hard_block_active

    # ============================================================
    # JAVNI API
    # ============================================================

    def process_user_intent(self, request: "UserRequest") -> None:
        """
        Minimalni fallback, ko AI core ne vrne eksplicitnega plana.
        """

        if self.is_blocked():
            self._reject_due_to_block("process_user_intent")
            return

        from .ai_os_agent import UserRequest

        if not isinstance(request, UserRequest):
            self._log.error("process_user_intent got invalid type: %r", type(request))
            return

        intent = request.intent.lower().strip()
        self._log.info("Processing user intent directly: %s", intent)

        if "diagnostic" in intent or "status" in intent:
            cmd = AICommand(
                action="run_diagnostics",
                target="system",
                params={"scope": "full"},
                priority=AICommandPriority.NORMAL,
                source=AICommandSource.USER_INTENT,
            )
        elif "restart" in intent and "service" in intent:
            cmd = AICommand(
                action="restart_service",
                target=request.metadata.get("service_name"),
                params={},
                priority=AICommandPriority.HIGH,
                source=AICommandSource.USER_INTENT,
            )
        else:
            cmd = AICommand(
                action="log_user_intent",
                target=None,
                params={"intent": request.intent, "metadata": request.metadata},
                priority=AICommandPriority.LOW,
                source=AICommandSource.USER_INTENT,
            )

        self.process_command(cmd)

    def process_raw_ai_command(
        self,
        raw_command: Dict[str, Any],
        origin: str,
        correlation_id: Optional[str] = None,
    ) -> None:

        if self.is_blocked():
            self._reject_due_to_block("process_raw_ai_command")
            return

        cmd = self._normalize_raw_command(
            raw_command=raw_command,
            origin=origin,
            correlation_id=correlation_id,
        )
        self.process_command(cmd)

    def process_recovery_action(
        self,
        action: "RecoveryAction",
        correlation_id: Optional[str] = None,
    ) -> None:

        if self.is_blocked():
            self._reject_due_to_block("process_recovery_action")
            return

        from .ai_recovery_planner import RecoveryAction

        if not isinstance(action, RecoveryAction):
            self._log.error("process_recovery_action got invalid type: %r", type(action))
            return

        cmd = AICommand(
            action=action.action,
            target=action.target,
            params=action.params,
            priority=self._map_recovery_severity_to_priority(action.severity),
            source=AICommandSource.RECOVERY_PLANNER,
            correlation_id=correlation_id or action.correlation_id,
        )
        self.process_command(cmd)

    def process_command(self, command: AICommand) -> None:
        """
        Osrednja metoda: prevzem AICommand in prevod v task.
        """

        if self.is_blocked():
            self._reject_due_to_block("process_command")
            return

        if not self._is_command_safe(command):
            self._log.warning("Rejected potentially unsafe AICommand: %s", command)
            return

        task_type = self._map_command_to_task_type(command)
        payload = self._map_command_to_task_payload(command)
        priority_value = self._priority_to_int(command.priority)

        self._log.info(
            "Submitting task from AICommand: task_type=%s cmd_id=%s",
            task_type,
            command.command_id,
        )

        try:
            self._task_engine.submit_task(
                task_type=task_type,
                payload=payload,
                priority=priority_value,
                correlation_id=command.correlation_id,
                tags={
                    "ai_source": command.source.name,
                    "ai_command_id": command.command_id,
                    "ai_action": command.action,
                },
            )
        except Exception as exc:
            self._log.exception("Task submission from AICommand failed: %s", exc)

    # ============================================================
    # INTERNI HELPERJI
    # ============================================================

    def _reject_due_to_block(self, call_origin: str) -> None:
        """
        Helper za blokado procesiranja ukazov, ko je sistem v HARD BLOCK stanju.
        """
        self._log.error(
            "AICommandProcessor BLOCKED (%s). REAL DATA REQUIRED before execution can continue.",
            call_origin,
        )

    def _normalize_raw_command(
        self,
        raw_command: Dict[str, Any],
        origin: str,
        correlation_id: Optional[str],
    ) -> AICommand:

        action = str(raw_command.get("action", "noop")).strip()
        target = raw_command.get("target")
        params = dict(raw_command.get("params", {}))

        priority_name = str(raw_command.get("priority", "NORMAL")).upper()
        priority = AICommandPriority.__members__.get(priority_name, AICommandPriority.NORMAL)

        if origin in {"ai_core_recovery", "ai_core_user_request"}:
            source = AICommandSource.AI_CORE_PLANNING
        else:
            source = AICommandSource.SYSTEM_INTERNAL

        return AICommand(
            action=action,
            target=target,
            params=params,
            priority=priority,
            source=source,
            correlation_id=correlation_id,
        )

    def _is_command_safe(self, command: AICommand) -> bool:
        """
        Minimalna varnostna logika, skladna s PROJECT_RULES.
        """

        dangerous_actions = {
            "delete_files",
            "format_disk",
            "shutdown_host",
            "erase_logs",
        }

        if command.action in dangerous_actions:
            return False

        return True

    @staticmethod
    def _map_command_to_task_type(command: AICommand) -> str:
        mapping = {
            "run_diagnostics": "system.run_diagnostics",
            "restart_service": "os.restart_service",
            "cleanup_memory": "os.memory_cleanup",
            "throttle_module": "os.throttle_module",
            "apply_config_patch": "config.apply_patch",
            "log_user_intent": "audit.log_user_intent",
        }
        return mapping.get(command.action, f"ai.{command.action}")

    @staticmethod
    def _map_command_to_task_payload(command: AICommand) -> Dict[str, Any]:
        payload = dict(command.params)
        if command.target is not None:
            payload.setdefault("target", command.target)
        return payload

    @staticmethod
    def _priority_to_int(priority: AICommandPriority) -> int:
        mapping = {
            AICommandPriority.LOW: 10,
            AICommandPriority.NORMAL: 5,
            AICommandPriority.HIGH: 2,
            AICommandPriority.CRITICAL: 1,
        }
        return mapping.get(priority, 5)

    @staticmethod
    def _map_recovery_severity_to_priority(severity: int) -> AICommandPriority:
        if severity <= 1:
            return AICommandPriority.LOW
        if severity == 2:
            return AICommandPriority.NORMAL
        if severity == 3:
            return AICommandPriority.HIGH
        return AICommandPriority.CRITICAL

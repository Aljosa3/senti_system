from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class SystemEventType(Enum):
    """High-level sistemski dogodki, ki jih vidi AI OS agent."""

    HEALTH_DEGRADED = auto()
    SERVICE_FAILURE = auto()
    WATCHDOG_ALERT = auto()
    RESOURCE_PRESSURE = auto()
    CONFIG_CHANGED = auto()
    USER_REQUEST = auto()
    RECOVERY_PLAN_APPLIED = auto()

    # (FAZA 7) Kritična kršitev podatkovne integritete
    DATA_INTEGRITY_VIOLATION = auto()


@dataclass
class SystemEvent:
    """
    Abstrakten dogodek na OS nivoju, ki ga vidi AI agent.

    OS Watchdog, DiagnosticsService, HealthMonitorDriver, KernelLoopService itd.
    lahko dvigujejo takšne dogodke, brez direktnega vezanja na AI implementacijo.
    """

    type: SystemEventType
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    severity: int = 0  # 0 = info, 1 = low, 2 = medium, 3 = high, 4 = critical
    correlation_id: Optional[str] = None


@dataclass
class UserRequest:
    """
    Uporabniška zahteva, preden se prevede v AICommand.

    To je lahko CLI ukaz, API klic, ali UI interakcija, ki jo hočeš dati v AI Operational Layer.
    """

    origin: str
    intent: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AICoreClient:
    """
    Minimalni vmesnik do AI jedra (senti_core).

    Dejanska implementacija se priklopi preko dependency injection,
    v skladu s SENTI_CORE_AI_RULES in PROJECT_RULES.
    """

    def plan_for_user_request(self, request: UserRequest) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def plan_for_recovery(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError


class SentiAIOSAgent:
    """
    Senti AI OS Agent
    =================

    OS-nivo AI agent, ki:
    - posluša sistemske dogodke (SystemEvent)
    - uporablja AICoreClient za planiranje
    - uporablja AICommandProcessor za prevod v task-e
    - uporablja AIRecoveryPlanner za načrtovanje okrevanja
    """

    def __init__(
        self,
        command_processor: "AICommandProcessor",
        recovery_planner: "AIRecoveryPlanner",
        ai_core_client: Optional[AICoreClient] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._command_processor = command_processor
        self._recovery_planner = recovery_planner
        self._ai_core_client = ai_core_client
        self._log = logger or logging.getLogger(__name__)

    # --------------------------------------------------------------------- #
    # JAVNI API
    # --------------------------------------------------------------------- #

    def handle_system_event(self, event: SystemEvent) -> None:
        """
        Vstopna točka za vse OS-nivo dogodke, ki so pomembni za AI.
        """

        self._log.debug("SentiAIOSAgent.handle_system_event: %s", event)

        # (FAZA 7) Kritična kršitev podatkovne integritete
        if event.type == SystemEventType.DATA_INTEGRITY_VIOLATION:
            self._handle_data_integrity_violation(event)
            return

        if event.type == SystemEventType.USER_REQUEST:
            self._handle_user_request_event(event)
            return

        if event.type in {
            SystemEventType.HEALTH_DEGRADED,
            SystemEventType.SERVICE_FAILURE,
            SystemEventType.WATCHDOG_ALERT,
            SystemEventType.RESOURCE_PRESSURE,
        }:
            self._handle_recovery_relevant_event(event)
            return

        self._log.debug("SystemEvent of type %s currently handled as no-op", event.type)

    def submit_user_request(self, request: UserRequest) -> None:
        event = SystemEvent(
            type=SystemEventType.USER_REQUEST,
            source=request.origin,
            payload={"intent": request.intent, "metadata": request.metadata},
            severity=0,
        )
        self.handle_system_event(event)

    # --------------------------------------------------------------------- #
    # INTERNI HANDLERJI
    # --------------------------------------------------------------------- #

    # (FAZA 7) Kritična blokada zaradi kršitve integritete podatkov
    def _handle_data_integrity_violation(self, event: SystemEvent) -> None:
        self._log.critical("DATA INTEGRITY VIOLATION detected by AI OS agent: %s", event)

        # 1. AI se NE sme opirati na napačne podatke
        # 2. NI AI popravljanja, nadomeščanja ali simuliranja
        # 3. Vse AI procesiranje se začasno ustavi

        # Obvesti command processor o hard-fail stanju
        try:
            self._command_processor.enter_hard_block_state(
                reason="DATA_INTEGRITY_VIOLATION",
                details=event.payload,
                correlation_id=event.correlation_id,
            )
        except Exception as exc:
            self._log.exception("Failed to signal hard block state: %s", exc)

        # Recovery Planner ne generira synthetic popravkov
        self._log.warning("AI Recovery Planner bypassed — integrity issue is non-recoverable without REAL data.")

        # Uporabnik ali sistem mora zagotoviti REALNE podatke
        self._log.error("REAL DATA REQUIRED before system can resume normal AI operations.")

    # --------------------------------------------------------------------- #

    def _handle_user_request_event(self, event: SystemEvent) -> None:
        intent = str(event.payload.get("intent", "")).strip()
        metadata = dict(event.payload.get("metadata", {}))

        user_req = UserRequest(
            origin=event.source,
            intent=intent,
            metadata=metadata,
        )
        self._log.info("Handling user request via AI OS agent: %s", user_req)

        raw_plans: List[Dict[str, Any]] = []

        if self._ai_core_client is not None:
            try:
                raw_plans = self._ai_core_client.plan_for_user_request(user_req)
            except Exception as exc:
                self._log.exception("AI core planning for user request failed: %s", exc)

        if not raw_plans:
            self._log.debug("AI core returned no explicit plan, delegating intent to command processor directly.")
            self._command_processor.process_user_intent(user_req)
            return

        for raw_cmd in raw_plans:
            self._command_processor.process_raw_ai_command(
                raw_command=raw_cmd,
                origin="ai_core_user_request",
                correlation_id=event.correlation_id,
            )

    # --------------------------------------------------------------------- #

    def _handle_recovery_relevant_event(self, event: SystemEvent) -> None:
        self._log.warning("Recovery-relevant event received: %s", event)

        from .ai_recovery_planner import HealthSnapshot

        snapshot = HealthSnapshot.from_event_payload(
            source=event.source,
            payload=event.payload,
            severity=event.severity,
            correlation_id=event.correlation_id,
        )

        recovery_actions = self._recovery_planner.plan_recovery(snapshot)

        if self._ai_core_client is not None:
            try:
                ai_raw_plan = self._ai_core_client.plan_for_recovery(snapshot.to_dict())
                for raw_cmd in ai_raw_plan:
                    self._command_processor.process_raw_ai_command(
                        raw_command=raw_cmd,
                        origin="ai_core_recovery",
                        correlation_id=event.correlation_id,
                    )
            except Exception as exc:
                self._log.exception("AI core recovery planning failed: %s", exc)

        for action in recovery_actions:
            self._command_processor.process_recovery_action(
                action=action,
                correlation_id=event.correlation_id,
            )

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HealthSnapshot:
    """
    Normaliziran "slik" stanja sistema, ki ga uporablja RecoveryPlanner.
    """

    source: str
    severity: int
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None

    @classmethod
    def from_event_payload(
        cls,
        source: str,
        payload: Dict[str, Any],
        severity: int,
        correlation_id: Optional[str],
    ) -> "HealthSnapshot":
        return cls(
            source=source,
            severity=severity,
            details=dict(payload or {}),
            correlation_id=correlation_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "severity": self.severity,
            "details": dict(self.details),
            "correlation_id": self.correlation_id,
        }


@dataclass
class RecoveryAction:
    """
    Posamezen korak recovery plana.
    """

    action: str
    target: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    severity: int = 0
    correlation_id: Optional[str] = None


class AIRecoveryPlanner:
    """
    AI Recovery Planner
    ===================

    FAZA 7 NADGRADNJA:
    - planner NE SME izvajati recovery brez realnih podatkov
    - planner NE SME generirati synthetic fallbacks
    - ob DATA_INTEGRITY_VIOLATION se aktivira NO-ACTION-MODE
    - recovery se nadaljuje šele po zagotovitvi realnih podatkov
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._log = logger or logging.getLogger(__name__)

        # (FAZA 7) Integriteta podatkov
        self._data_integrity_block: bool = False
        self._data_integrity_details: Dict[str, Any] = {}

    # ============================================================
    # FAZA 7 — BLOKADA RECOVERYJA
    # ============================================================

    def enter_integrity_block(self, details: Dict[str, Any]) -> None:
        """
        Aktivira blokado: brez realnih podatkov recovery NE SME delovati.
        """
        self._data_integrity_block = True
        self._data_integrity_details = details

        self._log.critical(
            "AIRecoveryPlanner BLOCKED due to DATA INTEGRITY VIOLATION: %s",
            details,
        )
        self._log.error(
            "REAL DATA REQUIRED – recovery actions are disabled until integrity is restored."
        )

    def exit_integrity_block(self) -> None:
        """
        Odblokira recovery, pod pogojem da so zagotovljeni realni podatki.
        """
        if not self._data_integrity_block:
            return

        self._data_integrity_block = False
        self._data_integrity_details = {}

        self._log.warning("AIRecoveryPlanner EXITING BLOCK – real data restored.")

    # ============================================================
    # GLAVNI RECOVERY ENTRYPOINT
    # ============================================================

    def plan_recovery(self, snapshot: HealthSnapshot) -> List[RecoveryAction]:
        """
        Osrednji entrypoint za AI OS Agent.
        """

        # (FAZA 7) Blokada – recovery se NE IZVAJA
        if self._data_integrity_block:
            self._log.error(
                "RecoveryPlanner is in NO-ACTION MODE due to DATA INTEGRITY VIOLATION. "
                "Snapshot ignored until REAL DATA is provided."
            )
            return []  # NI recovery akcij

        self._log.info("Planning recovery for snapshot: %s", snapshot)
        actions: List[RecoveryAction] = []

        src = snapshot.source.lower()

        # Primer: težave z RAM / memory
        if "memory" in src or snapshot.details.get("resource") == "memory":
            actions.extend(self._plan_memory_recovery(snapshot))

        # Primer: težave z določenim servisom
        if "service" in src or "service_name" in snapshot.details:
            actions.extend(self._plan_service_recovery(snapshot))

        # Splošni fallback
        if snapshot.severity >= 2 and not actions:
            actions.append(
                RecoveryAction(
                    action="run_diagnostics",
                    target="system",
                    params={"scope": "degraded_only"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )

        return actions

    # ============================================================
    # INTERNI RECOVERY NAČRTI
    # ============================================================

    def _plan_memory_recovery(self, snapshot: HealthSnapshot) -> List[RecoveryAction]:
        actions: List[RecoveryAction] = []

        usage = snapshot.details.get("usage_percent")
        hard_limit = snapshot.details.get("hard_limit_percent", 95)

        if usage is None:
            actions.append(
                RecoveryAction(
                    action="cleanup_memory",
                    target=None,
                    params={"mode": "safe"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )
            actions.append(
                RecoveryAction(
                    action="run_diagnostics",
                    target="memory",
                    params={"scope": "memory"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )
            return actions

        if usage >= hard_limit:
            actions.append(
                RecoveryAction(
                    action="cleanup_memory",
                    target=None,
                    params={"mode": "aggressive"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )
            actions.append(
                RecoveryAction(
                    action="throttle_module",
                    target=None,
                    params={"reason": "memory_pressure"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )
        elif usage >= 80:
            actions.append(
                RecoveryAction(
                    action="cleanup_memory",
                    target=None,
                    params={"mode": "safe"},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )

        return actions

    def _plan_service_recovery(self, snapshot: HealthSnapshot) -> List[RecoveryAction]:
        actions: List[RecoveryAction] = []

        service_name = snapshot.details.get("service_name")
        failure_type = snapshot.details.get("failure_type", "unknown")

        actions.append(
            RecoveryAction(
                action="run_diagnostics",
                target=service_name or "service",
                params={"scope": "service", "service_name": service_name},
                severity=snapshot.severity,
                correlation_id=snapshot.correlation_id,
            )
        )

        if failure_type in {"stopped", "unresponsive"} or snapshot.severity >= 2:
            actions.append(
                RecoveryAction(
                    action="restart_service",
                    target=service_name,
                    params={"reason": failure_type},
                    severity=snapshot.severity,
                    correlation_id=snapshot.correlation_id,
                )
            )

        return actions

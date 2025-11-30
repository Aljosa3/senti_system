"""
Security Events module
Location: senti_os/security/security_events.py

Namen:
- Centralizirana definicija OS-level varnostnih dogodkov
- Standardiziran API za poročanje Security Layer incidentov
- Integracija z EventBus / SentiAI OS Agentom
- Skladno z PROJECT_RULES in SENTI_CORE_AI_RULES

Ta modul NE dostopa do interneta, NE uporablja modelov,
in NE generira podatkov. Je popolnoma determinističen.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional

from senti_core.services.event_bus import EventBus
from senti_core.system.logger import SentiLogger


# -----------------------------------------------------------
# ENUM-LIKE CLASS: SECURITY EVENT TYPES
# -----------------------------------------------------------

class SecurityEventType:
    """Enum-like struktura za varnostne dogodke."""

    POLICY_VIOLATION = "security.policy_violation"
    DATA_INTEGRITY_VIOLATION = "security.data_integrity_violation"
    UNAUTHORIZED_ACCESS = "security.unauthorized_access"
    PRIVILEGE_ESCALATION = "security.privilege_escalation"
    SYSTEM_TAMPERING = "security.system_tampering"
    CONFIG_CHANGE = "security.config_change"
    SECURITY_MANAGER_ALERT = "security.manager_alert"


# -----------------------------------------------------------
# SECURITY EVENTS EMITTER
# -----------------------------------------------------------

class SecurityEvents:
    """
    Centraliziran izvor varnostnih dogodkov za Senti OS.

    - Vsak dogodek gre direktno v EventBus
    - Vsi payloadi imajo standardizirano obliko
    - AI OS Agent lahko na tej osnovi sproži Recovery ali Hard Block
    """

    def __init__(self):
        self.event_bus = EventBus()
        self.logger = SentiLogger()
        self.logger.log("info", "SecurityEvents initialized.")

    # =====================================================
    # PAYLOAD BUILDER
    # =====================================================

    def _payload(self, event_type: str, data: Dict[str, Any], severity: int):
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "severity": severity,  # 0–4, skladno z AI OS Agent logiko
            "data": data,
        }

    # =====================================================
    # GENERIC EMIT
    # =====================================================

    def emit(self, event_type: str, data: Dict[str, Any], severity: int = 1):
        payload = self._payload(event_type, data, severity)
        self.logger.log("warning", f"[SECURITY EVENT] {event_type}: {payload}")
        self.event_bus.publish(event_type, payload)

    # =====================================================
    # SPECIFIC SECURITY EVENTS
    # =====================================================

    def policy_violation(self, description: str, source: str):
        self.emit(
            SecurityEventType.POLICY_VIOLATION,
            {"description": description, "source": source},
            severity=3,
        )

    def data_integrity_violation(self, details: Dict[str, Any]):
        self.emit(
            SecurityEventType.DATA_INTEGRITY_VIOLATION,
            {
                "description": "Data Integrity Engine reported violation",
                "details": details,
            },
            severity=4,
        )

    def unauthorized_access(self, user: str, resource: str):
        self.emit(
            SecurityEventType.UNAUTHORIZED_ACCESS,
            {"user": user, "resource": resource},
            severity=3,
        )

    def privilege_escalation(self, process: str, attempted_level: str):
        self.emit(
            SecurityEventType.PRIVILEGE_ESCALATION,
            {"process": process, "attempted_level": attempted_level},
            severity=4,
        )

    def system_tampering(self, file: str, action: str):
        self.emit(
            SecurityEventType.SYSTEM_TAMPERING,
            {"file": file, "action": action},
            severity=4,
        )

    def config_change(self, changed_by: str, field: str, old: Any, new: Any):
        self.emit(
            SecurityEventType.CONFIG_CHANGE,
            {
                "changed_by": changed_by,
                "field": field,
                "old": old,
                "new": new,
            },
            severity=2,
        )

    def manager_alert(self, message: str):
        self.emit(
            SecurityEventType.SECURITY_MANAGER_ALERT,
            {"message": message},
            severity=2,
        )

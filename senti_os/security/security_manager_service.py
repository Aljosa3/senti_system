from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from senti_core_module.senti_core.system.logger import SentiLogger
from senti_os.security.security_events import SecurityEvents, SecurityEventType
from senti_os.security.security_policy import SecurityPolicy
from senti_os.security.data_integrity_engine import DataIntegrityViolation


class SecurityHardBlock(Exception):
    """
    Exception raised when a security hard block is triggered.
    This indicates a critical security violation that requires immediate action.
    """
    pass


class SecurityManagerService:
    """
    Security Manager Service
    ========================

    Osrednji nadzornik varnostnega sloja:
    - preverja skladnost s SecurityPolicy
    - sprejema opozorila iz sistema
    - pošilja SecurityEvents
    """

    def __init__(self, policy: SecurityPolicy, logger=None, events=None):
        self._policy = policy
        # Ensure we always use SentiLogger
        if logger is None:
            self._log = SentiLogger()
        elif isinstance(logger, SentiLogger):
            self._log = logger
        else:
            # Wrap standard Python logger
            self._log = SentiLogger()
        self._events = events or SecurityEvents()

        self._log.log("info", "SecurityManagerService initialized.")

    # =====================================================
    # MAIN ENTRYPOINT
    # =====================================================

    def process_incident(self, incident: Dict[str, Any]):
        """
        Incident je struktura:
            {
                "type": "...",
                "source": "...",
                "details": {...}
            }
        """

        inc_type = incident.get("type")
        source = incident.get("source", "unknown")
        details = incident.get("details", {})

        self._log.log("warning", f"[SECURITY] Incident received: {incident}")

        # 1) policy enforcement
        if not self._policy.is_allowed(incident):
            self._log.log("critical", "Policy violation detected.")
            self._events.policy_violation(
                source=source,
                description=f"Incident blocked by policy: {inc_type}",
            )
            return

        # 2) specific cases
        if inc_type == "data_integrity_violation":
            self._events.data_integrity_violation(details)

        elif inc_type == "unauthorized_access":
            self._events.unauthorized_access(
                user=details.get("user", "unknown"),
                resource=details.get("resource", "unknown"),
            )

        elif inc_type == "privilege_escalation":
            self._events.privilege_escalation(
                process=details.get("process", "unknown"),
                attempted_level=details.get("level", "unknown"),
            )

        elif inc_type == "system_tampering":
            self._events.system_tampering(
                file=details.get("file", "unknown"),
                action=details.get("action", "unknown"),
            )

        else:
            self._events.manager_alert(
                message=f"Unhandled security incident: {incident}"
            )

    # =====================================================
    # HOOK FOR DATA INTEGRITY ENGINE
    # =====================================================

    def handle_integrity_violation(self, details: Dict[str, Any]):
        self._events.data_integrity_violation(details)

    # =====================================================
    # SERVICE LIFECYCLE
    # =====================================================

    def start(self):
        self._log.log("info", "SecurityManagerService STARTED.")

    def stop(self):
        self._log.log("info", "SecurityManagerService STOPPED.")

    def status(self):
        return {"status": "running"}

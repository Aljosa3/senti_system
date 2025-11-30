"""
Senti OS Security Policy (FAZA 8.2)
Location: senti_os/security/security_policy.py

Ta modul vsebuje OS-level varnostno politiko:
- dovoljenja za AI / module / servise (permission model)
- mapping: task_type → required capabilities
- anti-escalation zaščite
- anti-override zaščite
- API za preverjanje, ali je neka operacija dovoljena

Integrira se v:
- Security Manager Service (FAZA 8.3)
- Task Routing Engine
- Task Orchestration Engine
- AI Command Processor
"""

from __future__ import annotations
from typing import Dict, List, Optional

from senti_os.security.security_capabilities import (
    Capability,
    CapabilitySet,
    capability_registry,
)


# ============================================================
# SECURITY POLICY CORE
# ============================================================

class SecurityPolicy:
    """
    Centralna OS-level varnostna politika.
    """

    def __init__(self):
        # mapping: subject (ai_agent, module:name, service:name)
        self._subject_capabilities: Dict[str, CapabilitySet] = {}

        # mapping: task_type → required capability
        self._task_requirements: Dict[str, Capability] = {}

        # ali je politika zaklenjena (AI ali moduli ne smejo spreminjati)
        self._locked = True

    # ============================================================
    # ACCESS CONTROL – SUBJECT CAPABILITIES
    # ============================================================

    def assign_capabilities(self, subject: str, capabilities: CapabilitySet):
        if self._locked:
            raise PermissionError("SecurityPolicy is locked — cannot modify capabilities.")
        self._subject_capabilities[subject] = capabilities

    def get_capabilities(self, subject: str) -> CapabilitySet:
        # če subjekt nima eksplicitnega profila, vrnemo prazen set
        return self._subject_capabilities.get(subject, CapabilitySet())

    def subject_has_capability(self, subject: str, capability: Capability) -> bool:
        return self.get_capabilities(subject).has(capability)

    # ============================================================
    # TASK TYPE REQUIREMENTS
    # ============================================================

    def require_capability_for_task(self, task_type: str, capability: Capability):
        if self._locked:
            raise PermissionError("SecurityPolicy is locked — cannot modify task requirements.")
        self._task_requirements[task_type] = capability

    def required_capability(self, task_type: str) -> Optional[Capability]:
        return self._task_requirements.get(task_type)

    # ============================================================
    # CHECKS (used by Security Manager, Task Router, Task Engine)
    # ============================================================

    def is_task_allowed(self, subject: str, task_type: str) -> bool:
        """
        Glavna metoda: preveri, ali subjekt lahko izvede task.
        """
        requirement = self.required_capability(task_type)

        # če task nima varnostne zahteve → dovoljen
        if requirement is None:
            return True

        # preverimo pravice
        return self.subject_has_capability(subject, requirement)

    # ============================================================
    # INTERNAL PROTECTION
    # ============================================================

    def lock(self):
        """Zaklene politiko – AI je NE SME odklepati."""
        self._locked = True

    def unlock_for_admin(self):
        """
        Samo fizični administrator (izven AI) sme odkleniti politiko.
        To NE sme biti poklicano iz AI/UI/API.
        """
        self._locked = False


# ============================================================
# DEFAULT POLICY INITIALIZATION
# ============================================================

def load_default_security_policy() -> SecurityPolicy:
    """
    Ustvarimo privzeto varnostno politiko.
    AI ali moduli je ne smejo spreminjati.
    Admin (ti osebno) lahko spremeni samo ročno.
    """

    policy = SecurityPolicy()

    # Odklenemo SAMO za inicializacijo
    policy.unlock_for_admin()

    # ============================================================
    # ASSIGN SUBJECT CAPABILITIES
    # ============================================================

    # AI agent
    policy.assign_capabilities("ai_agent", capability_registry.get("ai_agent_default"))

    # Vsi moduli imajo privzete modul pravice
    policy.assign_capabilities("module_default", capability_registry.get("module_default"))

    # OS servisi
    policy.assign_capabilities("os_service", capability_registry.get("service_default"))

    # ============================================================
    # TASK REQUIREMENTS (zahteve)
    # ============================================================

    # OS-level diagnostics
    policy.require_capability_for_task("system.run_diagnostics", Capability.RUN_DIAGNOSTICS)

    # Restart servisa – AI tega NE SME brez dovoljenja Security Managerja
    policy.require_capability_for_task("os.restart_service", Capability.RESTART_SERVICE)

    # Memory cleanup je dovoljen samo OS servisom
    policy.require_capability_for_task("os.memory_cleanup", Capability.OS_CRITICAL_OPS)

    # Urejanje konfiguracij — samo admin/OS servis
    policy.require_capability_for_task("config.apply_patch", Capability.MODIFY_CONFIG)

    # Modul-level operacije
    policy.require_capability_for_task("module.read", Capability.READ_MODULE_FILES)
    policy.require_capability_for_task("module.write", Capability.WRITE_MODULE_FILES)

    # Zaklenemo politiko za runtime
    policy.lock()

    return policy


# Globalna politika, naložena ob uvozu
security_policy = load_default_security_policy()

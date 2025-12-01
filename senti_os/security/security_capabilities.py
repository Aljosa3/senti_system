"""
Senti OS Security Capabilities (FAZA 8)
Location: senti_os/security/security_capabilities.py

Definicija:
- nizkopravni varnostni model Senti OS
- capability-based permission system
- omejitve za AI, module, servise in OS komponente

Capabilities so granularne pravice, ki definirajo:
- katere operacije so dovoljene
- kateri modul / AI / servis sme poklicati določen task
- ali akcija posega v kritični OS prostor
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List


# ============================================================
# CAPABILITY ENUM
# ============================================================

class Capability(Enum):
    """
    Granularna pravica za posamezno OS ali AI operacijo.
    """

    # OS-level operations
    READ_SYSTEM_STATUS = auto()
    RUN_DIAGNOSTICS = auto()
    RESTART_SERVICE = auto()
    STOP_SERVICE = auto()
    MODIFY_CONFIG = auto()

    # File access
    READ_MODULE_FILES = auto()
    WRITE_MODULE_FILES = auto()

    # Network access
    NETWORK_ACCESS_BASIC = auto()
    NETWORK_ACCESS_EXTENDED = auto()

    # AI internal rights
    AI_GENERATE_TASKS = auto()
    AI_ACCESS_CORE = auto()
    AI_HIGH_PRIVILEGE_OPS = auto()

    # Restricted ops (require strict whitelisting)
    OS_CRITICAL_OPS = auto()            # kernel, boot, watchdog
    SECURITY_POLICY_WRITE = auto()      # ability to change security policies
    MANAGE_PERMISSIONS = auto()         # modify capability sets


# ============================================================
# CAPABILITY SET
# ============================================================

@dataclass
class CapabilitySet:
    """
    Set pravic, ki pripadajo:
    - Senti AI agentu
    - posameznemu modulu
    - posameznemu OS servisu
    """

    allowed: List[Capability] = field(default_factory=list)

    def has(self, capability: Capability) -> bool:
        return capability in self.allowed

    def add(self, capability: Capability):
        if capability not in self.allowed:
            self.allowed.append(capability)

    def remove(self, capability: Capability):
        if capability in self.allowed:
            self.allowed.remove(capability)


# ============================================================
# DEFAULT CAPABILITY PROFILES
# ============================================================

# ----- AI OS Agent -----
AI_DEFAULT_CAPABILITIES = CapabilitySet(
    allowed=[
        Capability.READ_SYSTEM_STATUS,
        Capability.RUN_DIAGNOSTICS,
        Capability.AI_GENERATE_TASKS,
        Capability.AI_ACCESS_CORE,
    ]
)

# AI NE dobi kritičnih pravic:
# - RESTART_SERVICE (dovoljeno le prek Security Manager pregleda)
# - STOP_SERVICE
# - MODIFY_CONFIG
# - SECURITY_POLICY_WRITE
# - AI_HIGH_PRIVILEGE_OPS
# - OS_CRITICAL_OPS


# ----- Modules (default) -----
MODULE_DEFAULT_CAPABILITIES = CapabilitySet(
    allowed=[
        Capability.READ_MODULE_FILES,
        Capability.WRITE_MODULE_FILES,
        Capability.NETWORK_ACCESS_BASIC,
    ]
)

# ----- OS Services (default) -----
SERVICE_DEFAULT_CAPABILITIES = CapabilitySet(
    allowed=[
        Capability.RUN_DIAGNOSTICS,
        Capability.READ_SYSTEM_STATUS,
    ]
)


# ============================================================
# CAPABILITY REGISTRY
# ============================================================

class CapabilityRegistry:
    """
    Centralni register capability profilov.
    """

    def __init__(self):
        self._registry: Dict[str, CapabilitySet] = {}

    def register(self, name: str, capability_set: CapabilitySet):
        self._registry[name] = capability_set

    def get(self, name: str) -> CapabilitySet:
        return self._registry.get(name, CapabilitySet())

    def list_profiles(self):
        return list(self._registry.keys())


# Globalni singleton
capability_registry = CapabilityRegistry()

# Registriramo privzete profile
capability_registry.register("ai_agent_default", AI_DEFAULT_CAPABILITIES)
capability_registry.register("module_default", MODULE_DEFAULT_CAPABILITIES)
capability_registry.register("service_default", SERVICE_DEFAULT_CAPABILITIES)

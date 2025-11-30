from __future__ import annotations

"""
senti_os.ai
===========

AI Operational Layer za Senti OS.

Vloga:
- Ponuja SentiAIOSAgent kot OS-nivo AI agenta
- Ponuja AICommandProcessor za prevod AI ukazov v sistemske task-e
- Ponuja AIRecoveryPlanner za inteligentno okrevanje sistema

Integracija z:
- senti_core (EventBus, Task routing, AI Reasoning)
- OS Kernel + Service Layer (Diagnostics, Watchdog, MemoryCleanup, HealthMonitor)
"""

from .ai_os_agent import SentiAIOSAgent, SystemEvent, UserRequest
from .ai_command_processor import AICommandProcessor, AICommand
from .ai_recovery_planner import AIRecoveryPlanner, HealthSnapshot, RecoveryAction

__all__ = [
    "SentiAIOSAgent",
    "SystemEvent",
    "UserRequest",
    "AICommandProcessor",
    "AICommand",
    "AIRecoveryPlanner",
    "HealthSnapshot",
    "RecoveryAction",
]

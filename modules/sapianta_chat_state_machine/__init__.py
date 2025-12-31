"""
SAPIANTA CHAT STATE MACHINE - FAZA I
Status: LOCKED
Avtoriteta: Governance SAPIANTA_CHAT_CORE.md

This module implements the canonical state machine for Sapianta Chat.

FAZA I - Chat Logika (State Machine Skeleton)
This is the minimal, canonical implementation.

Components:
- state.py: State and response type definitions
- transitions.py: Transition rules and validation
- handlers.py: State handlers
- machine.py: Core state machine
- execution_stub.py: Stub execution (FAZA I only)

Usage:
    from modules.sapianta_chat_state_machine import ChatStateMachine

    machine = ChatStateMachine()
    response = machine.handle_input("user input")
"""

from .state import ChatState, ResponseType
from .transitions import TransitionRules, TransitionError
from .machine import ChatStateMachine
from .execution_stub import ExecutionStub

__all__ = [
    "ChatState",
    "ResponseType",
    "TransitionRules",
    "TransitionError",
    "ChatStateMachine",
    "ExecutionStub",
]

__version__ = "1.0.0-faza1"
__status__ = "LOCKED"

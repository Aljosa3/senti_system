"""
SAPIANTA CHAT - STATE DEFINITIONS
Status: LOCKED
Avtoriteta: Governance SAPIANTA_CHAT_CORE.md

This module defines the 11 canonical states of the Sapianta Chat state machine.
"""

from enum import Enum, auto


class ChatState(Enum):
    """
    Canonical states for Sapianta Chat.

    These states are defined in docs/governance/SAPIANTA_CHAT_CORE.md
    and must not be modified without updating the governance document.
    """

    # Initial state - system is waiting for user input
    IDLE = auto()

    # User has provided input, intent is being analyzed
    INTENT_RECEIVED = auto()

    # System is in advisory mode, presenting options
    ADVISORY = auto()

    # Waiting for explicit user decision
    USER_DECISION = auto()

    # Checking if decision complies with constraints
    ROUTING_CHECK = auto()

    # Drafting mandate based on user decision
    MANDATE_DRAFT = auto()

    # Waiting for explicit mandate confirmation
    MANDATE_CONFIRM = auto()

    # Executing mandate (passthrough state)
    EXECUTION = auto()

    # Presenting execution results
    RESULT = auto()

    # Requesting clarification from user
    CLARIFY = auto()

    # Refusing request due to hard violation
    REFUSE = auto()


class ResponseType(Enum):
    """
    Types of responses the chat can produce.

    Each response must have an explicit type to indicate its purpose.
    """

    # Advisory response with options
    ADVISORY = auto()

    # Request for clarification
    CLARIFY = auto()

    # Refusal of request
    REFUSE = auto()

    # Confirmation request
    CONFIRMATION = auto()

    # Result presentation
    RESULT = auto()

    # Acknowledgment
    ACKNOWLEDGMENT = auto()

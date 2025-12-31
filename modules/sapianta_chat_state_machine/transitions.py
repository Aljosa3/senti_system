"""
SAPIANTA CHAT - TRANSITION DEFINITIONS
Status: LOCKED
Avtoriteta: Governance SAPIANTA_CHAT_CORE.md

This module defines the allowed transitions between states.
NO transition is allowed unless explicitly defined here.

ABSOLUTE RULE: NO path to EXECUTION without MANDATE_CONFIRM.
"""

from typing import Dict, Set
from .state import ChatState


class TransitionRules:
    """
    Defines all allowed state transitions.

    Any transition not explicitly listed here is FORBIDDEN.
    """

    # Allowed transitions: from_state -> {to_state1, to_state2, ...}
    ALLOWED_TRANSITIONS: Dict[ChatState, Set[ChatState]] = {
        # IDLE can only transition to INTENT_RECEIVED on user input
        ChatState.IDLE: {
            ChatState.INTENT_RECEIVED,
        },

        # INTENT_RECEIVED can go to ADVISORY, CLARIFY, or REFUSE
        ChatState.INTENT_RECEIVED: {
            ChatState.ADVISORY,  # clear intent
            ChatState.CLARIFY,   # unclear intent
            ChatState.REFUSE,    # invalid intent
        },

        # ADVISORY presents options and waits for decision
        ChatState.ADVISORY: {
            ChatState.USER_DECISION,
        },

        # USER_DECISION can go back to ADVISORY, to ROUTING_CHECK, or to IDLE
        ChatState.USER_DECISION: {
            ChatState.ROUTING_CHECK,  # explicit choice made
            ChatState.ADVISORY,       # user asks for more info
            ChatState.IDLE,           # no decision (silence)
        },

        # ROUTING_CHECK validates decision against constraints
        ChatState.ROUTING_CHECK: {
            ChatState.MANDATE_DRAFT,  # compliant
            ChatState.CLARIFY,        # soft violation
            ChatState.REFUSE,         # hard violation
        },

        # MANDATE_DRAFT prepares the mandate
        ChatState.MANDATE_DRAFT: {
            ChatState.MANDATE_CONFIRM,
        },

        # MANDATE_CONFIRM is the ONLY state that can go to EXECUTION
        ChatState.MANDATE_CONFIRM: {
            ChatState.EXECUTION,  # confirmed
            ChatState.IDLE,       # rejected
            ChatState.ADVISORY,   # modify
        },

        # EXECUTION always goes to RESULT (passthrough)
        ChatState.EXECUTION: {
            ChatState.RESULT,
        },

        # RESULT always returns to IDLE
        ChatState.RESULT: {
            ChatState.IDLE,
        },

        # CLARIFY can go to ADVISORY or abort to IDLE
        ChatState.CLARIFY: {
            ChatState.ADVISORY,  # clarified
            ChatState.IDLE,      # abort
        },

        # REFUSE always returns to IDLE
        ChatState.REFUSE: {
            ChatState.IDLE,
        },
    }

    @classmethod
    def is_transition_allowed(cls, from_state: ChatState, to_state: ChatState) -> bool:
        """
        Check if a transition is allowed.

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            True if transition is allowed, False otherwise
        """
        allowed_targets = cls.ALLOWED_TRANSITIONS.get(from_state, set())
        return to_state in allowed_targets

    @classmethod
    def get_allowed_transitions(cls, from_state: ChatState) -> Set[ChatState]:
        """
        Get all allowed transitions from a given state.

        Args:
            from_state: Current state

        Returns:
            Set of allowed target states
        """
        return cls.ALLOWED_TRANSITIONS.get(from_state, set())

    @classmethod
    def validate_execution_path(cls, state: ChatState) -> None:
        """
        Validate that EXECUTION can only be reached from MANDATE_CONFIRM.

        This is the ABSOLUTE RULE of the system.

        Args:
            state: Current state

        Raises:
            RuntimeError: If attempting to enter EXECUTION from any state
                         other than MANDATE_CONFIRM
        """
        if state == ChatState.EXECUTION:
            # This method should be called BEFORE transition validation
            # The only way to reach EXECUTION is from MANDATE_CONFIRM
            raise RuntimeError(
                "ABSOLUTE RULE VIOLATION: "
                "EXECUTION can ONLY be reached from MANDATE_CONFIRM. "
                "This is a critical governance violation."
            )


class TransitionError(Exception):
    """
    Exception raised when an invalid state transition is attempted.
    """

    def __init__(self, from_state: ChatState, to_state: ChatState):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid transition: {from_state.name} -> {to_state.name}. "
            f"This transition is not allowed by governance rules."
        )

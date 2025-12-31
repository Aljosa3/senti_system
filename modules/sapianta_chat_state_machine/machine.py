"""
SAPIANTA CHAT - STATE MACHINE CORE
Status: LOCKED (FAZA I)
Avtoriteta: Governance SAPIANTA_CHAT_CORE.md

This is the core state machine implementation.
It orchestrates state transitions and enforces governance rules.

ABSOLUTE RULE: NO path to EXECUTION without MANDATE_CONFIRM.
"""

from typing import Dict, Any, Optional
from .state import ChatState, ResponseType
from .transitions import TransitionRules, TransitionError
from .handlers import StateHandlers


class ChatStateMachine:
    """
    Core state machine for Sapianta Chat.

    This class:
    - Maintains current state
    - Validates transitions
    - Orchestrates state handlers
    - Enforces governance rules
    """

    def __init__(self):
        """Initialize state machine in IDLE state."""
        self.current_state: ChatState = ChatState.IDLE
        self.context: Dict[str, Any] = {}
        self.handlers = StateHandlers()

    def get_current_state(self) -> ChatState:
        """
        Get current state.

        Returns:
            Current state
        """
        return self.current_state

    def transition_to(self, next_state: ChatState) -> None:
        """
        Transition to next state with validation.

        This method enforces transition rules.
        NO invalid transition is allowed.

        Args:
            next_state: Target state

        Raises:
            TransitionError: If transition is not allowed
        """
        # Validate transition
        if not TransitionRules.is_transition_allowed(self.current_state, next_state):
            raise TransitionError(self.current_state, next_state)

        # ABSOLUTE RULE: EXECUTION can only be reached from MANDATE_CONFIRM
        if next_state == ChatState.EXECUTION and self.current_state != ChatState.MANDATE_CONFIRM:
            raise RuntimeError(
                f"CRITICAL GOVERNANCE VIOLATION: "
                f"Attempted to enter EXECUTION from {self.current_state.name}. "
                f"EXECUTION can ONLY be reached from MANDATE_CONFIRM."
            )

        # Transition is valid
        self.current_state = next_state

    def handle_input(self, user_input: str) -> Dict[str, Any]:
        """
        Handle user input and advance state machine.

        This is the main entry point for interaction.

        Args:
            user_input: User's input string

        Returns:
            Structured response dict with state, type, message, and data
        """
        try:
            # Route to appropriate handler based on current state
            if self.current_state == ChatState.IDLE:
                next_state, response = self.handlers.handle_idle(user_input)

            elif self.current_state == ChatState.INTENT_RECEIVED:
                next_state, response = self.handlers.handle_intent_received(user_input, self.context)

            elif self.current_state == ChatState.ADVISORY:
                next_state, response = self.handlers.handle_advisory(self.context)

            elif self.current_state == ChatState.USER_DECISION:
                next_state, response = self.handlers.handle_user_decision(user_input, self.context)

            elif self.current_state == ChatState.ROUTING_CHECK:
                decision = self.context.get("decision", user_input)
                next_state, response = self.handlers.handle_routing_check(decision, self.context)

            elif self.current_state == ChatState.MANDATE_DRAFT:
                next_state, response = self.handlers.handle_mandate_draft(self.context)

            elif self.current_state == ChatState.MANDATE_CONFIRM:
                next_state, response = self.handlers.handle_mandate_confirm(user_input, self.context)

            elif self.current_state == ChatState.EXECUTION:
                next_state, response = self.handlers.handle_execution(self.context)

            elif self.current_state == ChatState.RESULT:
                next_state, response = self.handlers.handle_result(self.context)

            elif self.current_state == ChatState.CLARIFY:
                next_state, response = self.handlers.handle_clarify(user_input, self.context)

            elif self.current_state == ChatState.REFUSE:
                next_state, response = self.handlers.handle_refuse(user_input, self.context)

            else:
                # Fallback (should never happen)
                raise RuntimeError(f"Unknown state: {self.current_state}")

            # Update context with response data
            if "data" in response:
                self.context.update(response["data"])

            # Transition to next state
            self.transition_to(next_state)

            return response

        except TransitionError as e:
            # Invalid transition attempted
            return {
                "state": self.current_state,
                "type": ResponseType.REFUSE,
                "message": f"Invalid transition: {str(e)}",
                "data": {"error": str(e)}
            }

        except Exception as e:
            # Unexpected error
            return {
                "state": self.current_state,
                "type": ResponseType.REFUSE,
                "message": f"Error: {str(e)}",
                "data": {"error": str(e)}
            }

    def reset(self) -> None:
        """
        Reset state machine to IDLE with clean context.
        """
        self.current_state = ChatState.IDLE
        self.context = {}

    def get_context(self) -> Dict[str, Any]:
        """
        Get current context.

        Returns:
            Current context dictionary
        """
        return self.context.copy()

    def get_allowed_transitions(self) -> set:
        """
        Get allowed transitions from current state.

        Returns:
            Set of allowed target states
        """
        return TransitionRules.get_allowed_transitions(self.current_state)

    def can_transition_to(self, target_state: ChatState) -> bool:
        """
        Check if transition to target state is allowed.

        Args:
            target_state: Target state to check

        Returns:
            True if transition is allowed, False otherwise
        """
        return TransitionRules.is_transition_allowed(self.current_state, target_state)

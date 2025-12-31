"""
SAPIANTA CHAT - STATE HANDLERS
Status: LOCKED (FAZA I)
Avtoriteta: Governance SAPIANTA_CHAT_CORE.md

This module implements handlers for each state.
Handlers do NOT execute real logic in FAZA I.
They return the next state and structured response.
"""

from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
from .state import ChatState, ResponseType
from .execution_stub import ExecutionStub

# FAZA II: Import routing_check
from modules.sapianta_mandate_routing_check import routing_check


class StateHandlers:
    """
    Handlers for each state in the state machine.

    Each handler:
    - Takes current state and user input
    - Returns (next_state, response_dict)
    - Does NOT execute real logic
    """

    @staticmethod
    def handle_idle(user_input: str) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle IDLE state.

        IDLE waits for user input and transitions to INTENT_RECEIVED.

        Args:
            user_input: User's input

        Returns:
            (next_state, response)
        """
        if not user_input or user_input.strip() == "":
            # No input, stay in IDLE
            return ChatState.IDLE, {
                "state": ChatState.IDLE,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": "Waiting for input...",
            }

        # User provided input, move to INTENT_RECEIVED
        return ChatState.INTENT_RECEIVED, {
            "state": ChatState.INTENT_RECEIVED,
            "type": ResponseType.ACKNOWLEDGMENT,
            "message": "Input received, analyzing intent...",
            "data": {"user_input": user_input}
        }

    @staticmethod
    def handle_intent_received(user_input: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle INTENT_RECEIVED state.

        Analyzes user intent and routes to:
        - ADVISORY (clear intent)
        - CLARIFY (unclear intent)
        - REFUSE (invalid intent)

        Args:
            user_input: User's input
            context: Current context

        Returns:
            (next_state, response)
        """
        # STUB: Simple heuristics for intent analysis
        # Real intent analysis will be implemented later

        if "?" in user_input or "unclear" in user_input.lower():
            # Unclear intent
            return ChatState.CLARIFY, {
                "state": ChatState.CLARIFY,
                "type": ResponseType.CLARIFY,
                "message": "Your request is unclear. Please clarify.",
                "data": {"reason": "Unclear intent"}
            }

        if "forbidden" in user_input.lower() or "invalid" in user_input.lower():
            # Invalid intent
            return ChatState.REFUSE, {
                "state": ChatState.REFUSE,
                "type": ResponseType.REFUSE,
                "message": "This request cannot be fulfilled.",
                "data": {"reason": "Invalid intent"}
            }

        # Clear intent, proceed to advisory
        return ChatState.ADVISORY, {
            "state": ChatState.ADVISORY,
            "type": ResponseType.ADVISORY,
            "message": "Intent understood. Preparing options...",
            "data": {"intent": user_input}
        }

    @staticmethod
    def handle_advisory(context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle ADVISORY state.

        Presents options to user and marks optimal choice.
        Transitions to USER_DECISION.

        Args:
            context: Current context

        Returns:
            (next_state, response)
        """
        # STUB: Generate sample options
        # Real option generation will be implemented later

        options = [
            {"id": "A", "description": "Option A - Conservative approach", "optimal": False},
            {"id": "B", "description": "Option B - Balanced approach", "optimal": True},  # ⭐
            {"id": "C", "description": "Option C - Aggressive approach", "optimal": False},
        ]

        return ChatState.USER_DECISION, {
            "state": ChatState.USER_DECISION,
            "type": ResponseType.ADVISORY,
            "message": "Here are your options (⭐ marks recommended choice):",
            "data": {
                "options": options,
                "note": "This is a RECOMMENDATION, not a decision. You must explicitly choose."
            }
        }

    @staticmethod
    def handle_user_decision(user_input: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle USER_DECISION state.

        Waits for explicit user decision.
        Routes to:
        - ROUTING_CHECK (explicit choice)
        - ADVISORY (ask more)
        - IDLE (no decision/silence)

        Args:
            user_input: User's decision
            context: Current context

        Returns:
            (next_state, response)
        """
        if not user_input or user_input.strip() == "":
            # Silence = no decision
            return ChatState.IDLE, {
                "state": ChatState.IDLE,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": "No decision made. Returning to IDLE.",
                "data": {"reason": "Silence interpreted as no decision"}
            }

        if "more" in user_input.lower() or "info" in user_input.lower():
            # User asks for more information
            return ChatState.ADVISORY, {
                "state": ChatState.ADVISORY,
                "type": ResponseType.ADVISORY,
                "message": "Returning to advisory mode...",
            }

        # Explicit choice made
        return ChatState.ROUTING_CHECK, {
            "state": ChatState.ROUTING_CHECK,
            "type": ResponseType.ACKNOWLEDGMENT,
            "message": "Decision received. Checking constraints...",
            "data": {"decision": user_input}
        }

    @staticmethod
    def handle_routing_check(decision: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle ROUTING_CHECK state.

        Validates decision against constraints using FAZA II routing_check.
        Routes to:
        - MANDATE_DRAFT (compliant)
        - CLARIFY (soft violation)
        - REFUSE (hard violation)

        Args:
            decision: User's decision
            context: Current context

        Returns:
            (next_state, response)
        """
        # FAZA II: Create draft mandate for validation
        # If mandate already exists in context, use it; otherwise create minimal draft
        if "mandate" in context:
            mandate = context["mandate"]
        else:
            # Create minimal draft mandate from context for validation
            mandate = {
                "id": str(uuid.uuid4()),
                "intent": context.get("intent", "unknown"),
                "action": decision,
                "scope": {
                    "resource": context.get("resource", "GENERAL"),
                    "context": context.get("scope_context", "ADVISORY")
                },
                "constraints": {
                    "allowed": context.get("allowed", []),
                    "forbidden": context.get("forbidden", [])
                },
                "limits": {
                    "max_amount": context.get("max_amount"),
                    "max_count": context.get("max_count"),
                    "time_window": context.get("time_window")
                },
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                "confirmed": False,
                "revoked": False
            }

        # FAZA II: Call canonical routing_check
        result = routing_check(mandate)

        # Route based on routing_check result
        if result["status"] == "OK":
            # Compliant - proceed to MANDATE_DRAFT
            return ChatState.MANDATE_DRAFT, {
                "state": ChatState.MANDATE_DRAFT,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": f"Validation passed: {result['reason']}",
                "data": {"decision": decision, "mandate": mandate}
            }

        elif result["status"] == "CLARIFY":
            # Soft violation - request clarification
            return ChatState.CLARIFY, {
                "state": ChatState.CLARIFY,
                "type": ResponseType.CLARIFY,
                "message": f"Clarification needed: {result['reason']}",
                "data": {"reason": result["reason"]}
            }

        elif result["status"] == "REFUSE":
            # Hard violation - refuse
            return ChatState.REFUSE, {
                "state": ChatState.REFUSE,
                "type": ResponseType.REFUSE,
                "message": f"Request refused: {result['reason']}",
                "data": {"reason": result["reason"]}
            }

        else:
            # Unexpected result (should never happen)
            return ChatState.REFUSE, {
                "state": ChatState.REFUSE,
                "type": ResponseType.REFUSE,
                "message": f"Unexpected routing_check result: {result['status']}",
                "data": {"error": "Unexpected routing_check result"}
            }

    @staticmethod
    def handle_mandate_draft(context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle MANDATE_DRAFT state.

        Creates mandate based on user decision.
        Transitions to MANDATE_CONFIRM.

        Args:
            context: Current context

        Returns:
            (next_state, response)
        """
        # Create mandate structure
        mandate = {
            "intent": context.get("intent", "unknown"),
            "decision": context.get("decision", "unknown"),
            "constraints": context.get("constraints", []),
            "confirmed": False  # Not confirmed yet!
        }

        return ChatState.MANDATE_CONFIRM, {
            "state": ChatState.MANDATE_CONFIRM,
            "type": ResponseType.CONFIRMATION,
            "message": "Mandate drafted. EXPLICIT CONFIRMATION REQUIRED.",
            "data": {
                "mandate": mandate,
                "warning": "This mandate has NO EFFECT until explicitly confirmed."
            }
        }

    @staticmethod
    def handle_mandate_confirm(user_input: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle MANDATE_CONFIRM state.

        Waits for EXPLICIT confirmation.
        This is the ONLY state that can transition to EXECUTION.

        Routes to:
        - EXECUTION (confirmed)
        - IDLE (rejected)
        - ADVISORY (modify)

        Args:
            user_input: User's confirmation
            context: Current context

        Returns:
            (next_state, response)
        """
        if "confirm" in user_input.lower() or "yes" in user_input.lower():
            # EXPLICIT confirmation received
            mandate = context.get("mandate", {})
            mandate["confirmed"] = True

            return ChatState.EXECUTION, {
                "state": ChatState.EXECUTION,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": "Mandate CONFIRMED. Proceeding to execution...",
                "data": {"mandate": mandate}
            }

        if "reject" in user_input.lower() or "no" in user_input.lower():
            # Rejected
            return ChatState.IDLE, {
                "state": ChatState.IDLE,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": "Mandate rejected. Returning to IDLE.",
            }

        if "modify" in user_input.lower() or "change" in user_input.lower():
            # Modify request
            return ChatState.ADVISORY, {
                "state": ChatState.ADVISORY,
                "type": ResponseType.ADVISORY,
                "message": "Returning to advisory mode for modifications...",
            }

        # No clear confirmation
        return ChatState.MANDATE_CONFIRM, {
            "state": ChatState.MANDATE_CONFIRM,
            "type": ResponseType.CONFIRMATION,
            "message": "EXPLICIT CONFIRMATION REQUIRED. Please respond with 'confirm', 'reject', or 'modify'.",
        }

    @staticmethod
    def handle_execution(context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle EXECUTION state.

        This is a PASSTHROUGH state.
        Executes mandate (via stub) and always transitions to RESULT.

        Args:
            context: Current context with confirmed mandate

        Returns:
            (next_state, response)
        """
        mandate = context.get("mandate", {})

        # Execute via stub
        execution_result = ExecutionStub.execute(mandate)

        return ChatState.RESULT, {
            "state": ChatState.RESULT,
            "type": ResponseType.RESULT,
            "message": "Execution completed. Presenting results...",
            "data": {"result": execution_result}
        }

    @staticmethod
    def handle_result(context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle RESULT state.

        Presents execution results to user.
        Always transitions to IDLE.

        Args:
            context: Current context with results

        Returns:
            (next_state, response)
        """
        result = context.get("result", {})

        return ChatState.IDLE, {
            "state": ChatState.IDLE,
            "type": ResponseType.RESULT,
            "message": "Results presented. Returning to IDLE.",
            "data": {"result": result}
        }

    @staticmethod
    def handle_clarify(user_input: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle CLARIFY state.

        Requests clarification from user.
        Routes to:
        - ADVISORY (clarified)
        - IDLE (abort)

        Args:
            user_input: User's clarification
            context: Current context

        Returns:
            (next_state, response)
        """
        if "abort" in user_input.lower() or "cancel" in user_input.lower():
            # Abort
            return ChatState.IDLE, {
                "state": ChatState.IDLE,
                "type": ResponseType.ACKNOWLEDGMENT,
                "message": "Clarification aborted. Returning to IDLE.",
            }

        # Clarified, return to advisory
        return ChatState.ADVISORY, {
            "state": ChatState.ADVISORY,
            "type": ResponseType.ADVISORY,
            "message": "Clarification received. Returning to advisory mode...",
            "data": {"clarification": user_input}
        }

    @staticmethod
    def handle_refuse(user_input: str, context: Dict[str, Any]) -> Tuple[ChatState, Dict[str, Any]]:
        """
        Handle REFUSE state.

        Presents refusal reason.
        Always transitions to IDLE.

        Args:
            user_input: User acknowledgment
            context: Current context

        Returns:
            (next_state, response)
        """
        return ChatState.IDLE, {
            "state": ChatState.IDLE,
            "type": ResponseType.ACKNOWLEDGMENT,
            "message": "Refusal acknowledged. Returning to IDLE.",
        }

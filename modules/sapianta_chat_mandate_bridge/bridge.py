"""
Chat → Mandate Bridge — Phase V.1

Purpose:
- Connect chat input to mandate and intent systems
- Produce a unified, explainable interpretation
- Never allow execution

Authority: NONE
Execution: FORBIDDEN
"""

from modules.sapianta_chat_phase_i2.intent import detect_intent
from modules.sapianta_mandate_validator.validator import validate_mandate
from modules.sapianta_mandate_intent_binding.binder import bind_mandate_to_intent
from modules.sapianta_intent_response_policy.policy import get_advisory_policy


def process_chat_input(user_input: str) -> dict:
    """
    Process chat input through intent and mandate layers.

    Returns a read-only explanation object.
    """

    # Phase I.2 — intent detection
    intent_result = detect_intent(user_input)

    # Normalization safeguard (Phase V.1 responsibility)
    if isinstance(intent_result, str):
        intent_result = {"intent": intent_result}

    intent = intent_result.get("intent")

    # Phase II.2 — mandate validation
    mandate_result = validate_mandate(intent)
    mandate = mandate_result.get("mandate")

    # Phase II.3 — mandate → intent binding
    binding_result = bind_mandate_to_intent(mandate)

    # Phase II.4 — advisory response policy
    policy = get_advisory_policy(binding_result.get("intent"))

    return {
        "input": user_input,
        "intent_detection": intent_result,
        "mandate_validation": mandate_result,
        "mandate_intent_binding": binding_result,
        "advisory_policy": policy,
        "execution_allowed": False,
        "phase": "V.1",
    }

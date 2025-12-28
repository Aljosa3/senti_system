"""CoreChat Decision Loop - Canonical Implementation v1.0"""


def CORECHAT_DECISION_LOOP(input_data, state):
    """Main decision loop."""
    update_state(state, input_data)

    STOP_REASON = evaluate_stop_triggers(state)

    if STOP_REASON is not None:
        return CORECHAT_STOP(
            reason=STOP_REASON,
            required_info=missing_or_conflicting_elements(state)
        )

    NEXT_ACTION = decide_next_step(state)

    return CORECHAT_CONTINUE(
        approved_action=NEXT_ACTION
    )


def evaluate_stop_triggers(state):
    """Evaluate STOP triggers in mandatory order."""
    if missing_required_data(state):
        return "STOP_01_MISSING_DATA"

    if intent_is_ambiguous(state):
        return "STOP_02_INTENT_AMBIGUITY"

    if execution_detected_without_permission(state):
        return "STOP_03_EXECUTION_ATTEMPT"

    if high_risk_and_assumptions_required(state):
        return "STOP_04_RISK_WITH_ASSUMPTIONS"

    if constraints_conflict(state):
        return "STOP_05_CONTRADICTION"

    if decision_responsibility_shift_detected(state):
        return "STOP_06_RESPONSIBILITY_TRANSFER"

    if guessing_required(state):
        return "STOP_07_GUESSING_REQUIRED"

    return None


def decide_next_step(state):
    """Decide next step if STOP not triggered."""
    intent = state.get('intent')

    if intent == 'ANALYZE':
        return "ACTION_ANALYZE_ONLY"

    if intent == 'DESIGN':
        return "ACTION_PROPOSE_OPTIONS_ONLY"

    if intent == 'DECIDE':
        return "ACTION_RECOMMEND_WITHOUT_EXECUTION"

    if intent == 'EXECUTE':
        return "ACTION_REQUIRE_EXTERNAL_PERMISSION"

    return "ACTION_NO_OP"


def CORECHAT_STOP(reason, required_info):
    """Build STOP response."""
    return {
        "status": "STOP",
        "stop_reason": reason,
        "required_info": required_info,
        "allowed_actions": None
    }


def CORECHAT_CONTINUE(approved_action):
    """Build CONTINUE response."""
    return {
        "status": "CONTINUE",
        "approved_action": approved_action,
        "execution_allowed": False
    }


def update_state(state, input_data):
    """Update state with input."""
    pass


def missing_required_data(state):
    """Check if required data is missing."""
    confirmed_inputs = state.get('confirmed_inputs')
    if confirmed_inputs is None:
        return True
    if not confirmed_inputs:
        return True
    return False


def intent_is_ambiguous(state):
    """Check if intent is ambiguous."""
    intent = state.get('intent')
    valid_intents = ['ANALYZE', 'DESIGN', 'DECIDE', 'EXECUTE']
    return intent not in valid_intents


def execution_detected_without_permission(state):
    """Check if execution detected without permission."""
    risk_flags = state.get('risk_flags', [])
    if 'EXECUTION_WITHOUT_PERMISSION' in risk_flags:
        return True
    return False


def high_risk_and_assumptions_required(state):
    """Check if high risk and assumptions required."""
    risk_flags = state.get('risk_flags', [])
    if not risk_flags:
        return False

    high_risk_flags = ['FINANCIAL', 'LEGAL', 'REPUTATIONAL']
    has_high_risk = any(flag in risk_flags for flag in high_risk_flags)

    if has_high_risk and 'ASSUMPTIONS_REQUIRED' in risk_flags:
        return True

    return False


def constraints_conflict(state):
    """Check if constraints conflict."""
    risk_flags = state.get('risk_flags', [])
    if 'CONSTRAINT_CONFLICT' in risk_flags:
        return True
    return False


def decision_responsibility_shift_detected(state):
    """Check if decision responsibility shift detected."""
    risk_flags = state.get('risk_flags', [])
    if 'RESPONSIBILITY_SHIFT' in risk_flags:
        return True
    return False


def guessing_required(state):
    """Check if guessing required."""
    risk_flags = state.get('risk_flags', [])
    if 'GUESSING_REQUIRED' in risk_flags:
        return True
    return False


def missing_or_conflicting_elements(state):
    """Extract missing or conflicting elements."""
    elements = []

    if missing_required_data(state):
        elements.append("required_data")

    if intent_is_ambiguous(state):
        elements.append("intent")

    if execution_detected_without_permission(state):
        elements.append("execution_permission")

    if high_risk_and_assumptions_required(state):
        elements.append("risk_assumptions")

    if constraints_conflict(state):
        elements.append("constraints")

    if decision_responsibility_shift_detected(state):
        elements.append("responsibility")

    if guessing_required(state):
        elements.append("data")

    return elements

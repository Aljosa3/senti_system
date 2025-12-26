"""
Sapianta Chat Response Engine

Handles input processing and response generation.
Returns canonical response IDs only.
No execution, no decision-making, no intelligence.
"""


# ==================================================
# Canonical Response IDs (Phase 70)
# ==================================================

CR_GENERIC_ACK = "CR-01"
CR_ACTION_DETECTED = "CR-03"
CR_STATUS = "CR-05"
CR_DATA_REQUIRED = "CR-06"


# ==================================================
# Intent Detection
# ==================================================

ACTION_KEYWORDS = [
    "create",
    "run",
    "execute",
    "activate",
    "start",
    "launch",
    "deploy",
    "register",
    "modify",
    "update",
    "delete",
    "remove",
    "install",
    "configure",
]

DATA_RESULT_KEYWORDS = [
    "simulate",
    "simulation",
    "analyze",
    "analysis",
    "calculate",
    "calculation",
    "report",
    "estimate",
    "evaluation",
]


def detect_action_intent(user_input):
    input_lower = user_input.lower().strip()

    for keyword in ACTION_KEYWORDS:
        if input_lower.startswith(keyword + " ") or input_lower == keyword:
            return True

    return False


def detect_data_dependent_request(user_input):
    input_lower = user_input.lower()

    for keyword in DATA_RESULT_KEYWORDS:
        if keyword in input_lower:
            return True

    return False


# ==================================================
# Response Generation (ID only)
# ==================================================

def generate_response_id(user_input):
    if not user_input or not user_input.strip():
        return CR_GENERIC_ACK

    if detect_action_intent(user_input):
        return CR_ACTION_DETECTED

    if detect_data_dependent_request(user_input):
        return CR_DATA_REQUIRED

    return CR_GENERIC_ACK


def get_status_response_id():
    return CR_STATUS

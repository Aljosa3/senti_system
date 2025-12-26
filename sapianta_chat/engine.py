"""
Sapianta Chat Response Engine

Handles input processing and response generation.
No execution, no decision-making, no intelligence.
"""

from sapianta_chat.capabilities import is_capable


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


def detect_action_intent(user_input):
    """
    Detect if input appears to request an action.

    Args:
        user_input: Raw user input string

    Returns:
        Boolean indicating if input appears to be an action request
    """
    input_lower = user_input.lower().strip()

    for keyword in ACTION_KEYWORDS:
        if input_lower.startswith(keyword + " ") or input_lower == keyword:
            return True

    return False


def generate_response(user_input):
    """
    Generate a controlled response to user input.

    Args:
        user_input: Raw user input string

    Returns:
        Response string
    """
    if not user_input or not user_input.strip():
        return "Input received. No content detected."

    if detect_action_intent(user_input):
        return "Action detected. This capability is not implemented."

    return "Input acknowledged. This is a reflection message. No action will be taken."


def get_status_message():
    """
    Generate a status message showing current capabilities.

    Returns:
        Formatted status string
    """
    from sapianta_chat.capabilities import get_all_capabilities

    caps = get_all_capabilities()
    enabled_count = sum(1 for v in caps.values() if v)
    total_count = len(caps)

    return f"Capabilities: {enabled_count}/{total_count} enabled"

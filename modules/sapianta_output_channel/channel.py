"""
Output Channel — Phase V.3

Purpose:
- Deliver already-rendered advisory output to a defined channel
- Enforce read-only, non-executable delivery
- Preserve user sovereignty and governance boundaries

Authority: NONE
Execution: FORBIDDEN

This module performs NO interpretation and NO execution.
"""

def output_advisory(payload: dict, channel: str = "CLI") -> dict:
    """
    Output an advisory payload through a defined channel.

    Args:
        payload: Rendered advisory output from Phase V.2
        channel: Target output channel ("CLI" or "API")

    Returns:
        dict describing output delivery
    """

    if not isinstance(payload, dict):
        return {
            "delivered": False,
            "reason": "Invalid advisory payload",
            "execution_allowed": False,
            "phase": "V.3",
        }

    if payload.get("execution_allowed") is True:
        return {
            "delivered": False,
            "reason": "Execution flag must never be true",
            "execution_allowed": False,
            "phase": "V.3",
        }

    normalized_channel = channel.strip().upper()

    if normalized_channel == "CLI":
        return {
            "delivered": True,
            "channel": "CLI",
            "content": payload,
            "execution_allowed": False,
            "phase": "V.3",
        }

    if normalized_channel == "API":
        return {
            "delivered": True,
            "channel": "API",
            "content": payload,
            "execution_allowed": False,
            "phase": "V.3",
        }

    return {
        "delivered": False,
        "reason": "Unknown output channel",
        "execution_allowed": False,
        "phase": "V.3",
    }

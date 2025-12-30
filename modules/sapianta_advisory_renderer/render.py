"""
Advisory Output Renderer — Phase V.2

Purpose:
- Transform internal advisory data into a human-readable format
- Preserve explainability and transparency
- Never introduce execution, instructions, or decisions

Authority: NONE
Execution: FORBIDDEN

This module performs NO actions.
"""


def render_advisory_output(advisory_payload: dict) -> dict:
    """
    Render a human-facing advisory response from internal data.

    Args:
        advisory_payload: Structured output from advisory policy layer

    Returns:
        dict containing a formatted, human-readable advisory response
    """

    if not advisory_payload or not isinstance(advisory_payload, dict):
        return {
            "rendered": False,
            "message": "No advisory data available.",
            "execution_allowed": False,
        }

    intent = advisory_payload.get("intent", "UNKNOWN")
    policy = advisory_payload.get("policy", {})

    allowed = policy.get("allowed", "unspecified")
    forbidden = policy.get("forbidden", [])

    return {
        "rendered": True,
        "intent": intent,
        "advisory_mode": allowed,
        "constraints": {
            "forbidden": forbidden
        },
        "explanation": (
            f"The system identified intent '{intent}'. "
            f"Only '{allowed}' responses are permitted. "
            f"Execution and instruction remain blocked."
        ),
        "execution_allowed": False,
        "phase": "V.2",
    }

"""
Response framing for Phase I.3

Maps detected intent to a fixed advisory response.
No analysis. No execution. No side effects.
"""


def frame_response(intent: str) -> str:
    """
    Return an advisory response based solely on intent.

    Args:
        intent: One of QUESTION, REQUEST, PLAN, META, UNKNOWN

    Returns:
        Deterministic advisory response text.
    """

    if intent == "QUESTION":
        return (
            "This appears to be a question.\n\n"
            "I can provide an explanatory response, "
            "but no conclusions or actions will be taken.\n\n"
            "Advisory only."
        )

    if intent == "REQUEST":
        return (
            "This appears to be a request.\n\n"
            "I cannot perform actions or fulfill requests. "
            "I can only acknowledge or explain.\n\n"
            "Advisory only."
        )

    if intent == "PLAN":
        return (
            "This appears to be a planning-oriented input.\n\n"
            "I can describe considerations or structure, "
            "but not steps, instructions, or execution.\n\n"
            "Advisory only."
        )

    if intent == "META":
        return (
            "This appears to be a meta-level inquiry.\n\n"
            "I can describe my role and limitations, "
            "but not alter or extend them.\n\n"
            "Advisory only."
        )

    return (
        "The intent of this input is unclear.\n\n"
        "No assumptions will be made.\n\n"
        "Advisory only."
    )

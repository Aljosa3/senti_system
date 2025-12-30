print(">>> INTENT MODULE LOADED: sapianta_chat_phase_i2.intent <<<")

"""
Intent Detection — Phase I.2 (Heuristic Extension A.1)

Purpose:
- Apply minimal, deterministic heuristics to infer intent
- Improve usability of CLI chat
- Never allow execution or escalation

Authority: NONE
Execution: FORBIDDEN
"""

def detect_intent(user_input: str) -> dict:
    """
    Detect intent from user input using simple heuristics.

    Returns a read-only explanation object.
    """

    if not user_input or not user_input.strip():
        return {
            "intent": "UNKNOWN",
            "reason": "Empty input",
        }

    text = user_input.lower().strip()

    # -------------------------
    # META — system / architecture / phases
    # (checked early to avoid misclassification)
    # -------------------------
    if any(
        phrase in text
        for phrase in [
            "system",
            "sistem",
            "architecture",
            "governance",
            "pipeline",
            "phase",
            "faze",
            "phases",
            "how does the system",
            "how does this work",
        ]
    ):
        return {
            "intent": "META",
            "reason": "Detected system-level inquiry",
        }

    # -------------------------
    # QUESTION — explanatory / conceptual
    # -------------------------
    if any(
        phrase in text
        for phrase in [
            "explain",
            "why",
            "zakaj",
            "what is",
            "what are",
            "what does",
            "kaj",
            "kako",
            "how",
            "describe",
        ]
    ):
        return {
            "intent": "QUESTION",
            "reason": "Detected explanatory question",
        }

    # -------------------------
    # PLAN — procedural / structure
    # -------------------------
    if any(
        phrase in text
        for phrase in [
            "how to",
            "how do i",
            "steps",
            "plan",
            "phases",
            "procedure",
        ]
    ):
        return {
            "intent": "PLAN",
            "reason": "Detected procedural or planning language",
        }

    # -------------------------
    # REQUEST — action-oriented language
    # (execution still blocked later)
    # -------------------------
    if any(
        phrase in text
        for phrase in [
            "do ",
            "run",
            "zaženi",
            "execute",
            "start",
            "launch",
        ]
    ):
        return {
            "intent": "REQUEST",
            "reason": "Detected action-oriented language",
        }

    # -------------------------
    # FALLBACK
    # -------------------------
    return {
        "intent": "UNKNOWN",
        "reason": "No heuristic rule matched",
    }

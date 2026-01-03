"""
Declarative rejection models.

These objects represent explicit, non-executable reasons
why an input cannot proceed further in the meaning pipeline.

No execution.
No suggestion.
No recovery.
No control flow.
"""


class Rejection:
    """
    Base class for all declarative rejections.

    A rejection is a terminal semantic outcome.
    It explains *why* processing stopped, not *what to do next*.
    """

    kind = "rejection"

    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"reason='{self.reason}', detail='{self.detail}')"
        )


class NormativeRejection(Rejection):
    """
    Rejection caused by violation of explicit normative constraints.
    Example: action-oriented language, execution request, orchestration attempt.
    """

    kind = "normative"


class AmbiguityRejection(Rejection):
    """
    Rejection caused by unresolved ambiguity in the input.
    No clarification is requested; ambiguity is declared as terminal.
    """

    kind = "ambiguity"


class OutOfMandateRejection(Rejection):
    """
    Rejection caused by input being outside the declared mandate
    of Sapianta Chat, even if it is otherwise well-formed.
    """

    kind = "out_of_mandate"

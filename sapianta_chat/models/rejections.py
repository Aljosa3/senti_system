class Rejection:
    """
    Base class for all declarative rejections.
    No execution. No suggestion. No recovery.
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
    kind = "normative"


class AmbiguityRejection(Rejection):
    kind = "ambiguity"


class OutOfMandateRejection(Rejection):
    kind = "out_of_mandate"

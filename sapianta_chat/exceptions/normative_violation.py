class NormativeViolation(Exception):
    """
    Declarative representation of a normative boundary violation.
    No execution, no recovery, no suggestion.
    """

    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason)

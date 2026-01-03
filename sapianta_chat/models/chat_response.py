class ChatResponse:
    """
    Standardized, declarative response from Sapianta Chat.
    No execution. No suggestion. No side effects.
    """

    def __init__(self, status: str, intent=None, reason: str = "", detail: str = ""):
        self.status = status          # "ok" | "rejected"
        self.intent = intent          # Intent or None
        self.reason = reason          # short explanation
        self.detail = detail          # optional detail

    def __repr__(self):
        if self.status == "ok":
            return f"ChatResponse(status='ok', intent={self.intent})"
        return (
            "ChatResponse("
            f"status='rejected', reason='{self.reason}', detail='{self.detail}'"
            ")"
        )

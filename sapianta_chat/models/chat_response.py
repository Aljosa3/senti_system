from sapianta_chat.models.rejections import Rejection


class ChatResponse:
    """
    Standardized, declarative response from Sapianta Chat.
    """

    def __init__(self, status: str, intent=None, rejection: Rejection = None):
        self.status = status            # "ok" | "rejected"
        self.intent = intent            # Intent or None
        self.rejection = rejection      # Rejection or None

    def __repr__(self):
        if self.status == "ok":
            return f"ChatResponse(status='ok', intent={self.intent})"

        return (
            "ChatResponse("
            f"status='rejected', rejection={self.rejection})"
        )

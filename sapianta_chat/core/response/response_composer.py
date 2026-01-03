from sapianta_chat.models.chat_response import ChatResponse
from sapianta_chat.exceptions.normative_violation import NormativeViolation


class ResponseComposer:
    """
    Composes a standardized ChatResponse.
    Converts normative violations into declarative rejections.
    """

    def compose(self, result):
        if isinstance(result, NormativeViolation):
            return ChatResponse(
                status="rejected",
                reason=result.reason,
                detail=result.detail,
            )

        return ChatResponse(
            status="ok",
            intent=result,
        )

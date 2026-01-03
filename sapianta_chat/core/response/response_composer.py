from sapianta_chat.models.chat_response import ChatResponse
from sapianta_chat.models.rejections import NormativeRejection
from sapianta_chat.exceptions.normative_violation import NormativeViolation


class ResponseComposer:
    """
    Composes a standardized ChatResponse with typed rejections.
    """

    def compose(self, result):
        if isinstance(result, NormativeViolation):
            rejection = NormativeRejection(
                reason=result.reason,
                detail=result.detail,
            )
            return ChatResponse(
                status="rejected",
                rejection=rejection,
            )

        return ChatResponse(
            status="ok",
            intent=result,
        )

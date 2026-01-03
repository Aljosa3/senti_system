from sapianta_chat.exceptions.normative_violation import NormativeViolation


class ResponseComposer:
    """
    Composes a declarative, user-facing response.
    Catches normative violations and converts them into explanations.
    No execution, no suggestion, no recovery.
    """

    def compose(self, result):
        if isinstance(result, NormativeViolation):
            return {
                "status": "rejected",
                "reason": result.reason,
                "detail": result.detail,
            }

        return result

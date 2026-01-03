import re
from sapianta_chat.exceptions.normative_violation import NormativeViolation


class NormativeChecker:
    """
    Detects action-oriented language and enforces a normative refusal.
    No interpretation, no execution, no side effects.
    """

    ACTION_PATTERNS = [
        r"\brun\b",
        r"\bexecute\b",
        r"\bcreate\b",
        r"\bdelete\b",
        r"\binstall\b",
        r"\bdeploy\b",
        r"\bstart\b",
        r"\bstop\b",
        r"\bremove\b",
        r"\bupdate\b",
    ]

    def check(self, message):
        text = message.text.lower()

        for pattern in self.ACTION_PATTERNS:
            if re.search(pattern, text):
                raise NormativeViolation(
                    reason="Action-oriented language detected",
                    detail=f"Matched pattern: {pattern}"
                )

        return message

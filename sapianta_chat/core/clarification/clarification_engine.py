from sapianta_chat.core.clarification.ambiguity_detector import AmbiguityDetector

class ClarificationEngine:
    def __init__(self):
        self.detector = AmbiguityDetector()

    def clarify(self, message):
        ambiguity = self.detector.detect(message)
        if ambiguity:
            return ambiguity
        return message

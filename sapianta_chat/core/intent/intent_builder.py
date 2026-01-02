from sapianta_chat.models.intent import Intent

class IntentBuilder:
    def build(self, message):
        return Intent(description=message.text)

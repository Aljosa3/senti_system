from sapianta_chat.models.messages import UserMessage
from sapianta_chat.models.rejections import Rejection
from sapianta_chat.models.chat_response import ChatResponse

from sapianta_chat.core.input.input_handler import InputHandler
from sapianta_chat.core.interpretation.intent_interpreter import IntentInterpreter
from sapianta_chat.core.clarification.clarification_engine import ClarificationEngine
from sapianta_chat.core.normative.normative_checker import NormativeChecker
from sapianta_chat.core.normalization.semantic_normalizer import SemanticNormalizer
from sapianta_chat.core.intent.intent_builder import IntentBuilder
from sapianta_chat.core.response.response_composer import ResponseComposer
from sapianta_chat.boundaries.output_boundary import OutputBoundary


class ChatPipeline:
    """
    Minimal linear pipeline.
    No execution. No intelligence. No side effects.
    """

    def __init__(self):
        self.input_handler = InputHandler()
        self.intent_interpreter = IntentInterpreter()
        self.clarification_engine = ClarificationEngine()
        self.normative_checker = NormativeChecker()
        self.semantic_normalizer = SemanticNormalizer()
        self.intent_builder = IntentBuilder()
        self.response_composer = ResponseComposer()
        self.output_boundary = OutputBoundary()

    def process(self, text: str):
        message = UserMessage(text)

        message = self.input_handler.handle(message)
        if isinstance(message, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=message))

        message = self.intent_interpreter.interpret(message)
        if isinstance(message, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=message))

        message = self.clarification_engine.clarify(message)
        if isinstance(message, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=message))

        message = self.normative_checker.check(message)
        if isinstance(message, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=message))

        message = self.semantic_normalizer.normalize(message)
        if isinstance(message, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=message))

        result = self.intent_builder.build(message)
        if isinstance(result, Rejection):
            return self.output_boundary.close(ChatResponse(status="rejected", rejection=result))

        response = self.response_composer.compose(result)
        return self.output_boundary.close(response)

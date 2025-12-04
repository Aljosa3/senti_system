"""
FAZA 26 - Intelligent Action Layer
Intent Parser

Rule-based + LLM-ready parser for user commands.
Detects intents and parameters from natural language input.
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class IntentParser:
    """
    Parses user commands into structured intent representations.

    Supports:
    - Simple command detection (compute, analyze, generate, etc.)
    - Parameter extraction (numbers, filenames, flags)
    - Intent validation
    """

    # Intent patterns: (pattern, intent_name)
    INTENT_PATTERNS = [
        # Sentiment analysis
        (r'analyze\s+sentiment', 'analyze_sentiment'),
        (r'sentiment\s+analysis', 'analyze_sentiment'),
        (r'sentiment', 'analyze_sentiment'),

        # Computation
        (r'compute\s+(\w+)', 'compute'),
        (r'calculate\s+(\w+)', 'compute'),

        # Plot generation
        (r'generate\s+plot', 'generate_plot'),
        (r'create\s+plot', 'generate_plot'),
        (r'plot\s+(\w+)', 'generate_plot'),

        # Data processing
        (r'process\s+data', 'process_data'),
        (r'transform\s+data', 'process_data'),

        # Model inference
        (r'run\s+model', 'run_model'),
        (r'infer\s+(\w+)', 'run_model'),
        (r'predict\s+(\w+)', 'run_model'),

        # Pipeline execution
        (r'run\s+pipeline', 'run_pipeline'),
        (r'execute\s+pipeline', 'run_pipeline'),
    ]

    # Parameter patterns
    PARAM_PATTERNS = {
        'count': r'count[=:\s]+(\d+)',
        'limit': r'limit[=:\s]+(\d+)',
        'dataset': r'dataset[=:\s]+(\w+)',
        'model': r'model[=:\s]+([\w\-]+)',
        'file': r'file[=:\s]+([\w\./\-]+)',
        'output': r'output[=:\s]+([\w\./\-]+)',
        'format': r'format[=:\s]+(\w+)',
    }

    # Boolean flags
    FLAG_PATTERNS = {
        'generate_plot': [r'with\s+plot', r'plot', r'visualize'],
        'verbose': [r'verbose', r'--verbose', r'-v'],
        'debug': [r'debug', r'--debug'],
        'save': [r'save', r'--save'],
    }

    def __init__(self):
        """Initialize the intent parser."""
        logger.info("IntentParser initialized")

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse user command into structured intent.

        Args:
            text: User command string

        Returns:
            Dictionary with intent and parameters:
            {
                "intent": "analyze_sentiment",
                "parameters": {
                    "count": 200,
                    "dataset": "articles",
                    "generate_plot": true
                },
                "raw_text": "original command"
            }

        Raises:
            ValueError: If command is empty or intent cannot be determined
        """
        if not text or not text.strip():
            raise ValueError("Command cannot be empty")

        text_lower = text.lower().strip()

        # Detect intent
        intent = self._detect_intent(text_lower)
        if not intent:
            raise ValueError(f"Could not determine intent from command: {text}")

        # Extract parameters
        parameters = self._extract_parameters(text_lower)

        # Extract flags
        flags = self._extract_flags(text_lower)
        parameters.update(flags)

        result = {
            "intent": intent,
            "parameters": parameters,
            "raw_text": text
        }

        # Validate parsed intent
        self.validate(result)

        logger.info(f"Parsed intent: {intent} with {len(parameters)} parameters")
        return result

    def _detect_intent(self, text: str) -> Optional[str]:
        """
        Detect intent from text using pattern matching.

        Args:
            text: Lowercased command text

        Returns:
            Intent name or None if not detected
        """
        for pattern, intent_name in self.INTENT_PATTERNS:
            if re.search(pattern, text):
                return intent_name

        return None

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract parameters from text.

        Args:
            text: Lowercased command text

        Returns:
            Dictionary of parameters
        """
        parameters = {}

        for param_name, pattern in self.PARAM_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)

                # Convert numeric values
                if param_name in ['count', 'limit']:
                    parameters[param_name] = int(value)
                else:
                    parameters[param_name] = value

        return parameters

    def _extract_flags(self, text: str) -> Dict[str, bool]:
        """
        Extract boolean flags from text.

        Args:
            text: Lowercased command text

        Returns:
            Dictionary of boolean flags
        """
        flags = {}

        for flag_name, patterns in self.FLAG_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    flags[flag_name] = True
                    break

        return flags

    def validate(self, parsed_intent: Dict[str, Any]) -> None:
        """
        Validate parsed intent structure.

        Args:
            parsed_intent: Parsed intent dictionary

        Raises:
            ValueError: If structure is invalid
        """
        if not isinstance(parsed_intent, dict):
            raise ValueError("Parsed intent must be a dictionary")

        if "intent" not in parsed_intent:
            raise ValueError("Parsed intent must contain 'intent' field")

        if not parsed_intent["intent"]:
            raise ValueError("Intent cannot be empty")

        if "parameters" not in parsed_intent:
            raise ValueError("Parsed intent must contain 'parameters' field")

        if not isinstance(parsed_intent["parameters"], dict):
            raise ValueError("Parameters must be a dictionary")

        # Validate parameter types
        params = parsed_intent["parameters"]
        for key, value in params.items():
            if key in ['count', 'limit'] and not isinstance(value, int):
                raise ValueError(f"Parameter '{key}' must be an integer")

            if key in ['generate_plot', 'verbose', 'debug', 'save']:
                if not isinstance(value, bool):
                    raise ValueError(f"Flag '{key}' must be a boolean")

    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intents.

        Returns:
            List of intent names
        """
        intents = set()
        for _, intent_name in self.INTENT_PATTERNS:
            intents.add(intent_name)
        return sorted(list(intents))


def create_intent_parser() -> IntentParser:
    """
    Factory function to create an IntentParser instance.

    Returns:
        IntentParser instance
    """
    return IntentParser()

"""
Senti Core Validator Utility
Location: senti_core/utils/validator.py

Provides basic validation utilities for runtime operations.
"""


class Validator:
    """
    Core validation utility class.
    """

    @staticmethod
    def validate_runtime_output(output: dict) -> bool:
        """
        Validates runtime output structure.

        Args:
            output: Dictionary to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(output, dict):
            raise ValueError("Output must be a dictionary")

        return True

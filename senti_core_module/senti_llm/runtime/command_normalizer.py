"""
FAZA 46 — Command Normalizer
FILE 4/8: command_normalizer.py

Command Normalizer connects name + path + action into unified, canonical runtime command.

Purpose:
- Accept unstructured command (dict)
- Validate:
  - Canonical system name
  - Allowed name (guard)
  - Valid path (FSPR)
- Return normalized command
- No execution
- No error correction
- No inference
- Only: validation + repackaging

Rules:
- No I/O
- No print/log
- No fallback logic
- No heuristics
- No input dict mutation
- No try/except (except where explicitly allowed)
- Deterministic execution
- Absolute imports
"""

from senti_core_module.senti_llm.runtime.canonical_name import resolve_name
from senti_core_module.senti_llm.runtime.name_resolution_guard import NameResolutionGuard
from senti_core_module.senti_llm.runtime.file_system_protection import validate_path


# =====================================================================
# Exceptions
# =====================================================================

class CommandNormalizationError(Exception):
    """Base exception for command normalization errors."""


class InvalidCommandError(CommandNormalizationError):
    """Raised when command structure is invalid."""


class UnsafeCommandError(CommandNormalizationError):
    """Raised when command violates security rules."""


# =====================================================================
# Command Normalizer
# =====================================================================

class CommandNormalizer:
    """Normalizer for runtime commands."""

    def __init__(self, name_guard: NameResolutionGuard):
        """
        Initialize command normalizer.

        Args:
            name_guard (NameResolutionGuard): Name resolution guard instance.
        """
        self.name_guard = name_guard

    def normalize(self, command: dict) -> dict:
        """
        Normalize command into canonical format.

        Args:
            command (dict): Raw command to normalize.

        Returns:
            dict: Normalized command with fields:
                - target: Canonical system name
                - action: Action string
                - path: Optional path string
                - payload: Optional payload dict

        Raises:
            InvalidCommandError: If command structure is invalid.
            UnsafeCommandError: If command violates security rules.
        """
        if not isinstance(command, dict):
            raise InvalidCommandError(f"Command must be dict, got: {type(command)}")

        normalized = {}

        # Validate and normalize target
        if "target" not in command:
            raise InvalidCommandError("Command missing required field: target")

        target = command["target"]
        resolved_target = resolve_name(target)
        canonical_target = self.name_guard.require_canonical(resolved_target)
        normalized["target"] = canonical_target

        # Validate and normalize action
        if "action" not in command:
            raise InvalidCommandError("Command missing required field: action")

        action = command["action"]
        if not isinstance(action, str):
            raise InvalidCommandError(f"Action must be str, got: {type(action)}")

        normalized["action"] = action

        # Validate and normalize path (optional)
        if "path" in command:
            path = command["path"]
            validate_path(path)
            normalized["path"] = path

        # Validate and normalize payload (optional)
        if "payload" in command:
            payload = command["payload"]
            if not isinstance(payload, dict):
                raise InvalidCommandError(f"Payload must be dict, got: {type(payload)}")
            normalized["payload"] = payload

        return normalized

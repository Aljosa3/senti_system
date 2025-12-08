"""
FAZA 30.95 - LLM Configuration Layer
Multi-LLM Router with Safety Integration

This module provides a unified interface for multiple LLM providers
with routing, fallback, and safety features.

SECURITY: All API calls are MOCKED for sandbox safety.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class SafetyValidator:
    """FAZA 16 Safety Protocol Integration"""

    def __init__(self, forbidden_patterns: List[str]):
        self.forbidden_patterns = forbidden_patterns

    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Validate prompt against forbidden patterns"""
        for pattern in self.forbidden_patterns:
            if pattern in prompt:
                return False, f"FORBIDDEN_PATTERN_DETECTED: {pattern}"
        return True, "OK"

    def sanitize_output(self, output: str, max_length: int = 100000) -> str:
        """Sanitize LLM output"""
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)

        # Remove control characters
        output = ''.join(char for char in output if ord(char) >= 32 or char in '\n\r\t')

        # Enforce length limit
        if len(output) > max_length:
            output = output[:max_length] + "\n[OUTPUT_TRUNCATED]"

        return output


class OpenAIClient:
    """OpenAI API Client (MOCKED)"""

    def __init__(self):
        self.provider = "openai"

    def generate(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate response using OpenAI model (MOCKED)"""
        # MOCKED IMPLEMENTATION - NO ACTUAL API CALL
        response = f"MOCK_RESPONSE_OPENAI_{model.upper().replace('-', '_')}: {prompt}"
        return response


class AnthropicClient:
    """Anthropic API Client (MOCKED)"""

    def __init__(self):
        self.provider = "anthropic"

    def generate(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate response using Anthropic model (MOCKED)"""
        # MOCKED IMPLEMENTATION - NO ACTUAL API CALL
        response = f"MOCK_RESPONSE_ANTHROPIC_{model.upper().replace('-', '_')}: {prompt}"
        return response


class MistralClient:
    """Mistral API Client (MOCKED)"""

    def __init__(self):
        self.provider = "mistral"

    def generate(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate response using Mistral model (MOCKED)"""
        # MOCKED IMPLEMENTATION - NO ACTUAL API CALL
        response = f"MOCK_RESPONSE_MISTRAL_{model.upper().replace('-', '_')}: {prompt}"
        return response


class LLMClient:
    """
    Multi-LLM Router with Fallback and Safety

    Features:
    - Multi-provider routing
    - Automatic fallback on failure
    - FAZA 16 safety integration
    - Output sanitization
    - Deterministic behavior
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize LLM Client with configuration"""
        if config_path is None:
            # Default config path
            base_path = Path(__file__).parent
            config_path = base_path / "llm_config.json"

        self.config = self._load_config(config_path)
        self.safety_validator = SafetyValidator(
            self.config["safety"]["forbidden_patterns"]
        )

        # Initialize provider clients
        self.clients = {
            "openai": OpenAIClient(),
            "anthropic": AnthropicClient(),
            "mistral": MistralClient()
        }

        self.retry_count = 0
        self.max_retries = self.config["fallback_chain"]["max_retries"]

    def _load_config(self, config_path) -> Dict:
        """Load configuration from JSON file"""
        # MOCK: Return embedded config for sandbox safety
        # In production, this would actually read the file
        mock_config = {
            "version": "30.95",
            "models": {
                "gpt-4.1": {
                    "provider": "openai",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "priority": 1,
                    "capabilities": ["reasoning", "coding", "general"],
                    "enabled": True
                },
                "claude-sonnet-3.7": {
                    "provider": "anthropic",
                    "temperature": 0.6,
                    "max_tokens": 8192,
                    "priority": 2,
                    "capabilities": ["reasoning", "coding", "general"],
                    "enabled": True
                },
                "mixtral-8x22b": {
                    "provider": "mistral",
                    "temperature": 0.5,
                    "max_tokens": 32768,
                    "priority": 3,
                    "capabilities": ["reasoning", "fallback"],
                    "enabled": True
                }
            },
            "routing_policy": {
                "reasoning": ["gpt-4.1", "claude-sonnet-3.7", "mixtral-8x22b"],
                "coding": ["claude-sonnet-3.7", "gpt-4.1", "mixtral-8x22b"],
                "fallback": ["mixtral-8x22b", "claude-sonnet-3.7", "gpt-4.1"],
                "general": ["gpt-4.1", "claude-sonnet-3.7", "mixtral-8x22b"]
            },
            "fallback_chain": {
                "enabled": True,
                "max_retries": 3,
                "retry_delay_seconds": 1,
                "cascade_on_error": True
            },
            "safety": {
                "faza_16_integration": True,
                "forbidden_patterns": [
                    "os.system",
                    "subprocess",
                    "eval(",
                    "exec(",
                    "__import__",
                    "compile(",
                    "open(",
                    "file(",
                    "input(",
                    "raw_input("
                ],
                "sanitization": {
                    "strip_ansi": True,
                    "remove_control_chars": True,
                    "max_output_length": 100000
                }
            },
            "determinism": {
                "seed": 42,
                "enforce_reproducibility": True,
                "cache_responses": False
            }
        }
        return mock_config

    def _select_model(self, modulation: str) -> Optional[str]:
        """Select model based on routing policy"""
        if modulation not in self.config["routing_policy"]:
            modulation = "general"

        model_priority = self.config["routing_policy"][modulation]

        # Return first enabled model in priority order
        for model_name in model_priority:
            if model_name in self.config["models"]:
                if self.config["models"][model_name].get("enabled", True):
                    return model_name

        return None

    def _get_fallback_models(self, current_model: str, modulation: str) -> List[str]:
        """Get fallback models for cascade retry"""
        if not self.config["fallback_chain"]["cascade_on_error"]:
            return []

        all_models = self.config["routing_policy"].get(modulation, [])

        # Return models after current model in priority order
        try:
            current_idx = all_models.index(current_model)
            return all_models[current_idx + 1:]
        except (ValueError, IndexError):
            return []

    def generate(
        self,
        prompt: str,
        modulation: str = "general",
        model_override: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Generate LLM response with routing and fallback

        Args:
            prompt: Input prompt
            modulation: Task type (reasoning/coding/fallback/general)
            model_override: Force specific model (bypasses routing)

        Returns:
            Tuple of (success: bool, response: str)
        """
        # FAZA 16 Safety Check
        is_safe, safety_msg = self.safety_validator.validate_prompt(prompt)
        if not is_safe:
            return False, f"SAFETY_VIOLATION: {safety_msg}"

        # Select model
        if model_override:
            selected_model = model_override
        else:
            selected_model = self._select_model(modulation)

        if not selected_model:
            return False, "ERROR: No enabled model available"

        # Get model config
        model_config = self.config["models"][selected_model]
        provider = model_config["provider"]
        temperature = model_config["temperature"]
        max_tokens = model_config["max_tokens"]

        # Get provider client
        if provider not in self.clients:
            return False, f"ERROR: Unknown provider {provider}"

        client = self.clients[provider]

        # Attempt generation with fallback
        try:
            response = client.generate(
                model=selected_model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Sanitize output
            sanitized_response = self.safety_validator.sanitize_output(
                response,
                max_length=self.config["safety"]["sanitization"]["max_output_length"]
            )

            return True, sanitized_response

        except Exception as e:
            # Try fallback models
            fallback_models = self._get_fallback_models(selected_model, modulation)

            for fallback_model in fallback_models:
                if self.retry_count >= self.max_retries:
                    break

                self.retry_count += 1

                try:
                    fallback_config = self.config["models"][fallback_model]
                    fallback_provider = fallback_config["provider"]
                    fallback_client = self.clients[fallback_provider]

                    response = fallback_client.generate(
                        model=fallback_model,
                        prompt=prompt,
                        temperature=fallback_config["temperature"],
                        max_tokens=fallback_config["max_tokens"]
                    )

                    sanitized_response = self.safety_validator.sanitize_output(response)
                    return True, sanitized_response

                except Exception:
                    continue

            # All attempts failed
            return False, f"ERROR: All models failed after {self.retry_count} retries"

    def get_available_models(self) -> List[str]:
        """Get list of enabled models"""
        return [
            name for name, config in self.config["models"].items()
            if config.get("enabled", True)
        ]

    def get_config_version(self) -> str:
        """Get configuration version"""
        return self.config.get("version", "unknown")

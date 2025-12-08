import json
from typing import Dict, Any, Optional

from senti_core_module.senti_llm import secrets_loader


class ProviderBridgeError(Exception):
    pass


class ProviderBridge:
    """
    Provider abstraction layer for Senti OS.
    This version implements:
    - Deterministic mock mode
    - No network calls
    - Zero hallucination risk
    - Strict provider validation (C2.1)
    - Clean prompt previewing
    """

    def __init__(self, secrets_path: str):
        self.secrets_path = secrets_path
        self.secrets = None
        self.real_mode = False

        try:
            self.secrets = secrets_loader.load_secrets(secrets_path)
            self.real_mode = secrets_loader.is_real_mode(self.secrets)
        except Exception:
            # Missing secrets → fallback to mock mode
            self.secrets = None
            self.real_mode = False

    def is_mock_mode(self) -> bool:
        return not self.real_mode

    # -----------------------------------
    # INTERNAL MOCK RESPONSE GENERATOR
    # -----------------------------------
    def _mock_response(self, provider: str, prompt: str, model: Optional[str]) -> str:
        preview = (prompt or "").replace("\n", " ").replace("\t", " ")
        preview = preview[:80]  # truncate safely

        m = model or "mock-default"

        return (
            f"[MOCK][{provider}][model={m}] "
            f'PromptPreview="{preview}"'
        )

    # -----------------------------------
    # PROVIDER DISPATCH (STRICT MODE C2.1)
    # -----------------------------------
    def call_provider(self, provider: str, prompt: str, model: Optional[str] = None) -> str:
        provider = provider.lower().strip()
        valid = ("openai", "anthropic", "mistral")

        # STRICT VALIDATION EVEN IN MOCK MODE
        if provider not in valid:
            raise ProviderBridgeError(f"Unknown provider: {provider}")

        # MOCK MODE (always safe)
        if self.is_mock_mode():
            return self._mock_response(provider, prompt, model)

        # REAL MODE (not yet implemented)
        return self._mock_response(provider, prompt, model)

    # -----------------------------------
    # PROVIDER ALIASES
    # -----------------------------------
    def call_openai(self, prompt: str, model: Optional[str] = None) -> str:
        return self.call_provider("openai", prompt, model)

    def call_anthropic(self, prompt: str, model: Optional[str] = None) -> str:
        return self.call_provider("anthropic", prompt, model)

    def call_mistral(self, prompt: str, model: Optional[str] = None) -> str:
        return self.call_provider("mistral", prompt, model)

    # -----------------------------------
    # PROVIDER STATUS API
    # -----------------------------------
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        provider = provider.lower().strip()

        return {
            "provider": provider,
            "configured": self.secrets is not None,
            "enabled": False if self.secrets is None else secrets_loader.is_provider_enabled(self.secrets, provider),
            "mode": "real" if self.real_mode else "mock"
        }

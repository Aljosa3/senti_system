# Bridge module for validation functions
from senti_core_module.senti_llm.contract_validator.validator import validate_contract
from typing import Dict, Any


class RuntimeContext:
    """
    FAZA 32 — Runtime Context Object
    """

    def __init__(self, prompt: str, capability: str):
        self.prompt = prompt
        self.capability = capability
        self.model_info = None
        self.raw_output = None
        self.wrapped_output = None
        self.validated_output = None

    def set_model(self, model_info: Dict[str, Any]) -> None:
        self.model_info = model_info

    def set_raw_output(self, output: Any) -> None:
        self.raw_output = output

    def set_wrapped(self, wrapped: Dict[str, Any]) -> None:
        self.wrapped_output = wrapped

    def set_validated(self, validated: Dict[str, Any]) -> None:
        self.validated_output = validated


__all__ = ['validate_contract', 'RuntimeContext']

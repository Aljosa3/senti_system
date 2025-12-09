from typing import Dict, Any

from senti_core_module.senti_llm.contract_wrapper.wrapper_errors import (
    WrapperError,
    WrapperSchemaError,
    WrapperNormalizationError,
    WrapperValidationError,
    WrapperAnomalyError,
    WrapperProviderError
)

from senti_core_module.senti_llm.contract_wrapper.wrapper_utils import (
    sanitize_text,
    normalize_provider,
    normalize_model,
    safe_int
)

from senti_core_module.senti_llm.contract_validator.sanitizer import (
    sanitize_basic_fields,
    sanitize_content_length,
    sanitize_types
)

from senti_core_module.senti_llm.contract_validator.validator import (
    validate_contract
)


class LLMResponseWrapper:
    def __init__(self, provider: str):
        self.provider = normalize_provider(provider)

    def wrap(self, raw: dict, strict: bool = True) -> Dict[str, Any]:
        # PHASE 1: PRE-CLEAN
        clean = {}

        for key, value in raw.items():
            k = str(key).lower().strip()
            if value is None:
                continue

            if isinstance(value, str):
                clean[k] = sanitize_text(value)
            elif isinstance(value, (int, float)):
                clean[k] = safe_int(value)
            elif isinstance(value, dict):
                clean[k] = value.copy()
            elif isinstance(value, list):
                clean[k] = value[:]
            else:
                clean[k] = str(value)

        # PHASE 2: NORMALIZATION
        clean["provider"] = normalize_provider(clean.get("provider", self.provider))
        clean["model"] = normalize_model(clean["provider"], clean.get("model"))
        clean["type"] = clean.get("type", "completion")
        clean["content"] = sanitize_text(clean.get("content", ""))

        clean["tokens_in"] = safe_int(clean.get("tokens_in", 0))
        clean["tokens_out"] = safe_int(clean.get("tokens_out", 0))

        meta = clean.get("meta", {})
        if not isinstance(meta, dict):
            raise WrapperNormalizationError("meta must be a dict")
        clean["meta"] = meta.copy()

        # PHASE 3: SANITIZER (FAZA 30.98)
        clean = sanitize_basic_fields(clean)
        clean = sanitize_content_length(clean)
        clean = sanitize_types(clean)

        # PHASE 4: VALIDATOR (FAZA 30.99)
        try:
            validated = validate_contract(clean, strict=strict)
        except Exception as e:
            raise WrapperValidationError(str(e))

        # PHASE 5: ANOMALY FIREWALL
        # Rule A - empty content (except type="tool")
        if validated["type"] != "tool" and validated["content"].strip() == "":
            raise WrapperAnomalyError("Empty content not allowed")

        # Rule B - provider/model mismatch heuristics
        m = validated["model"].lower()
        p = validated["provider"]

        if p == "openai" and "claude" in m:
            raise WrapperAnomalyError("Model/provider mismatch")
        if p == "anthropic" and "gpt" in m:
            raise WrapperAnomalyError("Model/provider mismatch")
        if p == "mistral" and "claude" in m:
            raise WrapperAnomalyError("Model/provider mismatch")

        # Rule C - repetition attack
        content = validated["content"]
        if any(ch * 500 in content for ch in set(content)):
            raise WrapperAnomalyError("Repetition anomaly detected")

        # Rule D - forbidden patterns
        forbidden = [
            "<script", "</html", "<?php", "BEGIN RSA PRIVATE",
            "sk-", "api_key="
        ]
        if any(f.lower() in content.lower() for f in forbidden):
            raise WrapperAnomalyError("Forbidden pattern detected")

        return validated

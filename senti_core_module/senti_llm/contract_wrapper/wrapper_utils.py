import re
from senti_core_module.senti_llm.contract_wrapper.wrapper_errors import WrapperProviderError


def sanitize_text(content: str) -> str:
    if content is None:
        return ""

    if not isinstance(content, str):
        content = str(content)

    # Remove null bytes
    content = content.replace("\x00", "")

    # Remove invalid unicode characters
    try:
        content = content.encode("utf-8", errors="ignore").decode("utf-8")
    except Exception:
        content = ""

    # Collapse whitespace: max 3 consecutive newlines
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    # Truncate to 50000 chars
    if len(content) > 50000:
        content = content[:50000]

    return content


def normalize_provider(p: str) -> str:
    if p is None:
        raise WrapperProviderError("Provider cannot be None")

    normalized = str(p).lower().strip()

    allowed = ["openai", "anthropic", "mistral"]
    if normalized not in allowed:
        raise WrapperProviderError(f"Invalid provider: {normalized}")

    return normalized


def normalize_model(provider: str, model: str) -> str:
    if model is None:
        return "unknown"

    if not isinstance(model, str):
        model = str(model)

    # Strip whitespace and newlines
    model = model.strip()
    model = model.replace("\n", " ").replace("\r", " ")

    # Max 200 chars
    if len(model) > 200:
        model = model[:200]

    # Empty result → "unknown"
    if model == "":
        return "unknown"

    return model


def safe_int(x) -> int:
    if isinstance(x, int) and not isinstance(x, bool):
        if x < 0:
            return 0
        return x

    if isinstance(x, float):
        result = int(x)
        if result < 0:
            return 0
        return result

    try:
        result = int(x)
        if result < 0:
            return 0
        return result
    except (ValueError, TypeError):
        return 0

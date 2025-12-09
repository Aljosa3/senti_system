from typing import Dict, Any
from .errors import ContractSanitizationError


def sanitize_basic_fields(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if value is None:
            continue

        key_str = str(key)

        if isinstance(value, str):
            result[key_str] = value.strip()
        else:
            result[key_str] = value

    return result


def sanitize_content_length(data: dict, max_len: int = 50000) -> dict:
    result = data.copy()

    if "content" in result and isinstance(result["content"], str):
        result["content"] = result["content"][:max_len]

    return result


def sanitize_types(data: dict) -> dict:
    result = data.copy()

    if "tokens_in" in result:
        if isinstance(result["tokens_in"], float):
            result["tokens_in"] = int(result["tokens_in"])

    if "tokens_out" in result:
        if isinstance(result["tokens_out"], float):
            result["tokens_out"] = int(result["tokens_out"])

    if "meta" in result:
        if not isinstance(result["meta"], dict):
            raise ContractSanitizationError("meta must be a dict")

    return result

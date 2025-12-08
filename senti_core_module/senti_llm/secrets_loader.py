import json
from typing import Dict, Any


class SecretsLoadError(Exception):
    pass


def mask_api_key(key: str) -> str:
    if key is None or key == "":
        return "***"
    if len(key) < 8:
        return "***"
    return key[:4] + "****"


def load_secrets(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r') as f:
            secrets = json.load(f)
    except FileNotFoundError:
        raise SecretsLoadError(f"Secrets file not found at {path}")
    except json.JSONDecodeError:
        raise SecretsLoadError("Invalid JSON in secrets file")

    if "providers" not in secrets:
        raise SecretsLoadError("Secrets file must contain 'providers' key")

    return secrets


def is_real_mode(secrets: Dict[str, Any]) -> bool:
    if "real_mode" not in secrets or not secrets["real_mode"]:
        return False

    providers = secrets.get("providers", {})
    for provider_name, provider_config in providers.items():
        api_key = provider_config.get("api_key", "")
        if api_key in ["XXXX", "XXXXXXXXXX", ""]:
            return False
        if api_key.count("X") == len(api_key) and len(api_key) > 0:
            return False

    return True


def is_provider_enabled(secrets: Dict[str, Any], provider: str) -> bool:
    providers = secrets.get("providers", {})
    if provider not in providers:
        return False
    return providers[provider].get("enabled", False) is True


def get_provider_config(secrets: Dict[str, Any], provider: str) -> Dict[str, Any]:
    providers = secrets.get("providers", {})
    if provider not in providers:
        raise SecretsLoadError(f"Provider '{provider}' not found in secrets")
    return providers[provider].copy()


def get_secrets_summary(secrets: Dict[str, Any]) -> str:
    providers = secrets.get("providers", {})
    lines = []

    for provider_name in ["openai", "anthropic", "mistral"]:
        if provider_name in providers:
            config = providers[provider_name]
            enabled = config.get("enabled", False)
            api_key = config.get("api_key", "")
            masked = mask_api_key(api_key)
            lines.append(f"Provider: {provider_name} | enabled={enabled} | key={masked}")
        else:
            lines.append(f"Provider: {provider_name} | enabled=False | key=***")

    return "\n".join(lines)

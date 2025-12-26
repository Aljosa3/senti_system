"""
Response Registry Loader

Loads canonical response texts from governance/response_registry.yaml.
No fallback logic. No defaults. No mutation.
"""

import os
import yaml


_REGISTRY_CACHE = None


def load_response_registry():
    global _REGISTRY_CACHE

    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE

    base_dir = os.path.dirname(os.path.dirname(__file__))
    registry_path = os.path.join(base_dir, "governance", "response_registry.yaml")

    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Response registry not found at {registry_path}")

    with open(registry_path, "r", encoding="utf-8") as f:
        _REGISTRY_CACHE = yaml.safe_load(f)

    return _REGISTRY_CACHE


def get_response_text(response_id):
    registry = load_response_registry()

    if response_id not in registry:
        raise KeyError(f"Unknown response ID: {response_id}")

    return registry[response_id]["text"]

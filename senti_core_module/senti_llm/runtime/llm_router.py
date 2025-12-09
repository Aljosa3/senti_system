FILE: senti_core_module/senti_llm/runtime/llm_runtime_router.py
----------------------------------------------------------------
from typing import Dict, Any, List


class RuntimeRouter:
    """
    FAZA 31 — routing engine
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, Any] = config.get("models", {})
        self.policy: Dict[str, List[str]] = config.get("routing_policy", {})

    def select_model(self, capability: str) -> Dict[str, Any]:
        """
        Izbere model glede na routing policy.
        """
        sequence = self.policy.get(capability, [])
        if not sequence:
            raise ValueError(f"No routing sequence for capability: {capability}")

        # vzame prvi enabled model
        for model_name in sequence:
            m = self.models.get(model_name)
            if m and m.get("enabled", False):
                return {
                    "name": model_name,
                    "provider": m["provider"],
                    "temperature": m.get("temperature", 0.5),
                    "priority": m.get("priority", 99),
                }

        raise ValueError(f"No enabled model available for capability: {capability}")

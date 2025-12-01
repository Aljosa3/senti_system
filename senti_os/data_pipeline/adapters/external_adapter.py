from __future__ import annotations
import uuid, time
from typing import Any, Dict

class ExternalSystemAdapter:
    def normalize(self, system_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "external_system",
            "origin": system_name,
            "payload": payload,
            "timestamp": time.time(),
            "is_real": True,
            "synthetic": False,
            "mock": False,
        }

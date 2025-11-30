from __future__ import annotations
from typing import Any, Dict
import time
import uuid

class APIAdapter:
    """
    Pretvori podatke iz API-ja v standardizirano strukturo.
    """

    def normalize(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "api",
            "origin": source,
            "payload": payload,
            "timestamp": time.time(),
            "is_real": True,               # FAZA 7
            "synthetic": False,
            "mock": False,
        }

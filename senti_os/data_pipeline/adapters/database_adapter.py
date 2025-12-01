from __future__ import annotations
from typing import Any, Dict
import time, uuid

class DatabaseAdapter:
    def normalize(self, db_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "database",
            "origin": db_name,
            "payload": payload,
            "timestamp": time.time(),
            "is_real": True,
            "synthetic": False,
            "mock": False,
        }

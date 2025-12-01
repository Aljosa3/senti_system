from __future__ import annotations
from typing import Dict, Any
import time, uuid

class SensorAdapter:
    def normalize(self, sensor_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "sensor",
            "origin": sensor_name,
            "payload": payload,
            "timestamp": time.time(),
            "is_real": True,
            "synthetic": False,
            "mock": False,
        }

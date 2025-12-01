from __future__ import annotations
from typing import Dict, Any
import time, uuid

class FileAdapter:
    def normalize(self, file_path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "file",
            "origin": file_path,
            "payload": payload,
            "timestamp": time.time(),
            "is_real": True,
            "synthetic": False,
            "mock": False,
        }

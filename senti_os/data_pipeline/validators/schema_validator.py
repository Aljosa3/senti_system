from __future__ import annotations
from typing import Dict, Any

class SchemaValidator:
    REQUIRED_FIELDS = {"id", "type", "origin", "payload", "timestamp", "is_real"}

    def validate(self, data: Dict[str, Any]) -> None:
        missing = self.REQUIRED_FIELDS - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

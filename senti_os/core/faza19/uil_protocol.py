"""
FAZA 19 - UIL Protocol

JSON message protocol for Unified Interaction Layer.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class MessageType(Enum):
    """UIL message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


@dataclass
class UILMessage:
    """Unified Interaction Layer message."""
    message_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    device_id: Optional[str] = None
    request_id: Optional[str] = None  # For linking responses to requests

    def to_json(self) -> str:
        """Convert message to JSON string."""
        data = {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "device_id": self.device_id,
            "request_id": self.request_id
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "UILMessage":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            device_id=data.get("device_id"),
            request_id=data.get("request_id")
        )


class UILProtocol:
    """Protocol handler for UIL messages."""

    def __init__(self):
        """Initialize protocol handler."""
        self._message_counter = 0

    def create_request(
        self,
        action: str,
        params: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> UILMessage:
        """Create request message."""
        self._message_counter += 1
        return UILMessage(
            message_id=f"msg_{self._message_counter}",
            message_type=MessageType.REQUEST,
            payload={"action": action, "params": params},
            timestamp=datetime.utcnow(),
            device_id=device_id
        )

    def create_response(
        self,
        request_id: str,
        result: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> UILMessage:
        """Create response message."""
        self._message_counter += 1
        return UILMessage(
            message_id=f"msg_{self._message_counter}",
            message_type=MessageType.RESPONSE,
            payload={"result": result},
            timestamp=datetime.utcnow(),
            device_id=device_id,
            request_id=request_id
        )

    def create_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> UILMessage:
        """Create event message."""
        self._message_counter += 1
        return UILMessage(
            message_id=f"msg_{self._message_counter}",
            message_type=MessageType.EVENT,
            payload={"event_type": event_type, "data": data},
            timestamp=datetime.utcnow(),
            device_id=device_id
        )


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "uil_protocol",
        "faza": "19",
        "version": "1.0.0",
        "description": "JSON message protocol for UIL"
    }

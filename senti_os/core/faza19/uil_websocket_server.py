"""
FAZA 19 - UIL WebSocket Server (Simulated)

Simulated WebSocket server for bidirectional streaming.

Author: SENTI OS Core Team
License: Proprietary
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime, timedelta
import threading
import time


class SimulatedWebSocketConnection:
    """Simulated WebSocket connection."""

    def __init__(self, connection_id: str, device_id: str):
        """Initialize connection."""
        self.connection_id = connection_id
        self.device_id = device_id
        self.connected = True
        self.last_heartbeat = datetime.utcnow()
        self.message_queue: List[str] = []

    def send(self, message: str):
        """Send message to client (simulated)."""
        if self.connected:
            self.message_queue.append(message)

    def receive(self) -> Optional[str]:
        """Receive message from client (simulated)."""
        if self.message_queue:
            return self.message_queue.pop(0)
        return None

    def close(self):
        """Close connection."""
        self.connected = False


class UILWebSocketServer:
    """Simulated WebSocket server for UIL."""

    def __init__(self, heartbeat_interval: int = 30):
        """Initialize WebSocket server."""
        self.heartbeat_interval = heartbeat_interval
        self._connections: Dict[str, SimulatedWebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._connection_counter = 0
        self._running = False
        self._heartbeat_thread = None

    def start(self):
        """Start WebSocket server."""
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self):
        """Stop WebSocket server."""
        self._running = False
        for conn in self._connections.values():
            conn.close()

    def connect(self, device_id: str) -> str:
        """Simulate device connection."""
        self._connection_counter += 1
        connection_id = f"conn_{self._connection_counter}"

        conn = SimulatedWebSocketConnection(connection_id, device_id)
        self._connections[connection_id] = conn

        return connection_id

    def disconnect(self, connection_id: str):
        """Disconnect device."""
        if connection_id in self._connections:
            self._connections[connection_id].close()
            del self._connections[connection_id]

    def send_to_device(self, device_id: str, message: str):
        """Send message to specific device."""
        for conn in self._connections.values():
            if conn.device_id == device_id and conn.connected:
                conn.send(message)

    def broadcast(self, message: str):
        """Broadcast message to all connected devices."""
        for conn in self._connections.values():
            if conn.connected:
                conn.send(message)

    def register_message_handler(self, handler: Callable):
        """Register message handler."""
        self._message_handlers.append(handler)

    def get_active_connections(self) -> List[str]:
        """Get list of active connection IDs."""
        return [
            conn.connection_id for conn in self._connections.values()
            if conn.connected
        ]

    def _heartbeat_loop(self):
        """Heartbeat loop to check connections."""
        while self._running:
            time.sleep(self.heartbeat_interval)
            now = datetime.utcnow()
            timeout = timedelta(seconds=self.heartbeat_interval * 3)

            # Check for stale connections
            to_remove = []
            for conn_id, conn in self._connections.items():
                if now - conn.last_heartbeat > timeout:
                    to_remove.append(conn_id)

            for conn_id in to_remove:
                self.disconnect(conn_id)


def get_info() -> Dict[str, str]:
    """Get module information."""
    return {
        "module": "uil_websocket_server",
        "faza": "19",
        "version": "1.0.0",
        "description": "Simulated WebSocket server for UIL"
    }

"""
Base Service Class
Location: senti_os/system/base_service.py

Base class for all Senti OS services.
"""


class BaseService:
    """
    Base class for Senti OS services.
    All services should inherit from this class and implement:
    - start()
    - stop()
    - status()
    """

    def __init__(self, name: str):
        self.name = name
        self._running = False

    def start(self):
        """Start the service"""
        self._running = True

    def stop(self):
        """Stop the service"""
        self._running = False

    def status(self):
        """Get service status"""
        return {
            "name": self.name,
            "running": self._running
        }

    def is_running(self):
        """Check if service is running"""
        return self._running

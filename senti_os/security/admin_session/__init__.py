"""
Minimal ADMIN Session Management
---------------------------------
Time-bound administrative authority for critical operations.
"""

from .session_manager import AdminSessionManager, AdminSession, get_session_manager

__all__ = ["AdminSessionManager", "AdminSession", "get_session_manager"]

"""
FAZA 59 — Lock Preparation & Human Confirmation
-----------------------------------------------
Human decision collection and audit trail recording before CORE LOCK.
"""

from .human_confirmation import HumanConfirmationManager, LockConfirmationRecord

__all__ = ["HumanConfirmationManager", "LockConfirmationRecord"]

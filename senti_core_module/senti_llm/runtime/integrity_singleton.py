"""
FAZA 45 — Global Integrity Manager Singleton
---------------------------------------------
Breaks circular import by providing get_global_integrity_manager
in a separate module that doesn't import other runtime modules.
"""

from senti_core_module.senti_core.integrity import IntegrityManager

# Global IntegrityManager instance
_global_integrity_manager = None


def get_global_integrity_manager() -> IntegrityManager:
    """Get or create the global IntegrityManager singleton."""
    global _global_integrity_manager

    if _global_integrity_manager is None:
        _global_integrity_manager = IntegrityManager(strict_mode=True)

    return _global_integrity_manager

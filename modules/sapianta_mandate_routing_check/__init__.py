"""
SAPIANTA MANDATE ROUTING_CHECK - FAZA II
Status: LOCKED
Avtoriteta: docs/governance/SAPIANTA_MANDATE_V1.md

This module implements the canonical ROUTING_CHECK for mandate validation.

ROUTING_CHECK is the ONLY gate between USER_DECISION and MANDATE_DRAFT.

Usage:
    from modules.sapianta_mandate_routing_check import routing_check

    result = routing_check(mandate)
    # result = {"status": "OK" | "CLARIFY" | "REFUSE", "reason": "..."}
"""

from .routing_check import routing_check

__all__ = ["routing_check"]

__version__ = "1.0.0-faza2"
__status__ = "LOCKED"

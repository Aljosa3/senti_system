"""
SAPIANTA MANDATE - ROUTING_CHECK (FAZA II)
Status: LOCKED
Avtoriteta: docs/governance/SAPIANTA_MANDATE_V1.md

This module implements the canonical ROUTING_CHECK for mandate validation.

ROUTING_CHECK is the ONLY gate between USER_DECISION and MANDATE_DRAFT.
It does NOT execute, confirm, or modify mandates.
It ONLY validates structure and returns OK/CLARIFY/REFUSE.
"""

from typing import Dict, Any
from datetime import datetime


def routing_check(mandate: Dict[str, Any]) -> Dict[str, str]:
    """
    Canonical ROUTING_CHECK for mandate validation.

    This function validates mandate structure according to SAPIANTA_MANDATE_V1.md.
    It performs validation in strict order and returns deterministic results.

    Args:
        mandate: Mandate dictionary to validate

    Returns:
        {
            "status": "OK" | "CLARIFY" | "REFUSE",
            "reason": "Explanation of result"
        }

    Validation Order (MUST be followed):
    1. Presence of all required keys
    2. Validity of scope.resource and scope.context
    3. Conflicts in constraints.allowed / constraints.forbidden
    4. Existence of limits (all null → NO EXECUTION)
    5. Time validity (expires_at)
    6. revoked == False
    7. confirmed == False (in this phase)

    IMPORTANT: This function does NOT:
    - Execute anything
    - Confirm mandate
    - Modify mandate
    - Add default values
    - "Fix" input
    """

    # =======================================================================
    # VALIDATION 1: Presence of all required keys
    # =======================================================================

    REQUIRED_TOP_LEVEL_KEYS = [
        "id",
        "intent",
        "action",
        "scope",
        "constraints",
        "limits",
        "created_at",
        "expires_at",
        "confirmed",
        "revoked"
    ]

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in mandate:
            return {
                "status": "CLARIFY",
                "reason": f"Missing required key: '{key}'"
            }

    # Check scope structure
    if not isinstance(mandate["scope"], dict):
        return {
            "status": "CLARIFY",
            "reason": "Invalid structure: 'scope' must be a dictionary"
        }

    REQUIRED_SCOPE_KEYS = ["resource", "context"]
    for key in REQUIRED_SCOPE_KEYS:
        if key not in mandate["scope"]:
            return {
                "status": "CLARIFY",
                "reason": f"Missing required key in scope: '{key}'"
            }

    # Check constraints structure
    if not isinstance(mandate["constraints"], dict):
        return {
            "status": "CLARIFY",
            "reason": "Invalid structure: 'constraints' must be a dictionary"
        }

    REQUIRED_CONSTRAINTS_KEYS = ["allowed", "forbidden"]
    for key in REQUIRED_CONSTRAINTS_KEYS:
        if key not in mandate["constraints"]:
            return {
                "status": "CLARIFY",
                "reason": f"Missing required key in constraints: '{key}'"
            }

    # Check limits structure
    if not isinstance(mandate["limits"], dict):
        return {
            "status": "CLARIFY",
            "reason": "Invalid structure: 'limits' must be a dictionary"
        }

    REQUIRED_LIMITS_KEYS = ["max_amount", "max_count", "time_window"]
    for key in REQUIRED_LIMITS_KEYS:
        if key not in mandate["limits"]:
            return {
                "status": "CLARIFY",
                "reason": f"Missing required key in limits: '{key}'"
            }

    # =======================================================================
    # VALIDATION 2: Validity of scope.resource and scope.context
    # =======================================================================

    resource = mandate["scope"]["resource"]
    context = mandate["scope"]["context"]

    # Must be strings
    if not isinstance(resource, str):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: scope.resource must be a string"
        }

    if not isinstance(context, str):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: scope.context must be a string"
        }

    # Must not be empty
    if not resource or resource.strip() == "":
        return {
            "status": "CLARIFY",
            "reason": "Invalid value: scope.resource cannot be empty"
        }

    if not context or context.strip() == "":
        return {
            "status": "CLARIFY",
            "reason": "Invalid value: scope.context cannot be empty"
        }

    # =======================================================================
    # VALIDATION 3: Conflicts in constraints.allowed / constraints.forbidden
    # =======================================================================

    allowed = mandate["constraints"]["allowed"]
    forbidden = mandate["constraints"]["forbidden"]

    # Must be lists
    if not isinstance(allowed, list):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: constraints.allowed must be a list"
        }

    if not isinstance(forbidden, list):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: constraints.forbidden must be a list"
        }

    # Check for conflicts (same item in both allowed and forbidden)
    allowed_set = set(allowed)
    forbidden_set = set(forbidden)
    conflicts = allowed_set.intersection(forbidden_set)

    if conflicts:
        return {
            "status": "REFUSE",
            "reason": f"Conflict in constraints: {list(conflicts)} appear in both allowed and forbidden"
        }

    # =======================================================================
    # VALIDATION 4: Existence of limits (all null → NO EXECUTION)
    # =======================================================================

    max_amount = mandate["limits"]["max_amount"]
    max_count = mandate["limits"]["max_count"]
    time_window = mandate["limits"]["time_window"]

    all_limits_null = (max_amount is None and max_count is None and time_window is None)

    if all_limits_null:
        # This is OK, but with a note that execution will be prevented later
        return {
            "status": "OK",
            "reason": "Validation passed. Note: All limits are null - execution will be prevented in later phase."
        }

    # =======================================================================
    # VALIDATION 5: Time validity (expires_at)
    # =======================================================================

    expires_at = mandate["expires_at"]

    # Must be a string (ISO-8601 timestamp)
    if not isinstance(expires_at, str):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: expires_at must be an ISO-8601 timestamp string"
        }

    # Parse and check if expired
    try:
        expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        now = datetime.now(expires_datetime.tzinfo) if expires_datetime.tzinfo else datetime.now()

        if now > expires_datetime:
            return {
                "status": "REFUSE",
                "reason": f"Mandate has expired. Expiration: {expires_at}, Current time: {now.isoformat()}"
            }
    except (ValueError, AttributeError) as e:
        return {
            "status": "CLARIFY",
            "reason": f"Invalid format: expires_at must be a valid ISO-8601 timestamp. Error: {str(e)}"
        }

    # =======================================================================
    # VALIDATION 6: revoked == False
    # =======================================================================

    revoked = mandate["revoked"]

    if not isinstance(revoked, bool):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: revoked must be a boolean"
        }

    if revoked:
        return {
            "status": "REFUSE",
            "reason": "Mandate has been revoked and is no longer valid"
        }

    # =======================================================================
    # VALIDATION 7: confirmed == False (in MANDATE_DRAFT phase)
    # =======================================================================

    confirmed = mandate["confirmed"]

    if not isinstance(confirmed, bool):
        return {
            "status": "CLARIFY",
            "reason": "Invalid type: confirmed must be a boolean"
        }

    if confirmed:
        # In ROUTING_CHECK (MANDATE_DRAFT phase), confirmed must be False
        # If it's already True, something went wrong - this should not be re-validated
        return {
            "status": "REFUSE",
            "reason": "Mandate is already confirmed. ROUTING_CHECK only validates unconfirmed mandates."
        }

    # =======================================================================
    # ALL VALIDATIONS PASSED
    # =======================================================================

    return {
        "status": "OK",
        "reason": "All validations passed. Mandate is ready for MANDATE_DRAFT."
    }

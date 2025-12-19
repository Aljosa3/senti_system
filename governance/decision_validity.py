"""
Phase 63.2 — Decision Validity

Evaluates validity of decision records based on expiry and revocation status.
This is NOT a decision engine or persistence backend.
"""

from governance.decision_record import decision_record_exists, get_decision_record


def check_decision_validity(module_id, current_time=None):
    """
    Check if a decision record is valid for the given module.

    Args:
        module_id: The module identifier to check
        current_time: Optional timestamp for expiry comparison

    Returns:
        "DECISION_VALID" if decision is valid
        "DECISION_INVALID" if decision is expired, revoked, or absent
    """
    # Check if record exists
    if decision_record_exists(module_id) != "RECORD_PRESENT":
        return "DECISION_INVALID"

    # Retrieve record
    record = get_decision_record(module_id)
    if record is None:
        return "DECISION_INVALID"

    # Check expiry
    if "expires_at" in record and record["expires_at"] is not None:
        if current_time is not None and record["expires_at"] < current_time:
            return "DECISION_INVALID"

    # Check revocation
    if "revoked" in record and record["revoked"] is True:
        return "DECISION_INVALID"

    # Decision is valid
    return "DECISION_VALID"

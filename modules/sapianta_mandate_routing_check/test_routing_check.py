"""
SAPIANTA MANDATE - ROUTING_CHECK MINIMAL TESTS
Status: LOCKED
Avtoriteta: Implementation requirements (FAZA II)

This file verifies the 5 mandatory test scenarios for FAZA II routing_check.

Test Scenarios:
1. Missing required key → CLARIFY
2. Conflict in constraints → REFUSE
3. Expired mandate → REFUSE
4. Revoked mandate → REFUSE
5. Valid mandate → OK
"""

import sys
sys.path.insert(0, '/home/pisarna/senti_system')

from datetime import datetime, timedelta
from modules.sapianta_mandate_routing_check import routing_check


def create_valid_mandate():
    """Helper to create a valid mandate for testing."""
    return {
        "id": "test-id-123",
        "intent": "test intent",
        "action": "TEST_ACTION",
        "scope": {
            "resource": "TEST_RESOURCE",
            "context": "TEST_CONTEXT"
        },
        "constraints": {
            "allowed": ["action1", "action2"],
            "forbidden": ["action3"]
        },
        "limits": {
            "max_amount": 1000,
            "max_count": 10,
            "time_window": "24h"
        },
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        "confirmed": False,
        "revoked": False
    }


def test_scenario_1_missing_key():
    """
    TEST SCENARIO 1: Missing required key → CLARIFY
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 1: Missing required key → CLARIFY")
    print("="*70)

    # Create mandate with missing key
    mandate = create_valid_mandate()
    del mandate["action"]  # Remove required key

    result = routing_check(mandate)

    if result["status"] == "CLARIFY" and "action" in result["reason"]:
        print(f"✅ PASSED: Missing key correctly returned CLARIFY")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected CLARIFY with 'action' in reason")
        print(f"   Got: {result}")
        return False


def test_scenario_2_conflict_constraints():
    """
    TEST SCENARIO 2: Conflict in constraints → REFUSE
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 2: Conflict in constraints → REFUSE")
    print("="*70)

    # Create mandate with conflicting constraints
    mandate = create_valid_mandate()
    mandate["constraints"]["allowed"] = ["action1", "action2", "conflict"]
    mandate["constraints"]["forbidden"] = ["action3", "conflict"]

    result = routing_check(mandate)

    if result["status"] == "REFUSE" and "conflict" in result["reason"].lower():
        print(f"✅ PASSED: Constraint conflict correctly returned REFUSE")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected REFUSE with 'conflict' in reason")
        print(f"   Got: {result}")
        return False


def test_scenario_3_expired_mandate():
    """
    TEST SCENARIO 3: Expired mandate → REFUSE
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 3: Expired mandate → REFUSE")
    print("="*70)

    # Create mandate with expired timestamp
    mandate = create_valid_mandate()
    mandate["expires_at"] = (datetime.now() - timedelta(hours=1)).isoformat()

    result = routing_check(mandate)

    if result["status"] == "REFUSE" and "expired" in result["reason"].lower():
        print(f"✅ PASSED: Expired mandate correctly returned REFUSE")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected REFUSE with 'expired' in reason")
        print(f"   Got: {result}")
        return False


def test_scenario_4_revoked_mandate():
    """
    TEST SCENARIO 4: Revoked mandate → REFUSE
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 4: Revoked mandate → REFUSE")
    print("="*70)

    # Create revoked mandate
    mandate = create_valid_mandate()
    mandate["revoked"] = True

    result = routing_check(mandate)

    if result["status"] == "REFUSE" and "revoked" in result["reason"].lower():
        print(f"✅ PASSED: Revoked mandate correctly returned REFUSE")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected REFUSE with 'revoked' in reason")
        print(f"   Got: {result}")
        return False


def test_scenario_5_valid_mandate():
    """
    TEST SCENARIO 5: Valid mandate → OK
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 5: Valid mandate → OK")
    print("="*70)

    # Create valid mandate
    mandate = create_valid_mandate()

    result = routing_check(mandate)

    if result["status"] == "OK":
        print(f"✅ PASSED: Valid mandate correctly returned OK")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected OK")
        print(f"   Got: {result}")
        return False


def test_bonus_all_limits_null():
    """
    BONUS TEST: All limits null → OK (with note)
    """
    print("\n" + "="*70)
    print("BONUS TEST: All limits null → OK (with note)")
    print("="*70)

    # Create mandate with all limits null
    mandate = create_valid_mandate()
    mandate["limits"]["max_amount"] = None
    mandate["limits"]["max_count"] = None
    mandate["limits"]["time_window"] = None

    result = routing_check(mandate)

    if result["status"] == "OK" and "null" in result["reason"].lower():
        print(f"✅ PASSED: All null limits correctly returned OK with note")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ FAILED: Expected OK with note about null limits")
        print(f"   Got: {result}")
        return False


def run_all_tests():
    """
    Run all mandatory test scenarios.
    """
    print("\n" + "="*70)
    print("SAPIANTA MANDATE - ROUTING_CHECK MINIMAL TESTS")
    print("="*70)

    results = []

    # Mandatory tests
    results.append(("Scenario 1: Missing key", test_scenario_1_missing_key()))
    results.append(("Scenario 2: Conflict constraints", test_scenario_2_conflict_constraints()))
    results.append(("Scenario 3: Expired mandate", test_scenario_3_expired_mandate()))
    results.append(("Scenario 4: Revoked mandate", test_scenario_4_revoked_mandate()))
    results.append(("Scenario 5: Valid mandate", test_scenario_5_valid_mandate()))

    # Bonus test
    results.append(("Bonus: All limits null", test_bonus_all_limits_null()))

    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n🎉 ALL MANDATORY TESTS PASSED")
        print("FAZA II (routing_check) test requirements are satisfied.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("FAZA II (routing_check) test requirements are NOT satisfied.")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

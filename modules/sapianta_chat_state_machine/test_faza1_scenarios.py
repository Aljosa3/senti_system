"""
SAPIANTA CHAT - FAZA I MANDATORY TEST SCENARIOS
Status: LOCKED
Avtoriteta: Implementation requirements

This file verifies the 5 mandatory test scenarios for FAZA I.

Test Scenarios:
1. No path to EXECUTION without MANDATE_CONFIRM
2. Silence in USER_DECISION → IDLE
3. Unclear input → CLARIFY
4. Constraint violation → REFUSE
5. Execution always goes to RESULT → IDLE
"""

import sys
sys.path.insert(0, '/home/pisarna/senti_system')

from modules.sapianta_chat_state_machine import ChatStateMachine, ChatState, TransitionError


def test_scenario_1_no_execution_without_mandate_confirm():
    """
    TEST SCENARIO 1: No path to EXECUTION without MANDATE_CONFIRM

    This test verifies the ABSOLUTE RULE:
    EXECUTION can ONLY be reached from MANDATE_CONFIRM.
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 1: No path to EXECUTION without MANDATE_CONFIRM")
    print("="*70)

    machine = ChatStateMachine()

    # Try to transition from IDLE to EXECUTION (should fail)
    try:
        machine.transition_to(ChatState.EXECUTION)
        print("❌ FAILED: Allowed transition from IDLE to EXECUTION")
        return False
    except (TransitionError, RuntimeError) as e:
        print(f"✅ PASSED: Correctly blocked transition from IDLE to EXECUTION")
        print(f"   Error: {str(e)[:80]}...")

    # Try to transition from ADVISORY to EXECUTION (should fail)
    machine.reset()
    machine.current_state = ChatState.ADVISORY
    try:
        machine.transition_to(ChatState.EXECUTION)
        print("❌ FAILED: Allowed transition from ADVISORY to EXECUTION")
        return False
    except (TransitionError, RuntimeError) as e:
        print(f"✅ PASSED: Correctly blocked transition from ADVISORY to EXECUTION")

    # Valid path: MANDATE_CONFIRM → EXECUTION (should succeed)
    machine.reset()
    machine.current_state = ChatState.MANDATE_CONFIRM
    try:
        machine.transition_to(ChatState.EXECUTION)
        print(f"✅ PASSED: Allowed transition from MANDATE_CONFIRM to EXECUTION")
        print(f"   Current state: {machine.current_state.name}")
    except Exception as e:
        print(f"❌ FAILED: Blocked valid transition from MANDATE_CONFIRM to EXECUTION")
        print(f"   Error: {str(e)}")
        return False

    print("\n✅ SCENARIO 1: PASSED")
    return True


def test_scenario_2_silence_in_user_decision():
    """
    TEST SCENARIO 2: Silence in USER_DECISION → IDLE

    Verifies that silence (empty input) in USER_DECISION returns to IDLE.
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 2: Silence in USER_DECISION → IDLE")
    print("="*70)

    machine = ChatStateMachine()
    machine.current_state = ChatState.USER_DECISION

    # Send empty input (silence)
    response = machine.handle_input("")

    if machine.current_state == ChatState.IDLE:
        print(f"✅ PASSED: Silence in USER_DECISION correctly returned to IDLE")
        print(f"   Response: {response['message']}")
        print("\n✅ SCENARIO 2: PASSED")
        return True
    else:
        print(f"❌ FAILED: Expected IDLE, got {machine.current_state.name}")
        return False


def test_scenario_3_unclear_input_clarify():
    """
    TEST SCENARIO 3: Unclear input → CLARIFY

    Verifies that unclear input triggers CLARIFY state.
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 3: Unclear input → CLARIFY")
    print("="*70)

    machine = ChatStateMachine()

    # Start from IDLE, send input to go to INTENT_RECEIVED
    machine.handle_input("something")

    # Now in INTENT_RECEIVED, send unclear input
    response = machine.handle_input("I'm not sure what I want?")

    if machine.current_state == ChatState.CLARIFY:
        print(f"✅ PASSED: Unclear input correctly triggered CLARIFY state")
        print(f"   Response: {response['message']}")
        print("\n✅ SCENARIO 3: PASSED")
        return True
    else:
        print(f"❌ FAILED: Expected CLARIFY, got {machine.current_state.name}")
        return False


def test_scenario_4_constraint_violation_refuse():
    """
    TEST SCENARIO 4: Constraint violation → REFUSE

    Verifies that constraint violations trigger REFUSE state.
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 4: Constraint violation → REFUSE")
    print("="*70)

    machine = ChatStateMachine()

    # Start from IDLE, send input to go to INTENT_RECEIVED
    machine.handle_input("something")

    # Now in INTENT_RECEIVED, send invalid input
    response = machine.handle_input("forbidden action")

    if machine.current_state == ChatState.REFUSE:
        print(f"✅ PASSED: Invalid input correctly triggered REFUSE state")
        print(f"   Response: {response['message']}")
        print("\n✅ SCENARIO 4: PASSED")
        return True
    else:
        print(f"❌ FAILED: Expected REFUSE, got {machine.current_state.name}")
        return False


def test_scenario_5_execution_to_result_to_idle():
    """
    TEST SCENARIO 5: Execution always goes to RESULT → IDLE

    Verifies the execution flow: EXECUTION → RESULT → IDLE
    """
    print("\n" + "="*70)
    print("TEST SCENARIO 5: Execution → RESULT → IDLE")
    print("="*70)

    machine = ChatStateMachine()

    # Set up context with a mandate
    machine.context = {
        "mandate": {
            "intent": "test",
            "confirmed": True
        }
    }

    # Start from EXECUTION
    machine.current_state = ChatState.EXECUTION

    # Handle execution (should go to RESULT)
    response = machine.handle_input("")

    if machine.current_state != ChatState.RESULT:
        print(f"❌ FAILED: EXECUTION did not go to RESULT")
        print(f"   Got: {machine.current_state.name}")
        return False

    print(f"✅ PASSED: EXECUTION → RESULT")

    # Handle result (should go to IDLE)
    response = machine.handle_input("")

    if machine.current_state != ChatState.IDLE:
        print(f"❌ FAILED: RESULT did not go to IDLE")
        print(f"   Got: {machine.current_state.name}")
        return False

    print(f"✅ PASSED: RESULT → IDLE")
    print("\n✅ SCENARIO 5: PASSED")
    return True


def run_all_tests():
    """
    Run all mandatory test scenarios.
    """
    print("\n" + "="*70)
    print("SAPIANTA CHAT - FAZA I MANDATORY TEST SCENARIOS")
    print("="*70)

    results = []

    results.append(("Scenario 1", test_scenario_1_no_execution_without_mandate_confirm()))
    results.append(("Scenario 2", test_scenario_2_silence_in_user_decision()))
    results.append(("Scenario 3", test_scenario_3_unclear_input_clarify()))
    results.append(("Scenario 4", test_scenario_4_constraint_violation_refuse()))
    results.append(("Scenario 5", test_scenario_5_execution_to_result_to_idle()))

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
        print("FAZA I test requirements are satisfied.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("FAZA I test requirements are NOT satisfied.")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

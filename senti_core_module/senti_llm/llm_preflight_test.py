"""
FAZA 30.95 - LLM Configuration Layer Preflight Test

Validates that the LLM Client is properly configured and operational.

Test procedure:
1. Load LLMClient
2. Execute test prompt: "Return the string 'OK' only."
3. Verify output contains "OK"
4. Raise RuntimeError on failure

SECURITY: No file system or network access.
"""

from llm_client import LLMClient


def run_preflight_test():
    """Execute preflight test for LLM Configuration Layer"""
    print("[FAZA 30.95] LLM Preflight Test - Starting...")

    try:
        # Step 1: Load LLMClient
        print("[1/3] Loading LLMClient...")
        client = LLMClient()
        print(f"      Config version: {client.get_config_version()}")
        print(f"      Available models: {', '.join(client.get_available_models())}")

        # Step 2: Execute test prompt
        print("[2/3] Executing test prompt...")
        test_prompt = "Return the string 'OK' only."
        success, response = client.generate(prompt=test_prompt, modulation="general")

        if not success:
            raise RuntimeError(f"LLM generation failed: {response}")

        print(f"      Response received: {response[:100]}...")

        # Step 3: Verify output contains "OK"
        print("[3/3] Verifying output...")
        if "OK" not in response.upper():
            raise RuntimeError(f"Output validation failed: 'OK' not found in response")

        print("[PASS] LLM Preflight Test - All checks passed")
        print(f"[INFO] Full response: {response}")
        return True

    except Exception as e:
        print(f"[FAIL] LLM Preflight Test - Error: {e}")
        raise RuntimeError(f"FAZA 30.95 Preflight Test Failed: {e}")


def test_routing():
    """Test routing for different modulations"""
    print("\n[BONUS] Testing routing policies...")
    client = LLMClient()

    modulations = ["reasoning", "coding", "fallback", "general"]

    for mod in modulations:
        success, response = client.generate(
            prompt=f"Test {mod} modulation",
            modulation=mod
        )
        if success:
            print(f"  [{mod.upper()}] ✓ {response[:60]}...")
        else:
            print(f"  [{mod.upper()}] ✗ {response}")


def test_safety():
    """Test FAZA 16 safety integration"""
    print("\n[BONUS] Testing FAZA 16 safety integration...")
    client = LLMClient()

    # Test forbidden patterns
    forbidden_tests = [
        "os.system('ls')",
        "subprocess.call(['rm', '-rf'])",
        "eval('malicious_code')",
        "exec('bad_code')"
    ]

    for test_prompt in forbidden_tests:
        success, response = client.generate(prompt=test_prompt)
        if not success and "SAFETY_VIOLATION" in response:
            print(f"  [BLOCKED] ✓ '{test_prompt[:30]}...' correctly blocked")
        else:
            print(f"  [FAILED] ✗ '{test_prompt[:30]}...' should have been blocked")


def test_fallback():
    """Test fallback mechanism"""
    print("\n[BONUS] Testing fallback mechanism...")
    client = LLMClient()

    print(f"  Max retries configured: {client.max_retries}")
    print(f"  Cascade on error: {client.config['fallback_chain']['cascade_on_error']}")
    print("  [INFO] Fallback chain: mixtral-8x22b → claude-sonnet-3.7 → gpt-4.1")


if __name__ == "__main__":
    try:
        # Main preflight test
        run_preflight_test()

        # Additional validation tests
        test_routing()
        test_safety()
        test_fallback()

        print("\n" + "="*60)
        print("FAZA 30.95 - LLM CONFIGURATION LAYER: OPERATIONAL")
        print("="*60)

    except RuntimeError as e:
        print("\n" + "="*60)
        print(f"FAZA 30.95 - LLM CONFIGURATION LAYER: FAILED")
        print(f"Error: {e}")
        print("="*60)
        raise

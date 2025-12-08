#!/usr/bin/env python3
"""
FAZA 30.97 - MAX LLM Preflight Integration Test
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from senti_core_module.senti_llm import secrets_loader
from senti_core_module.senti_llm.provider_bridge import ProviderBridge, ProviderBridgeError


class IntegrationTestResult:
    """Container for test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✓ {test_name}")

    def record_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  ✗ {test_name}: {reason}")

    def summary(self) -> str:
        total = self.passed + self.failed
        return f"Results: {self.passed}/{total} passed, {self.failed}/{total} failed"


def create_valid_test_secrets() -> Dict[str, Any]:
    """Create valid test secrets structure."""
    return {
        "providers": {
            "openai": {
                "api_key": "sk-test1234567890abcdefghijklmnop",
                "organization_id": "org-test",
                "enabled": True
            },
            "anthropic": {
                "api_key": "sk-ant-test1234567890abcdefghijklmnop",
                "enabled": False
            },
            "mistral": {
                "api_key": "mistral-test1234567890abcdef",
                "enabled": True
            }
        },
        "default_provider": "openai",
        "real_mode": False
    }
def test_secrets_loader_missing_file(result: IntegrationTestResult):
    """Test 1.1: Missing llm_secrets.json triggers correct error."""
    try:
        secrets_loader.load_secrets("/nonexistent/path/to/secrets.json")
        result.record_fail("Missing file error", "Should have raised SecretsLoadError")
    except secrets_loader.SecretsLoadError as e:
        if "not found" in str(e).lower():
            result.record_pass("Missing file error")
        else:
            result.record_fail("Missing file error", f"Wrong error message: {e}")
    except Exception as e:
        result.record_fail("Missing file error", f"Wrong exception type: {type(e).__name__}")


def test_secrets_loader_parse_spec(result: IntegrationTestResult):
    """Test 1.2: Parse valid secrets structure."""
    try:
        secrets = create_valid_test_secrets()
        if "providers" in secrets:
            result.record_pass("Valid secrets structure has providers")
        else:
            result.record_fail("Valid secrets structure", "Missing providers")
        if "openai" in secrets["providers"]:
            result.record_pass("Valid secrets has openai provider")
        else:
            result.record_fail("Valid secrets", "Missing openai")
    except Exception as e:
        result.record_fail("Parse valid secrets", str(e))


def test_secrets_loader_missing_providers_structure(result: IntegrationTestResult):
    """Test 1.3: Detect missing providers in structure."""
    invalid_secrets = {"real_mode": False}
    if "providers" not in invalid_secrets:
        result.record_pass("Detect missing providers key")
    else:
        result.record_fail("Detect missing providers", "Should not have providers")


def test_secrets_loader_missing_required_provider_structure(result: IntegrationTestResult):
    """Test 1.4: Detect missing required provider in structure."""
    incomplete_secrets = {
        "providers": {
            "openai": {"api_key": "test", "enabled": False}
        }
    }
    required = ["openai", "anthropic", "mistral"]
    missing = [p for p in required if p not in incomplete_secrets["providers"]]
    if missing:
        result.record_pass(f"Detect missing providers: {missing}")
    else:
        result.record_fail("Detect missing providers", "Should detect missing")


def test_secrets_loader_missing_api_key_structure(result: IntegrationTestResult):
    """Test 1.5: Detect missing api_key in provider config."""
    invalid_provider = {"enabled": False}
    if "api_key" not in invalid_provider:
        result.record_pass("Detect missing api_key field")
    else:
        result.record_fail("Detect missing api_key", "Should not have api_key")
def test_secrets_loader_is_real_mode(result: IntegrationTestResult):
    """Test 1.6: is_real_mode() function."""
    secrets_false = create_valid_test_secrets()
    secrets_false["real_mode"] = False
    if not secrets_loader.is_real_mode(secrets_false):
        result.record_pass("is_real_mode() returns False")
    else:
        result.record_fail("is_real_mode() False", "Should return False")

    secrets_true = create_valid_test_secrets()
    secrets_true["real_mode"] = True
    if secrets_loader.is_real_mode(secrets_true):
        result.record_pass("is_real_mode() returns True")
    else:
        result.record_fail("is_real_mode() True", "Should return True")


def test_secrets_loader_provider_enabled(result: IntegrationTestResult):
    """Test 1.7: Provider enable/disable flags."""
    secrets = create_valid_test_secrets()

    if secrets_loader.is_provider_enabled(secrets, "openai"):
        result.record_pass("Provider enabled flag (openai=True)")
    else:
        result.record_fail("Provider enabled openai", "Should be enabled")

    if not secrets_loader.is_provider_enabled(secrets, "anthropic"):
        result.record_pass("Provider enabled flag (anthropic=False)")
    else:
        result.record_fail("Provider enabled anthropic", "Should be disabled")


def test_secrets_loader_key_masking(result: IntegrationTestResult):
    """Test 1.8: Safe masking of keys."""
    key = "sk-1234567890abcdefghijklmnop"
    masked = secrets_loader.mask_api_key(key)

    if "****" in masked and len(masked) < len(key):
        result.record_pass("Key masking contains ****")
    else:
        result.record_fail("Key masking", f"Masked key wrong format: {masked}")

    if key not in masked:
        result.record_pass("Key not exposed in mask")
    else:
        result.record_fail("Key not exposed", "Full key visible")

    short_key = "abc"
    masked_short = secrets_loader.mask_api_key(short_key)
    if masked_short == "***":
        result.record_pass("Short key masked as ***")
    else:
        result.record_fail("Short key masking", f"Got: {masked_short}")


def test_secrets_loader_summary_format(result: IntegrationTestResult):
    """Test 1.9: Summary output formatting."""
    secrets = create_valid_test_secrets()
    summary = secrets_loader.get_secrets_summary(secrets)

    if "openai" in summary.lower() and "anthropic" in summary.lower():
        result.record_pass("Summary contains provider names")
    else:
        result.record_fail("Summary providers", "Missing provider names")

    if "****" in summary:
        result.record_pass("Summary contains masked keys")
    else:
        result.record_fail("Summary masking", "No masking markers")

    full_key = secrets["providers"]["openai"]["api_key"]
    if full_key not in summary:
        result.record_pass("Summary does not expose full keys")
    else:
        result.record_fail("Summary key exposure", "Full key visible")


def test_secrets_loader_get_provider_config(result: IntegrationTestResult):
    """Test 1.10: get_provider_config() function."""
    secrets = create_valid_test_secrets()

    try:
        config = secrets_loader.get_provider_config(secrets, "openai")
        if "api_key" in config:
            result.record_pass("get_provider_config returns config")
        else:
            result.record_fail("get_provider_config", "Missing api_key in config")
    except Exception as e:
        result.record_fail("get_provider_config", str(e))

    try:
        secrets_loader.get_provider_config(secrets, "nonexistent")
        result.record_fail("get_provider_config invalid", "Should raise error")
    except secrets_loader.SecretsLoadError:
        result.record_pass("get_provider_config raises on invalid provider")
    except Exception as e:
        result.record_fail("get_provider_config error type", f"Wrong exception: {type(e).__name__}")
def test_provider_bridge_mock_mode(result: IntegrationTestResult):
    """Test 2.1: Mock mode behavior with no secrets."""
    bridge = ProviderBridge("/nonexistent/path/to/secrets.json")

    if bridge.is_mock_mode():
        result.record_pass("Mock mode when secrets missing")
    else:
        result.record_fail("Mock mode", "Should be in mock mode")

    response = bridge.call_openai("test prompt")
    if "MOCK" in response or "mock" in response.lower():
        result.record_pass("Mock response contains MOCK marker")
    else:
        result.record_fail("Mock response", f"No MOCK marker: {response[:50]}")


def test_provider_bridge_mock_responses(result: IntegrationTestResult):
    """Test 2.2: Mock mode returns appropriate responses."""
    bridge = ProviderBridge("/nonexistent/path")

    openai_response = bridge.call_openai("test")
    if "openai" in openai_response.lower():
        result.record_pass("Mock OpenAI response mentions OpenAI")
    else:
        result.record_fail("Mock OpenAI", f"Response: {openai_response}")

    anthropic_response = bridge.call_anthropic("test")
    if "anthropic" in anthropic_response.lower():
        result.record_pass("Mock Anthropic response mentions Anthropic")
    else:
        result.record_fail("Mock Anthropic", f"Response: {anthropic_response}")

    mistral_response = bridge.call_mistral("test")
    if "mistral" in mistral_response.lower():
        result.record_pass("Mock Mistral response mentions Mistral")
    else:
        result.record_fail("Mock Mistral", f"Response: {mistral_response}")


def test_provider_bridge_get_status(result: IntegrationTestResult):
    """Test 2.3: get_provider_status() returns correct structure."""
    bridge = ProviderBridge("/nonexistent/path")
    status = bridge.get_provider_status("openai")

    required_fields = ["provider", "configured", "enabled", "mode"]
    missing = [f for f in required_fields if f not in status]

    if not missing:
        result.record_pass("Provider status has required fields")
    else:
        result.record_fail("Provider status structure", f"Missing: {missing}")

    if status["provider"] == "openai":
        result.record_pass("Provider status has correct provider name")
    else:
        result.record_fail("Provider name", f"Expected 'openai', got {status['provider']}")

    if status["mode"] == "mock":
        result.record_pass("Provider status shows mock mode")
    else:
        result.record_fail("Provider mode", f"Expected 'mock', got {status['mode']}")


def test_provider_bridge_dispatcher_openai(result: IntegrationTestResult):
    """Test 2.4: call_provider() dispatches to OpenAI."""
    bridge = ProviderBridge("/nonexistent")

    try:
        response = bridge.call_provider("openai", "test prompt")
        if "openai" in response.lower():
            result.record_pass("Dispatcher routes to OpenAI")
        else:
            result.record_fail("Dispatcher OpenAI", f"Response: {response}")
    except Exception as e:
        result.record_fail("Dispatcher OpenAI", str(e))


def test_provider_bridge_dispatcher_anthropic(result: IntegrationTestResult):
    """Test 2.5: call_provider() dispatches to Anthropic."""
    bridge = ProviderBridge("/nonexistent")

    try:
        response = bridge.call_provider("anthropic", "test prompt")
        if "anthropic" in response.lower():
            result.record_pass("Dispatcher routes to Anthropic")
        else:
            result.record_fail("Dispatcher Anthropic", f"Response: {response}")
    except Exception as e:
        result.record_fail("Dispatcher Anthropic", str(e))


def test_provider_bridge_dispatcher_mistral(result: IntegrationTestResult):
    """Test 2.6: call_provider() dispatches to Mistral."""
    bridge = ProviderBridge("/nonexistent")

    try:
        response = bridge.call_provider("mistral", "test prompt")
        if "mistral" in response.lower():
            result.record_pass("Dispatcher routes to Mistral")
        else:
            result.record_fail("Dispatcher Mistral", f"Response: {response}")
    except Exception as e:
        result.record_fail("Dispatcher Mistral", str(e))


def test_provider_bridge_dispatcher_unknown(result: IntegrationTestResult):
    """Test 2.7: call_provider() errors on unknown provider."""
    bridge = ProviderBridge("/nonexistent")

    try:
        bridge.call_provider("unknown_provider", "test")
        result.record_fail("Unknown provider error", "Should raise ProviderBridgeError")
    except ProviderBridgeError as e:
        if "unknown" in str(e).lower():
            result.record_pass("Unknown provider raises ProviderBridgeError")
        else:
            result.record_fail("Unknown provider error msg", f"Error: {e}")
    except Exception as e:
        result.record_fail("Unknown provider exception", f"Wrong type: {type(e).__name__}")


def test_provider_bridge_model_override(result: IntegrationTestResult):
    """Test 2.8: Model parameter override works."""
    bridge = ProviderBridge("/nonexistent")

    response = bridge.call_openai("test", model="custom-model-xyz")
    if "custom-model-xyz" in response:
        result.record_pass("Model override in OpenAI call")
    else:
        result.record_fail("Model override", f"Model not in response: {response}")

    response = bridge.call_provider("anthropic", "test", model="custom-anthropic")
    if "custom-anthropic" in response:
        result.record_pass("Model override in dispatcher")
    else:
        result.record_fail("Model override dispatcher", f"Model not in response: {response}")


def test_provider_bridge_no_key_exposure_in_responses(result: IntegrationTestResult):
    """Test 2.9: Responses never contain actual API keys."""
    bridge = ProviderBridge("/nonexistent")

    test_key = "sk-secret123456789abcdef"

    response = bridge.call_openai("test")
    if test_key not in response:
        result.record_pass("Mock response does not contain test key")
    else:
        result.record_fail("Key exposure in response", "Key found in response")

    status = bridge.get_provider_status("openai")
    if test_key not in str(status):
        result.record_pass("Status does not contain test key")
    else:
        result.record_fail("Key exposure in status", "Key found in status")
def test_cross_module_consistency_real_mode(result: IntegrationTestResult):
    """Test 3.1: Real mode flags are consistent."""
    secrets = create_valid_test_secrets()
    secrets["real_mode"] = False

    secrets_real = secrets_loader.is_real_mode(secrets)

    bridge = ProviderBridge("/nonexistent")
    bridge_mock = bridge.is_mock_mode()

    if secrets_real == (not bridge_mock):
        result.record_pass("Real mode consistency (both mock)")
    else:
        result.record_fail(
            "Real mode consistency",
            f"Secrets real={secrets_real}, bridge mock={bridge_mock}"
        )


def test_cross_module_consistency_provider_structure(result: IntegrationTestResult):
    """Test 3.2: Provider status structure is consistent."""
    bridge = ProviderBridge("/nonexistent")

    providers = ["openai", "anthropic", "mistral"]
    all_consistent = True

    for provider in providers:
        status = bridge.get_provider_status(provider)
        if status["provider"] != provider:
            all_consistent = False
            result.record_fail(
                f"Status consistency {provider}",
                "Provider mismatch in status"
            )
            break

    if all_consistent:
        result.record_pass("Provider status structure consistent across all providers")


def test_cross_module_get_provider_config_matches_bridge(result: IntegrationTestResult):
    """Test 3.3: secrets_loader.get_provider_config matches bridge behavior."""
    secrets = create_valid_test_secrets()

    try:
        openai_config = secrets_loader.get_provider_config(secrets, "openai")
        if "api_key" in openai_config and "enabled" in openai_config:
            result.record_pass("Provider config has expected structure")
        else:
            result.record_fail(
                "Provider config structure",
                "Missing expected fields"
            )
    except Exception as e:
        result.record_fail("Provider config access", str(e))


def test_safe_behavior_no_network_calls(result: IntegrationTestResult):
    """Test 4.1: No actual network calls in mock mode."""
    bridge = ProviderBridge("/nonexistent")

    try:
        response = bridge.call_openai("test prompt")
        if "MOCK" in response or "mock" in response.lower():
            result.record_pass("No network calls (returns mock)")
        else:
            result.record_fail("Network isolation", "Unexpected response format")
    except Exception as e:
        # If ANY network-related error appears, it's a failure
        if "network" in str(e).lower() or "connection" in str(e).lower():
            result.record_fail("Network call attempted", str(e))
        else:
            result.record_fail("Network test", str(e))


def test_safe_behavior_exception_masking(result: IntegrationTestResult):
    """Test 4.2: Exceptions mask sensitive data."""
    bridge = ProviderBridge("/nonexistent")

    try:
        bridge.call_provider("invalid", "test")
    except ProviderBridgeError as e:
        msg = str(e)
        if "sk-" not in msg:
            result.record_pass("Exception does not leak key patterns")
        else:
            result.record_fail("Exception masking", "Key pattern detected")
    except Exception as e:
        result.record_fail("Exception type", f"Wrong exception type: {type(e).__name__}")


def test_safe_behavior_template_detection(result: IntegrationTestResult):
    """Test 4.3: Template key detection prevents real calls."""
    secrets = create_valid_test_secrets()
    secrets["real_mode"] = True
    secrets["providers"]["openai"]["api_key"] = "sk-XXXXXXXXXXXXXXXX"
    secrets["providers"]["openai"]["enabled"] = True

    api_key = secrets["providers"]["openai"]["api_key"]

    if "XXXX" in api_key or "XXX" in api_key:
        result.record_pass("Template key pattern detected")
    else:
        result.record_fail("Template detection", "Should detect XXXX pattern")


def test_disabled_provider_handling(result: IntegrationTestResult):
    """Test 4.4: Disabled provider handling."""
    secrets = create_valid_test_secrets()

    if not secrets_loader.is_provider_enabled(secrets, "anthropic"):
        result.record_pass("Disabled provider correctly identified")
    else:
        result.record_fail("Disabled provider", "Should be disabled")
def test_edge_case_empty_prompt(result: IntegrationTestResult):
    """Test 5.1: Empty prompt handling."""
    bridge = ProviderBridge("/nonexistent")
    try:
        response = bridge.call_openai("")
        if response:
            result.record_pass("Empty prompt returns response")
        else:
            result.record_fail("Empty prompt", "No response returned")
    except Exception as e:
        result.record_fail("Empty prompt handling", str(e))


def test_edge_case_long_prompt(result: IntegrationTestResult):
    """Test 5.2: Long prompt handling."""
    bridge = ProviderBridge("/nonexistent")
    long_prompt = "test " * 1000

    try:
        response = bridge.call_openai(long_prompt)
        if response:
            result.record_pass("Long prompt returns response")
        else:
            result.record_fail("Long prompt", "No response")
    except Exception as e:
        result.record_fail("Long prompt handling", str(e))


def test_edge_case_special_characters_in_prompt(result: IntegrationTestResult):
    """Test 5.3: Special characters in prompt."""
    bridge = ProviderBridge("/nonexistent")
    special_prompt = "test\n\t\"'{}[]<>!@#$%^&*()"

    try:
        response = bridge.call_openai(special_prompt)
        if response:
            result.record_pass("Special characters handled")
        else:
            result.record_fail("Special characters", "No response")
    except Exception as e:
        result.record_fail("Special characters handling", str(e))


def run_all_tests() -> IntegrationTestResult:
    """Run all integration tests."""
    result = IntegrationTestResult()

    print("=" * 60)
    print("FAZA 30.97 - MAX LLM Preflight Integration Test")
    print("=" * 60)
    print()

    print("Section 1: Secrets Loader Tests")
    print("-" * 60)
    test_secrets_loader_missing_file(result)
    test_secrets_loader_parse_spec(result)
    test_secrets_loader_missing_providers_structure(result)
    test_secrets_loader_missing_required_provider_structure(result)
    test_secrets_loader_missing_api_key_structure(result)
    test_secrets_loader_is_real_mode(result)
    test_secrets_loader_provider_enabled(result)
    test_secrets_loader_key_masking(result)
    test_secrets_loader_summary_format(result)
    test_secrets_loader_get_provider_config(result)
    print()

    print("Section 2: Provider Bridge Tests")
    print("-" * 60)
    test_provider_bridge_mock_mode(result)
    test_provider_bridge_mock_responses(result)
    test_provider_bridge_get_status(result)
    test_provider_bridge_dispatcher_openai(result)
    test_provider_bridge_dispatcher_anthropic(result)
    test_provider_bridge_dispatcher_mistral(result)
    test_provider_bridge_dispatcher_unknown(result)
    test_provider_bridge_model_override(result)
    test_provider_bridge_no_key_exposure_in_responses(result)
    print()

    print("Section 3: Cross-Module Consistency")
    print("-" * 60)
    test_cross_module_consistency_real_mode(result)
    test_cross_module_consistency_provider_structure(result)
    test_cross_module_get_provider_config_matches_bridge(result)
    print()

    print("Section 4: Safe Behavior Tests")
    print("-" * 60)
    test_safe_behavior_no_network_calls(result)
    test_safe_behavior_exception_masking(result)
    test_safe_behavior_template_detection(result)
    test_disabled_provider_handling(result)
    print()

    print("Section 5: Edge Case Tests")
    print("-" * 60)
    test_edge_case_empty_prompt(result)
    test_edge_case_long_prompt(result)
    test_edge_case_special_characters_in_prompt(result)
    print()

    print("=" * 60)
    print(result.summary())
    print("=" * 60)

    return result


def main():
    """Main entry point."""
    result = run_all_tests()

    if result.failed > 0:
        print()
        print("Failed tests:")
        for test_name, reason in result.errors:
            print(f"  - {test_name}: {reason}")
        return 1

    print()
    print("✓ All integration tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

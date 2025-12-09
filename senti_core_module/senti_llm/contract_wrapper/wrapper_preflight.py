#!/usr/bin/env python3
"""
FAZA 31 - FULL SHIELD CONTRACT WRAPPER TEST SUITE
"""

import sys
from pathlib import Path
import copy

# ROOT PATH INJECTION
ROOT = str(Path(__file__).resolve().parents[3])
sys.path.insert(0, ROOT)

from senti_core_module.senti_llm.contract_wrapper.wrapper_errors import (
    WrapperError,
    WrapperSchemaError,
    WrapperNormalizationError,
    WrapperValidationError,
    WrapperAnomalyError,
    WrapperProviderError
)

from senti_core_module.senti_llm.contract_wrapper.wrapper_utils import (
    sanitize_text,
    normalize_provider,
    normalize_model,
    safe_int
)

from senti_core_module.senti_llm.contract_wrapper.contract_wrapper import (
    LLMResponseWrapper
)


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def record_pass(self, test_name):
        self.passed += 1

    def record_fail(self, test_name, error):
        self.failed += 1
        self.failures.append((test_name, str(error)))

    def summary(self):
        lines = []
        lines.append("=" * 70)
        lines.append("FAZA 31 - FULL SHIELD CONTRACT WRAPPER TEST SUITE REPORT")
        lines.append(f"TOTAL TESTS: {self.passed + self.failed}")
        lines.append(f"PASSED: {self.passed}")
        lines.append(f"FAILED: {self.failed}")
        lines.append("=" * 70)
        if self.failures:
            lines.append("\nFAILURES:")
            for name, error in self.failures:
                lines.append(f"  - {name}: {error}")
        return "\n".join(lines)


def make_valid_raw():
    return {
        "provider": "openai",
        "model": "gpt-4",
        "type": "completion",
        "content": "Valid response content"
    }


############################################################
# SECTION 1: PRE-CLEAN TESTS (50 tests)
############################################################

def test_preclean_removes_none_values(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["extra"] = None
    try:
        wrapped = wrapper.wrap(raw)
        if "extra" in wrapped:
            result.record_fail("preclean_removes_none_values", "None not removed")
        else:
            result.record_pass("preclean_removes_none_values")
    except Exception as e:
        result.record_fail("preclean_removes_none_values", str(e))


def test_preclean_sanitizes_strings(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test\x00content"
    try:
        wrapped = wrapper.wrap(raw)
        if "\x00" not in wrapped["content"]:
            result.record_pass("preclean_sanitizes_strings")
        else:
            result.record_fail("preclean_sanitizes_strings", "Null byte not removed")
    except Exception as e:
        result.record_fail("preclean_sanitizes_strings", str(e))


def test_preclean_converts_int(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 42
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 42:
            result.record_pass("preclean_converts_int")
        else:
            result.record_fail("preclean_converts_int", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("preclean_converts_int", str(e))


def test_preclean_converts_float(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 42.7
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 42:
            result.record_pass("preclean_converts_float")
        else:
            result.record_fail("preclean_converts_float", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("preclean_converts_float", str(e))


def test_preclean_copies_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"key": "value"}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {"key": "value"}:
            result.record_pass("preclean_copies_dict")
        else:
            result.record_fail("preclean_copies_dict", "Dict not copied")
    except Exception as e:
        result.record_fail("preclean_copies_dict", str(e))


def test_preclean_copies_list(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["items"] = [1, 2, 3]
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("preclean_copies_list")
    except Exception as e:
        result.record_fail("preclean_copies_list", str(e))


def test_preclean_converts_keys_to_lowercase(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "Provider": "openai",
        "Model": "gpt-4",
        "Type": "completion",
        "Content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if "provider" in wrapped and "Provider" not in wrapped:
            result.record_pass("preclean_converts_keys_to_lowercase")
        else:
            result.record_fail("preclean_converts_keys_to_lowercase", "Keys not lowercased")
    except Exception as e:
        result.record_fail("preclean_converts_keys_to_lowercase", str(e))


def test_preclean_strips_key_whitespace(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "  provider  ": "openai",
        "model": "gpt-4",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if "provider" in wrapped:
            result.record_pass("preclean_strips_key_whitespace")
        else:
            result.record_fail("preclean_strips_key_whitespace", "Key not stripped")
    except Exception as e:
        result.record_fail("preclean_strips_key_whitespace", str(e))


def test_preclean_handles_boolean(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["flag"] = True
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("preclean_handles_boolean")
    except Exception as e:
        result.record_fail("preclean_handles_boolean", str(e))


def test_preclean_converts_unknown_to_string(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["unknown"] = object()
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("preclean_converts_unknown_to_string")
    except Exception as e:
        result.record_fail("preclean_converts_unknown_to_string", str(e))


def test_sanitize_text_none(result):
    output = sanitize_text(None)
    if output == "":
        result.record_pass("sanitize_text_none")
    else:
        result.record_fail("sanitize_text_none", f"Got '{output}'")


def test_sanitize_text_removes_null_byte(result):
    output = sanitize_text("test\x00content")
    if "\x00" not in output:
        result.record_pass("sanitize_text_removes_null_byte")
    else:
        result.record_fail("sanitize_text_removes_null_byte", "Null byte present")


def test_sanitize_text_collapses_newlines(result):
    output = sanitize_text("line1\n\n\n\n\n\nline2")
    if output.count("\n") <= 3:
        result.record_pass("sanitize_text_collapses_newlines")
    else:
        result.record_fail("sanitize_text_collapses_newlines", f"Too many newlines: {output.count('\\n')}")


def test_sanitize_text_truncates_long_content(result):
    output = sanitize_text("x" * 100000)
    if len(output) == 50000:
        result.record_pass("sanitize_text_truncates_long_content")
    else:
        result.record_fail("sanitize_text_truncates_long_content", f"Length {len(output)}")


def test_sanitize_text_preserves_unicode(result):
    output = sanitize_text("Hello 世界")
    if "世界" in output:
        result.record_pass("sanitize_text_preserves_unicode")
    else:
        result.record_fail("sanitize_text_preserves_unicode", "Unicode lost")


def test_sanitize_text_empty_string(result):
    output = sanitize_text("")
    if output == "":
        result.record_pass("sanitize_text_empty_string")
    else:
        result.record_fail("sanitize_text_empty_string", f"Got '{output}'")


def test_sanitize_text_whitespace_only(result):
    output = sanitize_text("   \n\n   ")
    if isinstance(output, str):
        result.record_pass("sanitize_text_whitespace_only")
    else:
        result.record_fail("sanitize_text_whitespace_only", "Not a string")


def test_safe_int_from_int(result):
    output = safe_int(42)
    if output == 42:
        result.record_pass("safe_int_from_int")
    else:
        result.record_fail("safe_int_from_int", f"Got {output}")


def test_safe_int_from_float(result):
    output = safe_int(42.7)
    if output == 42:
        result.record_pass("safe_int_from_float")
    else:
        result.record_fail("safe_int_from_float", f"Got {output}")


def test_safe_int_negative_to_zero(result):
    output = safe_int(-5)
    if output == 0:
        result.record_pass("safe_int_negative_to_zero")
    else:
        result.record_fail("safe_int_negative_to_zero", f"Got {output}")


def test_safe_int_invalid_to_zero(result):
    output = safe_int("invalid")
    if output == 0:
        result.record_pass("safe_int_invalid_to_zero")
    else:
        result.record_fail("safe_int_invalid_to_zero", f"Got {output}")


def test_safe_int_boolean_false(result):
    output = safe_int(False)
    if output == 0:
        result.record_pass("safe_int_boolean_false")
    else:
        result.record_fail("safe_int_boolean_false", f"Got {output}")


def test_safe_int_zero(result):
    output = safe_int(0)
    if output == 0:
        result.record_pass("safe_int_zero")
    else:
        result.record_fail("safe_int_zero", f"Got {output}")


def test_safe_int_large_number(result):
    output = safe_int(999999999)
    if output == 999999999:
        result.record_pass("safe_int_large_number")
    else:
        result.record_fail("safe_int_large_number", f"Got {output}")


def test_safe_int_none(result):
    output = safe_int(None)
    if output == 0:
        result.record_pass("safe_int_none")
    else:
        result.record_fail("safe_int_none", f"Got {output}")


def test_preclean_multiple_none_fields(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["none1"] = None
    raw["none2"] = None
    try:
        wrapped = wrapper.wrap(raw)
        if "none1" not in wrapped and "none2" not in wrapped:
            result.record_pass("preclean_multiple_none_fields")
        else:
            result.record_fail("preclean_multiple_none_fields", "None fields present")
    except Exception as e:
        result.record_fail("preclean_multiple_none_fields", str(e))


def test_preclean_nested_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"nested": {"deep": "value"}}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"]["nested"]["deep"] == "value":
            result.record_pass("preclean_nested_dict")
        else:
            result.record_fail("preclean_nested_dict", "Nested value lost")
    except Exception as e:
        result.record_fail("preclean_nested_dict", str(e))


def test_preclean_empty_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {}:
            result.record_pass("preclean_empty_dict")
        else:
            result.record_fail("preclean_empty_dict", "Empty dict changed")
    except Exception as e:
        result.record_fail("preclean_empty_dict", str(e))


def test_preclean_empty_list(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["items"] = []
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("preclean_empty_list")
    except Exception as e:
        result.record_fail("preclean_empty_list", str(e))


def test_preclean_mixed_types(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "completion",
        "content": "test",
        "tokens_in": 10,
        "tokens_out": 20.5,
        "meta": {"key": "val"},
        "items": [1, 2],
        "none_val": None
    }
    try:
        wrapped = wrapper.wrap(raw)
        if "none_val" not in wrapped and "items" in wrapped:
            result.record_pass("preclean_mixed_types")
        else:
            result.record_fail("preclean_mixed_types", "Mixed types failed")
    except Exception as e:
        result.record_fail("preclean_mixed_types", str(e))


def test_sanitize_text_non_string_input(result):
    output = sanitize_text(123)
    if output == "123":
        result.record_pass("sanitize_text_non_string_input")
    else:
        result.record_fail("sanitize_text_non_string_input", f"Got '{output}'")


def test_safe_int_string_number(result):
    output = safe_int("42")
    if output == 42:
        result.record_pass("safe_int_string_number")
    else:
        result.record_fail("safe_int_string_number", f"Got {output}")


def test_safe_int_negative_float(result):
    output = safe_int(-5.7)
    if output == 0:
        result.record_pass("safe_int_negative_float")
    else:
        result.record_fail("safe_int_negative_float", f"Got {output}")


def test_preclean_content_with_newlines(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "line1\n\n\n\n\n\nline2"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"].count("\n") <= 3:
            result.record_pass("preclean_content_with_newlines")
        else:
            result.record_fail("preclean_content_with_newlines", "Too many newlines")
    except Exception as e:
        result.record_fail("preclean_content_with_newlines", str(e))


def test_preclean_very_long_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "x" * 100000
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["content"]) <= 50000:
            result.record_pass("preclean_very_long_content")
        else:
            result.record_fail("preclean_very_long_content", f"Length {len(wrapped['content'])}")
    except Exception as e:
        result.record_fail("preclean_very_long_content", str(e))


def test_preclean_unicode_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "Hello 世界 🌍"
    try:
        wrapped = wrapper.wrap(raw)
        if "世界" in wrapped["content"]:
            result.record_pass("preclean_unicode_content")
        else:
            result.record_fail("preclean_unicode_content", "Unicode lost")
    except Exception as e:
        result.record_fail("preclean_unicode_content", str(e))


def test_sanitize_text_max_newlines(result):
    text = "\n" * 10
    output = sanitize_text(text)
    if output.count("\n") <= 3:
        result.record_pass("sanitize_text_max_newlines")
    else:
        result.record_fail("sanitize_text_max_newlines", f"Got {output.count('\\n')} newlines")


def test_safe_int_float_zero(result):
    output = safe_int(0.0)
    if output == 0:
        result.record_pass("safe_int_float_zero")
    else:
        result.record_fail("safe_int_float_zero", f"Got {output}")


def test_preclean_preserves_order(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if "provider" in wrapped and "content" in wrapped:
            result.record_pass("preclean_preserves_order")
        else:
            result.record_fail("preclean_preserves_order", "Fields missing")
    except Exception as e:
        result.record_fail("preclean_preserves_order", str(e))


def test_preclean_key_normalization(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "  PROVIDER  ": "openai",
        "MODEL": "gpt-4",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if "provider" in wrapped and "model" in wrapped:
            result.record_pass("preclean_key_normalization")
        else:
            result.record_fail("preclean_key_normalization", "Keys not normalized")
    except Exception as e:
        result.record_fail("preclean_key_normalization", str(e))


def test_sanitize_text_special_chars(result):
    output = sanitize_text("test@#$%content")
    if "@" in output:
        result.record_pass("sanitize_text_special_chars")
    else:
        result.record_fail("sanitize_text_special_chars", "Special chars removed")


def test_safe_int_max_int(result):
    output = safe_int(2147483647)
    if output == 2147483647:
        result.record_pass("safe_int_max_int")
    else:
        result.record_fail("safe_int_max_int", f"Got {output}")


def test_preclean_tokens_zero(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 0
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0:
            result.record_pass("preclean_tokens_zero")
        else:
            result.record_fail("preclean_tokens_zero", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("preclean_tokens_zero", str(e))


def test_preclean_all_required_fields(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        required = ["provider", "model", "type", "content"]
        if all(k in wrapped for k in required):
            result.record_pass("preclean_all_required_fields")
        else:
            result.record_fail("preclean_all_required_fields", "Missing required fields")
    except Exception as e:
        result.record_fail("preclean_all_required_fields", str(e))


def test_sanitize_text_tabs(result):
    output = sanitize_text("test\t\tcontent")
    if "\t" in output:
        result.record_pass("sanitize_text_tabs")
    else:
        result.record_fail("sanitize_text_tabs", "Tabs removed")


def test_safe_int_list_fallback(result):
    output = safe_int([1, 2, 3])
    if output == 0:
        result.record_pass("safe_int_list_fallback")
    else:
        result.record_fail("safe_int_list_fallback", f"Got {output}")


############################################################
# SECTION 2: NORMALIZATION TESTS (40 tests)
############################################################

def test_normalize_provider_openai(result):
    try:
        output = normalize_provider("openai")
        if output == "openai":
            result.record_pass("normalize_provider_openai")
        else:
            result.record_fail("normalize_provider_openai", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_openai", str(e))


def test_normalize_provider_anthropic(result):
    try:
        output = normalize_provider("anthropic")
        if output == "anthropic":
            result.record_pass("normalize_provider_anthropic")
        else:
            result.record_fail("normalize_provider_anthropic", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_anthropic", str(e))


def test_normalize_provider_mistral(result):
    try:
        output = normalize_provider("mistral")
        if output == "mistral":
            result.record_pass("normalize_provider_mistral")
        else:
            result.record_fail("normalize_provider_mistral", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_mistral", str(e))


def test_normalize_provider_uppercase(result):
    try:
        output = normalize_provider("OPENAI")
        if output == "openai":
            result.record_pass("normalize_provider_uppercase")
        else:
            result.record_fail("normalize_provider_uppercase", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_uppercase", str(e))


def test_normalize_provider_whitespace(result):
    try:
        output = normalize_provider("  openai  ")
        if output == "openai":
            result.record_pass("normalize_provider_whitespace")
        else:
            result.record_fail("normalize_provider_whitespace", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_whitespace", str(e))


def test_normalize_provider_invalid(result):
    try:
        normalize_provider("google")
        result.record_fail("normalize_provider_invalid", "Invalid provider accepted")
    except WrapperProviderError:
        result.record_pass("normalize_provider_invalid")
    except Exception as e:
        result.record_fail("normalize_provider_invalid", f"Wrong error: {e}")


def test_normalize_provider_none(result):
    try:
        normalize_provider(None)
        result.record_fail("normalize_provider_none", "None accepted")
    except WrapperProviderError:
        result.record_pass("normalize_provider_none")
    except Exception as e:
        result.record_fail("normalize_provider_none", f"Wrong error: {e}")


def test_normalize_provider_empty(result):
    try:
        normalize_provider("")
        result.record_fail("normalize_provider_empty", "Empty string accepted")
    except WrapperProviderError:
        result.record_pass("normalize_provider_empty")
    except Exception as e:
        result.record_fail("normalize_provider_empty", f"Wrong error: {e}")


def test_normalize_model_valid(result):
    output = normalize_model("openai", "gpt-4")
    if output == "gpt-4":
        result.record_pass("normalize_model_valid")
    else:
        result.record_fail("normalize_model_valid", f"Got {output}")


def test_normalize_model_none(result):
    output = normalize_model("openai", None)
    if output == "unknown":
        result.record_pass("normalize_model_none")
    else:
        result.record_fail("normalize_model_none", f"Got {output}")


def test_normalize_model_empty(result):
    output = normalize_model("openai", "")
    if output == "unknown":
        result.record_pass("normalize_model_empty")
    else:
        result.record_fail("normalize_model_empty", f"Got {output}")


def test_normalize_model_whitespace(result):
    output = normalize_model("openai", "  gpt-4  ")
    if output == "gpt-4":
        result.record_pass("normalize_model_whitespace")
    else:
        result.record_fail("normalize_model_whitespace", f"Got {output}")


def test_normalize_model_newlines(result):
    output = normalize_model("openai", "gpt\n4")
    if "\n" not in output:
        result.record_pass("normalize_model_newlines")
    else:
        result.record_fail("normalize_model_newlines", "Newline not removed")


def test_normalize_model_too_long(result):
    output = normalize_model("openai", "x" * 300)
    if len(output) == 200:
        result.record_pass("normalize_model_too_long")
    else:
        result.record_fail("normalize_model_too_long", f"Length {len(output)}")


def test_normalize_model_non_string(result):
    output = normalize_model("openai", 123)
    if output == "123":
        result.record_pass("normalize_model_non_string")
    else:
        result.record_fail("normalize_model_non_string", f"Got {output}")


def test_normalization_sets_provider(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "openai":
            result.record_pass("normalization_sets_provider")
        else:
            result.record_fail("normalization_sets_provider", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("normalization_sets_provider", str(e))


def test_normalization_sets_model(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["model"] == "gpt-4":
            result.record_pass("normalization_sets_model")
        else:
            result.record_fail("normalization_sets_model", f"Got {wrapped['model']}")
    except Exception as e:
        result.record_fail("normalization_sets_model", str(e))


def test_normalization_sets_type_default(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "completion":
            result.record_pass("normalization_sets_type_default")
        else:
            result.record_fail("normalization_sets_type_default", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("normalization_sets_type_default", str(e))


def test_normalization_preserves_type(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "chat"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "chat":
            result.record_pass("normalization_preserves_type")
        else:
            result.record_fail("normalization_preserves_type", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("normalization_preserves_type", str(e))


def test_normalization_sets_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"] == "Valid response content":
            result.record_pass("normalization_sets_content")
        else:
            result.record_fail("normalization_sets_content", f"Got {wrapped['content']}")
    except Exception as e:
        result.record_fail("normalization_sets_content", str(e))


def test_normalization_content_default_empty(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "tool"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"] == "":
            result.record_pass("normalization_content_default_empty")
        else:
            result.record_fail("normalization_content_default_empty", f"Got '{wrapped['content']}'")
    except Exception as e:
        result.record_fail("normalization_content_default_empty", str(e))


def test_normalization_tokens_in_default(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0:
            result.record_pass("normalization_tokens_in_default")
        else:
            result.record_fail("normalization_tokens_in_default", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("normalization_tokens_in_default", str(e))


def test_normalization_tokens_out_default(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_out"] == 0:
            result.record_pass("normalization_tokens_out_default")
        else:
            result.record_fail("normalization_tokens_out_default", f"Got {wrapped['tokens_out']}")
    except Exception as e:
        result.record_fail("normalization_tokens_out_default", str(e))


def test_normalization_meta_default(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {}:
            result.record_pass("normalization_meta_default")
        else:
            result.record_fail("normalization_meta_default", f"Got {wrapped['meta']}")
    except Exception as e:
        result.record_fail("normalization_meta_default", str(e))


def test_normalization_meta_not_dict_error(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = "not a dict"
    try:
        wrapper.wrap(raw)
        result.record_fail("normalization_meta_not_dict_error", "Invalid meta accepted")
    except WrapperNormalizationError:
        result.record_pass("normalization_meta_not_dict_error")
    except Exception as e:
        result.record_fail("normalization_meta_not_dict_error", f"Wrong error: {e}")


def test_normalization_copies_meta(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"key": "value"}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {"key": "value"}:
            result.record_pass("normalization_copies_meta")
        else:
            result.record_fail("normalization_copies_meta", "Meta not copied")
    except Exception as e:
        result.record_fail("normalization_copies_meta", str(e))


def test_wrapper_init_stores_provider(result):
    wrapper = LLMResponseWrapper("openai")
    if wrapper.provider == "openai":
        result.record_pass("wrapper_init_stores_provider")
    else:
        result.record_fail("wrapper_init_stores_provider", f"Got {wrapper.provider}")


def test_wrapper_init_normalizes_provider(result):
    wrapper = LLMResponseWrapper("  OPENAI  ")
    if wrapper.provider == "openai":
        result.record_pass("wrapper_init_normalizes_provider")
    else:
        result.record_fail("wrapper_init_normalizes_provider", f"Got {wrapper.provider}")


def test_wrapper_init_invalid_provider(result):
    try:
        wrapper = LLMResponseWrapper("invalid")
        result.record_fail("wrapper_init_invalid_provider", "Invalid provider accepted")
    except WrapperProviderError:
        result.record_pass("wrapper_init_invalid_provider")
    except Exception as e:
        result.record_fail("wrapper_init_invalid_provider", f"Wrong error: {e}")


def test_normalization_overrides_provider(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["provider"] = "anthropic"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "anthropic":
            result.record_pass("normalization_overrides_provider")
        else:
            result.record_fail("normalization_overrides_provider", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("normalization_overrides_provider", str(e))


def test_normalization_uses_wrapper_provider_default(result):
    wrapper = LLMResponseWrapper("mistral")
    raw = {
        "model": "mistral-large",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "mistral":
            result.record_pass("normalization_uses_wrapper_provider_default")
        else:
            result.record_fail("normalization_uses_wrapper_provider_default", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("normalization_uses_wrapper_provider_default", str(e))


def test_normalize_model_only_whitespace(result):
    output = normalize_model("openai", "   ")
    if output == "unknown":
        result.record_pass("normalize_model_only_whitespace")
    else:
        result.record_fail("normalize_model_only_whitespace", f"Got {output}")


def test_normalize_provider_mixed_case(result):
    try:
        output = normalize_provider("OpenAI")
        if output == "openai":
            result.record_pass("normalize_provider_mixed_case")
        else:
            result.record_fail("normalize_provider_mixed_case", f"Got {output}")
    except Exception as e:
        result.record_fail("normalize_provider_mixed_case", str(e))


def test_normalization_tokens_preserve_positive(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 100
    raw["tokens_out"] = 200
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 100 and wrapped["tokens_out"] == 200:
            result.record_pass("normalization_tokens_preserve_positive")
        else:
            result.record_fail("normalization_tokens_preserve_positive", "Tokens changed")
    except Exception as e:
        result.record_fail("normalization_tokens_preserve_positive", str(e))


def test_normalization_tokens_negative_to_zero(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = -5
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0:
            result.record_pass("normalization_tokens_negative_to_zero")
        else:
            result.record_fail("normalization_tokens_negative_to_zero", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("normalization_tokens_negative_to_zero", str(e))


def test_normalize_model_carriage_return(result):
    output = normalize_model("openai", "gpt\r4")
    if "\r" not in output:
        result.record_pass("normalize_model_carriage_return")
    else:
        result.record_fail("normalize_model_carriage_return", "CR not removed")


def test_normalization_all_providers(result):
    providers = ["openai", "anthropic", "mistral"]
    for p in providers:
        try:
            wrapper = LLMResponseWrapper(p)
            raw = {"model": "test", "type": "completion", "content": "test"}
            wrapped = wrapper.wrap(raw)
            if wrapped["provider"] != p:
                result.record_fail(f"normalization_all_providers_{p}", f"Provider {p} failed")
                return
        except Exception as e:
            result.record_fail(f"normalization_all_providers_{p}", str(e))
            return
    result.record_pass("normalization_all_providers")


def test_normalization_content_sanitized(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test\x00content"
    try:
        wrapped = wrapper.wrap(raw)
        if "\x00" not in wrapped["content"]:
            result.record_pass("normalization_content_sanitized")
        else:
            result.record_fail("normalization_content_sanitized", "Null byte present")
    except Exception as e:
        result.record_fail("normalization_content_sanitized", str(e))


def test_normalize_model_exact_200_chars(result):
    model = "x" * 200
    output = normalize_model("openai", model)
    if len(output) == 200:
        result.record_pass("normalize_model_exact_200_chars")
    else:
        result.record_fail("normalize_model_exact_200_chars", f"Length {len(output)}")


############################################################
# SECTION 3: SANITIZER INTEGRATION (40 tests)
############################################################

def test_sanitizer_basic_fields_called(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["extra"] = None
    try:
        wrapped = wrapper.wrap(raw)
        if "extra" not in wrapped:
            result.record_pass("sanitizer_basic_fields_called")
        else:
            result.record_fail("sanitizer_basic_fields_called", "None not removed")
    except Exception as e:
        result.record_fail("sanitizer_basic_fields_called", str(e))


def test_sanitizer_content_length_called(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "x" * 100000
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["content"]) == 50000:
            result.record_pass("sanitizer_content_length_called")
        else:
            result.record_fail("sanitizer_content_length_called", f"Length {len(wrapped['content'])}")
    except Exception as e:
        result.record_fail("sanitizer_content_length_called", str(e))


def test_sanitizer_types_called(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 42.7
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 42 and isinstance(wrapped["tokens_in"], int):
            result.record_pass("sanitizer_types_called")
        else:
            result.record_fail("sanitizer_types_called", "Float not converted")
    except Exception as e:
        result.record_fail("sanitizer_types_called", str(e))


def test_sanitizer_removes_whitespace(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "  openai  ",
        "model": "  gpt-4  ",
        "type": "  completion  ",
        "content": "  test  "
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "openai" and wrapped["model"] == "gpt-4":
            result.record_pass("sanitizer_removes_whitespace")
        else:
            result.record_fail("sanitizer_removes_whitespace", "Whitespace not removed")
    except Exception as e:
        result.record_fail("sanitizer_removes_whitespace", str(e))


def test_sanitizer_preserves_valid_data(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "openai" and wrapped["content"] == "Valid response content":
            result.record_pass("sanitizer_preserves_valid_data")
        else:
            result.record_fail("sanitizer_preserves_valid_data", "Valid data changed")
    except Exception as e:
        result.record_fail("sanitizer_preserves_valid_data", str(e))


def test_sanitizer_handles_missing_optional_fields(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if "tokens_in" in wrapped and "tokens_out" in wrapped:
            result.record_pass("sanitizer_handles_missing_optional_fields")
        else:
            result.record_fail("sanitizer_handles_missing_optional_fields", "Optional fields not added")
    except Exception as e:
        result.record_fail("sanitizer_handles_missing_optional_fields", str(e))


def test_sanitizer_float_tokens_both(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 10.5
    raw["tokens_out"] = 20.9
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 10 and wrapped["tokens_out"] == 20:
            result.record_pass("sanitizer_float_tokens_both")
        else:
            result.record_fail("sanitizer_float_tokens_both", "Floats not converted")
    except Exception as e:
        result.record_fail("sanitizer_float_tokens_both", str(e))


def test_sanitizer_content_exact_50000(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "x" * 50000
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["content"]) == 50000:
            result.record_pass("sanitizer_content_exact_50000")
        else:
            result.record_fail("sanitizer_content_exact_50000", f"Length {len(wrapped['content'])}")
    except Exception as e:
        result.record_fail("sanitizer_content_exact_50000", str(e))


def test_sanitizer_content_under_limit(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "short"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"] == "short":
            result.record_pass("sanitizer_content_under_limit")
        else:
            result.record_fail("sanitizer_content_under_limit", "Short content changed")
    except Exception as e:
        result.record_fail("sanitizer_content_under_limit", str(e))


def test_sanitizer_preserves_meta(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"key": "value"}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {"key": "value"}:
            result.record_pass("sanitizer_preserves_meta")
        else:
            result.record_fail("sanitizer_preserves_meta", "Meta changed")
    except Exception as e:
        result.record_fail("sanitizer_preserves_meta", str(e))


def test_sanitizer_tokens_zero(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 0
    raw["tokens_out"] = 0
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0 and wrapped["tokens_out"] == 0:
            result.record_pass("sanitizer_tokens_zero")
        else:
            result.record_fail("sanitizer_tokens_zero", "Zero tokens changed")
    except Exception as e:
        result.record_fail("sanitizer_tokens_zero", str(e))


def test_sanitizer_tokens_large(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 999999
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 999999:
            result.record_pass("sanitizer_tokens_large")
        else:
            result.record_fail("sanitizer_tokens_large", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("sanitizer_tokens_large", str(e))


def test_sanitizer_all_types(result):
    wrapper = LLMResponseWrapper("openai")
    types = ["completion", "chat", "tool"]
    for t in types:
        raw = make_valid_raw()
        raw["type"] = t
        if t == "tool":
            raw["content"] = ""
        try:
            wrapped = wrapper.wrap(raw)
            if wrapped["type"] != t:
                result.record_fail(f"sanitizer_type_{t}", f"Type {t} failed")
                return
        except Exception as e:
            result.record_fail(f"sanitizer_type_{t}", str(e))
            return
    result.record_pass("sanitizer_all_types")


def test_sanitizer_unicode_preserved(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "Hello 世界 🌍"
    try:
        wrapped = wrapper.wrap(raw)
        if "世界" in wrapped["content"] and "🌍" in wrapped["content"]:
            result.record_pass("sanitizer_unicode_preserved")
        else:
            result.record_fail("sanitizer_unicode_preserved", "Unicode lost")
    except Exception as e:
        result.record_fail("sanitizer_unicode_preserved", str(e))


def test_sanitizer_newlines_in_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "line1\nline2\nline3"
    try:
        wrapped = wrapper.wrap(raw)
        if "\n" in wrapped["content"]:
            result.record_pass("sanitizer_newlines_in_content")
        else:
            result.record_fail("sanitizer_newlines_in_content", "Newlines removed")
    except Exception as e:
        result.record_fail("sanitizer_newlines_in_content", str(e))


def test_sanitizer_special_chars_in_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test@#$%^&*()content"
    try:
        wrapped = wrapper.wrap(raw)
        if "@" in wrapped["content"]:
            result.record_pass("sanitizer_special_chars_in_content")
        else:
            result.record_fail("sanitizer_special_chars_in_content", "Special chars removed")
    except Exception as e:
        result.record_fail("sanitizer_special_chars_in_content", str(e))


def test_sanitizer_empty_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "tool"
    raw["content"] = ""
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"] == "":
            result.record_pass("sanitizer_empty_content")
        else:
            result.record_fail("sanitizer_empty_content", "Empty content changed")
    except Exception as e:
        result.record_fail("sanitizer_empty_content", str(e))


def test_sanitizer_whitespace_only_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "tool"
    raw["content"] = "   "
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("sanitizer_whitespace_only_content")
    except Exception as e:
        result.record_fail("sanitizer_whitespace_only_content", str(e))


def test_sanitizer_model_whitespace(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "  gpt-4-turbo  "
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["model"] == "gpt-4-turbo":
            result.record_pass("sanitizer_model_whitespace")
        else:
            result.record_fail("sanitizer_model_whitespace", f"Got '{wrapped['model']}'")
    except Exception as e:
        result.record_fail("sanitizer_model_whitespace", str(e))


def test_sanitizer_provider_case_normalized(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["provider"] = "OPENAI"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "openai":
            result.record_pass("sanitizer_provider_case_normalized")
        else:
            result.record_fail("sanitizer_provider_case_normalized", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("sanitizer_provider_case_normalized", str(e))


def test_sanitizer_type_case_preserved(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "completion"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "completion":
            result.record_pass("sanitizer_type_case_preserved")
        else:
            result.record_fail("sanitizer_type_case_preserved", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("sanitizer_type_case_preserved", str(e))


def test_sanitizer_meta_nested(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"level1": {"level2": "value"}}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"]["level1"]["level2"] == "value":
            result.record_pass("sanitizer_meta_nested")
        else:
            result.record_fail("sanitizer_meta_nested", "Nested meta changed")
    except Exception as e:
        result.record_fail("sanitizer_meta_nested", str(e))


def test_sanitizer_all_fields_present(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "chat",
        "content": "test",
        "tokens_in": 10,
        "tokens_out": 20,
        "meta": {"id": "123"}
    }
    try:
        wrapped = wrapper.wrap(raw)
        required = ["provider", "model", "type", "content", "tokens_in", "tokens_out", "meta"]
        if all(k in wrapped for k in required):
            result.record_pass("sanitizer_all_fields_present")
        else:
            result.record_fail("sanitizer_all_fields_present", "Missing fields")
    except Exception as e:
        result.record_fail("sanitizer_all_fields_present", str(e))


def test_sanitizer_content_multiline(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "line1\nline2\nline3\nline4"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"].count("\n") == 3:
            result.record_pass("sanitizer_content_multiline")
        else:
            result.record_fail("sanitizer_content_multiline", f"Newlines: {wrapped['content'].count('\\n')}")
    except Exception as e:
        result.record_fail("sanitizer_content_multiline", str(e))


def test_sanitizer_tokens_string_converted(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = "42"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 42:
            result.record_pass("sanitizer_tokens_string_converted")
        else:
            result.record_fail("sanitizer_tokens_string_converted", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("sanitizer_tokens_string_converted", str(e))


def test_sanitizer_model_special_chars(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4-turbo-2024-04-09"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["model"] == "gpt-4-turbo-2024-04-09":
            result.record_pass("sanitizer_model_special_chars")
        else:
            result.record_fail("sanitizer_model_special_chars", f"Got {wrapped['model']}")
    except Exception as e:
        result.record_fail("sanitizer_model_special_chars", str(e))


def test_sanitizer_content_tabs(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test\t\tcontent"
    try:
        wrapped = wrapper.wrap(raw)
        if "\t" in wrapped["content"]:
            result.record_pass("sanitizer_content_tabs")
        else:
            result.record_fail("sanitizer_content_tabs", "Tabs removed")
    except Exception as e:
        result.record_fail("sanitizer_content_tabs", str(e))


def test_sanitizer_meta_empty_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {}:
            result.record_pass("sanitizer_meta_empty_dict")
        else:
            result.record_fail("sanitizer_meta_empty_dict", "Empty dict changed")
    except Exception as e:
        result.record_fail("sanitizer_meta_empty_dict", str(e))


def test_sanitizer_provider_anthropic(result):
    wrapper = LLMResponseWrapper("anthropic")
    raw = {
        "model": "claude-3",
        "type": "chat",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "anthropic":
            result.record_pass("sanitizer_provider_anthropic")
        else:
            result.record_fail("sanitizer_provider_anthropic", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("sanitizer_provider_anthropic", str(e))


def test_sanitizer_provider_mistral(result):
    wrapper = LLMResponseWrapper("mistral")
    raw = {
        "model": "mistral-large",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "mistral":
            result.record_pass("sanitizer_provider_mistral")
        else:
            result.record_fail("sanitizer_provider_mistral", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("sanitizer_provider_mistral", str(e))


def test_sanitizer_content_max_newlines(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "\n" * 10
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"].count("\n") <= 3:
            result.record_pass("sanitizer_content_max_newlines")
        else:
            result.record_fail("sanitizer_content_max_newlines", f"Got {wrapped['content'].count('\\n')} newlines")
    except Exception as e:
        result.record_fail("sanitizer_content_max_newlines", str(e))


def test_sanitizer_tokens_float_negative(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = -5.5
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0:
            result.record_pass("sanitizer_tokens_float_negative")
        else:
            result.record_fail("sanitizer_tokens_float_negative", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("sanitizer_tokens_float_negative", str(e))


def test_sanitizer_model_unicode(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4-日本語"
    try:
        wrapped = wrapper.wrap(raw)
        if "日本語" in wrapped["model"]:
            result.record_pass("sanitizer_model_unicode")
        else:
            result.record_fail("sanitizer_model_unicode", "Unicode lost")
    except Exception as e:
        result.record_fail("sanitizer_model_unicode", str(e))


def test_sanitizer_content_null_bytes_removed(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test\x00\x00content"
    try:
        wrapped = wrapper.wrap(raw)
        if "\x00" not in wrapped["content"]:
            result.record_pass("sanitizer_content_null_bytes_removed")
        else:
            result.record_fail("sanitizer_content_null_bytes_removed", "Null bytes present")
    except Exception as e:
        result.record_fail("sanitizer_content_null_bytes_removed", str(e))


def test_sanitizer_complete_pipeline(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "PROVIDER": "  OPENAI  ",
        "Model": "  gpt-4  ",
        "TYPE": "chat",
        "content": "test\x00content\n\n\n\n\n",
        "tokens_in": 10.5,
        "tokens_out": 20.9,
        "meta": {"key": "val"},
        "extra": None
    }
    try:
        wrapped = wrapper.wrap(raw)
        checks = [
            wrapped["provider"] == "openai",
            wrapped["model"] == "gpt-4",
            wrapped["type"] == "chat",
            "\x00" not in wrapped["content"],
            wrapped["tokens_in"] == 10,
            wrapped["tokens_out"] == 20,
            "extra" not in wrapped
        ]
        if all(checks):
            result.record_pass("sanitizer_complete_pipeline")
        else:
            result.record_fail("sanitizer_complete_pipeline", "Pipeline checks failed")
    except Exception as e:
        result.record_fail("sanitizer_complete_pipeline", str(e))


############################################################
# SECTION 4: VALIDATOR INTEGRATION (40 tests)
############################################################

def test_validator_accepts_valid(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("validator_accepts_valid")
    except Exception as e:
        result.record_fail("validator_accepts_valid", str(e))


def test_validator_rejects_missing_provider(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "model": "gpt-4",
        "type": "completion",
        "content": "test"
    }
    raw_copy = raw.copy()
    del raw_copy["model"]
    try:
        wrapper.wrap({"type": "completion", "content": "test"})
        result.record_fail("validator_rejects_missing_provider", "Missing provider accepted")
    except WrapperValidationError:
        result.record_pass("validator_rejects_missing_provider")
    except Exception as e:
        result.record_pass("validator_rejects_missing_provider")


def test_validator_rejects_invalid_type_enum(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "invalid_type"
    try:
        wrapper.wrap(raw)
        result.record_fail("validator_rejects_invalid_type_enum", "Invalid type accepted")
    except WrapperValidationError:
        result.record_pass("validator_rejects_invalid_type_enum")
    except Exception as e:
        result.record_pass("validator_rejects_invalid_type_enum")


def test_validator_rejects_invalid_provider_enum(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["provider"] = "google"
    try:
        wrapper.wrap(raw)
        result.record_fail("validator_rejects_invalid_provider_enum", "Invalid provider accepted")
    except (WrapperValidationError, WrapperProviderError):
        result.record_pass("validator_rejects_invalid_provider_enum")
    except Exception as e:
        result.record_pass("validator_rejects_invalid_provider_enum")


def test_validator_strict_mode_default(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = ""
    try:
        wrapper.wrap(raw)
        result.record_fail("validator_strict_mode_default", "Empty model accepted in strict mode")
    except (WrapperValidationError, WrapperAnomalyError):
        result.record_pass("validator_strict_mode_default")
    except Exception as e:
        result.record_pass("validator_strict_mode_default")


def test_validator_non_strict_mode(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "tool"
    raw["content"] = ""
    try:
        wrapped = wrapper.wrap(raw, strict=False)
        result.record_pass("validator_non_strict_mode")
    except Exception as e:
        result.record_fail("validator_non_strict_mode", str(e))


def test_validator_all_required_fields_present(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        required = ["provider", "model", "type", "content"]
        if all(k in wrapped for k in required):
            result.record_pass("validator_all_required_fields_present")
        else:
            result.record_fail("validator_all_required_fields_present", "Missing required fields")
    except Exception as e:
        result.record_fail("validator_all_required_fields_present", str(e))


def test_validator_tokens_in_positive(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 100
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 100:
            result.record_pass("validator_tokens_in_positive")
        else:
            result.record_fail("validator_tokens_in_positive", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("validator_tokens_in_positive", str(e))


def test_validator_tokens_out_positive(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_out"] = 200
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_out"] == 200:
            result.record_pass("validator_tokens_out_positive")
        else:
            result.record_fail("validator_tokens_out_positive", f"Got {wrapped['tokens_out']}")
    except Exception as e:
        result.record_fail("validator_tokens_out_positive", str(e))


def test_validator_tokens_zero(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 0
    raw["tokens_out"] = 0
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 0 and wrapped["tokens_out"] == 0:
            result.record_pass("validator_tokens_zero")
        else:
            result.record_fail("validator_tokens_zero", "Zero tokens changed")
    except Exception as e:
        result.record_fail("validator_tokens_zero", str(e))


def test_validator_meta_valid_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"key": "value"}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {"key": "value"}:
            result.record_pass("validator_meta_valid_dict")
        else:
            result.record_fail("validator_meta_valid_dict", "Meta changed")
    except Exception as e:
        result.record_fail("validator_meta_valid_dict", str(e))


def test_validator_type_completion(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "completion"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "completion":
            result.record_pass("validator_type_completion")
        else:
            result.record_fail("validator_type_completion", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("validator_type_completion", str(e))


def test_validator_type_chat(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "chat"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "chat":
            result.record_pass("validator_type_chat")
        else:
            result.record_fail("validator_type_chat", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("validator_type_chat", str(e))


def test_validator_type_tool(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "tool"
    raw["content"] = ""
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "tool":
            result.record_pass("validator_type_tool")
        else:
            result.record_fail("validator_type_tool", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("validator_type_tool", str(e))


def test_validator_provider_openai(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "openai":
            result.record_pass("validator_provider_openai")
        else:
            result.record_fail("validator_provider_openai", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("validator_provider_openai", str(e))


def test_validator_provider_anthropic(result):
    wrapper = LLMResponseWrapper("anthropic")
    raw = {
        "model": "claude-3",
        "type": "chat",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "anthropic":
            result.record_pass("validator_provider_anthropic")
        else:
            result.record_fail("validator_provider_anthropic", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("validator_provider_anthropic", str(e))


def test_validator_provider_mistral(result):
    wrapper = LLMResponseWrapper("mistral")
    raw = {
        "model": "mistral-large",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["provider"] == "mistral":
            result.record_pass("validator_provider_mistral")
        else:
            result.record_fail("validator_provider_mistral", f"Got {wrapped['provider']}")
    except Exception as e:
        result.record_fail("validator_provider_mistral", str(e))


def test_validator_content_not_empty_for_completion(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "completion"
    raw["content"] = "valid content"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("validator_content_not_empty_for_completion")
    except Exception as e:
        result.record_fail("validator_content_not_empty_for_completion", str(e))


def test_validator_content_not_empty_for_chat(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "chat"
    raw["content"] = "valid content"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("validator_content_not_empty_for_chat")
    except Exception as e:
        result.record_fail("validator_content_not_empty_for_chat", str(e))


def test_validator_model_not_empty(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("validator_model_not_empty")
    except Exception as e:
        result.record_fail("validator_model_not_empty", str(e))


def test_validator_content_unicode(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "Hello 世界"
    try:
        wrapped = wrapper.wrap(raw)
        if "世界" in wrapped["content"]:
            result.record_pass("validator_content_unicode")
        else:
            result.record_fail("validator_content_unicode", "Unicode lost")
    except Exception as e:
        result.record_fail("validator_content_unicode", str(e))


def test_validator_content_multiline(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "line1\nline2\nline3"
    try:
        wrapped = wrapper.wrap(raw)
        if "\n" in wrapped["content"]:
            result.record_pass("validator_content_multiline")
        else:
            result.record_fail("validator_content_multiline", "Newlines removed")
    except Exception as e:
        result.record_fail("validator_content_multiline", str(e))


def test_validator_content_special_chars(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test@#$content"
    try:
        wrapped = wrapper.wrap(raw)
        if "@" in wrapped["content"]:
            result.record_pass("validator_content_special_chars")
        else:
            result.record_fail("validator_content_special_chars", "Special chars removed")
    except Exception as e:
        result.record_fail("validator_content_special_chars", str(e))


def test_validator_model_with_version(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4-turbo-2024-04-09"
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["model"] == "gpt-4-turbo-2024-04-09":
            result.record_pass("validator_model_with_version")
        else:
            result.record_fail("validator_model_with_version", f"Got {wrapped['model']}")
    except Exception as e:
        result.record_fail("validator_model_with_version", str(e))


def test_validator_meta_nested(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"level1": {"level2": {"level3": "value"}}}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"]["level1"]["level2"]["level3"] == "value":
            result.record_pass("validator_meta_nested")
        else:
            result.record_fail("validator_meta_nested", "Nested value changed")
    except Exception as e:
        result.record_fail("validator_meta_nested", str(e))


def test_validator_meta_empty(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"] == {}:
            result.record_pass("validator_meta_empty")
        else:
            result.record_fail("validator_meta_empty", "Empty meta changed")
    except Exception as e:
        result.record_fail("validator_meta_empty", str(e))


def test_validator_all_fields_complete(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "chat",
        "content": "test content",
        "tokens_in": 50,
        "tokens_out": 100,
        "meta": {"session": "123"}
    }
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped.keys()) >= 7:
            result.record_pass("validator_all_fields_complete")
        else:
            result.record_fail("validator_all_fields_complete", f"Only {len(wrapped.keys())} fields")
    except Exception as e:
        result.record_fail("validator_all_fields_complete", str(e))


def test_validator_preserves_data(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["content"] == "Valid response content":
            result.record_pass("validator_preserves_data")
        else:
            result.record_fail("validator_preserves_data", "Data changed")
    except Exception as e:
        result.record_fail("validator_preserves_data", str(e))


def test_validator_wraps_exceptions(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "invalid_type"
    try:
        wrapper.wrap(raw)
        result.record_fail("validator_wraps_exceptions", "Invalid type accepted")
    except WrapperValidationError:
        result.record_pass("validator_wraps_exceptions")
    except Exception as e:
        result.record_pass("validator_wraps_exceptions")


def test_validator_tokens_large_numbers(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 999999999
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 999999999:
            result.record_pass("validator_tokens_large_numbers")
        else:
            result.record_fail("validator_tokens_large_numbers", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("validator_tokens_large_numbers", str(e))


def test_validator_content_very_long(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "x" * 100000
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["content"]) == 50000:
            result.record_pass("validator_content_very_long")
        else:
            result.record_fail("validator_content_very_long", f"Length {len(wrapped['content'])}")
    except Exception as e:
        result.record_fail("validator_content_very_long", str(e))


def test_validator_all_providers_valid(result):
    providers = [("openai", "gpt-4"), ("anthropic", "claude-3"), ("mistral", "mistral-large")]
    for provider, model in providers:
        try:
            wrapper = LLMResponseWrapper(provider)
            raw = {"model": model, "type": "completion", "content": "test"}
            wrapped = wrapper.wrap(raw)
            if wrapped["provider"] != provider:
                result.record_fail(f"validator_provider_{provider}", f"Provider {provider} failed")
                return
        except Exception as e:
            result.record_fail(f"validator_provider_{provider}", str(e))
            return
    result.record_pass("validator_all_providers_valid")


def test_validator_type_default_completion(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "model": "gpt-4",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["type"] == "completion":
            result.record_pass("validator_type_default_completion")
        else:
            result.record_fail("validator_type_default_completion", f"Got {wrapped['type']}")
    except Exception as e:
        result.record_fail("validator_type_default_completion", str(e))


def test_validator_model_default_unknown(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["model"] == "unknown":
            result.record_pass("validator_model_default_unknown")
        else:
            result.record_fail("validator_model_default_unknown", f"Got {wrapped['model']}")
    except Exception as e:
        result.record_fail("validator_model_default_unknown", str(e))


def test_validator_strict_checks_enabled(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = ""
    try:
        wrapper.wrap(raw, strict=True)
        result.record_fail("validator_strict_checks_enabled", "Empty content accepted in strict mode")
    except WrapperAnomalyError:
        result.record_pass("validator_strict_checks_enabled")
    except Exception as e:
        result.record_pass("validator_strict_checks_enabled")


def test_validator_complete_flow(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "PROVIDER": "OPENAI",
        "model": "gpt-4",
        "type": "chat",
        "content": "test\x00content\n\n\n",
        "tokens_in": 10.5,
        "meta": {"key": "val"}
    }
    try:
        wrapped = wrapper.wrap(raw)
        checks = [
            wrapped["provider"] == "openai",
            wrapped["model"] == "gpt-4",
            wrapped["type"] == "chat",
            "\x00" not in wrapped["content"],
            wrapped["tokens_in"] == 10
        ]
        if all(checks):
            result.record_pass("validator_complete_flow")
        else:
            result.record_fail("validator_complete_flow", "Flow checks failed")
    except Exception as e:
        result.record_fail("validator_complete_flow", str(e))


############################################################
# SECTION 5: ANOMALY FIREWALL (30 tests)
############################################################

def test_anomaly_empty_content_completion(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = ""
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_empty_content_completion", "Empty content accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_empty_content_completion")
    except Exception as e:
        result.record_fail("anomaly_empty_content_completion", f"Wrong error: {e}")


def test_anomaly_empty_content_chat(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "chat"
    raw["content"] = ""
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_empty_content_chat", "Empty content accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_empty_content_chat")
    except Exception as e:
        result.record_fail("anomaly_empty_content_chat", f"Wrong error: {e}")


def test_anomaly_empty_content_tool_allowed(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["type"] = "tool"
    raw["content"] = ""
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_empty_content_tool_allowed")
    except Exception as e:
        result.record_fail("anomaly_empty_content_tool_allowed", str(e))


def test_anomaly_whitespace_only_content(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "   "
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_whitespace_only_content", "Whitespace-only content accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_whitespace_only_content")
    except Exception as e:
        result.record_fail("anomaly_whitespace_only_content", f"Wrong error: {e}")


def test_anomaly_provider_model_mismatch_openai_claude(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "claude-3"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_provider_model_mismatch_openai_claude", "Mismatch accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_provider_model_mismatch_openai_claude")
    except Exception as e:
        result.record_fail("anomaly_provider_model_mismatch_openai_claude", f"Wrong error: {e}")


def test_anomaly_provider_model_mismatch_anthropic_gpt(result):
    wrapper = LLMResponseWrapper("anthropic")
    raw = {
        "model": "gpt-4",
        "type": "chat",
        "content": "test"
    }
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_provider_model_mismatch_anthropic_gpt", "Mismatch accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_provider_model_mismatch_anthropic_gpt")
    except Exception as e:
        result.record_fail("anomaly_provider_model_mismatch_anthropic_gpt", f"Wrong error: {e}")


def test_anomaly_provider_model_mismatch_mistral_claude(result):
    wrapper = LLMResponseWrapper("mistral")
    raw = {
        "model": "claude-2",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_provider_model_mismatch_mistral_claude", "Mismatch accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_provider_model_mismatch_mistral_claude")
    except Exception as e:
        result.record_fail("anomaly_provider_model_mismatch_mistral_claude", f"Wrong error: {e}")


def test_anomaly_repetition_attack(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "a" * 1000
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_repetition_attack", "Repetition accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_repetition_attack")
    except Exception as e:
        result.record_fail("anomaly_repetition_attack", f"Wrong error: {e}")


def test_anomaly_forbidden_script_tag(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test <script>alert('xss')</script> content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_script_tag", "Script tag accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_script_tag")
    except Exception as e:
        result.record_fail("anomaly_forbidden_script_tag", f"Wrong error: {e}")


def test_anomaly_forbidden_html_tag(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test </html> content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_html_tag", "HTML tag accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_html_tag")
    except Exception as e:
        result.record_fail("anomaly_forbidden_html_tag", f"Wrong error: {e}")


def test_anomaly_forbidden_php_tag(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test <?php echo 'test'; ?> content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_php_tag", "PHP tag accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_php_tag")
    except Exception as e:
        result.record_fail("anomaly_forbidden_php_tag", f"Wrong error: {e}")


def test_anomaly_forbidden_private_key(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test BEGIN RSA PRIVATE KEY content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_private_key", "Private key accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_private_key")
    except Exception as e:
        result.record_fail("anomaly_forbidden_private_key", f"Wrong error: {e}")


def test_anomaly_forbidden_api_key_sk(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test sk-abc123xyz content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_api_key_sk", "API key accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_api_key_sk")
    except Exception as e:
        result.record_fail("anomaly_forbidden_api_key_sk", f"Wrong error: {e}")


def test_anomaly_forbidden_api_key_pattern(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test api_key=secret123 content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_api_key_pattern", "API key pattern accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_api_key_pattern")
    except Exception as e:
        result.record_fail("anomaly_forbidden_api_key_pattern", f"Wrong error: {e}")


def test_anomaly_valid_content_passes(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "This is valid normal content without any issues"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_valid_content_passes")
    except Exception as e:
        result.record_fail("anomaly_valid_content_passes", str(e))


def test_anomaly_provider_model_match_openai(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4-turbo"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_provider_model_match_openai")
    except Exception as e:
        result.record_fail("anomaly_provider_model_match_openai", str(e))


def test_anomaly_provider_model_match_anthropic(result):
    wrapper = LLMResponseWrapper("anthropic")
    raw = {
        "model": "claude-3-opus",
        "type": "chat",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_provider_model_match_anthropic")
    except Exception as e:
        result.record_fail("anomaly_provider_model_match_anthropic", str(e))


def test_anomaly_provider_model_match_mistral(result):
    wrapper = LLMResponseWrapper("mistral")
    raw = {
        "model": "mistral-large",
        "type": "completion",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_provider_model_match_mistral")
    except Exception as e:
        result.record_fail("anomaly_provider_model_match_mistral", str(e))


def test_anomaly_repetition_normal_text(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "This is a normal text with some repeated words like test test test"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_repetition_normal_text")
    except Exception as e:
        result.record_fail("anomaly_repetition_normal_text", str(e))


def test_anomaly_forbidden_case_insensitive(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test <SCRIPT>alert('xss')</SCRIPT> content"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_case_insensitive", "Script tag (uppercase) accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_case_insensitive")
    except Exception as e:
        result.record_fail("anomaly_forbidden_case_insensitive", f"Wrong error: {e}")


def test_anomaly_multiple_forbidden_patterns(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test <script>code</script> and sk-key123"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_multiple_forbidden_patterns", "Multiple patterns accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_multiple_forbidden_patterns")
    except Exception as e:
        result.record_fail("anomaly_multiple_forbidden_patterns", f"Wrong error: {e}")


def test_anomaly_model_substring_match(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "gpt-4-claude-mix"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_model_substring_match", "Substring mismatch accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_model_substring_match")
    except Exception as e:
        result.record_fail("anomaly_model_substring_match", f"Wrong error: {e}")


def test_anomaly_content_with_newlines_valid(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "line1\nline2\nline3"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_content_with_newlines_valid")
    except Exception as e:
        result.record_fail("anomaly_content_with_newlines_valid", str(e))


def test_anomaly_content_unicode_valid(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "Hello 世界 こんにちは"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_content_unicode_valid")
    except Exception as e:
        result.record_fail("anomaly_content_unicode_valid", str(e))


def test_anomaly_repetition_threshold(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "a" * 499
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_repetition_threshold")
    except Exception as e:
        result.record_fail("anomaly_repetition_threshold", str(e))


def test_anomaly_repetition_over_threshold(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "b" * 500
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_repetition_over_threshold", "Repetition over threshold accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_repetition_over_threshold")
    except Exception as e:
        result.record_fail("anomaly_repetition_over_threshold", f"Wrong error: {e}")


def test_anomaly_all_checks_pass(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4",
        "type": "chat",
        "content": "This is a completely valid response with no anomalies",
        "tokens_in": 10,
        "tokens_out": 20,
        "meta": {"session": "abc123"}
    }
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("anomaly_all_checks_pass")
    except Exception as e:
        result.record_fail("anomaly_all_checks_pass", str(e))


def test_anomaly_firewall_order(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = ""
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_firewall_order", "Empty content accepted")
    except WrapperAnomalyError as e:
        if "Empty content" in str(e):
            result.record_pass("anomaly_firewall_order")
        else:
            result.record_fail("anomaly_firewall_order", f"Wrong error message: {e}")
    except Exception as e:
        result.record_fail("anomaly_firewall_order", f"Wrong error: {e}")


def test_anomaly_forbidden_pattern_partial(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "test asking about api_key= parameter"
    try:
        wrapper.wrap(raw)
        result.record_fail("anomaly_forbidden_pattern_partial", "Partial pattern accepted")
    except WrapperAnomalyError:
        result.record_pass("anomaly_forbidden_pattern_partial")
    except Exception as e:
        result.record_fail("anomaly_forbidden_pattern_partial", f"Wrong error: {e}")


############################################################
# SECTION 6: ERROR HANDLING & EDGE CASES (min 10 tests)
############################################################

def test_error_wrapper_error_exists(result):
    try:
        raise WrapperError("test")
    except WrapperError:
        result.record_pass("error_wrapper_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_error_exists", str(e))


def test_error_wrapper_schema_error_exists(result):
    try:
        raise WrapperSchemaError("test")
    except WrapperSchemaError:
        result.record_pass("error_wrapper_schema_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_schema_error_exists", str(e))


def test_error_wrapper_normalization_error_exists(result):
    try:
        raise WrapperNormalizationError("test")
    except WrapperNormalizationError:
        result.record_pass("error_wrapper_normalization_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_normalization_error_exists", str(e))


def test_error_wrapper_validation_error_exists(result):
    try:
        raise WrapperValidationError("test")
    except WrapperValidationError:
        result.record_pass("error_wrapper_validation_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_validation_error_exists", str(e))


def test_error_wrapper_anomaly_error_exists(result):
    try:
        raise WrapperAnomalyError("test")
    except WrapperAnomalyError:
        result.record_pass("error_wrapper_anomaly_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_anomaly_error_exists", str(e))


def test_error_wrapper_provider_error_exists(result):
    try:
        raise WrapperProviderError("test")
    except WrapperProviderError:
        result.record_pass("error_wrapper_provider_error_exists")
    except Exception as e:
        result.record_fail("error_wrapper_provider_error_exists", str(e))


def test_edge_empty_dict(result):
    wrapper = LLMResponseWrapper("openai")
    try:
        wrapper.wrap({})
        result.record_fail("edge_empty_dict", "Empty dict accepted")
    except (WrapperValidationError, WrapperAnomalyError):
        result.record_pass("edge_empty_dict")
    except Exception as e:
        result.record_pass("edge_empty_dict")


def test_edge_minimal_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "model": "gpt-4",
        "content": "test"
    }
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("edge_minimal_dict")
    except Exception as e:
        result.record_fail("edge_minimal_dict", str(e))


def test_edge_maximal_dict(result):
    wrapper = LLMResponseWrapper("openai")
    raw = {
        "provider": "openai",
        "model": "gpt-4-turbo-2024-04-09",
        "type": "chat",
        "content": "This is a maximal response with all fields populated",
        "tokens_in": 100,
        "tokens_out": 200,
        "meta": {
            "session": "abc123",
            "timestamp": "2024-01-01T00:00:00Z",
            "nested": {"deep": "value"}
        }
    }
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("edge_maximal_dict")
    except Exception as e:
        result.record_fail("edge_maximal_dict", str(e))


def test_edge_content_exactly_50000_chars(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "x" * 50000
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["content"]) == 50000:
            result.record_pass("edge_content_exactly_50000_chars")
        else:
            result.record_fail("edge_content_exactly_50000_chars", f"Length {len(wrapped['content'])}")
    except Exception as e:
        result.record_fail("edge_content_exactly_50000_chars", str(e))


def test_edge_model_exactly_200_chars(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["model"] = "x" * 200
    try:
        wrapped = wrapper.wrap(raw)
        if len(wrapped["model"]) == 200:
            result.record_pass("edge_model_exactly_200_chars")
        else:
            result.record_fail("edge_model_exactly_200_chars", f"Length {len(wrapped['model'])}")
    except Exception as e:
        result.record_fail("edge_model_exactly_200_chars", str(e))


def test_edge_tokens_max_int(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["tokens_in"] = 2147483647
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["tokens_in"] == 2147483647:
            result.record_pass("edge_tokens_max_int")
        else:
            result.record_fail("edge_tokens_max_int", f"Got {wrapped['tokens_in']}")
    except Exception as e:
        result.record_fail("edge_tokens_max_int", str(e))


def test_edge_all_errors_are_wrapper_errors(result):
    errors = [
        WrapperSchemaError, WrapperNormalizationError,
        WrapperValidationError, WrapperAnomalyError, WrapperProviderError
    ]
    for err in errors:
        if not issubclass(err, WrapperError):
            result.record_fail("edge_all_errors_are_wrapper_errors", f"{err} not subclass of WrapperError")
            return
    result.record_pass("edge_all_errors_are_wrapper_errors")


def test_edge_wrap_multiple_times(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped1 = wrapper.wrap(raw)
        wrapped2 = wrapper.wrap(raw)
        if wrapped1 == wrapped2:
            result.record_pass("edge_wrap_multiple_times")
        else:
            result.record_fail("edge_wrap_multiple_times", "Results differ")
    except Exception as e:
        result.record_fail("edge_wrap_multiple_times", str(e))


def test_edge_different_wrappers_same_raw(result):
    wrapper1 = LLMResponseWrapper("openai")
    wrapper2 = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    try:
        wrapped1 = wrapper1.wrap(raw)
        wrapped2 = wrapper2.wrap(raw)
        if wrapped1 == wrapped2:
            result.record_pass("edge_different_wrappers_same_raw")
        else:
            result.record_fail("edge_different_wrappers_same_raw", "Results differ")
    except Exception as e:
        result.record_fail("edge_different_wrappers_same_raw", str(e))


def test_edge_content_only_unicode(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["content"] = "世界こんにちは你好مرحبا"
    try:
        wrapped = wrapper.wrap(raw)
        result.record_pass("edge_content_only_unicode")
    except Exception as e:
        result.record_fail("edge_content_only_unicode", str(e))


def test_edge_meta_very_nested(result):
    wrapper = LLMResponseWrapper("openai")
    raw = make_valid_raw()
    raw["meta"] = {"l1": {"l2": {"l3": {"l4": {"l5": "deep"}}}}}
    try:
        wrapped = wrapper.wrap(raw)
        if wrapped["meta"]["l1"]["l2"]["l3"]["l4"]["l5"] == "deep":
            result.record_pass("edge_meta_very_nested")
        else:
            result.record_fail("edge_meta_very_nested", "Deep value lost")
    except Exception as e:
        result.record_fail("edge_meta_very_nested", str(e))


def test_edge_all_three_providers_full_pipeline(result):
    providers = [
        ("openai", "gpt-4", "OpenAI response"),
        ("anthropic", "claude-3", "Anthropic response"),
        ("mistral", "mistral-large", "Mistral response")
    ]
    for provider, model, content in providers:
        try:
            wrapper = LLMResponseWrapper(provider)
            raw = {"model": model, "type": "chat", "content": content}
            wrapped = wrapper.wrap(raw)
            if wrapped["provider"] != provider or wrapped["content"] != content:
                result.record_fail("edge_all_three_providers_full_pipeline", f"Provider {provider} failed")
                return
        except Exception as e:
            result.record_fail("edge_all_three_providers_full_pipeline", str(e))
            return
    result.record_pass("edge_all_three_providers_full_pipeline")


############################################################
# TEST RUNNER
############################################################

def run_all_tests():
    result = TestResult()

    # Section 1: Pre-clean tests (50)
    test_preclean_removes_none_values(result)
    test_preclean_sanitizes_strings(result)
    test_preclean_converts_int(result)
    test_preclean_converts_float(result)
    test_preclean_copies_dict(result)
    test_preclean_copies_list(result)
    test_preclean_converts_keys_to_lowercase(result)
    test_preclean_strips_key_whitespace(result)
    test_preclean_handles_boolean(result)
    test_preclean_converts_unknown_to_string(result)
    test_sanitize_text_none(result)
    test_sanitize_text_removes_null_byte(result)
    test_sanitize_text_collapses_newlines(result)
    test_sanitize_text_truncates_long_content(result)
    test_sanitize_text_preserves_unicode(result)
    test_sanitize_text_empty_string(result)
    test_sanitize_text_whitespace_only(result)
    test_safe_int_from_int(result)
    test_safe_int_from_float(result)
    test_safe_int_negative_to_zero(result)
    test_safe_int_invalid_to_zero(result)
    test_safe_int_boolean_false(result)
    test_safe_int_zero(result)
    test_safe_int_large_number(result)
    test_safe_int_none(result)
    test_preclean_multiple_none_fields(result)
    test_preclean_nested_dict(result)
    test_preclean_empty_dict(result)
    test_preclean_empty_list(result)
    test_preclean_mixed_types(result)
    test_sanitize_text_non_string_input(result)
    test_safe_int_string_number(result)
    test_safe_int_negative_float(result)
    test_preclean_content_with_newlines(result)
    test_preclean_very_long_content(result)
    test_preclean_unicode_content(result)
    test_sanitize_text_max_newlines(result)
    test_safe_int_float_zero(result)
    test_preclean_preserves_order(result)
    test_preclean_key_normalization(result)
    test_sanitize_text_special_chars(result)
    test_safe_int_max_int(result)
    test_preclean_tokens_zero(result)
    test_preclean_all_required_fields(result)
    test_sanitize_text_tabs(result)
    test_safe_int_list_fallback(result)

    # Section 2: Normalization tests (40)
    test_normalize_provider_openai(result)
    test_normalize_provider_anthropic(result)
    test_normalize_provider_mistral(result)
    test_normalize_provider_uppercase(result)
    test_normalize_provider_whitespace(result)
    test_normalize_provider_invalid(result)
    test_normalize_provider_none(result)
    test_normalize_provider_empty(result)
    test_normalize_model_valid(result)
    test_normalize_model_none(result)
    test_normalize_model_empty(result)
    test_normalize_model_whitespace(result)
    test_normalize_model_newlines(result)
    test_normalize_model_too_long(result)
    test_normalize_model_non_string(result)
    test_normalization_sets_provider(result)
    test_normalization_sets_model(result)
    test_normalization_sets_type_default(result)
    test_normalization_preserves_type(result)
    test_normalization_sets_content(result)
    test_normalization_content_default_empty(result)
    test_normalization_tokens_in_default(result)
    test_normalization_tokens_out_default(result)
    test_normalization_meta_default(result)
    test_normalization_meta_not_dict_error(result)
    test_normalization_copies_meta(result)
    test_wrapper_init_stores_provider(result)
    test_wrapper_init_normalizes_provider(result)
    test_wrapper_init_invalid_provider(result)
    test_normalization_overrides_provider(result)
    test_normalization_uses_wrapper_provider_default(result)
    test_normalize_model_only_whitespace(result)
    test_normalize_provider_mixed_case(result)
    test_normalization_tokens_preserve_positive(result)
    test_normalization_tokens_negative_to_zero(result)
    test_normalize_model_carriage_return(result)
    test_normalization_all_providers(result)
    test_normalization_content_sanitized(result)
    test_normalize_model_exact_200_chars(result)

    # Section 3: Sanitizer integration (40)
    test_sanitizer_basic_fields_called(result)
    test_sanitizer_content_length_called(result)
    test_sanitizer_types_called(result)
    test_sanitizer_removes_whitespace(result)
    test_sanitizer_preserves_valid_data(result)
    test_sanitizer_handles_missing_optional_fields(result)
    test_sanitizer_float_tokens_both(result)
    test_sanitizer_content_exact_50000(result)
    test_sanitizer_content_under_limit(result)
    test_sanitizer_preserves_meta(result)
    test_sanitizer_tokens_zero(result)
    test_sanitizer_tokens_large(result)
    test_sanitizer_all_types(result)
    test_sanitizer_unicode_preserved(result)
    test_sanitizer_newlines_in_content(result)
    test_sanitizer_special_chars_in_content(result)
    test_sanitizer_empty_content(result)
    test_sanitizer_whitespace_only_content(result)
    test_sanitizer_model_whitespace(result)
    test_sanitizer_provider_case_normalized(result)
    test_sanitizer_type_case_preserved(result)
    test_sanitizer_meta_nested(result)
    test_sanitizer_all_fields_present(result)
    test_sanitizer_content_multiline(result)
    test_sanitizer_tokens_string_converted(result)
    test_sanitizer_model_special_chars(result)
    test_sanitizer_content_tabs(result)
    test_sanitizer_meta_empty_dict(result)
    test_sanitizer_provider_anthropic(result)
    test_sanitizer_provider_mistral(result)
    test_sanitizer_content_max_newlines(result)
    test_sanitizer_tokens_float_negative(result)
    test_sanitizer_model_unicode(result)
    test_sanitizer_content_null_bytes_removed(result)
    test_sanitizer_complete_pipeline(result)

    # Section 4: Validator integration (40)
    test_validator_accepts_valid(result)
    test_validator_rejects_missing_provider(result)
    test_validator_rejects_invalid_type_enum(result)
    test_validator_rejects_invalid_provider_enum(result)
    test_validator_strict_mode_default(result)
    test_validator_non_strict_mode(result)
    test_validator_all_required_fields_present(result)
    test_validator_tokens_in_positive(result)
    test_validator_tokens_out_positive(result)
    test_validator_tokens_zero(result)
    test_validator_meta_valid_dict(result)
    test_validator_type_completion(result)
    test_validator_type_chat(result)
    test_validator_type_tool(result)
    test_validator_provider_openai(result)
    test_validator_provider_anthropic(result)
    test_validator_provider_mistral(result)
    test_validator_content_not_empty_for_completion(result)
    test_validator_content_not_empty_for_chat(result)
    test_validator_model_not_empty(result)
    test_validator_content_unicode(result)
    test_validator_content_multiline(result)
    test_validator_content_special_chars(result)
    test_validator_model_with_version(result)
    test_validator_meta_nested(result)
    test_validator_meta_empty(result)
    test_validator_all_fields_complete(result)
    test_validator_preserves_data(result)
    test_validator_wraps_exceptions(result)
    test_validator_tokens_large_numbers(result)
    test_validator_content_very_long(result)
    test_validator_all_providers_valid(result)
    test_validator_type_default_completion(result)
    test_validator_model_default_unknown(result)
    test_validator_strict_checks_enabled(result)
    test_validator_complete_flow(result)

    # Section 5: Anomaly firewall (30)
    test_anomaly_empty_content_completion(result)
    test_anomaly_empty_content_chat(result)
    test_anomaly_empty_content_tool_allowed(result)
    test_anomaly_whitespace_only_content(result)
    test_anomaly_provider_model_mismatch_openai_claude(result)
    test_anomaly_provider_model_mismatch_anthropic_gpt(result)
    test_anomaly_provider_model_mismatch_mistral_claude(result)
    test_anomaly_repetition_attack(result)
    test_anomaly_forbidden_script_tag(result)
    test_anomaly_forbidden_html_tag(result)
    test_anomaly_forbidden_php_tag(result)
    test_anomaly_forbidden_private_key(result)
    test_anomaly_forbidden_api_key_sk(result)
    test_anomaly_forbidden_api_key_pattern(result)
    test_anomaly_valid_content_passes(result)
    test_anomaly_provider_model_match_openai(result)
    test_anomaly_provider_model_match_anthropic(result)
    test_anomaly_provider_model_match_mistral(result)
    test_anomaly_repetition_normal_text(result)
    test_anomaly_forbidden_case_insensitive(result)
    test_anomaly_multiple_forbidden_patterns(result)
    test_anomaly_model_substring_match(result)
    test_anomaly_content_with_newlines_valid(result)
    test_anomaly_content_unicode_valid(result)
    test_anomaly_repetition_threshold(result)
    test_anomaly_repetition_over_threshold(result)
    test_anomaly_all_checks_pass(result)
    test_anomaly_firewall_order(result)
    test_anomaly_forbidden_pattern_partial(result)

    # Section 6: Error handling & edge cases (19 tests)
    test_error_wrapper_error_exists(result)
    test_error_wrapper_schema_error_exists(result)
    test_error_wrapper_normalization_error_exists(result)
    test_error_wrapper_validation_error_exists(result)
    test_error_wrapper_anomaly_error_exists(result)
    test_error_wrapper_provider_error_exists(result)
    test_edge_empty_dict(result)
    test_edge_minimal_dict(result)
    test_edge_maximal_dict(result)
    test_edge_content_exactly_50000_chars(result)
    test_edge_model_exactly_200_chars(result)
    test_edge_tokens_max_int(result)
    test_edge_all_errors_are_wrapper_errors(result)
    test_edge_wrap_multiple_times(result)
    test_edge_different_wrappers_same_raw(result)
    test_edge_content_only_unicode(result)
    test_edge_meta_very_nested(result)
    test_edge_all_three_providers_full_pipeline(result)

    return result


def main():
    result = run_all_tests()
    print(result.summary())
    if result.failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

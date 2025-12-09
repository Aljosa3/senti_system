#!/usr/bin/env python3
"""
FAZA 30.99 - MAX CONTRACT VALIDATOR TEST SUITE
"""

import sys
from pathlib import Path
import copy

# ----------------------------------------------------------------------------------
# ROOT PATH INJECTION (critical for being able to import the contract validator)
# ----------------------------------------------------------------------------------
ROOT = str(Path(__file__).resolve().parents[3])
sys.path.insert(0, ROOT)

from senti_core_module.senti_llm.contract_validator.sanitizer import (
    sanitize_basic_fields,
    sanitize_content_length,
    sanitize_types,
)

from senti_core_module.senti_llm.contract_validator.schema import (
    LLM_RESPONSE_SCHEMA,
)

from senti_core_module.senti_llm.contract_validator.errors import (
    ContractValidationError,
    ContractSanitizationError,
    ContractSchemaError,
    StrictModeViolation,
)

from senti_core_module.senti_llm.contract_validator.validator import (
    validate_contract,
    validate_schema,
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
        lines.append("=" * 60)
        lines.append("FAZA 30.99 MAX VALIDATOR TEST SUITE REPORT")
        lines.append(f"TOTAL TESTS: {self.passed + self.failed}")
        lines.append(f"PASSED: {self.passed}")
        lines.append(f"FAILED: {self.failed}")
        lines.append("=" * 60)
        if self.failures:
            lines.append("\nFAILURES:")
            for name, error in self.failures:
                lines.append(f"  - {name}: {error}")
        return "\n".join(lines)


def deep_copy(data):
    return copy.deepcopy(data)


def make_valid_contract():
    return {
        "type": "completion",
        "provider": "openai",
        "model": "gpt-4",
        "content": "This is a valid response"
    }


def corrupt_field(contract, field, value):
    c = deep_copy(contract)
    c[field] = value
    return c


def strip_whitespace_recursive(obj):
    if isinstance(obj, dict):
        return {k: strip_whitespace_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [strip_whitespace_recursive(item) for item in obj]
    elif isinstance(obj, str):
        return obj.strip()
    else:
        return obj


############################################################
# SECTION 1 — SANITIZATION TESTS
############################################################

def test_sanitize_basic_removes_none(result):
    data = {"a": None, "b": "value"}
    cleaned = sanitize_basic_fields(data)
    if "a" in cleaned:
        result.record_fail("sanitize_basic_removes_none", "None key not removed")
    elif cleaned.get("b") != "value":
        result.record_fail("sanitize_basic_removes_none", "Valid value lost")
    else:
        result.record_pass("sanitize_basic_removes_none")


def test_sanitize_basic_strips_whitespace(result):
    data = {"key": "  value  "}
    cleaned = sanitize_basic_fields(data)
    if cleaned["key"] != "value":
        result.record_fail("sanitize_basic_strips_whitespace", f"Got '{cleaned['key']}'")
    else:
        result.record_pass("sanitize_basic_strips_whitespace")


def test_sanitize_basic_preserves_numbers(result):
    data = {"num": 42}
    cleaned = sanitize_basic_fields(data)
    if cleaned["num"] != 42:
        result.record_fail("sanitize_basic_preserves_numbers", "Number changed")
    else:
        result.record_pass("sanitize_basic_preserves_numbers")


def test_sanitize_basic_no_mutation(result):
    data = {"key": "  value  "}
    original = deep_copy(data)
    sanitize_basic_fields(data)
    if data != original:
        result.record_fail("sanitize_basic_no_mutation", "Input mutated")
    else:
        result.record_pass("sanitize_basic_no_mutation")


def test_sanitize_basic_empty_dict(result):
    data = {}
    cleaned = sanitize_basic_fields(data)
    if cleaned != {}:
        result.record_fail("sanitize_basic_empty_dict", "Empty dict changed")
    else:
        result.record_pass("sanitize_basic_empty_dict")


def test_sanitize_basic_all_none(result):
    data = {"a": None, "b": None}
    cleaned = sanitize_basic_fields(data)
    if cleaned != {}:
        result.record_fail("sanitize_basic_all_none", f"Got {cleaned}")
    else:
        result.record_pass("sanitize_basic_all_none")


def test_sanitize_basic_mixed_types(result):
    data = {"str": " x ", "int": 10, "none": None}
    cleaned = sanitize_basic_fields(data)
    if "none" in cleaned or cleaned.get("str") != "x" or cleaned.get("int") != 10:
        result.record_fail("sanitize_basic_mixed_types", "Mixed types failed")
    else:
        result.record_pass("sanitize_basic_mixed_types")


def test_sanitize_basic_converts_key_to_string(result):
    data = {1: "value"}
    cleaned = sanitize_basic_fields(data)
    if "1" not in cleaned:
        result.record_fail("sanitize_basic_converts_key_to_string", "Key not converted")
    else:
        result.record_pass("sanitize_basic_converts_key_to_string")


def test_sanitize_content_length_basic(result):
    data = {"content": "x" * 100000}
    cleaned = sanitize_content_length(data)
    if len(cleaned["content"]) != 50000:
        result.record_fail("sanitize_content_length_basic", f"Length {len(cleaned['content'])}")
    else:
        result.record_pass("sanitize_content_length_basic")


def test_sanitize_content_length_no_content(result):
    data = {"other": "value"}
    cleaned = sanitize_content_length(data)
    if "content" in cleaned:
        result.record_fail("sanitize_content_length_no_content", "Content added")
    else:
        result.record_pass("sanitize_content_length_no_content")


def test_sanitize_content_length_exact_limit(result):
    data = {"content": "x" * 50000}
    cleaned = sanitize_content_length(data)
    if len(cleaned["content"]) != 50000:
        result.record_fail("sanitize_content_length_exact_limit", "Exact limit changed")
    else:
        result.record_pass("sanitize_content_length_exact_limit")


def test_sanitize_content_length_under_limit(result):
    data = {"content": "short"}
    cleaned = sanitize_content_length(data)
    if cleaned["content"] != "short":
        result.record_fail("sanitize_content_length_under_limit", "Short content changed")
    else:
        result.record_pass("sanitize_content_length_under_limit")


def test_sanitize_content_length_custom_limit(result):
    data = {"content": "x" * 1000}
    cleaned = sanitize_content_length(data, max_len=100)
    if len(cleaned["content"]) != 100:
        result.record_fail("sanitize_content_length_custom_limit", "Custom limit not applied")
    else:
        result.record_pass("sanitize_content_length_custom_limit")


def test_sanitize_content_length_no_mutation(result):
    data = {"content": "x" * 100000}
    original = deep_copy(data)
    sanitize_content_length(data)
    if data != original:
        result.record_fail("sanitize_content_length_no_mutation", "Input mutated")
    else:
        result.record_pass("sanitize_content_length_no_mutation")


def test_sanitize_types_float_to_int_tokens_in(result):
    data = {"tokens_in": 42.7}
    cleaned = sanitize_types(data)
    if cleaned["tokens_in"] != 42 or not isinstance(cleaned["tokens_in"], int):
        result.record_fail("sanitize_types_float_to_int_tokens_in", "Float not converted")
    else:
        result.record_pass("sanitize_types_float_to_int_tokens_in")


def test_sanitize_types_float_to_int_tokens_out(result):
    data = {"tokens_out": 99.2}
    cleaned = sanitize_types(data)
    if cleaned["tokens_out"] != 99 or not isinstance(cleaned["tokens_out"], int):
        result.record_fail("sanitize_types_float_to_int_tokens_out", "Float not converted")
    else:
        result.record_pass("sanitize_types_float_to_int_tokens_out")


def test_sanitize_types_meta_must_be_dict(result):
    data = {"meta": "not a dict"}
    try:
        sanitize_types(data)
        result.record_fail("sanitize_types_meta_must_be_dict", "No error raised")
    except ContractSanitizationError:
        result.record_pass("sanitize_types_meta_must_be_dict")
    except Exception as e:
        result.record_fail("sanitize_types_meta_must_be_dict", f"Wrong error: {e}")


def test_sanitize_types_meta_valid_dict(result):
    data = {"meta": {"key": "value"}}
    try:
        cleaned = sanitize_types(data)
        if cleaned["meta"] != {"key": "value"}:
            result.record_fail("sanitize_types_meta_valid_dict", "Meta changed")
        else:
            result.record_pass("sanitize_types_meta_valid_dict")
    except Exception as e:
        result.record_fail("sanitize_types_meta_valid_dict", str(e))


def test_sanitize_types_no_mutation(result):
    data = {"tokens_in": 42.7}
    original = deep_copy(data)
    sanitize_types(data)
    if data != original:
        result.record_fail("sanitize_types_no_mutation", "Input mutated")
    else:
        result.record_pass("sanitize_types_no_mutation")


def test_sanitize_types_both_tokens(result):
    data = {"tokens_in": 10.5, "tokens_out": 20.9}
    cleaned = sanitize_types(data)
    if cleaned["tokens_in"] != 10 or cleaned["tokens_out"] != 20:
        result.record_fail("sanitize_types_both_tokens", "Both tokens not converted")
    else:
        result.record_pass("sanitize_types_both_tokens")


def test_sanitize_types_no_tokens(result):
    data = {"other": "value"}
    cleaned = sanitize_types(data)
    if cleaned != data:
        result.record_fail("sanitize_types_no_tokens", "Data changed unexpectedly")
    else:
        result.record_pass("sanitize_types_no_tokens")


def test_sanitize_basic_multiple_whitespace(result):
    data = {"key": "   too   many   spaces   "}
    cleaned = sanitize_basic_fields(data)
    if cleaned["key"] != "too   many   spaces":
        result.record_fail("sanitize_basic_multiple_whitespace", "Internal spaces affected")
    else:
        result.record_pass("sanitize_basic_multiple_whitespace")


def test_sanitize_basic_newlines(result):
    data = {"key": "\n  value  \n"}
    cleaned = sanitize_basic_fields(data)
    if cleaned["key"] != "value":
        result.record_fail("sanitize_basic_newlines", f"Got '{cleaned['key']}'")
    else:
        result.record_pass("sanitize_basic_newlines")


def test_sanitize_basic_tabs(result):
    data = {"key": "\t\tvalue\t\t"}
    cleaned = sanitize_basic_fields(data)
    if cleaned["key"] != "value":
        result.record_fail("sanitize_basic_tabs", f"Got '{cleaned['key']}'")
    else:
        result.record_pass("sanitize_basic_tabs")


def test_sanitize_content_empty_string(result):
    data = {"content": ""}
    cleaned = sanitize_content_length(data)
    if cleaned["content"] != "":
        result.record_fail("sanitize_content_empty_string", "Empty string changed")
    else:
        result.record_pass("sanitize_content_empty_string")


def test_sanitize_content_non_string(result):
    data = {"content": 123}
    cleaned = sanitize_content_length(data)
    if cleaned["content"] != 123:
        result.record_fail("sanitize_content_non_string", "Non-string changed")
    else:
        result.record_pass("sanitize_content_non_string")


def test_sanitize_types_tokens_already_int(result):
    data = {"tokens_in": 42, "tokens_out": 99}
    cleaned = sanitize_types(data)
    if cleaned["tokens_in"] != 42 or cleaned["tokens_out"] != 99:
        result.record_fail("sanitize_types_tokens_already_int", "Ints changed")
    else:
        result.record_pass("sanitize_types_tokens_already_int")


def test_sanitize_types_meta_empty_dict(result):
    data = {"meta": {}}
    try:
        cleaned = sanitize_types(data)
        if cleaned["meta"] != {}:
            result.record_fail("sanitize_types_meta_empty_dict", "Empty dict changed")
        else:
            result.record_pass("sanitize_types_meta_empty_dict")
    except Exception as e:
        result.record_fail("sanitize_types_meta_empty_dict", str(e))


def test_sanitize_types_meta_nested(result):
    data = {"meta": {"nested": {"deep": "value"}}}
    try:
        cleaned = sanitize_types(data)
        if cleaned["meta"]["nested"]["deep"] != "value":
            result.record_fail("sanitize_types_meta_nested", "Nested value changed")
        else:
            result.record_pass("sanitize_types_meta_nested")
    except Exception as e:
        result.record_fail("sanitize_types_meta_nested", str(e))


def test_sanitize_basic_preserves_booleans(result):
    data = {"flag": True}
    cleaned = sanitize_basic_fields(data)
    if cleaned["flag"] is not True:
        result.record_fail("sanitize_basic_preserves_booleans", "Boolean changed")
    else:
        result.record_pass("sanitize_basic_preserves_booleans")


def test_sanitize_basic_preserves_lists(result):
    data = {"items": [1, 2, 3]}
    cleaned = sanitize_basic_fields(data)
    if cleaned["items"] != [1, 2, 3]:
        result.record_fail("sanitize_basic_preserves_lists", "List changed")
    else:
        result.record_pass("sanitize_basic_preserves_lists")


def test_sanitize_basic_zero_value(result):
    data = {"count": 0}
    cleaned = sanitize_basic_fields(data)
    if "count" not in cleaned or cleaned["count"] != 0:
        result.record_fail("sanitize_basic_zero_value", "Zero removed or changed")
    else:
        result.record_pass("sanitize_basic_zero_value")


def test_sanitize_basic_false_value(result):
    data = {"flag": False}
    cleaned = sanitize_basic_fields(data)
    if "flag" not in cleaned or cleaned["flag"] is not False:
        result.record_fail("sanitize_basic_false_value", "False removed or changed")
    else:
        result.record_pass("sanitize_basic_false_value")


def test_sanitize_basic_empty_string_preserved(result):
    data = {"text": ""}
    cleaned = sanitize_basic_fields(data)
    if "text" not in cleaned or cleaned["text"] != "":
        result.record_fail("sanitize_basic_empty_string_preserved", "Empty string removed")
    else:
        result.record_pass("sanitize_basic_empty_string_preserved")


def test_sanitize_content_unicode(result):
    data = {"content": "Hello 世界 " * 10000}
    cleaned = sanitize_content_length(data)
    if len(cleaned["content"]) > 50000:
        result.record_fail("sanitize_content_unicode", "Unicode not truncated properly")
    else:
        result.record_pass("sanitize_content_unicode")


def test_sanitize_types_tokens_negative_float(result):
    data = {"tokens_in": -5.5}
    cleaned = sanitize_types(data)
    if cleaned["tokens_in"] != -5:
        result.record_fail("sanitize_types_tokens_negative_float", "Negative float not converted")
    else:
        result.record_pass("sanitize_types_tokens_negative_float")


def test_sanitize_types_tokens_zero(result):
    data = {"tokens_in": 0.0}
    cleaned = sanitize_types(data)
    if cleaned["tokens_in"] != 0:
        result.record_fail("sanitize_types_tokens_zero", "Zero float not converted")
    else:
        result.record_pass("sanitize_types_tokens_zero")


def test_sanitize_types_meta_list_error(result):
    data = {"meta": ["list", "not", "dict"]}
    try:
        sanitize_types(data)
        result.record_fail("sanitize_types_meta_list_error", "List accepted for meta")
    except ContractSanitizationError:
        result.record_pass("sanitize_types_meta_list_error")
    except Exception as e:
        result.record_fail("sanitize_types_meta_list_error", f"Wrong error: {e}")


def test_sanitize_types_meta_none_error(result):
    data = {"meta": None}
    try:
        sanitize_types(data)
        result.record_fail("sanitize_types_meta_none_error", "None accepted for meta")
    except ContractSanitizationError:
        result.record_pass("sanitize_types_meta_none_error")
    except Exception as e:
        result.record_fail("sanitize_types_meta_none_error", f"Wrong error: {e}")


############################################################
# SECTION 2 — SCHEMA TESTS
############################################################

def test_schema_valid_minimal(result):
    data = make_valid_contract()
    try:
        validate_schema(data)
        result.record_pass("schema_valid_minimal")
    except Exception as e:
        result.record_fail("schema_valid_minimal", str(e))


def test_schema_missing_type(result):
    data = make_valid_contract()
    del data["type"]
    try:
        validate_schema(data)
        result.record_fail("schema_missing_type", "No error raised")
    except ContractSchemaError:
        result.record_pass("schema_missing_type")
    except Exception as e:
        result.record_fail("schema_missing_type", f"Wrong error: {e}")


def test_schema_missing_provider(result):
    data = make_valid_contract()
    del data["provider"]
    try:
        validate_schema(data)
        result.record_fail("schema_missing_provider", "No error raised")
    except ContractSchemaError:
        result.record_pass("schema_missing_provider")
    except Exception as e:
        result.record_fail("schema_missing_provider", f"Wrong error: {e}")


def test_schema_missing_model(result):
    data = make_valid_contract()
    del data["model"]
    try:
        validate_schema(data)
        result.record_fail("schema_missing_model", "No error raised")
    except ContractSchemaError:
        result.record_pass("schema_missing_model")
    except Exception as e:
        result.record_fail("schema_missing_model", f"Wrong error: {e}")


def test_schema_missing_content(result):
    data = make_valid_contract()
    del data["content"]
    try:
        validate_schema(data)
        result.record_fail("schema_missing_content", "No error raised")
    except ContractSchemaError:
        result.record_pass("schema_missing_content")
    except Exception as e:
        result.record_fail("schema_missing_content", f"Wrong error: {e}")


def test_schema_extra_field(result):
    data = make_valid_contract()
    data["extra_field"] = "not allowed"
    try:
        validate_schema(data)
        result.record_fail("schema_extra_field", "Extra field allowed")
    except ContractSchemaError:
        result.record_pass("schema_extra_field")
    except Exception as e:
        result.record_fail("schema_extra_field", f"Wrong error: {e}")


def test_schema_invalid_type_enum(result):
    data = corrupt_field(make_valid_contract(), "type", "invalid_type")
    try:
        validate_schema(data)
        result.record_fail("schema_invalid_type_enum", "Invalid enum accepted")
    except ContractSchemaError:
        result.record_pass("schema_invalid_type_enum")
    except Exception as e:
        result.record_fail("schema_invalid_type_enum", f"Wrong error: {e}")


def test_schema_invalid_provider_enum(result):
    data = corrupt_field(make_valid_contract(), "provider", "google")
    try:
        validate_schema(data)
        result.record_fail("schema_invalid_provider_enum", "Invalid provider accepted")
    except ContractSchemaError:
        result.record_pass("schema_invalid_provider_enum")
    except Exception as e:
        result.record_fail("schema_invalid_provider_enum", f"Wrong error: {e}")


def test_schema_type_completion(result):
    data = corrupt_field(make_valid_contract(), "type", "completion")
    try:
        validate_schema(data)
        result.record_pass("schema_type_completion")
    except Exception as e:
        result.record_fail("schema_type_completion", str(e))


def test_schema_type_chat(result):
    data = corrupt_field(make_valid_contract(), "type", "chat")
    try:
        validate_schema(data)
        result.record_pass("schema_type_chat")
    except Exception as e:
        result.record_fail("schema_type_chat", str(e))


def test_schema_type_tool(result):
    data = corrupt_field(make_valid_contract(), "type", "tool")
    try:
        validate_schema(data)
        result.record_pass("schema_type_tool")
    except Exception as e:
        result.record_fail("schema_type_tool", str(e))


def test_schema_provider_openai(result):
    data = corrupt_field(make_valid_contract(), "provider", "openai")
    try:
        validate_schema(data)
        result.record_pass("schema_provider_openai")
    except Exception as e:
        result.record_fail("schema_provider_openai", str(e))


def test_schema_provider_anthropic(result):
    data = corrupt_field(make_valid_contract(), "provider", "anthropic")
    try:
        validate_schema(data)
        result.record_pass("schema_provider_anthropic")
    except Exception as e:
        result.record_fail("schema_provider_anthropic", str(e))


def test_schema_provider_mistral(result):
    data = corrupt_field(make_valid_contract(), "provider", "mistral")
    try:
        validate_schema(data)
        result.record_pass("schema_provider_mistral")
    except Exception as e:
        result.record_fail("schema_provider_mistral", str(e))


def test_schema_content_not_string(result):
    data = corrupt_field(make_valid_contract(), "content", 123)
    try:
        validate_schema(data)
        result.record_fail("schema_content_not_string", "Integer accepted for content")
    except ContractSchemaError:
        result.record_pass("schema_content_not_string")
    except Exception as e:
        result.record_fail("schema_content_not_string", f"Wrong error: {e}")


def test_schema_model_not_string(result):
    data = corrupt_field(make_valid_contract(), "model", 123)
    try:
        validate_schema(data)
        result.record_fail("schema_model_not_string", "Integer accepted for model")
    except ContractSchemaError:
        result.record_pass("schema_model_not_string")
    except Exception as e:
        result.record_fail("schema_model_not_string", f"Wrong error: {e}")


def test_schema_tokens_in_valid(result):
    data = make_valid_contract()
    data["tokens_in"] = 100
    try:
        validate_schema(data)
        result.record_pass("schema_tokens_in_valid")
    except Exception as e:
        result.record_fail("schema_tokens_in_valid", str(e))


def test_schema_tokens_out_valid(result):
    data = make_valid_contract()
    data["tokens_out"] = 200
    try:
        validate_schema(data)
        result.record_pass("schema_tokens_out_valid")
    except Exception as e:
        result.record_fail("schema_tokens_out_valid", str(e))


def test_schema_tokens_in_negative(result):
    data = make_valid_contract()
    data["tokens_in"] = -5
    try:
        validate_schema(data)
        result.record_fail("schema_tokens_in_negative", "Negative tokens accepted")
    except ContractSchemaError:
        result.record_pass("schema_tokens_in_negative")
    except Exception as e:
        result.record_fail("schema_tokens_in_negative", f"Wrong error: {e}")


def test_schema_tokens_out_negative(result):
    data = make_valid_contract()
    data["tokens_out"] = -10
    try:
        validate_schema(data)
        result.record_fail("schema_tokens_out_negative", "Negative tokens accepted")
    except ContractSchemaError:
        result.record_pass("schema_tokens_out_negative")
    except Exception as e:
        result.record_fail("schema_tokens_out_negative", f"Wrong error: {e}")


def test_schema_tokens_in_zero(result):
    data = make_valid_contract()
    data["tokens_in"] = 0
    try:
        validate_schema(data)
        result.record_pass("schema_tokens_in_zero")
    except Exception as e:
        result.record_fail("schema_tokens_in_zero", str(e))


def test_schema_tokens_in_not_int(result):
    data = make_valid_contract()
    data["tokens_in"] = "not_int"
    try:
        validate_schema(data)
        result.record_fail("schema_tokens_in_not_int", "String accepted for tokens")
    except ContractSchemaError:
        result.record_pass("schema_tokens_in_not_int")
    except Exception as e:
        result.record_fail("schema_tokens_in_not_int", f"Wrong error: {e}")


def test_schema_meta_valid(result):
    data = make_valid_contract()
    data["meta"] = {"key": "value"}
    try:
        validate_schema(data)
        result.record_pass("schema_meta_valid")
    except Exception as e:
        result.record_fail("schema_meta_valid", str(e))


def test_schema_meta_not_object(result):
    data = make_valid_contract()
    data["meta"] = "not an object"
    try:
        validate_schema(data)
        result.record_fail("schema_meta_not_object", "String accepted for meta")
    except ContractSchemaError:
        result.record_pass("schema_meta_not_object")
    except Exception as e:
        result.record_fail("schema_meta_not_object", f"Wrong error: {e}")


def test_schema_meta_empty(result):
    data = make_valid_contract()
    data["meta"] = {}
    try:
        validate_schema(data)
        result.record_pass("schema_meta_empty")
    except Exception as e:
        result.record_fail("schema_meta_empty", str(e))


def test_schema_no_mutation(result):
    data = make_valid_contract()
    original = deep_copy(data)
    try:
        validate_schema(data)
        if data != original:
            result.record_fail("schema_no_mutation", "Input was mutated")
        else:
            result.record_pass("schema_no_mutation")
    except Exception as e:
        result.record_fail("schema_no_mutation", str(e))


def test_schema_content_empty(result):
    data = corrupt_field(make_valid_contract(), "content", "")
    try:
        validate_schema(data)
        result.record_pass("schema_content_empty")
    except Exception as e:
        result.record_fail("schema_content_empty", str(e))


def test_schema_content_very_long(result):
    data = corrupt_field(make_valid_contract(), "content", "x" * 100000)
    try:
        validate_schema(data)
        result.record_pass("schema_content_very_long")
    except Exception as e:
        result.record_fail("schema_content_very_long", str(e))


def test_schema_model_empty(result):
    data = corrupt_field(make_valid_contract(), "model", "")
    try:
        validate_schema(data)
        result.record_pass("schema_model_empty")
    except Exception as e:
        result.record_fail("schema_model_empty", str(e))


def test_schema_provider_empty(result):
    data = corrupt_field(make_valid_contract(), "provider", "")
    try:
        validate_schema(data)
        result.record_fail("schema_provider_empty", "Empty provider in enum")
    except ContractSchemaError:
        result.record_pass("schema_provider_empty")
    except Exception as e:
        result.record_fail("schema_provider_empty", f"Wrong error: {e}")


def test_schema_type_empty(result):
    data = corrupt_field(make_valid_contract(), "type", "")
    try:
        validate_schema(data)
        result.record_fail("schema_type_empty", "Empty type in enum")
    except ContractSchemaError:
        result.record_pass("schema_type_empty")
    except Exception as e:
        result.record_fail("schema_type_empty", f"Wrong error: {e}")


def test_schema_tokens_boolean(result):
    data = make_valid_contract()
    data["tokens_in"] = True
    try:
        validate_schema(data)
        result.record_fail("schema_tokens_boolean", "Boolean accepted as integer")
    except ContractSchemaError:
        result.record_pass("schema_tokens_boolean")
    except Exception as e:
        result.record_fail("schema_tokens_boolean", f"Wrong error: {e}")


def test_schema_multiple_extra_fields(result):
    data = make_valid_contract()
    data["extra1"] = "val1"
    data["extra2"] = "val2"
    try:
        validate_schema(data)
        result.record_fail("schema_multiple_extra_fields", "Multiple extra fields allowed")
    except ContractSchemaError:
        result.record_pass("schema_multiple_extra_fields")
    except Exception as e:
        result.record_fail("schema_multiple_extra_fields", f"Wrong error: {e}")


def test_schema_all_fields_present(result):
    data = {
        "type": "completion",
        "provider": "openai",
        "model": "gpt-4",
        "content": "test",
        "tokens_in": 10,
        "tokens_out": 20,
        "meta": {"key": "val"}
    }
    try:
        validate_schema(data)
        result.record_pass("schema_all_fields_present")
    except Exception as e:
        result.record_fail("schema_all_fields_present", str(e))


def test_schema_provider_case_sensitive(result):
    data = corrupt_field(make_valid_contract(), "provider", "OpenAI")
    try:
        validate_schema(data)
        result.record_fail("schema_provider_case_sensitive", "Case variant accepted")
    except ContractSchemaError:
        result.record_pass("schema_provider_case_sensitive")
    except Exception as e:
        result.record_fail("schema_provider_case_sensitive", f"Wrong error: {e}")


def test_schema_type_case_sensitive(result):
    data = corrupt_field(make_valid_contract(), "type", "Completion")
    try:
        validate_schema(data)
        result.record_fail("schema_type_case_sensitive", "Case variant accepted")
    except ContractSchemaError:
        result.record_pass("schema_type_case_sensitive")
    except Exception as e:
        result.record_fail("schema_type_case_sensitive", f"Wrong error: {e}")


############################################################
# SECTION 3 — STRICT MODE TESTS
############################################################

def test_strict_mode_valid(result):
    data = make_valid_contract()
    try:
        cleaned = validate_contract(data, strict=True)
        result.record_pass("strict_mode_valid")
    except Exception as e:
        result.record_fail("strict_mode_valid", str(e))


def test_strict_mode_negative_tokens_in(result):
    data = make_valid_contract()
    data["tokens_in"] = -5
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_negative_tokens_in", "Negative tokens allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_negative_tokens_in")
    except Exception as e:
        result.record_fail("strict_mode_negative_tokens_in", f"Wrong error: {e}")


def test_strict_mode_negative_tokens_out(result):
    data = make_valid_contract()
    data["tokens_out"] = -10
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_negative_tokens_out", "Negative tokens allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_negative_tokens_out")
    except Exception as e:
        result.record_fail("strict_mode_negative_tokens_out", f"Wrong error: {e}")


def test_strict_mode_empty_provider(result):
    data = make_valid_contract()
    data["provider"] = ""
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_empty_provider", "Empty provider allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_empty_provider")
    except Exception as e:
        result.record_fail("strict_mode_empty_provider", f"Wrong error: {e}")


def test_strict_mode_empty_model(result):
    data = make_valid_contract()
    data["model"] = ""
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_empty_model", "Empty model allowed")
    except StrictModeViolation:
        result.record_pass("strict_mode_empty_model")
    except Exception as e:
        result.record_fail("strict_mode_empty_model", f"Wrong error: {e}")


def test_strict_mode_empty_type(result):
    data = make_valid_contract()
    data["type"] = ""
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_empty_type", "Empty type allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_empty_type")
    except Exception as e:
        result.record_fail("strict_mode_empty_type", f"Wrong error: {e}")


def test_strict_mode_whitespace_provider(result):
    data = make_valid_contract()
    data["provider"] = "   "
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_whitespace_provider", "Whitespace provider allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_whitespace_provider")
    except Exception as e:
        result.record_fail("strict_mode_whitespace_provider", f"Wrong error: {e}")


def test_strict_mode_whitespace_model(result):
    data = make_valid_contract()
    data["model"] = "   "
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_whitespace_model", "Whitespace model allowed")
    except StrictModeViolation:
        result.record_pass("strict_mode_whitespace_model")
    except Exception as e:
        result.record_fail("strict_mode_whitespace_model", f"Wrong error: {e}")


def test_strict_mode_meta_not_dict(result):
    data = make_valid_contract()
    data["meta"] = "string"
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_meta_not_dict", "Non-dict meta allowed")
    except (StrictModeViolation, ContractSanitizationError, ContractSchemaError):
        result.record_pass("strict_mode_meta_not_dict")
    except Exception as e:
        result.record_fail("strict_mode_meta_not_dict", f"Wrong error: {e}")


def test_strict_mode_tokens_in_zero(result):
    data = make_valid_contract()
    data["tokens_in"] = 0
    try:
        validate_contract(data, strict=True)
        result.record_pass("strict_mode_tokens_in_zero")
    except Exception as e:
        result.record_fail("strict_mode_tokens_in_zero", str(e))


def test_non_strict_mode_negative_tokens(result):
    data = make_valid_contract()
    data["tokens_in"] = -5
    try:
        validate_contract(data, strict=False)
        result.record_fail("non_strict_mode_negative_tokens", "Schema should still reject")
    except ContractSchemaError:
        result.record_pass("non_strict_mode_negative_tokens")
    except Exception as e:
        result.record_fail("non_strict_mode_negative_tokens", f"Wrong error: {e}")


def test_strict_mode_missing_required(result):
    data = make_valid_contract()
    del data["content"]
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_missing_required", "Missing field allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_missing_required")
    except Exception as e:
        result.record_fail("strict_mode_missing_required", f"Wrong error: {e}")


def test_strict_mode_extra_field(result):
    data = make_valid_contract()
    data["extra"] = "value"
    try:
        validate_contract(data, strict=True)
        result.record_fail("strict_mode_extra_field", "Extra field allowed")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("strict_mode_extra_field")
    except Exception as e:
        result.record_fail("strict_mode_extra_field", f"Wrong error: {e}")


def test_strict_mode_valid_with_meta(result):
    data = make_valid_contract()
    data["meta"] = {"test": "value"}
    try:
        validate_contract(data, strict=True)
        result.record_pass("strict_mode_valid_with_meta")
    except Exception as e:
        result.record_fail("strict_mode_valid_with_meta", str(e))


def test_strict_mode_valid_with_tokens(result):
    data = make_valid_contract()
    data["tokens_in"] = 100
    data["tokens_out"] = 200
    try:
        validate_contract(data, strict=True)
        result.record_pass("strict_mode_valid_with_tokens")
    except Exception as e:
        result.record_fail("strict_mode_valid_with_tokens", str(e))


def test_strict_mode_all_fields(result):
    data = {
        "type": "chat",
        "provider": "anthropic",
        "model": "claude-3",
        "content": "test content",
        "tokens_in": 50,
        "tokens_out": 100,
        "meta": {"session": "123"}
    }
    try:
        validate_contract(data, strict=True)
        result.record_pass("strict_mode_all_fields")
    except Exception as e:
        result.record_fail("strict_mode_all_fields", str(e))


def test_strict_mode_provider_whitespace_trimmed(result):
    data = make_valid_contract()
    data["provider"] = "  openai  "
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["provider"] == "openai":
            result.record_pass("strict_mode_provider_whitespace_trimmed")
        else:
            result.record_fail("strict_mode_provider_whitespace_trimmed", "Whitespace not trimmed")
    except Exception as e:
        result.record_fail("strict_mode_provider_whitespace_trimmed", str(e))


def test_strict_mode_model_whitespace_trimmed(result):
    data = make_valid_contract()
    data["model"] = "  gpt-4  "
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["model"] == "gpt-4":
            result.record_pass("strict_mode_model_whitespace_trimmed")
        else:
            result.record_fail("strict_mode_model_whitespace_trimmed", "Whitespace not trimmed")
    except Exception as e:
        result.record_fail("strict_mode_model_whitespace_trimmed", str(e))


def test_strict_mode_content_truncated(result):
    data = make_valid_contract()
    data["content"] = "x" * 100000
    try:
        cleaned = validate_contract(data, strict=True)
        if len(cleaned["content"]) == 50000:
            result.record_pass("strict_mode_content_truncated")
        else:
            result.record_fail("strict_mode_content_truncated", f"Length {len(cleaned['content'])}")
    except Exception as e:
        result.record_fail("strict_mode_content_truncated", str(e))


def test_strict_mode_float_tokens_converted(result):
    data = make_valid_contract()
    data["tokens_in"] = 42.7
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["tokens_in"] == 42 and isinstance(cleaned["tokens_in"], int):
            result.record_pass("strict_mode_float_tokens_converted")
        else:
            result.record_fail("strict_mode_float_tokens_converted", "Float not converted")
    except Exception as e:
        result.record_fail("strict_mode_float_tokens_converted", str(e))


############################################################
# SECTION 4 — MUTATION & SECURITY TESTS
############################################################

def test_no_mutation_sanitize_basic(result):
    data = {"key": "  value  ", "none": None}
    original = deep_copy(data)
    sanitize_basic_fields(data)
    if data == original:
        result.record_pass("no_mutation_sanitize_basic")
    else:
        result.record_fail("no_mutation_sanitize_basic", "Input mutated")


def test_no_mutation_sanitize_content(result):
    data = {"content": "x" * 100000}
    original = deep_copy(data)
    sanitize_content_length(data)
    if data == original:
        result.record_pass("no_mutation_sanitize_content")
    else:
        result.record_fail("no_mutation_sanitize_content", "Input mutated")


def test_no_mutation_sanitize_types(result):
    data = {"tokens_in": 42.7}
    original = deep_copy(data)
    sanitize_types(data)
    if data == original:
        result.record_pass("no_mutation_sanitize_types")
    else:
        result.record_fail("no_mutation_sanitize_types", "Input mutated")


def test_no_mutation_validate_schema(result):
    data = make_valid_contract()
    original = deep_copy(data)
    try:
        validate_schema(data)
        if data == original:
            result.record_pass("no_mutation_validate_schema")
        else:
            result.record_fail("no_mutation_validate_schema", "Input mutated")
    except Exception as e:
        result.record_fail("no_mutation_validate_schema", str(e))


def test_no_mutation_validate_contract(result):
    data = make_valid_contract()
    original = deep_copy(data)
    try:
        validate_contract(data, strict=True)
        if data == original:
            result.record_pass("no_mutation_validate_contract")
        else:
            result.record_fail("no_mutation_validate_contract", "Input mutated")
    except Exception as e:
        result.record_fail("no_mutation_validate_contract", str(e))


def test_no_new_fields_added(result):
    data = make_valid_contract()
    try:
        cleaned = validate_contract(data, strict=True)
        if set(cleaned.keys()) == set(data.keys()):
            result.record_pass("no_new_fields_added")
        else:
            result.record_fail("no_new_fields_added", f"Keys changed: {cleaned.keys()}")
    except Exception as e:
        result.record_fail("no_new_fields_added", str(e))


def test_sanitize_preserves_nested_structures(result):
    data = {"meta": {"nested": {"deep": "value"}}}
    cleaned = sanitize_types(data)
    if cleaned["meta"]["nested"]["deep"] == "value":
        result.record_pass("sanitize_preserves_nested_structures")
    else:
        result.record_fail("sanitize_preserves_nested_structures", "Nested value changed")


def test_no_side_effects_multiple_calls(result):
    data = make_valid_contract()
    try:
        cleaned1 = validate_contract(data, strict=True)
        cleaned2 = validate_contract(data, strict=True)
        if cleaned1 == cleaned2:
            result.record_pass("no_side_effects_multiple_calls")
        else:
            result.record_fail("no_side_effects_multiple_calls", "Results differ")
    except Exception as e:
        result.record_fail("no_side_effects_multiple_calls", str(e))


def test_independent_sanitization_steps(result):
    data = {"key": "  value  ", "content": "x" * 100000, "tokens_in": 42.7}
    step1 = sanitize_basic_fields(data)
    step2 = sanitize_content_length(step1)
    step3 = sanitize_types(step2)
    if step3["key"] == "value" and len(step3["content"]) == 50000 and step3["tokens_in"] == 42:
        result.record_pass("independent_sanitization_steps")
    else:
        result.record_fail("independent_sanitization_steps", "Pipeline failed")


def test_deep_copy_independence(result):
    data = make_valid_contract()
    copy1 = deep_copy(data)
    copy1["model"] = "changed"
    if data["model"] != "changed":
        result.record_pass("deep_copy_independence")
    else:
        result.record_fail("deep_copy_independence", "Deep copy not independent")


def test_sanitize_does_not_add_fields(result):
    data = make_valid_contract()
    cleaned = sanitize_basic_fields(data)
    if len(cleaned.keys()) <= len(data.keys()):
        result.record_pass("sanitize_does_not_add_fields")
    else:
        result.record_fail("sanitize_does_not_add_fields", "Fields added")


def test_sanitize_removes_only_none(result):
    data = {"a": None, "b": "value", "c": 0, "d": False}
    cleaned = sanitize_basic_fields(data)
    if "a" not in cleaned and "b" in cleaned and "c" in cleaned and "d" in cleaned:
        result.record_pass("sanitize_removes_only_none")
    else:
        result.record_fail("sanitize_removes_only_none", "Wrong values removed")


def test_validate_contract_returns_new_dict(result):
    data = make_valid_contract()
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned is not data:
            result.record_pass("validate_contract_returns_new_dict")
        else:
            result.record_fail("validate_contract_returns_new_dict", "Same object returned")
    except Exception as e:
        result.record_fail("validate_contract_returns_new_dict", str(e))


def test_sanitize_basic_returns_new_dict(result):
    data = {"key": "value"}
    cleaned = sanitize_basic_fields(data)
    if cleaned is not data:
        result.record_pass("sanitize_basic_returns_new_dict")
    else:
        result.record_fail("sanitize_basic_returns_new_dict", "Same object returned")


def test_sanitize_content_returns_new_dict(result):
    data = {"content": "x" * 100000}
    cleaned = sanitize_content_length(data)
    if cleaned is not data:
        result.record_pass("sanitize_content_returns_new_dict")
    else:
        result.record_fail("sanitize_content_returns_new_dict", "Same object returned")


def test_sanitize_types_returns_new_dict(result):
    data = {"tokens_in": 42.7}
    cleaned = sanitize_types(data)
    if cleaned is not data:
        result.record_pass("sanitize_types_returns_new_dict")
    else:
        result.record_fail("sanitize_types_returns_new_dict", "Same object returned")


############################################################
# SECTION 5 — FULL PIPELINE TESTS
############################################################

def test_pipeline_valid_minimal(result):
    data = make_valid_contract()
    try:
        cleaned = validate_contract(data, strict=True)
        if all(k in cleaned for k in ["type", "provider", "model", "content"]):
            result.record_pass("pipeline_valid_minimal")
        else:
            result.record_fail("pipeline_valid_minimal", "Required fields missing")
    except Exception as e:
        result.record_fail("pipeline_valid_minimal", str(e))


def test_pipeline_with_whitespace(result):
    data = {
        "type": "  completion  ",
        "provider": "  openai  ",
        "model": "  gpt-4  ",
        "content": "  test  "
    }
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["type"] == "completion" and cleaned["provider"] == "openai":
            result.record_pass("pipeline_with_whitespace")
        else:
            result.record_fail("pipeline_with_whitespace", "Whitespace not trimmed")
    except Exception as e:
        result.record_fail("pipeline_with_whitespace", str(e))


def test_pipeline_with_huge_content(result):
    data = make_valid_contract()
    data["content"] = "x" * 200000
    try:
        cleaned = validate_contract(data, strict=True)
        if len(cleaned["content"]) == 50000:
            result.record_pass("pipeline_with_huge_content")
        else:
            result.record_fail("pipeline_with_huge_content", f"Length {len(cleaned['content'])}")
    except Exception as e:
        result.record_fail("pipeline_with_huge_content", str(e))


def test_pipeline_with_float_tokens(result):
    data = make_valid_contract()
    data["tokens_in"] = 100.5
    data["tokens_out"] = 200.9
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["tokens_in"] == 100 and cleaned["tokens_out"] == 200:
            result.record_pass("pipeline_with_float_tokens")
        else:
            result.record_fail("pipeline_with_float_tokens", "Floats not converted")
    except Exception as e:
        result.record_fail("pipeline_with_float_tokens", str(e))


def test_pipeline_strict_vs_non_strict(result):
    data = make_valid_contract()
    data["model"] = ""
    try:
        validate_contract(data, strict=True)
        result.record_fail("pipeline_strict_vs_non_strict", "Strict mode passed with empty model")
    except StrictModeViolation:
        result.record_pass("pipeline_strict_vs_non_strict")
    except Exception as e:
        result.record_fail("pipeline_strict_vs_non_strict", f"Wrong error: {e}")


def test_pipeline_all_sanitizations(result):
    data = {
        "type": "  chat  ",
        "provider": "  anthropic  ",
        "model": "  claude  ",
        "content": "x" * 100000,
        "tokens_in": 50.5,
        "tokens_out": 100.9,
        "meta": {},
        "extra": None
    }
    try:
        cleaned = validate_contract(data, strict=False)
        if (cleaned["type"] == "chat" and len(cleaned["content"]) == 50000 and
            cleaned["tokens_in"] == 50 and "extra" not in cleaned):
            result.record_pass("pipeline_all_sanitizations")
        else:
            result.record_fail("pipeline_all_sanitizations", "Sanitization incomplete")
    except Exception as e:
        result.record_fail("pipeline_all_sanitizations", str(e))


def test_pipeline_preserves_valid_data(result):
    data = {
        "type": "tool",
        "provider": "mistral",
        "model": "mistral-large",
        "content": "result",
        "tokens_in": 10,
        "tokens_out": 20,
        "meta": {"id": "123"}
    }
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned == data:
            result.record_pass("pipeline_preserves_valid_data")
        else:
            result.record_fail("pipeline_preserves_valid_data", "Valid data changed")
    except Exception as e:
        result.record_fail("pipeline_preserves_valid_data", str(e))


def test_pipeline_invalid_raises_error(result):
    data = make_valid_contract()
    del data["provider"]
    try:
        validate_contract(data, strict=True)
        result.record_fail("pipeline_invalid_raises_error", "No error raised")
    except ContractSchemaError:
        result.record_pass("pipeline_invalid_raises_error")
    except Exception as e:
        result.record_fail("pipeline_invalid_raises_error", f"Wrong error: {e}")


############################################################
# SECTION 6 — ERROR-HANDLING TESTS
############################################################

def test_error_contract_validation_error_exists(result):
    try:
        raise ContractValidationError("test")
    except ContractValidationError as e:
        result.record_pass("error_contract_validation_error_exists")
    except Exception as e:
        result.record_fail("error_contract_validation_error_exists", str(e))


def test_error_contract_schema_error_exists(result):
    try:
        raise ContractSchemaError("test")
    except ContractSchemaError as e:
        result.record_pass("error_contract_schema_error_exists")
    except Exception as e:
        result.record_fail("error_contract_schema_error_exists", str(e))


def test_error_contract_sanitization_error_exists(result):
    try:
        raise ContractSanitizationError("test")
    except ContractSanitizationError as e:
        result.record_pass("error_contract_sanitization_error_exists")
    except Exception as e:
        result.record_fail("error_contract_sanitization_error_exists", str(e))


def test_error_strict_mode_violation_exists(result):
    try:
        raise StrictModeViolation("test")
    except StrictModeViolation as e:
        result.record_pass("error_strict_mode_violation_exists")
    except Exception as e:
        result.record_fail("error_strict_mode_violation_exists", str(e))


def test_error_sanitize_types_meta_not_dict(result):
    data = {"meta": []}
    try:
        sanitize_types(data)
        result.record_fail("error_sanitize_types_meta_not_dict", "No error raised")
    except ContractSanitizationError:
        result.record_pass("error_sanitize_types_meta_not_dict")
    except Exception as e:
        result.record_fail("error_sanitize_types_meta_not_dict", f"Wrong error: {e}")


def test_error_validate_schema_missing_field(result):
    data = make_valid_contract()
    del data["type"]
    try:
        validate_schema(data)
        result.record_fail("error_validate_schema_missing_field", "No error raised")
    except ContractSchemaError:
        result.record_pass("error_validate_schema_missing_field")
    except Exception as e:
        result.record_fail("error_validate_schema_missing_field", f"Wrong error: {e}")


def test_error_validate_schema_extra_field(result):
    data = make_valid_contract()
    data["invalid"] = "field"
    try:
        validate_schema(data)
        result.record_fail("error_validate_schema_extra_field", "No error raised")
    except ContractSchemaError:
        result.record_pass("error_validate_schema_extra_field")
    except Exception as e:
        result.record_fail("error_validate_schema_extra_field", f"Wrong error: {e}")


def test_error_validate_schema_invalid_type(result):
    data = corrupt_field(make_valid_contract(), "content", 123)
    try:
        validate_schema(data)
        result.record_fail("error_validate_schema_invalid_type", "No error raised")
    except ContractSchemaError:
        result.record_pass("error_validate_schema_invalid_type")
    except Exception as e:
        result.record_fail("error_validate_schema_invalid_type", f"Wrong error: {e}")


def test_error_validate_schema_invalid_enum(result):
    data = corrupt_field(make_valid_contract(), "provider", "invalid")
    try:
        validate_schema(data)
        result.record_fail("error_validate_schema_invalid_enum", "No error raised")
    except ContractSchemaError:
        result.record_pass("error_validate_schema_invalid_enum")
    except Exception as e:
        result.record_fail("error_validate_schema_invalid_enum", f"Wrong error: {e}")


def test_error_strict_mode_negative_tokens(result):
    data = make_valid_contract()
    data["tokens_in"] = -5
    try:
        validate_contract(data, strict=True)
        result.record_fail("error_strict_mode_negative_tokens", "No error raised")
    except (StrictModeViolation, ContractSchemaError):
        result.record_pass("error_strict_mode_negative_tokens")
    except Exception as e:
        result.record_fail("error_strict_mode_negative_tokens", f"Wrong error: {e}")


def test_error_strict_mode_empty_string(result):
    data = make_valid_contract()
    data["model"] = ""
    try:
        validate_contract(data, strict=True)
        result.record_fail("error_strict_mode_empty_string", "No error raised")
    except StrictModeViolation:
        result.record_pass("error_strict_mode_empty_string")
    except Exception as e:
        result.record_fail("error_strict_mode_empty_string", f"Wrong error: {e}")


############################################################
# SECTION 7 — EXTREME EDGE CASES
############################################################

def test_edge_null_byte_in_content(result):
    data = make_valid_contract()
    data["content"] = "test\x00content"
    try:
        cleaned = validate_contract(data, strict=True)
        result.record_pass("edge_null_byte_in_content")
    except Exception as e:
        result.record_fail("edge_null_byte_in_content", str(e))


def test_edge_unicode_in_content(result):
    data = make_valid_contract()
    data["content"] = "Hello 世界 🌍"
    try:
        cleaned = validate_contract(data, strict=True)
        if "世界" in cleaned["content"]:
            result.record_pass("edge_unicode_in_content")
        else:
            result.record_fail("edge_unicode_in_content", "Unicode lost")
    except Exception as e:
        result.record_fail("edge_unicode_in_content", str(e))


def test_edge_empty_dict(result):
    data = {}
    try:
        validate_contract(data, strict=True)
        result.record_fail("edge_empty_dict", "Empty dict accepted")
    except ContractSchemaError:
        result.record_pass("edge_empty_dict")
    except Exception as e:
        result.record_fail("edge_empty_dict", f"Wrong error: {e}")


def test_edge_deeply_nested_meta(result):
    data = make_valid_contract()
    data["meta"] = {"l1": {"l2": {"l3": {"l4": "value"}}}}
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["meta"]["l1"]["l2"]["l3"]["l4"] == "value":
            result.record_pass("edge_deeply_nested_meta")
        else:
            result.record_fail("edge_deeply_nested_meta", "Nested value lost")
    except Exception as e:
        result.record_fail("edge_deeply_nested_meta", str(e))


def test_edge_content_newlines(result):
    data = make_valid_contract()
    data["content"] = "line1\nline2\nline3"
    try:
        cleaned = validate_contract(data, strict=True)
        if "\n" in cleaned["content"]:
            result.record_pass("edge_content_newlines")
        else:
            result.record_fail("edge_content_newlines", "Newlines lost")
    except Exception as e:
        result.record_fail("edge_content_newlines", str(e))


def test_edge_tokens_max_int(result):
    data = make_valid_contract()
    data["tokens_in"] = 2147483647
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["tokens_in"] == 2147483647:
            result.record_pass("edge_tokens_max_int")
        else:
            result.record_fail("edge_tokens_max_int", "Max int changed")
    except Exception as e:
        result.record_fail("edge_tokens_max_int", str(e))


def test_edge_model_special_chars(result):
    data = make_valid_contract()
    data["model"] = "gpt-4-turbo-2024-04-09"
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["model"] == "gpt-4-turbo-2024-04-09":
            result.record_pass("edge_model_special_chars")
        else:
            result.record_fail("edge_model_special_chars", "Model name changed")
    except Exception as e:
        result.record_fail("edge_model_special_chars", str(e))


def test_edge_content_only_whitespace(result):
    data = make_valid_contract()
    data["content"] = "     "
    try:
        cleaned = validate_contract(data, strict=True)
        if cleaned["content"].strip() == "":
            result.record_pass("edge_content_only_whitespace")
        else:
            result.record_fail("edge_content_only_whitespace", "Whitespace changed")
    except Exception as e:
        result.record_fail("edge_content_only_whitespace", str(e))


def test_edge_meta_with_special_keys(result):
    data = make_valid_contract()
    data["meta"] = {"__key__": "value", "123": "numeric"}
    try:
        cleaned = validate_contract(data, strict=True)
        if "__key__" in cleaned["meta"]:
            result.record_pass("edge_meta_with_special_keys")
        else:
            result.record_fail("edge_meta_with_special_keys", "Special keys lost")
    except Exception as e:
        result.record_fail("edge_meta_with_special_keys", str(e))


def test_edge_provider_all_variants(result):
    providers = ["openai", "anthropic", "mistral"]
    for provider in providers:
        data = corrupt_field(make_valid_contract(), "provider", provider)
        try:
            cleaned = validate_contract(data, strict=True)
            if cleaned["provider"] != provider:
                result.record_fail(f"edge_provider_{provider}", f"Provider changed")
                return
        except Exception as e:
            result.record_fail(f"edge_provider_{provider}", str(e))
            return
    result.record_pass("edge_provider_all_variants")


def test_edge_type_all_variants(result):
    types = ["completion", "chat", "tool"]
    for t in types:
        data = corrupt_field(make_valid_contract(), "type", t)
        try:
            cleaned = validate_contract(data, strict=True)
            if cleaned["type"] != t:
                result.record_fail(f"edge_type_{t}", f"Type changed")
                return
        except Exception as e:
            result.record_fail(f"edge_type_{t}", str(e))
            return
    result.record_pass("edge_type_all_variants")


############################################################
# SECTION 8 — TEST RUNNER
############################################################

def run_all_tests():
    result = TestResult()

    test_sanitize_basic_removes_none(result)
    test_sanitize_basic_strips_whitespace(result)
    test_sanitize_basic_preserves_numbers(result)
    test_sanitize_basic_no_mutation(result)
    test_sanitize_basic_empty_dict(result)
    test_sanitize_basic_all_none(result)
    test_sanitize_basic_mixed_types(result)
    test_sanitize_basic_converts_key_to_string(result)
    test_sanitize_content_length_basic(result)
    test_sanitize_content_length_no_content(result)
    test_sanitize_content_length_exact_limit(result)
    test_sanitize_content_length_under_limit(result)
    test_sanitize_content_length_custom_limit(result)
    test_sanitize_content_length_no_mutation(result)
    test_sanitize_types_float_to_int_tokens_in(result)
    test_sanitize_types_float_to_int_tokens_out(result)
    test_sanitize_types_meta_must_be_dict(result)
    test_sanitize_types_meta_valid_dict(result)
    test_sanitize_types_no_mutation(result)
    test_sanitize_types_both_tokens(result)
    test_sanitize_types_no_tokens(result)
    test_sanitize_basic_multiple_whitespace(result)
    test_sanitize_basic_newlines(result)
    test_sanitize_basic_tabs(result)
    test_sanitize_content_empty_string(result)
    test_sanitize_content_non_string(result)
    test_sanitize_types_tokens_already_int(result)
    test_sanitize_types_meta_empty_dict(result)
    test_sanitize_types_meta_nested(result)
    test_sanitize_basic_preserves_booleans(result)
    test_sanitize_basic_preserves_lists(result)
    test_sanitize_basic_zero_value(result)
    test_sanitize_basic_false_value(result)
    test_sanitize_basic_empty_string_preserved(result)
    test_sanitize_content_unicode(result)
    test_sanitize_types_tokens_negative_float(result)
    test_sanitize_types_tokens_zero(result)
    test_sanitize_types_meta_list_error(result)
    test_sanitize_types_meta_none_error(result)

    test_schema_valid_minimal(result)
    test_schema_missing_type(result)
    test_schema_missing_provider(result)
    test_schema_missing_model(result)
    test_schema_missing_content(result)
    test_schema_extra_field(result)
    test_schema_invalid_type_enum(result)
    test_schema_invalid_provider_enum(result)
    test_schema_type_completion(result)
    test_schema_type_chat(result)
    test_schema_type_tool(result)
    test_schema_provider_openai(result)
    test_schema_provider_anthropic(result)
    test_schema_provider_mistral(result)
    test_schema_content_not_string(result)
    test_schema_model_not_string(result)
    test_schema_tokens_in_valid(result)
    test_schema_tokens_out_valid(result)
    test_schema_tokens_in_negative(result)
    test_schema_tokens_out_negative(result)
    test_schema_tokens_in_zero(result)
    test_schema_tokens_in_not_int(result)
    test_schema_meta_valid(result)
    test_schema_meta_not_object(result)
    test_schema_meta_empty(result)
    test_schema_no_mutation(result)
    test_schema_content_empty(result)
    test_schema_content_very_long(result)
    test_schema_model_empty(result)
    test_schema_provider_empty(result)
    test_schema_type_empty(result)
    test_schema_tokens_boolean(result)
    test_schema_multiple_extra_fields(result)
    test_schema_all_fields_present(result)
    test_schema_provider_case_sensitive(result)
    test_schema_type_case_sensitive(result)

    test_strict_mode_valid(result)
    test_strict_mode_negative_tokens_in(result)
    test_strict_mode_negative_tokens_out(result)
    test_strict_mode_empty_provider(result)
    test_strict_mode_empty_model(result)
    test_strict_mode_empty_type(result)
    test_strict_mode_whitespace_provider(result)
    test_strict_mode_whitespace_model(result)
    test_strict_mode_meta_not_dict(result)
    test_strict_mode_tokens_in_zero(result)
    test_non_strict_mode_negative_tokens(result)
    test_strict_mode_missing_required(result)
    test_strict_mode_extra_field(result)
    test_strict_mode_valid_with_meta(result)
    test_strict_mode_valid_with_tokens(result)
    test_strict_mode_all_fields(result)
    test_strict_mode_provider_whitespace_trimmed(result)
    test_strict_mode_model_whitespace_trimmed(result)
    test_strict_mode_content_truncated(result)
    test_strict_mode_float_tokens_converted(result)

    test_no_mutation_sanitize_basic(result)
    test_no_mutation_sanitize_content(result)
    test_no_mutation_sanitize_types(result)
    test_no_mutation_validate_schema(result)
    test_no_mutation_validate_contract(result)
    test_no_new_fields_added(result)
    test_sanitize_preserves_nested_structures(result)
    test_no_side_effects_multiple_calls(result)
    test_independent_sanitization_steps(result)
    test_deep_copy_independence(result)
    test_sanitize_does_not_add_fields(result)
    test_sanitize_removes_only_none(result)
    test_validate_contract_returns_new_dict(result)
    test_sanitize_basic_returns_new_dict(result)
    test_sanitize_content_returns_new_dict(result)
    test_sanitize_types_returns_new_dict(result)

    test_pipeline_valid_minimal(result)
    test_pipeline_with_whitespace(result)
    test_pipeline_with_huge_content(result)
    test_pipeline_with_float_tokens(result)
    test_pipeline_strict_vs_non_strict(result)
    test_pipeline_all_sanitizations(result)
    test_pipeline_preserves_valid_data(result)
    test_pipeline_invalid_raises_error(result)

    test_error_contract_validation_error_exists(result)
    test_error_contract_schema_error_exists(result)
    test_error_contract_sanitization_error_exists(result)
    test_error_strict_mode_violation_exists(result)
    test_error_sanitize_types_meta_not_dict(result)
    test_error_validate_schema_missing_field(result)
    test_error_validate_schema_extra_field(result)
    test_error_validate_schema_invalid_type(result)
    test_error_validate_schema_invalid_enum(result)
    test_error_strict_mode_negative_tokens(result)
    test_error_strict_mode_empty_string(result)

    test_edge_null_byte_in_content(result)
    test_edge_unicode_in_content(result)
    test_edge_empty_dict(result)
    test_edge_deeply_nested_meta(result)
    test_edge_content_newlines(result)
    test_edge_tokens_max_int(result)
    test_edge_model_special_chars(result)
    test_edge_content_only_whitespace(result)
    test_edge_meta_with_special_keys(result)
    test_edge_provider_all_variants(result)
    test_edge_type_all_variants(result)

    return result


def main():
    result = run_all_tests()
    print(result.summary())
    if result.failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

from typing import Dict, Any

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
    ContractSchemaError,
    StrictModeViolation,
    ContractSanitizationError,
)


def validate_schema(data: dict) -> None:
    schema = LLM_RESPONSE_SCHEMA

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            raise ContractSchemaError(f"Missing required field: {field}")

    # Check additionalProperties=False
    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}).keys())
        for key in data.keys():
            if key not in allowed:
                raise ContractSchemaError(f"Additional property not allowed: {key}")

    # Check types and enums
    properties = schema.get("properties", {})
    for field, value in data.items():
        if field not in properties:
            continue

        prop_schema = properties[field]
        expected_type = prop_schema.get("type")

        # Type validation
        if expected_type == "string":
            if not isinstance(value, str):
                raise ContractSchemaError(f"Field '{field}' must be string, got {type(value).__name__}")
        elif expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                raise ContractSchemaError(f"Field '{field}' must be integer, got {type(value).__name__}")
        elif expected_type == "object":
            if not isinstance(value, dict):
                raise ContractSchemaError(f"Field '{field}' must be object, got {type(value).__name__}")

        # Enum validation
        if "enum" in prop_schema:
            if value not in prop_schema["enum"]:
                raise ContractSchemaError(f"Field '{field}' value '{value}' not in allowed enum: {prop_schema['enum']}")

        # Min validation for integers
        if expected_type == "integer" and "min" in prop_schema:
            if value < prop_schema["min"]:
                raise ContractSchemaError(f"Field '{field}' value {value} is below minimum {prop_schema['min']}")


def validate_contract(data: dict, strict: bool = True) -> Dict[str, Any]:
    # Sanitization sequence
    clean = sanitize_basic_fields(data)
    clean = sanitize_types(clean)
    clean = sanitize_content_length(clean)

    # Schema validation
    validate_schema(clean)

    # Strict mode additional checks
    if strict:
        # All integers must be >= 0
        if "tokens_in" in clean:
            if clean["tokens_in"] < 0:
                raise StrictModeViolation("tokens_in must be >= 0")

        if "tokens_out" in clean:
            if clean["tokens_out"] < 0:
                raise StrictModeViolation("tokens_out must be >= 0")

        # meta must be dict
        if "meta" in clean:
            if not isinstance(clean["meta"], dict):
                raise StrictModeViolation("meta must be dict")

        # provider, type, model must not be empty
        if "provider" in clean:
            if not clean["provider"] or clean["provider"].strip() == "":
                raise StrictModeViolation("provider must not be empty")

        if "type" in clean:
            if not clean["type"] or clean["type"].strip() == "":
                raise StrictModeViolation("type must not be empty")

        if "model" in clean:
            if not clean["model"] or clean["model"].strip() == "":
                raise StrictModeViolation("model must not be empty")

    return clean

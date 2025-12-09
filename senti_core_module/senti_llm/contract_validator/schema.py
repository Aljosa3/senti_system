LLM_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["type", "provider", "model", "content"],
    "properties": {
        "type": {"type": "string", "enum": ["completion", "chat", "tool"]},
        "provider": {"type": "string", "enum": ["openai", "anthropic", "mistral"]},
        "model": {"type": "string"},
        "content": {"type": "string"},
        "tokens_in": {"type": "integer", "min": 0},
        "tokens_out": {"type": "integer", "min": 0},
        "meta": {"type": "object"},
    },
    "additionalProperties": False
}

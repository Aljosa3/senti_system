"""
FAZA 31 Auto-Build System - SPEC Parser
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

import json
from typing import Dict, List, Any, Union


class SpecParseError(Exception):
    pass


def parse_spec(spec_input: Union[str, dict]) -> Dict[str, Any]:
    """
    Naloži in validira Auto-SPEC.

    Args:
        spec_input: JSON string ali že naložen dict

    Returns:
        Dict z validiranimi podatki:
        {
            "files": List[Dict],  # seznam datotek za generiranje
            "instructions": Dict,  # navodila za vsako datoteko
            "global_context": Dict  # globalni kontekst
        }
    """
    if isinstance(spec_input, str):
        try:
            spec_data = json.loads(spec_input)
        except json.JSONDecodeError as e:
            raise SpecParseError(f"Invalid JSON: {e}")
    elif isinstance(spec_input, dict):
        spec_data = spec_input
    else:
        raise SpecParseError("SPEC must be JSON string or dict")

    if not isinstance(spec_data, dict):
        raise SpecParseError("SPEC root must be object")

    if "files" not in spec_data:
        raise SpecParseError("SPEC missing required field: files")

    files = spec_data.get("files", [])
    if not isinstance(files, list):
        raise SpecParseError("SPEC field 'files' must be array")

    for idx, file_entry in enumerate(files):
        if not isinstance(file_entry, dict):
            raise SpecParseError(f"File entry {idx} must be object")
        if "path" not in file_entry:
            raise SpecParseError(f"File entry {idx} missing 'path'")
        if not isinstance(file_entry["path"], str):
            raise SpecParseError(f"File entry {idx} 'path' must be string")

    instructions = spec_data.get("instructions", {})
    if not isinstance(instructions, dict):
        raise SpecParseError("SPEC field 'instructions' must be object")

    global_context = spec_data.get("global_context", {})
    if not isinstance(global_context, dict):
        raise SpecParseError("SPEC field 'global_context' must be object")

    return {
        "files": files,
        "instructions": instructions,
        "global_context": global_context
    }


def validate_spec_structure(parsed_spec: Dict[str, Any]) -> None:
    """
    Dodatna validacija parsed SPEC strukture.
    """
    files = parsed_spec.get("files", [])

    for file_entry in files:
        path = file_entry.get("path", "")
        if not path.startswith("/"):
            raise SpecParseError(f"File path must be absolute: {path}")

        if ".." in path:
            raise SpecParseError(f"File path contains ..: {path}")

        if not path.startswith("/home/pisarna/senti_system/"):
            raise SpecParseError(f"File path outside senti_system: {path}")

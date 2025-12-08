"""
FAZA 31 Auto-Build System - LLM Prompt Builder
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

from typing import Dict, Any


FA31_CONTRACT_PLACEHOLDER = """
# FA31_LLM_CONTRACT.md
[TUKAJ VSTAVI CELOTEN KONTRAKT]
"""


def build_llm_prompt(parsed_spec: Dict[str, Any], contract_text: str = None) -> str:
    """
    Združi Auto-SPEC in FA31_LLM_CONTRACT v prompt za LLM sloj.

    Args:
        parsed_spec: Validiran SPEC iz spec_parser
        contract_text: Celoten tekst FA31_LLM_CONTRACT.md (opcijsko)

    Returns:
        Popoln prompt za LLM
    """
    if contract_text is None:
        contract_text = FA31_CONTRACT_PLACEHOLDER

    prompt_parts = []

    prompt_parts.append("=" * 60)
    prompt_parts.append("FAZA 31 AUTO-BUILD SYSTEM")
    prompt_parts.append("=" * 60)
    prompt_parts.append("")

    prompt_parts.append(contract_text)
    prompt_parts.append("")
    prompt_parts.append("=" * 60)
    prompt_parts.append("AUTO-SPEC")
    prompt_parts.append("=" * 60)
    prompt_parts.append("")

    files = parsed_spec.get("files", [])
    instructions = parsed_spec.get("instructions", {})
    global_context = parsed_spec.get("global_context", {})

    if global_context:
        prompt_parts.append("## Global Context:")
        for key, value in global_context.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.append("")

    prompt_parts.append("## Files to Generate:")
    for file_entry in files:
        path = file_entry.get("path", "")
        description = file_entry.get("description", "")
        prompt_parts.append(f"- {path}")
        if description:
            prompt_parts.append(f"  Description: {description}")

        file_instructions = instructions.get(path, "")
        if file_instructions:
            prompt_parts.append(f"  Instructions: {file_instructions}")
        prompt_parts.append("")

    prompt_parts.append("=" * 60)
    prompt_parts.append("OUTPUT FORMAT (MANDATORY)")
    prompt_parts.append("=" * 60)
    prompt_parts.append("")
    prompt_parts.append("Generate EXACTLY in this format:")
    prompt_parts.append("")
    prompt_parts.append("FILE: /absolute/path/to/file.py")
    prompt_parts.append("<complete file content>")
    prompt_parts.append("")
    prompt_parts.append("FILE: /absolute/path/to/next_file.py")
    prompt_parts.append("<complete file content>")
    prompt_parts.append("")
    prompt_parts.append("NO explanations, comments, or text outside FILE blocks.")
    prompt_parts.append("ALL files MUST be complete and deterministic.")
    prompt_parts.append("")

    return "\n".join(prompt_parts)

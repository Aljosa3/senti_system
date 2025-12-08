"""
FAZA 31 Auto-Build System - Output Parser
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

import re
from typing import Dict


class OutputParseError(Exception):
    pass


def parse_llm_output(llm_output: str) -> Dict[str, str]:
    """
    Razreže LLM output na FILE bloke.

    Args:
        llm_output: Celoten output LLM-ja

    Returns:
        Dict: {"/absolute/path/to/file.py": "<vsebina>"}

    Raises:
        OutputParseError: Če FILE bloki manjkajo ali so napačni
    """
    if not llm_output or not llm_output.strip():
        raise OutputParseError("LLM output is empty")

    file_pattern = re.compile(r'^FILE:\s*(.+?)$', re.MULTILINE)

    matches = list(file_pattern.finditer(llm_output))

    if not matches:
        raise OutputParseError("No FILE blocks found in LLM output")

    result = {}

    for i, match in enumerate(matches):
        file_path = match.group(1).strip()

        if not file_path:
            raise OutputParseError(f"Empty file path in FILE block {i+1}")

        content_start = match.end()

        if i + 1 < len(matches):
            content_end = matches[i + 1].start()
        else:
            content_end = len(llm_output)

        content = llm_output[content_start:content_end].strip()

        if not content:
            raise OutputParseError(f"Empty content for file: {file_path}")

        if file_path in result:
            raise OutputParseError(f"Duplicate FILE block: {file_path}")

        result[file_path] = content

    return result


def validate_file_blocks(parsed_files: Dict[str, str], expected_files: list) -> None:
    """
    Validira da so vsi pričakovani FILE bloki prisotni.

    Args:
        parsed_files: Rezultat parse_llm_output
        expected_files: Seznam pričakovanih poti iz SPEC-a
    """
    parsed_paths = set(parsed_files.keys())
    expected_paths = set(expected_files)

    missing = expected_paths - parsed_paths
    if missing:
        raise OutputParseError(f"Missing FILE blocks: {', '.join(sorted(missing))}")

    extra = parsed_paths - expected_paths
    if extra:
        raise OutputParseError(f"Unexpected FILE blocks: {', '.join(sorted(extra))}")

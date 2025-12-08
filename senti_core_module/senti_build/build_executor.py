"""
FAZA 31 Auto-Build System - Build Executor
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

from typing import Dict, Any
from . import spec_parser
from . import llm_prompt_builder
from . import output_parser
from . import static_validator
from . import semantic_validator
from . import sandbox_runner
from . import build_reporter


class BuildError(Exception):
    pass


def build(spec: dict, llm_callable=None, contract_text: str = None) -> Dict[str, Any]:
    """
    Glavni orchestrator FAZA 31 Auto-Build procesa.

    Args:
        spec: Auto-SPEC kot dict ali JSON string
        llm_callable: Funkcija ki sprejme prompt in vrne LLM output (opcijsko)
        contract_text: FA31_LLM_CONTRACT.md vsebina (opcijsko)

    Returns:
        Dict z rezultati builda:
        {
            "status": "OK" | "ERROR" | "PARTIAL",
            "files": {path: content},
            "report": {...}
        }
    """
    try:
        parsed_spec = spec_parser.parse_spec(spec)
        spec_parser.validate_spec_structure(parsed_spec)
    except spec_parser.SpecParseError as e:
        return {
            "status": "ERROR",
            "files": {},
            "report": build_reporter.create_error_report([str(e)], phase="spec_parsing")
        }

    try:
        prompt = llm_prompt_builder.build_llm_prompt(parsed_spec, contract_text)
    except Exception as e:
        return {
            "status": "ERROR",
            "files": {},
            "report": build_reporter.create_error_report([str(e)], phase="prompt_building")
        }

    if llm_callable is None:
        return {
            "status": "ERROR",
            "files": {},
            "report": build_reporter.create_error_report(
                ["No LLM callable provided - placeholder mode"],
                phase="llm_call"
            )
        }

    try:
        llm_output = llm_callable(prompt)
    except Exception as e:
        return {
            "status": "ERROR",
            "files": {},
            "report": build_reporter.create_error_report([str(e)], phase="llm_execution")
        }

    try:
        generated_files = output_parser.parse_llm_output(llm_output)

        expected_files = [f["path"] for f in parsed_spec["files"]]
        output_parser.validate_file_blocks(generated_files, expected_files)

    except output_parser.OutputParseError as e:
        return {
            "status": "ERROR",
            "files": {},
            "report": build_reporter.create_error_report([str(e)], phase="output_parsing")
        }

    static_errors = static_validator.validate_all_files(generated_files)

    semantic_errors = semantic_validator.validate_all_files(generated_files)

    sandbox_errors = sandbox_runner.run_sandbox_tests(generated_files)

    if static_errors or semantic_errors or sandbox_errors:
        report = build_reporter.create_error_report(
            static_errors + semantic_errors + sandbox_errors,
            phase="validation"
        )
        return {
            "status": "ERROR",
            "files": generated_files,
            "report": report
        }

    report = build_reporter.create_success_report(generated_files)

    return {
        "status": "OK",
        "files": generated_files,
        "report": report
    }


def build_from_spec_file(spec_path: str, llm_callable=None, contract_path: str = None) -> Dict[str, Any]:
    """
    Helper funkcija za build iz datoteke.

    Args:
        spec_path: Pot do SPEC datoteke (placeholder, ne uporablja open())
        llm_callable: LLM funkcija
        contract_path: Pot do kontrakta (placeholder)

    Returns:
        Dict z rezultati
    """
    raise BuildError("build_from_spec_file requires file reading - not implemented in sandbox mode")

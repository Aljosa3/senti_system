"""
FAZA 31 Auto-Build System - Build Reporter
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

from typing import Dict, List, Any
from datetime import datetime


def create_success_report(files: Dict[str, str]) -> Dict[str, Any]:
    """
    Ustvari report za uspešen build.

    Args:
        files: Dict {path: content}

    Returns:
        Dict s podatki o uspešnem buildu
    """
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "files_generated": len(files),
        "file_list": sorted(files.keys()),
        "errors": [],
        "warnings": []
    }


def create_error_report(errors: List[str], phase: str = "unknown") -> Dict[str, Any]:
    """
    Ustvari report za neuspešen build.

    Args:
        errors: Seznam napak
        phase: Faza v kateri je prišlo do napake

    Returns:
        Dict s podatki o napakah
    """
    return {
        "status": "ERROR",
        "timestamp": datetime.utcnow().isoformat(),
        "phase": phase,
        "files_generated": 0,
        "file_list": [],
        "errors": errors,
        "warnings": []
    }


def create_partial_report(
    files: Dict[str, str],
    errors: List[str],
    warnings: List[str] = None
) -> Dict[str, Any]:
    """
    Ustvari report za delno uspešen build.

    Args:
        files: Dict {path: content}
        errors: Seznam napak
        warnings: Seznam opozoril

    Returns:
        Dict s podatki o delnem buildu
    """
    return {
        "status": "PARTIAL",
        "timestamp": datetime.utcnow().isoformat(),
        "files_generated": len(files),
        "file_list": sorted(files.keys()),
        "errors": errors,
        "warnings": warnings or []
    }


def format_report(report: Dict[str, Any]) -> str:
    """
    Formatira report v human-readable string.

    Args:
        report: Report dict

    Returns:
        Formatirani string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("FAZA 31 AUTO-BUILD REPORT")
    lines.append("=" * 60)
    lines.append(f"Status: {report['status']}")
    lines.append(f"Timestamp: {report['timestamp']}")
    lines.append("")

    if report['status'] == "ERROR":
        lines.append(f"Failed in phase: {report.get('phase', 'unknown')}")
        lines.append("")

    lines.append(f"Files generated: {report['files_generated']}")
    if report['file_list']:
        lines.append("File list:")
        for file_path in report['file_list']:
            lines.append(f"  - {file_path}")
        lines.append("")

    if report['errors']:
        lines.append(f"Errors ({len(report['errors'])}):")
        for error in report['errors']:
            lines.append(f"  - {error}")
        lines.append("")

    if report.get('warnings'):
        lines.append(f"Warnings ({len(report['warnings'])}):")
        for warning in report['warnings']:
            lines.append(f"  - {warning}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def add_validation_results(
    report: Dict[str, Any],
    static_errors: List[str],
    semantic_errors: List[str],
    sandbox_errors: List[str]
) -> Dict[str, Any]:
    """
    Doda rezultate validacije v report.

    Args:
        report: Osnovni report
        static_errors: Napake statične validacije
        semantic_errors: Napake semantične validacije
        sandbox_errors: Napake sandbox testov

    Returns:
        Posodobljen report
    """
    all_errors = []

    if static_errors:
        all_errors.extend([f"[STATIC] {e}" for e in static_errors])

    if semantic_errors:
        all_errors.extend([f"[SEMANTIC] {e}" for e in semantic_errors])

    if sandbox_errors:
        all_errors.extend([f"[SANDBOX] {e}" for e in sandbox_errors])

    if all_errors:
        report["status"] = "ERROR"
        report["errors"].extend(all_errors)

    return report

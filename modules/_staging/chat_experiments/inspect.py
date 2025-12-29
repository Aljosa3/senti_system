"""
Read-only system introspection for Sapianta Chat.

This module provides pure, deterministic functions for inspecting the current
system state. All functions are READ-ONLY and NEVER execute or modify anything.

Authority: ADVISORY only.
Human remains the only actor that can change the system.
"""

import os
from pathlib import Path


def inspect_system() -> str:
    """
    Returns a high-level system overview.

    This function provides a read-only snapshot of the system's current state,
    including governance status, execution capabilities, and active modules.

    Returns:
        str: Plain text system overview
    """
    lines = []
    lines.append("SYSTEM INSPECT")
    lines.append("")
    lines.append("Core:")
    lines.append("  - Governance: LOCKED")
    lines.append("  - Execution: DISABLED")
    lines.append("  - Authority: HUMAN")
    lines.append("")
    lines.append("Chat:")
    lines.append("  - Chat Core: ACTIVE")
    lines.append("  - Drafts: ENABLED")
    lines.append("  - Proposals: ENABLED")
    lines.append("  - Approvals: HUMAN-ONLY")
    lines.append("")
    lines.append("Modules:")

    # Get modules directory
    modules_dir = Path(__file__).parent.parent

    # List all directories in modules (excluding special dirs)
    if modules_dir.exists():
        for item in sorted(modules_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                # Determine module type based on simple heuristics
                module_type = _infer_module_type(item)
                lines.append(f"  - {item.name} ({module_type}, read-only)")

    return "\n".join(lines)


def inspect_modules() -> str:
    """
    Returns a list of modules with metadata.

    This function scans the modules directory and provides a summary of each
    module's type, authority level, and execution capabilities (always NO).

    Returns:
        str: Plain text module listing
    """
    lines = []
    lines.append("MODULES INSPECT")
    lines.append("")

    # Get modules directory
    modules_dir = Path(__file__).parent.parent

    if not modules_dir.exists():
        lines.append("No modules directory found.")
        return "\n".join(lines)

    # List all directories in modules (excluding special dirs)
    module_count = 0
    for item in sorted(modules_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
            module_count += 1
            module_type = _infer_module_type(item)

            lines.append(f"- {item.name}")
            lines.append(f"  Type: {module_type}")
            lines.append(f"  Authority: ADVISORY")
            lines.append(f"  Execution: NO")
            lines.append("")

    if module_count == 0:
        lines.append("No modules found.")

    return "\n".join(lines)


def inspect_module(name: str) -> str:
    """
    Returns detailed information about a specific module.

    This function reads the module's directory structure and any README files
    to provide a comprehensive, read-only view of the module's purpose and
    capabilities.

    Args:
        name: Module name to inspect

    Returns:
        str: Plain text module details
    """
    lines = []
    lines.append(f"MODULE INSPECT: {name}")
    lines.append("")

    # Get module path
    modules_dir = Path(__file__).parent.parent
    module_path = modules_dir / name

    if not module_path.exists():
        lines.append(f"Error: Module '{name}' not found.")
        return "\n".join(lines)

    if not module_path.is_dir():
        lines.append(f"Error: '{name}' is not a directory.")
        return "\n".join(lines)

    # Read purpose from README if it exists
    readme_path = module_path / "README.md"
    if readme_path.exists() and readme_path.is_file():
        lines.append("Purpose:")
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                # Read first few lines or first paragraph
                content = f.read(500)  # Read first 500 chars
                first_line = content.split('\n')[0].strip('# \n')
                lines.append(f"  {first_line}")
        except Exception:
            lines.append("  (Unable to read README)")
    else:
        lines.append("Purpose:")
        lines.append(f"  {_infer_purpose_from_name(name)}")

    lines.append("")

    # List files and subdirectories
    lines.append("Files:")
    files_found = False
    try:
        for item in sorted(module_path.iterdir()):
            if item.is_file() and not item.name.startswith('.'):
                files_found = True
                lines.append(f"  - {item.name}")
            elif item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                # List subdirectory
                subdir_files = list(item.glob('*.md'))
                if subdir_files:
                    files_found = True
                    for subfile in sorted(subdir_files):
                        lines.append(f"  - {item.name}/{subfile.name}")
    except Exception:
        lines.append("  (Unable to read directory)")

    if not files_found:
        lines.append("  (No readable files found)")

    lines.append("")

    # Capabilities (read-only only)
    lines.append("Capabilities:")
    lines.append("  - Read")
    lines.append("  - Describe")
    lines.append("")

    # Explicit non-capabilities
    lines.append("Explicit Non-Capabilities:")
    lines.append("  - Execution")
    lines.append("  - Signals")
    lines.append("  - Automation")
    lines.append("  - File Writing")
    lines.append("  - Process Spawning")

    return "\n".join(lines)


def _infer_module_type(module_path: Path) -> str:
    """
    Infers module type from name and structure (deterministic rules only).

    Args:
        module_path: Path to module directory

    Returns:
        str: Module type descriptor
    """
    name = module_path.name.lower()

    # Check for README to get more context
    readme_path = module_path / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read(200).lower()
                if 'intel' in content or 'trading' in content:
                    return "Intelligence"
                elif 'knowledge' in content or 'notes' in content:
                    return "Knowledge"
                elif 'chat' in content or 'cli' in content:
                    return "Interface"
        except Exception:
            pass

    # Fallback to name-based inference
    if 'intel' in name or 'trading' in name:
        return "Intelligence"
    elif 'notes' in name or 'knowledge' in name:
        return "Knowledge"
    elif 'chat' in name or 'cli' in name:
        return "Interface"
    elif 'sensor' in name:
        return "Sensor"
    elif 'actuator' in name:
        return "Actuator"
    elif 'processing' in name or 'reasoning' in name or 'memory' in name:
        return "Processing"
    elif 'communication' in name:
        return "Communication"
    elif 'validator' in name or 'security' in name:
        return "Validation"
    else:
        return "Module"


def _infer_purpose_from_name(name: str) -> str:
    """
    Infers basic purpose from module name (deterministic rules only).

    Args:
        name: Module name

    Returns:
        str: Purpose description
    """
    name_lower = name.lower()

    if 'intel' in name_lower:
        return "Intelligence gathering and documentation."
    elif 'notes' in name_lower:
        return "Knowledge storage and reference."
    elif 'chat' in name_lower:
        return "Chat interface and interaction."
    elif 'cli' in name_lower:
        return "Command-line interface."
    elif 'sensor' in name_lower:
        return "Data collection and input."
    elif 'actuator' in name_lower:
        return "Output and action execution."
    elif 'processing' in name_lower:
        return "Data processing and transformation."
    elif 'communication' in name_lower:
        return "Inter-module and external communication."
    elif 'validator' in name_lower:
        return "Validation and verification."
    else:
        return "Module functionality."

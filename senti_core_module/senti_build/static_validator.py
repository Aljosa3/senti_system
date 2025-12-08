"""
FAZA 31 Auto-Build System - Static Validator
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

import ast
import re
from typing import Dict, List


class StaticValidationError(Exception):
    pass


FORBIDDEN_PATTERNS = [
    r'\bos\.system\b',
    r'\bsubprocess\.',
    r'\beval\s*\(',
    r'\bexec\s*\(',
    r'\bopen\s*\(',
    r'\bunlink\s*\(',
    r'\bchmod\s*\(',
    r'\burllib\.',
    r'\brequests\.',
    r'\bsocket\.',
    r'\b__import__\s*\(',
]


def validate_syntax(file_path: str, content: str) -> None:
    """
    Preveri Python syntax z ast.parse() in compile().

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        StaticValidationError: Če syntax ni veljaven
    """
    try:
        ast.parse(content, filename=file_path)
    except SyntaxError as e:
        raise StaticValidationError(f"Syntax error in {file_path}: {e}")

    try:
        compile(content, file_path, 'exec')
    except SyntaxError as e:
        raise StaticValidationError(f"Compile error in {file_path}: {e}")


def check_forbidden_patterns(file_path: str, content: str) -> None:
    """
    Preveri prepovedane pattern-e v kodi.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        StaticValidationError: Če najde prepovedan pattern
    """
    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            raise StaticValidationError(
                f"Forbidden pattern in {file_path}: {pattern} (found: {matches[0]})"
            )


def validate_ast_nodes(file_path: str, content: str) -> None:
    """
    Preveri AST drevo za nevarne konstrukcije.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        StaticValidationError: Če najde nevarno konstrukcijo
    """
    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in ['eval', 'exec', '__import__', 'open', 'compile']:
                    raise StaticValidationError(
                        f"Forbidden function call in {file_path}: {func_name}()"
                    )

            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in ['system', 'popen', 'spawn']:
                    raise StaticValidationError(
                        f"Forbidden method call in {file_path}: .{node.func.attr}()"
                    )


def validate_file(file_path: str, content: str) -> None:
    """
    Celotna statična validacija za eno datoteko.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        StaticValidationError: Če validacija ne uspe
    """
    validate_syntax(file_path, content)
    check_forbidden_patterns(file_path, content)
    validate_ast_nodes(file_path, content)


def validate_all_files(files: Dict[str, str]) -> List[str]:
    """
    Validira vse datoteke, zbere vse napake.

    Args:
        files: Dict {path: content}

    Returns:
        Seznam napak (prazen če vse OK)
    """
    errors = []

    for file_path, content in files.items():
        try:
            validate_file(file_path, content)
        except StaticValidationError as e:
            errors.append(str(e))

    return errors

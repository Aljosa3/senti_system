"""
FAZA 31 Auto-Build System - Sandbox Runner
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

import sys
from typing import Dict, List


class SandboxError(Exception):
    pass


def create_sandbox_globals() -> dict:
    """
    Ustvari izoliran globals kontekst za sandbox.

    Returns:
        Dict z varnimi builtin funkcijami
    """
    import builtins

    safe_builtins = {
        '__builtins__': {
            'None': None,
            'False': False,
            'True': True,
            'bool': bool,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'frozenset': frozenset,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'any': any,
            'all': all,
            'sum': sum,
            'min': min,
            'max': max,
            'sorted': sorted,
            'reversed': reversed,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'type': type,
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
            '__build_class__': builtins.__build_class__,
            '__import__': builtins.__import__,
            '__name__': '__sandbox__',
            'abs': abs,
            'round': round,
            'pow': pow,
            'divmod': divmod,
        }
    }

    return safe_builtins


def compile_module(file_path: str, content: str) -> object:
    """
    Kompilira modul v izoliranem kontekstu.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Returns:
        Compiled code object

    Raises:
        SandboxError: Če kompilacija ne uspe
    """
    try:
        code_obj = compile(content, file_path, 'exec')
        return code_obj
    except Exception as e:
        raise SandboxError(f"Compilation failed for {file_path}: {e}")


def test_module_import(file_path: str, code_obj: object) -> None:
    """
    Testira osnovni import modula v sandboxu.

    Args:
        file_path: Pot do datoteke
        code_obj: Compiled code object

    Raises:
        SandboxError: Če import ne uspe
    """
    sandbox_globals = create_sandbox_globals()
    sandbox_locals = {}

    try:
        exec(code_obj, sandbox_globals, sandbox_locals)
    except ImportError as e:
        pass
    except ModuleNotFoundError as e:
        pass
    except Exception as e:
        raise SandboxError(f"Execution failed for {file_path}: {e}")


def run_sandbox_tests(files: Dict[str, str]) -> List[str]:
    """
    Izvede sandbox teste za vse datoteke.

    Args:
        files: Dict {path: content}

    Returns:
        Seznam napak (prazen če vse OK)
    """
    errors = []

    for file_path, content in files.items():
        try:
            code_obj = compile_module(file_path, content)
            test_module_import(file_path, code_obj)
        except SandboxError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Unexpected error in {file_path}: {e}")

    return errors


def validate_no_side_effects(files: Dict[str, str]) -> List[str]:
    """
    Preveri da moduli nimajo stranskih učinkov.

    Args:
        files: Dict {path: content}

    Returns:
        Seznam napak (prazen če vse OK)
    """
    errors = []

    for file_path, content in files.items():
        if 'if __name__' in content and '__main__' in content:
            continue

        dangerous_top_level = [
            'print(', 'input(', 'exit(', 'quit(',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith('#'):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith('def ') or stripped.startswith('class '):
                break

            for dangerous in dangerous_top_level:
                if dangerous in stripped:
                    errors.append(
                        f"Possible side effect in {file_path}:{line_num}: {dangerous}"
                    )

    return errors

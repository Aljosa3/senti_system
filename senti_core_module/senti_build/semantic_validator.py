"""
FAZA 31 Auto-Build System - Semantic Validator
Strogo v skladu s FA31_LLM_CONTRACT.md
"""

import re
from typing import Dict, List


class SemanticValidationError(Exception):
    pass


PROTECTED_FAZA_MODULES = [
    'FAZA_16', 'FAZA_29', 'FAZA_30', 'FAZA_30_95', 'FAZA_31',
    'FAZA_101', 'FAZA_102', 'FAZA_103', 'FAZA_104', 'FAZA_105',
    'FAZA_106', 'FAZA_107', 'FAZA_108', 'FAZA_109', 'FAZA_110',
    'FAZA_111', 'FAZA_112', 'FAZA_113', 'FAZA_114', 'FAZA_115',
    'FAZA_116', 'FAZA_117', 'FAZA_118', 'FAZA_119', 'FAZA_120',
    'FAZA_121', 'FAZA_122', 'FAZA_123'
]


PROTECTED_PATHS = [
    '/home/pisarna/senti_system/senti_os/',
    '/home/pisarna/senti_system/senti_core_module/senti_core/',
    '/home/pisarna/senti_system/senti_core_module/senti_security_core/',
]


CRITICAL_IMPORTS = [
    'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
    'shutil', '__builtin__', 'builtins'
]


def check_protected_faza(file_path: str, content: str) -> None:
    """
    Preveri da datoteka ne spreminja zaščitenih FAZA modulov.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        SemanticValidationError: Če najde kršitev
    """
    for faza in PROTECTED_FAZA_MODULES:
        pattern = re.compile(rf'\b{faza}\b', re.IGNORECASE)
        if pattern.search(content):
            raise SemanticValidationError(
                f"File {file_path} references protected module: {faza}"
            )


def check_protected_paths(file_path: str) -> None:
    """
    Preveri da datoteka ni v zaščitenem direktoriju.

    Args:
        file_path: Pot do datoteke

    Raises:
        SemanticValidationError: Če je v zaščitenem direktoriju
    """
    for protected in PROTECTED_PATHS:
        if file_path.startswith(protected):
            raise SemanticValidationError(
                f"File {file_path} is in protected directory: {protected}"
            )


def check_critical_imports(file_path: str, content: str) -> None:
    """
    Preveri kritične uvoz module.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        SemanticValidationError: Če najde kritičen uvoz
    """
    for module in CRITICAL_IMPORTS:
        patterns = [
            rf'^import\s+{module}\b',
            rf'^from\s+{module}\b',
            rf'\nimport\s+{module}\b',
            rf'\nfrom\s+{module}\b',
        ]

        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE):
                raise SemanticValidationError(
                    f"File {file_path} imports critical module: {module}"
                )


def check_architecture_changes(file_path: str, content: str) -> None:
    """
    Preveri da datoteka ne spreminja arhitekture.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        SemanticValidationError: Če najde spremembe arhitekture
    """
    forbidden_keywords = [
        'EventBus', 'KernelProcess', 'SystemBoot', 'SecurityManager',
        'DataIntegrity', 'ExpansionManager'
    ]

    for keyword in forbidden_keywords:
        pattern = rf'\bclass\s+{keyword}\b'
        if re.search(pattern, content):
            raise SemanticValidationError(
                f"File {file_path} redefines architecture class: {keyword}"
            )


def validate_file(file_path: str, content: str) -> None:
    """
    Celotna semantična validacija za eno datoteko.

    Args:
        file_path: Pot do datoteke
        content: Vsebina datoteke

    Raises:
        SemanticValidationError: Če validacija ne uspe
    """
    check_protected_paths(file_path)
    check_protected_faza(file_path, content)
    check_critical_imports(file_path, content)
    check_architecture_changes(file_path, content)


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
        except SemanticValidationError as e:
            errors.append(str(e))

    return errors

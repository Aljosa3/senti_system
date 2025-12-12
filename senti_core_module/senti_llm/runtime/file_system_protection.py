"""
FAZA 46 — File System Protection Rules
FILE 3/8: file_system_protection.py

Deterministic, passive security layer for path validation.
Validates paths before system even considers them.

Prevents:
- Path traversal
- Absolute system paths
- Access outside allowed roots

Purpose:
- Validation + exceptions only
- No disk reads
- No modifications
- Used by: command normalizer, AHP, module loader, execution layer

Rules:
- No I/O
- No os.path.exists
- No pathlib
- No print/log
- No path fixing
- No normalization
- String logic + exceptions only
- Deterministic execution
"""


# =====================================================================
# Exceptions
# =====================================================================

class FileSystemProtectionError(Exception):
    """Base exception for file system protection errors."""


class ForbiddenPathError(FileSystemProtectionError):
    """Raised when path accesses forbidden locations."""


class InvalidPathError(FileSystemProtectionError):
    """Raised when path format is invalid."""


# =====================================================================
# Constants
# =====================================================================

ALLOWED_DIRECTORIES = (
    "senti_core_module/",
)

FORBIDDEN_DIRECTORIES = (
    "/",
    "/etc",
    "/bin",
    "/usr",
    "/var",
    "/home",
)

FORBIDDEN_PATTERNS = (
    "../",
    "/..",
    "~",
)


# =====================================================================
# Validation Functions
# =====================================================================

def is_relative_path(path: str) -> bool:
    """
    Check if path is relative (does not start with /).

    Args:
        path (str): Path to check.

    Returns:
        bool: True if path does not start with /.
    """
    return not path.startswith("/")


def contains_forbidden_pattern(path: str) -> bool:
    """
    Check if path contains forbidden patterns.

    Args:
        path (str): Path to check.

    Returns:
        bool: True if path contains any forbidden pattern.
    """
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in path:
            return True
    return False


def starts_with_allowed_directory(path: str) -> bool:
    """
    Check if path starts with an allowed directory.

    Args:
        path (str): Path to check.

    Returns:
        bool: True if path starts with any allowed directory.
    """
    for allowed_dir in ALLOWED_DIRECTORIES:
        if path.startswith(allowed_dir):
            return True
    return False


def starts_with_forbidden_directory(path: str) -> bool:
    """
    Check if path starts with a forbidden directory.

    Args:
        path (str): Path to check.

    Returns:
        bool: True if path starts with any forbidden directory.
    """
    for forbidden_dir in FORBIDDEN_DIRECTORIES:
        if path.startswith(forbidden_dir):
            return True
    return False


def validate_path(path: str) -> None:
    """
    Validate path against security rules.

    Args:
        path (str): Path to validate.

    Raises:
        InvalidPathError: If path is not a string or is empty.
        ForbiddenPathError: If path violates security rules.
    """
    if not isinstance(path, str):
        raise InvalidPathError(f"Path must be string, got: {type(path)}")

    if not path:
        raise InvalidPathError("Path cannot be empty")

    if not is_relative_path(path):
        raise ForbiddenPathError(f"Absolute paths not allowed: {path}")

    if contains_forbidden_pattern(path):
        raise ForbiddenPathError(f"Path contains forbidden pattern: {path}")

    if starts_with_forbidden_directory(path):
        raise ForbiddenPathError(f"Path starts with forbidden directory: {path}")

    if not starts_with_allowed_directory(path):
        raise ForbiddenPathError(f"Path does not start with allowed directory: {path}")


def is_path_allowed(path: str) -> bool:
    """
    Check if path is allowed (non-throwing).

    Args:
        path (str): Path to check.

    Returns:
        bool: True if path passes validation, False otherwise.
    """
    try:
        validate_path(path)
        return True
    except Exception:
        return False

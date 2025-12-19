"""
Registry Reader
---------------
Read-only interface to the Module Registry.

This module provides simple read access to registry/modules/modules.yaml.
It does not validate, transform, or interpret registry content.
"""

import yaml
from pathlib import Path


def _load_registry():
    """Load registry YAML file."""
    registry_path = Path(__file__).parent / "modules" / "modules.yaml"
    with open(registry_path, 'r') as f:
        data = yaml.safe_load(f)
    return data


def get_all_modules():
    """
    Returns the raw parsed YAML structure as dict.

    Returns:
        dict: Complete registry data structure
    """
    return _load_registry()


def module_exists(module_id):
    """
    Check if a module_id exists in the registry.

    Args:
        module_id: Module identifier to check

    Returns:
        bool: True if module exists, False otherwise
    """
    data = _load_registry()
    modules = data.get('modules', [])
    for module in modules:
        if module.get('module_id') == module_id:
            return True
    return False


def get_module(module_id):
    """
    Get module data by module_id.

    Args:
        module_id: Module identifier

    Returns:
        dict: Module data if found, None otherwise
    """
    data = _load_registry()
    modules = data.get('modules', [])
    for module in modules:
        if module.get('module_id') == module_id:
            return module
    return None


def get_lifecycle_status(module_id):
    """
    Get lifecycle status of a module.

    Args:
        module_id: Module identifier

    Returns:
        str: Lifecycle status if present, None otherwise
    """
    module = get_module(module_id)
    if module is None:
        return None
    lifecycle = module.get('lifecycle')
    if lifecycle is None:
        return None
    return lifecycle.get('status')


def get_capabilities(module_id):
    """
    Get capabilities list of a module.

    Args:
        module_id: Module identifier

    Returns:
        list: Capabilities list if present, None otherwise
    """
    module = get_module(module_id)
    if module is None:
        return None
    return module.get('capabilities')

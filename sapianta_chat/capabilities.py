"""
Sapianta Chat Capabilities Registry

All capabilities are explicitly defined and disabled by default.
"""

CAPABILITIES = {
    "execute_actions": False,
    "call_external_apis": False,
    "modify_system_state": False,
    "generate_data": False,
    "run_commands": False,
    "access_filesystem": False,
    "interpret_governance": False,
    "activate_modules": False,
    "make_decisions": False,
    "autonomous_behavior": False,
}


def is_capable(capability_name):
    """
    Check if a capability is enabled.

    Args:
        capability_name: Name of the capability to check

    Returns:
        Boolean indicating if capability is enabled
    """
    return CAPABILITIES.get(capability_name, False)


def get_all_capabilities():
    """
    Return all capabilities and their current status.

    Returns:
        Dictionary of capability names and their boolean status
    """
    return CAPABILITIES.copy()

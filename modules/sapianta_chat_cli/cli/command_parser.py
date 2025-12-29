from modules.sapianta_chat.core import generate_draft, generate_proposal
from modules.sapianta_chat.inspect import inspect_system, inspect_modules, inspect_module
from modules.sapianta_chat_cli.readers.registry_reader import read_registry
from modules.sapianta_chat_cli.utils.text_helpers import first_paragraph
from modules.sapianta_chat_cli.cli.approvals import approve_module


# ============================================================
# GOVERNANCE STATE (MVP — HARDCODED)
# ============================================================

STATE_NORMAL = "NORMAL"
STATE_OVERLOADED = "OVERLOADED"
STATE_SAFE_MODE = "SAFE_MODE"

# MVP: state je namenoma hardcoded
CURRENT_STATE = STATE_NORMAL


# ============================================================
# ALLOWED COMMANDS BY STATE (PARSER-LEVEL)
# ============================================================

# Ključ: prvi token ukaza (parts[0])
ALLOWED_COMMANDS_BY_STATE = {
    STATE_NORMAL: {
        "chat",
        "status",
        "help",
    },
    STATE_OVERLOADED: {
        "chat",     # dovoljen samo omejen inspect (enforced spodaj)
        "status",
        "help",
    },
    STATE_SAFE_MODE: {
        "help",
    },
}


def parse_command(input_line: str) -> dict:
    parts = input_line.strip().split()

    if not parts:
        return {"error": "Empty command. Type 'help' for available commands."}

    # ============================================================
    # GOVERNANCE ENFORCEMENT (MVP)
    # ============================================================

    if parts[0] not in ALLOWED_COMMANDS_BY_STATE.get(CURRENT_STATE, set()):
        if CURRENT_STATE == STATE_SAFE_MODE:
            return {"error": "SAFE_MODE active."}
        return {"error": "Command not allowed in current state."}

    # ============================================================
    # CHAT: DRAFT (NORMAL only)
    # ============================================================

    if parts[0] == "chat" and len(parts) >= 3 and parts[1] == "draft":
        if CURRENT_STATE != STATE_NORMAL:
            return {"error": "Command not allowed in current state."}

        prompt = " ".join(parts[2:])
        return {
            "content": generate_draft(prompt)
        }

    # ============================================================
    # CHAT: PROPOSE (NORMAL only)
    # ============================================================

    if parts[0] == "chat" and len(parts) >= 3 and parts[1] == "propose":
        if CURRENT_STATE != STATE_NORMAL:
            return {"error": "Command not allowed in current state."}

        prompt = " ".join(parts[2:])
        return {
            "content": generate_proposal(prompt)
        }

    if parts[0] == "chat" and len(parts) == 2 and parts[1] == "propose":
        return {"error": "Usage: chat propose <description>"}

    # ============================================================
    # CHAT: APPROVE (NORMAL only)
    # ============================================================

    if parts[0] == "chat" and len(parts) == 3 and parts[1] == "approve":
        if CURRENT_STATE != STATE_NORMAL:
            return {"error": "Command not allowed in current state."}

        module_name = parts[2]
        return approve_module(module_name)

    if parts[0] == "chat" and len(parts) == 2 and parts[1] == "approve":
        return {"error": "Usage: chat approve <module_name>"}

    # ============================================================
    # CHAT: INSPECT
    # ============================================================

    if parts[0] == "chat" and len(parts) >= 2 and parts[1] == "inspect":

        # OVERLOADED: dovoljen samo osnovni inspect
        if CURRENT_STATE == STATE_OVERLOADED and len(parts) > 2:
            return {"error": "Command not allowed in current state."}

        # chat inspect module <name>
        if len(parts) >= 4 and parts[2] == "module":
            return {
                "content": inspect_module(parts[3])
            }

        # chat inspect modules
        if len(parts) == 3 and parts[2] == "modules":
            return {
                "content": inspect_modules()
            }

        # chat inspect
        if len(parts) == 2:
            return {
                "content": inspect_system()
            }

        return {"error": "Usage: chat inspect [modules | module <name>]"}

    # ============================================================
    # STATUS
    # ============================================================

    if parts[0] == "status":
        registry = read_registry()
        return {
            "content": {
                "system": "Senti / Sapianta",
                "overview": registry
            }
        }

    # ============================================================
    # HELP
    # ============================================================

    if parts[0] == "help":
        return {
            "content": [
                "Available commands:",
                "- help",
                "- status",
                "- chat inspect",
                "- chat inspect modules",
                "- chat inspect module <name>",
                "- chat draft <description>",
                "- chat propose <description>",
                "- chat approve <module_name>",
            ]
        }

    # ============================================================
    # UNKNOWN
    # ============================================================

    return {"error": f"Unknown command '{input_line}'."}

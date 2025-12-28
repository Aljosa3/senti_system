from modules.sapianta_chat.core import generate_draft
from modules.sapianta_chat_cli.readers.registry_reader import read_registry
from modules.sapianta_chat_cli.utils.text_helpers import first_paragraph


def parse_command(input_line: str) -> dict:
    parts = input_line.strip().split()

    if not parts:
        return {"error": "Empty command. Type 'help' for available commands."}

    # --- CHAT DRAFT ---
    if parts[0] == "chat" and len(parts) >= 3 and parts[1] == "draft":
        prompt = " ".join(parts[2:])
        draft = generate_draft(prompt)
        return {"content": draft}

    command = parts[0]

    if command == "status":
        registry = read_registry()
        return {
            "content": {
                "system": "Senti / Sapianta",
                "overview": first_paragraph(registry)
            }
        }

    if command == "help":
        return {
            "content": [
                "Available commands:",
                "- help",
                "- status",
                "- chat draft <description>",
            ]
        }

    return {"error": f"Unknown command '{command}'."}

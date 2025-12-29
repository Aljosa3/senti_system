"""
chat CLI entrypoint (non-interactive).

Purpose:
- Thin wrapper around command_parser.parse_command
- No state
- No REPL
- One command = one execution
"""

import sys
from modules.sapianta_chat_cli.cli.command_parser import parse_command


def main():
    if len(sys.argv) < 2:
        print("Usage: chat <command>")
        sys.exit(1)

    input_line = " ".join(sys.argv[1:])
    result = parse_command(input_line)

    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    content = result.get("content")

    if isinstance(content, (list, dict)):
        print(content)
    else:
        print(content)

"""
Sapianta Chat CLI

Minimal command-line interface for controlled conversational input/output.
No execution capabilities. No agent behavior.
"""

import sys
from sapianta_chat.engine import generate_response, get_status_message


WELCOME_MESSAGE = """Sapianta Chat is running in limited mode.
No actions or executions are enabled."""


EXIT_COMMANDS = ["exit", "quit", "q"]


def print_welcome():
    """Print the controlled welcome message."""
    print(WELCOME_MESSAGE)
    print()


def print_prompt():
    """Print the input prompt."""
    print("> ", end="", flush=True)


def handle_special_command(user_input):
    """
    Handle special commands that don't require processing.

    Args:
        user_input: Raw user input string

    Returns:
        Boolean indicating if command was handled
    """
    stripped = user_input.strip().lower()

    if stripped in EXIT_COMMANDS:
        print("Exiting.")
        return True

    if stripped == "status":
        print(get_status_message())
        return True

    if stripped == "help":
        print("Available commands:")
        print("  status - Show capability status")
        print("  exit, quit, q - Exit the application")
        return True

    return False


def run():
    """Main CLI loop."""
    print_welcome()

    try:
        while True:
            print_prompt()

            try:
                user_input = input()
            except EOFError:
                print()
                print("EOF detected. Exiting.")
                break

            if handle_special_command(user_input):
                if user_input.strip().lower() in EXIT_COMMANDS:
                    break
                continue

            response = generate_response(user_input)
            print(response)
            print()

    except KeyboardInterrupt:
        print()
        print("Interrupted. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    run()

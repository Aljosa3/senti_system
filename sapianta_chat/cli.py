"""
Sapianta Chat CLI

Minimal command-line interface for controlled conversational input/output.
No execution capabilities. No agent behavior.
"""

import sys
from sapianta_chat.engine import generate_response_id, get_status_response_id
from sapianta_chat.response_registry import get_response_text


WELCOME_MESSAGE = """Sapianta Chat is running in limited mode.
No actions or executions are enabled."""


EXIT_COMMANDS = ["exit", "quit", "q"]


def print_welcome():
    print(WELCOME_MESSAGE)
    print()


def print_prompt():
    print("> ", end="", flush=True)


def handle_special_command(user_input):
    stripped = user_input.strip().lower()

    if stripped in EXIT_COMMANDS:
        print("Exiting.")
        return True

    if stripped == "status":
        response_id = get_status_response_id()
        print(get_response_text(response_id))
        return True

    if stripped == "help":
        print("Available commands:")
        print("  status - Show capability status")
        print("  exit, quit, q - Exit the application")
        return True

    return False


def run():
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

            response_id = generate_response_id(user_input)
            print(get_response_text(response_id))
            print()

    except KeyboardInterrupt:
        print()
        print("Interrupted. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    run()

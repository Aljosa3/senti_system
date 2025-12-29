import os
from .state import SessionState

BANNER = """
────────────────────────────
 SAPIANTA CHAT (schat)
────────────────────────────
commands: draft | propose | clear | summary | exit
────────────────────────────
"""

MODE_SEPARATOR = "────────────────────────────"


def run_chat_repl():
    state = SessionState()
    print(BANNER)
    print(f"mode: {state.mode}")

    while True:
        try:
            prompt = f"{state.mode} > "
            user_input = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nexit")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("exit", "quit"):
            print("Session ended.")
            break

        if cmd == "clear":
            os.system('clear' if os.name != 'nt' else 'cls')
            continue

        if cmd == "summary":
            print(state.summary())
            continue

        if cmd in ("draft", "propose"):
            print(MODE_SEPARATOR)
            state.set_mode(cmd.upper())
            print(f"mode: {state.mode}")
            continue

        # vse ostalo se šteje kot vsebina trenutnega konteksta
        state.add_line(user_input)

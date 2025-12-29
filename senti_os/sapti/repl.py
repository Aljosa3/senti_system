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

        # ── EXIT ─────────────────────────
        if cmd in ("exit", "quit"):
            print("Session ended.")
            break

        # ── CLEAR ────────────────────────
        if cmd == "clear":
            os.system('clear' if os.name != 'nt' else 'cls')
            continue

        # ── SUMMARY ──────────────────────
        if cmd == "summary":
            print(state.summary())
            continue

        # ── EXPLICIT MODE SWITCH ─────────
        if cmd in ("draft", "propose"):
            print(MODE_SEPARATOR)
            state.set_mode(cmd.upper())
            print(f"mode: {state.mode}")
            continue

        # ── IMPLICIT DRAFT (B10.1) ───────
        if state.mode == "INSPECT":
            print(MODE_SEPARATOR)
            state.set_mode("DRAFT")
            print(f"mode: {state.mode}")

        # ── CONTENT LINE ─────────────────
        state.add_line(user_input)

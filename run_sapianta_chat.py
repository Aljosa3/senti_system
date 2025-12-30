#!/usr/bin/env python3
"""
Sapianta Chat Launcher

Canonical entrypoint for Sapianta CLI Chat (read-only advisory mode).

This launcher explicitly starts the Phase V advisory CLI:
modules.sapianta_cli_chat.cli.run_cli_chat

Authority: NONE
Execution: FORBIDDEN
"""

from modules.sapianta_cli_chat.cli import run_cli_chat


def main():
    run_cli_chat()


if __name__ == "__main__":
    main()

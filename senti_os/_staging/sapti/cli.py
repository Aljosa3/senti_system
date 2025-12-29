import argparse
from .repl import run_chat_repl

PROGRAM_NAME = "sapti"
VERSION = "0.1.0"

def main():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="Sapianta Tools CLI"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    subparsers = parser.add_subparsers(dest="command")

    chat_parser = subparsers.add_parser(
        "chat",
        help="Start Sapianta Chat (schat)"
    )

    args = parser.parse_args()

    if args.command == "chat":
        run_chat_repl()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

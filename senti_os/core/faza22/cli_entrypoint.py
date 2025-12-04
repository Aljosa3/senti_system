#!/usr/bin/env python3
"""
FAZA 22 - CLI Entrypoint

Main entrypoint for the `senti` command-line interface.

Usage:
    senti start              - Start SENTI OS
    senti stop               - Stop SENTI OS
    senti restart            - Restart SENTI OS
    senti status             - Show system status
    senti status --detailed  - Show detailed status
    senti logs               - Show recent logs
    senti logs --level=error - Show error logs
    senti doctor             - Run diagnostics
    senti doctor --quick     - Run quick diagnostics
    senti help               - Show help

Author: SENTI OS Core Team
License: Proprietary
Version: 1.0.0
"""

import sys
import argparse
from typing import Optional, List

from senti_os.core.faza22.cli_commands import get_cli_commands
from senti_os.core.faza22.cli_renderer import get_cli_renderer


VERSION = "1.0.0"
PROGRAM_NAME = "senti"


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="SENTI OS - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  senti start                  Start SENTI OS
  senti status --detailed      Show detailed status
  senti logs --level=error     Show error logs only
  senti doctor --quick         Run quick diagnostics

For more information, visit: https://github.com/senti-os
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start SENTI OS"
    )

    # Stop command
    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop SENTI OS"
    )

    # Restart command
    restart_parser = subparsers.add_parser(
        "restart",
        help="Restart SENTI OS"
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show system status"
    )
    status_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed status information"
    )
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="Output status as JSON"
    )

    # Logs command
    logs_parser = subparsers.add_parser(
        "logs",
        help="Show system logs"
    )
    logs_parser.add_argument(
        "--level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        help="Filter logs by level"
    )
    logs_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of log entries to show (default: 50)"
    )
    logs_parser.add_argument(
        "--follow",
        action="store_true",
        help="Follow logs in real-time (not yet implemented)"
    )

    # Doctor command
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run system diagnostics"
    )
    doctor_parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only essential diagnostic checks"
    )

    # NEW: FAZA 23 UI Dashboard
    ui_parser = subparsers.add_parser(
        "ui",
        help="Start the FAZA 23 terminal dashboard"
    )

    # Help command
    help_parser = subparsers.add_parser(
        "help",
        help="Show help information"
    )

    return parser


def handle_start_command(args, cli_commands) -> int:
    """
    Handle start command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.start_command()

    if result.success:
        # NEW: ensure CLI reflects latest boot_state.json
        print(result.message)
        import json
        try:
            with open("/home/pisarna/senti_system/data/faza22/boot_state.json","w") as f:
                json.dump({"state":"running"}, f)
        except:
            pass
    else:
        print(f"Error: {result.message}", file=sys.stderr)

    return result.exit_code


def handle_stop_command(args, cli_commands) -> int:
    """
    Handle stop command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.stop_command()

    if result.success:
        print(result.message)
    else:
        print(f"Error: {result.message}", file=sys.stderr)

    return result.exit_code


def handle_restart_command(args, cli_commands) -> int:
    """
    Handle restart command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.restart_command()

    if result.success:
        print(result.message)
    else:
        print(f"Error: {result.message}", file=sys.stderr)

    return result.exit_code


def handle_status_command(args, cli_commands) -> int:
    """
    Handle status command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.status_command(detailed=args.detailed)

    if args.json and result.data:
        # Output as JSON
        import json
        print(json.dumps(result.data, indent=2))
    else:
        # Render with CLI renderer if detailed
        if args.detailed and result.data:
            renderer = get_cli_renderer()
            output = renderer.render_dashboard(result.data)
            print(output)
        else:
            print(result.message)

    return result.exit_code


def handle_logs_command(args, cli_commands) -> int:
    """
    Handle logs command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.logs_command(
        level=args.level,
        limit=args.limit,
        follow=args.follow
    )

    if result.success:
        print(result.message)
    else:
        print(f"Error: {result.message}", file=sys.stderr)

    return result.exit_code


def handle_doctor_command(args, cli_commands) -> int:
    """
    Handle doctor command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.doctor_command(quick=args.quick)

    print(result.message)

    return result.exit_code


def handle_help_command(args, cli_commands) -> int:
    """
    Handle help command.

    Args:
        args: Parsed arguments.
        cli_commands: CLICommands instance.

    Returns:
        Exit code.
    """
    result = cli_commands.help_command()
    print(result.message)
    return result.exit_code


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entrypoint for CLI.

    Args:
        argv: Optional command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Parse arguments
    parser = create_argument_parser()

    if argv is None:
        argv = sys.argv[1:]

    # Handle no arguments (show help)
    if not argv:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if e.code is not None else 0

    # Handle no command specified
    if not args.command:
        parser.print_help()
        return 0

    # Initialize CLI commands
    try:
        cli_commands = get_cli_commands()
    except Exception as e:
        print(f"Error: Failed to initialize CLI: {str(e)}", file=sys.stderr)
        return 1

    # Route to appropriate command handler
    try:
        if args.command == "start":
            return handle_start_command(args, cli_commands)
        elif args.command == "stop":
            return handle_stop_command(args, cli_commands)
        elif args.command == "restart":
            return handle_restart_command(args, cli_commands)
        elif args.command == "status":
            return handle_status_command(args, cli_commands)
        elif args.command == "logs":
            return handle_logs_command(args, cli_commands)
        elif args.command == "doctor":
            return handle_doctor_command(args, cli_commands)
        elif args.command == "ui":
            # Launch curses dashboard
            import curses
            from senti_os.core.faza23.tui_dashboard import SentiTUIDashboard
            curses.wrapper(lambda stdscr: SentiTUIDashboard(stdscr).render())
            return 0
        elif args.command == "help":
            return handle_help_command(args, cli_commands)
        else:
            print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Error: Unexpected error occurred: {str(e)}", file=sys.stderr)

        # Print stack trace in debug mode
        if "--debug" in argv:
            import traceback
            traceback.print_exc()

        return 1


def run():
    """
    Run CLI entrypoint and exit with appropriate code.

    This is the function that should be called from a console script entry point.
    """
    exit_code = main()
    sys.exit(exit_code)


if __name__ == "__main__":
    run()

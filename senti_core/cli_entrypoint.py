import sys
from .cli_commands import CLICommands

def main():
    base_dir = "/home/pisarna/senti_system"
    cli = CLICommands(base_dir)

    if len(sys.argv) < 2:
        print("Use: senti <start|stop|status|doctor>")
        return

    cmd = sys.argv[1]

    if cmd == "start":
        cli.start()
    elif cmd == "stop":
        cli.stop()
    elif cmd == "status":
        cli.status()
    elif cmd == "doctor":
        cli.doctor()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

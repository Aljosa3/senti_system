from .command_parser import parse_command
from .renderer import render_output

def run_cli(input_line: str) -> str:
    """
    Entry point for the Sapianta Chat CLI.
    Accepts raw input and returns rendered text output.
    """
    result = parse_command(input_line)
    return render_output(result)

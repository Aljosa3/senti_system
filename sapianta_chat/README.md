# Sapianta Chat

Minimal CLI chat interface with no execution capabilities.

## What This Is

A controlled conversational shell that:
- Accepts user input
- Detects basic action intent
- Returns controlled responses
- Makes no assumptions
- Executes nothing
- Claims no capabilities it does not have

## What This Is NOT

- An AI assistant
- An agent
- An execution engine
- A decision-making system
- A simulation

## Architecture

```
sapianta_chat/
├── cli.py            # Terminal input/output loop
├── engine.py         # Response generation logic
└── capabilities.py   # Explicit capability flags (all false)
```

## Usage

```bash
# From project root
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 -m sapianta_chat.cli

# Or using the launcher
python3 run_sapianta_chat.py
```

## Commands

- `status` - Show capability status
- `help` - Show available commands
- `exit`, `quit`, `q` - Exit the application

## Current Capabilities

All capabilities are explicitly disabled:
- execute_actions: False
- call_external_apis: False
- modify_system_state: False
- generate_data: False
- run_commands: False
- access_filesystem: False
- interpret_governance: False
- activate_modules: False
- make_decisions: False
- autonomous_behavior: False

## Behavior

- If input appears to be an action request (starts with create, run, execute, etc.):
  Returns: "Action detected. This capability is not implemented."

- For all other input:
  Returns: "Input acknowledged. This is a reflection message. No action will be taken."

- Empty input:
  Returns: "Input received. No content detected."

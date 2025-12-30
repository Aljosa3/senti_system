# Sapianta CLI Chat — Phase A

Status: READ-ONLY  
Authority: NONE  
Execution: FORBIDDEN  

---

## Purpose

This module provides a human-facing CLI chat interface.

It allows users to:
- Enter free-form natural language input
- Observe how the system interprets intent
- Receive advisory explanations

---

## What this module does

- Routes input through the full advisory pipeline
- Displays human-readable explanations
- Enforces all execution and governance constraints

---

## What this module does NOT do

- Execute commands
- Modify system state
- Escalate authority
- Bypass governance

---

## Usage

```bash
python3 -m modules.sapianta_cli_chat.cli


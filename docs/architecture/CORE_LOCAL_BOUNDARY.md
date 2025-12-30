# Core ↔ Local Agent Boundary

## Core (Server-side)
- Stateless
- No user identity
- No user history
- No file system access
- No execution authority
- Receives only abstracted input
- Produces advisory or validated output

## Local Agent (User-side)
- Owns all user data
- Owns conversation history
- Owns files and keys
- Decides what information is shared
- Executes actions locally (if ever)

## Non-negotiable Rule
User data MUST NOT cross into the core
except in abstracted, non-identifiable form.

Privacy is guaranteed by architecture,
not by policy.

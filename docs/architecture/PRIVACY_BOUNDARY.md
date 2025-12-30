# Privacy Boundary

## Core (Server-side)
- Stateless
- No user data persistence
- No file system access for user context
- Receives only abstracted input
- Produces advisory or validated output

## Local Agent (User-side)
- Owns all user data
- Owns history and context
- Decides what to share
- Executes actions locally
- Can operate offline

## Non-negotiable Rule
No user-identifiable or persistent data
may be stored or inferred by the core.

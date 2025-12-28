# MODULE PERMISSION DESCRIPTOR

Module Name: Sapianta Chat CLI
Module ID: sapianta_chat_cli
Phase Introduced: 73
Applies To State: DEFINED

Authority Level: ADVISORY

---

## ALLOWED OPERATIONS
- read_module_registry
- read_module_descriptions
- read_phase_documents
- generate_text
- describe_system_state

## FORBIDDEN OPERATIONS
- execute_commands
- invoke_runtime_actions
- modify_registry
- modify_state
- write_files
- access_network
- trigger_external_io

## DATA ACCESS
- read: LIMITED
- write: NONE
- external_io: NONE

## EXECUTION
- allowed: NO
- conditions: N/A

## SIDE EFFECTS
- filesystem: NONE
- network: NONE
- state_mutation: NONE

## ESCALATION
- allowed: NO
- path: N/A

## NOTES
- Conversational, advisory-only interface
- No authority over Core or other modules
- All outputs are non-binding descriptions or suggestions

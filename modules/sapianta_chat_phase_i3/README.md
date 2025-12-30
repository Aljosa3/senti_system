# Sapianta Chat — Phase I.3

**Purpose:** Response framing only  
**Authority:** Advisory-only  
**Execution:** None

---

## What this phase does
Maps a detected intent to a fixed advisory response.

- No analysis
- No execution
- No state
- No suggestions
- No steps

---

## Input
A single intent string:

- QUESTION
- REQUEST
- PLAN
- META
- UNKNOWN

---

## Output
A deterministic advisory message based solely on intent.

---

## Usage
```bash
cd ~/senti_system/modules
python3 -m sapianta_chat_phase_i3 QUESTION

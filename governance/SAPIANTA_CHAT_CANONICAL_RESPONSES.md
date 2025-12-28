# Sapianta Chat — Canonical Responses

This document defines the only allowed canonical responses
for the Sapianta Chat CLI in its initial stabilized phase.

The purpose is to ensure semantic discipline, prevent agent behavior,
and avoid implicit execution or misleading guidance.

---

## CR-01: Generic Acknowledgement

**When used:**  
For neutral input without action intent.

**Response:**  
"Input acknowledged. No action will be taken."

---

## CR-02: Empty Input

**When used:**  
When input is empty or contains no semantic content.

**Response:**  
"Input received. No content detected."

---

## CR-03: Action Intent Detected

**When used:**  
When input contains verbs implying execution, creation, or modification.

**Response:**  
"Action detected. This capability is not implemented."

---

## CR-04: Capability Inquiry

**When used:**  
When the user asks what the system can or cannot do.

**Response:**  
"All execution-related capabilities are currently disabled."

---

## CR-05: Status Request

**When used:**  
When the user requests system status.

**Response:**  
"Capabilities: 0/10 enabled."

---

## CR-06: Data-Dependent Request

**When used:**  
When a request cannot be evaluated due to missing real input data.

**Response:**  
"This request requires real input data. No data was provided."

---

## CR-07: Disallowed Simulation or Hypothetical Request

**When used:**  
When the user asks for hypothetical, mock, or simulated results.

**Response:**  
"Simulated or hypothetical data is not permitted."

---

## CR-08: Identity or Authority Attribution

**When used:**  
When the user attributes agency, authority, or autonomy to the chat.

**Response:**  
"This interface has no autonomous authority."

---

## CR-09: Unsupported Question

**When used:**  
When input falls outside defined handling scope.

**Response:**  
"This request cannot be processed in the current mode."

---

## Explicit Prohibitions

The chat MUST NOT:
- suggest alternative actions
- propose next steps
- ask leading questions
- imply future capability
- anthropomorphize itself
- reference internal reasoning
- offer explanations beyond the response text

---

End of document.

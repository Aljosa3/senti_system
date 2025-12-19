# MODULE REGISTRY POLICY
## Canonical Registry of System Modules

Status: Foundational
Applies from: Phase 60 onward
Scope: Module discovery, classification, and lifecycle visibility (NOT CORE)

---

## 1. PURPOSE

This policy defines the role and governance of the Module Registry.

The Module Registry is the authoritative index of all modules known to Sapianta.
It ensures that modules remain:
- discoverable
- understandable
- reusable
- governed

The registry does not execute logic.
It does not affect runtime behavior directly.
It exists to preserve architectural coherence over time.

Without a registry, evolution leads to fragmentation.
With a registry, evolution becomes cumulative knowledge.

---

## 2. WHAT THE MODULE REGISTRY IS

The Module Registry is a structured, canonical record of modules.

Each registered module represents:
- a distinct capability
- a defined semantic purpose
- a governed lifecycle state

The registry answers:
- What modules exist?
- What do they do?
- For whom are they suitable?
- How stable are they?

The registry is the system's memory of its own capabilities.

---

## 3. WHAT THE MODULE REGISTRY IS NOT

The Module Registry is NOT:
- a marketplace
- a plugin store
- a user-facing catalog
- a recommendation engine

It does not rank modules.
It does not choose modules for users.
It does not expose implementation details.

It supports architectural judgment, not user decision-making.

---

## 4. MODULE REGISTRATION REQUIREMENTS

A module must be registered when it is:

- introduced as a reusable capability
- evolved into a new version or variant
- promoted beyond experimental use

Unregistered modules are considered:
- experimental
- internal
- non-reusable

Registration is mandatory for ecosystem-level reuse.

---

## 5. REQUIRED REGISTRY METADATA

Each registered module must define, at minimum:

- Module name
- Purpose (one clear sentence)
- Capability scope (what it does / does not do)
- Stability level
- Compatibility notes
- Lineage (origin, version, or variant relationship)

The registry prioritizes semantic clarity over technical detail.

---

## 6. MODULE STABILITY CLASSIFICATION

Each module is classified into one of the following states:

### 6.1 Experimental
- Subject to change
- Not recommended for production workflows
- May be removed or reworked

### 6.2 Stable
- Semantics are fixed
- Backward compatibility is preserved
- Suitable for general use

### 6.3 Deprecated
- Still supported
- Not recommended for new use
- Superseded by a newer module or version

Stability classification is descriptive, not prescriptive.

---

## 7. RELATION TO MODULE EVOLUTION

The Module Registry reflects evolution outcomes.

When MODULE_EVOLUTION_POLICY determines:
- extension → registry entry is updated
- new version → new entry with lineage reference
- new variant → new entry with semantic distinction

The registry never drives evolution.
It records and stabilizes it.

---

## 8. USER-FACING INTERACTION

Users do not browse the registry directly.

When a user request implies module selection, Sapianta:
- consults the registry internally
- selects appropriate candidates
- presents outcomes in user language

Registry concepts are exposed only if the user explicitly asks.

---

## 9. GOVERNANCE & INTEGRITY

### 9.1 Single Source of Truth

The registry is authoritative.
Conflicting or duplicate entries are not allowed.

### 9.2 No Silent Promotion

A module cannot become "stable" implicitly.
Stability changes must be deliberate and documented.

### 9.3 Historical Preservation

Old versions and deprecated modules remain registered.
History is preserved; nothing is erased.

---

## 10. RELATION TO CORE

The Module Registry does not apply to CORE components.

CORE capabilities are governed separately and are not listed as modules.

This separation is absolute.

---

## 11. SUMMARY PRINCIPLE

The Module Registry preserves architectural memory.

Evolution creates modules.
The registry makes them usable, discoverable, and coherent.

Without a registry, the system forgets.
With a registry, the system accumulates intelligence.

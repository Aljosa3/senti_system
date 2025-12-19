# MODULE LIFECYCLE POLICY
## Governed Progression from Inception to Retirement

Status: Foundational
Applies from: Phase 60 onward
Scope: Module lifecycle management only (NOT CORE)

---

## 1. PURPOSE

This policy defines how modules progress through their lifecycle from inception to retirement.

Modules are not permanent by default. They emerge, stabilize, age, and may eventually retire. Each stage requires different guarantees and management.

Without explicit lifecycle governance:
- stability becomes ambiguous
- deprecation occurs silently
- removal breaks dependents
- ecosystem coherence degrades

This policy ensures that module lifecycle changes are:
- visible
- deliberate
- safe
- reversible when necessary

Module lifecycle is architectural discipline, not reactive deletion.

---

## 2. LIFECYCLE STATES

Every module exists in one of four canonical states.

### 2.1 Experimental

**Definition:**
A module under active development or validation. Its purpose, interface, or behavior may change.

**Guarantees:**
- No backward compatibility promises
- May be removed or reworked
- Not recommended for production workflows

**Intent:**
Experimental modules allow rapid iteration without ecosystem burden.

---

### 2.2 Stable

**Definition:**
A module whose semantics, purpose, and interface are fixed. It is suitable for general use.

**Guarantees:**
- Backward compatibility preserved
- Breaking changes require new version
- Semantics do not change silently

**Intent:**
Stable modules provide reliable foundation for workflows and compositions.

---

### 2.3 Deprecated

**Definition:**
A module that is no longer recommended for new use but remains supported for existing dependents.

**Guarantees:**
- Continues to function
- Receives critical fixes only
- Will not be removed while dependents exist

**Intent:**
Deprecation signals evolution without forcing immediate migration.

---

### 2.4 Archived

**Definition:**
A module that is no longer maintained or available for use. It exists only in historical records.

**Guarantees:**
- No longer accessible for new use
- Documentation and lineage preserved
- Can be restored if necessary

**Intent:**
Archival removes obsolete modules safely without erasing history.

---

## 3. STATE TRANSITIONS

Modules progress through lifecycle states based on evidence and architectural judgment.

### 3.1 Experimental → Stable

**When:**
A module has been:
- used successfully across multiple contexts
- validated through real usage patterns
- proven architecturally sound

**Evidence Required:**
- usage history
- semantic clarity
- absence of fundamental design issues

**Authorization:**
Internal architectural judgment by Sapianta.

---

### 3.2 Stable → Deprecated

**When:**
A module is superseded by:
- a better alternative
- a new version
- architectural evolution

**Evidence Required:**
- existence of migration path
- clarity on why deprecation is beneficial

**Authorization:**
Internal architectural judgment with user notification.

---

### 3.3 Deprecated → Archived

**When:**
A deprecated module has:
- no remaining active dependents
- been deprecated for sufficient time
- clear successor or alternative

**Evidence Required:**
- dependency analysis showing no active use
- historical significance documented

**Authorization:**
Internal architectural judgment.

---

### 3.4 Stability Is Never Implicit

A module remains experimental until explicitly promoted.

Promotion to stable is deliberate, not automatic.

---

## 4. STABILITY GUARANTEES

### 4.1 Experimental Modules

**No guarantees:**
Users assume risk when using experimental modules.

**Communication:**
Status is clearly indicated.

---

### 4.2 Stable Modules

**Strong guarantees:**
- Interface does not change
- Semantics do not change
- Behavior is predictable

**Exception:**
Critical security fixes may alter behavior if necessary, but are announced.

---

### 4.3 Deprecated Modules

**Maintenance guarantees:**
- Critical bugs are fixed
- Security issues are addressed
- No new features are added

**Continuation guarantee:**
Deprecated modules remain available until archival.

---

### 4.4 Archived Modules

**No operational guarantees:**
Archived modules are not available for use.

**Historical guarantee:**
Documentation and lineage remain accessible.

---

## 5. DEPRECATION POLICY

Deprecation is announcement, not removal.

### 5.1 Announcement

Deprecation must be:
- clearly communicated
- explained with rationale
- accompanied by migration guidance

### 5.2 Coexistence

Deprecated and successor modules coexist.

Users are not forced to migrate immediately.

### 5.3 Migration Paths

When a module is deprecated, Sapianta provides:
- guidance on alternatives
- explanation of differences
- migration approach if needed

Migration remains optional.

### 5.4 Non-Forced Transitions

Users decide when to migrate from deprecated modules.

Forced upgrades are not allowed.

---

## 6. REMOVAL & ARCHIVAL

### 6.1 When Removal Is Allowed

A module may be archived only when:
- it is deprecated
- no active dependents exist
- sufficient notice has been given
- historical documentation is preserved

### 6.2 Why Archival Is Preferred Over Deletion

Archival preserves:
- historical context
- lineage relationships
- lessons learned

Deletion erases institutional knowledge.

### 6.3 Silent Deletion Is Forbidden

A module cannot be removed without:
- prior deprecation
- dependency verification
- documentation of rationale

Sudden disappearance is architectural violation.

---

## 7. USER-FACING BEHAVIOR

Users interact with lifecycle states through clear status indicators, not technical terminology.

### 7.1 Clear Status

Module status is visible when relevant:
- "This module is experimental and may change."
- "This module is stable and production-ready."
- "This module is deprecated; consider [alternative]."

### 7.2 Practical Implications

Users understand:
- what they can rely on
- what risks exist
- what alternatives are available

Lifecycle state translates to practical guidance.

### 7.3 No Architectural Burden

Users do not need to understand:
- promotion criteria
- archival procedures
- registry mechanics

They see outcomes, not processes.

---

## 8. RELATION TO OTHER POLICIES

This policy operates in conjunction with:

### 8.1 MODULE_EVOLUTION_POLICY.md

Evolution creates new modules or versions.
Lifecycle governs their progression toward stability or retirement.

### 8.2 MODULE_REGISTRY_POLICY.md

The registry records lifecycle state.
Lifecycle transitions update registry entries.

Together, these policies ensure:
- modules evolve deliberately
- modules are discoverable
- modules age transparently

---

## 9. MODULE LIFECYCLE DOES NOT AFFECT CORE

Module lifecycle applies only to modules.

CORE components follow separate governance:
- CORE_GOVERNANCE_PRINCIPLE.md
- CORE_UPGRADE_PROTOCOL.md

CORE does not have "experimental" or "deprecated" states.

This distinction is absolute.

---

## 10. SUMMARY PRINCIPLE

Modules are born experimental.
They earn stability through validation.
They age transparently through deprecation.
They retire deliberately through archival.

At every stage, the system knows what each module is,
what it guarantees, and where it is heading.

Lifecycle clarity is architectural maturity.

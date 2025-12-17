# FAZA 59.7 — SEMANTIC LOCK PREPARATION

**Phase:** FAZA 59.7
**Title:** Semantic & Pedagogical Constitution Preparation
**Status:** Active
**Type:** Non-Technical, Non-Security
**Purpose:** Prepare normative and semantic documents for CORE LOCK

---

## IMPORTANT NOTICE

**THIS IS NOT CORE LOCK.**

This phase does NOT:
- Lock the CORE
- Implement cryptography
- Implement identity or authority systems
- Modify runtime behavior
- Change or write code
- Implement security enforcement
- Create filesystem protection
- Integrate mutation engines with governance

**This phase ONLY prepares semantic and normative foundations that will later be locked at FAZA 60.**

---

## PURPOSE

FAZA 59.7 exists to establish the semantic constitution of Sapianta OS before technical CORE LOCK execution. This phase defines:

1. **The language of the system** - How the system understands requests
2. **Normative obligations** - How the system must respond
3. **Teaching responsibility** - How the system guides users
4. **Boundaries of adaptation** - What can evolve vs what remains fixed

These semantic foundations must be established and reviewed **before** any technical enforcement mechanisms are activated.

---

## WHY SEMANTIC LOCKING PRECEDES TECHNICAL CORE LOCK

Technical CORE LOCK (FAZA 60) will make the system's core behavior immutable through:
- Cryptographic checksums
- Runtime enforcement
- File system protection
- Identity and authority verification

However, **before** these technical mechanisms activate, the system must know:
- What it means to receive a valid request
- What obligations it has when responding
- When it must refuse vs guide
- How it maintains pedagogical responsibility

**If we lock the implementation before locking the meaning, we risk cementing undefined or incorrect semantic behavior.**

Therefore: **Semantic lock precedes technical lock.**

---

## PRINCIPLE: WE LOCK FACTS, NOT IMPLEMENTATIONS

### What We Lock (Semantic Layer)

**Facts:**
- The system does not accept implicit or free-form requests
- The system does not guess intent
- The system can refuse requests
- The system must explain refusals in human language
- The system must guide users toward achievable alternatives

**Obligations:**
- When refusing, the system MUST explain why
- When refusing, the system MUST consider user context
- When refusing, the system MUST suggest alternatives
- The system MUST NOT require technical vocabulary from users
- The system MUST NOT refuse without explanation

**Boundaries:**
- The system MUST enable improvement of pedagogical responses over time
- The system MUST NOT change semantic rules through adaptation
- The system MUST NOT mutate core language definitions

### What We Leave Open (Implementation Layer)

**Methods:**
- How explanations are phrased (tone, examples, detail level)
- How learning signals are collected
- Which pedagogical strategies are used
- How much guidance is offered

**Interfaces:**
- UX design and presentation
- Frontend interaction patterns
- Visualization of system state
- Learning progress tracking

**Adaptation:**
- Tone calibration based on user experience
- Help quantity adjustment
- Example selection strategies
- Progressive disclosure mechanisms

---

## SCOPE OF FAZA 59.7

### IN SCOPE

✅ **Semantic Rules**
- Definition of valid system language (PromptObject v1)
- Normative requirements for system responses
- Obligation to explain refusals
- Obligation to guide users

✅ **Pedagogical Constitution**
- Teaching responsibility of the system
- Role-aware guidance principles
- Adaptive learning boundaries
- Context-sensitive communication

✅ **Document Preparation**
- Creation of normative documents
- Definition of locked vs editable elements
- Establishment of semantic invariants
- Review and validation of semantic foundations

### OUT OF SCOPE

❌ **Technical Implementation**
- Cryptographic enforcement
- Filesystem protection
- Runtime mutation detection
- Import hooks or code guards

❌ **Security Infrastructure**
- Identity verification systems
- Authority delegation mechanisms
- ADMIN SESSION management
- Cryptographic signing

❌ **Code Modifications**
- Integration of mutation engines with governance
- Control Layer enforcement changes
- Execution Layer modifications
- Security Manager updates

❌ **User Interface**
- Frontend UI design
- Specific interaction flows
- Visual presentation
- UX implementation details

---

## DELIVERABLES

FAZA 59.7 produces exactly THREE normative documents:

### 1. PROMPT_OBJECT_V1.md
**Status:** LOCKED AT FAZA 60

The semantic constitution of system language. Defines:
- What constitutes a valid system request
- Internal protocol structure
- Normative principles (non-guessing, refusal capability)
- Teaching obligations (explanation, guidance, context-awareness)
- Adaptation boundaries (improve pedagogy, preserve semantics)

### 2. ROLE_AWARE_GUIDANCE_LAYER_SPEC.md
**Status:** EDITABLE (POST-FAZA 60)

The specification of how the system fulfills teaching responsibility. Describes:
- How system determines user context/authority
- How system evaluates request achievability
- How system communicates refusals in human language
- How system suggests alternatives

This is a policy/behavior specification, not core.

### 3. ADAPTIVE_GUIDANCE_LEARNING_POLICY.md
**Status:** EDITABLE (POST-FAZA 60)

The policy for pedagogical adaptation without core mutation. Describes:
- Learning signals (acceptance, correction, repetition)
- Adaptable elements (tone, help quantity, examples)
- Prohibited mutations (rules, validations, semantics)

This is a policy document, not core.

---

## CANONICAL CLAUDE CODE PROMPT FOR SEMANTIC LOCK PREPARATION

The following prompt is the **CANONICAL** specification for executing FAZA 59.7. It must be used exactly as written to generate the three normative documents listed above.

**Execution Timing:** BEFORE FAZA 60 (CORE LOCK)
**Review Required:** YES - All resulting documents must be reviewed before CORE LOCK
**Technical Enforcement:** NONE - This phase performs no technical implementation

---

### 🔐 CANONICAL PROMPT

```
🔐 PROMPT ZA CLAUDE CODE

Sapianta OS — FAZA 60 (CORE LOCK PREPARATION)

Deluješ kot Claude Code, sistemski arhitekt in dokumentacijski agent za projekt Sapianta OS (Senti System).

Sapianta OS vstopa v FAZO 60 — CORE LOCK.

Tvoja naloga je izključno ustvariti in umestiti normativne dokumente, ki bodo pripravljeni za zaklep.
NE piši kode. NE implementiraj funkcionalnosti.

1️⃣ KLJUČNA NAČELA (OBVEZNO)

FAZA 60:

zaklene semantiko jezika sistema

zaklene normativne obveznosti sistema

NE zaklene:

pedagoških metod

UX oblik

modela vlog

učnih strategij

adaptivnih mehanizmov

Zaklepamo dejstvo, ne izvedbe.

2️⃣ TVOJA NALOGA

Ustvari TOČNO TRI (3) dokumente, vsakega v celoti.

🔒 A) PROMPT_OBJECT_V1.md

Status: LOCKED AT FAZA 60

Ta dokument je ustava jezika sistema.

V njem MORAŠ:

Definirati PromptObject v1 kot interni protokol

kaj pomeni veljaven sistemski poziv

katera polja obstajajo (interno)

pomen teh polj

brez UX, brez uporabniških primerov

Zakleniti naslednja normativna načela:

sistem ne sprejema implicitnih ali prostih pozivov

sistem ne ugiba namena

sistem zna zavrniti poziv

Zakleniti učiteljsko obveznost sistema:

sistem MORA ob zavrnitvi:

razložiti, zakaj cilja ni mogoče doseči

upoštevati trenutno avtoriteto / kontekst uporabnika

usmeriti uporabnika k dovoljeni ali alternativni poti

sistem NE SME:

zahtevati poznavanja internih tehničnih pojmov

zavrniti brez razlage

Zakleniti postulat adaptivne zmožnosti:

sistem MORA omogočati izboljševanje učnih odzivov skozi čas

brez spreminjanja semantike jezika

brez samovoljne mutacije jedra

📌 Dokument mora vsebovati jasno oznako:

Status: LOCKED AT FAZA 60

🔓 B) ROLE_AWARE_GUIDANCE_LAYER_SPEC.md

Status: EDITABLE (POST-FAZA 60)

Ta dokument opisuje kako sistem uresničuje svojo učiteljsko vlogo.

V njem opiši:

da sistem:

sam pozna trenutno avtoriteto / kontekst uporabnika

uporabnik NE vpisuje vlog

uporabnik NE pozna pojmov kot so issuer, role, permission

da sistem presoja:

ali je cilj dosegljiv v trenutnem kontekstu

ali zahteva višjo avtoriteto

da sistem ob zavrnitvi:

govori v človeškem jeziku

govori v ciljih, ne v pravilih

ponudi alternativno pot (predlog, preoblikovanje, eskalacijo)

Ta dokument je policy / behavior specifikacija, ne jedro.

🔓 C) ADAPTIVE_GUIDANCE_LEARNING_POLICY.md

Status: EDITABLE (POST-FAZA 60)

Ta dokument določa kako se sistem uči iz interakcij z uporabniki, brez posega v jedro.

V njem opiši:

katere signale sistem lahko uporablja:

sprejem ali zavrnitev predlagane poti

popravljanje pozivov

ponavljanje istih napak

kaj se lahko prilagaja:

ton razlage

količina pomoči

izbira primerov

česa sistem NE SME spreminjati:

pravil PromptObject v1

validacij

semantike jezika

3️⃣ PREPOVEDI (STROGO)

NE SMEŠ:

pisati kode

opisovati UI

opisovati algoritmov učenja

uvajati imenovanih vlog (admin, operator …)

zaklepati karkoli razen normativnih načel

4️⃣ IZHOD

Na koncu:

izpiši vse tri dokumente v celoti

jasno loči vsak dokument

uporabi miren, normativen, profesionalen ton

brez filozofiranja

brez marketinškega jezika

5️⃣ CILJ

Po koncu mora biti Sapianta OS:

pripravljen za FAZO 60

semantično zaklenjen

pedagoško odgovoren

odprt za dolgoročni razvoj
```

---

## EXECUTION REQUIREMENTS

### Pre-Execution

1. Verify current phase status (FAZA 52 complete, FAZA 58-60 not yet executed)
2. Confirm no technical CORE LOCK has been activated
3. Ensure audit record from 2025-12-17 has been reviewed

### Execution

1. Use the canonical prompt exactly as specified above
2. Generate all three documents in full
3. Place documents in appropriate locations
4. Ensure proper status markers (LOCKED vs EDITABLE)

### Post-Execution

1. Review all generated documents for:
   - Clarity of semantic rules
   - Completeness of normative obligations
   - Proper separation of locked vs editable elements
   - Absence of implementation details
2. Validate no code has been written
3. Validate no technical enforcement has been implemented
4. Document review completion in phase record

---

## RELATIONSHIP TO OTHER PHASES

### Prerequisites

- **FAZA 52:** Governance & Observability (Complete)
- **Pre-CORE LOCK Audit:** System assessment completed (2025-12-17)

### Successors

- **FAZA 58:** Integrity Audit Pre-Lock Validation (Not yet implemented)
- **FAZA 59:** Lock Preparation Human Confirmation (Not yet implemented)
- **FAZA 60:** CORE LOCK Execution (Not yet implemented)

### Distinction from FAZA 60

| Aspect | FAZA 59.7 | FAZA 60 |
|--------|-----------|---------|
| **Nature** | Semantic preparation | Technical enforcement |
| **Output** | Normative documents | Immutable CORE |
| **Scope** | Language & obligations | Runtime protection |
| **Implementation** | None | Cryptography, checksums, guards |
| **Status** | Preparatory | Constitutional |
| **Reversibility** | Documents can be revised before FAZA 60 | Irreversible without CORE UPGRADE |

---

## SUCCESS CRITERIA

FAZA 59.7 is complete when:

1. ✅ All three normative documents exist and are complete
2. ✅ PROMPT_OBJECT_V1.md clearly marks locked semantic rules
3. ✅ ROLE_AWARE_GUIDANCE_LAYER_SPEC.md clearly marks editable policy
4. ✅ ADAPTIVE_GUIDANCE_LEARNING_POLICY.md clearly marks editable policy
5. ✅ No code has been written or modified
6. ✅ No technical enforcement has been implemented
7. ✅ Documents have been reviewed for semantic clarity
8. ✅ Distinction between locked and editable is clear
9. ✅ Phase completion has been documented

---

## GOVERNANCE NOTE

This phase operates under the governance principle:

**"Meaning before mechanism. Constitution before enforcement."**

Technical CORE LOCK (FAZA 60) will enforce immutability, but only after the system knows what must remain immutable. FAZA 59.7 establishes that semantic foundation.

No authority escalation is required for FAZA 59.7 execution, as it creates documents for review, not binding system changes.

Final authority for proceeding to FAZA 60 remains with System Architect after review of FAZA 59.7 outputs and completion of FAZA 58-59 technical prerequisites.

---

**Phase Status:** Active
**Phase Owner:** System Architect
**Execution Mode:** Document generation only
**Technical Impact:** None
**Review Required:** Yes (before FAZA 60)

---

*This document establishes FAZA 59.7 as the semantic constitution preparation phase of Sapianta OS. It defines scope, requirements, and the canonical prompt for execution. No technical implementation occurs in this phase.*

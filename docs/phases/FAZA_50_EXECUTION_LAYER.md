# FAZA 50 — Execution Layer (Controlled Execution)

## Status
**FAZA 50: ZAKLJUČENA**

- Zaključni tag: `v0.50-execution-layer-complete`
- Pod-faze (FILE):
  - FILE 1/? — Minimal Execution Engine
  - FILE 2/? — Guarded Lifecycle Hooks
  - FILE 3/? — Resolver Guard & Executor Contract

FAZA 50 predstavlja **prvi stabilni in nadzorovani execution sloj** sistema Senti OS.

---

## Namen FAZE 50

Namen FAZE 50 je omogočiti, da sistem:
- **dejansko izvaja kodo** (execution),
- vendar to počne **strogo nadzorovano, deterministično in brez avtonomije**.

Gre za prehod iz faz, kjer sistem:
- odloča, validira in filtrira (FAZA 45–49),

v fazo, kjer sistem:
- **izvede dovoljeni ukaz**,  
- in to stori na varen, pregleden in ponovljiv način.

---

## Arhitekturni obseg FAZE 50

FAZA 50 definira **Execution Layer**, ki vključuje:

- `ExecutionEngine`
- `ExecutionResult`
- `ExecutionReport`
- lifecycle hooke (`pre_execute`, `post_execute`)
- resolver za executor
- strogo validacijo executor pogodbe

FAZA 50 **ne uvaja inteligence**, temveč **kontrolirano izvajanje**.

---

## Kaj sistem PO FAZI 50 ZNA

Po zaključku FAZE 50 sistem zna:

- ✔️ izvesti ukaz prek `ExecutionEngine.execute()`
- ✔️ deterministično obravnavati uspeh ali napako
- ✔️ zajeti rezultat v `ExecutionResult`
- ✔️ vrniti strukturiran `ExecutionReport`
- ✔️ zaščititi execution tok pred:
  - napakami v lifecycle hookih
  - napačnimi resolverji
  - neveljavnimi executorji
- ✔️ zavrniti execution na varen način (FAILED), brez crasha

Execution tok je:
- determinističen,
- stateless,
- brez skritih stranskih učinkov.

---

## Guardi in varnostni robovi

### 1. Lifecycle hook guardi (FILE 2)

- `pre_execute`:
  - če pade → execution se zaključi z FAILED
  - executor se **ne kliče**
- `post_execute`:
  - če pade → execution se zaključi z FAILED
- nobena izjema iz hookov ne uide iz engine-a

### 2. Resolver & executor contract guard (FILE 3)

- `resolver.resolve()` mora vrniti **callable**
- executor mora imeti podpis:
  ```python
  def executor(*, context): ...
None, napačen tip ali napačen podpis → FAILED

brez fallbackov ali implicitnih popravil

S tem je execution pogodba eksplicitna in stroga.

Česa sistem ZAVESTNO ŠE NE ZNA
FAZA 50 namenoma NE omogoča:

❌ avtonomnega odločanja

❌ ponavljanja (retry)

❌ optimizacije ali učenja

❌ spreminjanja lastne kode

❌ vodenja stanja med klici

❌ logiranja ali opazovanja (observability)

FAZA 50 je izključno execution sloj, brez inteligence.

Meje FAZE 50
FAZA 50 se konča pri:

uspešni ali neuspešni izvedbi enega execution koraka,

vrnitvi strukturiranega poročila.

Vse, kar vključuje:

politiko,

budget enforcement,

opazovanje,

avtonomijo,

spada v FAZA 51+.

Povezani tagi
v0.49-controlled-execution

v0.50-file2-guarded-hooks

v0.50-file3-resolver-guard

v0.50-execution-layer-complete ← uradni zaključek FAZE 50

Povzetek v enem stavku
FAZA 50 omogoči, da Senti OS prvič varno in nadzorovano izvaja kodo, brez avtonomije, z jasno definirano execution pogodbo in zaprtimi varnostnimi robovi.

To predstavlja stabilen temelj za nadaljnje faze sistema.
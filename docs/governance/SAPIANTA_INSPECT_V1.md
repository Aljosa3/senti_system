SAPIANTA INSPECT — v1 (MINIMAL, READ-ONLY)

Status: LOCKED
Avtoriteta: Governance
Veljavnost: Globalna

Odvisnosti:
- FAZA I — SAPIANTA CHAT STATE MACHINE (LOCKED)
- FAZA II — SAPIANTA MANDATE v1 + ROUTING_CHECK (LOCKED)

======================================================================

SECTION 0 — NAMEN

INSPECT v1 omogoča read-only vpogled v notranje stanje sistema.

INSPECT:

- NE spreminja stanja
- NE sproža prehodov
- NE vpliva na tok
- NE odloča
- NE izvaja

INSPECT obstaja izključno zato, da je sistem:

- pregleden
- sledljiv
- auditen
- varen za FAZO III

======================================================================

SECTION 1 — OSNOVNA DEFINICIJA

INSPECT je pasivni vpogledni sloj, ki lahko:

- bere stanje state machine
- bere zadnji / aktivni mandat
- bere rezultat ROUTING_CHECK
- bere zgodovino prehodov (trace)

INSPECT NI:

- debugger
- kontrolna plošča
- UI
- runtime guard
- izvajalec

======================================================================

SECTION 2 — KAJ JE DOVOLJENO INSPECTATI (MINIMALNI OBSEG)

INSPECT v1 MORA omogočiti vpogled v:

----------------------------------------------------------------------
1️⃣ Trenutno stanje chata
----------------------------------------------------------------------

{
  "current_state": "ADVISORY | USER_DECISION | ...",
  "previous_state": "string",
  "timestamp": "ISO-8601"
}

----------------------------------------------------------------------
2️⃣ Zadnji obravnavani mandat
----------------------------------------------------------------------

{
  "id": "uuid",
  "intent": "string",
  "action": "string",
  "scope": { ... },
  "constraints": { ... },
  "limits": { ... },
  "confirmed": true | false,
  "revoked": true | false,
  "expires_at": "ISO-8601"
}

----------------------------------------------------------------------
3️⃣ Zadnji rezultat ROUTING_CHECK
----------------------------------------------------------------------

{
  "status": "OK | CLARIFY | REFUSE",
  "reason": "string",
  "checked_at": "ISO-8601"
}

----------------------------------------------------------------------
4️⃣ Trace prehodov (minimalno)
----------------------------------------------------------------------

[
  {
    "from": "STATE",
    "to": "STATE",
    "at": "ISO-8601",
    "trigger": "USER_INPUT | SYSTEM"
  }
]

Opomba:
- trigger je informativno polje
- nima vpliva na logiko
- ne sproža nobenih prehodov
- služi izključno auditabilnosti

======================================================================

SECTION 3 — ABSOLUTNE OMEJITVE (HARD NO)

INSPECT v1 STROGO NE SME:

- ❌ spreminjati current_state
- ❌ popravljati mandata
- ❌ potrjevati ali zavračati
- ❌ sprožiti ROUTING_CHECK
- ❌ sprožiti EXECUTION
- ❌ vplivati na čas (expires_at)
- ❌ dodajati ali odstranjevati trace zapise

INSPECT JE READ-ONLY.
Vsaka kršitev → governance violation.

======================================================================

SECTION 4 — ARHITEKTURNA LOČITEV

INSPECT:

- bere iz obstoječih struktur (state machine context)
- nima lastne logike odločanja
- nima pravice pisanja
- je ločen modul

INSPECT nikoli ne kliče:

- handlerjev
- transition funkcij
- execution stuba

======================================================================

SECTION 5 — DOSTOP

INSPECT je lahko klican:

- iz CLI
- iz testov
- iz prihodnjega UI (FAZA VII)

Vedno pa:

- eksplicitno
- zavestno
- brez stranskih učinkov

======================================================================

SECTION 6 — NEGATIVNI SCENARIJI

Če podatki ne obstajajo:

- brez aktivnega mandata → mandate: null
- brez trace → prazen seznam
- brez routing rezultata → routing: null

INSPECT nikoli ne sproži CLARIFY ali REFUSE.
INSPECT samo POROČA.

======================================================================

SECTION 7 — DEFINITION OF DONE (FAZA IV — INSPECT v1)

FAZA IV JE ZAKLJUČENA, KO:

- INSPECT modul obstaja
- omogoča vpogled v:
  - stanje
  - mandat
  - routing rezultat
  - trace
- nobena inspect funkcija nima side-effectov
- inspect ne spreminja nobenega objekta
- inspect je uporaben brez FAZE III

Če katerikoli pogoj ni izpolnjen:
FAZA IV NI ZAKLJUČENA.

======================================================================

SECTION 8 — ZAKAJ FAZA IV PRE FAZE III

Brez INSPECT:

- execution je slep
- audit ni mogoč
- napake so nevidne
- varnost je navidezna

INSPECT je:
→ predpogoj za varno izvajanje.

======================================================================

SECTION 9 — KONČNI ZAKLEP

INSPECT v1 je minimalen, pasiven in zaklenjen.

Ne dodajati funkcij.
Ne optimizirati.
Ne “pomagati”.

Najprej VIDIMO.
Šele potem DELAMO.

======================================================================

END OF DOCUMENT

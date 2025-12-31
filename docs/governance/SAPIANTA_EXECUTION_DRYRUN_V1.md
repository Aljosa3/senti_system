SAPIANTA EXECUTION DRY-RUN — v1 (FAZA III.0)

Status: LOCKED
Avtoriteta: Governance
Veljavnost: Globalna

Odvisnosti:
- FAZA I — SAPIANTA CHAT STATE MACHINE (LOCKED)
- FAZA II — SAPIANTA MANDATE v1 + ROUTING_CHECK (LOCKED)
- FAZA IV — INSPECT v1 (LOCKED)
- SAPIANTA EXECUTION POLICY v1 (LOCKED)

======================================================================

SECTION 0 — NAMEN

FAZA III.0 (EXECUTION DRY-RUN) definira simulirano izvajanje mandata
brez kakršnihkoli realnih učinkov.

Namen dry-run faze je:
- preveriti celoten tok (end-to-end)
- potrditi delovanje policy gate-ov
- ustvariti realističen audit in trace
- omogočiti učenje in pregled brez tveganja

FAZA III.0 JE OBVEZNA generalka pred vsakim realnim executionom.

======================================================================

SECTION 1 — KAJ JE EXECUTION DRY-RUN

EXECUTION DRY-RUN je:

- simulacija executiona
- deterministična
- brez stranskih učinkov
- popolnoma auditabilna
- popolnoma inspectable

EXECUTION DRY-RUN NI:

- pravi execution
- test API klicev
- sandbox zunanjih sistemov
- optimizacija
- avtomatizacija

======================================================================

SECTION 2 — ABSOLUTNI POGOJI ZA DRY-RUN

EXECUTION DRY-RUN je dovoljen IZKLJUČNO, če:

1. ChatStateMachine je v stanju EXECUTION
2. Mandat obstaja
3. Mandat ima confirmed = true
4. Mandat ni revoked
5. Mandat ni potekel (expires_at)
6. ROUTING_CHECK status == OK
7. EXECUTION POLICY v1 je aktivna
8. INSPECT v1 je na voljo

Če katerikoli pogoj NI izpolnjen:
→ DRY-RUN SE NE IZVEDE

======================================================================

SECTION 3 — OBNAŠANJE DRY-RUN IZVAJANJA

Med dry-run executionom sistem:

- NE kliče zunanjih API-jev
- NE zapisuje v zunanje sisteme
- NE spreminja stanja zunaj sistema
- NE izvaja retry-jev
- NE optimizira parametrov

Namesto tega sistem:

- ustvari simuliran execution zapis
- zapiše audit podatke
- vrne RESULT, ki jasno označuje DRY-RUN

======================================================================

SECTION 4 — REZULTAT DRY-RUN

Vsak dry-run execution MORA vrniti rezultat v obliki:

{
  "execution_type": "DRY_RUN",
  "mandate_id": "uuid",
  "action": "string",
  "scope": { ... },
  "simulated_effect": "opis v naravnem jeziku",
  "status": "SIMULATED_SUCCESS | SIMULATED_FAILURE",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601"
}

Rezultat:

- ne sme biti dvoumen
- mora jasno označiti, da NI šlo za realno izvedbo
- je inspectable

======================================================================

SECTION 5 — AUDIT & TRACE (OBVEZNO)

Dry-run MORA ustvariti audit zapis, enakovreden pravemu executionu:

- mandate.id
- execution_type = DRY_RUN
- start / end čas
- simuliran rezultat
- uporabljeni parametri
- morebitne simulirane napake

Audit zapisi so:

- read-only
- inspectable preko INSPECT
- nikoli retroaktivno spremenjeni

======================================================================

SECTION 6 — VPLIV NA STATE MACHINE

Dry-run:

- NE spremeni pomena stanja EXECUTION
- po zaključku preide v RESULT
- nato v IDLE (po obstoječih pravilih)

Dry-run:

- NE uvaja novih stanj
- NE spreminja state machine logike

======================================================================

SECTION 7 — ABSOLUTNE PREPOVEDI (HARD NO)

Strogo prepovedano:

- izvajanje realnih učinkov
- prikriti realni klici
- “testni” API klici
- zapis v sandbox zunanjih sistemov
- samodejni retry
- avtomatska eskalacija v pravi execution

Vsaka kršitev:
→ governance violation

======================================================================

SECTION 8 — ZAKAJ FAZA III.0 OBSTAJA

Brez FAZE III.0:

- execution se prvič zgodi brez generalke
- napake so odkrite prepozno
- zaupanje v sistem je navidezno
- audit ni preizkušen

FAZA III.0 omogoča:
→ videti sistem v akciji brez tveganja.

======================================================================

SECTION 9 — DEFINITION OF DONE (FAZA III.0)

FAZA III.0 JE ZAKLJUČENA, KO:

- ta dokument obstaja in je zaklenjen
- execution koda še NE obstaja
- pravila dry-run izvajanja so jasna
- sistem še vedno ne more povzročiti realnih učinkov
- INSPECT lahko prikaže dry-run rezultat

======================================================================

SECTION 10 — KONČNI ZAKLEP

FAZA III.0 je varna meja med teorijo in prakso.

Najprej simulacija.
Potem odločitev.
Šele nato realni učinki.

Če obstaja dvom:
→ DRY-RUN, ne EXECUTION.

======================================================================

END OF DOCUMENT

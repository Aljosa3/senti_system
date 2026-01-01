SAPIANTA EXECUTION POLICY — v1 (LOCKED)

Status: LOCKED
Avtoriteta: Governance
Veljavnost: Globalna

Odvisnosti:
- FAZA I — SAPIANTA CHAT STATE MACHINE (LOCKED)
- FAZA II — SAPIANTA MANDATE v1 + ROUTING_CHECK (LOCKED)
- FAZA IV — INSPECT v1 (LOCKED)

======================================================================

SECTION 0 — NAMEN

Ta dokument definira absolutna pravila izvajanja (EXECUTION) v sistemu SAPIANTA.

EXECUTION je edini del sistema, ki ima pravico povzročiti realne učinke
(zapis, klic API, spremembo stanja zunanjega sistema).

Cilj tega dokumenta je:
- preprečiti nenadzorovano izvajanje
- zagotoviti človeško suverenost
- omogočiti auditabilno in varno avtomatizacijo

Če pride do konflikta med kodo in tem dokumentom:
IMA PREDNOST TA DOKUMENT.

======================================================================

SECTION 1 — DEFINICIJA EXECUTION

EXECUTION je:

- izvajanje potrjenega mandata
- omejeno izključno na obseg mandata
- deterministično
- auditabilno
- preklicljivo

EXECUTION NI:

- odločanje
- optimizacija
- svetovanje
- interpretacija uporabnika
- popravljanje mandata
- ponovna validacija namena

======================================================================

SECTION 2 — ABSOLUTNI POGOJI ZA EXECUTION (GATE)

EXECUTION je dovoljen IZKLJUČNO, če so izpolnjeni VSI pogoji:

1. ChatStateMachine je v stanju EXECUTION
2. Mandat obstaja
3. Mandat ima confirmed = true
4. Mandat ni revoked
5. Mandat ni potekel (expires_at)
6. ROUTING_CHECK je bil uspešen (status = OK)
7. INSPECT je na voljo (FAZA IV obstaja)
8. Execution policy v1 je aktivna

Če katerikoli pogoj NI izpolnjen:
→ EXECUTION JE STROGO PREPOVEDAN

======================================================================

SECTION 3 — NAJMANJŠA DOVOLJENA AKCIJA (MINIMAL ACTION)

Vsaka execution implementacija mora:

- izvesti NAJMANJŠO možno akcijo
- brez implicitnih razširitev
- brez “helper” vedenja

Primer:
Če mandat dovoljuje BUY 100 EUR:
→ BUY 100 EUR
→ ne 101
→ ne večkrat
→ ne retry brez vednosti

======================================================================

SECTION 4 — OMEJITVE IN MEJE

EXECUTION:

- nikoli ne preseže limits
- nikoli ne ignorira constraints
- nikoli ne razširi scope
- nikoli ne spremeni mandata

Mandat je zgornja meja.
Execution je podrejena mandatu.

======================================================================

SECTION 5 — STOP & ABORT PRAVILA

EXECUTION SE MORA TAKOJ USTAVITI, če:

- pride do napake
- pride do neujemanja mandata
- zunanja storitev vrne nepričakovan odgovor
- sistem izgubi sledljivost (trace / inspect)
- uporabnik prekliče mandat (revoked = true)

V takem primeru:
- execution se prekine
- stanje se vrne v RESULT ali IDLE
- napaka se zabeleži
- NI avtomatskega retry-ja

======================================================================

SECTION 6 — BREZ AVTOMATIKE

Strogo prepovedano:

- avtomatsko ponavljanje (retry)
- avtomatsko optimiziranje
- avtomatsko razširjanje obsega
- verižni execution
- “samozdravljenje” brez vednosti uporabnika

Vsak nov execution:
→ zahteva NOV mandat
→ zahteva NOVO potrditev

======================================================================

SECTION 7 — AUDIT & TRACE (OBVEZNO)

Vsak execution MORA ustvariti audit zapis:

- mandate.id
- execution_start_time
- execution_end_time
- rezultat (success / failure)
- uporabljeni parametri
- napake (če obstajajo)

Ti podatki so:
- read-only
- inspectable
- nikoli retroaktivno popravljeni

======================================================================

SECTION 8 — EXECUTION KOT PODREJEN MODUL

Execution modul:

- ne kliče Chat logike
- ne kliče advisory logike
- ne kliče routing_check
- ne kliče inspect

Execution JE KLICAN, ne kliče.

======================================================================

SECTION 9 — PREPOVEDI (HARD NO)

Strogo prepovedano:

- execution brez mandata
- execution brez confirmed = true
- execution po expires_at
- execution z revoked mandatom
- execution brez audit sledi
- execution brez INSPECT sloja
- execution, ki spremeni mandat

Vsaka kršitev:
→ governance violation

======================================================================

SECTION 10 — DEFINITION OF DONE (FAZA III — POLICY)

EXECUTION POLICY v1 JE ZAKLJUČENA, KO:

- ta dokument obstaja in je zaklenjen
- execution implementacija NE obstaja
- vsi pogoji za execution so jasno zapisani
- sistem še vedno ne more izvajati realnih dejanj

Ta faza zavestno NE vključuje kode.

======================================================================

SECTION 11 — KONČNI ZAKLEP

Ta dokument je zadnja varnostna pregrada
pred tem, da sistem dobi realne učinke.

Najprej pravila.
Potem izvajanje.

Če obstaja dvom:
→ NI EXECUTIONA.

======================================================================

END OF DOCUMENT

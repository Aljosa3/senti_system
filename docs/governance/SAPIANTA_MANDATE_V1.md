# SAPIANTA MANDATE — v1 (MINIMAL)
Status: LOCKED  
Avtoriteta: Governance  
Veljavnost: Globalna  
Odvisnost: FAZA I — SAPIANTA CHAT STATE MACHINE (COMPLETED)

======================================================================

SECTION 0 — NAMEN

----------------------------------------------------------------------
Minimalni mandat v1 definira najmanjši možni dovolilni objekt, ki:

- omogoča ROUTING_CHECK
- omogoča MANDATE_CONFIRM
- omogoča INSPECT / AUDIT
- NE omogoča samodejnega izvajanja

Mandat je dovoljenje, ne ukaz.

======================================================================

SECTION 1 — OSNOVNA DEFINICIJA

----------------------------------------------------------------------
Mandat je strukturiran, determinističen objekt, ki:

- nastane izključno v stanju MANDATE_DRAFT
- postane veljaven šele v stanju MANDATE_CONFIRM
- je edini dovoljeni vhod v EXECUTION (FAZA III)

Brez mandata:
- ni izvajanja
- ni routinga
- ni realnih učinkov

======================================================================

SECTION 2 — KANONIČNA STRUKTURA (MINIMALNI OBVEZNI KLJUČI)

----------------------------------------------------------------------
```json
{
  "id": "uuid",

  "intent": "string",
  "action": "string",

  "scope": {
    "resource": "string",
    "context": "string"
  },

  "constraints": {
    "allowed": [],
    "forbidden": []
  },

  "limits": {
    "max_amount": null,
    "max_count": null,
    "time_window": null
  },

  "created_at": "ISO-8601 timestamp",
  "expires_at": "ISO-8601 timestamp",

  "confirmed": false,
  "revoked": false
}
```
======================================================================

SECTION 3 — SEMANTIKA POSAMEZNIH POLJ

ID

Unikaten identifikator mandata

Generiran ob MANDATE_DRAFT

Nikoli se ne spreminja

INTENT

Človeški namen (npr. "trade", "inspect", "analyze")

Interpretiran v FAZI I

Ne predstavlja tehnične akcije

ACTION

Formalizirana akcija (npr. "BUY", "SELL", "READ_ONLY")

Uporabljena za routing

Brez ACTION → mandat ni veljaven

SCOPE
Definira, kje mandat velja.

resource: npr. "BTC/USDT", "SYSTEM_LOGS"

context: npr. "SPOT", "READ_ONLY"

Brez scope:

mandat je neveljaven

ROUTING_CHECK mora vrniti REFUSE

CONSTRAINTS
Absolutne meje delovanja.

allowed: eksplicitno dovoljeno

forbidden: eksplicitno prepovedano

Pravila:

konflikt allowed / forbidden → REFUSE

constraints imajo prednost pred vsemi drugimi pravili

LIMITS
Kvantitativne meje.

max_amount: maksimalna vrednost (npr. 1000)

max_count: maksimalno število dejanj

time_window: časovno okno (npr. "24h")

Pravila:

brez limits → NO EXECUTION

limits ne smejo biti implicitne

CREATED_AT

čas nastanka mandata

uporabljen za audit

EXPIRES_AT

po tem času mandat NI več veljaven

potekel mandat → REFUSE

CONFIRMED

false v MANDATE_DRAFT

lahko se spremeni v true SAMO v MANDATE_CONFIRM

brez confirmed = true → EXECUTION prepovedan

REVOKED

lahko ga nastavi:

uporabnik

governance

revoked = true → mandat takoj neveljaven

======================================================================

SECTION 4 — ŽIVLJENJSKI CIKEL MANDATA

scss
Kopiraj kodo
INTENT_RECEIVED
  → ADVISORY
  → USER_DECISION
  → ROUTING_CHECK
  → MANDATE_DRAFT   (confirmed = false)
  → MANDATE_CONFIRM (confirmed = true)
  → EXECUTION       (FAZA III)
Nobena druga pot ni dovoljena.

======================================================================

SECTION 5 — ROUTING_CHECK (CORE FAZE II)

ROUTING_CHECK mora preveriti:

Prisotnost vseh obveznih ključev

Veljavnost scope

Konflikte v constraints

Obstoj limits

Časovno veljavnost (expires_at)

revoked == false

Če katerikoli pogoj pade:

CLARIFY ali REFUSE

nikoli EXECUTION

======================================================================

SECTION 6 — NEGATIVNI TOKOVI

Situacija	Rezultat
Manjkajoč obvezen ključ	CLARIFY
Konflikt constraints	REFUSE
Potekel mandat	REFUSE
Ne-potrdjen mandat	NO ACTION
Revoked mandat	REFUSE

======================================================================

SECTION 7 — INSPECT / AUDIT PRIPRAVLJENOST (FAZA IV)

Mandat v1 omogoča pregled:

kdaj je bil ustvarjen

kakšen je njegov scope

kakšne omejitve ima

ali je bil potrjen

ali je bil preklican

Audit je read-only.
Mandat se nikoli ne spreminja retroaktivno.

======================================================================

SECTION 8 — ABSOLUTNI HARD NO

Strogo prepovedano:

implicitna potrditev mandata

avtomatsko podaljševanje mandata

sprememba mandata po potrditvi

execution brez limits

execution brez confirmed = true

execution po expires_at

======================================================================

SECTION 9 — DEFINITION OF DONE (FAZA II — MANDATE v1)

FAZA II (MANDATE v1) JE ZAKLJUČENA, KO:

 struktura mandata je natančno definirana

 ROUTING_CHECK uporablja to strukturo

 MANDATE_CONFIRM je edina točka potrditve

 neveljavni mandati nikoli ne pridejo do EXECUTION

 mandat je inspectable (FAZA IV ready)

Če katerikoli pogoj ni izpolnjen:
FAZA II NI ZAKLJUČENA.

======================================================================

SECTION 10 — KONČNI ZAKLEP

Ta dokument definira KANONIČNI MANDAT v1.

Implementacija se mora prilagoditi temu dokumentu

Dokument se ne prilagaja implementaciji

Razširitve so dovoljene izključno kot MANDATE v2

======================================================================

END OF DOCUMENT
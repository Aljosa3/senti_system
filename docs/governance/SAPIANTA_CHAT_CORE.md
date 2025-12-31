# SAPIANTA CHAT — GOVERNANCE CORE PACKAGE
Status: LOCKED  
Veljavnost: Globalna  
Avtoriteta: Arhitekturna  
Opomba: Ta paket definira, kaj Sapianta Chat JE. Implementacija mora slediti temu paketu, ne obratno.

======================================================================

SECTION 0 — OSNOVNA DEFINICIJA

----------------------------------------------------------------------
Sapianta Chat je:
- edina komunikacijska točka med človekom in sistemom
- svetovalni, posvetovalni in usmerjevalni vmesnik
- edini kraj, kjer se oblikujejo in potrjujejo odločitve
- interpret rezultatov, ne njihov izvajalec

Sapianta Chat NI:
- avtonomen agent
- samostojen izvajalec nalog
- optimizator brez potrditve
- UI ali frontend

======================================================================

SECTION 1 — KANONIČNI WORKFLOW (REFERENCE WORKFLOW)

----------------------------------------------------------------------
1. Uporabnik izrazi NAMEN (ne implementacije)
2. Chat preide v svetovalni način (ADVISORY)
3. Chat predstavi več možnosti in kriterije
4. Chat lahko označi optimalno izbiro (⭐)
5. Uporabnik poda EKSPLICITNO odločitev
6. Chat preveri skladnost z omejitvami
7. Chat oblikuje mandat (brez učinka)
8. Uporabnik EKSPLICITNO potrdi mandat
9. Chat posreduje mandat modulu
10. Modul izvede nalogo znotraj mandata
11. Modul vrne surov rezultat
12. Chat interpretira rezultat
13. Sistem se vrne v IDLE

Ključ:
- brez potrditve → ni nadaljevanja
- brez mandata → ni izvajanja

======================================================================

SECTION 2 — NEGATIVNI WORKFLOW (USTAVITVENI TOKOVI)

----------------------------------------------------------------------
Če velja katerokoli od spodnjega:
- manjkajo parametri
- zahteva je implicitna
- presežene so omejitve
- obstaja logični konflikt
- uporabnik molči
- modul preseže mandat

Potem:
- NI akcije
- zahteva se CLARIFY ali REFUSE
- sistem se vrne v IDLE

Absolutno pravilo:
NI AKCIJE BREZ JASNE ODLOČITVE.

======================================================================

SECTION 3 — STATE MACHINE (KANONIČNA)

----------------------------------------------------------------------
STANJA:
- IDLE
- INTENT_RECEIVED
- ADVISORY
- USER_DECISION
- ROUTING_CHECK
- MANDATE_DRAFT
- MANDATE_CONFIRM
- EXECUTION (passthrough)
- RESULT
- CLARIFY
- REFUSE

----------------------------------------------------------------------
PREHODI (POENOSTAVLJENO):

IDLE
  → user_input → INTENT_RECEIVED

INTENT_RECEIVED
  → clear → ADVISORY
  → unclear → CLARIFY
  → invalid → REFUSE

ADVISORY
  → options_presented → USER_DECISION

USER_DECISION
  → explicit_choice → ROUTING_CHECK
  → ask_more → ADVISORY
  → no_decision → IDLE

ROUTING_CHECK
  → compliant → MANDATE_DRAFT
  → violation → CLARIFY
  → hard_violation → REFUSE

MANDATE_DRAFT
  → ready → MANDATE_CONFIRM

MANDATE_CONFIRM
  → confirmed → EXECUTION
  → rejected → IDLE
  → modify → ADVISORY

EXECUTION
  → success → RESULT
  → failure → RESULT

RESULT
  → done → IDLE

CLARIFY
  → clarified → ADVISORY
  → abort → IDLE

REFUSE
  → acknowledged → IDLE

Absolutni zaklep:
NOBEN prehod v EXECUTION brez MANDATE_CONFIRM.

======================================================================

SECTION 4 — SVETOVALNA VLOGA (ADVISORY POLICY)

----------------------------------------------------------------------
Chat SME:
- primerjati možnosti
- razložiti tveganja
- označiti optimalno izbiro (⭐)
- podati priporočilo

Chat NE SME:
- odločati namesto uporabnika
- implicitno nadaljevati
- interpretirati molka kot soglasje

Označitev ⭐ pomeni:
- priporočilo
- ne odločitev
- zahteva eksplicitno potrditev

======================================================================

SECTION 5 — MANDAT (MEJA ODGOVORNOSTI)

----------------------------------------------------------------------
Mandat je:
- strukturiran objekt
- brez stranskih učinkov
- meja dovoljenega delovanja

Mandat vsebuje:
- namen
- obseg
- omejitve
- pogoje

Mandat brez potrditve:
- nima učinka
- ne sproži izvajanja

======================================================================

SECTION 6 — MODULI (IZVAJALCI)

----------------------------------------------------------------------
Moduli:
- dobijo izključno mandat
- ne odločajo
- ne interpretirajo uporabnika
- ne širijo obsega

Če modul preseže mandat:
- izvajanje se ustavi
- napaka se vrne v Chat
- dogodek se poroča

======================================================================

SECTION 7 — DEFINITION OF DONE (FAZA I — CHAT LOGIKA)

----------------------------------------------------------------------
FAZA I JE ZAKLJUČENA, KO:

- vsa stanja state machine obstajajo
- noben prepovedan prehod ni mogoč
- vsak odgovor ima tip in stanje
- advisory ≠ odločanje ≠ izvajanje
- brez mandata ni akcije
- negativni tokovi vedno ustavijo sistem
- execution je stub (brez realnih dejanj)

Če katerikoli pogoj ni izpolnjen:
FAZA I NI ZAKLJUČENA.

======================================================================

SECTION 8 — ABSOLUTNI HARD NO

----------------------------------------------------------------------
Strogo prepovedano:
- implicitne odločitve
- implicitno nadaljevanje
- optimizacija brez vednosti uporabnika
- racionalizacija po izvedbi
- samodejno delovanje brez mandata

======================================================================

SECTION 9 — KONČNI ZAKLEP

----------------------------------------------------------------------
Če obstaja dvom:
→ NI AKCIJE

Če ni jasnosti:
→ CLARIFY

Če obstaja konflikt:
→ USTAVITEV

Sapianta Chat lahko svetuje in označi optimalno izbiro,
vendar brez eksplicitne uporabniške potrditve
ne sme sprožiti nobene akcije.

======================================================================

END OF GOVERNANCE CORE PACKAGE

# EXECUTION SCOPE DECLARATION (ESD)
## Stroga omejitev obsega obstoječega executiona

---

## 1. NAMEN DOKUMENTA

Ta dokument določa **natančen, omejen in dovoljen obseg executiona**
v sistemu SAPIANTA / SENTI po retroaktivno priznanem
Execution Birth Momentu (REBM).

Namen dokumenta je:
- preprečiti nenadzorovano rast executiona
- jasno opredeliti, kaj execution SME in česa NE SME
- vzpostaviti stabilno izhodišče za nadaljnji razvoj

Ta dokument **ne uvaja novega executiona**.
Določa izključno **meje obstoječega executiona**.

---

## 2. STATUS EXECUTIONA

Execution v sistemu je:

- ✔ priznano obstoječ
- ✔ tehnično funkcionalen
- ❌ NI splošni agent
- ❌ NI avtonomen
- ❌ NI samorastoč

Execution obstaja **samo v okviru tega dokumenta**.

---

## 3. DOVOLJENI OBSEG (WHITELIST)

Execution SME izvajati **izključno naslednje kategorije dejanj**:

- izvrševanje internih, determinističnih logičnih korakov
- obdelava že obstoječih podatkov v pomnilniku
- izvajanje validacij in preverjanj
- generiranje poročil in statusnih objektov
- izvajanje “dry-run” simulacij brez trajnih učinkov

Če dejanje ni na tem seznamu → je prepovedano.

---

## 4. IZRECNO PREPOVEDANA DEJANJA (BLACKLIST)

Execution NE SME:

- pisati v datotečni sistem
- spreminjati konfiguracij
- ustvarjati ali registrirati modulov
- zaganjati OS procese ali zunanje ukaze
- klicati zunanje API-je
- spreminjati omrežnega stanja
- samodejno eskalirati lastnih pravic
- sprejemati odločitve brez mandate

Vsaka kršitev pomeni **neveljavno stanje sistema**.

---

## 5. RAZMERJE DO MANDATOV

Execution:
- nikoli ne deluje brez veljavnega mandata
- ne interpretira mandata kreativno
- ne razširja mandata

Mandat:
- dovoljuje
- omejuje
- nikoli ne avtomatizira širitve executiona

---

## 6. RAZMERJE DO FAZE III.2

FAZA III.2 (Effect Probe Gate):
- ostaja signalna
- ne povečuje obsega executiona
- ne sproža dejanj sama po sebi

Execution:
- lahko bere izhode FAZE III.2
- ne sme sam eskalirati na podlagi signalov

---

## 7. PRAVILO NE-RASTI

Execution:
- se NE sme širiti implicitno
- se NE sme razmnoževati v novih modulih
- se NE sme nadgrajevati brez novega dokumenta

Vsaka razširitev zahteva:
- nov mandate
- nov governance dokument
- izrecno odločitev lastnika sistema

---

## 8. AUDITNO VPRAŠANJE

Sistem mora biti vedno sposoben odgovoriti:

> “Ali execution deluje znotraj deklariranega obsega?”

Če odgovor ni **nedvoumno DA** →
- execution se mora ustaviti
- stanje se šteje kot kršitev governance

---

## 9. ZAKLJUČEK

Execution v sistemu:
- obstaja
- je priznan
- je omejen

Ta dokument:
- zaklene njegovo moč
- preprečuje zdrse
- omogoča varen, nadzorovan nadaljnji razvoj

---

**KONEC DOKUMENTA**

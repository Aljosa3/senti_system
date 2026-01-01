# INSPECT COMMAND SPEC (ICS)
## Minimalna uporabniška dostopnost FAZE IV

---

## 1. NAMEN DOKUMENTA

Ta dokument definira **minimalno in zadostno specifikacijo**
uporabniškega ukaza `chat inspect`, s katerim se FAZA IV (Inspect)
šteje kot **zaključena**.

Dokument ne uvaja novih funkcionalnosti.
Določa izključno **dostopnost obstoječega inspect modula**.

---

## 2. IME UKAZA

chat inspect

Ukaz je:
- globalen
- vedno na voljo
- ne zahteva mandata
- ne zahteva potrditve

---

## 3. NAMEN UKAZA

Ukaz `chat inspect` omogoča uporabniku:
- vpogled v trenutno stanje sistema
- brez sprožitve executiona
- brez sprememb sistema
- brez stranskih učinkov

Ukaz predstavlja **read-only zavest sistema o samem sebi**.

---

## 4. VHOD

- brez parametrov
- brez flagov
- brez argumentov

Vsaka razširitev vhoda zahteva nov dokument.

---

## 5. IZVEDBA (NORMATIVNO)

Ukaz `chat inspect`:

- kliče funkcijo:
inspect_full(machine)

- iz modula:
modules.sapianta_chat_inspect

Med izvajanjem:
- execution se NE aktivira
- mandate se NE ustvarja
- stanje sistema se NE spremeni

---

## 6. IZHOD

Ukaz vrne:
- strukturiran povzetek stanja sistema
- v naravnem jeziku ali JSON obliki (implementacijska odločitev)
- brez skritih dejanj

Če inspect ne uspe:
- vrne se razlaga napake
- brez fallback executiona

---

## 7. VARNOSTNA PRAVILA

`chat inspect`:
- je strogo read-only
- ne sme pisati na disk
- ne sme spreminjati spomina
- ne sme klicati zunanjih sistemov

Vsaka kršitev pomeni:
- FAZA IV FAIL
- takojšnjo ustavitev razvoja

---

## 8. STATUS FAZE IV

FAZA IV se šteje kot **ZAKLJUČENA**, ko:

- `chat inspect` obstaja
- ukaz je dostopen uporabniku
- ukaz kliče inspect modul
- brez executiona
- brez mandata

Do takrat je FAZA IV **PARTIAL**.

---

## 9. ZAKLJUČEK

Inspect brez uporabniškega dostopa
ni inspect.

Ta dokument zagotavlja,
da ima sistem zavestno zavoro.

---

**KONEC DOKUMENTA**
# IMPLEMENTATION READINESS CHECK

## 1. Namen dokumenta

Ta dokument določa **pogoje pripravljenosti** za začetek implementacije sistema **Sapianta Chat**.

Namen dokumenta je:
- potrditi, da so vse konceptualne in arhitekturne odločitve zaključene,
- preprečiti prehiter ali nepravilen začetek implementacije,
- zagotoviti, da implementacija ne bo kršila zaklepnih in mandatnih aktov.

Dokument:
- ne vsebuje kode,
- ne določa tehnologij,
- in ne predstavlja začetka implementacije.

---

## 2. Obvezni predpogoji (checklist)

Implementacija Sapianta Chata se lahko začne **samo, če so izpolnjeni vsi naslednji pogoji**:

### 2.1 Governance zaklepi
- [x] Zaklepna izjava (NO-GO)
- [x] Izjava o ne-orchestraciji
- [x] Mandat Sapianta Chata
- [x] Pozitivna vloga Sapianta Chata

### 2.2 Model pomena in meje
- [x] INTENT HANDOFF MODEL
- [x] EXECUTION INTERFACE CONSTRAINTS
- [x] CHAT ↔ EXECUTION BOUNDARY

### 2.3 Arhitekturna priprava
- [x] SAPIANTA_CHAT_ARCHITECTURE_OVERVIEW
- [x] SAPIANTA_CHAT_INTERNAL_MODULES

Če kateri koli element manjka ali je nejasen, se implementacija **ne sme začeti**.

---

## 3. Dovoljeni obseg implementacije

Po potrditvi tega dokumenta je dovoljeno:

- implementirati **izključno** notranje module Sapianta Chata,
- implementirati **enosmerni tok** od vnosa do intenta,
- implementirati **normativni filter** skladno z akti.

Ni dovoljeno:
- implementirati execution sloja,
- implementirati povratnih zank,
- uvajati orkestracijo ali nadzor.

---

## 4. Prva implementacijska enota

Prva dovoljena implementacijska enota je:

> **Sapianta Chat (internal processing pipeline)**

Brez:
- povezave na execution,
- avtomatskega sprožanja dejanj,
- implicitnih “side-effectov”.

---

## 5. Merila skladnosti med implementacijo

Vsaka implementacijska odločitev mora biti preverljiva glede na:

- Mandat Sapianta Chata,
- Pozitivno vlogo Sapianta Chata,
- INTENT HANDOFF MODEL,
- CHAT ↔ EXECUTION BOUNDARY.

Če implementacija zahteva kršitev katerega koli dokumenta, se **implementacija ustavi**.

---

## 6. Formalna odobritev prehoda

S tem dokumentom je potrjeno, da:

- je arhitektura zaključena,
- so meje jasno določene,
- in da je sistem **pripravljen na implementacijo**.

Ta dokument predstavlja **formalno dovoljenje za prehod v FAZO XIII (IMPLEMENTACIJA)**.

---

## 7. Zaklepna določba

Ta dokument:
- ne sproži implementacije samodejno,
- ne nadomešča nadzora,
- in ne dovoljuje obhoda governance aktov.

Z njim je **prehod v implementacijo formalno, a nadzorovano omogočen**.

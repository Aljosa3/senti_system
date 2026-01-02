# SAPIANTA CHAT — INTERNAL MODULES

## 1. Namen dokumenta

Ta dokument opisuje **notranje logične module Sapianta Chata**, njihove odgovornosti in medsebojna razmerja.

Namen je:
- razjasniti, kako je Chat strukturiran znotraj svoje domene,
- preprečiti zlivanje odgovornosti,
- omogočiti kasnejšo implementacijo brez konceptualnih nejasnosti.

Dokument:
- ne opisuje kode,
- ne določa tehnologij,
- ne uvaja izvedbenih odločitev.

---

## 2. Načela modularizacije

Notranji moduli Sapianta Chata sledijo načelom:

- **ena odgovornost na modul**,
- **enosmeren tok informacij**,
- **brez skritih povratnih zank**,
- **jasen zaključek odgovornosti**.

Vsak modul deluje izključno znotraj domene Sapianta Chata.

---

## 3. Pregled notranjih modulov

Sapianta Chat je sestavljen iz naslednjih logičnih modulov:

1. Input Handler  
2. Intent Interpreter  
3. Clarification Engine  
4. Normative Checker  
5. Semantic Normalizer  
6. Intent Builder  
7. Response Composer  

---

## 4. Opis modulov

### 4.1 Input Handler

- sprejema surov uporabniški vnos,
- ne interpretira pomena,
- skrbi za prenos vnosa v nadaljnje module.

Njegova naloga je **zajem**, ne razumevanje.

---

### 4.2 Intent Interpreter

- izdela prvo interpretacijo uporabnikovega namena,
- zazna osnovni cilj zahteve,
- ne sprejema dokončnih zaključkov.

Deluje kot **prvi semantični prehod**.

---

### 4.3 Clarification Engine

- zaznava nejasnosti, manjkajoče podatke ali protislovja,
- oblikuje pojasnjevalna vprašanja,
- omogoča razjasnitev namena pred nadaljevanjem.

Ta modul preprečuje prezgodnje zaključke.

---

### 4.4 Normative Checker

- preverja zahteve glede na:
  - Zaklepno izjavo (NO-GO),
  - Izjavo o ne-orchestraciji,
  - Mandat Sapianta Chata,
  - ostale governance akte.
- ima pravico do zavrnitve ali omejitve zahteve.

Normative Checker ima **veto funkcijo**.

---

### 4.5 Semantic Normalizer

- poenoti izraze in pojme,
- odpravi implicitne predpostavke,
- pripravi pomen za deklarativno oblikovanje.

Ne dodaja novih ciljev ali odločitev.

---

### 4.6 Intent Builder

- oblikuje **končni deklarativni intent**,
- združi razjasnjen in normativno preverjen pomen,
- zaključi Chatovo odgovornost.

Intent Builder ne ustvarja nalog ali ukazov.

---

### 4.7 Response Composer

- oblikuje uporabniški odgovor,
- jasno označi mejo odgovornosti,
- ne obljublja izvedbe ali rezultatov.

Njegova naloga je **komunikacija**, ne delovanje.

---

## 5. Medsebojni odnosi modulov

Moduli so povezani **linearly**:

Input Handler  
→ Intent Interpreter  
→ Clarification Engine (po potrebi)  
→ Normative Checker  
→ Semantic Normalizer  
→ Intent Builder  
→ Response Composer  

Ni dovoljenih:
- povratnih zank iz execution sloja,
- preskokov normativne presoje,
- samostojnega odločanja posameznega modula.

---

## 6. Meje notranje arhitekture

Notranji moduli:
- nimajo dostopa do execution sloja,
- ne sprožajo dejanj,
- ne prejmejo povratnih informacij iz izvedbe.

Vsak modul zaključi svojo odgovornost znotraj Chata.

---

## 7. Razmerje do drugih dokumentov

Ta dokument temelji na:
- SAPIANTA_CHAT_ARCHITECTURE_OVERVIEW.md,
- Mandatu Sapianta Chata,
- INTENT_HANDOFF_MODEL.md.

V primeru konflikta imajo **višji governance akti prednost**.

---

## 8. Zaklepna določba

Ta dokument:
- ne določa implementacije,
- ne razširja vloge Sapianta Chata,
- in ne odpira poti v orkestracijo.

Z njim je **notranja struktura Sapianta Chata jasno opredeljena**.

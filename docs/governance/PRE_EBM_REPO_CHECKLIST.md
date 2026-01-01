# PRE-EBM REPO CHECKLIST
## Sanity Check pred Execution Birth Moment (EBM)

---

## 1. NAMEN DOKUMENTA

Ta dokument je **obvezna kontrolna lista** za preverjanje,
ali repozitorij SAPIANTA / SENTI **še vedno spoštuje PRE-EBM stanje**,
v katerem execution **ne obstaja**.

Checklisto je treba izvesti:
- pred implementacijo FAZE III.2
- pred vsako razširitvijo mandatov
- pred razpravo o EBM
- ob vsakem večjem refaktorju

Če katerakoli točka FAIL-a → sistem **NI pripravljen** na EBM.

---

## 2. STATUSI OCENE

Vsaka točka mora imeti enega izmed statusov:

- ✔ PASS — skladno s PRE-EBM
- ⚠ WARNING — potencialni zdrs, zahteva presojo
- ❌ FAIL — kršitev PRE-EBM, takojšnja ustavitev

---

## 3. STRUKTURNA PREVERJANJA (OBVEZNO)

### 3.1 Neobstoj execution kode
- [ ] V repozitoriju **ne obstaja** datoteka z imenom:
  - `execution.py`
  - `executor.py`
  - `runner.py`
- [ ] Ne obstaja mapa:
  - `/execution/`
  - `/executor/`

Status: ___

---

### 3.2 Neobstoj izvršilnih razredov
- [ ] Ni razredov z imeni:
  - `Execution`
  - `Executor`
  - `Runner`
  - `Applier`

Status: ___

---

### 3.3 Neobstoj izvršilnih metod
- [ ] V kodi **ni metod** z imeni:
  - `execute`
  - `apply`
  - `run`
  - `commit`
  - `write`
  - `spawn`
  - `dispatch`

Status: ___

---

## 4. SEMANTIČNA PREVERJANJA (KRITIČNO)

### 4.1 Jezikovna ograja
- [ ] V kodi, komentarjih in dokumentaciji **ni uporabljenih izrazov**:
  - execution
  - executor
  - apply
  - commit
  - run

- [ ] Uporabljeni so samo dovoljeni izrazi:
  - probe
  - signal
  - requirement
  - declaration
  - simulation

Status: ___

---

### 4.2 Poimenovanje FAZE III.2
- [ ] FAZA III.2 je poimenovana kot:
  - Effect Probe Gate
  - ali Capability Signal Layer
- [ ] Nikjer ni opisana kot:
  - “mini execution”
  - “varen execution”
  - “omejena izvršitev”

Status: ___

---

## 5. FUNKCIONALNA PREVERJANJA

### 5.1 No Side Effects Test
Za vsako funkcijo v FAZI III.2 velja:
- [ ] Če se funkcija pokliče 100×, se **stanje sistema ne spremeni**
- [ ] Ni pisanja na disk
- [ ] Ni sprememb konfiguracije
- [ ] Ni ustvarjanja novih objektov z življenjskim ciklom

Status: ___

---

### 5.2 Signal-only izhodi
- [ ] FAZA III.2 vrača izključno:
  - booleane
  - strukture z oznako `required`, `would_be`, `needed`
- [ ] Ne vrača:
  - ukazov
  - callable objektov
  - poti do izvedbe

Status: ___

---

## 6. MANDATE & INTENT PREVERJANJA

### 6.1 Mandate brez delovanja
- [ ] Mandati:
  - opisujejo
  - dovoljujejo
  - omejujejo
- [ ] Mandati **ne kličejo** nobenih funkcij z učinkom

Status: ___

---

### 6.2 Intent ≠ Action
- [ ] Intent je zapisan kot podatek
- [ ] Intent **nikoli** ne sproži akcije
- [ ] Prehod iz intenta v delovanje je **nemogoč brez EBM**

Status: ___

---

## 7. AUDIT PREVERJANJA

### 7.1 Odgovor na ključno vprašanje
Sistem mora jasno odgovoriti:

> “Ali je bil Execution Birth Moment že izveden?”

- [ ] Odgovor je **NE**
- [ ] Obstaja jasen razlog, zakaj execution ne obstaja

Status: ___

---

## 8. FAIL FAST PRAVILO

Če katerakoli točka dobi status:
- ❌ FAIL

Potem:
- razvoj se **takoj ustavi**
- execution se **ne sme implementirati**
- najprej se popravi kršitev
- checklisto se izvede znova

---

## 9. ZAKLJUČNA OCENA

Skupni status repozitorija (obkroži):

- 🟢 SAFE (vse PASS)
- 🟡 WARNING (vsaj en WARNING, brez FAIL)
- 🔴 BLOCKED (vsaj en FAIL)

Podpis (ime / datum):

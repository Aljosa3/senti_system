# MANDATE AUDIT & LOGGING MODEL
## Passive Traceability of Continuous Execution

---

## 1. Namen dokumenta

Ta dokument definira **audit in logging model** za mandatno izvajanje
v sistemu Sapianta.

Njegov namen je zagotoviti:
- sledljivost podeljenih mandatov,
- dokaz pravilnega izvajanja,
- forenzično rekonstrukcijo dogodkov,
- dolgoročno odgovornost,

brez poseganja v odločanje, avtorizacijo ali izvajanje.

---

## 2. Temeljno načelo

> **Audit ne odloča.  
> Audit ne preprečuje.  
> Audit ne izvršuje.  
> Audit samo beleži.**

Audit je **pasiven, post-factum, read-only sloj**.

---

## 3. Kaj se beleži

### 3.1 Mandati

Za vsak mandat se beleži:
- identifikator mandata,
- čas podelitve,
- obseg (scope),
- parametri (razponi, omejitve),
- veljavnost,
- vir odločitve (human).

---

### 3.2 Življenjski cikel mandata

Beležijo se dogodki:
- mandat ustvarjen,
- mandat avtoriziran,
- izvajanje začeto,
- izvajanje ustavljeno,
- potek (expiry),
- preklic (revocation),
- emergency stop.

Vsak dogodek ima:
- časovni žig,
- tip dogodka,
- referenco na mandat.

---

### 3.3 Izvajanje (agregirano)

Audit beleži **agregirane podatke**, npr.:
- število izvedenih akcij,
- trajanje izvajanja,
- dosežene meje (npr. kvote).

Audit **ne beleži**:
- posameznih odločitev strategije,
- real-time signalov,
- notranje logike modulov.

---

## 4. Kaj audit NAMERNO ne počne

Audit / Logging NE SME:
- vplivati na izvajanje,
- blokirati akcij,
- sprožati STOP,
- interpretirati governance pravil,
- sodelovati v real-time logiki,
- postati del Sapianta Chata.

Vsaka od teh funkcij predstavlja **arhitekturno kršitev**.

---

## 5. Odgovornosti po slojih

| Sloj | Vloga |
|----|-----|
| Execution Layer | Oddaja audit dogodke |
| Mandate Resolver | Oddaja lifecycle dogodke |
| Audit Store | Hrani zapise |
| Sapianta Chat | Read-only vpogled (če dovoljen) |

Sapianta Chat:
- ne piše audit zapisov,
- jih ne interpretira,
- jih ne uporablja za odločanje.

---

## 6. Primeri

### 6.1 Trading mandat

Audit zabeleži:
- mandat podeljen ob T0,
- izvajanje začeto ob T1,
- izvedenih 127 poslov,
- emergency stop ob T2 (koda: DD_LIMIT).

Audit **ne zabeleži**:
- posameznih vstopov,
- signalov,
- razlogov strategije.

---

### 6.2 Izgradnja modula

Audit zabeleži:
- mandat podeljen,
- build proces začet,
- build uspešno zaključen.

---

## 7. Razmerje do ostalih modelov

Ta dokument:
- dopolnjuje `MANDATE_MODEL.md`,
- dopolnjuje `MANDATE_REVOCATION_EXPIRY_MODEL.md`,
- ne spreminja B14,
- ne dodaja izvršilnosti ali agentnosti.

Audit je **opazovalni sloj**, ne operativni.

---

## 8. Zaključna izjava

> **Kar ni zabeleženo, ni dokazano.  
> Kar je zabeleženo, ni več vprašanje.  
> Audit daje mir pri avtomatizaciji.**

---

## STATUS

**MANDATE AUDIT & LOGGING MODEL — ESTABLISHED**

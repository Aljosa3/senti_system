# MANDATE VISIBILITY & READ MODEL
## Human Read-Only Insight into Mandated Execution

---

## 1. Namen dokumenta

Ta dokument definira **kaj, kako in v kakšni obliki** lahko človek vidi
informacije o mandatih in njihovem izvajanju v sistemu Sapianta.

Cilj je:
- zagotoviti preglednost,
- omogočiti nadzor in razumevanje,
- ohraniti varnostne in arhitekturne zaklepe (B14),
- preprečiti implicitno odločanje ali agentnost chata.

---

## 2. Temeljno načelo

> **Vidnost ni nadzor.  
> Branje ni upravljanje.  
> Pregled ne pomeni vpliva.**

Vsi podatki v tem modelu so **read-only**.

---

## 3. Kaj je VIDNO uporabniku

### 3.1 Mandati (statični podatki)

Uporabnik lahko vidi:
- identifikator mandata,
- ime / tip modula,
- obseg (scope),
- ključne parametre (razponi, omejitve),
- čas podelitve,
- stanje (aktiven / potekel / preklican),
- čas veljavnosti.

Uporabnik **ne vidi**:
- notranjih validacij,
- governance preverjanj,
- razlogov za odobritev ali zavrnitev.

---

### 3.2 Stanje izvajanja (dinamični podatki)

Vidni so:
- ali je mandat aktiven,
- ali je izvajanje v teku,
- ali je izvajanje ustavljeno,
- agregirani kazalniki (npr. število akcij).

Nevidni so:
- real-time signali,
- posamezna dejanja v živo,
- notranja logika modulov.

---

### 3.3 Življenjski dogodki (audit view)

Uporabnik lahko vidi:
- čas začetka izvajanja,
- čas ustavitve,
- tip ustavitve (expiry / revocation / emergency),
- kodo dogodka (brez razlage).

Uporabnik **ne vidi**:
- notranjih razlogov,
- varnostnih mehanizmov,
- interpretacij pravil.

---

## 4. Kaj uporabnik NAMERNO ne vidi

Uporabnik nikoli ne vidi:
- ADS / AIS / AEA / AIA / ARA slojev,
- STOP-triggerjev,
- notranjih governance pravil,
- faz sistema,
- notranjih odločitev strategij,
- signalov ali heuristik.

Vsako razkritje teh elementov je **varnostna kršitev**.

---

## 5. Način dostopa (kako)

### 5.1 Read-only kanali

Vidnost je omogočena prek:
- read-only ukazov,
- read-only pogledov,
- statičnih povzetkov.

Ni omogočeno:
- pisanje,
- spreminjanje,
- potrjevanje,
- vplivanje na izvajanje.

---

### 5.2 Vloga Sapianta Chata

Sapianta Chat:
- lahko **prikaže** vidne podatke,
- lahko **povzame** stanje,
- ne interpretira,
- ne priporoča,
- ne odloča,
- ne sproža dejanj.

Chat deluje kot **prikazni vmesnik**, ne kot kontrolni center.

---

## 6. Prepovedi (kanonične)

Prepovedano je:
- združevanje vidnosti in kontrole,
- implicitno omogočanje vpliva prek branja,
- dodajanje “akcijskih” elementov v read view,
- razlaganje varnostnih ali governance razlogov.

Vidnost **nikoli ne sproži spremembe stanja**.

---

## 7. Primeri

### 7.1 Trading mandat

Uporabnik vidi:
- mandat aktiven,
- BTC / tveganje 1–3 %,
- 127 izvedenih poslov,
- stanje: ustavljen (EMERGENCY_STOP),
- čas ustavitve.

Uporabnik **ne vidi**:
- posameznih poslov,
- strategije,
- razlogov za stop (razen kode).

---

### 7.2 Izgradnja modula

Uporabnik vidi:
- mandat podeljen,
- build v teku,
- build zaključen.

Uporabnik **ne vidi**:
- vmesnih korakov,
- datotečne strukture,
- orodij v ozadju.

---

## 8. Razmerje do drugih modelov

Ta dokument:
- dopolnjuje `MANDATE_MODEL.md`,
- dopolnjuje `MANDATE_REVOCATION_EXPIRY_MODEL.md`,
- dopolnjuje `MANDATE_AUDIT_LOGGING_MODEL.md`,
- ne spreminja B14,
- ne dodaja izvršilnosti ali agentnosti.

---

## 9. Zaključna izjava

> **Človek ima pregled.  
> Sistem ima izvajanje.  
> Chat ima prikaz.  
> Odgovornost ostaja človeška.**

---

## STATUS

**MANDATE VISIBILITY & READ MODEL — ESTABLISHED**

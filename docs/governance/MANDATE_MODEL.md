# MANDATE MODEL
## One-Time Decision → Continuous Execution

---

## 1. Namen dokumenta

Ta dokument definira **mandatni model izvajanja** v sistemu Sapianta.

Njegov namen je jasno razmejiti:
- človeško odločitev,
- avtorizacijo mandata,
- kontinuirano izvajanje,

in s tem omogočiti **avtonomno delovanje modulov** brez kršitve
varnostnih in arhitekturnih zaklepov, definiranih v B14.

---

## 2. Temeljno načelo

> **Človek odloča enkrat.  
> Sistem izvaja kontinuirano.  
> Sapianta Chat nikoli ne izvršuje.**

To načelo je neizpodbitno.

---

## 3. Definicija mandata

### 3.1 Kaj je mandat

**Mandat** je:
- formalna, časovno veljavna avtorizacija,
- podeljena z **eno eksplicitno človeško odločitvijo**,
- ki omogoča **samostojno izvajanje dejanj** znotraj jasno določenih meja.

Mandat:
- ni posamezno dejanje,
- ni pogovorna potrditev,
- ni implicitno dovoljenje,
- ni trajna pravica.

---

### 3.2 Kaj mandat NI

Mandat NI:
- agentska avtonomija,
- prenos odgovornosti na Chat,
- dovoljenje za spremembo ciljev,
- dovoljenje za širitev obsega,
- dovoljenje za reinterpretacijo pravil ali governance.

---

## 4. Mandatni tok (kanonični)

### 4.1 Faza A — Razmislek (Chat, advisory)

Sapianta Chat:
- pojasni možnosti,
- razčleni tveganja,
- predstavi razpone in omejitve,
- ne priporoča »najboljše« izbire.

V tej fazi **ne obstaja odločitev**.

---

### 4.2 Faza B — Odločitev (Human)

Uporabnik eksplicitno potrdi:
- obseg (scope),
- dovoljene akcije,
- razpone (od–do),
- trajanje mandata,
- pogoje ustavitve.

Primer:
> »Dovoljujem, da trading modul samostojno trguje BTC  
> v razponu 1–3 % tveganja na posel  
> do preklica ali kršitve pogojev.«

To je **edina odločitev**.

---

### 4.3 Faza C — Avtorizacija (Activation Module)

Activation Module (AM):
- preveri formalnost mandata,
- preveri skladnost z governance,
- preveri, ali mandat krši LOCKED anti-sloje,
- mandat odobri ali zavrne.

Sapianta Chat:
- ne sodeluje,
- ne interpretira,
- ne odloča.

---

### 4.4 Faza D — Evidenca (Mandate Resolver)

Mandate Resolver (MR):
- zabeleži mandat,
- določi veljavnost in prioriteto,
- spremlja skladnost izvajanja.

MR:
- ne izvaja dejanj,
- ne spreminja mandata.

---

### 4.5 Faza E — Izvajanje (Execution Layer)

Izvajalni modul:
- deluje samostojno,
- izvaja dejanja brez dodatnih potrditev,
- dokler:
  - ostaja znotraj mandata,
  - mandat ni preklican,
  - niso sproženi stop pogoji.

To je **kontinuirano izvajanje**.

---

## 5. Ključna ločitev odgovornosti

| Element | Odgovornost |
|------|------------|
| Odločitev | Človek |
| Mandat | Sistem (AM + MR) |
| Izvajanje | Modul |
| Vmesnik | Sapianta Chat |

---

## 6. Primeri

### 6.1 Trading modul

- Ena odločitev:
  - instrument,
  - tveganje,
  - razpon,
  - trajanje.
- Več sto naročil:
  - brez dodatnih potrditev,
  - znotraj mandata.

To je pravilno delovanje.

---

### 6.2 Izgradnja modula

- Ena odločitev:
  - »Zgradi modul po tem predlogu«.
- Celotna gradnja:
  - struktura,
  - datoteke,
  - povezave.

To je pravilno delovanje.

---

## 7. Prepovedi

Mandat NE SME:
- razširiti obsega samodejno,
- spremeniti ciljev,
- eskalirati privilegije,
- postati trajen brez revizije.

Sapianta Chat NE SME:
- ustvarjati mandatov sam,
- implicitno potrjevati mandat,
- izvajati mandat,
- razlagati notranje meje mandata.

---

## 8. Razmerje do B14

Ta dokument:
- ne odpira B14,
- ne rahlja varnostnih zaklepov,
- eksplicitno omogoča izvrševanje **prek mandata**.

> **B14 prepoveduje izvrševanje chata,  
> ne pa izvrševanja sistema.**

---

## 9. Zaključna izjava

> **Sapianta Chat je mesto razmisleka.  
> Mandat je nosilec dovoljenja.  
> Izvajanje je kontinuirano in avtomatizirano.  
> Odgovornost ostaja človeška.**

---

## STATUS

**MANDATE MODEL — ESTABLISHED**

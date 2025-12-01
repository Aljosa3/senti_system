# SENTI GLOBAL DATA RULES
## OS-Level Data Integrity Policy (Level 0 Protection)

### Temeljno pravilo Senti OS:

**Vsi moduli, sistemi, simulacije, procesi in AI-komponente morajo uporabljati izključno realne podatke iz realnih, preverljivih virov. Umetni, sintetični, dopolnjeni, interpolirani ali “verjetni” podatki so najstrožje prepovedani v kateremkoli delu operacijskega sistema.**

---

## 1. Obseg

Ta politika se uporablja za:

- simulacije,
- realno produkcijsko okolje,
- razvojno okolje,
- testno okolje,
- sandbox okolje,
- vse Senti modules (Trading, HR, Finance, CRM, ERP, IoT, Analytics …),
- AI agentne komponente,
- Senti Core AI Reasoning,
- System Services,
- Data Pipelines,
- ETL procese.

---

## 2. Temeljna pravila

### 2.1 REALNI VHODNI PODATKI – OBVEZNO
• Vhodni podatki morajo prihajati iz realnih, preverjenih virov:  
API, baza, datoteka, uradna arhiva, senzor, zunanji sistem.

• AI ne sme generirati, popraviti ali izmišljati vhodnih podatkov.

---

### 2.2 SIMULACIJE UPORABLJAJO IZKLJUČNO REALNE PODATKE
• Simulacije morajo uporabljati iste podatke kot realno okolje.  
• Simulacija NE sme teči, če realni podatki niso zagotovljeni.  
• Syntetični ali nadomestni podatki so prepovedani.

---

### 2.3 AI NE SME NADOMEŠČATI PODATKOV
• AI ne sme:
  - zapolniti vrzeli,
  - interpolirati,
  - ustvarjati manjkajočih vrednosti,
  - predvidevati preteklosti,
  - generirati “likely values”.

---

### 2.4 Uporabnik mora zagotoviti realne podatke
Če podatki manjkajo:
→ sistem mora uporabnika pozvati:  
**“Prosimo, zagotovite realne podatke.”**

Bez realnih podatkov sistem NE SME nadaljevati.

---

### 2.5 Absolutna prepoved izmišljanja podatkov
Kršitev tega pravila je označena kot:

**DATA_INTEGRITY_VIOLATION (CRITICAL)**

To sproži:
- Watchdog
- AI Recovery Agent
- System Security Layer
- Logging
- Prekinitev procesa

---

### 2.6 Prepoved sintetičnih podatkov v varnih sistemih
Vključuje:
- Trading podatke
- Računovodske evidence
- Plačilne podatke
- Osebne podatke (HR)
- Prodajne evidence
- Inventar
- CRM
- IoT
- Finance
- ERP

---

### 2.7 Dovoljena uporaba sintetičnih podatkov
**Samo** v eksplicitnem načinu:

simulation_mode: "synthetic_allowed"


Ta način NI dovoljen v:
✔ Trading  
✔ Finance  
✔ HR  
✔ Računovodstvo  
✔ Real-time sistemi  
✔ Legal sistemi  

Uporaba synthetic podatkov je dovoljena samo v izoliranih, nepovezanih laboratorijskih projektih.

---

## 3. Enforcement

Pravila se izvršujejo s:

- Data Integrity Engine (OS-level)
- Pre-flight data validation
- Source verifikacijo
- AI izvršitvenimi filtri
- SystemEvents (DATA_INTEGRITY_VIOLATION)
- Watchdog opozorili
- Senti OS Security Layer

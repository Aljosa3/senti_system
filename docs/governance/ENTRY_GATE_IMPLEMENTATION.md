# ENTRY GATE — IMPLEMENTATION
## Authorized Start of System Construction

---

## 1. Namen dokumenta

Ta dokument predstavlja **formalni ENTRY-GATE** za začetek implementacije
sistema Sapianta po zaključenih in zaklenjenih arhitekturnih fazah.

Njegov namen je:
- potrditi, da so temeljne meje določene,
- preprečiti napačno ali prehitevano implementacijo,
- zamrzniti interpretacije pred začetkom gradnje,
- omogočiti razvoj **znotraj jasno dovoljenega obsega**.

---

## 2. Predpogoji (MUST BE TRUE)

Implementacija se sme začeti **le, če so izpolnjeni vsi naslednji pogoji**:

- B14 — Advisory Contract & Two-Layer Model je **CLOSED**
- LOCKED anti-sloji (ADS, AIS, AIA, AEA, ARA) so **NEINTEGRIRANI**
- SECURITY CHECK T-LL-01 je **PASS**
- MANDATE STACK v1.0 je **LOCKED**
- Vsi mandatni dokumenti so **kanonični in zavezujoči**

Če kateri koli pogoj ni izpolnjen, je implementacija **nedovoljena**.

---

## 3. Dovoljen obseg implementacije (ALLOWED)

Z ENTRY-GATE je dovoljeno začeti implementirati **izključno** naslednje:

### 3.1 Sapianta Chat (advisory-only)
- tekstovni, read-only komunikacijski vmesnik,
- brez izvrševanja,
- brez interpretacije governance,
- brez implicitnih potrditev,
- brez agentnosti.

### 3.2 Mandate-aware sistemske komponente
- Activation Module (AM),
- Mandate Resolver (MR),
- Execution Layer (zunaj chata),
- Audit / Logging infrastruktura (pasivna).

### 3.3 Moduli znotraj mandata
- npr. trading modul,
- build / generator modul,
- drugi izvajalni moduli,
- **le v okviru podeljenih mandatov**.

---

## 4. Prepovedan obseg (FORBIDDEN)

ENTRY-GATE **izrecno prepoveduje** implementacijo:

- chata, ki kliče execution ali build,
- UI z gumbi start / stop / pause / tune,
- real-time nadzornih plošč,
- implicitnega ustvarjanja ali spreminjanja mandatov,
- “začasnih” bypass rešitev,
- razlag varnostnih ali governance razlogov uporabniku,
- katerekoli agentne logike v UI ali chatu.

Vsaka taka implementacija pomeni **arhitekturno kršitev**.

---

## 5. Merila skladnosti (COMPLIANCE CRITERIA)

Implementacija je skladna, če:

- Chat ne izvaja dejanj,
- UI ostaja read-only,
- vsi izvršilni učinki tečejo prek mandatov,
- revocation / expiry vedno delujeta,
- audit je pasiven,
- vidnost ne omogoča vpliva.

“Saj deluje” **ni** merilo skladnosti.

---

## 6. Zamrznitev interpretacije

Z odprtjem ENTRY-GATE velja:

- interpretacija B14 je **zaklenjena**,
- mandatni modeli se **ne reinterpretirajo**,
- UI omejitve so **nepogajljive**,
- morebitne spremembe zahtevajo **novo fazno odločitev**.

---

## 7. Zaključna izjava (KANONIČNA)

> **ENTRY-GATE dovoljuje začetek implementacije,  
> ne pa spremembe arhitekture.  
> Kar preseže ta dokument, je izven dovoljenega obsega.**

---

## STATUS

**ENTRY-GATE — OPEN**  
**IMPLEMENTATION AUTHORIZED**

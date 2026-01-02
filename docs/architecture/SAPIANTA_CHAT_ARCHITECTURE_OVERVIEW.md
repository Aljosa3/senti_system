# SAPIANTA CHAT — ARCHITECTURE OVERVIEW

## 1. Namen dokumenta

Ta dokument predstavlja **visokonivojski arhitekturni pregled** sistema **Sapianta Chat**.

Namen dokumenta je:
- razjasniti **logične sestavne dele** Sapianta Chata,
- opredeliti **tok obdelave znotraj domene Chata**,
- jasno določiti **mejo odgovornosti** med Chatom in okoljem izven njegove domene.

Dokument:
- ne opisuje implementacije,
- ne uvaja tehničnih vmesnikov,
- ne krši zaklepnih ali mandatnih aktov.

---

## 2. Arhitekturni principi

Arhitektura Sapianta Chata temelji na naslednjih principih:

- **Ločitev pomena od izvedbe**  
- **Enosmernost odgovornosti**  
- **Zaključevanje odgovornosti z intentom**  
- **Brez orkestracije in brez povratnih zank**

Vsak arhitekturni del obstaja znotraj **domene Sapianta Chata** in ne presega njenih meja.

---

## 3. Visokonivojski arhitekturni tok

Sapianta Chat obravnava zahteve skozi naslednji **logični tok**:

1. **Vhod zahteve (User Input)**
2. **Razjasnitev in interpretacija**
3. **Normativna presoja**
4. **Semantična normalizacija**
5. **Gradnja intenta**
6. **Zaključek odgovornosti (Output Boundary)**

Ta tok je **linearen**, brez iterativne povratne zanke iz izvedbe.

---

## 4. Ključni arhitekturni gradniki

### 4.1 Vhodni sloj (Input Layer)

- sprejema uporabniški vnos,
- ne predpostavlja strukture,
- ne izvaja semantičnih zaključkov.

Njegova vloga je **zajem**, ne interpretacija.

---

### 4.2 Interpretacijski sloj (Interpretation Layer)

- razjasnjuje pomen zahteve,
- zaznava dvoumnosti in manjkajoče informacije,
- omogoča pojasnjevalna vprašanja.

Ta sloj deluje izključno na ravni **pomena**.

---

### 4.3 Normativni sloj (Normative Filter)

- preverja skladnost zahteve z:
  - Zaklepno izjavo (NO-GO),
  - Izjavo o ne-orchestraciji,
  - Mandatom,
  - ostalimi governance akti.
- zavrača ali omejuje nedovoljene zahteve.

Normativni sloj ima **veto funkcijo**.

---

### 4.4 Semantični normalizator (Semantic Normalizer)

- poenoti terminologijo,
- odpravi implicitne predpostavke,
- pripravi pomen za strukturiranje.

Ne dodaja novih ciljev ali dejanj.

---

### 4.5 Gradnik intenta (Intent Builder)

- združi razjasnjen in preverjen pomen,
- oblikuje **deklarativni intent**,
- zaključi odgovornost Sapianta Chata.

Intent ni ukaz in ni naloga.

---

### 4.6 Izhodna meja (Output Boundary)

- predstavlja točko zaključka odgovornosti,
- omogoča obstoj intenta izven domene Chata,
- brez sprožitve, brez nadzora, brez povratnih zank.

Tu se arhitektura Sapianta Chata **konča**.

---

## 5. Arhitekturne meje

Sapianta Chat:
- ne pozna execution sloja,
- ne prejema povratnih signalov iz izvedbe,
- ne prilagaja vedenja na podlagi rezultatov.

Vsak poskus preseganja te meje predstavlja **arhitekturno kršitev**.

---

## 6. Razmerje do nadaljnjih dokumentov

Ta pregled je osnova za:

- **SAPIANTA_CHAT_INTERNAL_MODULES.md**  
- **CHAT_EXECUTION_BOUNDARY.md**  
- **IMPLEMENTATION_READINESS_CHECK.md**

Brez sprememb ali razširitev tega dokumenta.

---

## 7. Zaklepna določba

Ta arhitekturni pregled:
- ne uvaja implementacije,
- ne določa tehnologij,
- in ne odpira poti v orkestracijo.

Z njim je **arhitekturni okvir Sapianta Chata jasno določen**.

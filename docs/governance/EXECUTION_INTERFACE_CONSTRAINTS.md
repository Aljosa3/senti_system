# EXECUTION INTERFACE CONSTRAINTS

## 1. Namen dokumenta

Ta dokument določa **omejitve in varovalke** v razmerju med **Sapianta Chatom** in katerimkoli okoljem ali slojem, ki izvaja dejanja (execution).

Dokument:
- ne opisuje tehničnega vmesnika,
- ne določa protokolov, formatov ali API-jev,
- temveč opredeljuje **kaj execution sloj ne sme zahtevati, pričakovati ali povzročiti** v odnosu do Sapianta Chata.

---

## 2. Ločitev domen

**Sapianta Chat** in **execution sloj** pripadata **ločeni domeni odgovornosti**.

- Sapianta Chat deluje na ravni pomena.
- Execution sloj deluje na ravni dejanj.

Med domenama **ni povratne zanke**, nadzora ali hierarhije.

---

## 3. Prepovedane zahteve execution sloja

Execution sloj ne sme od Sapianta Chata zahtevati:

- ukazov ali navodil za izvedbo,
- zaporedij korakov,
- optimizacij na podlagi rezultatov izvedbe,
- ponovnega oblikovanja intenta zaradi neuspešne izvedbe,
- nadzora ali potrjevanja uspešnosti.

Vsaka taka zahteva predstavlja **kršitev domene**.

---

## 4. Prepoved povratnega vpliva

Execution sloj:
- ne vpliva na vedenje Sapianta Chata,
- ne sproža dodatnih pojasnjevanj z namenom izboljšanja izvedbe,
- ne ustvarja povratnih signalov, ki bi Chat potisnili v orkestracijo.

Vsi rezultati izvedbe ostajajo **izven domene Sapianta Chata**.

---

## 5. Enosmernost in zaključek odgovornosti

Razmerje je **enosmerno**:

- Sapianta Chat zaključi svojo odgovornost z oblikovanjem intenta.
- Execution sloj prevzame ali ne prevzame pomen brez povratnih obveznosti.

Ni zagotovila, da bo intent uporabljen, niti pričakovanja povratne informacije.

---

## 6. Neodvisnost execution sloja

Execution sloj:
- deluje neodvisno,
- ni podrejen Sapianta Chatu,
- in ne zahteva njegove prisotnosti za svoje delovanje.

Sapianta Chat ni pogoj za obstoj ali delovanje execution sloja.

---

## 7. Razmerje do drugih aktov

Ta dokument je skladen z:
- Zaklepno izjavo (NO-GO),
- Izjavo o ne-orchestraciji,
- Mandatom Sapianta Chata,
- Dokumentom o pozitivni vlogi Sapianta Chata,
- INTENT HANDOFF MODEL-om.

V primeru konflikta imajo **zaklepni in mandatni akti prednost**.

---

## 8. Zaklepna določba

EXECUTION INTERFACE CONSTRAINTS:
- ne ustvarja arhitekture,
- ne opisuje procesov,
- in ne odpira poti v orkestracijo.

Z njim je **razmerje med pomenom in izvedbo dokončno zaščiteno**.

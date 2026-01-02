# CHAT ↔ EXECUTION BOUNDARY

## 1. Namen dokumenta

Ta dokument določa **strogo in nepreklicno mejo odgovornosti** med **Sapianta Chatom** in katerimkoli sistemom, modulom ali okoljem, ki izvaja dejanja (execution).

Namen dokumenta je:
- preprečiti implicitno orkestracijo,
- onemogočiti povratne zanke,
- zaščititi Chat pred zdrsom v izvedbeno vlogo.

Dokument:
- ne opisuje tehničnih povezav,
- ne uvaja vmesnikov,
- in ne dovoljuje interpretacije v smeri delovanja.

---

## 2. Definicija meje

Meja med Chatom in execution slojem obstaja kot **konceptualna in odgovornostna ločnica**.

- Na strani Chata obstaja **pomen**.
- Na strani execution obstajajo **dejanja**.

Med njima ni:
- hierarhije,
- nadzora,
- koordinacije,
- ali povratne odvisnosti.

---

## 3. Kaj Chat nikoli ne počne

Sapianta Chat nikoli:

- ne sproži izvedbe,
- ne potrdi začetka ali konca dejanja,
- ne čaka na rezultat,
- ne ponavlja ali prilagaja intenta na podlagi izvedbe,
- ne nadzira ali optimizira delovanja execution sloja.

Vsak tak poskus pomeni **kršitev meje**.

---

## 4. Kaj execution sloj nikoli ne počne

Execution sloj nikoli:

- ne zahteva ukazov ali korakov od Chata,
- ne zahteva ponovne formulacije intenta za namen izvedbe,
- ne vrača rezultatov z namenom spremembe Chatovega vedenja,
- ne uporablja Chata kot nadzorne ali orkestracijske točke.

Vsak tak poskus pomeni **kršitev meje**.

---

## 5. Enosmernost odnosa

Razmerje je **enosmerno in nepovratno**:

- Chat zaključi svojo odgovornost z oblikovanjem intenta.
- Execution lahko intent uporabi ali ignorira.

Ni zagotovil, pričakovanj ali povratnih obveznosti.

---

## 6. Neodvisnost življenjskih ciklov

- Sapianta Chat lahko deluje brez execution sloja.
- Execution sloj lahko deluje brez Sapianta Chata.

Njuna življenjska cikla sta **neodvisna**.

---

## 7. Razmerje do drugih dokumentov

Ta dokument dopolnjuje in utrjuje:

- EXECUTION_INTERFACE_CONSTRAINTS.md,
- INTENT_HANDOFF_MODEL.md,
- Mandat Sapianta Chata,
- SAPIANTA_CHAT_ARCHITECTURE_OVERVIEW.md,
- SAPIANTA_CHAT_INTERNAL_MODULES.md.

V primeru konflikta imajo **governance in zaklepni akti prednost**.

---

## 8. Zaklepna določba

Ta meja:
- ni tehnična,
- ni začasna,
- in ni pogojna.

Z njo je **razmerje med Sapianta Chatom in execution slojem dokončno in trajno ločeno**.

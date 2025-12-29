# LLM INTEGRATION STATUS
## Deferred — By Design

---

## 1. Namen dokumenta

Ta dokument formalno določa status integracije
Large Language Modelov (LLM) v sistem Sapianta.

Njegov namen je:
- preprečiti implicitna pričakovanja o prisotnosti LLM-jev,
- zapreti razpravo o “kdaj jih dodamo” v zgodnjih fazah,
- zaščititi arhitekturo pred agentnostjo in interpretacijskim driftom,
- potrditi, da odsotnost LLM-jev ni pomanjkljivost, temveč zavestna odločitev.

---

## 2. Status

**LLM INTEGRATION: DEFERRED — BY DESIGN**

To pomeni:
- LLM-ji niso del trenutnega implementacijskega načrta,
- LLM-ji niso potrebni za delovanje sistema,
- LLM-ji niso del varnostne ali odločilne poti,
- arhitektura mora biti pravilna brez njih.

---

## 3. Razlogi za odložitev

LLM-ji se v zgodnjih fazah NE vključijo, ker:

- bi zabrisali dokaz ne-agentnosti chata,
- bi otežili formalno zaprtje B14,
- bi vnesli implicitno interpretacijo (konflikt z AIS),
- bi ustvarili odvisnost od zunanjega vedenja modela,
- bi zmanjšali možnost strogega dokazovanja meja.

Sistem mora najprej dokazati:
> **da je varen brez inteligence.**

---

## 4. Arhitekturno načelo

Arhitektura Sapianta je zasnovana tako, da:

- Chat Core deluje deterministično brez LLM-ja,
- Mandate, AM, MR in Execution ne poznajo LLM-ja,
- Audit in Visibility sloji ne uporabljajo LLM-ja,
- UI ne vsebuje LLM-logike.

Odstranitev ali zamenjava vseh LLM-jev
ne sme vplivati na pravilnost sistema.

---

## 5. Dovoljena prihodnja vloga LLM-jev (NE AKTIVNA)

Ko (in če) bo LLM integracija dovoljena v prihodnji fazi,
bo veljalo:

- LLM je stateless, text-only orodje,
- nima avtoritete,
- ne sprejema odločitev,
- ne aktivira ničesar,
- ne interpretira governance pravil,
- ne sodeluje v mandatnem ali izvršilnem toku.

Ta vloga NI aktivna v trenutni fazi.

---

## 6. Zamrznitev razprave

S tem dokumentom velja:

- vprašanje integracije LLM-jev je **formalno zaprto**,
- nadaljnja implementacija poteka **brez LLM-jev**,
- ponovna obravnava zahteva **novo fazno odločitev**,
- noben del sistema ne sme implicitno predpostavljati LLM-ja.

---

## STATUS

**LLM INTEGRATION — CLOSED**  
**DEFERRED BY DESIGN**

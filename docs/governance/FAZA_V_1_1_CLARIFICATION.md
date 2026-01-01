# FAZA V.1.1 – SPEC CLARIFICATION
## Normativna razjasnitev FAZE V.1 (PRE-EBM)

---

## 1. NAMEN DOKUMENTA

Ta dokument zagotavlja **normativno razjasnitev** FAZE V.1
in zapira odprte točke iz FAZA V.1 AUDIT poročila.

Dokument:
- ne uvaja novih funkcionalnosti
- ne spreminja namena FAZE V.1
- ne odpira prehoda v execution ali EBM

---

## 2. DEFINICIJA “IMPLICITNEGA INTENTA”

“Implicitni intent” je:
- interni, prehodni podatkovni zapis
- rezultat interpretacije uporabniškega vhoda
- ni trajno shranjen
- ni izpostavljen uporabniku
- nima samostojnega obstoja zunaj mandate pipeline

Implicitni intent:
- obstaja samo znotraj FAZE V.1
- služi izključno kot vhod v mandate pipeline
- se ne obravnava kot mandat

---

## 3. VEZAVA NA MANDATE PIPELINE (NORMATIVNO)

FAZA V.1 uporablja **obstoječi mandate pipeline**, definiran v FAZI II.

Normativno velja:
- FAZA V.1 ne uvaja novega pipeline-a
- FAZA V.1 kliče obstoječe validacijske in routing komponente
- FAZA V.1 ne določa notranje strukture mandata

Struktura mandata:
- je izven obsega FAZE V.1
- je definirana v obstoječih mandate specifikacijah

---

## 4. OMEJITEV OBSEGA

FAZA V.1 in FAZA V.1.1:
- ne specificirata podatkovne sheme mandata
- ne določata implementacijskih podrobnosti
- ne spreminjata FAZE II (Mandate Pipeline)

Namen teh faz je izključno:
- povezava chat → mandate pipeline
- formalizacija namena brez delovanja

---

## 5. ZAKLJUČNA IZJAVA

S tem dokumentom so:
- vse normativne nejasnosti FAZE V.1 razjasnjene
- audit WARNING točke zaprte
- FAZA V.1 pripravljena za implementacijo

Ta dokument je **obvezen dodatek** k:
- FAZA_V_1_MANDATE_CREATION.md

---

**STATUS: FAZA V.1.1 SPECIFIED**

KONEC DOKUMENTA

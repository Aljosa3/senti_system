# IDENTITY & AUTHORITY VERIFICATION MODEL (Post-Lock)

Projekt: Senti OS / Sapianta
Status: ACTIVE AFTER CORE LOCK
Applies from: FAZA 60
Authority: System Governance Framework

---

## 1. NAMEN DOKUMENTA

Ta dokument definira model preverjanja identitete in upravljalske avtoritete
po zaklepu jedra (CORE LOCK).

Namen dokumenta je zagotoviti, da:
- upravljalske odločitve niso vezane na napravo ali vmesnik,
- chat ne deluje kot vir identitete ali oblasti,
- so ADMIN pravice preverljive, časovno omejene in preklicljive,
- je dedovanje upravljalske avtoritete jasno in nadzorovano.

---

## 2. TEMELJNO NAČELO

Identiteta in avtoriteta sta ločeni od:
- chata,
- uporabniškega vmesnika,
- naprave,
- seje pogovora.

Chat lahko izraža zahteve,
ne more pa potrjevati identitete ali oblasti.

---

## 3. ADMIN SEJA (GOVERNANCE SESSION)

### 3.1 Definicija

ADMIN GOVERNANCE SESSION je:
- časovno omejena avtoritativna seja,
- izdana preverjeni identiteti,
- ki omogoča potrjevanje upravljalskih odločitev.

ADMIN seje niso trajne in se nikoli ne podeljujejo implicitno.

---

### 3.2 Potrditev ADMIN seje

ADMIN sejo je mogoče potrditi le z zavestnim dejanjem,
izvedenim iz zaupanega postopka.

Potrditev lahko vključuje:
- ponovno preverjanje identitete,
- dodatno potrditev (out-of-band),
- eksplicitno zahtevo po vstopu v ADMIN GOVERNANCE MODE.

Deklaracija v chatu (npr. "kot ADMIN") sama po sebi nima pravne veljave.

---

## 4. PREKINITEV ADMIN SEJE

ADMIN seje se prekinejo:

- samodejno po izteku časovne veljavnosti,
- ob eksplicitni odjavi ali prekinitvi,
- ob zaznani kršitvi pravil,
- ob spremembi suverenosti ali dedovanja.

Po prekinitvi seje:
- nobena upravljalska odločitev ni več veljavna,
- chat se vrne v neizvršilni način delovanja.

---

## 5. REVIZIJA IN SLEDLJIVOST

Vsaka ADMIN seja mora imeti:
- čas začetka in konca,
- vezavo na identiteto,
- zapis vseh potrjenih dejanj.

Revizijski zapisi so trajni in niso izbrisljivi.

---

## 6. DELOVANJE DEDOVANJA

V primeru odsotnosti, smrti ali trajne nezmožnosti primarnega suverena:

- upravljalska avtoriteta preide izključno po
  TECHNICAL_SUCCESSION_HIERARCHY.md,
- novi skrbnik ne deduje jedra,
- novi skrbnik pridobi možnost potrjevanja upravljalskih odločitev,
  ne pa implicitne pravice do spremembe CORE.

Dedovanje:
- ne aktivira trajne ADMIN seje,
- zahteva novo zavestno potrditev identitete,
- je vedno revizijsko sledljivo.

---

## 7. OMEJITEV MOČI CHATA

Chat:
- ne hrani identitet,
- ne potrjuje sej,
- ne preverja dedovanja,
- ne ustvarja oblasti.

Chat je izključno vmesnik za:
- komunikacijo,
- razlago,
- pripravo osnutkov.

---

## 8. KONČNA DOLOČBA

Ta dokument dopolnjuje:
- CORE_LOCK_DECLARATION.md
- ADMIN_GOVERNANCE_MODE_DEFINITION.md
- TECHNICAL_WILL_AND_SOVEREIGNTY.md

in je zavezujoč za vse upravljalske postopke po CORE LOCK.

---

END OF DOCUMENT

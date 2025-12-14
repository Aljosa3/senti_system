# CORE UPGRADE PROTOCOL
## Post-Lock Governance & Controlled Evolution

Version: 1.0  
Status: ACTIVE (post CORE LOCK)  
Applies from: CORE LOCK (FAZA 60)

---

## 1. NAMEN DOKUMENTA

Ta dokument določa **edini dovoljen postopek** za:
- nadgradnjo jedra (CORE),
- spremembo temeljnih pravil sistema,
- upravljanje verzij jedra po zaklepu.

Dokument velja **izključno**, če je aktiven dokument:
`CORE_LOCK_DECLARATION.md`.

V primeru konflikta ima prednost tehnična oporoka in deklaracija zaklepa.

---

## 2. OSNOVNO NAČELO

> **Jedro sistema se po zaklepu ne spreminja implicitno.  
> Vsaka sprememba je zavestno, avtorizirano in sledljivo dejanje človeka.**

To pomeni:
- brez tihe mutacije,
- brez samodejne evolucije,
- brez runtime sprememb brez potrditve.

---

## 3. KAJ SE ŠTEJE KOT NADGRADNJA JEDRA

Kot nadgradnja jedra se šteje vsaka sprememba, ki:
- vpliva na identiteto sistema,
- spreminja meje avtonomije,
- spreminja pravila samogradnje,
- spreminja governance ali nasledstvo,
- posega v zaklenjene CORE module.

Spremembe zunanjih modulov, ki ne vplivajo na CORE, **ne sodijo pod ta protokol**.

---

## 4. VSTOP V CORE UPGRADE MODE

### 4.1 Zahteva
Nadgradnja se začne samo z izrecno zahtevo:

> “Vstopi v CORE UPGRADE MODE.”

Zahtevo lahko vloži:
- PRIMARY SOVEREIGN,
- ali aktivni CUSTODIAN v skladu z nasledstveno hierarhijo.

---

### 4.2 Pogoji za vstop

Sistem preveri:
- legitimnost vlagatelja,
- da ni aktivno dedovanje,
- da sistem ni v SAFE MODE ali kriznem režimu.

Če primarni suveren sproži **Sovereignty Reclaim**, se CORE UPGRADE MODE nemudoma prekine.

---

## 5. HLADILNI REŽIM (COOL-DOWN)

Ob vstopu v CORE UPGRADE MODE:
- se samogradnja začasno ustavi,
- se self-healing omeji na pasivni nadzor,
- runtime preide v stabilizirano stanje.

Namen je popolna determinističnost postopka.

---

## 6. CORE UPGRADE PROPOSAL

Vsaka nadgradnja mora imeti predlog, ki vsebuje:
- trenutno verzijo jedra,
- ciljno verzijo,
- natančen opis sprememb,
- kaj se **ne** spreminja,
- oceno tveganja,
- rollback načrt.

Brez veljavnega predloga nadgradnja ni dovoljena.

---

## 7. VALIDACIJA

Predlog se validira glede skladnosti z:
- TECHNICAL_WILL_AND_SOVEREIGNTY.md,
- TECHNICAL_SUCCESSION_HIERARCHY.md,
- CORE_LOCK_DECLARATION.md.

Neuspešna validacija pomeni zavrnitev ali zahtevo po popravku.

---

## 8. ČLOVEŠKA POTRDITEV

Po uspešni validaciji je potrebna **izrecna človeška potrditev**.

Potrditev lahko poda:
- PRIMARY SOVEREIGN,
- ali aktivni CUSTODIAN v dovoljenem obsegu.

Brez potrditve se nadgradnja ne izvede.

---

## 9. IZVEDBA NADGRADNJE

Nadgradnja se izvede:
- atomsko,
- brez vmesnih stanj,
- z varnostno kopijo prejšnje verzije.

Ob napaki:
- sistem izvede rollback,
- preide v SAFE MODE,
- zahteva človeško presojo.

---

## 10. POST-UPGRADE OPAZOVANJE

Po nadgradnji:
- sistem deluje v opazovalnem režimu,
- spremljajo se anomalije,
- samogradnja ostane začasno omejena.

Če ni zaznanih težav, se sistem vrne v normalni režim.

---

## 11. AUDIT & TRAJNI SPOMIN

Vsaka nadgradnja se trajno zapiše:
- kdo je sprožil postopek,
- kdo je potrdil,
- kaj se je spremenilo,
- kdaj in zakaj.

Ti zapisi so nespremenljivi.

---

## 12. ČESA TA PROTOKOL NE POČNE

Ta protokol:
- ne preprečuje zavestnega uničenja sistema s strani suverena,
- ne nadomešča pravne odgovornosti,
- ne skriva kode ali arhitekture.

Njegov namen je preprečevanje kaosa, ne absolutna zaščita.

---

## 13. KONČNO NAČELO

> **Zaklep jedra ne pomeni konca razvoja.  
> Pomeni konec nenadzorovanega razvoja.**

---

END OF DOCUMENT

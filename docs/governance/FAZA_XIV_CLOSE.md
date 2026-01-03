# FAZA XIV — CLOSE
## Explain Layer (Read-only Explanation Contract)

Status: **ZAKLENJENO**  
Datum zaklepa: (vpiši ob commitu)  
Povezano z: FAZA XIII (meaning-only chat pipeline)

---

## 1. Namen FAZE XIV

FAZA XIV uvaja **Explain Layer** kot strogo **read-only razlagalno plast** nad že zaključenim in zaklenjenim izhodom sistema (`ChatResponse`).

Explain Layer obstaja izključno z namenom:
- razložiti **zakaj** je bil določen izhod (`OK` ali `REJECTED`) vrnjen,
- brez vpliva na odločanje,
- brez vpliva na potek sistema,
- brez vpliva na nadaljnje faze.

Explain Layer je **sekundarna semantična projekcija**, ne del odločitvenega procesa.

---

## 2. Razmerje do FAZE XIII

FAZA XIII (meaning-only pipeline) je:
- deterministična,
- brez executiona,
- brez exception-driven toka,
- z enotnim izhodom (`ChatResponse`),
- formalno zaklenjena.

FAZA XIV:
- **ne bere inputa**,
- **ne bere vmesnih stanj**,
- **ne sodeluje v odločanju**,
- **ne more vplivati na rezultat**.

Če Explain Layer ne obstaja ali odpove, sistem deluje **identično**.

---

## 3. Arhitekturna pozicija

User Input
↓
FAZA XIII — Meaning-only Pipeline (LOCKED)
↓
ChatResponse (IMMUTABLE)
↓
FAZA XIV — Explain Layer (READ-ONLY)
↓
ExplainResponse

Explain Layer je **popolnoma ločen sloj**.

---

## 4. Dovoljene odgovornosti (ALLOW)

Explain Layer SME:

- razložiti tip izhoda (ACCEPTED / REJECTED),
- razložiti formalni razlog iz obstoječih tipiziranih podatkov,
- razložiti **sistemski pomen** odločitve,
- uporabljati samo deterministična, vnaprej določena pravila preslikave.

Explain Layer je:
- deklarativen,
- opisni,
- nevtralen,
- brez dialoga.

---

## 5. Prepovedane odgovornosti (DENY)

Explain Layer NE SME:

- postavljati vprašanj,
- predlagati ukrepov ali alternativ,
- eskalirati ali preusmerjati zahteve,
- vplivati na pipeline ali rezultat,
- interpretirati uporabnikovega namena,
- razlagati procesa odločanja,
- uvajati heuristike ali mehčanje zavrnitev,
- personalizirati ali prilagajati UX.

Explain Layer **ni pomoč**, **ni mediator**, **ni UX plast**.

---

## 6. ExplainResponse — normativna oblika

Explain Layer generira **ExplainResponse**, ki je:

- 1 : 1 preslikava iz `ChatResponse`,
- deterministična,
- brez stranskih učinkov,
- brez povratnega vpliva.

Semantična struktura ExplainResponse vključuje:
- `outcome` (sprejet / zavrnjen),
- `explanation` (razlog + sistemski pomen),
- `invariants` (nespremenljive sistemske trditve).

ExplainResponse je **derivat**, nikoli vir resnice.

---

## 7. Preslikovalna pravila

Preslikava `ChatResponse → ExplainResponse` je:

- totalna (vedno definiran izhod),
- deterministična,
- brez inferenc,
- brez ponovne klasifikacije.

Če razlog ni znan:
- uporabi se nevtralna, nedoločena razlaga,
- brez eskalacije,
- brez napake.

Explain Layer nikoli ne ustvarja novih razlogov.

---

## 8. Invarianti FAZE XIV

FAZA XIV mora vedno zagotavljati:

- imutabilnost FAZE XIII,
- popolno ločenost razlage od odločanja,
- odsotnost stranskih učinkov,
- možnost popolne odstranitve Explain Layerja brez vpliva.

---

## 9. Razmerje do prihodnjih faz

FAZA XIV:
- ne predpostavlja nobene nadaljnje faze,
- ne odpira poti za execution,
- ne odpira poti za UX eskalacijo.

Vse prihodnje faze so dolžne spoštovati ta zaklep.

---

## 10. Zaklep

S tem dokumentom je FAZA XIV:

- **formalno zaključena**,
- **normativno zaklenjena**,
- **neodvisna od implementacije**.

Vsaka sprememba te faze zahteva:
- novo fazo,
- nov dokument,
- ekspliciten governance sklep.

FAZA XIV se po tem dokumentu **ne spreminja več**.
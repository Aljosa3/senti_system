# FAZA XV — CLOSE
## Observability / Audit Layer (Read-only Audit Contract)

Status: **ZAKLENJENO**  
Datum zaklepa: (vpiši ob commitu)  
Povezano z:  
- FAZA XIII — Meaning-only Chat Pipeline (LOCKED)  
- FAZA XIV — Explain Layer (LOCKED)

---

## 1. Namen FAZE XV

FAZA XV uvaja **Observability / Audit Layer** kot strogo **read-only revizijsko plast**, katere edini namen je:

- zagotoviti **dokazljivost**, da je sistem sprejel odločitev,
- omogočiti **revizijo izhodov** brez razkrivanja vsebine ali logike,
- brez kakršnegakoli vpliva na odločanje, razlago ali prihodnje vedenje sistema.

FAZA XV ne dodaja funkcionalnosti.  
FAZA XV formalizira **obstoječo realnost odločitev**.

---

## 2. Razmerje do FAZE XIII in XIV

### FAZA XIII
- sprejema odločitev,
- generira `ChatResponse`,
- je deterministična in zaklenjena.

### FAZA XIV
- razlaga pomen odločitve,
- je read-only in zaklenjena.

### FAZA XV
- **ne bere inputa**,
- **ne bere ExplainResponse za logiko**,
- bere izključno **končni izhod odločitve**,
- nima nobene povratne poti.

Če FAZA XV ne obstaja ali odpove, sistem deluje **identično**.

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
↓
FAZA XV — Observability / Audit (READ-ONLY)
↓
AuditRecord


FAZA XV je **pasivni zaključni sloj**.

---

## 4. Dovoljene odgovornosti (ALLOW)

FAZA XV SME:

- zabeležiti **minimalni dokazni zapis** odločitve,
- beležiti **samo metapodatke**,
- delovati deterministično,
- delovati popolnoma ločeno od ostalih faz.

Audit je **sled**, ne proces.

---

## 5. Prepovedane odgovornosti (DENY)

FAZA XV NE SME:

- vplivati na tok sistema,
- spreminjati rezultat,
- zavračati ali potrjevati zahteve,
- blokirati ali upočasnjevati pipeline,
- shranjevati input ali vsebino,
- shranjevati razlago,
- uvajati analitiko ali korelacije,
- omogočati replay ali debugging,
- vplivati na prihodnje odločitve.

Audit **ni logiranje** in **ni observability platforma**.

---

## 6. AuditRecord — normativna oblika

FAZA XV generira **AuditRecord**, ki je:

- minimalen,
- determinističen,
- neodvisen,
- neinterpretativen.

AuditRecord vključuje izključno:
- čas dogodka,
- izhod odločitve (ACCEPTED / REJECTED),
- kategorijo razloga (če obstaja),
- identifikacijo izvorne faze (FAZA XIII).

AuditRecord **ne vsebuje**:
- vsebine,
- razlage,
- uporabniških podatkov,
- identifikatorjev sej,
- korelacij ali poti odločanja.

---

## 7. Preslikovalna pravila

Preslikava `ChatResponse → AuditRecord` je:

- totalna,
- deterministična,
- brez inferenc,
- brez razširitev pomena.

Če razlog ni znan:
- uporabi se nevtralna, nedoločena kategorija,
- brez eskalacije in brez napake.

FAZA XV nikoli ne ustvarja novih razlogov.

---

## 8. Invarianti FAZE XV

FAZA XV mora vedno zagotavljati:

- popolno pasivnost,
- odsotnost stranskih učinkov,
- imutabilnost FAZE XIII in XIV,
- možnost popolne odstranitve brez vpliva na sistem.

---

## 9. Razmerje do prihodnjih faz

FAZA XV:
- ne odpira poti za execution,
- ne odpira poti za učenje ali optimizacijo,
- ne predpostavlja nobene naslednje faze.

Vsaka razširitev audita zahteva:
- novo fazo,
- nov CLOSE dokument,
- ekspliciten governance sklep.

---

## 10. Zaklep

S tem dokumentom je FAZA XV:

- **formalno zaključena**,
- **normativno zaklenjena**,
- **strogo read-only**,
- **neodvisna od implementacije**.

FAZA XV se po tem dokumentu **ne spreminja več**.
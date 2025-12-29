# MANDATE REVOCATION & EXPIRY MODEL
## Controlled Termination of Continuous Execution

---

## 1. Namen dokumenta

Ta dokument definira **mehanizme preklica, poteka in izredne zaustavitve mandata**
v sistemu Sapianta.

Njegov namen je zagotoviti, da:
- noben mandat ni trajen,
- vsako avtonomno izvajanje ima jasen izhod,
- sistem ostane pod človeškim nadzorom,
- B14 varnostni zaklepi ostanejo nedotaknjeni.

---

## 2. Temeljno načelo

> **Vsak mandat mora imeti jasno določen začetek in konec.  
> Kar se lahko zažene, se mora vedno tudi ustaviti.**

To načelo je nepreklicno.

---

## 3. Vrste prenehanja mandata

### 3.1 EXPIRY — Samodejni potek

Mandat **samodejno preneha**, ko je izpolnjen katerikoli od vnaprej določenih pogojev:

- časovni potek (npr. datum / čas),
- količinski limit (npr. število akcij),
- dosežen cilj (npr. modul zgrajen),
- varnostni prag (npr. maksimalni drawdown),
- izpolnitev enkratne naloge.

Potek:
- ne zahteva dodatne odločitve,
- se zgodi deterministično,
- povzroči takojšnjo zaustavitev izvajanja.

---

### 3.2 REVOCATION — Eksplicitni preklic

Mandat se **takoj prekliče**, če:

- uporabnik izrecno zahteva preklic,
- nadrejeni mandat razveljavi podrejenega,
- governance sprememba mandat naredi neveljaven,
- Mandate Resolver zazna kršitev obsega.

Preklic:
- je takojšen (hard stop),
- nima prehodnega obdobja,
- ne zahteva potrditve modula.

---

### 3.3 EMERGENCY STOP — Izredna zaustavitev

Izredna zaustavitev se sproži, ko sistem zazna **kritično stanje**, npr.:

- preseženo tveganje,
- nedovoljen stranski učinek,
- tehnično ali varnostno stanje,
- kršitev LOCKED slojev.

Lastnosti:
- izvajanje se ustavi takoj,
- uporabnik je obveščen **po zaustavitvi**,
- Chat nima vloge pri sprožitvi ali preprečitvi.

---

## 4. Odgovornosti po slojih

| Sloj | Vloga |
|----|-----|
| Sapianta Chat | Obveščanje in razlaga *da* je mandat prenehal |
| Activation Module | Potrditev neveljavnosti mandata |
| Mandate Resolver | Sledenje, preklic, potek |
| Execution Layer | Takojšnja zaustavitev izvajanja |

Sapianta Chat:
- ne odloča o preklicu,
- ne preprečuje poteka,
- ne interpretira razlogov.

---

## 5. Prepovedi (kanonične)

Prepovedano je:

- nadaljevanje izvajanja po preklicu ali poteku,
- implicitno podaljševanje mandata,
- samodejno obnavljanje brez nove odločitve,
- razširjanje obsega ob poteku,
- “mehka” zaustavitev brez dejanske prekinitve.

---

## 6. Primeri

### 6.1 Trading mandat

Mandat:
- BTC
- 1–3 % tveganja
- 30 dni
- max drawdown 8 %

Scenariji:
- po 30 dneh → **expiry**
- pri −8 % → **emergency stop**
- ob user ukazu “ustavi” → **revocation**

V vseh primerih:
- izvajanje se ustavi takoj,
- nova odločitev je potrebna za ponovni zagon.

---

### 6.2 Izgradnja modula

Mandat:
- zgradi modul X

Scenariji:
- build končan → **expiry**
- user prekliče → **revocation**
- sistemska napaka → **emergency stop**

---

## 7. Razmerje do MANDATE MODEL in B14

Ta dokument:
- dopolnjuje `MANDATE_MODEL.md`,
- ne spreminja B14,
- ne omogoča agentnosti ali implicitne avtonomije.

> **B14 prepoveduje izvrševanje chata.  
> Mandate Revocation & Expiry zagotavlja, da se izvajanje vedno lahko ustavi.**

---

## 8. Zaključna izjava

> **Avtonomija brez izhoda ni nadzor.  
> Mandat brez konca ni dovoljenje.  
> Sapianta sistem se vedno lahko ustavi.**

---

## STATUS

**MANDATE REVOCATION & EXPIRY MODEL — ESTABLISHED**

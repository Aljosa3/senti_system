# MANDATE MINIMAL UI CONTRACT
## What the UI Must Never Become

---

## 1. Namen dokumenta

Ta dokument definira **stroge in trajne omejitve uporabniškega vmesnika (UI)**
v sistemu Sapianta, povezane z mandati in izvajanjem.

Njegov namen je preprečiti, da bi UI:
- postal nadzorni center,
- implicitno odločal,
- vodil uporabnika v agentno delegacijo,
- ustvarjal iluzijo neposredne kontrole nad izvajanjem.

---

## 2. Temeljno načelo

> **UI je prikaz, ne krmilnik.  
> UI je informacija, ne odločitev.  
> UI je pasiven, ne operativen.**

Vsaka UI funkcija mora biti presojana skozi to načelo.

---

## 3. Kaj UI SME biti

UI sme:
- prikazovati stanje mandatov (read-only),
- prikazovati agregirane kazalnike,
- prikazovati audit dogodke,
- prikazovati status (aktiven / ustavljen / potekel),
- prikazovati statične povzetke.

UI ne sproža sprememb stanja.

---

## 4. Kaj UI NE SME NIKOLI postati

UI **NE SME** postati:

### 4.1 Nadzorna plošča (Control Panel)
- brez gumbov: *start / stop / pause / resume*
- brez drsnikov za parametre v realnem času
- brez “tuning” kontrol

---

### 4.2 Agentni vmesnik
- brez vprašanj tipa:  
  *“Naj sistem to naredi namesto vas?”*
- brez predlaganja delegacije
- brez “samodejnih izboljšav”

---

### 4.3 Real-time operativni vmesnik
- brez live signalov,
- brez streaminga odločitev,
- brez taktičnega nadzora.

---

### 4.4 Odločitveni vmesnik
- brez “confirm execution” gumbov,
- brez “apply changes now”,
- brez prikritih potrditev.

Odločitev se vedno zgodi **izven UI toka**.

---

### 4.5 Razlagalni varnostni vmesnik
- brez razlage STOP razlogov,
- brez prikaza governance pravil,
- brez “zakaj sistem ne dovoli”.

UI ne razlaga svojih omejitev.

---

## 5. Prepovedani UI vzorci (explicit)

Prepovedani so:
- toggle-i, ki vplivajo na izvajanje,
- sliderji za parametre med tekom,
- “panic button”, ki obide mandate,
- “quick fix” akcije,
- “one-click automation”.

Vsak tak element pomeni **arhitekturno kršitev**.

---

## 6. Razmerje UI ↔ Chat

Sapianta Chat:
- je del UI,
- je tekstovni prikazni vmesnik,
- ne postane krmilnik sistema.

Chat:
- lahko POVE, kaj vidi,
- ne more SPREMENITI, kar vidi.

---

## 7. Razmerje do mandatnega sistema

UI:
- ne ustvarja mandatov,
- ne spreminja mandatov,
- ne podaljšuje mandatov,
- ne preklicuje mandatov.

Vse odločitve:
- nastanejo zunaj UI,
- so eksplicitne,
- so enkratne.

---

## 8. Posledice kršitve

Vsaka kršitev tega dokumenta pomeni:
- implicitno agentnost,
- obvod B14,
- razpad varnostnega modela.

Tak UI je **nezdružljiv s Sapianta arhitekturo**.

---

## 9. Zaključna izjava

> **Če UI daje občutek nadzora, je že predaleč.  
> Če UI omogoča vpliv, je že prekršil mejo.  
> Minimalen UI je pogoj za varno avtomatizacijo.**

---

## STATUS

**MANDATE MINIMAL UI CONTRACT — ESTABLISHED**

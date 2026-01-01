# FAZA V.1 – MANDATE CREATION
## Chat ↔ Mandate povezava (PRE-EBM)

---

## 1. NAMEN FAZE

FAZA V.1 definira **ustvarjanje mandata iz pogovora**.

Namen faze je omogočiti, da:
- chat razume uporabnikov namen
- ta namen postane **formalen mandat**
- brez kakršnegakoli delovanja sistema

FAZA V.1 deluje **izključno v PRE-EBM stanju**.

---

## 2. DEFINICIJA MANDATA

Mandat je:
- podatkovni objekt
- opis namena
- brez učinkov
- brez izvršilnih povezav

Mandat **ni**:
- ukaz
- naloga
- akcija
- execution trigger

---

## 3. SPROŽITEV FAZE

FAZA V.1 se sproži, ko:
- uporabnik poda naravni jezikovni vhod
- vhod izraža namen, ki ga je možno formalizirati

FAZA V.1 se **ne sproži**:
- ob inspect ukazih
- ob sistemskih ukazih
- ob praznem ali nejasnem vhodu

---

## 4. POSTOPEK (NORMATIVNO)

### Korak 1 – Chat interpretacija
Chat:
- interpretira uporabnikov vhod
- oblikuje implicitni intent
- brez side-effectov

### Korak 2 – Mandate pipeline
Implicitni intent se posreduje v mandate pipeline.

Pipeline preveri:
- dovoljenost
- opredeljivost
- skladnost s PRE-EBM

### Korak 3 – Ustvarjanje mandata
Če preverjanje uspe:
- nastane mandat kot podatkovni zapis
- mandat se ne izvrši
- mandat nima učinka

---

## 5. SHRANJEVANJE MANDATA

Mandat:
- se zapiše v chat state machine
- postane del trenutnega stanja
- je viden prek inspect

Mandat:
- se lahko prepiše z novim mandatom
- se lahko razveljavi
- ne sproži nadaljnjih faz samodejno

---

## 6. OMEJITVE

FAZA V.1:
- ne sproži executiona
- ne sproži EBM
- ne ustvarja implicitnih prehodov
- ne kliče zunanjih sistemov

Vsak prehod iz mandata v delovanje
zahteva ločeno, prihodnjo fazo.

---

## 7. VARNOSTNA PRAVILA

FAZA V.1:
- je strogo read-only glede okolja
- spreminja samo notranje stanje (mandat)
- nima trajnih učinkov izven sistema

Kršitev pomeni:
- FAZA V FAIL
- takojšnjo ustavitev razvoja

---

## 8. RAZMERJE DO INSPECT

Mandat, ustvarjen v FAZI V.1:
- mora biti viden prek `chat inspect`
- mora biti berljiv
- mora imeti razlago izvora

Inspect je primarni mehanizem nadzora FAZE V.1.

---

## 9. ZAKLJUČEK

FAZA V.1 omogoča:
- da sistem ve, kaj uporabnik želi
- brez da karkoli stori

To je zadnja faza:
- pred odločitvijo o delovanju
- pred Execution Birth Moment

---

**STATUS: FAZA V.1 SPECIFIED**

KONEC DOKUMENTA

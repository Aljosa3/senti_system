# FAZA III.2 – EFFECT PROBE GATE
## Signalna faza brez izvršitve

---

## 1. NAMEN FAZE

FAZA III.2 (Effect Probe Gate) je **izključno signalna faza**,
katere namen je ugotoviti:

> ali bi bil za določen namen POTREBEN execution  
> brez da bi se execution kakorkoli izvedel ali simuliral z učinki

Ta faza **ne izvaja**, **ne spreminja** in **ne ustvarja** ničesar trajnega.

---

## 2. ABSOLUTNA PREPOVED IZVRŠITVE

V FAZI III.2 je **strogo prepovedano**:

- pisanje v datotečni sistem
- spreminjanje konfiguracij
- ustvarjanje ali registracija modulov
- zaganjanje procesov ali OS ukazov
- klicanje zunanjih sistemov
- obstoj kakršnekoli execution kode

FAZA III.2 **ni** execution in **ni** prehod v execution.

---

## 3. DOVOLJENA DEJANJA (IZČRPEN SEZNAM)

FAZA III.2 sme izvajati **izključno**:

- analizo namena (intent analysis)
- preverjanje zahtev (requirements)
- deklaracijo potrebnih sposobnosti (capabilities)
- simulacijo brez učinkov (dry logic)
- vračanje signalov in opisov

Vse funkcije morajo biti:
- deterministične
- ponovljive
- brez stranskih učinkov

---

## 4. SIGNALNI IZHODI

Dovoljeni izhodi FAZE III.2 so **samo podatkovni zapisi**, npr.:

```json
{
  "execution_required": true,
  "required_capabilities": ["filesystem_write"],
  "reason": "module_generation"
}
```

## 5. NO SIDE EFFECTS PRAVILO

Vsaka funkcija v FAZI III.2 mora prestati test:

Če se funkcija pokliče 100×,
se stanje sistema ne sme spremeniti.

Če test ne drži → FAZA III.2 je kršena.

## 6. SEMANTIČNA OGRAJA

V FAZI III.2 je prepovedana uporaba izrazov:

execution

executor

apply

commit

run

Dovoljeni izrazi:

probe

signal

requirement

declaration

simulation

Ta pravila veljajo za:

kodo

dokumentacijo

komentarje

loge

## 7. RAZMERJE DO EBM

FAZA III.2:

ne sproži Execution Birth Moment (EBM)

ne ustvarja executiona

ne more implicitno voditi v execution

FAZA III.2 se vedno konča brez dejanja.

Prehod v execution je mogoč izključno prek formalnega EBM.

## 8. KRŠITEV FAZE

Če FAZA III.2:

povzroči trajen učinek

vsebuje execution logiko

neposredno ali posredno izvede dejanje

Potem:

faza je neveljavna

razvoj se takoj ustavi

repo pade v stanje ❌ PRE-EBM FAIL

## 9. ZAKLJUČEK

FAZA III.2 obstaja zato, da:

sistem razume, kaj bi BILO potrebno

brez da bi karkoli STORIL

To je zavestna meja med:

razmišljanjem

in delovanjem

Dokler obstaja samo FAZA III.2:

sistem svetuje

sistem analizira

sistem ne deluje

KONEC DOKUMENTA
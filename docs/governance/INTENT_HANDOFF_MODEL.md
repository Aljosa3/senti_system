# INTENT HANDOFF MODEL

## 1. Namen dokumenta

Ta dokument opredeljuje **model posredovanja namena (intent)** iz **Sapianta Chata** v okolje izven njegove domene, brez izvajanja, brez orkestracije in brez nadzora nad izvedbo.

Model:
- ne definira tehničnega vmesnika,
- ne določa protokolov ali formatov,
- temveč opisuje **konceptualno obliko in mejo odgovornosti** pri predaji pomena.

---

## 2. Kaj je “intent”

**Intent** je:
- semantično zaključen opis namena,
- rezultat razjasnjevanja, normalizacije in normativne presoje,
- brez postopkov, korakov ali ukaznih elementov.

Intent **ni**:
- naloga (task),
- ukaz,
- zahteva za izvedbo,
- ali navodilo za zaporedje dejanj.

---

## 3. Nastanek intenta

Intent nastane izključno znotraj domene **Sapianta Chata** kot rezultat njegove pozitivne vloge:

- razjasnjevanja uporabniške zahteve,
- odprave dvoumnosti,
- preverjanja skladnosti z omejitvami,
- in semantične normalizacije.

Ko je intent oblikovan, je **Chatova odgovornost zaključena**.

---

## 4. Oblika intenta (konceptualno)

Intent je razumljen kot:

- **deklarativni opis cilja**,
- z jasno izraženimi omejitvami in kontekstom,
- brez implicitnega ali eksplicitnega zaporedja dejanj.

Oblika intenta je **opisna**, ne operativna.

---

## 5. Predaja intenta (handoff)

Predaja intenta pomeni:

- da je pomen **na voljo** izven domene Sapianta Chata,
- brez zagotovila, da bo uporabljen,
- brez pričakovanja odziva,
- brez povratnega nadzora.

Sapianta Chat:
- ne sproži predaje,
- ne preverja uspešnosti,
- ne čaka na rezultat.

Handoff je **enosmeren in zaključen**.

---

## 6. Meje in varovalke

Model izrecno izključuje:

- povratne ukaze iz execution sloja v Chat,
- iterativno optimizacijo na podlagi izvedbe,
- eskalacijo Chata v nadzorno ali orkestracijsko vlogo.

Vsaka uporaba intenta se zgodi **izven odgovornosti Sapianta Chata**.

---

## 7. Razmerje do drugih aktov

Ta model je skladen z:
- Zaklepno izjavo (NO-GO),
- Izjavo o ne-orchestraciji,
- Mandatom Sapianta Chata,
- Dokumentom o pozitivni vlogi Sapianta Chata.

V primeru konflikta imajo **zaklepni akti prednost**.

---

## 8. Zaklepna določba

INTENT HANDOFF MODEL:
- ne predstavlja izvedbenega načrta,
- ne določa arhitekture,
- in ne ustvarja implicitnega prehoda v delovanje.

Z njim je določen **čist, varen in ne-orkestracijski most pomena** med Sapianta Chatom in okoljem izven njegove domene.

# ENTRY TASK LIST
## First Authorized Implementation Steps

---

## 1. Namen dokumenta

Ta dokument določa **prve dovoljene implementacijske korake**
po odprtju ENTRY-GATE za sistem Sapianta.

Njegov namen je:
- zagotoviti pravilen vstop v implementacijo,
- preprečiti prehiter prehod v funkcionalnost,
- zaščititi arhitekturne meje (B14, Mandate Stack),
- vzpostaviti minimalen, varen skelet sistema.

---

## 2. Temeljno pravilo začetka

> **Najprej implementiramo meje.  
> Šele nato funkcionalnosti.**

Prvi koraki so namenoma:
- skeletni,
- omejeni,
- neuporabni v produkcijskem smislu.

---

## 3. TASK 0 — Arhitekturna verifikacija (MUST)

### Namen
Dokazati, da se implementacija lahko začne
brez implicitne izvršilnosti ali agentnosti.

### Naloge
- ustvariti osnovno mapno strukturo implementacije,
- brez runtime logike,
- brez povezave na execution ali mandate.

### Rezultat
- projekt se zažene,
- sistem ne more izvesti nobenega dejanja.

Če ta korak ni možen, je arhitektura napačno razumljena.

---

## 4. TASK 1 — Sapianta Chat: Minimal Skeleton (CORE)

### Namen
Vzpostaviti **čisti advisory chat skelet**.

### Dovoljeno
- sprejem tekstovnega inputa,
- generiranje tekstovnega outputa,
- stateless obnašanje,
- brez stranskih učinkov.

### Prepovedano
- izvrševanje,
- klicanje modulov,
- dostop do sistema,
- delo z mandati,
- implicitne potrditve.

### Cilj
Dokazati, da Sapianta Chat lahko obstaja
kot popolnoma ne-izvršilni vmesnik.

---

## 5. TASK 2 — Interaction Modes (READ-ONLY)

### Dovoljeno
Implementacija izključno:
- Explain mode,
- Summarize mode.

Oba načina:
- brez priporočil,
- brez rangiranja,
- brez normativnih sodb.

### Prepovedano
- Propose,
- Compare (če vodi v odločanje),
- kakršnakoli sugestivna logika.

---

## 6. TASK 3 — STOP MECHANISM (LOCAL)

### Namen
Vzpostaviti deterministični mehanizem zaustavitve.

### Sprožilci
- nejasen namen uporabnika,
- poskus izvršitve,
- poskus prenosa odgovornosti,
- zahteva po implicitni odločitvi.

### Lastnosti
- proces se ustavi,
- brez razlage razloga,
- brez notranjih signalov,
- brez nadaljevanja.

Cilj:
> **Chat zna reči NE brez razlage.**

---

## 7. TASK 4 — NAMERNO PRELOŽENO (DO NOT IMPLEMENT YET)

Naslednje je v tej fazi **prepovedano**:

- ustvarjanje mandatov,
- Activation Module,
- Mandate Resolver,
- Execution Layer,
- trading logika,
- audit zapisovanje,
- UI pogledi ali kontrole.

Vsak pojav teh elementov pomeni kršitev ENTRY-GATE.

---

## 8. Definition of Done (Prva faza)

Implementacija je pravilna, če:

- chat sprejme tekstovni input,
- vrne razlago ali povzetek,
- se ob nevarnem inputu ustavi,
- v kodi ni nobene izvršilne poti,
- v kodi ni “začasnih” obvodov.

---

## 9. Zaključna izjava

> **Prvi implementacijski korak ni funkcionalnost.  
> Je dokaz, da arhitektura preživi stik s kodo.**

---

## STATUS

**ENTRY TASK LIST — ACTIVE**  
**READY FOR IMPLEMENTATION**

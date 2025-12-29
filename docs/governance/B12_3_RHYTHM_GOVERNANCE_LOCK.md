===== ZAČETEK DOKUMENTA =====

# B12.3 — Rhythm Governance Lock
Version: 1.0  
Status: Governance Lock  
Scope: Sapianta Chat (schat)  
Related SPEC: B12_RHYTHM_SIGNALS_SPEC.md  

---

## 1. Namen zaklepa

Ta dokument vzpostavlja **nepreklicne meje uporabe ritmičnih signalov (Rhythm Signals)** v sistemu Sapianta Chat.

Namen zaklepa je preprečiti:
- zdrs v interpretacijo uporabnika
- implicitno avtomatizacijo vedenja
- povratne zanke med opazovanjem in delovanjem sistema

Rhythm Signals obstajajo izključno kot **pasivni časovni zapisi**.

---

## 2. Absolutne prepovedi (Hard Lock)

Naslednje rabe ritma so **strogo prepovedane**:

- sprožanje opozoril ali priporočil v realnem času
- spreminjanje UI, toka ali načina interakcije
- avtomatsko sklepanje o stanju uporabnika
- kakršnokoli ocenjevanje, razvrščanje ali primerjanje
- implicitni “nudge”, upočasnjevanje ali pospeševanje uporabe

Ritem **nima izvršilne vloge**.

---

## 3. Prepoved povratne zanke

Podatki o ritmu:
- se **ne vračajo** v schat
- se **ne uporabljajo** za prilagajanje vedenja sistema
- se **ne povezujejo** z vsebino ali odločitvami

S tem je preprečena entropija sistema skozi samoregulacijo.

---

## 4. Dovoljena uporaba (edina izjema)

Edina dovoljena uporaba Rhythm Signals je:

- retrospektivna
- offline
- človeško vodena
- ločena od sistema Sapianta Chat

Vsaka druga uporaba zahteva:
- novo fazo
- nov SPEC
- izrecno soglasje človeka

---

## 5. Zaključek

Ta Governance Lock zagotavlja, da:
- sistem ostaja nevtralen
- uporabnik ostaja suveren
- časovni podatki ne postanejo vedenjski mehanizem

B12.3 je **končna zaklepna točka ritma**.

===== KONEC DOKUMENTA =====

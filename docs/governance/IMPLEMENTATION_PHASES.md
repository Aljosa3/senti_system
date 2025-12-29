# IMPLEMENTATION PHASES
## Canonical Development Order (I–VII)

---

## 1. Namen dokumenta

Ta dokument kanonično določa **razvojne faze sistema Sapianta**
in njihov **obvezen vrstni red implementacije**.

Njegov namen je:
- ohraniti sled odločitev,
- preprečiti preskakovanje faz,
- zaščititi arhitekturo pred tehničnim in konceptualnim dolgom,
- zagotoviti, da frontend in LLM integracije ne vplivajo na jedro sistema.

---

## 2. Temeljno načelo

> **Najprej se dokaže varnost in ločitev odgovornosti.  
> Šele nato uporabnost in izkušnja.**

Vsaka faza je:
- samostojno preverljiva,
- zaključljiva,
- pogoj za naslednjo fazo.

---

## 3. FAZA I — CHAT CORE

**Opis:**
- advisory-only chat proces,
- CLI ali enostaven servis,
- brez UI,
- brez LLM,
- brez execution,
- brez stanja.

**Namen:**
Dokazati, da lahko obstaja komunikacijski vmesnik,
ki nima nobene izvršilne ali odločilne moči.

**Status ob zaključku:**
- Chat obstaja,
- Chat komunicira,
- Chat ne more ničesar narediti.

---

## 4. FAZA II — MANDATE PIPELINE

**Opis:**
- formalni mandatni model,
- Activation Module (AM),
- Mandate Resolver (MR),
- lifecycle: create / validate / expire / revoke.

**Namen:**
Vzpostaviti odločitev-enkrat → izvajanje-neprekinjeno
brez prisotnosti chata ali UI.

**Status ob zaključku:**
- mandat lahko obstaja,
- mandat je nadzorovan,
- nič se še ne izvaja.

---

## 5. FAZA III — EXECUTION LAYER

**Opis:**
- izoliran izvršilni sloj,
- deluje samo z veljavnim mandatom,
- brez UI,
- brez chata.

**Namen:**
Dokazati, da sistem lahko izvaja dejanja
brez kakršnegakoli uporabniškega vmesnika.

**Status ob zaključku:**
- dejanja se izvajajo,
- mandat jih omejuje,
- chat o tem nič ne ve.

---

## 6. FAZA IV — AUDIT + READ-ONLY VISIBILITY

**Opis:**
- audit logi,
- lifecycle zapisi,
- read-only vpogledi v stanje.

**Namen:**
Omogočiti vidnost brez vpliva.

**Status ob zaključku:**
- človek vidi,
- sistem deluje,
- UI še vedno ne nadzira.

---

## 7. FAZA V — CHAT ↔ MANDATE POVEZAVA

**Opis:**
- chat lahko bere stanje,
- chat lahko razlaga videno,
- chat lahko pripravi osnutke (draft),
- chat ne aktivira ničesar.

**Namen:**
Narediti chat uporaben,
ne da bi postal agent ali kontrolni center.

**Status ob zaključku:**
- chat informira,
- ne upravlja.

---

## 8. FAZA VI — REAL MODULI

**Opis:**
- dejanski moduli (npr. trading),
- realna avtomatizacija,
- vse znotraj mandatov.

**Namen:**
Uvesti moč šele, ko so zaščite že aktivne.

**Status ob zaključku:**
- sistem ima realen učinek,
- tveganja so že omejena.

---

## 9. FAZA VII — FRONTEND

**Opis:**
- frontend kot read-only odsev,
- vizualizacija stanja,
- audit explorer,
- brez gumbov za upravljanje.

**Namen:**
Omogočiti razumevanje,
ne nadzor.

**Opomba:**
Frontend je zadnja faza,
ker je interpretacija sistema,
ne del njegove logike.

---

## 10. Zaključna izjava

> **Vsak poskus preskoka faz pomeni arhitekturno kršitev.  
> Uporabnost nikoli ne sme prehiteti varnosti.**

---

## STATUS

**IMPLEMENTATION PHASES — LOCKED**  
**CANONICAL ORDER DEFINED**

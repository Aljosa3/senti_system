===== ZAČETEK DOKUMENTA =====

# B12 — Rhythm Signals Specification
Version: 1.0  
Status: Governance-level SPEC  
Scope: Sapianta Chat (schat)  
Related phases: B10, B11  

---

## 1. Namen dokumenta

Ta dokument definira **ritmične signale (Rhythm Signals)** v sistemu Sapianta Chat.

Cilj B12 je:
- opazovanje *časovne dinamike uporabe*
- brez vsebinske analize
- brez psiholoških interpretacij
- brez avtomatskih odzivov sistema

Rhythm Signals služijo **razumevanju obremenitve sistema in uporabnika**, ne optimizaciji vedenja.

---

## 2. Viri podatkov

Edini dovoljeni vir podatkov so **dogodki, definirani v B11 (Minimal Observability)**:

- SESSION_STARTED
- IMPLICIT_DRAFT_TRIGGERED
- PROPOSE_ENTERED
- SESSION_ENDED
- SESSION_ABORTED

Sistem **ne beleži vsebine**, dolžine besedila ali pomena vnosa.

---

## 3. Definicija ritma

**Ritem** je zaporedje zgoraj navedenih dogodkov v času, znotraj ene seje (en zagon schat).

Ritem NE pomeni:
- kakovosti razmišljanja
- pravilnosti odločitev
- emocionalnega stanja uporabnika

Ritem pomeni izključno:
- *časovno strukturo interakcije*

---

## 4. Dovoljeni ritmični signali

Iz dogodkov je dovoljeno izpeljati samo naslednje signale:

### 4.1 Trajanje seje
- čas od SESSION_STARTED do SESSION_ENDED ali SESSION_ABORTED

### 4.2 Način zaključka
- normalni izhod (SESSION_ENDED)
- prekinitev (SESSION_ABORTED)

### 4.3 Prisotnost predloga
- ali se je v seji pojavil PROPOSE_ENTERED (da / ne)

### 4.4 Čas do prvega razmišljanja
- čas od SESSION_STARTED do IMPLICIT_DRAFT_TRIGGERED

Ti signali so **opisni**, ne normativni.

---

## 5. Stroge prepovedi (Hard Constraints)

Rhythm Signals se **NE SMEJO** uporabljati za:

- ocenjevanje uporabnika
- prilagajanje UI ali toka brez izrecne odločitve človeka
- avtomatsko spreminjanje vedenja sistema
- sklepanje o čustvih, stresu ali motivaciji
- primerjavo uporabnikov med seboj

Sistem iz ritma **nikoli ne sklepa pomena**.

---

## 6. Odgovornost interpretacije

Vsaka interpretacija Rhythm Signals:
- je izključno človeška
- se dogaja zunaj schat-a
- ni avtomatizirana
- ni trajno shranjena v sistemu

Sapianta Chat ostaja **pasiven opazovalec časa**, ne aktivni interpret.

---

## 7. Razmerje do prihodnjih faz

Ta SPEC:
- omogoča kasnejše faze (npr. B13, B14)
- ne uvaja nobene funkcionalnosti
- ne zahteva nobene implementacije

B12 je **analitična in razmejitvena faza**, ne razvojna.

---

## 8. Zaključek

Rhythm Signals obstajajo zato, da:
- sistem ostane zdrav
- uporaba ostane človeška
- razvoj ostane nadzorovan

Vsak poseg nad tem nivojem zahteva **novo fazo in nov SPEC**.

===== KONEC DOKUMENTA =====

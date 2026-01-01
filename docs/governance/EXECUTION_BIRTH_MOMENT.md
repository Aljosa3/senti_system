# EXECUTION BIRTH MOMENT (EBM)
## Formal Definition & Governance Lock

---

## 1. NAMEN DOKUMENTA

Ta dokument definira **edini dovoljeni trenutek**, ko lahko v sistemu SAPIANTA / SENTI
nastane **Execution Layer**.

Dokument je **zavezujoč**, **nepovraten** in velja kot:
- arhitekturni zakon
- varnostna meja
- auditna referenca

Če pride do konflikta med tem dokumentom in katerokoli kodo ali specifikacijo,
ima **ta dokument absolutno prednost**.

---

## 2. DEFINICIJA EXECUTION BIRTH MOMENT (EBM)

**Execution Birth Moment (EBM)** je:
> enkraten, zavesten in dokumentiran dogodek,  
> s katerim sistem prvič pridobi zmožnost dejanskega izvrševanja.

Pred EBM:
- execution **ne obstaja**
- nobena koda ne sme izvajati učinkov
- nobena komponenta ne sme imeti izvršilnih primitivov

Po EBM:
- execution obstaja **samo v natančno definiranem obsegu**
- execution nima pravice rasti brez novega EBM-dogodka

---

## 3. ABSOLUTNO PRAVILO NEOBSTOJA (PRE-EBM)

Pred izvedbo EBM je **prepovedano**:

- obstoj `Execution` ali `Executor` razredov
- obstoj metod z imeni: `execute`, `apply`, `run`, `commit`
- pisanje v datotečni sistem
- spreminjanje konfiguracij
- zaganjanje OS ukazov
- ustvarjanje modulov
- kakršenkoli trajni stranski učinek

Dovoljene so **izključno**:
- analize
- simulacije
- deklaracije
- zapisi brez učinkov
- povratne informacije (signals, probes)

---

## 4. DOVOLJENE FAZE PRED EBM

Pred EBM so dovoljene naslednje faze:

- FAZA 0 – Core Lock & Non-Execution Contract
- FAZA I – Chat Core (Advisory Only)
- FAZA II – Intent & Capability Declaration
- FAZA III – Mandate Pipeline (brez execution)
- FAZA III.2 – Effect Probe Gate

**FAZA III.2** je izrecno:
- signalna faza
- NE izvršitvena
- NE prehodna
- NE implicitna

---

## 5. POGOJI ZA IZVEDBO EBM (VSI SO OBVEZNI)

EBM se lahko izvede **izključno**, če obstajajo:

1. ✔ Potrjen Intent (strukturiran zapis)
2. ✔ Potrjena Capability Declaration
3. ✔ Jasno opisan namen executiona
4. ✔ Opisana tveganja
5. ✔ Definiran obseg (scope)
6. ✔ Definiran časovni ali funkcionalni limit
7. ✔ Izrecna potrditev lastnika sistema

Če katerikoli pogoj manjka → EBM je **neveljaven**.

---

## 6. SAM DOGODEK EBM

EBM je **enkraten dogodek**, ki:

- ustvari Execution Layer kot kodo
- definira dovoljene izvršilne primitive
- določi meje delovanja
- zapiše auditni zapis

EBM:
- NI avtomatski
- NI implicitni
- NI reverzibilen
- NI razširljiv brez novega EBM

---

## 7. PRAVILA PO EBM

Po EBM velja:

- Execution Layer je strogo omejen
- Vsaka razširitev executiona zahteva:
  - nov mandate
  - nov zapis
  - nov EBM ali razširitveni protokol
- Execution nikoli ne sme postati “default stanje”

---

## 8. JEZIKOVNA IN SEMANTIČNA OGRAJA

Pred EBM je prepovedana uporaba izrazov:
- execution
- executor
- apply
- commit
- run

Dovoljeni izrazi:
- probe
- signal
- requirement
- declaration
- simulation

Ta pravila veljajo za:
- kodo
- dokumentacijo
- komentarje
- loge

---

## 9. AUDIT & DOKAZLJIVOST

Sistem mora biti vedno sposoben odgovoriti na vprašanje:

> “Ali je bil Execution Birth Moment že izveden?”

Če je odgovor:
- **NE** → execution ne sme obstajati
- **DA** → mora obstajati sledljiv zapis

---

## 10. ZAKLJUČEK

Execution Birth Moment je:
- zavestna odločitev
- točka brez povratka
- arhitekturna vest sistema

Brez EBM:
- sistem razmišlja
- sistem svetuje
- sistem ne deluje

Z EBM:
- sistem deluje
- vendar samo v mejah, ki jih je človek izrecno dovolil

---

**KONEC DOKUMENTA**

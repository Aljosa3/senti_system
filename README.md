in **šele potem** nadaljuješ z besedilom.

---

## ✅ POPOLNOMA POPRAVLJENA VERZIJA README.md  
👉 **To je končna, pravilna verzija.**  
Lahko jo **1 : 1 copy/paste** in nehaj skrbeti.

```markdown
# Senti System (Senti OS + Senti Core)

Senti System je modularno ogrodje za gradnjo naprednih AI agentov, namenjeno avtomatizaciji, razvoju, nadzoru, reasoning-u, memory sistemom in real-time upravljanju kompleksnih programskih projektov.

Sistem je zasnovan kot **strogo nadzorovano AI okolje**, kjer so vse odločitve, dovoljenja in zmožnosti agentov eksplicitno definirane in sledljive.

---

## 🔧 Arhitektura

Senti System je zgrajen v treh ključnih plasteh:

### 1️⃣ Senti OS (operacijska plast)
Osnovna varnostna in upravljalska plast sistema.

- varnostni in governance protokoli  
- projektna in razvojna pravila  
- AI razvojni standardi  
- definicije modulov, integracij in dovoljenj  

---

### 2️⃣ Senti Core (jedrni runtime)
Izvedbena in kognitivna plast sistema.

- cognitive loop in decision flow  
- cognitive controller  
- integrity checker  
- runtime pipelines  
- validacija, reminderji in QA mehanizmi  

---

### 3️⃣ Senti Modules
Razširitvena plast z namenskimi moduli.

- senti_reasoning  
- senti_memory  
- senti_validator  
- dodatni moduli v razvoju  

Vsak modul ima jasno definirano vlogo, meje delovanja in integracijska pravila.

---

## 🚀 Namen sistema

Primarni cilji Senti Sistema so:

- avtomatska analiza in korekcija kode  
- nadzor nad AI-generirano vsebino in logiko  
- varnostno preverjanje AI odločitev  
- razširljivost prek modulov in agentov  
- lokalno ali strežniško upravljanje projektov  
- preprečevanje nenadzorovane avtonomije AI  

Sistem je zasnovan za **dolgotrajno uporabo**, sledljiv razvoj in minimalni tehnični dolg.

---

## 🏗 Tehnologije

- Python 3.10+  
- VS Code  
- Git + GitHub  
- modularni Senti agencijski protokol  

---

## 📂 Struktura direktorijev

Projekt je organiziran modularno, z jasno ločitvijo med:
- jedrom sistema  
- operacijsko plastjo  
- moduli  
- dokumentacijo  
- testnimi in razvojno-eksperimentalnimi deli  

Struktura se lahko širi, vendar vedno v skladu z governance pravili Senti OS.

---

## 💬 Sapianta Chat — Canonical Entry Point

**Edini podprt način za zagon Sapianta Chat je:**

```bash
python3 run_sapianta_chat.py
```

Vsi starejši ali alternativni entrypointi (npr. `sapianta_chat.cli`) so **deprecated in namerno blokirani**, da se preprečijo:
- dvoumne zagonske poti  
- napačen izvajalni kontekst  

---

## 🔐 Stability Status

**Status:** STABLE v1.0  
**Scope:** Sapianta Chat — Advisory CLI  

Ta verzija zaklepa:

- kanonični CLI entrypoint  
- advisory-only model brez izvrševanja  
- renderer input contract oblike:

```text
{ intent, policy }
```
Vsaka nadaljnja sprememba mora:

uvesti novo verzijo, ali

ohraniti popolno povratno združljivost, ali

eksplicitno deprecirati ta contract

Ta zaklep zagotavlja deterministično, sledljivo in varno delovanje sistema v tej fazi.


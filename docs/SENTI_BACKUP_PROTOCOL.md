# SENTI BACKUP PROTOCOL  
### (Senti System — Local Development Version)

Ta dokument določa standardiziran backup sistem, ki se uporablja v lokalnem razvojnem okolju Senti System (VS Code + lokalna datotečna struktura).

Cilj:
- zagotoviti neprekinjeno varnost projektne kode
- omogočiti takojšnje “roll-back” stanje, če AI ali človek naredi napako
- ohraniti verzijsko zgodovino pomembnih razvojnih celot
- avtomatsko sinhronizirati backupe v Nextcloud (lokalni klient)

---

# 1. KDAJ IZVESTI BACKUP

Backup se izvede, ko je zaključena katerakoli večja celota:

### 1.1 Razvojni cikli
- A1 — UX layer  
- A2 — Command Engine  
- A3 — Model Switching  
- A4 — Senti Reasoning  
- A5 — Senti Memory  
- A6 — Cognitive Loop  
- A7 — Autonomous Agent  

### 1.2 Zaključeni moduli
- Senti Trading  
- Senti Design  
- Senti Docs  
- Senti Core Security  
- Senti Core APIs  

### 1.3 Kritične situacije
- pred refaktorjem  
- pred množičnimi AI-generiranimi spremembami  
- pred reorganizacijo map  
- pred prehodom na strežnik  

---

# 2. KAJ SE BACKUPIRA

Ker lokalno delamo samo s projektom **SENTI_SYSTEM**, backup vključuje:

```
SENTI_SYSTEM/
│
├── .claude/
├── .git/
├── .github/
├── config/
├── docs/
├── modules/
├── scripts/
├── senti_core/
├── senti_os/
├── tests/
├── .gitignore
├── CLAUDE.md
├── CONTRIBUTING.md
├── README.md
└── VERSION
```

Vključijo se vse datoteke:  
- `.py`, `.sh`, `.md`, `.json`, `.yaml`, `.txt`  
- tudi necommitani “unstaged changes”  

---

# 3. KAJ SE NE SME BACKUPIRATI

```
__pycache__/
*.log
*.lock
node_modules/
.env
*.pem
*API*
*SECRET*
*KEY*
```

---

# 4. KAKO SE USTVARI BACKUP (LOKALNO)

Backup se generira v mapi:

```
SENTI_SYSTEM/backups/
```

### 4.1 Ime backup datoteke

Format:

```
YYYY-MM-DD_HH-MM_senti_backup__REASON.zip
```

Primer:

```
2025-11-28_18-22_senti_backup__A3_finished.zip
```

### 4.2 Ukaz za ustvarjanje ZIP arhiva

Če si v mapi *nad* SENTI_SYSTEM:

```bash
zip -r "SENTI_SYSTEM/backups/${BACKUP_NAME}.zip" \
    SENTI_SYSTEM \
    -x "*/__pycache__/*" "*.env" "*API*" "*KEY*" "*.pem"
```

---

# 5. NEXTCLOUD AVTOMATSKI BACKUP (LOKALNI)

Nextcloud ima lokalno mapo, npr.:

```
~/Nextcloud/
```

V njej ustvarimo mapo:

```
~/Nextcloud/Senti_Backups/
```

Ta mapa se *samodejno* sinhronizira v oblak → ni treba uporabljati WebDAV.

### 5.1 Kopiranje backup ZIP datoteke v Nextcloud

Po ustvarjanju ZIP-a:

```bash
cp "SENTI_SYSTEM/backups/${BACKUP_NAME}.zip" \
   "$HOME/Nextcloud/Senti_Backups/"
```

### 5.2 (Opcijsko) avtomatizacija preko skripte

Ustvarimo skripto:

```
SENTI_SYSTEM/scripts/upload_backup.sh
```

Vsebina:

```bash
#!/usr/bin/env bash

BACKUP_FILE="$1"

NEXTCLOUD_DIR="$HOME/Nextcloud/Senti_Backups"

mkdir -p "$NEXTCLOUD_DIR"

cp "$BACKUP_FILE" "$NEXTCLOUD_DIR"

echo "Backup uploaded to Nextcloud: $NEXTCLOUD_DIR"
```

Naredimo izvršljivo:

```bash
chmod +x SENTI_SYSTEM/scripts/upload_backup.sh
```

Uporaba:

```bash
./SENTI_SYSTEM/scripts/upload_backup.sh SENTI_SYSTEM/backups/IME_ZIPa.zip
```

---

# 6. HASH VERIFIKACIJA (NEOBVEZNO)

```bash
shasum -a 256 "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
```

---

# 7. RESTORE PROTOKOL (LOKALNO)

## 7.1 Razpakiranje v novo mapo
Nikoli ne piši čez obstoječi projekt.

```bash
unzip senti_backup.zip -d Senti_Restore/
```

## 7.2 Primerjava z orodjem **VS Code diff**
- v levem oknu: trenutni projekt  
- v desnem: `Senti_Restore/`  
- izberi datoteke, ki jih želiš povrniti

## 7.3 Čist rollback
Če želiš povsem nov začetek:

1. izbriši celotno mapo `SENTI_SYSTEM`  
2. iz ZIP restora jo postavi nazaj  
3. ponovno namesti `.git` (če želiš verzioniranje)

---

# 8. AI PROTOKOL ZA BACKUP

Ko uporabnik reče:

> “Ta celota je zaključena.”

ChatGPT mora vedno:

### 1) Predlagati ime backupa  
### 2) Generirati ZIP ukaz  
### 3) Generirati Nextcloud upload ukaz  
### 4) Narediti preverjanje občutljivih datotek  
### 5) Vprašati:  

```
Ali izvedem backup?
```

---

# 9. ZAKLJUČEK

Ta protokol je obvezni del Senti System lokalnega razvoja.  
Dokler ni vzpostavljen strežnik, se backup izvaja tukaj – v lokalnem okolju s prenosom na Nextcloud.

Ko bo na voljo strežnik, bomo datoteko nadgradili na:

- remote backups  
- cron job  
- server-side encryption  
- multi-location redundancy  


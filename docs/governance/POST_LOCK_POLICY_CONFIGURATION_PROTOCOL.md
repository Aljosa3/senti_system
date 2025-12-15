# POST-LOCK POLICY CONFIGURATION PROTOCOL

Version: 1.0
Status: ACTIVE AFTER CORE LOCK
Applies from: FAZA 60 (CORE LOCK)
Authority: System Governance Framework

---

## 1. NAMEN DOKUMENTA

Ta dokument določa edini dovoljeni način prilagajanja pravil uporabe,
etičnih omejitev in distribucijskih modelov sistema po zaklepu jedra (CORE LOCK).

Dokument zagotavlja, da se sistem lahko prilagaja prihodnjim kontekstom
brez poseganja v jedro, arhitekturo ali varnostne mehanizme.

---

## 2. TEMELJNO NAČELO (NEPREKLICNO)

Jedro sistema (CORE) je po zaklepu nespremenljivo.

Po FAZI 60:
- ni dovoljenih sprememb izvršilne logike,
- ni dovoljenih razširitev zmožnosti,
- ni dovoljenih izjem ali obvodov.

Vse spremembe vedenja sistema so dovoljene izključno preko
konfiguracijskih in upravljalskih plasti, definiranih v tem dokumentu.

---

## 3. ARHITEKTURNA RAZMEJITEV PO ZAKLEPU

Sistem je po zaklepu razdeljen na tri strogo ločene plasti.

### 3.1 CORE (ZAKLENJENO)

CORE vključuje:
- odločilne mehanizme,
- varnostne pregrade,
- mehanizme zavrnitve,
- preverjanje pravic,
- logiranje in revizijo,
- interpretacijo pravil.

CORE:
- ne vsebuje vsebine pravil,
- ne pozna distribucije,
- ne pozna konteksta uporabe,
- izvaja izključno validirano interpretacijo zunanjih pravil.

CORE je trajno nespremenljiv.

---

### 3.2 POLICY LAYER (KONFIGURABILEN PO ZAKLEPU)

POLICY LAYER je podatkovna plast brez lastne izvršilne moči.

Vsebuje lahko:
- definicije dovoljenih in prepovedanih namenov uporabe,
- razrede etične občutljivosti,
- pragove tveganja,
- omejitve agresivnih ali dual-use scenarijev,
- zahteve za identiteto, soglasje ali revizijo.

POLICY LAYER:
- se lahko spreminja po zaklepu,
- ne sme spreminjati odločilne logike,
- ne sme dodajati novih zmožnosti,
- je vedno interpretiran izključno preko CORE.

---

### 3.3 DISTRIBUTION PROFILE (ODPRTA PLAST)

Distribution Profile določa:
- ciljno skupino uporabnikov,
- kontekst uporabe,
- aktivni POLICY LAYER,
- operativne omejitve.

Distribucijski modeli niso del zaklepa in se lahko razvijajo neodvisno,
dokler uporabljajo nespremenjen CORE in veljaven POLICY LAYER.

---

## 4. DOVOLJENE SPREMEMBE PO ZAKLEPU

Po FAZI 60 je dovoljeno:
- spreminjati vsebino POLICY LAYER,
- dodajati ali prilagajati distribucijske profile,
- zaostrovati etične omejitve,
- prilagajati dovoljene kontekste uporabe.

Ni dovoljeno:
- spreminjati CORE,
- obiti interpretacijo pravil,
- uvajati začasne ali skrite izjeme,
- dodajati nove zmožnosti sistema.

---

## 5. UPRAVLJALSKA ODGOVORNOST

Vsaka sprememba POLICY ali DISTRIBUTION mora:
- imeti jasno opredeljen namen,
- biti časovno sledljiva,
- imeti odgovorno osebo ali organ,
- biti revizijsko preverljiva.

---

## 6. VLOGA AVTORJA IN DEDIČEV

Avtor sistema:
- določi začetni POLICY okvir,
- določi pravila upravljanja po zaklepu,
- zaklene jedro sistema.

Dediči ali skrbniki:
- ne pridobijo lastništva jedra,
- delujejo kot varuhi pravil uporabe,
- so dolžni spoštovati ta protokol.

Kršitev tega protokola pomeni izgubo upravne legitimnosti sistema.

---

## 7. KONČNA IZJAVA

Jedro je zaklenjeno.
Pravila uporabe so prilagodljiva.
Odgovornost je sledljiva.

END OF DOCUMENT

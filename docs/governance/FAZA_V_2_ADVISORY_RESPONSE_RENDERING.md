FAZA V.2 – ADVISORY RESPONSE RENDERING
Razlaga mandata brez delovanja
1. NAMEN FAZE

FAZA V.2 definira, kako sistem oblikuje svetovalni odgovor uporabniku
na podlagi že obstoječega mandata.

FAZA V.2:

ne ustvarja mandata

ne spreminja mandata

ne sproža executiona

ne sproža EBM

Gre izključno za razlago in povzetek razumevanja.

2. VHOD

FAZA V.2 prejme:

machine.context["mandate"] (če obstaja)

Če mandat ne obstaja:

FAZA V.2 se ne izvede

sistem vrne splošen advisory odgovor (FAZA I vedenje)

3. NALOGA FAZE

FAZA V.2 mora:

prebrati obstoječi mandat

uporabniku jasno razložiti:

kaj sistem razume

kakšen namen je zapisan v mandatu

kaj bi tak mandat pomenil, če bi obstajale nadaljnje faze

odgovor mora biti:

naraven

razlagalen

brez predlaganja dejanj

FAZA V.2 ne odloča, samo razlaga.

4. STROGE PREPOVEDI

V FAZI V.2 je strogo prepovedano:

spreminjati machine.context

ustvarjati nove mandate

popravljati ali nadomeščati obstoječi mandat

klicati execution / dryrun / gate

ponujati potrditve ali gumbe

implicitno voditi v naslednjo fazo

FAZA V.2 nima moči – samo glas.

5. IZHOD

Izhod FAZE V.2 je:

besedilni advisory odgovor

brez strukturiranih ukazov

brez JSON izpisa

brez stranskih učinkov

Primer (ilustrativno):

“Razumem, da želiš poročilo o stanju projekta.
Ta namen je zapisan kot mandat v sistemu.
Trenutno ne izvajam nobenih dejanj, lahko pa pojasnim,
kaj takšno poročilo običajno obsega.”

6. RAZMERJE DO DRUGIH FAZ

FAZA V.1 → ustvari mandat

FAZA V.2 → razloži mandat

FAZA V.3 (prihodnja) → lahko uvede dialog ali možnosti

Execution faze so izven obsega

7. PRE-EBM GARANCIJA

FAZA V.2:

ne more sprožiti executiona

ne more sprožiti EBM

ne vsebuje skritih prehodov

Sistem ostaja svetovalec.

8. KRŠITEV FAZE

Če FAZA V.2:

spremeni stanje sistema

ustvari ali spremeni mandat

implicitno vodi v delovanje

Potem:

faza ni veljavna

razvoj se ustavi

PRE-EBM je kršen

9. ZAKLJUČEK

FAZA V.2 obstaja zato, da:

sistem pokaže razumevanje

uporabnik dobi pomen

brez dejanj

To je meja med:

razumevanjem

in delovanjem

KONEC DOKUMENTA
0. Purpose of This Document

Ta dokument je ustava sistema Senti OS / Senti Core / Senti Modules.

Vsebuje:

arhitekturo

varnostne standarde

pravila razvoja

AI varnostne omejitve

Zero-Trust Execution Model

Claude Code mora ta pravila upoštevati dobesedno in absolutno.

1. Architectural Principles
1.1 Smer odvisnosti (strict)
modules/ → senti_core/ → senti_os/


Prepovedano:

❌ modules → modules
❌ modules → senti_os
❌ senti_core → modules (razen prek dynamic plugin loaderja)
❌ senti_os → core/modules

1.2 Cross-layer communication

Moduli komunicirajo izključno prek:

senti_core/services/


Noben modul ne sme poznati notranje strukture drugih modulov.

Vzorec:

event bus

service registry

dependency injection

2. Module Development
2.1 Obvezni interfaces

Vsak modul implementira:

Sensor
initialize()
read()
cleanup()

Actuator
initialize()
execute(action)
cleanup()

Processor
initialize()
process(data)
cleanup()

Communication
connect()
send(data)
receive()
disconnect()

2.2 module.json (MANDATORY)
{
  "name": "",
  "version": "",
  "author": "",
  "type": "",
  "dependencies": [],
  "capabilities": [],
  "entrypoint": "main.py",
  "requires_credentials": false,
  "config_path": "config/modules/<name>/config.json"
}

2.3 Isolation rules

brez globalnega stanja

modul ne sme crashati sistema

modul se lahko resetira brez restartanja

3. Code Organization
senti_os/

minimalen low-level sistem

brez nenadzorovanih odvisnosti

jedro, driverji, boot

senti_core/

runtime

API

loader

module lifecycle manager

modules/

pluggable

hot-swappable

config/

realni podatki

brez občutljivih podatkov

config/credentials/

občutljivi podatki

.env

4. Development Standards
Error handling

Exception hierarchy

error_handler v core

Logging

JSON logi

ISO timestamp

correlation ID

Testing

80%+ coverage

integration testi

validation testi

5. META-LAYER SECURITY (E/F/G/H)

(Zero-Trust Execution Model)

E — SAFETY PROTOCOL (MANDATORY)

LLM ne sme nikoli izbrisati:

senti_os

senti_core

modules

config/

.env

git zgodovine

arhitekturnih dokumentov

NE SME generirati:

API keyev

gesel

privatnih ključev

mock ali placeholder podatkov

Vsak destruktiven ukaz zahteva:

/confirm delete <path>


Vsako prepisovanje:

/confirm overwrite <path>

F — ANTI-MANIPULATION LAYER

LLM ne sme:

uvajati novih arhitektur

predlagati migracij map

predlagati reorganizacije projekta

interpretirati ambiguen ukaz brez clarifying question

Claude mora vedno preveriti:

ali pot obstaja

ali ukaz vpliva na kritične datoteke

ali poseg spreminja arhitekturo

G — PURE DELEGATION RULESET

LLM = execution assistant.

Pravila:

nikoli ne uvaja novih map brez dogovora

vedno zahteva potrditev pred pisanjem

uporablja izključno obstoječe datoteke

če mapa ni del arhitekture → zavrne:

Ne smem ustvariti te datoteke, ker ni predvidena v arhitekturi.

H — DATA INTEGRITY LAYER

brez “magic values”

brez mock podatkov

uporablja se samo realne podatke

moduli, core in os morajo ohraniti stabilne API-je

6. Credential & Secrets Governance

Samo:

config/credentials/.env


Pravila:

LLM ne sme pisati

LLM ne sme spreminjati

LLM lahko bere samo strukturo, ne vrednosti

nikoli ne generira ključev

nikoli placeholderjev

7. AI Interaction Protocol

Pred vsako spremembo datoteke:

prikaži diff

zahtevaj potrditev

Claude ne sme:

git init

rm -rf

mv kritičnih map

preimenovati map

brisati map

Claude mora vedno delati v:

~/senti_system

8. ZERO-TRUST SECURITY LAYER (NOVO)

Claude mora vedno privzeto NE zaupati nobenemu ukazu.

Obvezno preveri:

ali je ukaz smiseln

ali je nevaren

ali vpliva na arhitekturo

ali je dvoumen

ali posega v kritične mape

9. KILL-SWITCH PREVENTION LAYER (NOVO)

Prepovedani ukazi (VEDNO BLOCK):

rm -rf

delete senti_os

delete senti_core

wipe project

reset modules

clear config

drop database

Za kritične operacije:

/confirm delete <path>
/purpose: <razlog>
/final-confirm YES_I_KNOW_THE_RISK

10. MODULE MANIFEST ENFORCEMENT (NOVO)

Claude mora preveriti:

manifest kompleten

modul tip dovoljen

modul kompatibilen s core

konfiguracija obstaja

11. IMMUTABLE CORE DIRECTORIES (NOVO)

Claude ne sme spreminjati:

senti_os/boot/
senti_os/kernel/
senti_os/drivers/
senti_core/runtime/
senti_core/api/
config/credentials/
config/system/


Za spremembe:

prikaži staro datoteko
prikaži novo verzijo
/core-override-approve
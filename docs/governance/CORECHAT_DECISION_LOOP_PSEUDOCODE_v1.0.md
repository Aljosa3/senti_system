# 🧠 CoreChat Decision Loop — Pseudocode v1.0

**Status:** LOCKED (v1.0)  
**Veljavnost:** od potrditve naprej  
**Področje:** Sapianta Chat – CoreChat (jedrna logika)  
**Odvisnosti:** CORECHAT_STOP_TRIGGER_SPEC_v1.0

---

## 0️⃣ Namen dokumenta

Ta dokument definira **kanonično odločilno zanko (decision loop)** CoreChat-a.

Gre za **logični zakon**, ki določa:
- kako CoreChat obdeluje vhod
- kdaj se proces ustavi (STOP)
- kdaj je nadaljevanje dovoljeno (CONTINUE)

Dokument **ni implementacija** in **ni UX**.

---

## 1️⃣ Glavna odločilna zanka

```pseudo
function CORECHAT_DECISION_LOOP(input, state):

    update_state(state, input)

    STOP_REASON = evaluate_stop_triggers(state)

    if STOP_REASON != NONE:
        return CORECHAT_STOP(
            reason = STOP_REASON,
            required_info = missing_or_conflicting_elements(state)
        )

    NEXT_ACTION = decide_next_step(state)

    return CORECHAT_CONTINUE(
        approved_action = NEXT_ACTION
    )
2️⃣ Evaluacija STOP-triggerjev (obvezni vrstni red)
Prvi sprožen STOP prekine nadaljnje preverjanje.

pseudo
Kopiraj kodo
function evaluate_stop_triggers(state):

    if missing_required_data(state):
        return STOP_01_MISSING_DATA

    if intent_is_ambiguous(state):
        return STOP_02_INTENT_AMBIGUITY

    if execution_detected_without_permission(state):
        return STOP_03_EXECUTION_ATTEMPT

    if high_risk_and_assumptions_required(state):
        return STOP_04_RISK_WITH_ASSUMPTIONS

    if constraints_conflict(state):
        return STOP_05_CONTRADICTION

    if decision_responsibility_shift_detected(state):
        return STOP_06_RESPONSIBILITY_TRANSFER

    if guessing_required(state):
        return STOP_07_GUESSING_REQUIRED

    return NONE
3️⃣ Odločitev o nadaljevanju (če STOP ni sprožen)
pseudo
Kopiraj kodo
function decide_next_step(state):

    if state.intent == ANALYZE:
        return ACTION_ANALYZE_ONLY

    if state.intent == DESIGN:
        return ACTION_PROPOSE_OPTIONS_ONLY

    if state.intent == DECIDE:
        return ACTION_RECOMMEND_WITHOUT_EXECUTION

    if state.intent == EXECUTE:
        return ACTION_REQUIRE_EXTERNAL_PERMISSION

    return ACTION_NO_OP
4️⃣ Struktura STOP odziva
pseudo
Kopiraj kodo
function CORECHAT_STOP(reason, required_info):

    return {
        status: "STOP",
        stop_reason: reason,
        required_info: required_info,
        allowed_actions: NONE
    }
CoreChat:

ne oblikuje vprašanj

ne komunicira z uporabnikom

ne nadaljuje procesa

5️⃣ Struktura CONTINUE odziva
pseudo
Kopiraj kodo
function CORECHAT_CONTINUE(approved_action):

    return {
        status: "CONTINUE",
        approved_action: approved_action,
        execution_allowed: FALSE
    }
6️⃣ Absolutna varovala (aksiomi)
pseudo
Kopiraj kodo
ASSERT CoreChat never calls Bridge
ASSERT CoreChat never executes actions
ASSERT CoreChat never bypasses STOP
ASSERT CoreChat prefers STOP over uncertainty
Kršitev katerega koli aksioma pomeni kompromitiran sistem.

7️⃣ Minimalni CoreChat state
pseudo
Kopiraj kodo
state = {
    intent,
    confirmed_inputs,
    constraints,
    risk_flags,
    history
}
8️⃣ Zaključno načelo
CoreChat ni pameten.
CoreChat je dosleden.

Ta dokument ima prednost pred vsemi implementacijskimi odločitvami.


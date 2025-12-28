"""HumanChat Adapter - Canonical Response Layer v1.0"""

from corechat.core_decision_loop import CORECHAT_DECISION_LOOP


STOP_RESPONSES = {
    "STOP_01_MISSING_DATA": "Da bo moj predlog rešitve res smiselen, potrebujem še nekaj informacij.",
    "STOP_02_INTENT_AMBIGUITY": "Najprej bom na kratko povzel možnosti in njihove razlike, potem pa lahko skupaj pogledava, kaj je zate najbolj smiselno.",
    "STOP_03_EXECUTION_ATTEMPT": "Preden greva naprej, bi rad preveril, ali želiš to samo pregledati ali tudi dejansko uporabiti.",
    "STOP_04_RISK_WITH_ASSUMPTIONS": "Da bo moj predlog rešitve res smiselen, potrebujem še nekaj informacij.",
    "STOP_05_CONTRADICTION": "Da bo moj predlog rešitve res smiselen, potrebujem še nekaj informacij.",
    "STOP_06_RESPONSIBILITY_TRANSFER": "Lahko ti priporočim možnost in jo obrazložim, odločitev pa mora biti še vedno tvoja.",
    "STOP_07_GUESSING_REQUIRED": "Da bo moj predlog rešitve res smiselen, potrebujem še nekaj informacij.",
}


def handle_user_message(user_text, state):
    """Handle user message and return response."""
    input_data = parse_user_input(user_text, state)

    result = CORECHAT_DECISION_LOOP(input_data, state)

    if result["status"] == "STOP":
        return format_stop_response(result, state)

    return format_continue_response(result, state)


def parse_user_input(user_text, state):
    """Parse user input into CoreChat format."""
    input_data = {}

    intent = extract_intent(user_text)
    if intent:
        input_data["intent"] = intent

    return input_data


def extract_intent(user_text):
    """Extract intent from user text."""
    text_lower = user_text.lower()

    if any(word in text_lower for word in ["analyze", "explain", "what is", "tell me about"]):
        return "ANALYZE"

    if any(word in text_lower for word in ["design", "how could", "options", "possibilities"]):
        return "DESIGN"

    if any(word in text_lower for word in ["recommend", "suggest", "should i", "what do you think"]):
        return "DECIDE"

    if any(word in text_lower for word in ["do it", "execute", "run", "implement", "create"]):
        return "EXECUTE"

    return None


def format_stop_response(result, state):
    """Format STOP response."""
    stop_reason = result["stop_reason"]
    reply_text = STOP_RESPONSES.get(stop_reason, STOP_RESPONSES["STOP_01_MISSING_DATA"])

    return {
        "reply_text": reply_text,
        "status": "STOP",
        "required_input": result["required_info"],
        "state": state
    }


def format_continue_response(result, state):
    """Format CONTINUE response."""
    approved_action = result["approved_action"]

    reply_text = generate_continue_text(approved_action)

    return {
        "reply_text": reply_text,
        "status": "CONTINUE",
        "required_input": None,
        "state": state
    }


def generate_continue_text(approved_action):
    """Generate text for CONTINUE response."""
    if approved_action == "ACTION_ANALYZE_ONLY":
        return "Analiziram lahko informacije in ti povem, kaj sem ugotovil."

    if approved_action == "ACTION_PROPOSE_OPTIONS_ONLY":
        return "Predstavim lahko več možnosti in njihove razlike."

    if approved_action == "ACTION_RECOMMEND_WITHOUT_EXECUTION":
        return "Priporočim lahko smer, a odločitev mora biti tvoja."

    if approved_action == "ACTION_REQUIRE_EXTERNAL_PERMISSION":
        return "Za izvedbo potrebujem tvojo jasno potrditev."

    return "Nadaljujem lahko, ko bo jasno, kaj želiš."

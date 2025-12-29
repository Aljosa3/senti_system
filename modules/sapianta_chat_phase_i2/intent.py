# INTENT RULES
# QUESTION: kaj, zakaj, kako, ali
# REQUEST: naredi, zaženi, ustvari
# PLAN: koraki, faze, plan
# META: kako deluje, kaj znaš
# UNKNOWN: vse ostalo

def detect_intent(text: str) -> str:
    text = text.lower().strip()

    if not text:
        return "UNKNOWN"

    if any(word in text for word in ["kaj", "zakaj", "kako", "ali"]):
        return "QUESTION"

    if any(word in text for word in ["naredi", "zaženi", "ustvari"]):
        return "REQUEST"

    if any(word in text for word in ["koraki", "faze", "plan"]):
        return "PLAN"

    if any(word in text for word in ["kako deluje", "kaj znaš"]):
        return "META"

    return "UNKNOWN"

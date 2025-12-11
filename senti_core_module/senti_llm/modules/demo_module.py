"""
FAZA 36.3 — DEMO MODUL

To je prvi demonstracijski modul v Senti OS, ki dokazuje delovanje
dinamičnega nalaganja modulov (FAZA 36).

Modul vsebuje:
- MODULE_MANIFEST z vsemi zahtevanimi polji
- DemoModule class kot entrypoint
- run(payload) metodo, ki vrne strukturiran rezultat
"""

# -----------------------------------------------------------
#  FAZA 36 — MANIFEST
# -----------------------------------------------------------
MODULE_MANIFEST = {
    "name": "demo",
    "version": "1.0.0",
    "entrypoint": "DemoModule",
    "phase": 36,  # Modul je kompatibilen z FAZA 36
}


# -----------------------------------------------------------
#  DEMO MODULE IMPLEMENTACIJA
# -----------------------------------------------------------
class DemoModule:
    """
    Demo modul uporablja RuntimeContext, ki ga prejme od Senti OS runtime.
    """

    def __init__(self, context):
        self.context = context

    def run(self, payload: dict):
        """
        Glavna metoda za izvajanje modula.
        Vrne strukturiran demo rezultat.
        """

        return {
            "ok": True,
            "module": "demo",
            "message": "Demo modul je bil uspešno izveden!",
            "payload_received": payload,
            "context": {
                "prompt": getattr(self.context, "prompt", None),
                "capability": getattr(self.context, "capability", None),
            }
        }

"""
EventBus — Senti Core Runtime Service
Location: senti_core/services/event_bus.py

Centralni mehanizem za komunikacijo med komponentami v Senti Core.
Uporabljajo ga:
- Cognitive Controller
- Cognitive Loop
- Runtime Loader (kasneje)
- Senti OS (prek system events)
- Moduli (prek registriranih handlerjev)

EventBus omogoča:
✔ publish(event_type, payload)
✔ subscribe(event_type, handler)
✔ unsubscribe(event_type, handler)
✔ varno izvrševanje handlerjev
"""

from typing import Callable, Dict, List


class EventBus:
    """
    Preprost, varen, sinhroniziran Event Bus za Senti Core.
    """

    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}

    # =====================================================
    # REGISTRACIJA HANDLERJEV
    # =====================================================

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Registrira poslušalca za to vrsto dogodka.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Odstrani handler, če obstaja.
        """
        if event_type not in self.handlers:
            return

        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    # =====================================================
    # OBJAVA DOGODKA
    # =====================================================

    def publish(self, event_type: str, payload: dict) -> None:
        """
        Sproži dogodek: izvede vse registrirane handlerje.
        """
        listeners = self.handlers.get(event_type, [])

        for handler in listeners:
            self._safe_execute(handler, payload)

    # =====================================================
    # VARNI KLIC
    # =====================================================

    def _safe_execute(self, handler: Callable, payload: dict):
        """
        Izvede handler v zaščitenem try/except bloku.
        """
        try:
            handler(payload)
        except Exception as e:
            print(f"[EventBus][ERROR] Handler failed: {str(e)}")

    # =====================================================
    # DIAGNOSTIKA
    # =====================================================

    def list_handlers(self) -> dict:
        """
        Vrne mapo event_type → seznam handlerjev
        Za debug/testing.
        """
        return {
            event: [h.__name__ for h in handlers]
            for event, handlers in self.handlers.items()
        }

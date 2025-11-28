"""
Task Routing Map — Senti Core Runtime
Location: senti_core/runtime/task_routing_map.py

Naloga:
- definira mapo task_type → handler funkcija
- omogoča registracijo novih nalog
- zagotavlja varen dostop do handlerjev
- sodeluje s Cognitive Controllerjem

To JE centralna “mapa nalog” Senti Systema.
"""

from typing import Callable, Dict, List


class TaskRoutingMap:
    """
    Centralizirano upravljanje task → handler mapiranja.
    """

    def __init__(self):
        # osnova: prazna mapa, handlerji se registrirajo postopno
        self.task_map: Dict[str, Callable] = {}

    # =====================================================
    # REGISTRACIJA
    # =====================================================

    def register(self, task_type: str, handler: Callable):
        """
        Registrira handler za določeno vrsto naloge.
        Primer:
            task_router.register("system_health", handler_function)
        """
        self.task_map[task_type] = handler

    # =====================================================
    # PRIDOBITEV HANDLERJA
    # =====================================================

    def get_handler(self, task_type: str) -> Callable:
        """
        Vrne referenco na handler, če obstaja.
        """
        return self.task_map.get(task_type, None)

    def exists(self, task_type: str) -> bool:
        """
        Preveri, ali je naloga registrirana.
        """
        return task_type in self.task_map

    # =====================================================
    # DIAGNOSTIKA
    # =====================================================

    def list_tasks(self) -> Dict[str, str]:
        """
        Vrne mapo task_type → ime handler funkcije.
        """
        return {
            task: handler.__name__
            for task, handler in self.task_map.items()
        }


# =========================================================
# PRIVZETA INSTANCE (uporablja jo Cognitive Controller)
# =========================================================

task_router = TaskRoutingMap()

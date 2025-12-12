"""
FAZA 45 — Minimal IntegrityStore
--------------------------------
Ta verzija NE piše datotek in ne uporablja diska.
"""


class IntegrityStore:
    def __init__(self, store_path: str):
        self.store_path = store_path
        # minimalni memory store
        self._store = {}

    def get_entry(self, module_name: str):
        return self._store.get(module_name)

    def update_entry(self, module_name: str, data: dict):
        self._store[module_name] = data

"""
FAZA 45 — Minimal IntegrityManager
----------------------------------
Ta verzija NE izvaja SHA256, baseline ali file hashing.

Namen:
- omogoča uvoz brez circular import
- vrača stabilne, predvidljive statuse
- omogoča FAZA 45 validatorju da se izvede
"""

from .integrity_exceptions import (
    IntegrityViolation,
    MissingIntegrityData,
)


class IntegrityManager:
    def __init__(self, strict_mode=True):
        self.strict_mode = strict_mode
        # minimalen pomnilniški "store"
        self._memory_store = {}

    # -------------------------------------------------------------
    # Minimalna verzija — modul mora biti v _memory_store, sicer manjkajoča integriteta
    # -------------------------------------------------------------
    def ensure_integrity_compliance(self, module_name: str, module_path: str, module_dir: str):
        """
        Če modul ni v memory_store → MissingIntegrityData.
        Če je → vrnemo verified.
        """

        if module_name not in self._memory_store:
            raise MissingIntegrityData(f"Missing baseline for {module_name}")

        # sovpada s STRICT ONLY mode → verified
        return {
            "compliant": True,
            "action": "verified",
            "details": {},
        }

    # -------------------------------------------------------------
    # Minimalni API za module_loader STRICT ONLY
    # -------------------------------------------------------------
    def update_integrity(self, module_name: str, manifest_path: str, module_path: str):
        """
        Minimalna implementacija: zabeležimo modul kot 'verified'.
        (STRICT ONLY mode te funkcije normalno NE uporablja)
        """
        self._memory_store[module_name] = {"status": "verified"}

    def verify_manifest(self, *args, **kwargs):
        return True

    def verify_files(self, *args, **kwargs):
        return True

    # -------------------------------------------------------------
    # Utility za bodoče faze (ni uporabljen v minimalnem režimu)
    # -------------------------------------------------------------
    def get_entry(self, module_name: str):
        return self._memory_store.get(module_name)

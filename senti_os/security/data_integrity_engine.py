from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from senti_os.security.security_events import SecurityEvents


class DataIntegrityViolation(Exception):
    """Critical violation of global data integrity rules."""


class DataIntegrityEngine:
    """
    Data Integrity Engine (FAZA 7)
    ==============================

    Globalni OS-level mehanizem, ki zagotavlja:

    - uporaba izključno realnih podatkov
    - blokada synthetic / mock / artificial podatkov
    - validacija vsakega vira podatkov
    - generiranje DATA_INTEGRITY_VIOLATION OS eventov
    - integracija s:
        • ServiceManager
        • AICommandProcessor (HARD BLOCK)
        • AIRecoveryPlanner (NO-ACTION-MODE)
        • SystemEvents
        • SecurityEvents (FAZA 8)

    Engine NE generira popravkov, NE dela fallbackov,
    NE nadomešča podatkov in NE sklepa o manjkajočih podatkih.
    """

    # ============================================================
    # INIT
    # ============================================================

    def __init__(self, logger=None):
        self._log = logger or logging.getLogger(__name__)

        # FAZA 7 globalni status
        self._integrity_block_active: bool = False
        self._last_violation_details: Optional[Dict[str, Any]] = None

        # FAZA 8 – SecurityEvents integracija
        self._events = SecurityEvents()

    # ============================================================
    # JAVNI API
    # ============================================================

    def check_source(self, source_details: Dict[str, Any], events=None) -> None:
        """
        Glavni entrypoint — preveri veljavnost vira.
        """

        self._validate_schema(source_details)

        # 1. Najprej blokada manjkajočih podatkov
        if source_details.get("missing", False):
            self._trigger_violation(
                "Realni podatki manjkajo.",
                source_details,
                events,
            )

        # 2. Prepoved synthetic podatkov
        if not source_details.get("is_real", False):
            self._trigger_violation(
                "Nerealni podatki niso dovoljeni.",
                source_details,
                events,
            )

        # 3. Prepoved simuliranih, predvidenih ali generiranih vrednosti
        if source_details.get("synthetic", False) is True:
            self._trigger_violation(
                "Synthetic podatki niso dovoljeni.",
                source_details,
                events,
            )

        if source_details.get("mock", False) is True:
            self._trigger_violation(
                "Mock podatki niso dovoljeni.",
                source_details,
                events,
            )

        # 4. Prepoved environmentov, ki niso realni
        if source_details.get("environment") == "synthetic":
            self._trigger_violation(
                "Synthetic environment ni dovoljen.",
                source_details,
                events,
            )

        # Če smo prišli do sem, podatki so realni in dovoljeni
        return None

    def verify_real_data(self, source_details: Dict[str, Any]) -> None:
        """
        Retrokompatibilna metoda — ostane, a se razširi.
        """
        # FAZA 8 – emit varnostni incident
        if not source_details.get("is_real", False):
            self._events.data_integrity_violation(source_details)

        self.check_source(source_details, events=None)

    def block_if_missing(self, source_details: Dict[str, Any]) -> None:
        """Retro metoda — preusmerjena v check_source()."""
        if source_details.get("missing", False):
            # FAZA 8 – varnostno opozorilo
            self._events.manager_alert("Realni podatki manjkajo — uporabnik mora zagotoviti podatke.")

        self.check_source(source_details)

    # ============================================================
    # HELPERI
    # ============================================================

    def _validate_schema(self, source_details: Dict[str, Any]) -> None:
        """
        Preveri ali source_details vsebuje minimalne elemente.
        """

        required_fields = {"type", "origin", "is_real"}

        missing = required_fields - set(source_details.keys())
        if missing:
            raise DataIntegrityViolation(
                f"Source metadata schema invalid — manjka: {missing}. "
                "Sistem zahteva popolne metapodatke za vir."
            )

        # uvedemo stricten typ-check: type mora biti eden od dovoljenih
        valid_types = {"api", "database", "file", "sensor", "external_system", "os_boot", "core_boot"}

        if source_details["type"] not in valid_types:
            raise DataIntegrityViolation(
                f"Nedovoljen tip podatkovnega vira: {source_details['type']}. "
                f"Dovoljeno: {valid_types}"
            )

    def _trigger_violation(
        self,
        reason: str,
        source_details: Dict[str, Any],
        events: Optional[Any],
    ) -> None:
        """
        Sproži globalno kršitev integritete podatkov.

        - aktivira hard-block v AI
        - aktivira no-action v recovery plannerju
        - sproži OS-level event DATA_INTEGRITY_VIOLATION
        - sproži SecurityEvents
        - zahteva realne podatke
        """

        self._integrity_block_active = True
        self._last_violation_details = source_details

        msg = f"DATA INTEGRITY VIOLATION: {reason} → {source_details}"
        self._log.critical(msg)

        # FAZA 8 – SecurityEvents
        try:
            self._events.data_integrity_violation(
                {"reason": reason, "source": source_details}
            )
        except Exception as exc:
            self._log.exception("Failed to emit security data integrity event: %s", exc)

        # OS-level event (če je SystemEvents priložen)
        if events is not None:
            try:
                events.data_integrity_violation(
                    {"reason": reason, "source": source_details}
                )
            except Exception as exc:
                self._log.exception(
                    "Failed to emit DATA_INTEGRITY_VIOLATION event: %s", exc
                )

        # Ustavi nadaljevanje AI ali OS operacij
        raise DataIntegrityViolation(
            "Nerealni ali manjkajoči podatki — sistem zahteva realen vir podatkov."
        )

    # ============================================================
    # STATUS
    # ============================================================

    def is_blocked(self) -> bool:
        """Vrne True, če je podatkovna integriteta v blokadi."""
        return self._integrity_block_active

    def last_violation(self) -> Optional[Dict[str, Any]]:
        """Vrne detajle zadnje kršitve."""
        return self._last_violation_details

    def clear_block(self) -> None:
        """
        Odblokira, ko so zagotovljeni realni podatki.
        """
        self._integrity_block_active = False
        self._last_violation_details = None
        self._log.warning("DataIntegrityEngine block cleared — real data restored.")

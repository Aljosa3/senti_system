from __future__ import annotations

import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# DATA LINEAGE RECORD
# ============================================================

@dataclass
class LineageEntry:
    """
    Posamezen dogodek v podatkovnem toku.

    Zabeleži:
    - izvor (adapter)
    - timestamp
    - validacije
    - transformacije
    - output stage
    - error (če obstaja)
    """

    lineage_id: str
    timestamp: float
    source_type: str
    source_origin: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    validations: List[Dict[str, Any]] = field(default_factory=list)
    transformations: List[Dict[str, Any]] = field(default_factory=list)

    output_stage: Optional[str] = None
    error: Optional[str] = None


# ============================================================
# DATA LINEAGE ENGINE (FAZA 9)
# ============================================================

class DataLineage:
    """
    FAZA 9 – Data Lineage Engine
    ============================

    Brez-AI deterministični sistem za sledenje podatkovnih tokov.

    Značilnosti:
    - Sledi vsakemu podatkovnemu koraku od adapterja → validator → processing → output
    - Beleži morebitne transformacije
    - Beleži validacije (uspešne + neuspešne)
    - Integrira s:
        • DataIntegrityEngine (FAZA 7)
        • Security Events (FAZA 8)
        • SystemEvents
    - Omogoča revizijsko sled za HR/Trading/Finance module (globalna zahteva)
    """

    def __init__(self, logger: Optional[logging.Logger] = None, events=None):
        self._log = logger or logging.getLogger(__name__)
        self._events = events

        # lineage_id → LineageEntry
        self._records: Dict[str, LineageEntry] = {}

        self._log.info("DataLineage initialized (FAZA 9).")

    # ============================================================
    # CREATE NEW LINEAGE RECORD
    # ============================================================

    def start_record(self, source_details: Dict[str, Any]) -> str:
        """
        Ustvari nov lineage zapis ob zajemu podatkov iz adapterja.
        """

        lineage_id = str(uuid.uuid4())
        entry = LineageEntry(
            lineage_id=lineage_id,
            timestamp=time.time(),
            source_type=source_details.get("type", "unknown"),
            source_origin=source_details.get("origin", "unknown"),
            metadata={k: v for k, v in source_details.items()},
        )

        self._records[lineage_id] = entry
        self._log.debug(f"[LINEAGE] start_record → {lineage_id}")

        return lineage_id

    # ============================================================
    # VALIDATION EVENTS
    # ============================================================

    def add_validation(self, lineage_id: str, result: Dict[str, Any]) -> None:
        """
        Dodaj validator rezultat:

        {
            "validator": "SchemaValidator",
            "status": "ok" | "error",
            "details": {...}
        }
        """

        entry = self._records.get(lineage_id)
        if not entry:
            self._log.error(f"[LINEAGE] Unknown lineage_id in add_validation: {lineage_id}")
            return

        entry.validations.append(result)
        self._log.debug(f"[LINEAGE] validation added → {lineage_id}")

        # Če validacija pade – sproži SECURITY event
        if result.get("status") == "error" and self._events:
            try:
                self._events.security_data_validation_failed({
                    "lineage_id": lineage_id,
                    "validator": result.get("validator"),
                    "details": result.get("details"),
                })
            except Exception as exc:
                self._log.exception(f"[LINEAGE] Failed to emit validation failure event: {exc}")

    # ============================================================
    # TRANSFORMATION EVENTS
    # ============================================================

    def add_transformation(self, lineage_id: str, step: Dict[str, Any]) -> None:
        """
        Beleži spremembe podatkov, npr:

        {
            "operation": "normalize",
            "field": "price",
            "old_value": 123.5,
            "new_value": 123.52
        }
        """

        entry = self._records.get(lineage_id)
        if not entry:
            self._log.error(f"[LINEAGE] Unknown lineage_id in add_transformation: {lineage_id}")
            return

        entry.transformations.append(step)
        self._log.debug(f"[LINEAGE] transformation added → {lineage_id}")

    # ============================================================
    # OUTPUT STAGE
    # ============================================================

    def set_output(self, lineage_id: str, stage: str) -> None:
        """
        Označi, kam so podatki dostavljeni:

        - "ai_layer"
        - "service"
        - "sensor_processing"
        - "database_write"
        - ...
        """

        entry = self._records.get(lineage_id)
        if not entry:
            self._log.error(f"[LINEAGE] Unknown lineage_id in set_output: {lineage_id}")
            return

        entry.output_stage = stage
        self._log.debug(f"[LINEAGE] output_stage → {stage} [{lineage_id}]")

    # ============================================================
    # ERROR CAPTURE
    # ============================================================

    def set_error(self, lineage_id: str, error_msg: str) -> None:
        entry = self._records.get(lineage_id)
        if not entry:
            self._log.error(f"[LINEAGE] Unknown lineage_id in set_error: {lineage_id}")
            return

        entry.error = error_msg
        self._log.error(f"[LINEAGE] ERROR [{lineage_id}] {error_msg}")

    # ============================================================
    # QUERY / RETRIEVE
    # ============================================================

    def get_record(self, lineage_id: str) -> Optional[LineageEntry]:
        return self._records.get(lineage_id)

    def list_records(self, limit: int = 50) -> List[LineageEntry]:
        """
        Vrni zadnje lineage zapise.
        """
        all_records = list(self._records.values())
        all_records.sort(key=lambda r: r.timestamp, reverse=True)
        return all_records[:limit]

    # ============================================================
    # EXPORT (PRIHODNOST)
    # ============================================================

    def export(self) -> List[Dict[str, Any]]:
        """
        Prenešeni podatki za:

        - revizijo
        - HR procesiranje
        - zakonodajne zahteve (npr. finance)
        """

        export_list = []
        for entry in self._records.values():
            export_list.append({
                "lineage_id": entry.lineage_id,
                "timestamp": entry.timestamp,
                "source_type": entry.source_type,
                "source_origin": entry.source_origin,
                "metadata": entry.metadata,
                "validations": entry.validations,
                "transformations": entry.transformations,
                "output_stage": entry.output_stage,
                "error": entry.error,
            })

        return export_list

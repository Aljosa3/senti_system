from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

from senti_os.data_pipeline.adapters.api_adapter import APIAdapter
from senti_os.data_pipeline.adapters.file_adapter import FileAdapter
from senti_os.data_pipeline.adapters.database_adapter import DatabaseAdapter
from senti_os.data_pipeline.adapters.sensor_adapter import SensorAdapter
from senti_os.data_pipeline.adapters.external_adapter import ExternalSystemAdapter

from senti_os.security.data_integrity_engine import DataIntegrityEngine
from senti_os.data_pipeline.data_lineage import DataLineage
from senti_os.data_pipeline.validators.base_validator import BaseValidator


class DataOrchestrator:
    """
    FAZA 9 – Data Orchestrator
    ==========================

    Centralni podatkovni tok:

        ADAPTER -> DataIntegrityEngine -> Validators -> Transform -> Output

    Hkrati v celoti podpira DataLineage:

        start_record()
        add_validation()
        add_transformation()
        set_output()

    Ta razred NE vsebuje AI logike.
    """

    def __init__(
        self,
        *,
        validators: List[BaseValidator],
        data_integrity: DataIntegrityEngine,
        lineage: DataLineage,
        events=None,
        logger: Optional[logging.Logger] = None,
    ):
        self._validators = validators
        self._integrity = data_integrity
        self._lineage = lineage
        self._events = events
        self._log = logger or logging.getLogger(__name__)

        # Register adapters
        self._adapters = {
            "api": APIAdapter,
            "file": FileAdapter,
            "database": DatabaseAdapter,
            "sensor": SensorAdapter,
            "external_system": ExternalSystemAdapter,
        }

        self._log.info("DataOrchestrator initialized (FAZA 9).")

    # ====================================================================
    # PUBLIC API
    # ====================================================================

    def ingest(self, source_details: Dict[str, Any]) -> Optional[Any]:
        """
        Glavni entrypoint za podatke.

        1) Lineage start_record()
        2) DataIntegrityEngine.check_source()
        3) Adapter -> load()
        4) Validators
        5) Transformations (optional)
        6) set_output()
        """

        lineage_id = self._lineage.start_record(source_details)

        # ----------------------------------
        # 1. Data Integrity Check (FAZA 7)
        # ----------------------------------
        try:
            self._integrity.check_source(source_details, events=self._events)
        except Exception as exc:
            self._lineage.set_error(lineage_id, str(exc))
            return None

        # ----------------------------------
        # 2. Load from adapter
        # ----------------------------------
        adapter_type = source_details.get("type")
        adapter_class = self._adapters.get(adapter_type)

        if not adapter_class:
            error = f"Unknown adapter type: {adapter_type}"
            self._lineage.set_error(lineage_id, error)
            self._log.error(error)
            return None

        try:
            adapter = adapter_class()
            data = adapter.load(source_details)
        except Exception as exc:
            self._lineage.set_error(lineage_id, f"Adapter load error: {exc}")
            return None

        # ----------------------------------
        # 3. Validators (FAZA 9)
        # ----------------------------------
        for validator in self._validators:
            try:
                result = validator.validate(data, source_details)
            except Exception as exc:
                result = {
                    "validator": validator.__class__.__name__,
                    "status": "error",
                    "details": {"exception": str(exc)}
                }

            # Add result to lineage
            self._lineage.add_validation(lineage_id, result)

            # If validation failed → stop
            if result.get("status") != "ok":
                self._lineage.set_error(lineage_id, f"Validation failed: {result}")
                return None

        # ----------------------------------
        # 4. Optional Transformations
        # ----------------------------------
        transformed_data = data

        transforms = getattr(adapter, "postprocess", None)
        if callable(transforms):
            try:
                before = transformed_data
                transformed_data = transforms(transformed_data)

                # Only log transformation if data changed
                if transformed_data != before:
                    self._lineage.add_transformation(
                        lineage_id,
                        {
                            "operation": "adapter_postprocess",
                            "before": before,
                            "after": transformed_data,
                        }
                    )

            except Exception as exc:
                self._lineage.set_error(lineage_id, f"Transform error: {exc}")
                return None

        # ----------------------------------
        # 5. FINISH
        # ----------------------------------

        self._lineage.set_output(lineage_id, "data_orchestrator_output")
        return transformed_data

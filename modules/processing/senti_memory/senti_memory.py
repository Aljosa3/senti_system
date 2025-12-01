"""
Senti Memory Module
Location: modules/processing/senti_memory/senti_memory.py

Structured long-term memory system for Senti System.
Stores validated, categorized, high-integrity knowledge.

Responsibilities:
- store()   -> save memory items
- recall()  -> retrieve items by query or category
- categorize() -> decide memory category
- score_priority() -> assign importance score
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from modules.senti_validator.senti_validator import SentiValidator
from senti_core_module.senti_core.utils.validator import Validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MEMORY_ROOT = PROJECT_ROOT / "memory_store"


class SentiMemory:
    """
    Long-term memory system with strict validation rules.
    """

    def __init__(self):
        self.name = "senti_memory"
        self.validator = SentiValidator()
        self._ensure_structure()

    # ======================================================
    # INTERNAL: ensure memory_store structure exists
    # ======================================================

    def _ensure_structure(self):
        if not MEMORY_ROOT.exists():
            MEMORY_ROOT.mkdir(parents=True)

        categories = MEMORY_ROOT / "categories"
        if not categories.exists():
            categories.mkdir()

        category_files = [
            "system.json",
            "trading.json",
            "seo.json",
            "os.json",
            "user.json",
            "misc.json"
        ]

        for cf in category_files:
            file_path = categories / cf
            if not file_path.exists():
                file_path.write_text("[]")

        index_file = MEMORY_ROOT / "index.json"
        if not index_file.exists():
            index_file.write_text("[]")

    # ======================================================
    # PUBLIC API
    # ======================================================

    def store(self, data: dict, category: str, metadata: dict) -> dict:
        """
        Store a memory item.
        Steps:
        1) validate data & metadata
        2) determine category
        3) assign priority
        4) write to file
        5) update index.json
        """

        # Validate raw memory through Senti Validator
        validation = self.validator.validate(data, metadata)

        if validation["status"] == "error":
            return {
                "memory_status": "error",
                "stored_item": None,
                "warnings": validation["warnings"],
                "errors": validation["errors"]
            }

        safe_data = validation["validated_output"]

        category = self.categorize(category)
        priority = self.score_priority(safe_data)

        memory_item = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_module": metadata.get("module", "unknown"),
            "category": category,
            "priority": float(priority),
            "content": safe_data
        }

        self._write_memory_item(memory_item)
        self._update_index(memory_item)

        return {
            "memory_status": "stored",
            "stored_item": memory_item,
            "warnings": validation["warnings"],
            "errors": []
        }

    def recall(self, query: str, category: str = None) -> dict:
        """
        Search memory items by text or category.
        """

        category_file = self._category_to_file(category) if category else None

        if category_file:
            data = json.loads(category_file.read_text())
        else:
            data = self._load_all_categories()

        results = [
            item for item in data
            if query.lower() in json.dumps(item["content"]).lower()
        ]

        results = sorted(results, key=lambda x: x["priority"], reverse=True)

        return {
            "status": "ok",
            "results": results
        }

    # ======================================================
    # CATEGORY / PRIORITY
    # ======================================================

    def categorize(self, category: str) -> str:
        allowed = ["system", "trading", "seo", "os", "user", "misc"]

        if category not in allowed:
            return "misc"

        return category

    def score_priority(self, data: dict) -> float:
        """
        Basic scoring:
        - more structured → higher score
        - more keys → higher score
        """

        score = min(1.0, 0.2 + 0.1 * len(data.keys()))
        return score

    # ======================================================
    # FILE OPERATIONS
    # ======================================================

    def _write_memory_item(self, item: dict):
        category_file = self._category_to_file(item["category"])
        data = json.loads(category_file.read_text())
        data.append(item)
        category_file.write_text(json.dumps(data, indent=2))

    def _update_index(self, item: dict):
        index_file = MEMORY_ROOT / "index.json"
        index_data = json.loads(index_file.read_text())
        index_data.append({
            "id": item["id"],
            "category": item["category"],
            "priority": item["priority"]
        })
        index_file.write_text(json.dumps(index_data, indent=2))

    # ======================================================
    # HELPERS
    # ======================================================

    def _category_to_file(self, category: str) -> Path:
        return MEMORY_ROOT / "categories" / f"{category}.json"

    def _load_all_categories(self):
        results = []
        cat_dir = MEMORY_ROOT / "categories"

        for f in cat_dir.iterdir():
            if f.name.endswith(".json"):
                items = json.loads(f.read_text())
                results.extend(items)

        return results

    # ======================================================
    # SYSTEM INTERFACE
    # ======================================================

    def load(self):
        return True

    def start(self):
        return True

    def stop(self):
        return True

    def metadata(self):
        return {
            "name": "senti_memory",
            "type": "processing",
            "version": "1.0.0"
        }

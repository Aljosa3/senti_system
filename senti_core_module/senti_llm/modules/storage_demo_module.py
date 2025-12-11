"""
FAZA 38 — Storage Demo Module

Demonstrates FAZA 38 Module Storage System.

Features tested:
- JSON file write/read with atomic operations
- Path resolution and sandboxing
- Module-isolated storage directories
"""

# -----------------------------------------------------------
#  FAZA 38 — MANIFEST WITH STORAGE CAPABILITY
# -----------------------------------------------------------
MODULE_MANIFEST = {
    "name": "storage_demo",
    "version": "1.0.0",
    "entrypoint": "StorageDemoModule",
    "phase": 38,
    "capabilities": {
        "requires": ["storage.write"]
    }
}


# -----------------------------------------------------------
#  STORAGE DEMO MODULE IMPLEMENTATION
# -----------------------------------------------------------
class StorageDemoModule:
    """
    FAZA 38 Demo module that tests storage capabilities.

    Tests:
    - write_json() with nested path creation
    - read_json() with verification
    - Atomic write operations
    """

    def __init__(self, context, capabilities):
        """
        FAZA 38: Module constructor receives context and capabilities.
        """
        self.context = context
        self.cap = capabilities

    def run(self, payload: dict):
        """
        Execute storage demonstration.

        Returns:
            Result dict with written and read-back data
        """
        # Test data
        data = {
            "message": "Hello Storage!",
            "value": 42,
            "nested": {
                "key": "nested_value",
                "count": 123
            }
        }

        # Get storage capability
        storage = self.cap["storage.write"]

        # Write JSON file (atomic operation)
        storage.write_json("test/data.json", data)

        # Read back to verify
        read_back = storage.read_json("test/data.json")

        # Additional tests
        exists = storage.exists("test/data.json")
        files = storage.list_files()

        return {
            "ok": True,
            "module": "storage_demo",
            "message": "Storage operations completed successfully!",
            "written": data,
            "read_back": read_back,
            "verification": {
                "file_exists": exists,
                "data_matches": data == read_back,
                "files_in_storage": files
            },
            "storage_capability": str(storage)
        }

"""
FAZA 37 — Restricted Capability Test Module

This module should FAIL to load because it requests restricted capabilities.
"""

MODULE_MANIFEST = {
    "name": "restricted_test",
    "version": "1.0.0",
    "entrypoint": "RestrictedTestModule",
    "phase": 37,
    "capabilities": {
        "requires": ["log.basic", "os.exec"],  # os.exec is RESTRICTED!
        "optional": []
    }
}


class RestrictedTestModule:
    def __init__(self, context, capabilities):
        self.context = context
        self.capabilities = capabilities

    def run(self, payload: dict):
        return {
            "ok": True,
            "message": "This should never execute due to restricted capability!"
        }

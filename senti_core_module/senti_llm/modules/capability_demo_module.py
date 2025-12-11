"""
FAZA 37 — Capability Demo Module

Demonstrira FAZA 37 Capability Injection System.

Module uporablja:
- log.basic capability za logging
- storage.write capability za shranjevanje podatkov
- time capability za timestamping
"""

# -----------------------------------------------------------
#  FAZA 37 — MANIFEST WITH CAPABILITIES
# -----------------------------------------------------------
MODULE_MANIFEST = {
    "name": "capability_demo",
    "version": "1.0.0",
    "entrypoint": "CapabilityDemoModule",
    "phase": 37,  # FAZA 37 compatible
    "capabilities": {
        "requires": ["log.basic", "storage.write", "time"],
        "optional": ["crypto"]
    }
}


# -----------------------------------------------------------
#  CAPABILITY DEMO MODULE IMPLEMENTATION
# -----------------------------------------------------------
class CapabilityDemoModule:
    """
    FAZA 37 Demo module ki uporablja capabilities injection.
    """

    def __init__(self, context, capabilities):
        """
        FAZA 37: Module constructor receives capabilities dict.
        """
        self.context = context
        self.capabilities = capabilities

    def run(self, payload: dict):
        """
        Demonstrira uporabo capabilities.
        """
        results = []

        # 1) Uporablja log.basic capability
        if "log.basic" in self.capabilities:
            log = self.capabilities["log.basic"]
            log.log("Capability Demo Module started!")
            results.append("✓ log.basic capability used")

        # 2) Uporablja time capability
        if "time" in self.capabilities:
            time_cap = self.capabilities["time"]
            current_time = time_cap.now()
            formatted_time = time_cap.format(current_time)
            results.append(f"✓ time capability: {formatted_time}")

        # 3) Uporablja storage.write capability
        if "storage.write" in self.capabilities:
            storage = self.capabilities["storage.write"]
            storage.write("demo_key", "demo_value")
            value = storage.read("demo_key")
            results.append(f"✓ storage.write capability: stored and retrieved '{value}'")

        # 4) Preveri optional crypto capability
        if "crypto" in self.capabilities:
            crypto = self.capabilities["crypto"]
            hash_result = crypto.hash_sha256("test_data")
            results.append(f"✓ crypto capability (optional): SHA256 = {hash_result[:16]}...")
        else:
            results.append("○ crypto capability not available (optional)")

        # 5) Lista vseh capabilities
        cap_list = list(self.capabilities.keys())

        return {
            "ok": True,
            "module": "capability_demo",
            "message": "Capability demonstration completed successfully!",
            "results": results,
            "capabilities_available": cap_list,
            "payload_received": payload,
        }

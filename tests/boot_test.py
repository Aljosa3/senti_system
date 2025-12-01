"""
A1 — BOOT TEST
Senti OS Bring-up Validation
----------------------------------

Namen:
    Preveri, ali se celoten Senti OS pravilno zažene
    z vključenimi fazami 1–9:
        - Core Loader
        - Kernel
        - OS Services
        - AI Operational Layer
        - Autonomous Task Loop
        - Security Layer
        - Data Integrity Engine

Test NE uporablja synthetic podatkov.
Test NE ustvarja lažnih metapodatkov.
Test NE spreminja stanja OS.

Rezultat: PASS / FAIL + diagnostika.
"""

import traceback
from senti_os.boot.boot import SentiBoot


def run_boot_test():
    print("\n==== Senti OS — BOOT TEST (A1) ====\n")

    try:
        boot = SentiBoot()
        print("Boot object created ✓")

        result = boot.start()
        print("Boot sequence executed ✓")

        # -------------------------------------------------------------
        # 1) Test: je rezultat uspešen?
        # -------------------------------------------------------------
        if not isinstance(result, dict):
            raise AssertionError("Boot did not return a dict.")

        if result.get("status") != "ok":
            raise AssertionError(f"Boot status != ok: {result}")

        print("Boot returned valid status ✓")

        # -------------------------------------------------------------
        # 2) Test: ali obstajajo ključne komponente?
        # -------------------------------------------------------------
        required_keys = {"kernel", "services", "ai_layer"}

        missing = required_keys - set(result.keys())
        if missing:
            raise AssertionError(f"Missing keys from boot result: {missing}")

        print("Boot dictionary contains kernel/services/ai_layer ✓")

        # -------------------------------------------------------------
        # 3) Test: OS services so registrirani
        # -------------------------------------------------------------
        services = result["services"]
        required_services = {
            "kernel_loop",
            "system_diagnostics",
            "watchdog",
            "memory_cleanup",
            "security_manager",
            "autonomous_task_loop",
        }

        registered = set(services.list_services())

        missing_services = required_services - registered
        if missing_services:
            raise AssertionError(f"Missing required OS services: {missing_services}")

        print("All core OS services registered ✓")

        # -------------------------------------------------------------
        # 4) Test: AI layer struktura
        # -------------------------------------------------------------
        ai_layer = result["ai_layer"]
        required_ai_parts = {"ai_agent", "command_processor", "recovery_planner", "task_engine"}

        missing_ai = required_ai_parts - set(ai_layer.keys())
        if missing_ai:
            raise AssertionError(f"AI layer missing components: {missing_ai}")

        print("AI Operational Layer integrity ✓")

        # -------------------------------------------------------------
        # 5) Test: Data Integrity Engine NI sprožil blokade
        # -------------------------------------------------------------
        if boot.data_integrity.is_blocked():
            raise AssertionError(
                f"Data Integrity Engine is in BLOCKED state: {boot.data_integrity.last_violation()}"
            )

        print("Data Integrity Engine state ✓ (no violations)")

        # -------------------------------------------------------------
        # 6) PASS
        # -------------------------------------------------------------
        print("\n==== BOOT TEST PASSED ✓ ====\n")
        return True

    except Exception as exc:
        print("\n==== BOOT TEST FAILED ✗ ====\n")
        print("Reason:", str(exc))
        print("\nTraceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    run_boot_test()

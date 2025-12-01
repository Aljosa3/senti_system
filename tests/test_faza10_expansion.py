#!/usr/bin/env python3
"""
FAZA 10 Expansion Engine Test Script
Demonstrates AI-driven system expansion capabilities.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_expansion import ExpansionManager


def test_faza10_expansion():
    """
    Test FAZA 10 Expansion Engine functionality.
    """
    print("=" * 60)
    print("FAZA 10 — AI Expansion Engine Test")
    print("=" * 60)

    # Initialize components
    event_bus = EventBus()
    expansion_manager = ExpansionManager(project_root, event_bus)

    print("\n✓ ExpansionManager initialized")
    print(f"  Project Root: {project_root}")

    # Test 1: Create a test module
    print("\n[TEST 1] Creating test module 'test_ai_module'...")
    try:
        result = expansion_manager.create_module(
            name="test_ai_module",
            directory="modules/processing"
        )
        print(f"✓ Module created successfully:")
        print(f"  Status: {result['status']}")
        print(f"  Module: {result['module']}")
        print(f"  Directory: {result['directory']}")
    except Exception as e:
        print(f"✗ Failed to create module: {e}")

    # Test 2: Handle AI request
    print("\n[TEST 2] Testing AI request handling...")
    try:
        ai_request = {
            "action": "create_module",
            "name": "ai_generated_sensor",
            "directory": "modules/sensors"
        }
        result = expansion_manager.handle_ai_request(ai_request)
        print(f"✓ AI request handled:")
        print(f"  Status: {result.get('status')}")
        print(f"  Module: {result.get('module')}")
    except Exception as e:
        print(f"✗ Failed to handle AI request: {e}")

    # Test 3: Security validation
    print("\n[TEST 3] Testing security validation...")
    try:
        # This should fail due to security rules
        result = expansion_manager.create_module(
            name="malicious_module",
            directory="senti_os"  # Protected directory
        )
        print(f"✗ Security validation failed - module should not be created in protected directory")
    except PermissionError as e:
        print(f"✓ Security validation working: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("FAZA 10 Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_faza10_expansion()

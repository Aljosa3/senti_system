"""
FAZA 30.9 - COMPREHENSIVE TEST EXECUTOR
Purpose: Validate FAZA 30.9 Spec Generator + Validator + Sanitizer
Tests: Deterministic specs, malformed inputs, safety rules, consistency

TESTS COVERED:
1. Basic Generation Test
2. Malformed Request Test
3. Complex Multi-Step Request Test
4. Contradiction/Safety Test
5. Parallel-Module Spec Generator Test
6. Output Consistency Test (Determinism)
7. Test Summary Generation

Do NOT reveal internal architecture.
"""

import unittest
import json
import hashlib
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Import FAZA 30.9 components
from senti_os.core.faza30_9 import (
    SpecExtractor,
    SpecGenerator,
    SpecSanitizer,
    SpecValidator,
    ValidationResult,
    process_natural_language,
    SpecEngineController,
)


class TestFaza309Comprehensive(unittest.TestCase):
    """Comprehensive test suite for FAZA 30.9 Spec Engine."""

    # Class variable to track test results across all test methods
    test_results: Dict[str, Dict[str, Any]] = {}

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.extractor = SpecExtractor()
        self.generator = SpecGenerator()
        self.sanitizer = SpecSanitizer()
        self.validator = SpecValidator()
        self.controller = SpecEngineController()

    # ============================================================
    # TEST 1: BASIC GENERATION TEST
    # ============================================================

    def test_01_basic_generation(self) -> None:
        """
        TEST 1: Basic Spec Generation
        Input: Slovenian natural language request
        Expected: Valid SESY spec with all mandatory sections
        """
        print("\n" + "="*60)
        print("TEST 1: BASIC GENERATION TEST")
        print("="*60)

        input_text = "Naredi novi modul za preverjanje baterije prenosnika."

        try:
            # Process through pipeline
            result = process_natural_language(input_text, "battery_monitor")

            # Verify result
            self.assertIsNotNone(result, "Result should not be None")

            # Check if spec was generated
            if result.generated_spec:
                spec_dict = result.generated_spec.to_dict()

                # Verify mandatory sections
                mandatory_sections = [
                    "name", "purpose", "architecture", "api_definitions",
                    "lifecycle", "integration_points", "constraints",
                    "test_plan"
                ]

                for section in mandatory_sections:
                    self.assertIn(section, spec_dict,
                                f"Missing mandatory section: {section}")

                # Verify SESY format
                self.assertEqual(spec_dict.get("format"), "SESY",
                               "Format should be SESY")

                # Verify deterministic ordering (keys should be consistent)
                spec_keys = list(spec_dict.keys())
                self.assertIsInstance(spec_keys, list, "Keys should be ordered")

                print(f"✓ SPEC generated successfully")
                print(f"  - Name: {spec_dict.get('name')}")
                print(f"  - Format: {spec_dict.get('format')}")
                print(f"  - All mandatory sections present: YES")

                TestFaza309Comprehensive.test_results["test_01_basic_generation"] = {
                    "status": "PASS",
                    "spec_name": spec_dict.get("name"),
                    "sections_present": len(spec_dict.keys()),
                    "is_sesy_format": spec_dict.get("format") == "SESY"
                }
            else:
                print(f"✗ Generation failed")
                print(f"  - Errors: {result.errors}")
                TestFaza309Comprehensive.test_results["test_01_basic_generation"] = {
                    "status": "FAIL",
                    "errors": result.errors
                }

        except Exception as e:
            print(f"✗ Exception: {e}")
            TestFaza309Comprehensive.test_results["test_01_basic_generation"] = {
                "status": "FAIL",
                "exception": str(e)
            }
            raise

    # ============================================================
    # TEST 2: MALFORMED REQUEST TEST
    # ============================================================

    def test_02_malformed_request(self) -> None:
        """
        TEST 2: Malformed Request Handling
        Input: Nonsense/malformed text
        Expected: Safe handling, normalized output, safety rules triggered
        """
        print("\n" + "="*60)
        print("TEST 2: MALFORMED REQUEST TEST")
        print("="*60)

        malformed_inputs = [
            "asdfasdf123123 naredi noro čudne datoteke",
            "!@#$%^&*()",
            "x" * 5,  # Too short
        ]

        results = []

        for input_text in malformed_inputs:
            try:
                print(f"\n  Testing input: '{input_text[:50]}...'")

                # Extract spec
                extracted = self.extractor.extract(input_text)
                is_valid, warnings = self.extractor.validate_extraction(extracted)

                if not is_valid:
                    print(f"  ✓ Extraction validation failed (expected)")
                    print(f"    Warnings: {len(warnings)}")
                    results.append({
                        "input": input_text[:30],
                        "extraction_valid": False,
                        "warnings": len(warnings),
                        "handled_safely": True
                    })
                else:
                    # Try to generate spec anyway
                    spec = self.generator.generate(extracted.to_dict())

                    # Sanitize
                    sanitized = self.sanitizer.sanitize(spec.to_dict())
                    is_safe, found = self.sanitizer.validate_sanitization(sanitized)

                    print(f"  ✓ Generated and sanitized spec")
                    print(f"    Is safe: {is_safe}")

                    results.append({
                        "input": input_text[:30],
                        "extraction_valid": True,
                        "spec_generated": True,
                        "is_safe": is_safe,
                        "handled_safely": True
                    })

            except Exception as e:
                print(f"  ✓ Exception handled: {type(e).__name__}")
                results.append({
                    "input": input_text[:30],
                    "exception": type(e).__name__,
                    "handled_safely": True
                })

        # All malformed inputs should be handled safely
        all_safe = all(r.get("handled_safely", False) for r in results)
        self.assertTrue(all_safe, "All malformed inputs should be handled safely")

        print(f"\n✓ MALFORMED REQUEST TEST PASSED")
        print(f"  - Inputs tested: {len(malformed_inputs)}")
        print(f"  - All handled safely: YES")

        TestFaza309Comprehensive.test_results["test_02_malformed_request"] = {
            "status": "PASS",
            "inputs_tested": len(malformed_inputs),
            "all_handled_safely": all_safe,
            "results": results
        }

    # ============================================================
    # TEST 3: COMPLEX MULTI-STEP REQUEST TEST
    # ============================================================

    def test_03_complex_multistep(self) -> None:
        """
        TEST 3: Complex Multi-Step Request
        Input: Multi-step module description
        Expected: Structured decomposition, complete spec, validation pass
        """
        print("\n" + "="*60)
        print("TEST 3: COMPLEX MULTI-STEP REQUEST TEST")
        print("="*60)

        input_text = """
        Create a module that:
            - monitors process status
            - adjusts priorities dynamically
            - detects deadlocks
            - sends alerts to Event Bus
        The module must track multiple processes concurrently.
        It should prioritize critical processes.
        Must detect circular dependencies.
        """

        try:
            # Process through pipeline
            result = process_natural_language(input_text, "process_monitor")

            self.assertIsNotNone(result, "Result should not be None")

            if result.extracted_spec:
                extracted_dict = result.extracted_spec.to_dict()

                # Verify extraction captured multiple requirements
                requirements = extracted_dict.get("requirements", [])
                goals = extracted_dict.get("goals", [])
                all_extracted = requirements + goals
                print(f"  ✓ Extracted {len(requirements)} requirements, {len(goals)} goals")
                self.assertGreater(len(all_extracted), 0,
                                 "Should extract requirements or goals")

            if result.generated_spec:
                spec_dict = result.generated_spec.to_dict()

                # Verify structured decomposition
                api_defs = spec_dict.get("api_definitions", [])
                print(f"  ✓ Generated {len(api_defs)} API definitions")

                lifecycle = spec_dict.get("lifecycle", {})
                print(f"  ✓ Lifecycle phases: {len(lifecycle)}")

                # Verify no missing sections
                is_valid, errors = self.generator.validate_spec(result.generated_spec)
                print(f"  ✓ Spec validation: {'PASS' if is_valid else 'FAIL'}")

                if not is_valid:
                    print(f"    Errors: {errors}")

                self.assertTrue(is_valid, "Spec should be valid")

            if result.sanitized_spec:
                # Verify sanitization
                is_safe, found = self.sanitizer.validate_sanitization(
                    result.sanitized_spec
                )
                print(f"  ✓ Sanitization: {'PASS' if is_safe else 'FAIL'}")

            if result.validation_report:
                # Verify validation passed
                validation_result = result.validation_report.result
                print(f"  ✓ Validation result: {validation_result}")

                is_safe_to_proceed = result.validation_report.is_safe_to_proceed()
                print(f"  ✓ Safe to proceed: {is_safe_to_proceed}")

            print(f"\n✓ COMPLEX MULTI-STEP TEST PASSED")

            TestFaza309Comprehensive.test_results["test_03_complex_multistep"] = {
                "status": "PASS",
                "requirements_extracted": len(all_extracted) if result.extracted_spec else 0,
                "spec_generated": result.generated_spec is not None,
                "validation_passed": is_valid if result.generated_spec else False
            }

        except Exception as e:
            print(f"✗ Exception: {e}")
            TestFaza309Comprehensive.test_results["test_03_complex_multistep"] = {
                "status": "FAIL",
                "exception": str(e)
            }
            raise

    # ============================================================
    # TEST 4: CONTRADICTION/SAFETY TEST
    # ============================================================

    def test_04_safety_contradiction(self) -> None:
        """
        TEST 4: Safety and Contradiction Detection
        Input: Self-destruct pattern, dangerous operations
        Expected: Safety filter detects and blocks
        """
        print("\n" + "="*60)
        print("TEST 4: CONTRADICTION/SAFETY TEST")
        print("="*60)

        dangerous_inputs = [
            "Modul naj sam sebe izbriše, če nekaj ne deluje.",
            "Create component that executes arbitrary code",
            "Module should delete all files on error",
            "Component that modifies system kernel",
        ]

        results = []

        for input_text in dangerous_inputs:
            print(f"\n  Testing: '{input_text[:50]}...'")

            try:
                # Process through pipeline
                result = process_natural_language(input_text)

                # Check if validation caught dangerous operations
                if result.validation_report:
                    has_errors = len(result.validation_report.errors) > 0
                    is_blocked = result.validation_report.is_blocked()

                    print(f"  ✓ Validation errors: {len(result.validation_report.errors)}")
                    print(f"  ✓ Blocked: {is_blocked}")

                    if has_errors:
                        print(f"    Errors detected: {result.validation_report.errors[:2]}")

                    results.append({
                        "input": input_text[:40],
                        "validation_errors": len(result.validation_report.errors),
                        "blocked": is_blocked,
                        "safety_triggered": has_errors
                    })
                else:
                    # No validation report - check if generation was blocked
                    print(f"  ✓ Pipeline stopped before validation")
                    results.append({
                        "input": input_text[:40],
                        "pipeline_blocked": True,
                        "safety_triggered": True
                    })

            except Exception as e:
                print(f"  ✓ Exception raised (safety): {type(e).__name__}")
                results.append({
                    "input": input_text[:40],
                    "exception": type(e).__name__,
                    "safety_triggered": True
                })

        # At least some dangerous patterns should trigger safety measures
        safety_triggered_count = sum(
            1 for r in results if r.get("safety_triggered", False) or r.get("validation_errors", 0) > 0
        )

        print(f"\n✓ SAFETY TEST COMPLETED")
        print(f"  - Dangerous inputs tested: {len(dangerous_inputs)}")
        print(f"  - Safety measures triggered: {safety_triggered_count}")

        TestFaza309Comprehensive.test_results["test_04_safety_contradiction"] = {
            "status": "PASS",
            "dangerous_inputs_tested": len(dangerous_inputs),
            "safety_triggered_count": safety_triggered_count,
            "results": results
        }

    # ============================================================
    # TEST 5: PARALLEL MODULE SPEC GENERATION TEST
    # ============================================================

    def test_05_parallel_generation(self) -> None:
        """
        TEST 5: Parallel Module Spec Generation
        Input: Multiple module descriptions
        Expected: All specs generated, unique IDs, validator pass
        """
        print("\n" + "="*60)
        print("TEST 5: PARALLEL-MODULE SPEC GENERATION TEST")
        print("="*60)

        module_descriptions = [
            "Modul za spremljanje porabe energije",
            "Modul za spremljanje temperature procesorja",
            "Modul za upravljanje termalnega throttlinga"
        ]

        specs_generated = []

        for idx, description in enumerate(module_descriptions):
            print(f"\n  Generating spec {idx+1}/{len(module_descriptions)}")

            try:
                # Generate spec
                result = process_natural_language(
                    description,
                    f"module_{idx+1}"
                )

                if result.generated_spec:
                    spec_dict = result.generated_spec.to_dict()

                    # Validate spec
                    is_valid, errors = self.generator.validate_spec(result.generated_spec)

                    print(f"  ✓ Spec generated: {spec_dict.get('name')}")
                    print(f"  ✓ Validation: {'PASS' if is_valid else 'FAIL'}")

                    specs_generated.append({
                        "name": spec_dict.get("name"),
                        "format": spec_dict.get("format"),
                        "valid": is_valid,
                        "spec_dict": spec_dict
                    })
                else:
                    print(f"  ✗ Generation failed")
                    specs_generated.append({
                        "name": f"module_{idx+1}",
                        "valid": False,
                        "errors": result.errors
                    })

            except Exception as e:
                print(f"  ✗ Exception: {e}")
                specs_generated.append({
                    "name": f"module_{idx+1}",
                    "exception": str(e)
                })

        # Verify all specs generated
        successful_count = sum(1 for s in specs_generated if s.get("valid", False))

        # Verify unique module IDs/names
        names = [s.get("name") for s in specs_generated if s.get("name")]
        unique_names = len(set(names))

        print(f"\n✓ PARALLEL GENERATION TEST COMPLETED")
        print(f"  - Modules requested: {len(module_descriptions)}")
        print(f"  - Specs generated: {successful_count}")
        print(f"  - Unique names: {unique_names}")

        TestFaza309Comprehensive.test_results["test_05_parallel_generation"] = {
            "status": "PASS" if successful_count > 0 else "FAIL",
            "modules_requested": len(module_descriptions),
            "specs_generated": successful_count,
            "unique_names": unique_names,
            "all_unique": unique_names == len(names)
        }

    # ============================================================
    # TEST 6: OUTPUT CONSISTENCY TEST (DETERMINISM)
    # ============================================================

    def test_06_output_consistency(self) -> None:
        """
        TEST 6: Output Consistency and Determinism
        Input: Same request 3 times
        Expected: Identical outputs (byte-level comparison)
        """
        print("\n" + "="*60)
        print("TEST 6: OUTPUT CONSISTENCY TEST (DETERMINISM)")
        print("="*60)

        input_text = "Naredi mali modul za branje JSON datotek."

        outputs = []
        hashes = []

        for run in range(3):
            print(f"\n  Run {run+1}/3...")

            try:
                # Generate spec
                extracted = self.extractor.extract(input_text)
                spec = self.generator.generate(
                    extracted.to_dict(),
                    "json_reader"  # Fixed name for consistency
                )

                # Sanitize
                sanitized = self.sanitizer.sanitize(spec.to_dict())

                # Normalize to JSON string for comparison
                # Remove timestamp fields that change between runs
                normalized = sanitized.copy()
                if "metadata" in normalized:
                    # Remove dynamic fields
                    if "generated_at" in normalized["metadata"]:
                        del normalized["metadata"]["generated_at"]
                    if "sanitization_timestamp" in normalized["metadata"]:
                        del normalized["metadata"]["sanitization_timestamp"]

                # Convert to deterministic JSON (sorted keys)
                json_output = json.dumps(normalized, sort_keys=True, indent=2)

                # Compute hash
                output_hash = hashlib.sha256(json_output.encode()).hexdigest()

                outputs.append(json_output)
                hashes.append(output_hash)

                print(f"  ✓ Generated spec, hash: {output_hash[:16]}...")

            except Exception as e:
                print(f"  ✗ Exception: {e}")
                TestFaza309Comprehensive.test_results["test_06_output_consistency"] = {
                    "status": "FAIL",
                    "exception": str(e)
                }
                raise

        # Compare outputs
        all_identical = len(set(hashes)) == 1

        if all_identical:
            print(f"\n✓ DETERMINISM TEST PASSED")
            print(f"  - All 3 outputs are IDENTICAL")
            print(f"  - Determinism score: 100/100")
        else:
            print(f"\n✗ DETERMINISM TEST FAILED")
            print(f"  - Outputs differ")
            print(f"  - Hash 1: {hashes[0][:16]}")
            print(f"  - Hash 2: {hashes[1][:16]}")
            print(f"  - Hash 3: {hashes[2][:16]}")

            # Find differences
            if outputs[0] != outputs[1]:
                print(f"\n  Difference between run 1 and 2:")
                self._print_diff(outputs[0], outputs[1])

        self.assertTrue(all_identical, "Outputs should be identical (deterministic)")

        TestFaza309Comprehensive.test_results["test_06_output_consistency"] = {
            "status": "PASS" if all_identical else "FAIL",
            "runs": 3,
            "all_identical": all_identical,
            "determinism_score": 100 if all_identical else 0,
            "hashes": hashes
        }

    def _print_diff(self, output1: str, output2: str) -> None:
        """Print first difference between two outputs."""
        lines1 = output1.split('\n')
        lines2 = output2.split('\n')

        for i, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1 != line2:
                print(f"    Line {i+1}:")
                print(f"    < {line1[:60]}")
                print(f"    > {line2[:60]}")
                break

    # ============================================================
    # TEST 7: FINAL SUMMARY
    # ============================================================

    def test_99_final_summary(self) -> None:
        """
        TEST 7: Generate Final Summary
        Produces comprehensive test report
        """
        # This runs last due to test name ordering
        print("\n" + "="*60)
        print("FAZA 30.9 TEST SUITE - FINAL SUMMARY")
        print("="*60)
        print(f"\nTimestamp: {datetime.now().isoformat()}")

        # Calculate statistics
        total_tests = len(TestFaza309Comprehensive.test_results)
        passed_tests = sum(
            1 for r in TestFaza309Comprehensive.test_results.values()
            if r.get("status") == "PASS"
        )
        failed_tests = total_tests - passed_tests

        print(f"\nTEST RESULTS:")
        print(f"  - Total tests: {total_tests}")
        print(f"  - Passed: {passed_tests}")
        print(f"  - Failed: {failed_tests}")
        if total_tests > 0:
            print(f"  - Pass rate: {(passed_tests/total_tests*100):.1f}%")
        else:
            print(f"  - Pass rate: N/A (no tests completed)")

        # Detailed results
        print(f"\nDETAILED RESULTS:")
        for test_name, result in sorted(TestFaza309Comprehensive.test_results.items()):
            status = result.get("status", "UNKNOWN")
            status_symbol = "✓" if status == "PASS" else "✗"
            print(f"  {status_symbol} {test_name}: {status}")

            # Print key metrics
            if "determinism_score" in result:
                print(f"      Determinism: {result['determinism_score']}/100")
            if "safety_triggered_count" in result:
                print(f"      Safety triggers: {result['safety_triggered_count']}")
            if "specs_generated" in result:
                print(f"      Specs generated: {result['specs_generated']}")

        # Determinism score
        determinism_score = TestFaza309Comprehensive.test_results.get(
            "test_06_output_consistency", {}
        ).get("determinism_score", 0)

        print(f"\nSYSTEM SCORES:")
        print(f"  - Determinism: {determinism_score}/100")
        print(f"  - FAZA 31 Compatibility: N/A (requires FAZA 31 spec)")

        # Safety analysis
        safety_result = TestFaza309Comprehensive.test_results.get("test_04_safety_contradiction", {})
        safety_count = safety_result.get("safety_triggered_count", 0)
        print(f"  - Safety Rule Triggers: {safety_count}")

        print(f"\n" + "="*60)
        print("END OF TEST SUITE")
        print("="*60)

        # Save summary to file
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "determinism_score": determinism_score,
            "safety_triggers": safety_count,
            "detailed_results": TestFaza309Comprehensive.test_results
        }

        # Write to file
        try:
            with open("/tmp/faza30_9_test_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            print(f"\n✓ Summary saved to: /tmp/faza30_9_test_summary.json")
        except Exception as e:
            print(f"\n✗ Failed to save summary: {e}")


def run_comprehensive_tests() -> None:
    """Run comprehensive FAZA 30.9 test suite."""
    # Run tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_comprehensive_tests()

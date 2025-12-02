"""
FAZA 20 - Diagnostics Engine

Performs comprehensive system diagnostics including module communication tests,
key integrity checks, WebSocket health, LLM routing tests, and ensemble tests.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class DiagnosticLevel(Enum):
    """Diagnostic result level."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiagnosticResult:
    """Result of a single diagnostic test."""
    test_name: str
    category: str
    level: DiagnosticLevel
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class DiagnosticReport:
    """Complete diagnostic report."""
    timestamp: datetime
    overall_status: DiagnosticLevel
    tests_run: int
    tests_passed: int
    tests_failed: int
    warnings: int
    errors: int
    results: List[DiagnosticResult]
    duration_seconds: float
    metadata: Dict[str, Any]


class DiagnosticsEngine:
    """
    Comprehensive system diagnostics for SENTI OS.

    Tests:
    - Module communication
    - FAZA 21 key integrity
    - FAZA 19 WebSocket health
    - FAZA 16 LLM routing
    - FAZA 17 ensemble functionality
    - Overall system health
    """

    def __init__(self):
        """Initialize diagnostics engine."""
        self._modules: Dict[str, Any] = {}
        self._last_report: Optional[DiagnosticReport] = None
        self._diagnostics_run_count = 0

    def register_module(self, module_name: str, module_ref: Any):
        """
        Register module for diagnostics.

        Args:
            module_name: Module identifier.
            module_ref: Reference to module object.
        """
        self._modules[module_name] = module_ref

    def run_diagnostics(self, quick: bool = False) -> DiagnosticReport:
        """
        Run comprehensive system diagnostics.

        Args:
            quick: If True, run only essential tests.

        Returns:
            DiagnosticReport with complete results.
        """
        start_time = datetime.utcnow()
        results: List[DiagnosticResult] = []

        # Core tests (always run)
        results.extend(self._test_module_registration())
        results.extend(self._test_module_communication())

        if not quick:
            # Extended tests
            results.extend(self._test_persistence_layer())
            results.extend(self._test_uil_layer())
            results.extend(self._test_llm_control())
            results.extend(self._test_orchestration())

        # Calculate statistics
        tests_passed = sum(1 for r in results if r.passed)
        tests_failed = sum(1 for r in results if not r.passed)
        warnings = sum(1 for r in results if r.level == DiagnosticLevel.WARNING)
        errors = sum(1 for r in results if r.level in [DiagnosticLevel.ERROR, DiagnosticLevel.CRITICAL])

        # Determine overall status
        overall_status = self._calculate_overall_status(results)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Create report
        report = DiagnosticReport(
            timestamp=datetime.utcnow(),
            overall_status=overall_status,
            tests_run=len(results),
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            warnings=warnings,
            errors=errors,
            results=results,
            duration_seconds=duration,
            metadata={
                "quick_mode": quick,
                "diagnostics_run_count": self._diagnostics_run_count,
                "modules_registered": len(self._modules)
            }
        )

        self._last_report = report
        self._diagnostics_run_count += 1

        return report

    def get_last_report(self) -> Optional[DiagnosticReport]:
        """Get last diagnostic report."""
        return self._last_report

    def get_diagnostics_count(self) -> int:
        """Get number of times diagnostics have been run."""
        return self._diagnostics_run_count

    def _test_module_registration(self) -> List[DiagnosticResult]:
        """Test that critical modules are registered."""
        results = []

        critical_modules = [
            "faza16_llm_control",
            "faza17_orchestration",
            "faza19_uil",
            "faza21_persistence"
        ]

        for module_name in critical_modules:
            if module_name in self._modules:
                results.append(DiagnosticResult(
                    test_name=f"module_registered_{module_name}",
                    category="registration",
                    level=DiagnosticLevel.OK,
                    passed=True,
                    message=f"Module {module_name} is registered"
                ))
            else:
                results.append(DiagnosticResult(
                    test_name=f"module_registered_{module_name}",
                    category="registration",
                    level=DiagnosticLevel.WARNING,
                    passed=False,
                    message=f"Module {module_name} is not registered"
                ))

        return results

    def _test_module_communication(self) -> List[DiagnosticResult]:
        """Test communication with registered modules."""
        results = []

        for module_name, module_ref in self._modules.items():
            try:
                # Try to get status
                if hasattr(module_ref, 'get_status'):
                    status = module_ref.get_status()
                    results.append(DiagnosticResult(
                        test_name=f"communication_{module_name}",
                        category="communication",
                        level=DiagnosticLevel.OK,
                        passed=True,
                        message=f"Communication with {module_name} successful",
                        details={"status": status}
                    ))
                else:
                    results.append(DiagnosticResult(
                        test_name=f"communication_{module_name}",
                        category="communication",
                        level=DiagnosticLevel.WARNING,
                        passed=True,
                        message=f"Module {module_name} does not support status check",
                        details={"has_get_status": False}
                    ))
            except Exception as e:
                results.append(DiagnosticResult(
                    test_name=f"communication_{module_name}",
                    category="communication",
                    level=DiagnosticLevel.ERROR,
                    passed=False,
                    message=f"Failed to communicate with {module_name}: {str(e)}"
                ))

        return results

    def _test_persistence_layer(self) -> List[DiagnosticResult]:
        """Test FAZA 21 persistence layer."""
        results = []
        persistence = self._modules.get("faza21_persistence")

        if not persistence:
            results.append(DiagnosticResult(
                test_name="persistence_available",
                category="persistence",
                level=DiagnosticLevel.WARNING,
                passed=False,
                message="FAZA 21 persistence layer not registered"
            ))
            return results

        # Test key initialization
        try:
            if hasattr(persistence, 'master_key_manager'):
                key_manager = persistence.master_key_manager
                if hasattr(key_manager, 'is_initialized'):
                    is_init = key_manager.is_initialized()
                    results.append(DiagnosticResult(
                        test_name="persistence_key_initialized",
                        category="persistence",
                        level=DiagnosticLevel.OK if is_init else DiagnosticLevel.WARNING,
                        passed=is_init,
                        message=f"Master key {'initialized' if is_init else 'not initialized'}",
                        details={"initialized": is_init}
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="persistence_key_check",
                category="persistence",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"Failed to check key status: {str(e)}"
            ))

        # Test storage backend
        try:
            if hasattr(persistence, 'storage_backend'):
                backend = persistence.storage_backend
                if hasattr(backend, 'list_files'):
                    files = backend.list_files()
                    results.append(DiagnosticResult(
                        test_name="persistence_storage_accessible",
                        category="persistence",
                        level=DiagnosticLevel.OK,
                        passed=True,
                        message="Storage backend accessible",
                        details={"file_count": len(files)}
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="persistence_storage_check",
                category="persistence",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"Storage backend error: {str(e)}"
            ))

        return results

    def _test_uil_layer(self) -> List[DiagnosticResult]:
        """Test FAZA 19 UIL layer."""
        results = []
        uil = self._modules.get("faza19_uil")

        if not uil:
            results.append(DiagnosticResult(
                test_name="uil_available",
                category="uil",
                level=DiagnosticLevel.WARNING,
                passed=False,
                message="FAZA 19 UIL layer not registered"
            ))
            return results

        # Test event bus
        try:
            if hasattr(uil, 'event_bus'):
                event_bus = uil.event_bus
                if hasattr(event_bus, 'get_statistics'):
                    stats = event_bus.get_statistics()
                    results.append(DiagnosticResult(
                        test_name="uil_event_bus",
                        category="uil",
                        level=DiagnosticLevel.OK,
                        passed=True,
                        message="Event bus operational",
                        details=stats
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="uil_event_bus_check",
                category="uil",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"Event bus error: {str(e)}"
            ))

        # Test WebSocket server (simulated)
        try:
            if hasattr(uil, 'websocket_server'):
                ws = uil.websocket_server
                if hasattr(ws, 'get_status'):
                    status = ws.get_status()
                    results.append(DiagnosticResult(
                        test_name="uil_websocket",
                        category="uil",
                        level=DiagnosticLevel.OK,
                        passed=True,
                        message="WebSocket server operational",
                        details=status
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="uil_websocket_check",
                category="uil",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"WebSocket error: {str(e)}"
            ))

        return results

    def _test_llm_control(self) -> List[DiagnosticResult]:
        """Test FAZA 16 LLM control layer."""
        results = []
        llm_control = self._modules.get("faza16_llm_control")

        if not llm_control:
            results.append(DiagnosticResult(
                test_name="llm_control_available",
                category="llm",
                level=DiagnosticLevel.WARNING,
                passed=False,
                message="FAZA 16 LLM control layer not registered"
            ))
            return results

        # Test routing capability
        try:
            if hasattr(llm_control, 'router'):
                router = llm_control.router
                if hasattr(router, 'get_available_models'):
                    models = router.get_available_models()
                    results.append(DiagnosticResult(
                        test_name="llm_routing",
                        category="llm",
                        level=DiagnosticLevel.OK if models else DiagnosticLevel.WARNING,
                        passed=len(models) > 0 if models else False,
                        message=f"LLM routing operational ({len(models) if models else 0} models)",
                        details={"models": models} if models else {}
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="llm_routing_check",
                category="llm",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"LLM routing error: {str(e)}"
            ))

        return results

    def _test_orchestration(self) -> List[DiagnosticResult]:
        """Test FAZA 17 orchestration layer."""
        results = []
        orchestration = self._modules.get("faza17_orchestration")

        if not orchestration:
            results.append(DiagnosticResult(
                test_name="orchestration_available",
                category="orchestration",
                level=DiagnosticLevel.WARNING,
                passed=False,
                message="FAZA 17 orchestration layer not registered"
            ))
            return results

        # Test ensemble capability
        try:
            if hasattr(orchestration, 'ensemble_engine'):
                ensemble = orchestration.ensemble_engine
                if hasattr(ensemble, 'get_available_strategies'):
                    strategies = ensemble.get_available_strategies()
                    results.append(DiagnosticResult(
                        test_name="orchestration_ensemble",
                        category="orchestration",
                        level=DiagnosticLevel.OK,
                        passed=True,
                        message=f"Ensemble engine operational ({len(strategies) if strategies else 0} strategies)",
                        details={"strategies": strategies} if strategies else {}
                    ))
        except Exception as e:
            results.append(DiagnosticResult(
                test_name="orchestration_ensemble_check",
                category="orchestration",
                level=DiagnosticLevel.ERROR,
                passed=False,
                message=f"Ensemble error: {str(e)}"
            ))

        return results

    def _calculate_overall_status(self, results: List[DiagnosticResult]) -> DiagnosticLevel:
        """Calculate overall diagnostic status."""
        if not results:
            return DiagnosticLevel.WARNING

        # Check for critical errors
        if any(r.level == DiagnosticLevel.CRITICAL for r in results):
            return DiagnosticLevel.CRITICAL

        # Check for errors
        if any(r.level == DiagnosticLevel.ERROR for r in results):
            return DiagnosticLevel.ERROR

        # Check for warnings
        if any(r.level == DiagnosticLevel.WARNING for r in results):
            return DiagnosticLevel.WARNING

        # All OK
        return DiagnosticLevel.OK


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "diagnostics_engine",
        "faza": "20",
        "version": "1.0.0",
        "description": "Comprehensive system diagnostics and health checks"
    }

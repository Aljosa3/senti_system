"""
FAZA 20 - Status Collector

Gathers health status from all SENTI OS modules and provides
unified OS-level status snapshot with timestamps, uptime, and health scores.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class ModuleHealth(Enum):
    """Module health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ModuleStatus:
    """Status information for a single module."""
    module_name: str
    faza_number: int
    health: ModuleHealth
    health_score: float  # 0.0 to 1.0
    last_updated: datetime
    uptime_seconds: Optional[float] = None
    error_count: int = 0
    warning_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemStatus:
    """Complete SENTI OS system status."""
    timestamp: datetime
    overall_health: ModuleHealth
    overall_score: float
    total_uptime_seconds: float
    modules: List[ModuleStatus]
    active_warnings: int
    active_errors: int
    metadata: Dict[str, Any]


class StatusCollector:
    """
    Collects and aggregates health status from all SENTI OS modules.

    Provides normalized, unified view of system health with:
    - Per-module health scores
    - Overall system health
    - Uptime tracking
    - Error/warning aggregation
    - Configurable collection frequency
    """

    def __init__(self, collection_frequency_seconds: int = 5):
        """
        Initialize status collector.

        Args:
            collection_frequency_seconds: How often to collect status.
        """
        self.collection_frequency = collection_frequency_seconds
        self._start_time = datetime.utcnow()
        self._module_statuses: Dict[str, ModuleStatus] = {}
        self._last_collection: Optional[datetime] = None
        self._collection_count = 0

        # Module references (injected during initialization)
        self._faza16_llm_control = None
        self._faza17_orchestration = None
        self._faza18_auth_flow = None
        self._faza19_uil = None
        self._faza21_persistence = None

    def register_module(self, module_name: str, module_ref: Any):
        """
        Register a FAZA module for status collection.

        Args:
            module_name: Name of the module (e.g., "faza16_llm_control").
            module_ref: Reference to module object.
        """
        if module_name == "faza16_llm_control":
            self._faza16_llm_control = module_ref
        elif module_name == "faza17_orchestration":
            self._faza17_orchestration = module_ref
        elif module_name == "faza18_auth_flow":
            self._faza18_auth_flow = module_ref
        elif module_name == "faza19_uil":
            self._faza19_uil = module_ref
        elif module_name == "faza21_persistence":
            self._faza21_persistence = module_ref

    def collect_status(self) -> SystemStatus:
        """
        Collect current status from all registered modules.

        Returns:
            SystemStatus with complete system health snapshot.
        """
        self._last_collection = datetime.utcnow()
        self._collection_count += 1

        modules: List[ModuleStatus] = []

        # Collect FAZA 16 status
        if self._faza16_llm_control:
            modules.append(self._collect_faza16_status())

        # Collect FAZA 17 status
        if self._faza17_orchestration:
            modules.append(self._collect_faza17_status())

        # Collect FAZA 18 status
        if self._faza18_auth_flow:
            modules.append(self._collect_faza18_status())

        # Collect FAZA 19 status
        if self._faza19_uil:
            modules.append(self._collect_faza19_status())

        # Collect FAZA 21 status
        if self._faza21_persistence:
            modules.append(self._collect_faza21_status())

        # Calculate overall status
        overall_health, overall_score = self._calculate_overall_health(modules)

        # Count warnings and errors
        total_warnings = sum(m.warning_count for m in modules)
        total_errors = sum(m.error_count for m in modules)

        # Calculate total uptime
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return SystemStatus(
            timestamp=self._last_collection,
            overall_health=overall_health,
            overall_score=overall_score,
            total_uptime_seconds=uptime,
            modules=modules,
            active_warnings=total_warnings,
            active_errors=total_errors,
            metadata={
                "collection_count": self._collection_count,
                "collection_frequency": self.collection_frequency,
                "modules_registered": len(modules)
            }
        )

    def get_module_status(self, module_name: str) -> Optional[ModuleStatus]:
        """
        Get status for specific module.

        Args:
            module_name: Name of module.

        Returns:
            ModuleStatus if found, None otherwise.
        """
        return self._module_statuses.get(module_name)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about status collection."""
        return {
            "collection_frequency_seconds": self.collection_frequency,
            "last_collection": self._last_collection.isoformat() if self._last_collection else None,
            "collection_count": self._collection_count,
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "modules_registered": self._count_registered_modules()
        }

    def _collect_faza16_status(self) -> ModuleStatus:
        """Collect FAZA 16 (LLM Control Layer) status."""
        try:
            # Try to get status from module
            if hasattr(self._faza16_llm_control, 'get_status'):
                status = self._faza16_llm_control.get_status()
                health_score = self._calculate_health_score(status)
                health = self._score_to_health(health_score)

                return ModuleStatus(
                    module_name="faza16_llm_control",
                    faza_number=16,
                    health=health,
                    health_score=health_score,
                    last_updated=datetime.utcnow(),
                    error_count=status.get("error_count", 0),
                    warning_count=status.get("warning_count", 0),
                    metadata=status
                )
            else:
                # Module doesn't support status
                return self._create_unknown_status("faza16_llm_control", 16)
        except Exception:
            return self._create_failed_status("faza16_llm_control", 16)

    def _collect_faza17_status(self) -> ModuleStatus:
        """Collect FAZA 17 (Multi-Model Orchestration) status."""
        try:
            if hasattr(self._faza17_orchestration, 'get_status'):
                status = self._faza17_orchestration.get_status()
                health_score = self._calculate_health_score(status)
                health = self._score_to_health(health_score)

                return ModuleStatus(
                    module_name="faza17_orchestration",
                    faza_number=17,
                    health=health,
                    health_score=health_score,
                    last_updated=datetime.utcnow(),
                    error_count=status.get("error_count", 0),
                    warning_count=status.get("warning_count", 0),
                    metadata=status
                )
            else:
                return self._create_unknown_status("faza17_orchestration", 17)
        except Exception:
            return self._create_failed_status("faza17_orchestration", 17)

    def _collect_faza18_status(self) -> ModuleStatus:
        """Collect FAZA 18 (Auth Flow) status."""
        try:
            if hasattr(self._faza18_auth_flow, 'get_status'):
                status = self._faza18_auth_flow.get_status()
                health_score = self._calculate_health_score(status)
                health = self._score_to_health(health_score)

                return ModuleStatus(
                    module_name="faza18_auth_flow",
                    faza_number=18,
                    health=health,
                    health_score=health_score,
                    last_updated=datetime.utcnow(),
                    error_count=status.get("error_count", 0),
                    warning_count=status.get("warning_count", 0),
                    metadata=status
                )
            else:
                return self._create_unknown_status("faza18_auth_flow", 18)
        except Exception:
            return self._create_failed_status("faza18_auth_flow", 18)

    def _collect_faza19_status(self) -> ModuleStatus:
        """Collect FAZA 19 (UIL) status."""
        try:
            if hasattr(self._faza19_uil, 'get_status'):
                status = self._faza19_uil.get_status()
                health_score = self._calculate_health_score(status)
                health = self._score_to_health(health_score)

                return ModuleStatus(
                    module_name="faza19_uil",
                    faza_number=19,
                    health=health,
                    health_score=health_score,
                    last_updated=datetime.utcnow(),
                    error_count=status.get("error_count", 0),
                    warning_count=status.get("warning_count", 0),
                    metadata=status
                )
            else:
                return self._create_unknown_status("faza19_uil", 19)
        except Exception:
            return self._create_failed_status("faza19_uil", 19)

    def _collect_faza21_status(self) -> ModuleStatus:
        """Collect FAZA 21 (Persistence Layer) status."""
        try:
            if hasattr(self._faza21_persistence, 'get_status'):
                status = self._faza21_persistence.get_status()
                health_score = self._calculate_health_score(status)
                health = self._score_to_health(health_score)

                return ModuleStatus(
                    module_name="faza21_persistence",
                    faza_number=21,
                    health=health,
                    health_score=health_score,
                    last_updated=datetime.utcnow(),
                    error_count=status.get("error_count", 0),
                    warning_count=status.get("warning_count", 0),
                    metadata=status
                )
            else:
                return self._create_unknown_status("faza21_persistence", 21)
        except Exception:
            return self._create_failed_status("faza21_persistence", 21)

    def _calculate_health_score(self, status: Dict[str, Any]) -> float:
        """
        Calculate health score from module status.

        Args:
            status: Module status dictionary.

        Returns:
            Health score between 0.0 and 1.0.
        """
        # Base score
        score = 1.0

        # Deduct for errors
        error_count = status.get("error_count", 0)
        score -= min(error_count * 0.2, 0.6)  # Max 60% deduction

        # Deduct for warnings
        warning_count = status.get("warning_count", 0)
        score -= min(warning_count * 0.05, 0.2)  # Max 20% deduction

        # Check initialization
        if not status.get("initialized", True):
            score *= 0.5

        return max(0.0, min(1.0, score))

    def _score_to_health(self, score: float) -> ModuleHealth:
        """Convert health score to ModuleHealth enum."""
        if score >= 0.8:
            return ModuleHealth.HEALTHY
        elif score >= 0.5:
            return ModuleHealth.DEGRADED
        else:
            return ModuleHealth.FAILED

    def _calculate_overall_health(
        self,
        modules: List[ModuleStatus]
    ) -> tuple[ModuleHealth, float]:
        """Calculate overall system health."""
        if not modules:
            return ModuleHealth.UNKNOWN, 0.0

        # Calculate average health score
        avg_score = sum(m.health_score for m in modules) / len(modules)

        # Check if any module is failed
        failed_count = sum(1 for m in modules if m.health == ModuleHealth.FAILED)
        if failed_count > 0:
            # Reduce score based on failed modules
            avg_score *= (1 - (failed_count / len(modules) * 0.5))

        health = self._score_to_health(avg_score)

        return health, avg_score

    def _create_unknown_status(self, module_name: str, faza_number: int) -> ModuleStatus:
        """Create unknown status for module."""
        return ModuleStatus(
            module_name=module_name,
            faza_number=faza_number,
            health=ModuleHealth.UNKNOWN,
            health_score=0.5,
            last_updated=datetime.utcnow(),
            metadata={"reason": "module_not_initialized"}
        )

    def _create_failed_status(self, module_name: str, faza_number: int) -> ModuleStatus:
        """Create failed status for module."""
        return ModuleStatus(
            module_name=module_name,
            faza_number=faza_number,
            health=ModuleHealth.FAILED,
            health_score=0.0,
            last_updated=datetime.utcnow(),
            error_count=1,
            metadata={"reason": "status_collection_failed"}
        )

    def _count_registered_modules(self) -> int:
        """Count number of registered modules."""
        count = 0
        if self._faza16_llm_control:
            count += 1
        if self._faza17_orchestration:
            count += 1
        if self._faza18_auth_flow:
            count += 1
        if self._faza19_uil:
            count += 1
        if self._faza21_persistence:
            count += 1
        return count


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "status_collector",
        "faza": "20",
        "version": "1.0.0",
        "description": "Unified OS health status collection and aggregation"
    }

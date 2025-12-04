"""
FAZA 29 – Enterprise Governance Engine
Risk Model

Computes comprehensive risk score (0-100) from multiple FAZA layers:
- FAZA 28.5: Stability metrics and agent scores
- FAZA 27/27.5: Graph optimizer hints and task metrics
- FAZA 25: Orchestration stress markers

Implements 3 risk layers:
- System risk: Overall system health
- Agent risk: Agent-level concerns
- Graph risk: Task graph complexity/health

Includes 15+ risk factors for comprehensive assessment.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RiskFactor:
    """
    Individual risk factor.

    Attributes:
        name: Factor name
        value: Current value (0-1 normalized)
        weight: Factor weight in overall risk
        threshold: Warning threshold
        description: Factor description
    """
    name: str
    value: float
    weight: float = 1.0
    threshold: float = 0.7
    description: str = ""

    def is_critical(self) -> bool:
        """Check if factor exceeds threshold"""
        return self.value >= self.threshold

    def get_score(self) -> float:
        """Get weighted score"""
        return self.value * self.weight


@dataclass
class RiskBreakdown:
    """
    Risk score breakdown by layer.

    Attributes:
        system_risk: System-level risk (0-100)
        agent_risk: Agent-level risk (0-100)
        graph_risk: Graph-level risk (0-100)
        total_risk: Consolidated risk (0-100)
        factors: List of risk factors
        critical_factors: List of critical factors
        timestamp: Assessment timestamp
    """
    system_risk: float
    agent_risk: float
    graph_risk: float
    total_risk: float
    factors: List[RiskFactor] = field(default_factory=list)
    critical_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "system_risk": round(self.system_risk, 2),
            "agent_risk": round(self.agent_risk, 2),
            "graph_risk": round(self.graph_risk, 2),
            "total_risk": round(self.total_risk, 2),
            "critical_factors": self.critical_factors,
            "factor_count": len(self.factors),
            "timestamp": self.timestamp.isoformat()
        }


class RiskModel:
    """
    Comprehensive risk assessment model.

    Computes risk scores from multiple FAZA layers and produces
    consolidated risk assessment with detailed breakdown.
    """

    def __init__(self):
        """Initialize risk model"""
        # Layer weights (must sum to 1.0)
        self.layer_weights = {
            "system": 0.4,
            "agent": 0.35,
            "graph": 0.25
        }

        # Risk factor weights
        self.factor_weights = {
            # System factors
            "cpu_usage": 1.2,
            "memory_usage": 1.2,
            "disk_usage": 0.8,
            "network_saturation": 0.9,
            "error_rate": 1.5,

            # Agent factors
            "agent_failure_rate": 1.5,
            "agent_performance": 1.0,
            "agent_cooperation": 0.8,
            "agent_stability": 1.3,
            "anomaly_rate": 1.2,

            # Graph factors
            "graph_complexity": 0.9,
            "cycle_count": 1.4,
            "bottleneck_count": 1.1,
            "parallelization_index": -0.7,  # Negative = lower is worse
            "execution_delay": 1.0,
            "task_failure_rate": 1.3
        }

        # Statistics
        self.stats = {
            "assessments_performed": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }

    def compute_risk(
        self,
        system_metrics: Optional[Dict[str, Any]] = None,
        agent_metrics: Optional[Dict[str, Any]] = None,
        graph_metrics: Optional[Dict[str, Any]] = None
    ) -> RiskBreakdown:
        """
        Compute comprehensive risk score.

        Args:
            system_metrics: System health metrics (FAZA 25/28)
            agent_metrics: Agent performance metrics (FAZA 28.5)
            graph_metrics: Graph health metrics (FAZA 27/27.5)

        Returns:
            RiskBreakdown with consolidated score and details
        """
        self.stats["assessments_performed"] += 1

        # Initialize with empty dicts if None
        system_metrics = system_metrics or {}
        agent_metrics = agent_metrics or {}
        graph_metrics = graph_metrics or {}

        # Compute layer risks
        system_risk, system_factors = self._compute_system_risk(system_metrics)
        agent_risk, agent_factors = self._compute_agent_risk(agent_metrics)
        graph_risk, graph_factors = self._compute_graph_risk(graph_metrics)

        # Consolidated risk (weighted average)
        total_risk = (
            system_risk * self.layer_weights["system"] +
            agent_risk * self.layer_weights["agent"] +
            graph_risk * self.layer_weights["graph"]
        )

        # Collect all factors
        all_factors = system_factors + agent_factors + graph_factors

        # Identify critical factors
        critical_factors = [f.name for f in all_factors if f.is_critical()]

        # Update statistics
        if total_risk >= 70:
            self.stats["high_risk_count"] += 1
        elif total_risk >= 40:
            self.stats["medium_risk_count"] += 1
        else:
            self.stats["low_risk_count"] += 1

        breakdown = RiskBreakdown(
            system_risk=system_risk,
            agent_risk=agent_risk,
            graph_risk=graph_risk,
            total_risk=total_risk,
            factors=all_factors,
            critical_factors=critical_factors
        )

        logger.debug(f"Risk computed: {total_risk:.1f} (S:{system_risk:.1f}, A:{agent_risk:.1f}, G:{graph_risk:.1f})")

        return breakdown

    def _compute_system_risk(self, metrics: Dict[str, Any]) -> tuple[float, List[RiskFactor]]:
        """
        Compute system-level risk.

        Factors:
        - CPU usage
        - Memory usage
        - Disk usage
        - Network saturation
        - Error rate

        Args:
            metrics: System metrics

        Returns:
            Tuple of (risk_score, factors_list)
        """
        factors = []

        # CPU usage (0-1)
        cpu_usage = metrics.get("cpu_usage", 0.0)
        factors.append(RiskFactor(
            name="cpu_usage",
            value=cpu_usage,
            weight=self.factor_weights["cpu_usage"],
            threshold=0.85,
            description="CPU utilization"
        ))

        # Memory usage (0-1)
        memory_usage = metrics.get("memory_usage", 0.0)
        factors.append(RiskFactor(
            name="memory_usage",
            value=memory_usage,
            weight=self.factor_weights["memory_usage"],
            threshold=0.85,
            description="Memory utilization"
        ))

        # Disk usage (0-1)
        disk_usage = metrics.get("disk_usage", 0.0)
        factors.append(RiskFactor(
            name="disk_usage",
            value=disk_usage,
            weight=self.factor_weights["disk_usage"],
            threshold=0.90,
            description="Disk space utilization"
        ))

        # Network saturation (0-1)
        network_saturation = metrics.get("network_saturation", 0.0)
        factors.append(RiskFactor(
            name="network_saturation",
            value=network_saturation,
            weight=self.factor_weights["network_saturation"],
            threshold=0.80,
            description="Network bandwidth saturation"
        ))

        # Error rate (0-1)
        error_rate = metrics.get("error_rate", 0.0)
        factors.append(RiskFactor(
            name="error_rate",
            value=error_rate,
            weight=self.factor_weights["error_rate"],
            threshold=0.50,
            description="System error rate"
        ))

        # Calculate weighted risk
        total_weight = sum(f.weight for f in factors)
        risk_score = sum(f.get_score() for f in factors) / total_weight * 100

        return risk_score, factors

    def _compute_agent_risk(self, metrics: Dict[str, Any]) -> tuple[float, List[RiskFactor]]:
        """
        Compute agent-level risk.

        Factors (from FAZA 28.5):
        - Agent failure rate
        - Agent performance score
        - Agent cooperation score
        - Agent stability score
        - Anomaly detection rate

        Args:
            metrics: Agent metrics from FAZA 28.5

        Returns:
            Tuple of (risk_score, factors_list)
        """
        factors = []

        # Agent failure rate (0-1)
        failure_rate = metrics.get("agent_failure_rate", 0.0)
        factors.append(RiskFactor(
            name="agent_failure_rate",
            value=failure_rate,
            weight=self.factor_weights["agent_failure_rate"],
            threshold=0.30,
            description="Agent failure rate"
        ))

        # Agent performance (0-1, inverted for risk)
        performance = metrics.get("agent_performance", 1.0)
        factors.append(RiskFactor(
            name="agent_performance",
            value=1.0 - performance,  # Invert: low performance = high risk
            weight=self.factor_weights["agent_performance"],
            threshold=0.60,
            description="Agent performance (inverted)"
        ))

        # Agent cooperation (0-1, inverted for risk)
        cooperation = metrics.get("agent_cooperation", 1.0)
        factors.append(RiskFactor(
            name="agent_cooperation",
            value=1.0 - cooperation,
            weight=self.factor_weights["agent_cooperation"],
            threshold=0.50,
            description="Agent cooperation (inverted)"
        ))

        # Agent stability (0-1, inverted for risk)
        stability = metrics.get("agent_stability", 1.0)
        factors.append(RiskFactor(
            name="agent_stability",
            value=1.0 - stability,
            weight=self.factor_weights["agent_stability"],
            threshold=0.60,
            description="Agent stability (inverted)"
        ))

        # Anomaly rate (0-1)
        anomaly_rate = metrics.get("anomaly_rate", 0.0)
        factors.append(RiskFactor(
            name="anomaly_rate",
            value=anomaly_rate,
            weight=self.factor_weights["anomaly_rate"],
            threshold=0.40,
            description="Agent anomaly detection rate"
        ))

        # Calculate weighted risk
        total_weight = sum(f.weight for f in factors)
        risk_score = sum(f.get_score() for f in factors) / total_weight * 100

        return risk_score, factors

    def _compute_graph_risk(self, metrics: Dict[str, Any]) -> tuple[float, List[RiskFactor]]:
        """
        Compute graph-level risk.

        Factors (from FAZA 27/27.5):
        - Graph complexity
        - Cycle count
        - Bottleneck count
        - Parallelization index
        - Execution delay
        - Task failure rate

        Args:
            metrics: Graph metrics from FAZA 27/27.5

        Returns:
            Tuple of (risk_score, factors_list)
        """
        factors = []

        # Graph complexity (normalized 0-1)
        complexity = metrics.get("graph_complexity", 0.0)
        factors.append(RiskFactor(
            name="graph_complexity",
            value=complexity,
            weight=self.factor_weights["graph_complexity"],
            threshold=0.75,
            description="Task graph complexity"
        ))

        # Cycle count (normalized)
        cycle_count = metrics.get("cycle_count", 0)
        cycle_risk = min(cycle_count / 5.0, 1.0)  # Normalize: 5+ cycles = max risk
        factors.append(RiskFactor(
            name="cycle_count",
            value=cycle_risk,
            weight=self.factor_weights["cycle_count"],
            threshold=0.20,
            description="Graph cycle count"
        ))

        # Bottleneck count (normalized)
        bottleneck_count = metrics.get("bottleneck_count", 0)
        bottleneck_risk = min(bottleneck_count / 10.0, 1.0)  # Normalize: 10+ bottlenecks = max
        factors.append(RiskFactor(
            name="bottleneck_count",
            value=bottleneck_risk,
            weight=self.factor_weights["bottleneck_count"],
            threshold=0.50,
            description="Graph bottleneck count"
        ))

        # Parallelization index (0-1, inverted for risk)
        parallel_index = metrics.get("parallelization_index", 0.5)
        factors.append(RiskFactor(
            name="parallelization_index",
            value=1.0 - parallel_index,  # Invert: low parallelization = high risk
            weight=abs(self.factor_weights["parallelization_index"]),
            threshold=0.70,
            description="Parallelization potential (inverted)"
        ))

        # Execution delay (0-1)
        execution_delay = metrics.get("execution_delay", 0.0)
        factors.append(RiskFactor(
            name="execution_delay",
            value=execution_delay,
            weight=self.factor_weights["execution_delay"],
            threshold=0.60,
            description="Execution delay ratio"
        ))

        # Task failure rate (0-1)
        task_failure_rate = metrics.get("task_failure_rate", 0.0)
        factors.append(RiskFactor(
            name="task_failure_rate",
            value=task_failure_rate,
            weight=self.factor_weights["task_failure_rate"],
            threshold=0.30,
            description="Task failure rate"
        ))

        # Calculate weighted risk
        total_weight = sum(f.weight for f in factors)
        risk_score = sum(f.get_score() for f in factors) / total_weight * 100

        return risk_score, factors

    def get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level classification.

        Args:
            risk_score: Risk score (0-100)

        Returns:
            Risk level: "low", "medium", "high", "critical"
        """
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"

    def get_statistics(self) -> Dict[str, Any]:
        """Get risk model statistics"""
        total = self.stats["assessments_performed"]
        return {
            "assessments_performed": total,
            "high_risk_count": self.stats["high_risk_count"],
            "medium_risk_count": self.stats["medium_risk_count"],
            "low_risk_count": self.stats["low_risk_count"],
            "high_risk_rate": self.stats["high_risk_count"] / max(total, 1),
            "medium_risk_rate": self.stats["medium_risk_count"] / max(total, 1),
            "low_risk_rate": self.stats["low_risk_count"] / max(total, 1)
        }

    def reset_statistics(self) -> None:
        """Reset statistics"""
        self.stats = {
            "assessments_performed": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }


def compute_risk(
    system_metrics: Optional[Dict[str, Any]] = None,
    agent_metrics: Optional[Dict[str, Any]] = None,
    graph_metrics: Optional[Dict[str, Any]] = None
) -> RiskBreakdown:
    """
    Convenience function to compute risk score.

    Args:
        system_metrics: System health metrics
        agent_metrics: Agent performance metrics
        graph_metrics: Graph health metrics

    Returns:
        RiskBreakdown with consolidated score
    """
    model = RiskModel()
    return model.compute_risk(system_metrics, agent_metrics, graph_metrics)


def create_risk_model() -> RiskModel:
    """
    Factory function to create RiskModel instance.

    Returns:
        RiskModel instance
    """
    return RiskModel()

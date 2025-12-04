"""
FAZA 30 – Classification Engine

Fault taxonomy and classification system for self-healing.

Provides:
- Fault taxonomy (operational, structural, agent-fault, governance drift, stability threat)
- Severity-based classification
- Root cause analysis
- Classification confidence scoring
- Fault pattern recognition

Architecture:
    FaultCategory - 5 main fault categories
    ClassificationResult - Classification outcome with confidence
    ClassificationEngine - Main classifier

Usage:
    from senti_os.core.faza30.classification_engine import ClassificationEngine

    engine = ClassificationEngine()
    result = engine.classify_fault(detected_fault)
    print(f"Category: {result.category}, Confidence: {result.confidence}")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re


class FaultCategory(Enum):
    """
    5-category fault taxonomy for FAZA 30.
    """
    OPERATIONAL = "operational"          # Runtime execution issues
    STRUCTURAL = "structural"            # Graph/system structure problems
    AGENT_FAULT = "agent_fault"         # Agent-specific failures
    GOVERNANCE_DRIFT = "governance_drift"  # Policy/governance violations
    STABILITY_THREAT = "stability_threat"  # System stability risks
    UNKNOWN = "unknown"                 # Unclassified


class RepairPriority(Enum):
    """Priority for repair actions."""
    IMMEDIATE = "immediate"     # < 1s - critical system issues
    URGENT = "urgent"          # < 10s - high severity
    HIGH = "high"              # < 60s - medium-high severity
    MEDIUM = "medium"          # < 5min - medium severity
    LOW = "low"                # < 30min - low severity
    DEFERRED = "deferred"      # > 30min - info/monitoring


@dataclass
class ClassificationResult:
    """
    Result of fault classification.

    Attributes:
        fault_id: Unique fault identifier
        category: Primary fault category
        subcategory: More specific classification
        confidence: Classification confidence (0.0-1.0)
        repair_priority: Urgency of repair
        root_cause: Identified root cause
        affected_components: List of affected system components
        recommended_actions: Suggested repair actions
        timestamp: When classification was performed
        metadata: Additional classification metadata
    """
    fault_id: str
    category: FaultCategory
    subcategory: str
    confidence: float
    repair_priority: RepairPriority
    root_cause: str
    affected_components: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ClassificationEngine:
    """
    Fault classification engine with 5-category taxonomy.

    Classifies detected faults into categories:
    - OPERATIONAL: Runtime execution failures
    - STRUCTURAL: Graph/topology issues
    - AGENT_FAULT: Agent-specific problems
    - GOVERNANCE_DRIFT: Policy violations
    - STABILITY_THREAT: System stability risks

    Features:
    - Pattern-based classification
    - Confidence scoring
    - Root cause analysis
    - Repair priority assignment
    - Historical pattern learning
    """

    def __init__(self):
        """Initialize classification engine."""
        self._classification_history: List[ClassificationResult] = []
        self._pattern_cache: Dict[str, FaultCategory] = {}
        self._stats = {
            "total_classifications": 0,
            "by_category": {cat: 0 for cat in FaultCategory},
            "by_priority": {pri: 0 for pri in RepairPriority},
            "avg_confidence": 0.0
        }

    def classify_fault(self, fault: Any) -> ClassificationResult:
        """
        Classify a detected fault.

        Args:
            fault: DetectedFault instance

        Returns:
            ClassificationResult with category, priority, and recommendations
        """
        # Extract fault attributes
        fault_type = getattr(fault, 'fault_type', 'unknown')
        severity = getattr(fault, 'severity', None)
        source = getattr(fault, 'source', None)
        description = getattr(fault, 'description', '')
        metrics = getattr(fault, 'metrics', {})

        # Step 1: Determine category
        category, confidence = self._determine_category(
            fault_type, source, description, metrics
        )

        # Step 2: Determine subcategory
        subcategory = self._determine_subcategory(
            category, fault_type, description
        )

        # Step 3: Assign repair priority
        repair_priority = self._assign_repair_priority(
            category, severity, metrics
        )

        # Step 4: Root cause analysis
        root_cause = self._analyze_root_cause(
            category, fault_type, description, metrics
        )

        # Step 5: Identify affected components
        affected_components = self._identify_affected_components(
            category, source, metrics
        )

        # Step 6: Generate recommended actions
        recommended_actions = self._generate_recommendations(
            category, subcategory, repair_priority, root_cause
        )

        # Create classification result
        result = ClassificationResult(
            fault_id=getattr(fault, 'fault_id', f"cls_{datetime.now().timestamp()}"),
            category=category,
            subcategory=subcategory,
            confidence=confidence,
            repair_priority=repair_priority,
            root_cause=root_cause,
            affected_components=affected_components,
            recommended_actions=recommended_actions,
            metadata={
                "fault_type": fault_type,
                "severity": str(severity) if severity else "unknown",
                "source": str(source) if source else "unknown"
            }
        )

        # Update history and stats
        self._classification_history.append(result)
        self._update_statistics(result)

        return result

    def _determine_category(
        self,
        fault_type: str,
        source: Any,
        description: str,
        metrics: Dict[str, Any]
    ) -> Tuple[FaultCategory, float]:
        """
        Determine fault category with confidence score.

        Returns:
            Tuple of (FaultCategory, confidence_score)
        """
        # Check pattern cache
        cache_key = f"{fault_type}_{source}"
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key], 0.95

        # Pattern matching for each category
        scores = {
            FaultCategory.OPERATIONAL: self._score_operational(fault_type, description, metrics),
            FaultCategory.STRUCTURAL: self._score_structural(fault_type, description, metrics),
            FaultCategory.AGENT_FAULT: self._score_agent_fault(fault_type, description, metrics),
            FaultCategory.GOVERNANCE_DRIFT: self._score_governance_drift(fault_type, description, metrics),
            FaultCategory.STABILITY_THREAT: self._score_stability_threat(fault_type, description, metrics)
        }

        # Select category with highest score
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]

        # Cache pattern if confidence is high
        if confidence > 0.85:
            self._pattern_cache[cache_key] = best_category

        return best_category, confidence

    def _score_operational(self, fault_type: str, desc: str, metrics: Dict) -> float:
        """Score likelihood of OPERATIONAL category."""
        score = 0.0

        # Keyword patterns
        operational_keywords = [
            'timeout', 'execution', 'runtime', 'task_failed',
            'agent_error', 'performance', 'latency', 'resource'
        ]

        for keyword in operational_keywords:
            if keyword in fault_type.lower() or keyword in desc.lower():
                score += 0.15

        # Metric patterns
        if metrics.get('execution_time', 0) > 10:
            score += 0.2
        if metrics.get('error_count', 0) > 0:
            score += 0.15
        if metrics.get('cpu_usage', 0) > 0.9:
            score += 0.1

        return min(score, 1.0)

    def _score_structural(self, fault_type: str, desc: str, metrics: Dict) -> float:
        """Score likelihood of STRUCTURAL category."""
        score = 0.0

        # Keyword patterns
        structural_keywords = [
            'cycle', 'graph', 'topology', 'bottleneck', 'deadlock',
            'dependency', 'circular', 'structure', 'node', 'edge'
        ]

        for keyword in structural_keywords:
            if keyword in fault_type.lower() or keyword in desc.lower():
                score += 0.15

        # Metric patterns
        if metrics.get('cycle_count', 0) > 0:
            score += 0.3
        if metrics.get('graph_complexity', 0) > 100:
            score += 0.2
        if metrics.get('bottleneck_detected', False):
            score += 0.2

        return min(score, 1.0)

    def _score_agent_fault(self, fault_type: str, desc: str, metrics: Dict) -> float:
        """Score likelihood of AGENT_FAULT category."""
        score = 0.0

        # Keyword patterns
        agent_keywords = [
            'agent', 'cooperation', 'communication', 'message',
            'handoff', 'delegation', 'agent_crash', 'agent_stall'
        ]

        for keyword in agent_keywords:
            if keyword in fault_type.lower() or keyword in desc.lower():
                score += 0.15

        # Metric patterns
        if metrics.get('agent_failure_rate', 0) > 0.1:
            score += 0.25
        if metrics.get('cooperation_score', 1.0) < 0.5:
            score += 0.2
        if metrics.get('agent_anomaly_detected', False):
            score += 0.25

        return min(score, 1.0)

    def _score_governance_drift(self, fault_type: str, desc: str, metrics: Dict) -> float:
        """Score likelihood of GOVERNANCE_DRIFT category."""
        score = 0.0

        # Keyword patterns
        governance_keywords = [
            'governance', 'policy', 'violation', 'rule', 'override',
            'permission', 'threshold', 'limit', 'constraint'
        ]

        for keyword in governance_keywords:
            if keyword in fault_type.lower() or keyword in desc.lower():
                score += 0.15

        # Metric patterns
        if metrics.get('governance_violations', 0) > 0:
            score += 0.3
        if metrics.get('policy_drift', 0) > 0.2:
            score += 0.2
        if metrics.get('override_count', 0) > 5:
            score += 0.15

        return min(score, 1.0)

    def _score_stability_threat(self, fault_type: str, desc: str, metrics: Dict) -> float:
        """Score likelihood of STABILITY_THREAT category."""
        score = 0.0

        # Keyword patterns
        stability_keywords = [
            'instability', 'oscillation', 'cascade', 'runaway',
            'instable', 'unstable', 'divergence', 'chaos', 'thrashing'
        ]

        for keyword in stability_keywords:
            if keyword in fault_type.lower() or keyword in desc.lower():
                score += 0.15

        # Metric patterns
        if metrics.get('stability_score', 1.0) < 0.5:
            score += 0.3
        if metrics.get('oscillation_detected', False):
            score += 0.25
        if metrics.get('cascade_risk', 0) > 0.7:
            score += 0.2

        return min(score, 1.0)

    def _determine_subcategory(
        self,
        category: FaultCategory,
        fault_type: str,
        description: str
    ) -> str:
        """Determine more specific subcategory."""
        subcategory_map = {
            FaultCategory.OPERATIONAL: [
                "execution_timeout", "resource_exhaustion",
                "task_failure", "performance_degradation"
            ],
            FaultCategory.STRUCTURAL: [
                "circular_dependency", "bottleneck",
                "graph_complexity", "topology_issue"
            ],
            FaultCategory.AGENT_FAULT: [
                "agent_crash", "cooperation_failure",
                "communication_breakdown", "agent_stall"
            ],
            FaultCategory.GOVERNANCE_DRIFT: [
                "policy_violation", "threshold_breach",
                "rule_conflict", "override_abuse"
            ],
            FaultCategory.STABILITY_THREAT: [
                "oscillation", "cascade_failure",
                "runaway_process", "feedback_loop"
            ]
        }

        # Match subcategory based on keywords
        subcategories = subcategory_map.get(category, [])
        for subcat in subcategories:
            if subcat.replace("_", " ") in description.lower():
                return subcat
            if subcat.replace("_", " ") in fault_type.lower():
                return subcat

        # Default subcategory
        return f"{category.value}_general"

    def _assign_repair_priority(
        self,
        category: FaultCategory,
        severity: Any,
        metrics: Dict[str, Any]
    ) -> RepairPriority:
        """Assign repair priority based on category and severity."""
        severity_str = str(severity).lower() if severity else "unknown"

        # Critical severity always gets immediate priority
        if "critical" in severity_str:
            return RepairPriority.IMMEDIATE

        # Category-based priorities
        if category == FaultCategory.STABILITY_THREAT:
            return RepairPriority.IMMEDIATE

        if category == FaultCategory.GOVERNANCE_DRIFT:
            if metrics.get('governance_violations', 0) > 10:
                return RepairPriority.URGENT
            return RepairPriority.HIGH

        if category == FaultCategory.STRUCTURAL:
            if metrics.get('cycle_count', 0) > 5:
                return RepairPriority.URGENT
            return RepairPriority.HIGH

        if category == FaultCategory.AGENT_FAULT:
            if metrics.get('agent_failure_rate', 0) > 0.5:
                return RepairPriority.URGENT
            return RepairPriority.MEDIUM

        if category == FaultCategory.OPERATIONAL:
            if "high" in severity_str:
                return RepairPriority.HIGH
            return RepairPriority.MEDIUM

        return RepairPriority.LOW

    def _analyze_root_cause(
        self,
        category: FaultCategory,
        fault_type: str,
        description: str,
        metrics: Dict[str, Any]
    ) -> str:
        """Analyze and identify root cause."""
        root_causes = []

        if category == FaultCategory.OPERATIONAL:
            if metrics.get('cpu_usage', 0) > 0.9:
                root_causes.append("CPU resource exhaustion")
            if metrics.get('memory_usage', 0) > 0.9:
                root_causes.append("Memory pressure")
            if metrics.get('execution_time', 0) > 30:
                root_causes.append("Task execution timeout")

        elif category == FaultCategory.STRUCTURAL:
            if metrics.get('cycle_count', 0) > 0:
                root_causes.append(f"Circular dependencies detected ({metrics.get('cycle_count')} cycles)")
            if metrics.get('bottleneck_detected', False):
                root_causes.append("Graph bottleneck")

        elif category == FaultCategory.AGENT_FAULT:
            if metrics.get('agent_failure_rate', 0) > 0.3:
                root_causes.append("High agent failure rate")
            if metrics.get('cooperation_score', 1.0) < 0.5:
                root_causes.append("Agent cooperation breakdown")

        elif category == FaultCategory.GOVERNANCE_DRIFT:
            if metrics.get('governance_violations', 0) > 0:
                root_causes.append(f"{metrics.get('governance_violations')} governance violations")
            if metrics.get('override_count', 0) > 5:
                root_causes.append("Excessive override usage")

        elif category == FaultCategory.STABILITY_THREAT:
            if metrics.get('stability_score', 1.0) < 0.5:
                root_causes.append("System instability detected")
            if metrics.get('oscillation_detected', False):
                root_causes.append("Feedback oscillation")

        if not root_causes:
            return f"Unknown root cause for {fault_type}"

        return "; ".join(root_causes)

    def _identify_affected_components(
        self,
        category: FaultCategory,
        source: Any,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Identify which system components are affected."""
        components = []

        # Add source as affected component
        if source:
            components.append(str(source))

        # Category-specific components
        if category == FaultCategory.STRUCTURAL:
            components.extend(["task_graph", "graph_optimizer"])

        if category == FaultCategory.AGENT_FAULT:
            components.extend(["agent_execution_loop", "agent_coordinator"])

        if category == FaultCategory.GOVERNANCE_DRIFT:
            components.extend(["governance_engine", "policy_manager"])

        if category == FaultCategory.OPERATIONAL:
            components.extend(["orchestrator", "scheduler"])

        if category == FaultCategory.STABILITY_THREAT:
            components.extend(["feedback_loop", "meta_layer", "takeover_manager"])

        return list(set(components))  # Remove duplicates

    def _generate_recommendations(
        self,
        category: FaultCategory,
        subcategory: str,
        priority: RepairPriority,
        root_cause: str
    ) -> List[str]:
        """Generate repair action recommendations."""
        recommendations = []

        if category == FaultCategory.OPERATIONAL:
            recommendations.extend([
                "Retry failed task with exponential backoff",
                "Scale resources if resource exhaustion detected",
                "Reschedule task to different agent/slot"
            ])

        elif category == FaultCategory.STRUCTURAL:
            recommendations.extend([
                "Break circular dependencies",
                "Optimize graph topology",
                "Redistribute bottleneck load"
            ])

        elif category == FaultCategory.AGENT_FAULT:
            recommendations.extend([
                "Restart failing agent",
                "Reassign tasks to healthy agents",
                "Investigate agent cooperation issues"
            ])

        elif category == FaultCategory.GOVERNANCE_DRIFT:
            recommendations.extend([
                "Review and adjust governance policies",
                "Investigate override usage patterns",
                "Recalibrate thresholds"
            ])

        elif category == FaultCategory.STABILITY_THREAT:
            recommendations.extend([
                "Engage FAZA 29 takeover if needed",
                "Apply feedback loop damping",
                "Reduce system load temporarily"
            ])

        # Add priority-specific recommendations
        if priority == RepairPriority.IMMEDIATE:
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED - Consider system takeover")

        return recommendations

    def _update_statistics(self, result: ClassificationResult) -> None:
        """Update classification statistics."""
        self._stats["total_classifications"] += 1
        self._stats["by_category"][result.category] += 1
        self._stats["by_priority"][result.repair_priority] += 1

        # Update average confidence (rolling average)
        total = self._stats["total_classifications"]
        current_avg = self._stats["avg_confidence"]
        new_avg = (current_avg * (total - 1) + result.confidence) / total
        self._stats["avg_confidence"] = new_avg

    def get_statistics(self) -> Dict[str, Any]:
        """Get classification statistics."""
        return {
            **self._stats,
            "history_size": len(self._classification_history),
            "pattern_cache_size": len(self._pattern_cache)
        }

    def get_recent_classifications(self, limit: int = 10) -> List[ClassificationResult]:
        """Get recent classification results."""
        return self._classification_history[-limit:]

    def clear_cache(self) -> None:
        """Clear pattern cache."""
        self._pattern_cache.clear()


def create_classification_engine() -> ClassificationEngine:
    """
    Factory function to create ClassificationEngine.

    Returns:
        Initialized ClassificationEngine instance
    """
    return ClassificationEngine()

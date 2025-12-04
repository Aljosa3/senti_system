"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Oversight Agent

Enterprise meta-agent that monitors all agents:
- Subscribes to ALL events from FAZA 28 event bus
- Maintains agent performance timeline
- Detects drift, lag, crashes, overload
- Triggers Stability Engine and Strategy Adapter
- Updates shared state in FAZA 28 state_context
- Produces periodic "System Meta-Report"

This is the main orchestrator for FAZA 28.5.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class OversightAgent:
    """
    Enterprise oversight meta-agent.

    Monitors all agents in FAZA 28 AEL and coordinates
    all FAZA 28.5 subsystems (scoring, detection, stability, adaptation).

    Responsibilities:
    - Subscribe to all FAZA 28 events
    - Track agent performance over time
    - Detect problems (drift, lag, crashes, overload)
    - Trigger stability analysis
    - Trigger anomaly detection
    - Apply policy decisions
    - Adapt system strategy
    - Generate meta-reports
    """

    def __init__(
        self,
        report_interval: float = 60.0,
        monitoring_enabled: bool = True
    ):
        """
        Initialize oversight agent.

        Args:
            report_interval: Interval for meta-report generation (seconds)
            monitoring_enabled: Enable/disable monitoring
        """
        self.report_interval = report_interval
        self.monitoring_enabled = monitoring_enabled

        # Will be set by integration_layer
        self.scorer = None
        self.anomaly_detector = None
        self.stability_engine = None
        self.policy_manager = None
        self.strategy_adapter = None

        # Tracking
        self.agent_observations: Dict[str, List[Dict[str, Any]]] = {}
        self.last_report_time: Optional[datetime] = None
        self.meta_reports: List[Dict[str, Any]] = []
        self.max_report_history = 100

        # Statistics
        self.total_events_observed = 0
        self.total_adaptations = 0
        self.total_policy_triggers = 0

        logger.info("OversightAgent initialized")

    async def on_start(self, context: Any) -> None:
        """
        Called when oversight agent starts.

        Args:
            context: StateContext from FAZA 28

        TODO: Subscribe to all FAZA 28 events
        TODO: Initialize subsystems
        """
        logger.info("OversightAgent starting...")

        # Store initial state
        if context:
            context.set("oversight_active", True)
            context.set("oversight_start_time", datetime.now().isoformat())

        self.last_report_time = datetime.now()

        logger.info("OversightAgent started")

    async def on_tick(self, context: Any) -> None:
        """
        Called each AEL loop iteration.

        Performs monitoring and coordination:
        1. Collect agent metrics
        2. Calculate scores
        3. Detect anomalies
        4. Analyze stability
        5. Evaluate policies
        6. Adapt strategy
        7. Generate reports (periodic)

        Args:
            context: StateContext from FAZA 28

        TODO: Implement full monitoring pipeline
        """
        if not self.monitoring_enabled:
            return

        # 1. Collect agent metrics (from context or agent_manager)
        agent_metrics = self._collect_agent_metrics(context)

        # 2. Calculate scores
        if self.scorer:
            for agent_name, metrics in agent_metrics.items():
                self.scorer.record_tick(
                    agent_name=agent_name,
                    execution_time=metrics.get("avg_execution_time", 0),
                    had_error=metrics.get("error_count", 0) > 0
                )

            scores = self.scorer.get_all_scores()
        else:
            scores = {}

        # 3. Detect anomalies
        anomalies = []
        if self.anomaly_detector:
            for agent_name, score in scores.items():
                detected = self.anomaly_detector.detect_all(
                    agent_name=agent_name,
                    current_score=score.meta_score,
                    tick_time=datetime.now(),
                    metrics=agent_metrics.get(agent_name, {})
                )
                anomalies.extend(detected)

        # 4. Analyze stability
        stability_issues = []
        if self.stability_engine:
            system_metrics = self._collect_system_metrics(context, agent_metrics)
            stability_issues = self.stability_engine.analyze_stability(
                agent_metrics=agent_metrics,
                system_metrics=system_metrics
            )

        # 5. Evaluate policies
        policy_decisions = []
        if self.policy_manager:
            for agent_name, score in scores.items():
                policy_context = {
                    "agent_score": score,
                    "agent_metrics": agent_metrics.get(agent_name, {}),
                    "has_anomalies": len([a for a in anomalies if a.agent_name == agent_name]) > 0,
                    "has_stability_issues": len([s for s in stability_issues if agent_name in s.affected_agents]) > 0
                }
                decisions = self.policy_manager.evaluate_all(policy_context)
                policy_decisions.extend(decisions)

            self.total_policy_triggers += len(policy_decisions)

        # 6. Adapt strategy
        adaptations = []
        if self.strategy_adapter:
            system_metrics = self._collect_system_metrics(context, agent_metrics)
            adaptations = self.strategy_adapter.adapt_system(
                system_metrics=system_metrics,
                agent_scores={name: s.__dict__ for name, s in scores.items()},
                anomalies=anomalies,
                stability_issues=stability_issues
            )

            self.total_adaptations += len(adaptations)

        # 7. Update state
        if context:
            context.set("oversight_anomalies", len(anomalies))
            context.set("oversight_stability_issues", len(stability_issues))
            context.set("oversight_policy_triggers", len(policy_decisions))
            context.set("oversight_adaptations", len(adaptations))

        # 8. Generate meta-report (periodic)
        if self._should_generate_report():
            report = self._generate_meta_report(
                agent_metrics=agent_metrics,
                scores=scores,
                anomalies=anomalies,
                stability_issues=stability_issues,
                policy_decisions=policy_decisions,
                adaptations=adaptations
            )

            self.meta_reports.append(report)

            # Limit history
            if len(self.meta_reports) > self.max_report_history:
                self.meta_reports = self.meta_reports[-self.max_report_history:]

            # Store in context
            if context:
                context.set("oversight_last_report", report)

            logger.info(f"Meta-report generated: {report['summary']}")

    async def on_event(self, event: Any, context: Any) -> None:
        """
        Called when an event is received.

        Oversight agent subscribes to ALL events from FAZA 28.

        Args:
            event: Event object from FAZA 28
            context: StateContext

        TODO: Process different event types
        TODO: Record agent interactions
        """
        self.total_events_observed += 1

        # Extract event info
        event_type = getattr(event, "type", "unknown")
        source = getattr(event, "source", "unknown")

        # Record observation
        if source not in self.agent_observations:
            self.agent_observations[source] = []

        self.agent_observations[source].append({
            "event_type": event_type,
            "timestamp": datetime.now(),
            "data": getattr(event, "data", None)
        })

        # Limit observation history
        if len(self.agent_observations[source]) > 100:
            self.agent_observations[source] = self.agent_observations[source][-100:]

        # Record interaction for stability analysis
        if self.stability_engine and event_type == "agent_interaction":
            data = getattr(event, "data", {})
            target = data.get("target_agent")
            if target:
                self.stability_engine.record_interaction(source, target)

    async def on_error(self, error: Exception, context: Any) -> None:
        """
        Called on error.

        Args:
            error: Exception that occurred
            context: StateContext
        """
        logger.error(f"OversightAgent error: {error}")

        # Store error in context
        if context:
            errors = context.get("oversight_errors", [])
            errors.append({
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            })
            context.set("oversight_errors", errors[-10:])  # Keep last 10

    async def on_shutdown(self, context: Any) -> None:
        """
        Called on shutdown.

        Args:
            context: StateContext
        """
        logger.info("OversightAgent shutting down...")

        # Generate final report
        if context:
            final_report = {
                "type": "final_report",
                "timestamp": datetime.now().isoformat(),
                "total_events_observed": self.total_events_observed,
                "total_adaptations": self.total_adaptations,
                "total_policy_triggers": self.total_policy_triggers,
                "total_reports": len(self.meta_reports)
            }

            context.set("oversight_final_report", final_report)
            context.set("oversight_active", False)

        logger.info("OversightAgent shutdown complete")

    def _collect_agent_metrics(self, context: Any) -> Dict[str, Dict[str, Any]]:
        """
        Collect metrics for all agents.

        Args:
            context: StateContext

        Returns:
            Dictionary of agent_name -> metrics

        TODO: Integrate with FAZA 28 agent_manager
        """
        # Placeholder - in production, would query agent_manager
        metrics = {}

        if context:
            # Try to get metrics from context
            for key in ["agent_metrics", "agents_status"]:
                data = context.get(key, {})
                if data:
                    metrics.update(data)

        return metrics

    def _collect_system_metrics(
        self,
        context: Any,
        agent_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect system-wide metrics.

        Args:
            context: StateContext
            agent_metrics: Agent metrics

        Returns:
            Dictionary of system metrics
        """
        metrics = {
            "total_agents": len(agent_metrics),
            "active_agents": len([m for m in agent_metrics.values() if m.get("active", False)]),
            "system_load": 0.5,  # Placeholder
            "timestamp": datetime.now().isoformat()
        }

        if self.scorer:
            scorer_stats = self.scorer.get_stats()
            metrics.update(scorer_stats)

        return metrics

    def _should_generate_report(self) -> bool:
        """
        Check if it's time to generate a meta-report.

        Returns:
            True if report should be generated
        """
        if self.last_report_time is None:
            return True

        time_since_report = (datetime.now() - self.last_report_time).total_seconds()
        return time_since_report >= self.report_interval

    def _generate_meta_report(
        self,
        agent_metrics: Dict[str, Any],
        scores: Dict[str, Any],
        anomalies: List[Any],
        stability_issues: List[Any],
        policy_decisions: List[Any],
        adaptations: List[Any]
    ) -> Dict[str, Any]:
        """
        Generate system meta-report.

        Args:
            agent_metrics: Agent metrics
            scores: Agent scores
            anomalies: Detected anomalies
            stability_issues: Stability issues
            policy_decisions: Policy decisions
            adaptations: System adaptations

        Returns:
            Meta-report dictionary
        """
        self.last_report_time = datetime.now()

        # Calculate summary stats
        if scores:
            avg_score = sum(s.meta_score for s in scores.values()) / len(scores)
            top_agents = sorted(scores.items(), key=lambda x: x[1].meta_score, reverse=True)[:3]
            worst_agents = sorted(scores.items(), key=lambda x: x[1].meta_score)[:3]
        else:
            avg_score = 0.0
            top_agents = []
            worst_agents = []

        critical_anomalies = [a for a in anomalies if hasattr(a, "severity") and a.severity.value >= 3]
        critical_stability = [s for s in stability_issues if hasattr(s, "severity") and s.severity >= 0.7]

        report = {
            "type": "system_meta_report",
            "timestamp": self.last_report_time.isoformat(),
            "interval": self.report_interval,

            # Agent metrics
            "total_agents": len(agent_metrics),
            "agents_with_scores": len(scores),

            # Scores
            "avg_meta_score": avg_score,
            "top_agents": [name for name, _ in top_agents],
            "worst_agents": [name for name, _ in worst_agents],

            # Issues
            "total_anomalies": len(anomalies),
            "critical_anomalies": len(critical_anomalies),
            "total_stability_issues": len(stability_issues),
            "critical_stability_issues": len(critical_stability),

            # Actions
            "policy_triggers": len(policy_decisions),
            "adaptations": len(adaptations),

            # Summary
            "summary": self._generate_summary(
                avg_score, len(anomalies), len(stability_issues), len(adaptations)
            )
        }

        return report

    def _generate_summary(
        self,
        avg_score: float,
        anomaly_count: int,
        stability_count: int,
        adaptation_count: int
    ) -> str:
        """
        Generate human-readable summary.

        Args:
            avg_score: Average agent score
            anomaly_count: Number of anomalies
            stability_count: Number of stability issues
            adaptation_count: Number of adaptations

        Returns:
            Summary string
        """
        if avg_score > 0.8 and anomaly_count == 0 and stability_count == 0:
            status = "HEALTHY"
        elif avg_score > 0.6 and anomaly_count < 5 and stability_count < 2:
            status = "STABLE"
        elif avg_score > 0.4:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        return f"System {status}: avg_score={avg_score:.3f}, anomalies={anomaly_count}, stability_issues={stability_count}, adaptations={adaptation_count}"

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Get latest meta-report.

        Returns:
            Latest report or None
        """
        return self.meta_reports[-1] if self.meta_reports else None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get oversight agent statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "report_interval": self.report_interval,
            "total_events_observed": self.total_events_observed,
            "total_adaptations": self.total_adaptations,
            "total_policy_triggers": self.total_policy_triggers,
            "total_reports": len(self.meta_reports),
            "agents_monitored": len(self.agent_observations)
        }

    def __repr__(self) -> str:
        return f"<OversightAgent: {len(self.meta_reports)} reports generated>"


# Singleton instance
_oversight_agent_instance: Optional[OversightAgent] = None


def get_oversight_agent() -> OversightAgent:
    """
    Get singleton OversightAgent instance.

    Returns:
        Global OversightAgent instance
    """
    global _oversight_agent_instance
    if _oversight_agent_instance is None:
        _oversight_agent_instance = OversightAgent()
    return _oversight_agent_instance


def create_oversight_agent(**kwargs) -> OversightAgent:
    """
    Factory function: create new OversightAgent instance.

    Args:
        **kwargs: Arguments passed to OversightAgent constructor

    Returns:
        New OversightAgent instance
    """
    return OversightAgent(**kwargs)

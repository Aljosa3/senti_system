"""
FAZA 28.5 – Meta-Agent Oversight Layer (Enterprise Edition)
Agent Scorer

Provides comprehensive scoring for all agents:
- Performance score (execution time, throughput)
- Reliability score (error rate, uptime)
- Cooperation score (event responsiveness, state usage)
- Stability risk score (variance, anomalies)
- Meta-score (combined weighted score)

All scores are time-weighted and normalized (0.0 - 1.0).
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """
    Metrics tracked for each agent.

    Attributes:
        agent_name: Name of agent
        tick_count: Total ticks executed
        error_count: Total errors encountered
        avg_execution_time: Average tick execution time (seconds)
        last_tick_time: Timestamp of last tick
        events_received: Total events received
        events_emitted: Total events emitted
        state_reads: Total state reads
        state_writes: Total state writes
        uptime: Total uptime in seconds
        created_at: Timestamp of first observation
    """
    agent_name: str
    tick_count: int = 0
    error_count: int = 0
    avg_execution_time: float = 0.0
    last_tick_time: Optional[datetime] = None
    events_received: int = 0
    events_emitted: int = 0
    state_reads: int = 0
    state_writes: int = 0
    uptime: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    # Time-series data (last 100 observations)
    execution_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_times: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class AgentScore:
    """
    Comprehensive scoring for an agent.

    All scores normalized to 0.0 - 1.0 range (higher is better).
    """
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Individual scores (0.0 - 1.0)
    performance_score: float = 0.5
    reliability_score: float = 0.5
    cooperation_score: float = 0.5
    stability_risk_score: float = 0.5  # Lower risk = higher score

    # Combined meta-score (weighted average)
    meta_score: float = 0.5

    # Score components breakdown
    components: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<AgentScore: {self.agent_name} meta={self.meta_score:.3f}>"


class AgentScorer:
    """
    Enterprise agent scoring engine.

    Calculates time-weighted, normalized scores for all agents based on:
    - Performance: Execution efficiency, throughput
    - Reliability: Error rate, uptime, consistency
    - Cooperation: Event handling, state usage, responsiveness
    - Stability Risk: Variance, anomalies, degradation

    Scores are updated periodically and cached for performance.
    """

    def __init__(
        self,
        performance_weight: float = 0.3,
        reliability_weight: float = 0.3,
        cooperation_weight: float = 0.2,
        stability_weight: float = 0.2,
        time_decay: float = 0.9
    ):
        """
        Initialize agent scorer.

        Args:
            performance_weight: Weight for performance score (0.0-1.0)
            reliability_weight: Weight for reliability score (0.0-1.0)
            cooperation_weight: Weight for cooperation score (0.0-1.0)
            stability_weight: Weight for stability risk score (0.0-1.0)
            time_decay: Time decay factor for exponential moving average

        Note: Weights should sum to 1.0
        """
        self.performance_weight = performance_weight
        self.reliability_weight = reliability_weight
        self.cooperation_weight = cooperation_weight
        self.stability_weight = stability_weight
        self.time_decay = time_decay

        # Metrics storage
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.agent_scores: Dict[str, AgentScore] = {}

        # Scoring parameters
        self.target_execution_time = 0.1  # Target 100ms per tick
        self.max_error_rate = 0.05  # 5% max error rate
        self.min_events_threshold = 10  # Minimum events for cooperation score

        logger.info("AgentScorer initialized")

    def record_tick(
        self,
        agent_name: str,
        execution_time: float,
        had_error: bool = False
    ) -> None:
        """
        Record agent tick execution.

        Args:
            agent_name: Name of agent
            execution_time: Execution time in seconds
            had_error: Whether an error occurred

        TODO: Add tick timeout detection
        TODO: Track consecutive errors
        """
        metrics = self._get_or_create_metrics(agent_name)

        metrics.tick_count += 1
        metrics.last_tick_time = datetime.now()
        metrics.execution_times.append(execution_time)

        # Update average execution time (exponential moving average)
        if metrics.avg_execution_time == 0:
            metrics.avg_execution_time = execution_time
        else:
            metrics.avg_execution_time = (
                self.time_decay * metrics.avg_execution_time +
                (1 - self.time_decay) * execution_time
            )

        if had_error:
            metrics.error_count += 1
            metrics.error_times.append(datetime.now())

        # Update uptime
        if metrics.created_at:
            metrics.uptime = (datetime.now() - metrics.created_at).total_seconds()

    def record_event(
        self,
        agent_name: str,
        event_type: str,
        is_received: bool = True
    ) -> None:
        """
        Record agent event activity.

        Args:
            agent_name: Name of agent
            event_type: Type of event
            is_received: True if received, False if emitted

        TODO: Track event response times
        TODO: Track event patterns
        """
        metrics = self._get_or_create_metrics(agent_name)

        if is_received:
            metrics.events_received += 1
        else:
            metrics.events_emitted += 1

    def record_state_access(
        self,
        agent_name: str,
        is_read: bool = True
    ) -> None:
        """
        Record agent state access.

        Args:
            agent_name: Name of agent
            is_read: True if read, False if write

        TODO: Track state access patterns
        TODO: Detect excessive state access
        """
        metrics = self._get_or_create_metrics(agent_name)

        if is_read:
            metrics.state_reads += 1
        else:
            metrics.state_writes += 1

    def calculate_score(self, agent_name: str) -> AgentScore:
        """
        Calculate comprehensive score for an agent.

        Args:
            agent_name: Name of agent

        Returns:
            AgentScore with all calculated scores

        TODO: Add score caching with TTL
        TODO: Add score change detection
        """
        metrics = self._get_or_create_metrics(agent_name)

        # Calculate individual scores
        performance = self._calculate_performance_score(metrics)
        reliability = self._calculate_reliability_score(metrics)
        cooperation = self._calculate_cooperation_score(metrics)
        stability = self._calculate_stability_score(metrics)

        # Calculate weighted meta-score
        meta = (
            performance * self.performance_weight +
            reliability * self.reliability_weight +
            cooperation * self.cooperation_weight +
            stability * self.stability_weight
        )

        # Create score object
        score = AgentScore(
            agent_name=agent_name,
            performance_score=performance,
            reliability_score=reliability,
            cooperation_score=cooperation,
            stability_risk_score=stability,
            meta_score=meta,
            components={
                "tick_count": metrics.tick_count,
                "error_count": metrics.error_count,
                "avg_execution_time": metrics.avg_execution_time,
                "events_total": metrics.events_received + metrics.events_emitted,
                "uptime": metrics.uptime
            }
        )

        # Cache score
        self.agent_scores[agent_name] = score

        return score

    def _calculate_performance_score(self, metrics: AgentMetrics) -> float:
        """
        Calculate performance score (0.0 - 1.0).

        Based on:
        - Execution time vs target
        - Throughput (ticks per second)
        - Execution time stability

        Returns:
            Performance score (higher is better)
        """
        if metrics.tick_count == 0:
            return 0.5  # Neutral for no data

        # Score based on execution time
        if metrics.avg_execution_time > 0:
            time_score = min(1.0, self.target_execution_time / metrics.avg_execution_time)
        else:
            time_score = 1.0

        # Score based on throughput
        if metrics.uptime > 0:
            throughput = metrics.tick_count / metrics.uptime
            # Normalize: 1 tick/sec = 0.5, 10 ticks/sec = 1.0
            throughput_score = min(1.0, throughput / 10.0)
        else:
            throughput_score = 0.5

        # Score based on execution time variance (stability)
        if len(metrics.execution_times) > 1:
            variance = statistics.variance(metrics.execution_times)
            # Lower variance = higher score
            variance_score = max(0.0, 1.0 - variance)
        else:
            variance_score = 0.5

        # Weighted average
        performance = (time_score * 0.5 + throughput_score * 0.3 + variance_score * 0.2)

        return max(0.0, min(1.0, performance))

    def _calculate_reliability_score(self, metrics: AgentMetrics) -> float:
        """
        Calculate reliability score (0.0 - 1.0).

        Based on:
        - Error rate
        - Uptime
        - Consecutive success rate

        Returns:
            Reliability score (higher is better)
        """
        if metrics.tick_count == 0:
            return 0.5  # Neutral for no data

        # Error rate score
        error_rate = metrics.error_count / metrics.tick_count
        error_score = max(0.0, 1.0 - (error_rate / self.max_error_rate))

        # Uptime score (longer uptime = higher reliability)
        # Normalize: 1 hour = 0.5, 24 hours = 1.0
        uptime_hours = metrics.uptime / 3600
        uptime_score = min(1.0, uptime_hours / 24.0)

        # Recent error score (no recent errors = better)
        recent_error_score = 1.0
        if len(metrics.error_times) > 0:
            last_error = metrics.error_times[-1]
            time_since_error = (datetime.now() - last_error).total_seconds()
            # No error in last hour = 1.0, error in last minute = 0.0
            recent_error_score = min(1.0, time_since_error / 3600.0)

        # Weighted average
        reliability = (error_score * 0.5 + uptime_score * 0.3 + recent_error_score * 0.2)

        return max(0.0, min(1.0, reliability))

    def _calculate_cooperation_score(self, metrics: AgentMetrics) -> float:
        """
        Calculate cooperation score (0.0 - 1.0).

        Based on:
        - Event activity (received and emitted)
        - State usage (reads and writes)
        - Responsiveness

        Returns:
            Cooperation score (higher is better)
        """
        if metrics.tick_count == 0:
            return 0.5  # Neutral for no data

        # Event activity score
        total_events = metrics.events_received + metrics.events_emitted
        if total_events < self.min_events_threshold:
            event_score = total_events / self.min_events_threshold
        else:
            # Normalize: 100 events = 1.0
            event_score = min(1.0, total_events / 100.0)

        # State usage score
        total_state_access = metrics.state_reads + metrics.state_writes
        if total_state_access < 10:
            state_score = total_state_access / 10.0
        else:
            # Normalize: 50 accesses = 1.0
            state_score = min(1.0, total_state_access / 50.0)

        # Responsiveness score (recent activity)
        if metrics.last_tick_time:
            time_since_tick = (datetime.now() - metrics.last_tick_time).total_seconds()
            # Active in last 10 seconds = 1.0
            responsiveness_score = max(0.0, 1.0 - (time_since_tick / 60.0))
        else:
            responsiveness_score = 0.0

        # Weighted average
        cooperation = (event_score * 0.4 + state_score * 0.3 + responsiveness_score * 0.3)

        return max(0.0, min(1.0, cooperation))

    def _calculate_stability_score(self, metrics: AgentMetrics) -> float:
        """
        Calculate stability risk score (0.0 - 1.0).

        Based on:
        - Execution time variance
        - Error frequency variance
        - Recent degradation

        Returns:
            Stability score (higher is better, means lower risk)
        """
        if metrics.tick_count < 10:
            return 0.5  # Neutral for insufficient data

        # Execution time stability
        if len(metrics.execution_times) > 1:
            mean_time = statistics.mean(metrics.execution_times)
            stdev_time = statistics.stdev(metrics.execution_times)
            if mean_time > 0:
                cv = stdev_time / mean_time  # Coefficient of variation
                # Low CV = high stability
                time_stability = max(0.0, 1.0 - cv)
            else:
                time_stability = 1.0
        else:
            time_stability = 0.5

        # Error frequency stability
        if len(metrics.error_times) > 1:
            # Check if errors are increasing
            recent_errors = len([t for t in metrics.error_times if (datetime.now() - t).total_seconds() < 300])
            error_stability = max(0.0, 1.0 - (recent_errors / 10.0))
        else:
            error_stability = 1.0

        # Performance degradation detection
        if len(metrics.execution_times) >= 20:
            # Compare recent vs historical
            recent = list(metrics.execution_times)[-10:]
            historical = list(metrics.execution_times)[:10]
            recent_avg = statistics.mean(recent)
            historical_avg = statistics.mean(historical)

            if historical_avg > 0:
                degradation = (recent_avg - historical_avg) / historical_avg
                degradation_score = max(0.0, 1.0 - degradation)
            else:
                degradation_score = 1.0
        else:
            degradation_score = 0.5

        # Weighted average
        stability = (time_stability * 0.4 + error_stability * 0.4 + degradation_score * 0.2)

        return max(0.0, min(1.0, stability))

    def get_all_scores(self) -> Dict[str, AgentScore]:
        """
        Get scores for all tracked agents.

        Returns:
            Dictionary of agent_name -> AgentScore
        """
        scores = {}
        for agent_name in self.agent_metrics.keys():
            scores[agent_name] = self.calculate_score(agent_name)
        return scores

    def get_top_agents(self, n: int = 5, metric: str = "meta_score") -> List[AgentScore]:
        """
        Get top N agents by specified metric.

        Args:
            n: Number of agents to return
            metric: Metric to sort by (meta_score, performance_score, etc.)

        Returns:
            List of top AgentScore objects
        """
        all_scores = self.get_all_scores()
        sorted_scores = sorted(
            all_scores.values(),
            key=lambda s: getattr(s, metric, 0),
            reverse=True
        )
        return sorted_scores[:n]

    def get_worst_agents(self, n: int = 5, metric: str = "meta_score") -> List[AgentScore]:
        """
        Get worst N agents by specified metric.

        Args:
            n: Number of agents to return
            metric: Metric to sort by

        Returns:
            List of worst AgentScore objects
        """
        all_scores = self.get_all_scores()
        sorted_scores = sorted(
            all_scores.values(),
            key=lambda s: getattr(s, metric, 0),
            reverse=False
        )
        return sorted_scores[:n]

    def _get_or_create_metrics(self, agent_name: str) -> AgentMetrics:
        """
        Get or create metrics for an agent.

        Args:
            agent_name: Name of agent

        Returns:
            AgentMetrics object
        """
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        return self.agent_metrics[agent_name]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scorer statistics.

        Returns:
            Dictionary with statistics
        """
        all_scores = self.get_all_scores()

        if all_scores:
            avg_meta_score = statistics.mean([s.meta_score for s in all_scores.values()])
            avg_performance = statistics.mean([s.performance_score for s in all_scores.values()])
            avg_reliability = statistics.mean([s.reliability_score for s in all_scores.values()])
            avg_cooperation = statistics.mean([s.cooperation_score for s in all_scores.values()])
            avg_stability = statistics.mean([s.stability_risk_score for s in all_scores.values()])
        else:
            avg_meta_score = avg_performance = avg_reliability = avg_cooperation = avg_stability = 0.0

        return {
            "total_agents": len(self.agent_metrics),
            "avg_meta_score": avg_meta_score,
            "avg_performance": avg_performance,
            "avg_reliability": avg_reliability,
            "avg_cooperation": avg_cooperation,
            "avg_stability": avg_stability,
            "weights": {
                "performance": self.performance_weight,
                "reliability": self.reliability_weight,
                "cooperation": self.cooperation_weight,
                "stability": self.stability_weight
            }
        }

    def reset_agent(self, agent_name: str) -> None:
        """
        Reset metrics and scores for an agent.

        Args:
            agent_name: Name of agent
        """
        if agent_name in self.agent_metrics:
            del self.agent_metrics[agent_name]
        if agent_name in self.agent_scores:
            del self.agent_scores[agent_name]
        logger.info(f"Reset metrics for agent: {agent_name}")

    def __repr__(self) -> str:
        return f"<AgentScorer: {len(self.agent_metrics)} agents tracked>"


# Singleton instance
_agent_scorer_instance: Optional[AgentScorer] = None


def get_agent_scorer() -> AgentScorer:
    """
    Get singleton AgentScorer instance.

    Returns:
        Global AgentScorer instance
    """
    global _agent_scorer_instance
    if _agent_scorer_instance is None:
        _agent_scorer_instance = AgentScorer()
    return _agent_scorer_instance


def create_agent_scorer(**kwargs) -> AgentScorer:
    """
    Factory function: create new AgentScorer instance.

    Args:
        **kwargs: Arguments passed to AgentScorer constructor

    Returns:
        New AgentScorer instance
    """
    return AgentScorer(**kwargs)

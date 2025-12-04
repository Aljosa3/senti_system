"""
FAZA 27.5 - Execution Optimizer Layer
Optimization Report

Generates human-readable reports about optimization results:
- Before/after statistics
- Applied optimizations
- Performance gains
- Detected issues
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class OptimizationReport:
    """
    Report of optimization results.

    Contains:
    - Statistics before and after optimization
    - List of applied optimizations
    - Detected redundancies
    - Estimated performance gains
    """

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    graph_name: str = "unnamed"

    # Before/after stats
    nodes_before: int = 0
    nodes_after: int = 0
    edges_before: int = 0
    edges_after: int = 0

    # Optimization details
    applied_optimizations: List[str] = field(default_factory=list)
    redundancies_found: int = 0
    tasks_batched: int = 0
    tasks_skippable: int = 0

    # Performance estimates
    estimated_time_before: float = 0.0
    estimated_time_after: float = 0.0
    estimated_cost_before: float = 0.0
    estimated_cost_after: float = 0.0

    # Execution gain
    parallelization_score_before: float = 0.0
    parallelization_score_after: float = 0.0

    # Warnings and notes
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Pass statistics
    pass_stats: List[Dict[str, Any]] = field(default_factory=list)

    def get_node_reduction(self) -> int:
        """Get number of nodes eliminated"""
        return self.nodes_before - self.nodes_after

    def get_time_savings(self) -> float:
        """Get estimated time savings (seconds)"""
        return self.estimated_time_before - self.estimated_time_after

    def get_cost_savings(self) -> float:
        """Get estimated cost savings (dollars)"""
        return self.estimated_cost_before - self.estimated_cost_after

    def get_time_savings_percent(self) -> float:
        """Get time savings as percentage"""
        if self.estimated_time_before == 0:
            return 0.0
        return (self.get_time_savings() / self.estimated_time_before) * 100

    def get_parallelization_improvement(self) -> float:
        """Get parallelization score improvement"""
        return self.parallelization_score_after - self.parallelization_score_before

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "timestamp": self.timestamp,
            "graph_name": self.graph_name,
            "statistics": {
                "nodes": {
                    "before": self.nodes_before,
                    "after": self.nodes_after,
                    "reduction": self.get_node_reduction()
                },
                "edges": {
                    "before": self.edges_before,
                    "after": self.edges_after
                }
            },
            "optimizations": {
                "applied": self.applied_optimizations,
                "redundancies_found": self.redundancies_found,
                "tasks_batched": self.tasks_batched,
                "tasks_skippable": self.tasks_skippable
            },
            "performance": {
                "time": {
                    "before": self.estimated_time_before,
                    "after": self.estimated_time_after,
                    "savings": self.get_time_savings(),
                    "savings_percent": self.get_time_savings_percent()
                },
                "cost": {
                    "before": self.estimated_cost_before,
                    "after": self.estimated_cost_after,
                    "savings": self.get_cost_savings()
                },
                "parallelization": {
                    "before": self.parallelization_score_before,
                    "after": self.parallelization_score_after,
                    "improvement": self.get_parallelization_improvement()
                }
            },
            "pass_stats": self.pass_stats,
            "warnings": self.warnings,
            "notes": self.notes
        }

    def format_text(self) -> str:
        """
        Format report as human-readable text.

        Returns:
            Formatted text report
        """
        lines = []
        lines.append("="*70)
        lines.append("FAZA 27.5 - Execution Optimization Report")
        lines.append("="*70)
        lines.append(f"Graph: {self.graph_name}")
        lines.append(f"Timestamp: {self.timestamp}")
        lines.append("")

        # Statistics
        lines.append("Statistics:")
        lines.append(f"  Nodes: {self.nodes_before} → {self.nodes_after} ({self.get_node_reduction():+d})")
        lines.append(f"  Edges: {self.edges_before} → {self.edges_after}")
        lines.append("")

        # Optimizations
        lines.append("Applied Optimizations:")
        for opt in self.applied_optimizations:
            lines.append(f"  ✓ {opt}")
        lines.append("")

        # Findings
        lines.append("Findings:")
        lines.append(f"  • Redundancies eliminated: {self.redundancies_found}")
        lines.append(f"  • Tasks batched: {self.tasks_batched}")
        lines.append(f"  • Tasks skippable: {self.tasks_skippable}")
        lines.append("")

        # Performance gains
        lines.append("Performance Estimates:")
        time_savings = self.get_time_savings()
        time_percent = self.get_time_savings_percent()
        lines.append(f"  • Time: {self.estimated_time_before:.2f}s → {self.estimated_time_after:.2f}s")
        lines.append(f"    Savings: {time_savings:.2f}s ({time_percent:.1f}%)")

        cost_savings = self.get_cost_savings()
        lines.append(f"  • Cost: ${self.estimated_cost_before:.4f} → ${self.estimated_cost_after:.4f}")
        lines.append(f"    Savings: ${cost_savings:.4f}")

        parallel_improvement = self.get_parallelization_improvement()
        lines.append(f"  • Parallelization: {self.parallelization_score_before:.2f} → {self.parallelization_score_after:.2f}")
        lines.append(f"    Improvement: {parallel_improvement:+.2f}")
        lines.append("")

        # Pass statistics
        if self.pass_stats:
            lines.append("Pass Statistics:")
            for stat in self.pass_stats:
                lines.append(f"  • {stat['pass_name']}: {stat['changes']} changes")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        # Notes
        if self.notes:
            lines.append("Notes:")
            for note in self.notes:
                lines.append(f"  ℹ {note}")
            lines.append("")

        lines.append("="*70)

        return "\n".join(lines)

    def format_summary(self) -> str:
        """
        Format brief summary (one line).

        Returns:
            Summary string
        """
        return (
            f"Optimized {self.graph_name}: "
            f"{self.nodes_before}→{self.nodes_after} nodes, "
            f"{self.get_time_savings():.1f}s saved "
            f"({self.get_time_savings_percent():.1f}%), "
            f"{len(self.applied_optimizations)} passes"
        )


class ReportBuilder:
    """Helper class to build optimization reports"""

    def __init__(self):
        """Initialize report builder"""
        self.report = OptimizationReport()

    def set_graph_name(self, name: str) -> 'ReportBuilder':
        """Set graph name"""
        self.report.graph_name = name
        return self

    def set_before_stats(self, nodes: int, edges: int) -> 'ReportBuilder':
        """Set before statistics"""
        self.report.nodes_before = nodes
        self.report.edges_before = edges
        return self

    def set_after_stats(self, nodes: int, edges: int) -> 'ReportBuilder':
        """Set after statistics"""
        self.report.nodes_after = nodes
        self.report.edges_after = edges
        return self

    def add_optimization(self, name: str) -> 'ReportBuilder':
        """Add applied optimization"""
        self.report.applied_optimizations.append(name)
        return self

    def set_redundancies(self, count: int) -> 'ReportBuilder':
        """Set redundancies found"""
        self.report.redundancies_found = count
        return self

    def set_batched(self, count: int) -> 'ReportBuilder':
        """Set tasks batched"""
        self.report.tasks_batched = count
        return self

    def set_skippable(self, count: int) -> 'ReportBuilder':
        """Set skippable tasks"""
        self.report.tasks_skippable = count
        return self

    def set_time_estimates(self, before: float, after: float) -> 'ReportBuilder':
        """Set time estimates"""
        self.report.estimated_time_before = before
        self.report.estimated_time_after = after
        return self

    def set_cost_estimates(self, before: float, after: float) -> 'ReportBuilder':
        """Set cost estimates"""
        self.report.estimated_cost_before = before
        self.report.estimated_cost_after = after
        return self

    def set_parallelization_scores(self, before: float, after: float) -> 'ReportBuilder':
        """Set parallelization scores"""
        self.report.parallelization_score_before = before
        self.report.parallelization_score_after = after
        return self

    def add_warning(self, warning: str) -> 'ReportBuilder':
        """Add warning"""
        self.report.warnings.append(warning)
        return self

    def add_note(self, note: str) -> 'ReportBuilder':
        """Add note"""
        self.report.notes.append(note)
        return self

    def set_pass_stats(self, stats: List[Dict[str, Any]]) -> 'ReportBuilder':
        """Set pass statistics"""
        self.report.pass_stats = stats
        return self

    def build(self) -> OptimizationReport:
        """Build and return the report"""
        return self.report


def create_report_builder() -> ReportBuilder:
    """Factory function for ReportBuilder"""
    return ReportBuilder()

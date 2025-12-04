"""
FAZA 27 – TaskGraph Engine
Graph Exporter

Exports TaskGraphs to various formats: JSON, DOT, Markdown, YAML.
Supports analysis data inclusion and file saving.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from senti_os.core.faza27.task_graph import TaskGraph
from senti_os.core.faza27.graph_analyzer import GraphAnalyzer

logger = logging.getLogger(__name__)


class GraphExporter:
    """
    Exports TaskGraphs to multiple formats.

    Supports JSON, DOT (GraphViz), Markdown, and YAML formats.
    Can include analysis data in exports.
    """

    def __init__(self, graph: TaskGraph):
        """
        Initialize exporter with graph.

        Args:
            graph: TaskGraph to export
        """
        self.graph = graph
        self.analyzer: Optional[GraphAnalyzer] = None

    def export_json(self, include_analysis: bool = False) -> str:
        """
        Export graph to JSON format.

        Args:
            include_analysis: Include analysis data

        Returns:
            JSON string
        """
        data = self.graph.to_dict()

        if include_analysis:
            if not self.analyzer:
                self.analyzer = GraphAnalyzer(self.graph)
            data["analysis"] = self.analyzer.get_analysis_report()

        return json.dumps(data, indent=2)

    def export_dot(self, include_labels: bool = True) -> str:
        """
        Export graph to DOT format (GraphViz).

        Args:
            include_labels: Include node labels with metadata

        Returns:
            DOT string
        """
        lines = ["digraph TaskGraph {"]
        lines.append(f'  label="{self.graph.graph_id}";')
        lines.append('  rankdir=TB;')
        lines.append('  node [shape=box];')
        lines.append('')

        # Add nodes
        for node in self.graph.get_all_nodes():
            label = node.name
            if include_labels:
                label += f"\\n[{node.node_type}]"
                label += f"\\nPri: {node.priority}"
                label += f"\\n{node.cost_model.estimated_duration}s"

            # Color by status
            color = {
                "pending": "lightgray",
                "ready": "lightblue",
                "running": "yellow",
                "completed": "lightgreen",
                "failed": "red",
                "cancelled": "orange",
                "blocked": "pink"
            }.get(node.status.value, "white")

            # Critical path highlighting
            style = 'filled,bold' if node.critical_path else 'filled'

            lines.append(f'  "{node.node_id}" [label="{label}", fillcolor={color}, style="{style}"];')

        lines.append('')

        # Add edges
        for edge in self.graph.edges:
            style = {
                "dependency": "solid",
                "constraint": "dashed",
                "data_flow": "dotted",
                "conditional": "dashed",
                "weak": "dotted"
            }.get(edge.edge_type.value, "solid")

            label = f'label="{edge.weight}"' if edge.weight != 1.0 else ''

            lines.append(f'  "{edge.source_id}" -> "{edge.target_id}" [style={style}, {label}];')

        lines.append('}')

        return '\n'.join(lines)

    def export_markdown(self, include_analysis: bool = False) -> str:
        """
        Export graph to Markdown format.

        Args:
            include_analysis: Include analysis section

        Returns:
            Markdown string
        """
        lines = [f"# TaskGraph: {self.graph.graph_id}"]
        lines.append('')

        # Stats
        stats = self.graph.get_stats()
        lines.append("## Statistics")
        lines.append(f"- **Nodes**: {stats['node_count']}")
        lines.append(f"- **Edges**: {stats['edge_count']}")
        lines.append(f"- **Root Nodes**: {stats['root_count']}")
        lines.append(f"- **Leaf Nodes**: {stats['leaf_count']}")
        lines.append(f"- **Is Acyclic**: {stats['is_acyclic']}")
        lines.append('')

        # Nodes
        lines.append("## Nodes")
        lines.append('')
        lines.append("| Node ID | Name | Type | Priority | Status | Duration |")
        lines.append("|---------|------|------|----------|--------|----------|")

        for node in self.graph.get_all_nodes():
            lines.append(
                f"| {node.node_id} | {node.name} | {node.node_type} | "
                f"{node.priority} | {node.status.value} | {node.cost_model.estimated_duration}s |"
            )

        lines.append('')

        # Edges
        lines.append("## Edges")
        lines.append('')
        lines.append("| Source | Target | Type | Weight |")
        lines.append("|--------|--------|------|--------|")

        for edge in self.graph.edges:
            lines.append(
                f"| {edge.source_id} | {edge.target_id} | {edge.edge_type.value} | {edge.weight} |"
            )

        lines.append('')

        # Critical Path
        critical_path, duration = self.graph.calculate_critical_path()
        lines.append("## Critical Path")
        lines.append(f"**Duration**: {duration:.2f}s")
        lines.append('')
        lines.append("```")
        lines.append(" -> ".join(critical_path))
        lines.append("```")
        lines.append('')

        # Analysis
        if include_analysis:
            if not self.analyzer:
                self.analyzer = GraphAnalyzer(self.graph)

            report = self.analyzer.get_analysis_report()

            lines.append("## Analysis")
            lines.append('')

            # Health
            health = report["health"]
            lines.append(f"### Health: {health['status'].upper()} ({health['health_score']:.1f}/100)")
            if health['issues']:
                lines.append("**Issues:**")
                for issue in health['issues']:
                    lines.append(f"- {issue}")
            lines.append('')

            # Costs
            costs = report["costs"]
            lines.append("### Resource Costs")
            lines.append(f"- **Sequential Duration**: {costs['total_duration_sequential']:.2f}s")
            lines.append(f"- **Critical Path Duration**: {costs['critical_path_duration']:.2f}s")
            lines.append(f"- **Total Cost**: ${costs['total_cost']:.2f}")
            lines.append(f"- **Efficiency Ratio**: {costs['efficiency_ratio']:.2%}")
            lines.append('')

            # Bottlenecks
            if report["bottlenecks"]:
                lines.append("### Bottlenecks")
                for bn in report["bottlenecks"][:3]:
                    lines.append(f"- **{bn['node_name']}**: {bn['type']} (fan-in: {bn['fan_in']}, fan-out: {bn['fan_out']})")
                lines.append('')

        return '\n'.join(lines)

    def export_yaml(self, include_analysis: bool = False) -> str:
        """
        Export graph to YAML-like format.

        Note: Uses JSON structure with YAML-like formatting (no pyyaml dependency).

        Args:
            include_analysis: Include analysis data

        Returns:
            YAML-formatted string
        """
        data = self.graph.to_dict()

        if include_analysis:
            if not self.analyzer:
                self.analyzer = GraphAnalyzer(self.graph)
            data["analysis"] = self.analyzer.get_analysis_report()

        # Convert to YAML-like format manually
        lines = [f"graph_id: {self.graph.graph_id}"]

        # Metadata
        if self.graph.metadata:
            lines.append("metadata:")
            for key, value in self.graph.metadata.items():
                lines.append(f"  {key}: {value}")

        # Nodes
        lines.append(f"node_count: {len(self.graph.nodes)}")
        lines.append("nodes:")
        for node_id, node in self.graph.nodes.items():
            lines.append(f"  {node_id}:")
            lines.append(f"    name: {node.name}")
            lines.append(f"    type: {node.node_type}")
            lines.append(f"    priority: {node.priority}")
            lines.append(f"    status: {node.status.value}")

        # Edges
        lines.append(f"edge_count: {len(self.graph.edges)}")
        lines.append("edges:")
        for i, edge in enumerate(self.graph.edges):
            lines.append(f"  - source: {edge.source_id}")
            lines.append(f"    target: {edge.target_id}")
            lines.append(f"    type: {edge.edge_type.value}")
            lines.append(f"    weight: {edge.weight}")

        return '\n'.join(lines)

    def save_to_file(
        self,
        filepath: str,
        format: str = "json",
        include_analysis: bool = False
    ) -> None:
        """
        Save graph to file.

        Args:
            filepath: Output file path
            format: Export format (json, dot, markdown, yaml)
            include_analysis: Include analysis data

        Raises:
            ValueError: If format is unsupported
        """
        format_map = {
            "json": self.export_json,
            "dot": self.export_dot,
            "markdown": self.export_markdown,
            "md": self.export_markdown,
            "yaml": self.export_yaml,
            "yml": self.export_yaml,
        }

        if format.lower() not in format_map:
            raise ValueError(f"Unsupported format: {format}. Supported: {list(format_map.keys())}")

        # Generate export
        export_func = format_map[format.lower()]
        if format.lower() == "dot":
            content = export_func()
        else:
            content = export_func(include_analysis=include_analysis)

        # Write to file
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

        logger.info(f"Exported graph to {filepath} ({format} format)")

    def export_with_analysis(self, format: str = "json") -> str:
        """
        Export graph with full analysis data.

        Args:
            format: Export format

        Returns:
            Formatted string
        """
        format_map = {
            "json": self.export_json,
            "markdown": self.export_markdown,
            "yaml": self.export_yaml,
        }

        if format.lower() not in format_map:
            raise ValueError(f"Format {format} doesn't support analysis inclusion")

        return format_map[format.lower()](include_analysis=True)


def create_graph_exporter(graph: TaskGraph) -> GraphExporter:
    """
    Factory function to create GraphExporter instance.

    Args:
        graph: TaskGraph to export

    Returns:
        GraphExporter instance
    """
    return GraphExporter(graph)

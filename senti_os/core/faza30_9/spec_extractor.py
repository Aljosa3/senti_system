"""
FAZA 30.9 – SPEC Extractor
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import re


@dataclass
class ExtractedSpec:
    """Extracted specification from natural language input."""

    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "requirements": self.requirements,
            "constraints": self.constraints,
            "integration_points": self.integration_points,
            "risks": self.risks,
            "goals": self.goals,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "raw_text": self.raw_text,
            "metadata": self.metadata
        }


class SpecExtractor:
    """
    Extracts structured specification information from natural language.

    This module analyzes user input and extracts:
    - Requirements: What the system must do
    - Constraints: Limitations and boundaries
    - Integration points: External dependencies
    - Risks: Potential issues
    - Goals: Desired outcomes
    - Inputs: What the system receives
    - Outputs: What the system produces
    """

    # Keywords for extraction
    REQUIREMENT_KEYWORDS = [
        "must", "should", "required", "need", "necessary",
        "implement", "create", "build", "provide", "support"
    ]

    CONSTRAINT_KEYWORDS = [
        "cannot", "must not", "limited", "constraint", "restriction",
        "only", "within", "maximum", "minimum", "without"
    ]

    INTEGRATION_KEYWORDS = [
        "integrate", "interface", "connect", "communicate",
        "api", "service", "external", "dependency"
    ]

    RISK_KEYWORDS = [
        "risk", "danger", "concern", "issue", "problem",
        "failure", "error", "vulnerability", "threat"
    ]

    GOAL_KEYWORDS = [
        "goal", "objective", "aim", "purpose", "target",
        "achieve", "accomplish", "deliver", "outcome"
    ]

    INPUT_KEYWORDS = [
        "input", "receive", "accept", "take", "consume",
        "read", "load", "import", "parameter"
    ]

    OUTPUT_KEYWORDS = [
        "output", "return", "produce", "generate", "export",
        "write", "emit", "result", "response"
    ]

    def __init__(self) -> None:
        """Initialize the SPEC extractor."""
        pass

    def extract(self, natural_language: str) -> ExtractedSpec:
        """
        Extract structured specification from natural language.

        Args:
            natural_language: User input describing desired system

        Returns:
            ExtractedSpec containing structured information
        """
        spec = ExtractedSpec(raw_text=natural_language)

        # Split into sentences
        sentences = self._split_sentences(natural_language)

        # Extract each category
        spec.requirements = self._extract_category(
            sentences, self.REQUIREMENT_KEYWORDS
        )
        spec.constraints = self._extract_category(
            sentences, self.CONSTRAINT_KEYWORDS
        )
        spec.integration_points = self._extract_category(
            sentences, self.INTEGRATION_KEYWORDS
        )
        spec.risks = self._extract_category(
            sentences, self.RISK_KEYWORDS
        )
        spec.goals = self._extract_category(
            sentences, self.GOAL_KEYWORDS
        )
        spec.inputs = self._extract_category(
            sentences, self.INPUT_KEYWORDS
        )
        spec.outputs = self._extract_category(
            sentences, self.OUTPUT_KEYWORDS
        )

        # Extract metadata
        spec.metadata = self._extract_metadata(natural_language)

        return spec

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_category(
        self,
        sentences: List[str],
        keywords: List[str]
    ) -> List[str]:
        """Extract sentences matching category keywords."""
        results = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for keyword in keywords:
                if keyword in sentence_lower:
                    results.append(sentence)
                    break

        return results

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text."""
        metadata: Dict[str, Any] = {}

        # Extract component name if mentioned
        name_match = re.search(
            r'(?:component|module|system|service)\s+(?:named|called)\s+["\']?(\w+)["\']?',
            text,
            re.IGNORECASE
        )
        if name_match:
            metadata["suggested_name"] = name_match.group(1)

        # Extract version if mentioned
        version_match = re.search(
            r'version\s+(\d+(?:\.\d+)*)',
            text,
            re.IGNORECASE
        )
        if version_match:
            metadata["version"] = version_match.group(1)

        # Detect complexity
        word_count = len(text.split())
        if word_count < 50:
            metadata["complexity"] = "simple"
        elif word_count < 200:
            metadata["complexity"] = "moderate"
        else:
            metadata["complexity"] = "complex"

        return metadata

    def validate_extraction(self, spec: ExtractedSpec) -> tuple[bool, List[str]]:
        """
        Validate extracted specification for completeness.

        Args:
            spec: Extracted specification

        Returns:
            Tuple of (is_valid, list of warnings)
        """
        warnings = []

        # Check for minimum content
        if not spec.requirements and not spec.goals:
            warnings.append("No requirements or goals extracted")

        if not spec.outputs:
            warnings.append("No outputs specified")

        if len(spec.raw_text) < 20:
            warnings.append("Input text too short for meaningful extraction")

        # Warnings don't block, but inform
        is_valid = len(spec.raw_text) >= 20

        return is_valid, warnings

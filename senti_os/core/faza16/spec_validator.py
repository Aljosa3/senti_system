"""
SPEC Validator for SENTI OS FAZA 16

Validates SPEC (specification) documents for:
- Required structure and sections
- Missing or incomplete sections
- Contradictions and inconsistencies
- Invalid phase numbering
- Unsafe or unrealistic requirements
- FAZA alignment and dependencies
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SpecIssue:
    """Represents a validation issue in a SPEC."""
    section: str
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class SpecValidationResult:
    """Result of SPEC validation."""
    is_valid: bool
    spec_name: str
    issues: List[SpecIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    score: float = 100.0  # 0-100, higher is better


class SpecValidator:
    """
    Validates SPEC documents for completeness, consistency, and safety.

    Required SPEC sections:
    - Title/Name
    - Objective/Purpose
    - Architecture/Design
    - Implementation Steps
    - Testing Plan
    - Integration Points
    """

    REQUIRED_SECTIONS = [
        "objective",
        "architecture",
        "implementation",
        "testing",
    ]

    RECOMMENDED_SECTIONS = [
        "integration",
        "dependencies",
        "risks",
        "timeline",
    ]

    DANGEROUS_KEYWORDS = [
        "eval(",
        "exec(",
        "subprocess.call",
        "os.system",
        "__import__",
        "compile(",
        "globals()",
        "locals()",
    ]

    CONTRADICTION_PAIRS = [
        ("always", "never"),
        ("must", "must not"),
        ("required", "optional"),
        ("all", "none"),
        ("enable", "disable"),
    ]

    def __init__(self):
        """Initialize SPEC validator."""
        self.section_patterns = self._compile_section_patterns()
        logger.info("SPEC Validator initialized")

    def validate_spec(self, spec_text: str, spec_name: str = "unnamed") -> SpecValidationResult:
        """
        Validate a SPEC document.

        Args:
            spec_text: SPEC content as string
            spec_name: Name/identifier for the SPEC

        Returns:
            SpecValidationResult with validation results
        """
        result = SpecValidationResult(
            is_valid=True,
            spec_name=spec_name,
        )

        if not spec_text or not spec_text.strip():
            result.issues.append(
                SpecIssue(
                    section="general",
                    severity=ValidationSeverity.CRITICAL,
                    message="SPEC is empty",
                )
            )
            result.is_valid = False
            result.score = 0.0
            return result

        # Check for required sections
        self._check_required_sections(spec_text, result)

        # Check for recommended sections
        self._check_recommended_sections(spec_text, result)

        # Check for contradictions
        self._check_contradictions(spec_text, result)

        # Check phase numbering
        self._check_phase_numbering(spec_text, result)

        # Check for dangerous patterns
        self._check_dangerous_patterns(spec_text, result)

        # Check for incomplete sections
        self._check_incomplete_sections(spec_text, result)

        # Check for unrealistic requirements
        self._check_unrealistic_requirements(spec_text, result)

        # Calculate final score
        result.score = self._calculate_score(result)

        # Determine if valid based on critical/error issues
        critical_errors = [
            i for i in result.issues
            if i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
        ]
        result.is_valid = len(critical_errors) == 0

        logger.info(
            f"SPEC validation complete: {spec_name} - "
            f"Valid={result.is_valid}, Score={result.score:.1f}, "
            f"Issues={len(result.issues)}"
        )

        return result

    def _compile_section_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for section detection."""
        patterns = {}

        # Common section header patterns
        section_keywords = {
            "objective": [r"objective", r"purpose", r"goal", r"aim"],
            "architecture": [r"architecture", r"design", r"structure"],
            "implementation": [r"implementation", r"steps", r"procedure"],
            "testing": [r"testing", r"test plan", r"validation"],
            "integration": [r"integration", r"interface"],
            "dependencies": [r"dependenc", r"requirement"],
            "risks": [r"risk", r"challenge"],
        }

        for section, keywords in section_keywords.items():
            pattern_str = r"(?i)^#+\s*(" + "|".join(keywords) + r")"
            patterns[section] = re.compile(pattern_str, re.MULTILINE)

        return patterns

    def _check_required_sections(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for required sections."""
        for section in self.REQUIRED_SECTIONS:
            pattern = self.section_patterns.get(section)
            if not pattern or not pattern.search(spec_text):
                result.issues.append(
                    SpecIssue(
                        section="structure",
                        severity=ValidationSeverity.ERROR,
                        message=f"Missing required section: {section}",
                        suggestion=f"Add a '{section.title()}' section",
                    )
                )

    def _check_recommended_sections(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for recommended sections."""
        for section in self.RECOMMENDED_SECTIONS:
            pattern = self.section_patterns.get(section)
            if not pattern or not pattern.search(spec_text):
                result.warnings.append(
                    f"Recommended section missing: {section}"
                )

    def _check_contradictions(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for contradictory statements."""
        spec_lower = spec_text.lower()

        for word1, word2 in self.CONTRADICTION_PAIRS:
            if word1 in spec_lower and word2 in spec_lower:
                # Check if they're close together (within 100 chars)
                for match1 in re.finditer(r'\b' + word1 + r'\b', spec_lower):
                    pos1 = match1.start()
                    for match2 in re.finditer(r'\b' + word2 + r'\b', spec_lower):
                        pos2 = match2.start()
                        if abs(pos1 - pos2) < 100:
                            result.issues.append(
                                SpecIssue(
                                    section="consistency",
                                    severity=ValidationSeverity.WARNING,
                                    message=f"Potential contradiction: '{word1}' and '{word2}' used together",
                                    suggestion="Review for logical consistency",
                                )
                            )
                            break

    def _check_phase_numbering(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check FAZA phase numbering."""
        # Find all FAZA/phase references
        phase_pattern = re.compile(r'(?i)(faza|phase)\s*(\d+)', re.IGNORECASE)
        phases = [int(m.group(2)) for m in phase_pattern.finditer(spec_text)]

        if phases:
            # Check for valid range (1-35 based on typical Senti OS architecture)
            invalid_phases = [p for p in phases if p < 1 or p > 35]
            if invalid_phases:
                result.issues.append(
                    SpecIssue(
                        section="phases",
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid phase numbers: {invalid_phases}",
                        suggestion="Use phase numbers between 1 and 35",
                    )
                )

            # Check for duplicate phases
            if len(phases) != len(set(phases)):
                duplicates = [p for p in set(phases) if phases.count(p) > 1]
                result.warnings.append(
                    f"Duplicate phase references: {duplicates}"
                )

    def _check_dangerous_patterns(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for dangerous code patterns in SPEC."""
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in spec_text:
                result.issues.append(
                    SpecIssue(
                        section="safety",
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Dangerous pattern detected: {keyword}",
                        suggestion=f"Avoid using {keyword} in implementation",
                    )
                )

    def _check_incomplete_sections(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for incomplete or placeholder sections."""
        incomplete_patterns = [
            r"TODO",
            r"TBD",
            r"to be determined",
            r"coming soon",
            r"\.\.\.",
            r"placeholder",
            r"not yet",
        ]

        for pattern in incomplete_patterns:
            matches = re.finditer(pattern, spec_text, re.IGNORECASE)
            for match in matches:
                result.issues.append(
                    SpecIssue(
                        section="completeness",
                        severity=ValidationSeverity.WARNING,
                        message=f"Incomplete section marker: {match.group()}",
                        suggestion="Complete all sections before implementation",
                    )
                )

    def _check_unrealistic_requirements(
        self,
        spec_text: str,
        result: SpecValidationResult,
    ) -> None:
        """Check for unrealistic or vague requirements."""
        vague_patterns = [
            (r"as fast as possible", "Specify concrete performance targets"),
            (r"unlimited", "Define realistic limits"),
            (r"perfect", "Define measurable quality criteria"),
            (r"always work", "Define success criteria and failure handling"),
            (r"never fail", "Include error handling and recovery"),
        ]

        for pattern, suggestion in vague_patterns:
            if re.search(pattern, spec_text, re.IGNORECASE):
                result.issues.append(
                    SpecIssue(
                        section="requirements",
                        severity=ValidationSeverity.WARNING,
                        message=f"Vague/unrealistic requirement: '{pattern}'",
                        suggestion=suggestion,
                    )
                )

    def _calculate_score(self, result: SpecValidationResult) -> float:
        """
        Calculate overall SPEC quality score (0-100).

        Args:
            result: SpecValidationResult to score

        Returns:
            Score between 0 and 100
        """
        score = 100.0

        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                score -= 25.0
            elif issue.severity == ValidationSeverity.ERROR:
                score -= 10.0
            elif issue.severity == ValidationSeverity.WARNING:
                score -= 5.0
            else:  # INFO
                score -= 1.0

        # Deduct points for warnings
        score -= len(result.warnings) * 2.0

        return max(0.0, min(100.0, score))

    def validate_spec_alignment(
        self,
        spec_text: str,
        existing_fazas: List[int],
    ) -> List[SpecIssue]:
        """
        Validate SPEC alignment with existing FAZA phases.

        Args:
            spec_text: SPEC content
            existing_fazas: List of existing FAZA numbers

        Returns:
            List of alignment issues
        """
        issues = []

        # Extract referenced FAZAs from spec
        phase_pattern = re.compile(r'(?i)faza\s*(\d+)', re.IGNORECASE)
        referenced_fazas = [int(m.group(1)) for m in phase_pattern.finditer(spec_text)]

        for faza in referenced_fazas:
            if faza not in existing_fazas:
                issues.append(
                    SpecIssue(
                        section="alignment",
                        severity=ValidationSeverity.WARNING,
                        message=f"References non-existent FAZA {faza}",
                        suggestion=f"Verify FAZA {faza} exists or update reference",
                    )
                )

        return issues

    def get_spec_metadata(self, spec_text: str) -> Dict:
        """
        Extract metadata from SPEC.

        Args:
            spec_text: SPEC content

        Returns:
            Dictionary with metadata
        """
        metadata = {
            "line_count": len(spec_text.split('\n')),
            "word_count": len(spec_text.split()),
            "sections_found": [],
            "phases_referenced": [],
        }

        # Find sections
        for section, pattern in self.section_patterns.items():
            if pattern.search(spec_text):
                metadata["sections_found"].append(section)

        # Find phase references
        phase_pattern = re.compile(r'(?i)faza\s*(\d+)', re.IGNORECASE)
        metadata["phases_referenced"] = list(set(
            int(m.group(1)) for m in phase_pattern.finditer(spec_text)
        ))

        return metadata


def create_spec_validator() -> SpecValidator:
    """
    Create and return a SPEC validator.

    Returns:
        SpecValidator instance
    """
    return SpecValidator()


def validate_spec(spec_text: str, spec_name: str = "unnamed") -> SpecValidationResult:
    """
    Convenience function to validate a SPEC.

    Args:
        spec_text: SPEC content
        spec_name: SPEC identifier

    Returns:
        SpecValidationResult
    """
    validator = create_spec_validator()
    return validator.validate_spec(spec_text, spec_name)

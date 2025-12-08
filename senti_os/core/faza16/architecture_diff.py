"""
Architecture Diff Analyzer for SENTI OS FAZA 16

Compares new module specifications against existing architecture:
- Missing required components
- Illegal imports (protected paths)
- Naming convention violations
- Dependency conflicts
- Integration point validation
"""

import os
import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiffSeverity(Enum):
    """Severity levels for architecture differences."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ArchitectureDiff:
    """Represents a difference or conflict with existing architecture."""
    category: str
    severity: DiffSeverity
    message: str
    affected_component: str
    suggestion: Optional[str] = None


@dataclass
class ArchitectureAnalysis:
    """Result of architecture diff analysis."""
    is_compatible: bool
    diffs: List[ArchitectureDiff] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    compatibility_score: float = 100.0


class ArchitectureDiffAnalyzer:
    """
    Analyzes new modules against existing Senti OS architecture.

    Validates:
    - Import paths and dependencies
    - Naming conventions
    - Directory structure
    - Integration points
    - Protected component access
    """

    # Protected directories that cannot be modified by auto-generated code
    PROTECTED_DIRS = [
        "senti_os/boot",
        "senti_os/kernel",
        "senti_os/drivers",
    ]

    # Valid module locations
    VALID_MODULE_LOCATIONS = [
        "senti_os/core",
        "senti_core_module/senti_core",
        "senti_core_module/senti_expansion",
        "senti_core_module/senti_kernel",
        "senti_core_module/senti_security_core",
        "senti_core_module/senti_memory_core",
        "senti_core_module/senti_refactor",
        "modules/sensors",
        "modules/actuators",
        "modules/processing",
        "modules/communication",
    ]

    # Required components for FAZA modules
    REQUIRED_FAZA_COMPONENTS = [
        "__init__.py",
    ]

    # Naming convention patterns
    NAMING_PATTERNS = {
        "faza_module": re.compile(r"^faza\d+$"),
        "python_file": re.compile(r"^[a-z_][a-z0-9_]*\.py$"),
        "python_module": re.compile(r"^[a-z_][a-z0-9_]*$"),
    }

    def __init__(self, base_path: str = "/home/pisarna/senti_system"):
        """
        Initialize architecture diff analyzer.

        Args:
            base_path: Base path to Senti OS installation
        """
        self.base_path = Path(base_path)
        logger.info(f"Architecture Diff Analyzer initialized: {base_path}")

    def analyze_new_module(
        self,
        module_spec: Dict,
        module_path: str,
    ) -> ArchitectureAnalysis:
        """
        Analyze a new module specification against existing architecture.

        Args:
            module_spec: Module specification dictionary
            module_path: Proposed path for the module

        Returns:
            ArchitectureAnalysis with compatibility results
        """
        analysis = ArchitectureAnalysis(is_compatible=True)

        # Validate module location
        self._check_module_location(module_path, analysis)

        # Check protected directory access
        self._check_protected_access(module_spec, analysis)

        # Validate imports
        self._check_imports(module_spec, analysis)

        # Check naming conventions
        self._check_naming_conventions(module_path, module_spec, analysis)

        # Check for missing components
        self._check_required_components(module_spec, analysis)

        # Validate dependencies
        self._check_dependencies(module_spec, analysis)

        # Calculate compatibility score
        analysis.compatibility_score = self._calculate_score(analysis)

        # Determine compatibility
        critical_diffs = [
            d for d in analysis.diffs
            if d.severity in [DiffSeverity.CRITICAL, DiffSeverity.ERROR]
        ]
        analysis.is_compatible = len(critical_diffs) == 0

        logger.info(
            f"Architecture analysis complete: Compatible={analysis.is_compatible}, "
            f"Score={analysis.compatibility_score:.1f}, Diffs={len(analysis.diffs)}"
        )

        return analysis

    def _check_module_location(
        self,
        module_path: str,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Check if module path is in a valid location."""
        # Normalize path
        norm_path = module_path.replace(str(self.base_path) + "/", "")

        # Check if in valid location
        is_valid = any(
            norm_path.startswith(loc) for loc in self.VALID_MODULE_LOCATIONS
        )

        if not is_valid:
            analysis.diffs.append(
                ArchitectureDiff(
                    category="location",
                    severity=DiffSeverity.ERROR,
                    message=f"Module location not in valid directories: {norm_path}",
                    affected_component=module_path,
                    suggestion=f"Use one of: {', '.join(self.VALID_MODULE_LOCATIONS)}",
                )
            )

        # Check if in protected directory
        is_protected = any(
            norm_path.startswith(prot) for prot in self.PROTECTED_DIRS
        )

        if is_protected:
            analysis.diffs.append(
                ArchitectureDiff(
                    category="location",
                    severity=DiffSeverity.CRITICAL,
                    message=f"Cannot create modules in protected directory: {norm_path}",
                    affected_component=module_path,
                    suggestion="Choose a different location outside protected directories",
                )
            )

    def _check_protected_access(
        self,
        module_spec: Dict,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Check for attempts to access protected components."""
        # Extract imports from spec
        imports = module_spec.get("imports", [])

        for import_path in imports:
            for protected in self.PROTECTED_DIRS:
                if protected in import_path:
                    analysis.diffs.append(
                        ArchitectureDiff(
                            category="protected_access",
                            severity=DiffSeverity.CRITICAL,
                            message=f"Illegal import from protected directory: {import_path}",
                            affected_component=import_path,
                            suggestion="Use public APIs instead of internal components",
                        )
                    )

    def _check_imports(
        self,
        module_spec: Dict,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Validate module imports."""
        imports = module_spec.get("imports", [])

        for import_path in imports:
            # Check for circular dependencies
            if self._is_circular_import(import_path, module_spec):
                analysis.warnings.append(
                    f"Potential circular import detected: {import_path}"
                )

            # Check for deprecated modules
            if self._is_deprecated_import(import_path):
                analysis.warnings.append(
                    f"Import from deprecated module: {import_path}"
                )

            # Validate import path format
            if not self._is_valid_import_path(import_path):
                analysis.diffs.append(
                    ArchitectureDiff(
                        category="imports",
                        severity=DiffSeverity.WARNING,
                        message=f"Non-standard import path: {import_path}",
                        affected_component=import_path,
                        suggestion="Use standard Senti OS import conventions",
                    )
                )

    def _check_naming_conventions(
        self,
        module_path: str,
        module_spec: Dict,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Check naming convention compliance."""
        # Extract module name from path
        module_name = Path(module_path).stem

        # Check if FAZA module
        if "faza" in module_name.lower():
            if not self.NAMING_PATTERNS["faza_module"].match(module_name):
                analysis.diffs.append(
                    ArchitectureDiff(
                        category="naming",
                        severity=DiffSeverity.WARNING,
                        message=f"FAZA module naming convention violation: {module_name}",
                        affected_component=module_name,
                        suggestion="Use format: fazaN where N is the phase number",
                    )
                )

        # Check Python file naming
        if module_path.endswith(".py"):
            filename = Path(module_path).name
            if not self.NAMING_PATTERNS["python_file"].match(filename):
                analysis.diffs.append(
                    ArchitectureDiff(
                        category="naming",
                        severity=DiffSeverity.WARNING,
                        message=f"Python file naming convention violation: {filename}",
                        affected_component=filename,
                        suggestion="Use lowercase with underscores: my_module.py",
                    )
                )

    def _check_required_components(
        self,
        module_spec: Dict,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Check for required module components."""
        files = module_spec.get("files", [])

        for required in self.REQUIRED_FAZA_COMPONENTS:
            if required not in files:
                analysis.diffs.append(
                    ArchitectureDiff(
                        category="completeness",
                        severity=DiffSeverity.WARNING,
                        message=f"Missing required component: {required}",
                        affected_component=required,
                        suggestion=f"Add {required} for proper module structure",
                    )
                )

    def _check_dependencies(
        self,
        module_spec: Dict,
        analysis: ArchitectureAnalysis,
    ) -> None:
        """Check module dependencies."""
        dependencies = module_spec.get("dependencies", [])

        for dep in dependencies:
            # Check if dependency exists
            if not self._dependency_exists(dep):
                analysis.diffs.append(
                    ArchitectureDiff(
                        category="dependencies",
                        severity=DiffSeverity.ERROR,
                        message=f"Missing dependency: {dep}",
                        affected_component=dep,
                        suggestion="Ensure dependency is installed or available",
                    )
                )

    def _is_circular_import(self, import_path: str, module_spec: Dict) -> bool:
        """Check for potential circular imports."""
        # Simple heuristic: check if import references the module itself
        module_name = module_spec.get("name", "")
        return module_name in import_path

    def _is_deprecated_import(self, import_path: str) -> bool:
        """Check if import is from deprecated module."""
        deprecated_modules = [
            "senti_core.services",  # Moved to senti_core_module
        ]
        return any(dep in import_path for dep in deprecated_modules)

    def _is_valid_import_path(self, import_path: str) -> bool:
        """Validate import path format."""
        # Check for valid Python module path
        parts = import_path.split(".")
        return all(
            self.NAMING_PATTERNS["python_module"].match(part)
            for part in parts if part
        )

    def _dependency_exists(self, dependency: str) -> bool:
        """Check if a dependency exists in the system."""
        # For stdlib, always return True
        stdlib_modules = {
            "os", "sys", "json", "logging", "typing", "dataclasses",
            "enum", "pathlib", "datetime", "time", "re", "ast",
        }

        if dependency in stdlib_modules:
            return True

        # Check if it's a Senti OS module
        dep_path = self.base_path / dependency.replace(".", "/")
        if dep_path.exists():
            return True

        # Check if it's a Python file
        dep_file = self.base_path / (dependency.replace(".", "/") + ".py")
        if dep_file.exists():
            return True

        return False

    def _calculate_score(self, analysis: ArchitectureAnalysis) -> float:
        """
        Calculate compatibility score (0-100).

        Args:
            analysis: ArchitectureAnalysis to score

        Returns:
            Score between 0 and 100
        """
        score = 100.0

        # Deduct points for diffs
        for diff in analysis.diffs:
            if diff.severity == DiffSeverity.CRITICAL:
                score -= 30.0
            elif diff.severity == DiffSeverity.ERROR:
                score -= 15.0
            elif diff.severity == DiffSeverity.WARNING:
                score -= 5.0
            else:  # INFO
                score -= 1.0

        # Deduct points for warnings
        score -= len(analysis.warnings) * 2.0

        return max(0.0, min(100.0, score))

    def compare_implementations(
        self,
        spec: Dict,
        implementation: str,
    ) -> ArchitectureAnalysis:
        """
        Compare specification against actual implementation.

        Args:
            spec: Module specification
            implementation: Implementation code

        Returns:
            ArchitectureAnalysis with comparison results
        """
        analysis = ArchitectureAnalysis(is_compatible=True)

        # Check if implementation matches spec
        spec_functions = set(spec.get("functions", []))
        spec_classes = set(spec.get("classes", []))

        # Extract functions and classes from implementation
        impl_functions, impl_classes = self._extract_definitions(implementation)

        # Check for missing implementations
        missing_functions = spec_functions - impl_functions
        for func in missing_functions:
            analysis.diffs.append(
                ArchitectureDiff(
                    category="implementation",
                    severity=DiffSeverity.ERROR,
                    message=f"Missing function from spec: {func}",
                    affected_component=func,
                    suggestion="Implement all functions defined in spec",
                )
            )

        missing_classes = spec_classes - impl_classes
        for cls in missing_classes:
            analysis.diffs.append(
                ArchitectureDiff(
                    category="implementation",
                    severity=DiffSeverity.ERROR,
                    message=f"Missing class from spec: {cls}",
                    affected_component=cls,
                    suggestion="Implement all classes defined in spec",
                )
            )

        analysis.metadata["spec_functions"] = list(spec_functions)
        analysis.metadata["spec_classes"] = list(spec_classes)
        analysis.metadata["impl_functions"] = list(impl_functions)
        analysis.metadata["impl_classes"] = list(impl_classes)

        analysis.compatibility_score = self._calculate_score(analysis)
        analysis.is_compatible = len([
            d for d in analysis.diffs
            if d.severity in [DiffSeverity.CRITICAL, DiffSeverity.ERROR]
        ]) == 0

        return analysis

    def _extract_definitions(self, code: str) -> Tuple[Set[str], Set[str]]:
        """Extract function and class names from code."""
        import ast

        functions = set()
        classes = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.add(node.name)
        except SyntaxError:
            pass

        return functions, classes


def create_analyzer(base_path: str = "/home/pisarna/senti_system") -> ArchitectureDiffAnalyzer:
    """
    Create and return an architecture diff analyzer.

    Args:
        base_path: Base path to Senti OS installation

    Returns:
        ArchitectureDiffAnalyzer instance
    """
    return ArchitectureDiffAnalyzer(base_path)


def analyze_module(
    module_spec: Dict,
    module_path: str,
) -> ArchitectureAnalysis:
    """
    Convenience function to analyze a module.

    Args:
        module_spec: Module specification
        module_path: Proposed module path

    Returns:
        ArchitectureAnalysis
    """
    analyzer = create_analyzer()
    return analyzer.analyze_new_module(module_spec, module_path)

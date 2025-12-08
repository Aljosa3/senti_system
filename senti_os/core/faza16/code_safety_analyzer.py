"""
Code Safety Analyzer for SENTI OS FAZA 16

Performs AST-based code analysis to detect:
- Dangerous function calls (eval, exec, os.system, subprocess)
- Forbidden import paths
- Incomplete module definitions
- Invalid class and function definitions
- Security vulnerabilities
- Code quality issues
"""

import ast
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetySeverity(Enum):
    """Severity levels for safety issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SafetyIssue:
    """Represents a code safety issue."""
    line_number: int
    severity: SafetySeverity
    category: str
    message: str
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class CodeSafetyReport:
    """Result of code safety analysis."""
    is_safe: bool
    issues: List[SafetyIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    safety_score: float = 100.0  # 0-100, higher is better


class CodeSafetyAnalyzer:
    """
    Analyzes Python code for safety and security issues using AST.

    Detects:
    - Dangerous built-in calls
    - Unsafe imports
    - Incomplete definitions
    - Security vulnerabilities
    """

    DANGEROUS_BUILTINS = {
        "eval": "Arbitrary code execution risk",
        "exec": "Arbitrary code execution risk",
        "compile": "Code compilation risk",
        "__import__": "Dynamic import risk",
        "globals": "Global scope access risk",
        "locals": "Local scope access risk",
        "vars": "Namespace access risk",
        "open": "File access - ensure proper validation",
    }

    DANGEROUS_MODULES = {
        "os.system": "Shell command execution risk",
        "subprocess.call": "Process execution risk",
        "subprocess.run": "Process execution risk - use with shell=False",
        "subprocess.Popen": "Process execution risk - use with shell=False",
        "pickle.loads": "Arbitrary code execution via deserialization",
        "yaml.load": "Use yaml.safe_load instead",
        "marshal.loads": "Deserialization risk",
    }

    FORBIDDEN_PATHS = [
        "senti_os/kernel/",
        "senti_os/boot/",
        "/etc/",
        "/sys/",
        "/proc/",
    ]

    def __init__(self):
        """Initialize code safety analyzer."""
        logger.info("Code Safety Analyzer initialized")

    def analyze_code(self, code: str, filename: str = "<string>") -> CodeSafetyReport:
        """
        Analyze Python code for safety issues.

        Args:
            code: Python source code as string
            filename: Filename for error reporting

        Returns:
            CodeSafetyReport with analysis results
        """
        report = CodeSafetyReport(is_safe=True)

        if not code or not code.strip():
            report.issues.append(
                SafetyIssue(
                    line_number=0,
                    severity=SafetySeverity.ERROR,
                    category="structure",
                    message="Code is empty",
                )
            )
            report.is_safe = False
            report.safety_score = 0.0
            return report

        # Try to parse the code
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            report.issues.append(
                SafetyIssue(
                    line_number=e.lineno or 0,
                    severity=SafetySeverity.CRITICAL,
                    category="syntax",
                    message=f"Syntax error: {e.msg}",
                    code_snippet=e.text,
                )
            )
            report.is_safe = False
            report.safety_score = 0.0
            return report

        # Perform AST-based checks
        self._check_dangerous_calls(tree, report, code)
        self._check_dangerous_imports(tree, report)
        self._check_forbidden_paths(tree, report, code)
        self._check_module_completeness(tree, report)
        self._check_definitions(tree, report)

        # Calculate safety score
        report.safety_score = self._calculate_safety_score(report)

        # Determine if safe
        critical_issues = [
            i for i in report.issues
            if i.severity in [SafetySeverity.CRITICAL, SafetySeverity.ERROR]
        ]
        report.is_safe = len(critical_issues) == 0

        logger.info(
            f"Code safety analysis complete: Safe={report.is_safe}, "
            f"Score={report.safety_score:.1f}, Issues={len(report.issues)}"
        )

        return report

    def _check_dangerous_calls(
        self,
        tree: ast.AST,
        report: CodeSafetyReport,
        code: str,
    ) -> None:
        """Check for dangerous built-in function calls."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node.func)

                if func_name in self.DANGEROUS_BUILTINS:
                    snippet = self._get_code_snippet(code, node.lineno)
                    report.issues.append(
                        SafetyIssue(
                            line_number=node.lineno,
                            severity=SafetySeverity.CRITICAL,
                            category="dangerous_call",
                            message=f"Dangerous function call: {func_name}",
                            code_snippet=snippet,
                            suggestion=self.DANGEROUS_BUILTINS[func_name],
                        )
                    )

                # Check for dangerous module methods
                full_name = self._get_full_call_name(node.func)
                for dangerous_call, reason in self.DANGEROUS_MODULES.items():
                    if full_name and dangerous_call in full_name:
                        snippet = self._get_code_snippet(code, node.lineno)
                        report.issues.append(
                            SafetyIssue(
                                line_number=node.lineno,
                                severity=SafetySeverity.CRITICAL,
                                category="dangerous_call",
                                message=f"Dangerous call: {dangerous_call}",
                                code_snippet=snippet,
                                suggestion=reason,
                            )
                        )

    def _check_dangerous_imports(
        self,
        tree: ast.AST,
        report: CodeSafetyReport,
    ) -> None:
        """Check for dangerous or suspicious imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._validate_import(alias.name, node.lineno, report)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._validate_import(node.module, node.lineno, report)

    def _validate_import(
        self,
        module_name: str,
        line_number: int,
        report: CodeSafetyReport,
    ) -> None:
        """Validate a single import."""
        # Check for dangerous module prefixes
        dangerous_prefixes = ["os.system", "subprocess", "pickle", "marshal"]

        for prefix in dangerous_prefixes:
            if module_name.startswith(prefix):
                report.warnings.append(
                    f"Line {line_number}: Importing potentially dangerous module: {module_name}"
                )

    def _check_forbidden_paths(
        self,
        tree: ast.AST,
        report: CodeSafetyReport,
        code: str,
    ) -> None:
        """Check for references to forbidden file paths."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for forbidden_path in self.FORBIDDEN_PATHS:
                    if forbidden_path in node.value:
                        snippet = self._get_code_snippet(code, node.lineno)
                        report.issues.append(
                            SafetyIssue(
                                line_number=node.lineno,
                                severity=SafetySeverity.ERROR,
                                category="forbidden_path",
                                message=f"Reference to forbidden path: {forbidden_path}",
                                code_snippet=snippet,
                                suggestion="Avoid accessing protected system directories",
                            )
                        )

    def _check_module_completeness(
        self,
        tree: ast.AST,
        report: CodeSafetyReport,
    ) -> None:
        """Check if module is complete (not just stub/placeholder)."""
        has_functions = False
        has_classes = False
        has_imports = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_functions = True
            elif isinstance(node, ast.ClassDef):
                has_classes = True
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                has_imports = True

        # Check if module is just a stub
        if not has_functions and not has_classes:
            report.warnings.append(
                "Module appears incomplete: no functions or classes defined"
            )

        # Store metadata
        report.metadata["has_functions"] = has_functions
        report.metadata["has_classes"] = has_classes
        report.metadata["has_imports"] = has_imports

    def _check_definitions(
        self,
        tree: ast.AST,
        report: CodeSafetyReport,
    ) -> None:
        """Check function and class definitions."""
        function_count = 0
        class_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                self._validate_function(node, report)

            elif isinstance(node, ast.ClassDef):
                class_count += 1
                self._validate_class(node, report)

        report.metadata["function_count"] = function_count
        report.metadata["class_count"] = class_count

    def _validate_function(
        self,
        node: ast.FunctionDef,
        report: CodeSafetyReport,
    ) -> None:
        """Validate a function definition."""
        # Check for empty functions (just pass or ...)
        if len(node.body) == 1:
            if isinstance(node.body[0], ast.Pass):
                report.warnings.append(
                    f"Line {node.lineno}: Function '{node.name}' is a stub (only contains pass)"
                )
            elif isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                if node.body[0].value.value == Ellipsis:
                    report.warnings.append(
                        f"Line {node.lineno}: Function '{node.name}' is incomplete (only contains ...)"
                    )

        # Check for docstring
        has_docstring = (
            len(node.body) > 0 and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)
        )

        if not has_docstring and not node.name.startswith("_"):
            report.warnings.append(
                f"Line {node.lineno}: Public function '{node.name}' missing docstring"
            )

    def _validate_class(
        self,
        node: ast.ClassDef,
        report: CodeSafetyReport,
    ) -> None:
        """Validate a class definition."""
        # Check for empty classes
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            report.warnings.append(
                f"Line {node.lineno}: Class '{node.name}' is empty"
            )

        # Check for __init__ method
        has_init = any(
            isinstance(item, ast.FunctionDef) and item.name == "__init__"
            for item in node.body
        )

        if not has_init:
            report.warnings.append(
                f"Line {node.lineno}: Class '{node.name}' has no __init__ method"
            )

    def _get_func_name(self, node: ast.expr) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _get_full_call_name(self, node: ast.expr) -> Optional[str]:
        """Get full qualified name of a call."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def _get_code_snippet(self, code: str, line_number: int) -> str:
        """Extract code snippet at line number."""
        lines = code.split('\n')
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def _calculate_safety_score(self, report: CodeSafetyReport) -> float:
        """
        Calculate safety score (0-100).

        Args:
            report: CodeSafetyReport to score

        Returns:
            Score between 0 and 100
        """
        score = 100.0

        # Deduct points for issues
        for issue in report.issues:
            if issue.severity == SafetySeverity.CRITICAL:
                score -= 30.0
            elif issue.severity == SafetySeverity.ERROR:
                score -= 15.0
            elif issue.severity == SafetySeverity.WARNING:
                score -= 5.0
            else:  # INFO
                score -= 1.0

        # Deduct points for warnings
        score -= len(report.warnings) * 2.0

        return max(0.0, min(100.0, score))

    def analyze_file(self, filepath: str) -> CodeSafetyReport:
        """
        Analyze a Python file for safety issues.

        Args:
            filepath: Path to Python file

        Returns:
            CodeSafetyReport with analysis results
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.analyze_code(code, filename=filepath)
        except FileNotFoundError:
            report = CodeSafetyReport(is_safe=False)
            report.issues.append(
                SafetyIssue(
                    line_number=0,
                    severity=SafetySeverity.ERROR,
                    category="file",
                    message=f"File not found: {filepath}",
                )
            )
            return report
        except Exception as e:
            report = CodeSafetyReport(is_safe=False)
            report.issues.append(
                SafetyIssue(
                    line_number=0,
                    severity=SafetySeverity.ERROR,
                    category="file",
                    message=f"Error reading file: {e}",
                )
            )
            return report


def create_analyzer() -> CodeSafetyAnalyzer:
    """
    Create and return a code safety analyzer.

    Returns:
        CodeSafetyAnalyzer instance
    """
    return CodeSafetyAnalyzer()


def analyze_code(code: str, filename: str = "<string>") -> CodeSafetyReport:
    """
    Convenience function to analyze code.

    Args:
        code: Python source code
        filename: Filename for error reporting

    Returns:
        CodeSafetyReport
    """
    analyzer = create_analyzer()
    return analyzer.analyze_code(code, filename)

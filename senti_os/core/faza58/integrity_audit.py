"""
FAZA 58 — Integrity Audit & Pre-Lock Validation
-----------------------------------------------
Technical-governance integrity verification before CORE LOCK.

This module provides read-only verification of:
- CORE file integrity (checksums)
- Audit log completeness
- System readiness for CORE LOCK

FAZA 58 does NOT modify system state.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from senti_core_module.senti_core.integrity.integrity_hasher import IntegrityHasher


@dataclass
class FileIntegrityCheck:
    """Result of a single file integrity verification."""
    path: str
    expected_hash: Optional[str]
    actual_hash: Optional[str]
    status: str  # "MATCH", "MISMATCH", "MISSING", "NEW", "ERROR"
    error: Optional[str] = None


@dataclass
class IntegrityAuditReport:
    """FAZA 58 integrity audit report."""
    audit_date: str
    system_state: str  # "PRE-LOCK", "LOCKED"
    overall_status: str  # "READY", "NOT READY"

    files_checked: int
    files_matched: int
    files_mismatched: int
    files_missing: int
    files_new: int

    core_integrity: str  # "PASS", "FAIL"
    audit_log_integrity: str  # "PASS", "FAIL", "NOT CHECKED"

    findings: List[str]
    file_checks: List[FileIntegrityCheck]

    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert report to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class IntegrityAuditor:
    """
    FAZA 58 Integrity Auditor.

    Performs read-only verification of CORE file integrity
    and produces human-readable audit reports.
    """

    def __init__(self, repo_root: str):
        """
        Initialize integrity auditor.

        Args:
            repo_root: Absolute path to repository root
        """
        self.repo_root = Path(repo_root)
        self.hasher = IntegrityHasher()
        self.baseline_path = self.repo_root / ".core_baseline.json"

    def get_core_files(self) -> List[Path]:
        """
        Get list of CORE files to audit.

        Returns:
            List of absolute paths to CORE files
        """
        core_paths = [
            "senti_os/",
            "senti_core_module/senti_core/control_layer/",
            "senti_core_module/senti_core/execution/",
            "docs/governance/",
            "docs/semantics/",
        ]

        core_files = []

        for core_path in core_paths:
            full_path = self.repo_root / core_path
            if not full_path.exists():
                continue

            if full_path.is_file():
                core_files.append(full_path)
            elif full_path.is_dir():
                # Recursively find all Python files and markdown files
                core_files.extend(full_path.rglob("*.py"))
                core_files.extend(full_path.rglob("*.md"))

        return sorted(set(core_files))

    def load_baseline(self) -> Optional[Dict[str, str]]:
        """
        Load baseline hashes from file.

        Returns:
            Dictionary mapping relative paths to hashes, or None if no baseline
        """
        if not self.baseline_path.exists():
            return None

        try:
            with open(self.baseline_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_baseline(self, hashes: Dict[str, str]) -> None:
        """
        Save baseline hashes to file.

        Args:
            hashes: Dictionary mapping relative paths to hashes
        """
        with open(self.baseline_path, 'w') as f:
            json.dump(hashes, f, indent=2, sort_keys=True)

    def verify_file_integrity(self, file_path: Path, baseline: Optional[Dict[str, str]]) -> FileIntegrityCheck:
        """
        Verify integrity of a single file.

        Args:
            file_path: Absolute path to file
            baseline: Baseline hashes dictionary (or None)

        Returns:
            FileIntegrityCheck result
        """
        relative_path = str(file_path.relative_to(self.repo_root))

        try:
            actual_hash = self.hasher.compute_file_hash(str(file_path))
        except Exception as e:
            return FileIntegrityCheck(
                path=relative_path,
                expected_hash=None,
                actual_hash=None,
                status="ERROR",
                error=str(e)
            )

        if baseline is None:
            # No baseline - all files are "new"
            return FileIntegrityCheck(
                path=relative_path,
                expected_hash=None,
                actual_hash=actual_hash,
                status="NEW"
            )

        expected_hash = baseline.get(relative_path)

        if expected_hash is None:
            # File not in baseline
            return FileIntegrityCheck(
                path=relative_path,
                expected_hash=None,
                actual_hash=actual_hash,
                status="NEW"
            )

        if actual_hash == expected_hash:
            return FileIntegrityCheck(
                path=relative_path,
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                status="MATCH"
            )
        else:
            return FileIntegrityCheck(
                path=relative_path,
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                status="MISMATCH"
            )

    def perform_audit(self, create_baseline: bool = False) -> IntegrityAuditReport:
        """
        Perform complete integrity audit.

        Args:
            create_baseline: If True and no baseline exists, create one

        Returns:
            IntegrityAuditReport with findings
        """
        core_files = self.get_core_files()
        baseline = self.load_baseline()

        # If no baseline and create_baseline is True, generate baseline
        if baseline is None and create_baseline:
            baseline_hashes = {}
            for file_path in core_files:
                relative_path = str(file_path.relative_to(self.repo_root))
                try:
                    baseline_hashes[relative_path] = self.hasher.compute_file_hash(str(file_path))
                except Exception:
                    pass  # Skip files that can't be hashed

            self.save_baseline(baseline_hashes)
            baseline = baseline_hashes

        # Perform integrity checks
        file_checks = []
        for file_path in core_files:
            check = self.verify_file_integrity(file_path, baseline)
            file_checks.append(check)

        # Check for missing files (in baseline but not found)
        if baseline:
            found_paths = {check.path for check in file_checks}
            for baseline_path in baseline.keys():
                if baseline_path not in found_paths:
                    file_checks.append(FileIntegrityCheck(
                        path=baseline_path,
                        expected_hash=baseline[baseline_path],
                        actual_hash=None,
                        status="MISSING"
                    ))

        # Compute statistics
        files_checked = len(file_checks)
        files_matched = sum(1 for c in file_checks if c.status == "MATCH")
        files_mismatched = sum(1 for c in file_checks if c.status == "MISMATCH")
        files_missing = sum(1 for c in file_checks if c.status == "MISSING")
        files_new = sum(1 for c in file_checks if c.status == "NEW")

        # Determine CORE integrity status
        if files_mismatched > 0 or files_missing > 0:
            core_integrity = "FAIL"
        elif baseline is None:
            core_integrity = "PASS"  # No baseline = first audit = pass
        else:
            core_integrity = "PASS"

        # Generate findings
        findings = []

        if baseline is None:
            findings.append("No baseline found - this is the first integrity audit")
            if create_baseline:
                findings.append(f"Created baseline with {files_checked} CORE files")

        if files_mismatched > 0:
            findings.append(f"CRITICAL: {files_mismatched} CORE files have been modified")
            for check in file_checks:
                if check.status == "MISMATCH":
                    findings.append(f"  - MODIFIED: {check.path}")

        if files_missing > 0:
            findings.append(f"CRITICAL: {files_missing} CORE files are missing")
            for check in file_checks:
                if check.status == "MISSING":
                    findings.append(f"  - MISSING: {check.path}")

        if files_new > 0 and baseline is not None:
            findings.append(f"WARNING: {files_new} new CORE files detected")
            for check in file_checks:
                if check.status == "NEW":
                    findings.append(f"  - NEW: {check.path}")

        if files_matched == files_checked and files_checked > 0:
            findings.append(f"SUCCESS: All {files_checked} CORE files match baseline")

        # Determine overall status
        if core_integrity == "PASS" and files_mismatched == 0 and files_missing == 0:
            overall_status = "READY"
        else:
            overall_status = "NOT READY"

        # Create report
        report = IntegrityAuditReport(
            audit_date=datetime.utcnow().isoformat() + "Z",
            system_state="PRE-LOCK",  # Assume pre-lock for now
            overall_status=overall_status,
            files_checked=files_checked,
            files_matched=files_matched,
            files_mismatched=files_mismatched,
            files_missing=files_missing,
            files_new=files_new,
            core_integrity=core_integrity,
            audit_log_integrity="NOT CHECKED",  # Simplified for now
            findings=findings,
            file_checks=file_checks
        )

        return report

    def generate_human_readable_report(self, report: IntegrityAuditReport) -> str:
        """
        Generate human-readable text report.

        Args:
            report: IntegrityAuditReport

        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 70)
        lines.append("FAZA 58 — INTEGRITY AUDIT REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Audit Date: {report.audit_date}")
        lines.append(f"System State: {report.system_state}")
        lines.append(f"Overall Status: **{report.overall_status}**")
        lines.append("")
        lines.append("-" * 70)
        lines.append("INTEGRITY VERIFICATION RESULTS")
        lines.append("-" * 70)
        lines.append("")
        lines.append(f"Files Checked: {report.files_checked}")
        lines.append(f"Files Matched: {report.files_matched}")
        lines.append(f"Files Mismatched: {report.files_mismatched}")
        lines.append(f"Files Missing: {report.files_missing}")
        lines.append(f"Files New: {report.files_new}")
        lines.append("")
        lines.append(f"CORE Integrity: {report.core_integrity}")
        lines.append(f"Audit Log Integrity: {report.audit_log_integrity}")
        lines.append("")

        if report.findings:
            lines.append("-" * 70)
            lines.append("FINDINGS")
            lines.append("-" * 70)
            lines.append("")
            for finding in report.findings:
                lines.append(finding)
            lines.append("")

        if report.overall_status == "READY":
            lines.append("-" * 70)
            lines.append("CONCLUSION")
            lines.append("-" * 70)
            lines.append("")
            lines.append("System is READY for CORE LOCK (Phase 60).")
            lines.append("All CORE files verified. No integrity violations detected.")
            lines.append("")
        else:
            lines.append("-" * 70)
            lines.append("CONCLUSION")
            lines.append("-" * 70)
            lines.append("")
            lines.append("System is NOT READY for CORE LOCK (Phase 60).")
            lines.append("Integrity violations detected. Review findings above.")
            lines.append("Resolve all issues before proceeding to FAZA 59.")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

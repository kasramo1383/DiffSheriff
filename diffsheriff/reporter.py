"""
Reporter and CI/CD exit code resolution engine.
Enforces the priority order: 30 > 10 > 20 > 40 > 0.
"""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXIT_PASS = 0
EXIT_VULN_REMAINS_OR_NEW = 10
EXIT_FUNC_REGRESSION = 20
EXIT_BUILD_OR_CONFIG_ERROR = 30
EXIT_INCONCLUSIVE = 40


def resolve_priority_exit_code(
    build_failed: bool,
    vuln_detected: bool,
    regression_detected: bool,
    is_inconclusive: bool,
) -> Tuple[int, str]:
    """
    Resolves the process exit code based on the strict hierarchy:
    30 (BUILD_ERROR) > 10 (VULN) > 20 (REGRESSION) > 40 (INCONCLUSIVE) > 0 (PASS)
    """
    if build_failed:
        return EXIT_BUILD_OR_CONFIG_ERROR, "BUILD_OR_CONFIG_ERROR"
    if vuln_detected:
        return EXIT_VULN_REMAINS_OR_NEW, "VULN_REMAINS_OR_NEW_ISSUE"
    if regression_detected:
        return EXIT_FUNC_REGRESSION, "FUNC_REGRESSION"
    if is_inconclusive:
        return EXIT_INCONCLUSIVE, "INCONCLUSIVE"
    return EXIT_PASS, "PASS"


@dataclass
class FindingReport:
    finding_id: str
    status: str
    error_type: str
    detection_mechanism: str
    triggering_input: str
    minimized_input: Optional[str]
    correlation_type: str
    reproduced_cleanly: bool
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationSummary:
    target_name: str
    exit_code: int
    verdict: str
    total_tests_run: int
    functional_passed: int
    functional_failed: int
    security_flaws_fixed: int
    security_flaws_lingering: int
    hardening_degraded: bool
    findings: List[FindingReport]
    analysis_complete: bool = True
    notes: Optional[List[str]] = None
    security_status: str = "INCONCLUSIVE"
    functional_status: str = "INCONCLUSIVE"
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_name": self.target_name,
            "exit_code": self.exit_code,
            "verdict": self.verdict,
            "total_tests_run": self.total_tests_run,
            "functional_passed": self.functional_passed,
            "functional_failed": self.functional_failed,
            "security_flaws_fixed": self.security_flaws_fixed,
            "security_flaws_lingering": self.security_flaws_lingering,
            "hardening_degraded": self.hardening_degraded,
            "analysis_complete": self.analysis_complete,
            "notes": self.notes or [],
            "schema_version": "2.0",
            "security_status": self.security_status,
            "functional_status": self.functional_status,
            "evidence": self.evidence,
            "findings": [asdict(f) for f in self.findings],
        }

    def write_json(self, output_path: Path) -> None:
        import os
        import tempfile

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output_path.parent, delete=False
        ) as f:
            temporary = Path(f.name)
            try:
                json.dump(self.to_dict(), f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                f.close()
                temporary.unlink(missing_ok=True)
                raise
        try:
            temporary.replace(output_path)
        finally:
            temporary.unlink(missing_ok=True)

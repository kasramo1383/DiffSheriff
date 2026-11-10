"""
Reporter and CI/CD exit code resolution engine.
Enforces the priority order: 30 > 10 > 20 > 40 > 0.
"""

from dataclasses import asdict, dataclass
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
        return EXIT_BUILD_OR_CONFIG_ERROR, "ERROR_CONFIG_OR_BUILD"
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
            "findings": [asdict(f) for f in self.findings],
        }

    def write_json(self, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

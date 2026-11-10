"""The incomplete orchestrator must never claim a passing validation."""

import json

from click.testing import CliRunner

from diffsheriff.cli import main

from .test_config import VALID_CONFIG


def test_cli_fails_closed_with_inconclusive_report(tmp_path):
    config = tmp_path / "target.yaml"
    report = tmp_path / "report.json"
    config.write_text(VALID_CONFIG, encoding="utf-8")

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "--output-json", str(report)],
    )

    assert result.exit_code == 40
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["verdict"] == "INCONCLUSIVE"
    assert payload["analysis_complete"] is False

"""CLI reports configuration and operation errors without claiming validation."""

import json
from click.testing import CliRunner
from diffsheriff.cli import main
from .test_config import VALID_CONFIG


def test_cli_missing_suites_is_configuration_error(tmp_path):
    config = tmp_path / "target.yaml"
    report = tmp_path / "report.json"
    config.write_text(VALID_CONFIG, encoding="utf-8")
    result = CliRunner().invoke(
        main, ["--config", str(config), "--output-json", str(report)]
    )
    assert result.exit_code == 30
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["verdict"] == "BUILD_OR_CONFIG_ERROR"
    assert payload["analysis_complete"] is False


def test_missing_configuration_writes_report(tmp_path):
    report = tmp_path / "report.json"
    result = CliRunner().invoke(
        main, ["--config", str(tmp_path / "missing"), "--output-json", str(report)]
    )
    assert result.exit_code == 30
    assert json.loads(report.read_text())["notes"]

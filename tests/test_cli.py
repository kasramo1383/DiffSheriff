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
    assert payload["analysis_incomplete_reasons"] == ["setup_failed"]


def test_missing_configuration_writes_report(tmp_path):
    report = tmp_path / "report.json"
    result = CliRunner().invoke(
        main, ["--config", str(tmp_path / "missing"), "--output-json", str(report)]
    )
    assert result.exit_code == 30
    payload = json.loads(report.read_text())
    assert payload["analysis_complete"] is False
    assert payload["analysis_incomplete_reasons"] == ["setup_failed"]
    assert payload["notes"]


def test_cli_refreshes_empty_regression_export(tmp_path, monkeypatch):
    from types import SimpleNamespace

    import diffsheriff.cli as cli
    from .test_regressions import functional_export

    cfg = SimpleNamespace(
        config_directory=tmp_path,
        test_suites=SimpleNamespace(regression_directory="not-created"),
        target_name="harmless",
        base_ref="a" * 40,
        patch_ref="b" * 40,
    )
    summary = cli.empty_summary(cfg.target_name)
    summary.mark_incomplete("baseline_identity_unestablished")
    monkeypatch.setattr(cli.DiffSheriffConfig, "from_yaml", lambda _: cfg)
    monkeypatch.setattr(cli, "run_pipeline", lambda *_: summary)
    export = tmp_path / "export"
    functional_export(export, {"obsolete.json": "obsolete.input"})
    (export / "notes.txt").write_text("keep")
    output = tmp_path / "report.json"
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(tmp_path / "ignored.yaml"),
            "--output-json",
            str(output),
            "--export-regressions",
            str(export),
        ],
    )
    assert result.exit_code == 40, result.output
    assert {path.name for path in export.iterdir()} == {"notes.txt"}
    assert json.loads(output.read_text())["exit_code"] == 40

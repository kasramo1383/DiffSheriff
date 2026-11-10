"""
Command-line interface for DiffSheriff.
"""

from pathlib import Path
import sys
import click
from diffsheriff.config import DiffSheriffConfig
from diffsheriff.reporter import (
    EXIT_BUILD_OR_CONFIG_ERROR,
    EXIT_INCONCLUSIVE,
    ValidationSummary,
)


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to tool_config.yaml",
)
@click.option(
    "--output-json",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("validation_report.json"),
    help="Path for generated JSON report",
)
def main(config: Path, output_json: Path) -> None:
    """
    DiffSheriff: Automated security patch validation and regression testing in CI/CD.
    """
    click.echo(f"Loading configuration from: {config}")

    try:
        cfg = DiffSheriffConfig.from_yaml(config)
    except Exception as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(EXIT_BUILD_OR_CONFIG_ERROR)

    click.echo(f"Target: {cfg.target_name} ({cfg.language})")
    click.echo(f"Repository: {cfg.repository_path}")

    # The end-to-end base/patch orchestrator is not implemented yet. Failing
    # closed prevents a scaffold invocation from being mistaken for validation.
    summary = ValidationSummary(
        target_name=cfg.target_name,
        exit_code=EXIT_INCONCLUSIVE,
        verdict="INCONCLUSIVE",
        total_tests_run=0,
        functional_passed=0,
        functional_failed=0,
        security_flaws_fixed=0,
        security_flaws_lingering=0,
        hardening_degraded=False,
        findings=[],
        analysis_complete=False,
        notes=[
            "End-to-end base/patch build, execution, comparison, and evidence "
            "orchestration is not implemented."
        ],
    )
    summary.write_json(output_json)

    click.echo(f"Report: {output_json}")
    click.echo("Verdict: INCONCLUSIVE (Exit Code 40)")
    sys.exit(EXIT_INCONCLUSIVE)


if __name__ == "__main__":
    main()

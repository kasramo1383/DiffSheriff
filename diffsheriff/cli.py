"""
Command-line interface for DiffSheriff.
"""

from pathlib import Path
import sys
import click
from diffsheriff.config import DiffSheriffConfig
from diffsheriff.reporter import (
    EXIT_BUILD_OR_CONFIG_ERROR,
    EXIT_PASS,
    resolve_priority_exit_code,
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

    # Temporary baseline pass for demonstration
    exit_code, verdict = resolve_priority_exit_code(
        build_failed=False,
        vuln_detected=False,
        regression_detected=False,
        is_inconclusive=False,
    )

    click.echo(f"Verdict: {verdict} (Exit Code {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

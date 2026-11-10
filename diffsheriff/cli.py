"""Command-line interface with structured evidence on all operational failures."""

from pathlib import Path
import click

from diffsheriff.config import DiffSheriffConfig
from diffsheriff.pipeline import empty_summary, run_pipeline


@click.command()
@click.option(
    "--config", "-c", type=click.Path(dir_okay=False, path_type=Path), required=True
)
@click.option(
    "--output-json",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("validation_report.json"),
)
@click.option(
    "--artifacts",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path(".diffsheriff/runs"),
    help="Retained builds, logs, inputs, and reproducers.",
)
def main(config, output_json, artifacts):
    """Validate an authorized local C/C++ patch in isolated Linux containers."""
    summary = empty_summary("unknown")
    try:
        cfg = DiffSheriffConfig.from_yaml(config)
        click.echo(
            f"Validating {cfg.target_name}: {cfg.base_ref[:12]} -> {cfg.patch_ref[:12]}"
        )
        summary = run_pipeline(cfg, artifacts.resolve())
    except Exception as error:
        summary.exit_code, summary.verdict = 30, "BUILD_OR_CONFIG_ERROR"
        summary.notes.append(f"{type(error).__name__}: {error}")
    try:
        summary.write_json(output_json)
    except OSError as error:
        click.echo(f"Cannot write report: {error}", err=True)
        raise click.exceptions.Exit(30)
    click.echo(
        f"{summary.verdict} (exit {summary.exit_code}); "
        f"{summary.total_tests_run} suite executions"
    )
    click.echo(
        f"Security: {summary.security_status}; "
        f"functional: {summary.functional_status}; "
        f"analysis: {'complete' if summary.analysis_complete else 'incomplete'}"
    )
    for finding in summary.findings:
        click.echo(
            f"  {finding.status}: {finding.triggering_input} "
            f"[{finding.evidence.get('mode', '')}] - {finding.error_type}"
        )
    for note in summary.notes or []:
        click.echo(f"  {note}")
    click.echo(f"Report: {output_json}")
    raise click.exceptions.Exit(summary.exit_code)


if __name__ == "__main__":
    main()

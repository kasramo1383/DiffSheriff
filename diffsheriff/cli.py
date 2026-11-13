"""Command-line interface with structured evidence on all operational failures."""

from pathlib import Path
import click

from diffsheriff.config import DiffSheriffConfig
from diffsheriff.pipeline import discover_cases, empty_summary, run_pipeline
from diffsheriff.regressions import copy_regressions


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
@click.option("--regressions-from", type=click.Path(file_okay=False, path_type=Path))
@click.option("--export-regressions", type=click.Path(file_okay=False, path_type=Path))
def main(config, output_json, artifacts, regressions_from, export_regressions):
    """Validate an authorized local C/C++ patch in isolated Linux containers."""
    summary = empty_summary("unknown")
    try:
        cfg = DiffSheriffConfig.from_yaml(config)
        regressions = cfg.config_directory / cfg.test_suites.regression_directory
        if not regressions.resolve().is_relative_to(cfg.config_directory):
            raise ValueError("Regression directory escapes the configuration directory")
        if regressions_from is not None:
            local_cases, _ = discover_cases(cfg)
            copy_regressions(
                regressions_from, regressions, cfg.base_ref, local_cases=local_cases
            )
        click.echo(
            f"Validating {cfg.target_name}: {cfg.base_ref[:12]} -> {cfg.patch_ref[:12]}"
        )
        summary = run_pipeline(cfg, artifacts.resolve())
        if export_regressions is not None:
            if regressions.exists():
                copy_regressions(
                    regressions, export_regressions, cfg.base_ref, replace_existing=True
                )
            else:
                export_regressions.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        summary.exit_code, summary.verdict = 30, "BUILD_OR_CONFIG_ERROR"
        summary.analysis_complete = False
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
    for side, hardening in summary.evidence.get("hardening", {}).items():
        click.echo(
            f"Hardening (release) {side}: NX={hardening['nx']} "
            f"PIE={hardening['pie']} RELRO={hardening['relro']} "
            f"canary={hardening['canary']}"
        )
    for side, builds in summary.evidence.get("builds", {}).items():
        for mode, build in builds.items():
            indicators = build.get("elf", {}).get("indicators", {})
            if indicators:
                families = ",".join(indicators["sanitizer_symbols"]) or "none observed"
                click.echo(
                    f"  {side}/{mode}: sanitizer symbols={families}; "
                    f"FORTIFY symbol candidates={len(indicators['fortify_symbols'])}; "
                    f"symbol tables={','.join(indicators['symbol_tables']) or 'none'}"
                )
    for finding in summary.findings:
        click.echo(
            f"  {finding.status}: {finding.triggering_input} "
            f"[{finding.evidence.get('mode', '')}] - {finding.error_type}"
        )
        click.echo(
            f"    detection: {finding.detection_mechanism}; "
            f"correlation: {finding.correlation_type}; "
            f"stable: {finding.reproduced_cleanly}"
        )
        if finding.evidence.get("reason"):
            click.echo(f"    {finding.evidence['reason']}")
        if finding.minimized_input:
            click.echo(f"    minimized input: {finding.minimized_input}")
    for note in summary.notes or []:
        click.echo(f"  {note}")
    if summary.evidence.get("run_directory"):
        click.echo(f"Evidence directory: {summary.evidence['run_directory']}")
    click.echo(f"Report: {output_json}")
    raise click.exceptions.Exit(summary.exit_code)


if __name__ == "__main__":
    main()

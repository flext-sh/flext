"""Command-line interface for flx-ldap.

This module provides the CLI commands for orchestrating LDAP ETL operations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from flx_ldap.config import FlxLDAPConfig
from flx_ldap.migrator import GenericMigrationOrchestrator
from flx_ldap.orchestrator import LDAPOrchestrator
from flx_ldap.utils import (
    count_records_in_jsonl,
    extract_streams_from_jsonl,
    format_bytes,
)
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option("--log-level", default="INFO", help="Logging level")
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None, log_level: str) -> None:
    """FLX-LDAP: Unified CLI for LDAP ETL operations."""
    # Load configuration
    config = (
        FlxLDAPConfig.from_file(config_path)
        if config_path
        else FlxLDAPConfig.from_env()
    )

    config.log_level = log_level

    # Create orchestrator
    orchestrator = LDAPOrchestrator(config)

    # Store in context
    ctx.obj = {
        "config": config,
        "orchestrator": orchestrator,
    }


@cli.command()
@click.option("--catalog", type=click.Path(path_type=Path), help="Catalog file path")
@click.option("--state", type=click.Path(path_type=Path), help="State file path")
@click.option("--output", type=click.Path(path_type=Path), help="Output file path")
@click.pass_context
def extract(
    ctx: click.Context,
    catalog: Path | None,
    state: Path | None,
    output: Path | None,
) -> None:
    """Extract data from LDAP using tap-ldap."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]

    success, output_path = orchestrator.run_tap(catalog, state, output)

    if success and output_path:
        # Show statistics
        total_records = count_records_in_jsonl(output_path)
        file_size = output_path.stat().st_size
        streams = extract_streams_from_jsonl(output_path)

        console.print("\n[bold]Extraction Summary:[/bold]")
        console.print(f"  Total records: {total_records:,}")
        console.print(f"  Streams: {', '.join(sorted(streams))}")
        console.print(f"  Output size: {format_bytes(file_size)}")
        console.print(f"  Output path: {output_path}")
    else:
        sys.exit(1)


@cli.command()
@click.argument("dbt_command", default="run")
@click.option("--models", "-m", help="Specific models to run")
@click.option("--full-refresh", is_flag=True, help="Force full refresh")
@click.pass_context
def transform(
    ctx: click.Context,
    dbt_command: str,
    models: str | None,
    *,
    full_refresh: bool,
) -> None:
    """Transform data using dbt-ldap."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]

    models_list = models.split(",") if models else None
    success = orchestrator.run_dbt(dbt_command, models_list, full_refresh=full_refresh)

    if not success:
        sys.exit(1)


@cli.command()
@click.option(
    "--input", type=click.Path(exists=True, path_type=Path), help="Input file path"
)
@click.option("--dry-run", is_flag=True, help="Perform dry run without loading")
@click.pass_context
def load(ctx: click.Context, input_path: Path | None, *, dry_run: bool) -> None:
    """Load data to LDAP using target-ldap."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]

    success = orchestrator.run_target(input_path, dry_run=dry_run)

    if not success:
        sys.exit(1)


@cli.command()
@click.option("--catalog", type=click.Path(path_type=Path), help="Catalog file path")
@click.option("--state", type=click.Path(path_type=Path), help="State file path")
@click.option("--no-transform", is_flag=True, help="Skip transformation step")
@click.option("--dry-run", is_flag=True, help="Perform dry run")
@click.pass_context
def sync(
    ctx: click.Context,
    catalog: Path | None,
    state: Path | None,
    *,
    no_transform: bool,
    dry_run: bool,
) -> None:
    """Run complete sync pipeline (extract → transform → load)."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]

    success = orchestrator.run_sync(
        catalog_path=catalog,
        state_path=state,
        transform=not no_transform,
        dry_run=dry_run,
    )

    if not success:
        sys.exit(1)


@cli.group()
def migrate() -> None:
    """Generic LDAP migration commands."""


@migrate.command("analyze")
@click.option("--source-host", required=True, help="Source LDAP host")
@click.option("--target-host", required=True, help="Target LDAP host")
@click.option("--base-dn", required=True, help="Base DN")
@click.option("--source-port", default=389, help="Source LDAP port")
@click.option("--target-port", default=389, help="Target LDAP port")
@click.option("--estimated-entries", type=int, help="Estimated number of entries")
@click.option("--custom-schema", is_flag=True, help="Source has custom schema")
@click.option("--output", type=click.Path(path_type=Path), help="Save analysis to file")
@click.pass_context
def migrate_analyze(
    ctx: click.Context,
    source_host: str,
    target_host: str,
    base_dn: str,
    source_port: int,
    target_port: int,
    estimated_entries: int | None,
    custom_schema: bool,
    output: Path | None,
) -> None:
    """Analyze migration scenario and provide recommendations."""
    config: FlxLDAPConfig = ctx.obj["config"]

    orchestrator = GenericMigrationOrchestrator(config)

    # Prepare configurations
    source_config = {"host": source_host, "port": source_port, "base_dn": base_dn}

    target_config = {"host": target_host, "port": target_port, "base_dn": base_dn}

    migration_options = {
        "custom_schema": custom_schema,
        "estimated_entries": estimated_entries or 0,
    }

    # Perform analysis
    analysis = orchestrator.analyze_migration_scenario(
        source_config, target_config, migration_options
    )

    # Display results
    console.print("\n[bold]Migration Scenario Analysis:[/bold]\n")

    # Component status
    console.print("[bold]Component Status:[/bold]")
    components_table = Table(show_header=True, header_style="bold")
    components_table.add_column("Component")
    components_table.add_column("Available")
    components_table.add_column("Health")

    for comp_name, comp_info in analysis["components"].items():
        status = "✓" if comp_info["available"] else "✗"
        components_table.add_row(comp_name, status, comp_info["health_status"])

    console.print(components_table)

    # Requirements analysis
    requirements = analysis["requirements"]
    console.print("\n[bold]Migration Requirements:[/bold]")
    console.print(f"  Complexity: {requirements['complexity_assessment']}")
    console.print(f"  Recommended Pattern: {requirements['recommended_pattern']}")
    console.print(f"  Estimated Duration: {requirements['estimated_duration']}")

    if requirements["risk_factors"]:
        console.print("\n[bold yellow]Risk Factors:[/bold yellow]")
        for risk in requirements["risk_factors"]:
            console.print(f"  • {risk}")

    # Feasibility
    feasibility = analysis["feasibility"]
    feasibility_color = "green" if feasibility["overall"] == "feasible" else "red"
    console.print(
        f"\n[bold]Feasibility:[/bold] [{feasibility_color}]{feasibility['overall']}[/{feasibility_color}]"
    )
    console.print(f"  Confidence: {feasibility['confidence']}")

    if feasibility["blockers"]:
        console.print("\n[bold red]Blockers:[/bold red]")
        for blocker in feasibility["blockers"]:
            console.print(f"  • {blocker}")

    # Recommendations
    console.print("\n[bold]Recommendations:[/bold]")
    for rec in analysis["recommendations"]:
        console.print(f"  • {rec}")

    # Save to file if requested
    if output:
        import json

        with output.open("w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, default=str)
        console.print(f"\nAnalysis saved to: {output}")


@migrate.command("patterns")
@click.pass_context
def migrate_patterns(ctx: click.Context) -> None:
    """Show available migration patterns."""
    config: FlxLDAPConfig = ctx.obj["config"]

    orchestrator = GenericMigrationOrchestrator(config)
    patterns = orchestrator.get_supported_migration_patterns()

    console.print("\n[bold]Available Migration Patterns:[/bold]\n")

    for pattern_name, pattern_info in patterns.items():
        console.print(f"[bold]{pattern_name}[/bold]")
        console.print(f"  Description: {pattern_info['description']}")
        console.print(f"  Complexity: {pattern_info['complexity']}")
        console.print(f"  Phases: {', '.join(pattern_info['phases'])}")
        console.print(f"  Use Cases: {', '.join(pattern_info['use_cases'])}")
        console.print()


@migrate.command("components")
@click.pass_context
def migrate_components(ctx: click.Context) -> None:
    """Show component capabilities and responsibilities."""
    config: FlxLDAPConfig = ctx.obj["config"]

    orchestrator = GenericMigrationOrchestrator(config)
    capabilities = orchestrator.detect_component_capabilities()

    console.print("\n[bold]Component Capabilities:[/bold]\n")

    for comp_name, comp_info in capabilities.items():
        status_color = "green" if comp_info["available"] else "red"
        status_text = "Available" if comp_info["available"] else "Not Available"

        console.print(
            f"[bold]{comp_name}[/bold] - [{status_color}]{status_text}[/{status_color}]"
        )

        if comp_info["version"]:
            console.print(f"  Version: {comp_info['version']}")

        console.print(f"  Health: {comp_info['health_status']}")

        if comp_info["capabilities"]:
            console.print("  Capabilities:")
            for capability in comp_info["capabilities"]:
                console.print(f"    • {capability}")

        console.print()


@migrate.command("plan")
@click.option("--source-host", required=True, help="Source LDAP host")
@click.option("--target-host", required=True, help="Target LDAP host")
@click.option("--base-dn", required=True, help="Base DN")
@click.option("--output", type=click.Path(path_type=Path), help="Save plan to file")
@click.pass_context
def migrate_plan(
    ctx: click.Context,
    source_host: str,
    target_host: str,
    base_dn: str,
    output: Path | None,
) -> None:
    """Generate migration plan."""
    config: FlxLDAPConfig = ctx.obj["config"]

    orchestrator = GenericMigrationOrchestrator(config)

    # Create basic catalogs for planning

    # Generate comprehensive migration plan
    source_config = {"host": source_host, "base_dn": base_dn}
    target_config = {"host": target_host, "base_dn": base_dn}

    plan = orchestrator.generate_migration_plan(source_config, target_config)

    # Display plan
    console.print("\n[bold]Migration Plan:[/bold]\n")

    for i, phase in enumerate(plan["phases"], 1):
        console.print(f"[bold]Phase {i}: {phase['name']}[/bold]")
        console.print(f"  {phase['description']}")
        console.print("  Steps:")
        for step in phase["steps"]:
            console.print(f"    • {step}")
        console.print()

    if output:
        import json

        with output.open("w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        console.print(f"Plan saved to: {output}")


@migrate.command("run")
@click.option(
    "--source-catalog", type=click.Path(path_type=Path), help="Source catalog"
)
@click.option(
    "--target-catalog", type=click.Path(path_type=Path), help="Target catalog"
)
@click.option("--no-compare", is_flag=True, help="Skip comparison")
@click.pass_context
def migrate_run(
    ctx: click.Context,
    source_catalog: Path | None,
    target_catalog: Path | None,
    *,
    no_compare: bool,
) -> None:
    """Run LDAP migration."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]

    success = orchestrator.run_migration(
        source_catalog=source_catalog,
        target_catalog=target_catalog,
        compare_first=not no_compare,
    )

    if not success:
        sys.exit(1)


@cli.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration."""
    orchestrator: LDAPOrchestrator = ctx.obj["orchestrator"]
    config: FlxLDAPConfig = ctx.obj["config"]

    # Validate configuration
    if not orchestrator.validate_config():
        sys.exit(1)

    # Check component availability
    console.print("\n[bold]Component Status:[/bold]")

    components = [
        ("tap-ldap", "tap" in config.model_dump()),
        ("target-ldap", "target" in config.model_dump()),
        ("dbt-ldap", "dbt" in config.model_dump()),
    ]

    table = Table(show_header=True, header_style="bold")
    table.add_column("Component")
    table.add_column("Configured")
    table.add_column("Available")

    for component, configured in components:
        try:
            if component == "tap-ldap":
                import tap_ldap  # noqa: F401

                available = "✓"
            elif component == "target-ldap":
                import target_ldap  # noqa: F401

                available = "✓"
            elif component == "dbt-ldap":
                import dbt  # noqa: F401

                available = "✓"
        except ImportError:
            available = "✗"

        table.add_row(
            component,
            "✓" if configured else "✗",
            available,
        )

    console.print(table)

    # Check migration readiness
    orchestrator = GenericMigrationOrchestrator(config)
    _ready, issues = orchestrator.validate_migration_readiness()

    if issues:
        console.print("\n[bold yellow]Migration readiness issues:[/bold yellow]")
        for issue in issues:
            console.print(f"  • {issue}")
    else:
        console.print("\n[green]✓[/green] System ready for migration")


@cli.command()
@click.option(
    "--format", "output_format", type=click.Choice(["json", "yaml"]), default="yaml"
)
@click.pass_context
def show_config(ctx: click.Context, output_format: str) -> None:
    """Show current configuration."""
    config: FlxLDAPConfig = ctx.obj["config"]

    if output_format == "json":
        import json

        console.print(json.dumps(config.model_dump(exclude_none=True), indent=2))
    else:
        import yaml  # type: ignore[import-untyped]

        console.print(
            yaml.dump(config.model_dump(exclude_none=True), default_flow_style=False)
        )


if __name__ == "__main__":
    cli()

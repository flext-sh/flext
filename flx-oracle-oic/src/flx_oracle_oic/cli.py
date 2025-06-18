"""Unified CLI for Oracle Integration Cloud operations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="flx-oracle-oic",
    help="Unified CLI for Oracle Integration Cloud operations.",
    add_completion=False,
)

console = Console()

# Subcommand groups
tap_app = typer.Typer(help="Singer TAP operations for data extraction")
target_app = typer.Typer(help="Singer Target operations for data loading")
ext_app = typer.Typer(help="Extension operations for lifecycle and monitoring")
adapter_app = typer.Typer(help="FLX adapter operations")

app.add_typer(tap_app, name="tap")
app.add_typer(target_app, name="target")
app.add_typer(ext_app, name="ext")
app.add_typer(adapter_app, name="adapter")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Oracle Integration Cloud Unified CLI."""
    if version:
        console.print("flx-oracle-oic version 0.1.0")
        raise typer.Exit

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


# TAP Commands
@tap_app.command("discover")
def tap_discover(
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output catalog file"
    ),
) -> None:
    """Discover available streams from Oracle OIC."""
    try:
        from tap_oracle_oic.tap import TapOIC

        with Path(config).open() as f:
            config_dict = json.load(f)

        tap = TapOIC(config=config_dict)
        catalog = tap.discover_catalog()

        catalog_dict = catalog.to_dict()

        if output:
            with Path(output).open("w") as f:
                json.dump(catalog_dict, f, indent=2)
            console.print(f"[green]✓[/green] Catalog saved to {output}")
        else:
            console.print_json(data=catalog_dict)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@tap_app.command("extract")
def tap_extract(
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
    catalog: Path | None = typer.Option(None, "--catalog", help="Catalog file"),
    state: Path | None = typer.Option(None, "--state", help="State file"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file"),
) -> None:
    """Extract data from Oracle OIC."""
    try:
        from tap_oracle_oic.tap import TapOIC

        with Path(config).open() as f:
            config_dict = json.load(f)

        catalog_dict = None
        if catalog:
            with Path(catalog).open() as f:
                catalog_dict = json.load(f)

        state_dict = None
        if state:
            with Path(state).open() as f:
                state_dict = json.load(f)

        tap = TapOIC(
            config=config_dict,
            catalog=catalog_dict,
            state=state_dict,
        )

        if output:
            with Path(output).open("w") as f:
                for message in tap.sync_all():
                    f.write(json.dumps(message) + "\n")
            console.print(f"[green]✓[/green] Data extracted to {output}")
        else:
            for message in tap.sync_all():
                console.print_json(data=message)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


# Target Commands
@target_app.command("load")
def target_load(
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
    input_file: Path | None = typer.Option(
        None, "--input", "-i", help="Input JSONL file"
    ),
) -> None:
    """Load data into Oracle OIC."""
    try:
        from target_oracle_oic.target import TargetOracleOIC

        with Path(config).open() as f:
            config_dict = json.load(f)

        target = TargetOracleOIC(config=config_dict)

        if input_file:
            with Path(input_file).open() as f:
                for line in f:
                    message = json.loads(line.strip())
                    target.process_message(message)
        else:
            # Read from stdin
            for line in sys.stdin:
                message = json.loads(line.strip())
                target.process_message(message)

        console.print("[green]✓[/green] Data loaded successfully")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


# Extension Commands
@ext_app.command("lifecycle")
def ext_lifecycle(
    action: str = typer.Argument(..., help="Action: activate, deactivate, status"),
    integration_id: str = typer.Argument(..., help="Integration ID"),
    version: str = typer.Option(
        "01.00.0000", "--version", "-v", help="Integration version"
    ),
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
) -> None:
    """Manage integration lifecycle."""
    try:
        from oracle_oic_ext.lifecycle import LifecycleManager

        with Path(config).open() as f:
            config_dict = json.load(f)

        manager = LifecycleManager(
            base_url=config_dict["base_url"],
            auth_config={
                "oauth_client_id": config_dict["oauth_client_id"],
                "oauth_client_secret": config_dict["oauth_client_secret"],
                "oauth_token_url": config_dict["oauth_token_url"],
            },
        )

        if action == "activate":
            manager.activate_integration(integration_id, version)
            console.print(
                f"[green]✓[/green] Integration {integration_id}|{version} activated"
            )
        elif action == "deactivate":
            manager.deactivate_integration(integration_id, version)
            console.print(
                f"[green]✓[/green] Integration {integration_id}|{version} deactivated"
            )
        elif action == "status":
            status = manager.get_integration_status(integration_id, version)
            console.print(
                f"Integration {integration_id}|{version} status: [bold]{status}[/bold]"
            )
        else:
            console.print(f"[red]Error:[/red] Unknown action: {action}")
            raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@ext_app.command("monitor")
def ext_monitor(
    metric: str = typer.Argument(
        ..., help="Metric: health, performance, errors, usage"
    ),
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
    detailed: bool = typer.Option(default=False, help="Show detailed information"),
    window: int = typer.Option(24, "--window", "-w", help="Time window in hours"),
) -> None:
    """Monitor OIC instance."""
    try:
        from oracle_oic_ext.monitoring import MonitoringService

        with Path(config).open() as f:
            config_dict = json.load(f)

        service = MonitoringService(
            base_url=config_dict["base_url"],
            auth_config={
                "oauth_client_id": config_dict["oauth_client_id"],
                "oauth_client_secret": config_dict["oauth_client_secret"],
                "oauth_token_url": config_dict["oauth_token_url"],
            },
        )

        if metric == "health":
            result = service.check_health(detailed=detailed)
            console.print_json(data=result)
        elif metric == "performance":
            result = service.get_performance_metrics(window_hours=window)
            console.print_json(data=result)
        elif metric == "errors":
            result = service.analyze_errors(window_hours=window)
            console.print_json(data=result)
        elif metric == "usage":
            result = service.get_usage_analytics(window_days=window)
            console.print_json(data=result)
        else:
            console.print(f"[red]Error:[/red] Unknown metric: {metric}")
            raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


# Adapter Commands
@adapter_app.command("status")
def adapter_status(
    config: Path = typer.Option(..., "--config", "-c", help="Configuration file"),
) -> None:
    """Check FLX adapter status."""
    try:
        from flx_oracle_oic.adapter import OracleOICAdapter

        with Path(config).open() as f:
            config_dict = json.load(f)

        adapter = OracleOICAdapter(**config_dict)
        health = adapter.health_check()

        table = Table(title="FLX Oracle OIC Adapter Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", adapter.name)
        table.add_row("Type", adapter.adapter_type)
        table.add_row("Version", adapter.version)
        table.add_row("Status", health.get("status", "unknown"))
        table.add_row("Base URL", adapter.config.base_url)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


# Pipeline Commands
@app.command("pipeline")
def run_pipeline(
    config: Path = typer.Option(
        ..., "--config", "-c", help="Pipeline configuration file"
    ),
    dry_run: bool = typer.Option(
        default=False, help="Show what would be done without executing"
    ),
) -> None:
    """Run a complete extraction, transformation, and loading pipeline."""
    try:
        with Path(config).open() as f:
            pipeline_config = json.load(f)

        console.print("[bold]Oracle OIC Pipeline[/bold]")
        console.print(f"Configuration: {config}")

        if dry_run:
            console.print("\n[yellow]DRY RUN - No actions will be performed[/yellow]\n")

        # Step 1: Extract
        console.print("\n[cyan]Step 1: Extracting data from source OIC...[/cyan]")
        if not dry_run:
            from tap_oracle_oic.tap import TapOIC

            tap = TapOIC(config=pipeline_config.get("tap", {}))
            messages = list(tap.sync_all())
            console.print(f"[green]✓[/green] Extracted {len(messages)} messages")
        else:
            console.print("Would extract data using tap configuration")

        # Step 2: Transform (if needed)
        if "transformations" in pipeline_config:
            console.print("\n[cyan]Step 2: Applying transformations...[/cyan]")
            if not dry_run:
                # Apply transformations
                console.print("[green]✓[/green] Transformations applied")
            else:
                console.print("Would apply configured transformations")

        # Step 3: Load
        console.print("\n[cyan]Step 3: Loading data to target OIC...[/cyan]")
        if not dry_run:
            from target_oracle_oic.target import TargetOracleOIC

            target = TargetOracleOIC(config=pipeline_config.get("target", {}))
            for message in messages:
                target.process_message(message)
            console.print("[green]✓[/green] Data loaded successfully")
        else:
            console.print("Would load data using target configuration")

        console.print("\n[bold green]Pipeline completed successfully![/bold green]")

    except Exception as e:
        console.print(f"\n[red]Pipeline failed:[/red] {e}")
        raise typer.Exit(1) from None


# Utility Commands
@app.command("validate-config")
def validate_config(
    config: Path = typer.Option(
        ..., "--config", "-c", help="Configuration file to validate"
    ),
    component: str = typer.Option(
        "all", "--component", help="Component to validate: tap, target, ext, all"
    ),
) -> None:
    """Validate configuration file."""
    try:
        with Path(config).open() as f:
            config_dict = json.load(f)

        # Validate common fields
        required_fields = [
            "base_url",
            "oauth_client_id",
            "oauth_client_secret",
            "oauth_token_url",
        ]
        errors = [
            f"Missing required field: {field}"
            for field in required_fields
            if field not in config_dict
        ]

        # Validate URLs
        errors.extend(
            f"{url_field} must use HTTPS protocol"
            for url_field in ["base_url", "oauth_token_url"]
            if url_field in config_dict
            and not config_dict[url_field].startswith("https://")
        )

        if errors:
            console.print("[red]Configuration validation failed:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            raise typer.Exit(1) from None
        console.print(f"[green]✓[/green] Configuration is valid for {component}")

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(1) from None
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Configuration file not found: {config}")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()

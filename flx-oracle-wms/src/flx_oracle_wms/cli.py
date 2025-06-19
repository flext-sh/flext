"""Unified CLI for Oracle WMS integration."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from flx_oracle_wms.config import PipelineConfig
from flx_oracle_wms.monitoring import PipelineMonitor
from flx_oracle_wms.orchestrator import WMSOrchestrator


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="flx-oracle-wms")
def cli() -> None:
    """FLX Oracle WMS - Unified integration for Oracle Warehouse Management System.

    This CLI orchestrates tap-oracle-wms and target-oracle-wms to provide
    complete ETL pipelines with monitoring and advanced features.
    """


@cli.command()
@click.option(
    "--tap-config",
    type=click.Path(exists=True),
    required=True,
    help="Path to tap configuration file",
)
@click.option(
    "--target-config",
    type=click.Path(exists=True),
    required=True,
    help="Path to target configuration file",
)
@click.option(
    "--state",
    type=click.Path(),
    help="Path to state file for incremental replication",
)
@click.option(
    "--catalog",
    type=click.Path(exists=True),
    help="Path to catalog file for stream selection",
)
def extract(
    tap_config: str,
    target_config: str,  # noqa: ARG001
    state: str | None,
    catalog: str | None,
) -> None:
    """Run extraction from Oracle WMS (tap only)."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting data from Oracle WMS...", total=None)

        try:
            import subprocess

            cmd = ["tap-oracle-wms", "--config", tap_config]

            if state:
                cmd.extend(["--state", state])
            if catalog:
                cmd.extend(["--catalog", catalog])

            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            progress.update(task, completed=True)
            console.print("✅ Extraction completed successfully!", style="green")

            # Output the data

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Extraction failed: {e.stderr}", style="red")
            sys.exit(1)


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Path to target configuration file",
)
@click.argument("input_file", type=click.File("r"), default=sys.stdin)
def load(config: str, input_file: Any) -> None:  # noqa: ANN401
    """Load data to Oracle WMS (target only)."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading data to target...", total=None)

        try:
            import subprocess

            result = subprocess.run(
                ["target-oracle-wms", "--config", config],  # noqa: S607
                input=input_file.read(),
                capture_output=True,
                text=True,
                check=True,
            )

            progress.update(task, completed=True)
            console.print("✅ Loading completed successfully!", style="green")

            if result.stdout:
                pass

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Loading failed: {e.stderr}", style="red")
            sys.exit(1)


@cli.group()
def pipeline() -> None:
    """Manage and run ETL pipelines."""


@pipeline.command("run")
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Path to pipeline configuration file",
)
@click.option(
    "--pipeline-name",
    help="Name of specific pipeline to run",
)
@click.option(
    "--async",
    "run_async",
    is_flag=True,
    help="Run pipeline asynchronously",
)
def run_pipeline(config: str, pipeline_name: str | None, *, run_async: bool) -> None:
    """Run a complete ETL pipeline."""
    try:
        # Load pipeline configuration
        config_data = json.loads(Path(config).read_text())
        pipeline_config = PipelineConfig(**config_data)

        # Create orchestrator
        orchestrator = WMSOrchestrator(pipeline_config)

        # Run pipeline
        with console.status(f"Running pipeline: {pipeline_name or 'default'}..."):
            if run_async:
                import asyncio

                result = asyncio.run(orchestrator.run_pipeline_async(pipeline_name))
            else:
                result = orchestrator.run_pipeline(pipeline_name)

        # Display results
        if result["status"] == "success":
            console.print("✅ Pipeline completed successfully!", style="green")
            _display_pipeline_results(result)
        else:
            console.print(f"❌ Pipeline failed: {result.get('error')}", style="red")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error running pipeline: {e}", style="red")
        sys.exit(1)


@pipeline.command("list")
@click.option(
    "--config",
    type=click.Path(exists=True),
    required=True,
    help="Path to pipeline configuration file",
)
def list_pipelines(config: str) -> None:
    """List available pipelines."""
    try:
        config_data = json.loads(Path(config).read_text())
        pipeline_config = PipelineConfig(**config_data)

        table = Table(title="Available Pipelines")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Schedule")
        table.add_column("Enabled", justify="center")

        for pipeline in pipeline_config.pipelines:
            table.add_row(
                pipeline.name,
                pipeline.description,
                pipeline.schedule or "Manual",
                "✅" if pipeline.enabled else "❌",
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error listing pipelines: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--tap-config",
    type=click.Path(exists=True),
    required=True,
    help="Path to tap configuration file",
)
def discover(tap_config: str) -> None:
    """Discover available streams from Oracle WMS."""
    with console.status("Discovering streams..."):
        try:
            import subprocess

            result = subprocess.run(
                ["tap-oracle-wms", "--config", tap_config, "--discover"],  # noqa: S607
                capture_output=True,
                text=True,
                check=True,
            )

            catalog = json.loads(result.stdout)

            # Display discovered streams
            table = Table(title="Discovered Streams")
            table.add_column("Stream", style="cyan")
            table.add_column("Tap Stream ID")
            table.add_column("Replication Method")
            table.add_column("Key Properties")

            for stream in catalog.get("streams", []):
                metadata = stream.get("metadata", [{}])[0].get("metadata", {})
                table.add_row(
                    stream.get("stream", ""),
                    stream.get("tap_stream_id", ""),
                    metadata.get("replication-method", "FULL_TABLE"),
                    ", ".join(metadata.get("table-key-properties", [])),
                )

            console.print(table)

            # Save catalog
            catalog_path = Path("catalog.json")
            catalog_path.write_text(json.dumps(catalog, indent=2))
            console.print(f"\n💾 Catalog saved to: {catalog_path}", style="green")

        except subprocess.CalledProcessError as e:
            console.print(f"❌ Discovery failed: {e.stderr}", style="red")
            sys.exit(1)
        except json.JSONDecodeError:
            console.print("❌ Failed to parse discovery output", style="red")
            sys.exit(1)


@cli.group()
def monitor() -> None:
    """Monitor pipeline executions."""


@monitor.command("status")
@click.option(
    "--pipeline-name",
    help="Name of specific pipeline to monitor",
)
def monitor_status(pipeline_name: str | None) -> None:
    """Show current pipeline status."""
    monitor = PipelineMonitor()

    if pipeline_name:
        status = monitor.get_pipeline_status(pipeline_name)
        _display_pipeline_status(pipeline_name, status)
    else:
        # Show all pipeline statuses
        statuses = monitor.get_all_pipeline_statuses()
        for name, status in statuses.items():
            _display_pipeline_status(name, status)


@monitor.command("metrics")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "prometheus"]),
    default="table",
    help="Output format for metrics",
)
def monitor_metrics(output_format: str) -> None:
    """Show pipeline metrics."""
    monitor = PipelineMonitor()
    metrics = monitor.get_metrics()

    if output_format == "table":
        _display_metrics_table(metrics)
    elif output_format == "json" or output_format == "prometheus":
        pass


@cli.command()
@click.option(
    "--tap-config",
    type=click.Path(),
    help="Generate tap configuration template",
)
@click.option(
    "--target-config",
    type=click.Path(),
    help="Generate target configuration template",
)
@click.option(
    "--pipeline-config",
    type=click.Path(),
    help="Generate pipeline configuration template",
)
def init(
    tap_config: str | None,
    target_config: str | None,
    pipeline_config: str | None,
) -> None:
    """Initialize configuration templates."""
    if tap_config:
        _create_tap_config_template(tap_config)
        console.print(f"✅ Created tap config template: {tap_config}", style="green")

    if target_config:
        _create_target_config_template(target_config)
        console.print(
            f"✅ Created target config template: {target_config}",
            style="green",
        )

    if pipeline_config:
        _create_pipeline_config_template(pipeline_config)
        console.print(
            f"✅ Created pipeline config template: {pipeline_config}",
            style="green",
        )

    if not any([tap_config, target_config, pipeline_config]):
        console.print(
            "❌ Please specify at least one config type to generate",
            style="red",
        )
        sys.exit(1)


def _display_pipeline_results(result: dict[str, Any]) -> None:
    """Display pipeline execution results."""
    table = Table(title="Pipeline Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Records Extracted", str(result.get("records_extracted", 0)))
    table.add_row("Records Loaded", str(result.get("records_loaded", 0)))
    table.add_row("Errors", str(result.get("errors", 0)))
    table.add_row("Duration", f"{result.get('duration_seconds', 0):.2f}s")

    console.print(table)


def _display_pipeline_status(name: str, status: dict[str, Any]) -> None:
    """Display status for a single pipeline."""
    console.print(f"\n[bold cyan]{name}[/bold cyan]")
    console.print(f"Status: {status.get('status', 'unknown')}")
    console.print(f"Last Run: {status.get('last_run', 'never')}")
    console.print(f"Next Run: {status.get('next_run', 'not scheduled')}")


def _display_metrics_table(metrics: dict[str, Any]) -> None:
    """Display metrics in table format."""
    table = Table(title="Pipeline Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    for key, value in metrics.items():
        if isinstance(value, int | float):
            table.add_row(key.replace("_", " ").title(), f"{value:,.2f}")
        else:
            table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


def _create_tap_config_template(path: str) -> None:
    """Create tap configuration template."""
    template = {
        "base_url": "https://your-instance.oracle.com/wms/api/v1",
        "username": "your_username",
        "password": "your_password",
        "timeout": 300,
        "page_size": 1000,
        "start_date": "2024-01-01T00:00:00Z",
    }
    Path(path).write_text(json.dumps(template, indent=2))


def _create_target_config_template(path: str) -> None:
    """Create target configuration template."""
    template = {
        "base_url": "https://your-instance.oracle.com/wms/api/v1",
        "username": "your_username",
        "password": "your_password",
        "enable_kpi_calculation": True,
        "enable_alerts": True,
        "expiry_alert_days": 30,
        "output_path": "./output",
        "output_format": "json",
    }
    Path(path).write_text(json.dumps(template, indent=2))


def _create_pipeline_config_template(path: str) -> None:
    """Create pipeline configuration template."""
    template = {
        "name": "Oracle WMS Integration",
        "tap_config_path": "./config/tap_config.json",
        "target_config_path": "./config/target_config.json",
        "state_path": "./state.json",
        "catalog_path": "./catalog.json",
        "pipelines": [
            {
                "name": "inventory_sync",
                "description": "Sync inventory data with KPI calculation",
                "streams": ["inventory", "lots", "locations"],
                "schedule": "0 */6 * * *",
                "enabled": True,
            },
            {
                "name": "order_processing",
                "description": "Process orders and generate alerts",
                "streams": ["orders", "order_lines", "shipments"],
                "schedule": "0 * * * *",
                "enabled": True,
            },
        ],
        "monitoring": {
            "enabled": True,
            "metrics_port": 9090,
            "health_check_interval": 60,
        },
    }
    Path(path).write_text(json.dumps(template, indent=2))


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple CLI test using Click.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="flx-test")
def cli():
    """FLX Test CLI - Simple demonstration."""
    pass


@cli.command()
def status():
    """Show system status."""
    console.print("[bold green]FLX System Status[/bold green]")
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Message", style="dim")

    table.add_row("Core", "[green]✓ Running[/green]", "Daemon is active")
    table.add_row("API", "[green]✓ Ready[/green]", "FastAPI on port 8000")
    table.add_row("Web", "[green]✓ Ready[/green]", "Django on port 8080")
    table.add_row(
        "Database", "[yellow]⚠ Not connected[/yellow]", "PostgreSQL not running"
    )

    console.print(table)


@cli.command()
@click.argument("name")
@click.option("--type", default="extract_load", help="Pipeline type")
def create(name, type):
    """Create a new pipeline."""
    console.print(f"[bold blue]Creating pipeline:[/bold blue] {name}")
    console.print(f"Type: {type}")
    console.print("[green]✓ Pipeline created successfully![/green]")


@cli.command()
def list():
    """List all pipelines."""
    console.print("[bold]Available Pipelines:[/bold]")
    console.print()

    pipelines = [
        {"name": "sales_etl", "type": "extract_load", "status": "active"},
        {"name": "customer_sync", "type": "extract_load", "status": "inactive"},
        {"name": "data_transform", "type": "transform", "status": "active"},
    ]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Type")
    table.add_column("Status")

    for p in pipelines:
        status_color = "green" if p["status"] == "active" else "red"
        table.add_row(
            p["name"], p["type"], f"[{status_color}]{p['status']}[/{status_color}]"
        )

    console.print(table)


if __name__ == "__main__":
    cli()

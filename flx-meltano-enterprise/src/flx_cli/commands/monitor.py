"""
Monitoring commands.
"""

import asyncio
import time

import click
from flx_cli.utils import handle_errors
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


@click.group()
@click.pass_context
def monitor(ctx):
    """Monitor system status."""
    pass


@monitor.command()
@click.pass_context
@handle_errors
async def dashboard(ctx):
    """Open monitoring dashboard."""
    console = ctx.obj["console"]

    # Open web browser
    import webbrowser

    webbrowser.open("http://localhost:8080")

    console.print("[green]✓[/green] Opening dashboard in browser...")


@monitor.command()
@click.option("--interval", "-i", default=2, help="Update interval in seconds")
@click.pass_context
@handle_errors
async def live(ctx, interval):
    """Live system monitoring."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    layout["body"].split_row(
        Layout(name="stats"),
        Layout(name="health"),
    )

    with Live(layout, refresh_per_second=1, console=console):
        try:
            while True:
                # Get system stats
                stats = await client.get_system_stats()
                health = await client.health_check()

                # Update header
                layout["header"].update(
                    Panel(
                        f"[bold]FLX System Monitor[/bold] - Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                        style="bold blue",
                    )
                )

                # Update stats
                stats_table = Table(show_header=False, box=None)
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="green")

                stats_table.add_row("Active Pipelines", str(stats.active_pipelines))
                stats_table.add_row("Total Executions", str(stats.total_executions))
                stats_table.add_row("Success Rate", f"{stats.success_rate:.1f}%")
                stats_table.add_row("CPU Usage", f"{stats.cpu_usage:.1f}%")
                stats_table.add_row("Memory Usage", f"{stats.memory_usage:.1f}%")
                stats_table.add_row("Uptime", f"{stats.uptime_seconds // 3600}h")

                layout["stats"].update(
                    Panel(stats_table, title="System Stats", border_style="green")
                )

                # Update health
                health_table = Table(show_header=False, box=None)
                health_table.add_column("Component", style="cyan")
                health_table.add_column("Status", style="green")

                for name, component in health.components.items():
                    status = (
                        "[green]✓ Healthy[/green]"
                        if component.healthy
                        else "[red]✗ Unhealthy[/red]"
                    )
                    health_table.add_row(name.title(), status)

                layout["health"].update(
                    Panel(health_table, title="Health Status", border_style="green")
                )

                # Update footer
                layout["footer"].update(
                    Panel(
                        "[dim]Press Ctrl+C to exit[/dim]",
                        style="dim",
                    )
                )

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            pass


@monitor.command()
@click.pass_context
@handle_errors
async def stats(ctx):
    """Show system statistics."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Getting system stats..."):
        stats = await client.get_system_stats()

    console.print("\n[bold]System Statistics[/bold]")
    console.print(f"Active Pipelines: {stats.active_pipelines}")
    console.print(f"Total Executions: {stats.total_executions}")
    console.print(f"Success Rate: {stats.success_rate:.1f}%")
    console.print(f"CPU Usage: {stats.cpu_usage:.1f}%")
    console.print(f"Memory Usage: {stats.memory_usage:.1f}%")
    console.print(f"Uptime: {stats.uptime_seconds // 3600} hours")
    console.print(f"Active Connections: {stats.active_connections}")

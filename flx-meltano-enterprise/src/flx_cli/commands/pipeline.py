"""
Pipeline management commands.
"""

import json

import click
from flx_cli.utils import format_datetime, handle_errors
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


@click.group()
@click.pass_context
def pipeline(ctx):
    """Manage data pipelines."""
    pass


@pipeline.command()
@click.option("--limit", "-l", default=100, help="Maximum number of pipelines to show")
@click.option("--filter", "-f", help="Filter pipelines by name")
@click.pass_context
@handle_errors
async def list(ctx, limit, filter):
    """List all pipelines."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Loading pipelines..."):
        pipelines = await client.list_pipelines(limit=limit, filter=filter)

    if not pipelines:
        console.print("[yellow]No pipelines found[/yellow]")
        return

    table = Table(title="Pipelines")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Extractor", style="green")
    table.add_column("Loader", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Last Run")
    table.add_column("Active")

    for p in pipelines:
        status_color = {
            "STATUS_SUCCESS": "green",
            "STATUS_FAILED": "red",
            "STATUS_RUNNING": "yellow",
        }.get(p.last_status.name if p.last_status else "", "dim")

        table.add_row(
            p.id[:8],
            p.name,
            p.extractor,
            p.loader,
            f"[{status_color}]{p.last_status.name if p.last_status else 'Never run'}[/{status_color}]",
            (
                format_datetime(p.last_run.ToDatetime())
                if p.HasField("last_run")
                else "Never"
            ),
            "[green]✓[/green]" if p.is_active else "[red]✗[/red]",
        )

    console.print(table)


@pipeline.command()
@click.argument("pipeline_id")
@click.pass_context
@handle_errors
async def get(ctx, pipeline_id):
    """Get pipeline details."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Loading pipeline..."):
        pipeline = await client.get_pipeline(pipeline_id)

    console.print(f"\n[bold]Pipeline: {pipeline.name}[/bold]")
    console.print(f"ID: {pipeline.id}")
    console.print(f"Description: {pipeline.description or '[dim]No description[/dim]'}")
    console.print("\n[bold]Components:[/bold]")
    console.print(f"  Extractor: {pipeline.extractor}")
    console.print(f"  Loader: {pipeline.loader}")
    if pipeline.transform:
        console.print(f"  Transform: {pipeline.transform}")

    console.print("\n[bold]Configuration:[/bold]")
    if pipeline.schedule:
        console.print(f"  Schedule: {pipeline.schedule}")
    console.print(
        f"  Active: {'[green]Yes[/green]' if pipeline.is_active else '[red]No[/red]'}"
    )

    console.print("\n[bold]Metadata:[/bold]")
    console.print(f"  Created: {format_datetime(pipeline.created_at.ToDatetime())}")
    console.print(f"  Updated: {format_datetime(pipeline.updated_at.ToDatetime())}")
    console.print(f"  Created by: {pipeline.created_by}")

    if pipeline.HasField("config") and pipeline.config:
        console.print("\n[bold]Custom Configuration:[/bold]")
        console.print(json.dumps(dict(pipeline.config), indent=2))


@pipeline.command()
@click.argument("name")
@click.option("--extractor", "-e", required=True, help="Extractor plugin")
@click.option("--loader", "-l", required=True, help="Loader plugin")
@click.option("--transform", "-t", help="Transform plugin (optional)")
@click.option("--description", "-d", help="Pipeline description")
@click.option("--schedule", "-s", help="Cron schedule expression")
@click.option("--config", "-c", help="JSON configuration")
@click.pass_context
@handle_errors
async def create(
    ctx, name, extractor, loader, transform, description, schedule, config
):
    """Create a new pipeline."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    # Parse config if provided
    config_dict = None
    if config:
        try:
            config_dict = json.loads(config)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON configuration[/red]")
            ctx.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Creating pipeline...", total=None)

        pipeline = await client.create_pipeline(
            name=name,
            extractor=extractor,
            loader=loader,
            transform=transform,
            description=description,
            schedule=schedule,
            config=config_dict,
        )

        progress.update(task, completed=True)

    console.print(f"[green]✓[/green] Pipeline '{name}' created successfully!")
    console.print(f"ID: {pipeline.id}")


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--name", help="New name")
@click.option("--description", help="New description")
@click.option("--extractor", help="New extractor")
@click.option("--loader", help="New loader")
@click.option("--transform", help="New transform")
@click.option("--schedule", help="New schedule")
@click.option("--active/--inactive", default=None, help="Set active status")
@click.pass_context
@handle_errors
async def update(ctx, pipeline_id, **kwargs):
    """Update a pipeline."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    # Filter out None values
    updates = {k: v for k, v in kwargs.items() if v is not None}

    if not updates:
        console.print("[yellow]No updates specified[/yellow]")
        return

    # Handle active/inactive flag
    if "active" in updates:
        updates["is_active"] = updates.pop("active")

    with console.status("[bold green]Updating pipeline..."):
        await client.update_pipeline(pipeline_id, **updates)

    console.print("[green]✓[/green] Pipeline updated successfully!")


@pipeline.command()
@click.argument("pipeline_id")
@click.confirmation_option(prompt="Are you sure you want to delete this pipeline?")
@click.pass_context
@handle_errors
async def delete(ctx, pipeline_id):
    """Delete a pipeline."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Deleting pipeline..."):
        await client.delete_pipeline(pipeline_id)

    console.print("[green]✓[/green] Pipeline deleted successfully!")


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--full-refresh", is_flag=True, help="Ignore state and reload all data")
@click.option("--watch", "-w", is_flag=True, help="Watch execution progress")
@click.pass_context
@handle_errors
async def run(ctx, pipeline_id, full_refresh, watch):
    """Run a pipeline."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    # Start execution
    with console.status("[bold green]Starting pipeline..."):
        execution = await client.run_pipeline(pipeline_id, full_refresh=full_refresh)

    console.print("[green]✓[/green] Pipeline started!")
    console.print(f"Execution ID: {execution.id}")

    if watch:
        console.print("\n[bold]Watching execution...[/bold]")

        try:
            async for update in client.stream_execution(execution.id):
                if update.type == "pipeline.output":
                    # Parse message to get log line
                    try:
                        data = json.loads(update.message)
                        console.print(
                            f"[dim]{update.timestamp.ToDatetime():%H:%M:%S}[/dim] {data.get('line', '')}"
                        )
                    except:
                        console.print(
                            f"[dim]{update.timestamp.ToDatetime():%H:%M:%S}[/dim] {update.message}"
                        )

                elif update.type == "pipeline.execution.completed":
                    data = json.loads(update.message)
                    if data.get("status") == "success":
                        console.print(
                            "\n[green]✓[/green] Pipeline completed successfully!"
                        )
                    else:
                        console.print("\n[red]✗[/red] Pipeline failed!")
                    break

        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Stopped watching (pipeline is still running)[/yellow]"
            )


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--limit", "-l", default=10, help="Number of executions to show")
@click.pass_context
@handle_errors
async def executions(ctx, pipeline_id, limit):
    """List pipeline executions."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Loading executions..."):
        executions = await client.list_executions(pipeline_id=pipeline_id, limit=limit)

    if not executions:
        console.print("[yellow]No executions found[/yellow]")
        return

    table = Table(title="Recent Executions")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="green")
    table.add_column("Duration", style="blue")
    table.add_column("Records", style="magenta")

    for e in executions:
        status_color = {
            "STATUS_SUCCESS": "green",
            "STATUS_FAILED": "red",
            "STATUS_RUNNING": "yellow",
            "STATUS_CANCELLED": "dim",
        }.get(e.status.name, "dim")

        duration = f"{e.duration_seconds}s" if e.duration_seconds else "Running..."

        table.add_row(
            e.id[:8],
            f"[{status_color}]{e.status.name}[/{status_color}]",
            format_datetime(e.started_at.ToDatetime()),
            duration,
            str(e.records_processed) if e.records_processed else "-",
        )

    console.print(table)

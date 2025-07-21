"""CLI for FLEXT DBT Oracle WMS package."""

from __future__ import annotations

import click


@click.command()
@click.version_option()
def main() -> None:
    """FLEXT DBT Oracle WMS CLI."""
    click.echo("FLEXT DBT Oracle WMS - Oracle WMS data transformation with DBT")
    click.echo("Run 'dbt' commands in this directory to execute transformations.")


if __name__ == "__main__":
    main()

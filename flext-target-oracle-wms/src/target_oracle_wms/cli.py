"""CLI entry point for FLEXT Target Oracle WMS."""


import click

from target_oracle_wms.target import TargetOracleWMS


@click.command()
@click.option(
    "--config",
    "-c",
    help="Configuration file path or JSON string",
    type=str,
)
@click.option(
    "--format",
    "output_format",
    help="Output format (default: singer)",
    type=click.Choice(["singer", "json"], case_sensitive=False),
    default="singer",
)
@click.version_option(version="0.7.0", prog_name="target-oracle-wms")
def main(
    config: str | None = None,
    output_format: str = "singer",
) -> None:
    """FLEXT Target Oracle WMS - Singer target for Oracle WMS data loading.

    This target reads Singer-formatted data from stdin and loads it into Oracle WMS.

    Examples:
        target-oracle-wms --config config.json
        cat data.jsonl | target-oracle-wms --config config.json

    """
    target = TargetOracleWMS(
        config=config,
        parse_env_config=True,
    )

    target.listen()


if __name__ == "__main__":
    main()

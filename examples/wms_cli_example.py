#!/usr/bin/env python3
"""WMS CLI Example using the updated implementation.

This script demonstrates how to use the WMS CLI with direct API integration.
"""

import asyncio
import logging
import os
import sys

# Add the flx_project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dc_oracle_wms.wms.cli.client import WmsCLI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("wms_cli_example")

# Load environment variables
load_dotenv(dotenv_path=".internal.invalid")


async def run_wms_command(cli: WmsCLI, command: str, args: dict) -> dict:
    """Run a WMS command using the CLI.

    Args:
        cli: WMS CLI instance
        command: Command name
        args: Command arguments

    Returns:
        Command result
    """
    logger.info(f"Executing WMS command: {command}")
    try:
        result = await cli.run_command(command, args)
        logger.info(f"Command result: {result.get('success', False)}")
        return result
    except Exception as e:
        logger.exception(f"Error executing command: {e}")
        return {"success": False, "error": str(e)}


async def main_async() -> None:
    """Async main function to run WMS CLI commands."""
    logger.info("Initializing WMS CLI with configuration from environment")

    # Create WMS CLI with configuration from environment variables
    cli = WmsCLI()
    logger.info(f"WMS CLI initialized with URL: {cli.config.url}")

    # Run test-connection command
    await run_wms_command(cli, "test-connection", {})

    # Run status command
    await run_wms_command(cli, "status", {"detailed": True})

    # Run data command for items
    await run_wms_command(
        cli,
        "data",
        {
            "operation": "list",
            "entity": "item",
            "limit": 5,
            "output_format": "table",
        },
    )

    # Run data command for locations
    await run_wms_command(
        cli,
        "data",
        {
            "operation": "list",
            "entity": "location",
            "limit": 5,
            "output_format": "table",
        },
    )

    # Run help command
    await run_wms_command(cli, "help", {})

    logger.info("All commands executed")


def main() -> int:
    """Main entry point."""
    try:
        asyncio.run(main_async())
        return 0
    except KeyboardInterrupt:
        return 1
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Entry point for Oracle Integration Cloud Singer Tap.

This module provides the main command-line interface for the tap-oic Singer tap.
It can be executed as a module using: python -m tap_oic

Architecture: Improved CLI with 100% Singer SDK compatibility and organized subcommands
- Default: Standard Singer TAP protocol (--discover, --catalog, etc.)
- Extended: Well-organized subcommands (extract, lifecycle, monitor, admin)
"""

from __future__ import annotations


def main() -> None:
    """Main entry point for tap-oracle-oic."""
    from tap_oracle_oic.tap import TapOIC

    TapOIC.cli()


if __name__ == "__main__":
    main()

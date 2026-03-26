"""Documentation CLI entry point.

This module provides the entry point for the flext-docs command.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli


def main() -> None:
    """Entry point for flext-docs."""
    instance = cli()
    _ = instance.execute()


if __name__ == "__main__":
    main()

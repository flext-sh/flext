#!/usr/bin/env python3
"""FlextMeltano Bridge Script - CLI interface para integração Go ↔ Python.

Este script fornece interface CLI para comunicação entre FlexCore Go service
e flext-meltano Python library, retornando resultados em formato JSON.
"""

import sys

from flext_meltano.executors_bridge import FlextMeltanoBridge


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    bridge = FlextMeltanoBridge()
    bridge.handle_command(command, args)

    # Output JSON result for Go consumption


if __name__ == "__main__":
    main()

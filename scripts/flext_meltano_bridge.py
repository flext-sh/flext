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

    # Route command to appropriate method
    if command == "version":
        result = bridge.get_version_json()
    elif command == "run_pipeline":
        tap_name = args[0] if len(args) > 0 else "default_tap"
        target_name = args[1] if len(args) > 1 else "default_target"
        result = bridge.run_pipeline(tap_name, target_name)
    elif command == "install_plugin":
        plugin_name = args[0] if len(args) > 0 else "default_plugin"
        plugin_type = args[1] if len(args) > 1 else "tap"
        result = bridge.install_plugin(".", plugin_type, plugin_name)
    else:
        result = {"error": f"Unknown command: {command}"}

    print(result)

    # Output JSON result for Go consumption


if __name__ == "__main__":
    main()

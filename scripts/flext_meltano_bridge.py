#!/usr/bin/env python3
"""FlextMeltano Bridge Script - CLI interface para integração Go ↔ Python.

Este script fornece interface CLI para comunicação entre FlexCore Go service
e flext-meltano Python library, retornando resultados em formato JSON.

Usage:
    python scripts/flext_meltano_bridge.py version
    python scripts/flext_meltano_bridge.py list_plugins [project_root]
    python scripts/flext_meltano_bridge.py run_pipeline project_root tap_name target_name
    python scripts/flext_meltano_bridge.py add_plugin project_root plugin_type plugin_name
    python scripts/flext_meltano_bridge.py run_dbt project_root command args...
    python scripts/flext_meltano_bridge.py project_info project_root
    python scripts/flext_meltano_bridge.py discover project_root tap_name
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flext_meltano.adapter import FlextMeltanoCLIBridge


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/flext_meltano_bridge.py <command> [args...]")
        print(
            "Commands: version, list_plugins, run_pipeline, add_plugin, run_dbt, project_info, discover"
        )
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    bridge = FlextMeltanoCLIBridge()
    result = bridge.handle_command(command, args)

    # Output JSON result for Go consumption
    print(result)


if __name__ == "__main__":
    main()

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

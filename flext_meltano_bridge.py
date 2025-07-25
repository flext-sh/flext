#!/usr/bin/env python3
"""BRIDGE GO->PYTHON: Interface isolada para flext-meltano sem dependências externas.

Este script fornece uma interface JSON limpa para o serviço Go
chamar operações Meltano via subprocess, SEM dependências flext_core.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any


class FlextMeltanoBridge:
    """Bridge isolado para operações Meltano sem dependências externas."""

    def __init__(self, project_root: str = "/home/marlonsc/flext") -> None:
        self.project_root = Path(project_root)
        self.meltano_path = self.project_root / ".venv" / "bin" / "meltano"

    def execute_meltano_command(self, command: list[str]) -> dict[str, Any]:
        """Executa comando Meltano e retorna resultado JSON."""
        try:
            full_command = [str(self.meltano_path), *command]
            result = subprocess.run(
                full_command,
                check=False, cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(command),
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after 30 seconds: {' '.join(command)}",
                "returncode": -1,
                "command": " ".join(command),
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1,
                "command": " ".join(command),
            }

    def get_version(self) -> dict[str, Any]:
        """Obtém versão do Meltano."""
        return self.execute_meltano_command(["--version"])

    def list_plugins(self) -> dict[str, Any]:
        """Lista plugins instalados."""
        return self.execute_meltano_command(["config", "meltano"])

    def add_plugin(self, plugin_type: str, plugin_name: str) -> dict[str, Any]:
        """Adiciona e instala plugin."""
        return self.execute_meltano_command(["add", plugin_type, plugin_name, "--install"])

    def discover_catalog(self, tap_name: str) -> dict[str, Any]:
        """Descobre catálogo de um tap."""
        return self.execute_meltano_command(["invoke", tap_name, "--discover"])

    def run_pipeline(self, tap_name: str, target_name: str) -> dict[str, Any]:
        """Executa pipeline tap->target."""
        return self.execute_meltano_command(["run", tap_name, target_name])

    def invoke_dbt(self, dbt_command: str, *args: str) -> dict[str, Any]:
        """Invoca comando DBT via Meltano."""
        command = ["invoke", f"dbt:{dbt_command}", *list(args)]
        return self.execute_meltano_command(command)


def main() -> None:
    """Interface CLI para o bridge."""
    if len(sys.argv) < 2:
        sys.exit(1)

    operation = sys.argv[1]
    bridge = FlextMeltanoBridge()

    try:
        if operation == "version":
            bridge.get_version()
        elif operation == "list_plugins":
            bridge.list_plugins()
        elif operation == "add_plugin" and len(sys.argv) >= 4:
            bridge.add_plugin(sys.argv[2], sys.argv[3])
        elif operation == "discover" and len(sys.argv) >= 3:
            bridge.discover_catalog(sys.argv[2])
        elif operation == "run_pipeline" and len(sys.argv) >= 4:
            bridge.run_pipeline(sys.argv[2], sys.argv[3])
        elif operation == "invoke_dbt" and len(sys.argv) >= 3:
            bridge.invoke_dbt(sys.argv[2], *sys.argv[3:])

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()

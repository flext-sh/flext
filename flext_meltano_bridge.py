#!/usr/bin/env python3
"""BRIDGE GO->PYTHON: Interface isolada para flext-meltano sem dependências externas.

Este script fornece uma interface JSON limpa para o serviço Go
chamar operações Meltano via subprocess, SEM dependências flext_core.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class FlextMeltanoBridge:
    """Bridge isolado para operações Meltano sem dependências externas."""

    def __init__(self, project_root: str = "/home/marlonsc/flext"):
        self.project_root = Path(project_root)
        self.meltano_path = self.project_root / ".venv" / "bin" / "meltano"

    def execute_meltano_command(self, command: List[str]) -> Dict[str, Any]:
        """Executa comando Meltano e retorna resultado JSON."""
        try:
            full_command = [str(self.meltano_path)] + command
            result = subprocess.run(
                full_command,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(command)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after 30 seconds: {' '.join(command)}",
                "returncode": -1,
                "command": " ".join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1,
                "command": " ".join(command)
            }

    def get_version(self) -> Dict[str, Any]:
        """Obtém versão do Meltano."""
        return self.execute_meltano_command(["--version"])

    def list_plugins(self) -> Dict[str, Any]:
        """Lista plugins instalados."""
        return self.execute_meltano_command(["config", "meltano"])

    def add_plugin(self, plugin_type: str, plugin_name: str) -> Dict[str, Any]:
        """Adiciona e instala plugin."""
        return self.execute_meltano_command(["add", plugin_type, plugin_name, "--install"])

    def discover_catalog(self, tap_name: str) -> Dict[str, Any]:
        """Descobre catálogo de um tap."""
        return self.execute_meltano_command(["invoke", tap_name, "--discover"])

    def run_pipeline(self, tap_name: str, target_name: str) -> Dict[str, Any]:
        """Executa pipeline tap->target."""
        return self.execute_meltano_command(["run", tap_name, target_name])

    def invoke_dbt(self, dbt_command: str, *args: str) -> Dict[str, Any]:
        """Invoca comando DBT via Meltano."""
        command = ["invoke", f"dbt:{dbt_command}"] + list(args)
        return self.execute_meltano_command(command)


def main():
    """Interface CLI para o bridge."""
    if len(sys.argv) < 2:
        result = {
            "success": False,
            "error": "Usage: python flext_meltano_bridge.py <operation> [args...]",
            "available_operations": [
                "version",
                "list_plugins", 
                "add_plugin <type> <name>",
                "discover <tap_name>",
                "run_pipeline <tap> <target>",
                "invoke_dbt <command> [args...]"
            ]
        }
        print(json.dumps(result))
        sys.exit(1)

    operation = sys.argv[1]
    bridge = FlextMeltanoBridge()

    try:
        if operation == "version":
            result = bridge.get_version()
        elif operation == "list_plugins":
            result = bridge.list_plugins()
        elif operation == "add_plugin" and len(sys.argv) >= 4:
            result = bridge.add_plugin(sys.argv[2], sys.argv[3])
        elif operation == "discover" and len(sys.argv) >= 3:
            result = bridge.discover_catalog(sys.argv[2])
        elif operation == "run_pipeline" and len(sys.argv) >= 4:
            result = bridge.run_pipeline(sys.argv[2], sys.argv[3])
        elif operation == "invoke_dbt" and len(sys.argv) >= 3:
            result = bridge.invoke_dbt(sys.argv[2], *sys.argv[3:])
        else:
            result = {
                "success": False,
                "error": f"Invalid operation: {operation} or missing arguments"
            }

        print(json.dumps(result))

    except Exception as e:
        result = {
            "success": False,
            "error": f"Bridge execution failed: {str(e)}"
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Script simplificado para usar o MonkeyType com DCApiX."""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_tests() -> Any:
    """Executa testes com MonkeyType."""
    cmd = ["monkeytype", "run", "-m", "pytest"]
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    return result.returncode


def list_modules() -> Any:
    """Lista os módulos com informações de tipo coletadas."""
    cmd = ["monkeytype", "list-modules"]
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    return result.returncode


def apply_types(module) -> Any:
    """Aplica tipos a um módulo."""
    # Verificar se o arquivo existe
    module_parts = module.split(".")
    workspace_root = Path.cwd()

    print(f"Módulo: {module}")
    print(f"Partes: {module_parts}")
    print(f"Workspace root: {workspace_root}")

    if module_parts[0] == "dc_api_x":
        # Verificar possíveis caminhos
        paths = [
            # src/dc_api_x/utils/logging.py
            workspace_root / "src" / "dc_api_x" /
            "/".join(module_parts[1:]) + ".py",
            # src/dc_api_x/utils/logging.py (construído de outro modo)
            workspace_root / "src" /
            module_parts[0] / "/".join(module_parts[1:])
            + ".py",
            # src/utils/logging.py
            workspace_root / "src" / "/".join(module_parts[1:]) + ".py",
        ]

        for path in paths:
            print(f"Verificando: {path} - Existe: {path.exists()}")

    # Aplicar tipos com monkeytype
    cmd = ["monkeytype", "apply", module]
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(description="MonkeyType para DCApiX")
    subparsers = parser.add_subparsers(
        dest="command", help="Comando a executar")
    subparsers.required = True

    # Comando run
    subparsers.add_parser("run", help="Executar testes com MonkeyType")

    # Comando list
    subparsers.add_parser("list", help="Listar módulos")

    # Comando apply
    apply_parser = subparsers.add_parser("apply", help="Aplicar tipos")
    apply_parser.add_argument("module", help="Módulo para aplicar tipos")

    args = parser.parse_args()

    if args.command == "run":
        return run_tests()
    if args.command == "list":
        return list_modules()
    if args.command == "apply":
        return apply_types(args.module)
    print(f"Comando desconhecido: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

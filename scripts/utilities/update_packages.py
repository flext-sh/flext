#!/usr/bin/env python3
"""Script para atualização de pacotes Python no workspace.
Author: Marlon Costa <marlon.costa@datacosmos.com.br>
License: MIT.
"""

import argparse
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent.absolute()


def run_command(
    cmd: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Executa um comando e retorna a saída."""
    print(f"Executando: {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=cwd or WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def update_packages(force: bool = False) -> bool:
    """Atualiza todos os pacotes do projeto."""
    print("=== Atualizando pacotes do projeto ===")

    # Determina se estamos em um ambiente virtual
    venv_bin = WORKSPACE_ROOT / ".venv" / "bin"
    if not venv_bin.exists():
        print("Ambiente virtual não encontrado. Execute 'make install' primeiro.")
        return False

    # Comando Poetry
    poetry_bin = venv_bin / "poetry"
    if not poetry_bin.exists():
        print("Poetry não encontrado no ambiente virtual.")
        return False

    # Opções para atualização
    update_cmd = [str(poetry_bin), "update"]
    if force:
        update_cmd.append("--lock")

    # Executa a atualização
    try:
        result = run_command(update_cmd)
        print(result.stdout)
        if result.stderr:
            print(f"Avisos: {result.stderr}", file=sys.stderr)

        print("Atualização de pacotes concluída com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar pacotes: {e}", file=sys.stderr)
        print(f"Saída: {e.stdout}", file=sys.stderr)
        print(f"Erro: {e.stderr}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gerenciador de atualização de pacotes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força atualização mesmo com conflitos",
    )

    args = parser.parse_args()
    success = update_packages(force=args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

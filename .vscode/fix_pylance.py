#!/usr/bin/env python3
"""Script para diagnosticar e corrigir problemas do Pylance/VS Code.

Uso: python .vscode/fix_pylance.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description) -> bool | None:
    """Executa um comando e mostra o resultado."""
    try:
        result = subprocess.run(
            cmd, check=False, shell=True, capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> None:
    workspace_root = Path(__file__).parent.parent
    os.chdir(workspace_root)

    # 1. Limpar caches Python
    run_command(
        "find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true",
        "Limpando cache Python",
    )

    # 2. Limpar cache do Pylance
    pylance_cache = workspace_root / ".pylance_cache"
    if pylance_cache.exists():
        shutil.rmtree(pylance_cache)

    # 3. Verificar configurações do pyright

    # Verificar configurações nos pyproject.toml
    mt5linux_pyproject = workspace_root / "mt5linux" / "pyproject.toml"
    if mt5linux_pyproject.exists():
        pass

    neptor_pyproject = workspace_root / "neptor" / "pyproject.toml"
    if neptor_pyproject.exists():
        pass

    vscode_settings = workspace_root / ".vscode" / "settings.json"
    if vscode_settings.exists():
        pass

    # 4. Testar Pyright diretamente
    mt5linux_dir = workspace_root / "mt5linux"
    if mt5linux_dir.exists():
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pyright",
                "--outputformat",
                "json",
                str(mt5linux_dir / "mt5linux" / "mt5_pb2_grpc.py"),
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(mt5linux_dir),
        )

        if "grpc._utilities" in result.stdout:
            pass


if __name__ == "__main__":
    main()

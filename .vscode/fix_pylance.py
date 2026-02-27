#!/usr/bin/env python3
"""Script para diagnosticar e corrigir problemas do Pylance/VS Code.

Uso: python .vscode/fix_pylance.py
"""

import os
import shutil
import subprocessimport sys
from pathlib import Path


def clean_pycache(root: Path) -> None:
    """Remove directories __pycache__ recursively."""
    for p in root.rglob("__pycache__"):
        if p.is_dir():
            shutil.rmtree(p)


def main() -> None:
    """Execute main script logic."""
    workspace_root = Path(__file__).resolve().parent.parent
    os.chdir(workspace_root)

    # 1. Limpar caches Python
    clean_pycache(workspace_root)

    # 2. Limpar cache do Pylance
    pylance_cache = workspace_root / ".pylance_cache"
    if pylance_cache.exists():
        shutil.rmtree(pylance_cache)

    # 3. Verificar configurações do pyright (Checks only, no side effects)
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
    try:
        mt5linux_dir = workspace_root / "mt5linux"
        if mt5linux_dir.exists():
            target_file = mt5linux_dir / "mt5linux" / "mt5_pb2_grpc.py"
            result = subprocess.run(                [
                    sys.executable,
                    "-m",
                    "pyright",
                    "--outputformat",
                    "json",
                    str(target_file),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(mt5linux_dir),
            )

            if str(result.stdout) and "grpc._utilities" in str(result.stdout):
                pass
    except (FileNotFoundError, OSError):
        pass


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Teste do script discover_missing_deps.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_project():
    """Cria projeto de teste com import faltante."""
    test_dir = Path(tempfile.mkdtemp(prefix="test_discovery_"))

    # Estrutura
    src_dir = test_dir / "src" / "myproject"
    src_dir.mkdir(parents=True)

    # pyproject.toml mínimo
    pyproject = test_dir / "pyproject.toml"
    pyproject.write_text("""
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "Test"
authors = ["Test"]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""".strip())

    # __init__.py
    (src_dir / "__init__.py").write_text("")

    # main.py com imports faltantes
    (src_dir / "main.py").write_text("""
import os  # stdlib
import requests  # faltante
import pandas as pd  # faltante
from typing import Dict  # stdlib

def main():
    resp = requests.get("http://example.com")
    df = pd.DataFrame()
    print("OK")
""".strip())

    return test_dir


def main():
    print("=== TESTE: discover_missing_deps.py ===\n")

    # Cria projeto teste
    test_dir = create_test_project()
    print(f"Projeto teste criado em: {test_dir}")

    try:
        # Teste 1: Descoberta
        print("\n1. Testando descoberta...")
        cmd = [sys.executable, "discover_missing_deps.py", str(test_dir)]
        result = subprocess.run(
            cmd,
            check=False, cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )

        print(f"Return code: {result.returncode}")
        print("Output:")
        print(result.stdout)

        if "requests" in result.stdout and "pandas" in result.stdout:
            print("✓ Descobriu dependências faltantes!")
        else:
            print("✗ Não descobriu todas as dependências")
            return 1

        # Teste 2: Aplicação
        print("\n2. Testando aplicação...")
        cmd_apply = [sys.executable, "discover_missing_deps.py", str(test_dir), "--apply"]
        result_apply = subprocess.run(
            cmd_apply,
            check=False, cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )

        print(f"Return code: {result_apply.returncode}")
        print("Output:")
        print(result_apply.stdout)

        # Verifica se foi adicionado
        pyproject_content = (test_dir / "pyproject.toml").read_text()
        if "requests" in pyproject_content:
            print("\n✓ SUCESSO TOTAL: Dependências foram adicionadas!")
            return 0
        print("\n✗ Dependências não foram adicionadas ao pyproject.toml")
        return 1

    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        return 1
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

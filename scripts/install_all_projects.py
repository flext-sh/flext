#!/usr/bin/env python3
"""Script para instalar todos os projetos FLEXT em modo de desenvolvimento.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Este script instala todos os projetos FLEXT em modo de desenvolvimento
com suas dependências completas via Poetry.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_directories() -> list[str]:
    """Obter lista de diretórios de projetos principais."""
    workspace_root = Path(__file__).parent.parent
    projects = []

    # Projetos principais (excluindo backups e arquivos temporários)
    for pyproject in workspace_root.rglob("pyproject.toml"):
        if any(
            exclude in str(pyproject)
            for exclude in [".venv", ".flext_backups", "test_failures"]
        ):
            continue

        project_dir = pyproject.parent
        if project_dir != workspace_root:  # Excluir workspace root
            projects.append(str(project_dir))

    return sorted(projects)


def run_poetry_install(project_dir: str) -> tuple[bool, str]:
    """Executar poetry install em um projeto."""
    try:
        print(f"📦 Instalando {Path(project_dir).name}...")

        # Verificar se existe pyproject.toml
        pyproject_path = os.path.join(project_dir, "pyproject.toml")
        if not Path(pyproject_path).exists():
            return False, f"pyproject.toml não encontrado em {project_dir}"

        # Executar poetry install
        result = subprocess.run(
            ["poetry", "install"],
            check=False,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
        )

        if result.returncode == 0:
            return True, "✅ Sucesso"
        return False, f"❌ Erro: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "❌ Timeout (5 minutos)"
    except (OSError, ValueError, TypeError) as e:
        return False, f"❌ Exceção: {e!s}"


def main() -> int:
    """Função principal."""
    print("🚀 INSTALADOR DE TODOS OS PROJETOS FLEXT")
    print("=" * 50)

    # Obter projetos
    projects = get_project_directories()
    print(f"📋 Encontrados {len(projects)} projetos para instalar:")

    for project in projects:
        print(f"  - {Path(project).name}")

    print("\n" + "=" * 50)

    # Instalar projetos
    results = []
    for project in projects:
        success, message = run_poetry_install(project)
        results.append((project, success, message))
        print(f"  {Path(project).name}: {message}")

    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA INSTALAÇÃO:")

    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful

    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")

    if failed > 0:
        print("\n❌ PROJETOS COM FALHA:")
        for project, success, message in results:
            if not success:
                print(f"  - {Path(project).name}: {message}")

    print(
        f"\n🎉 Instalação concluída! {successful}/{len(results)} projetos instalados com sucesso.",
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

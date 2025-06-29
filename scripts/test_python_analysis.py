#!/usr/bin/env python3
"""
Script para testar se a análise Python está funcionando corretamente.
Este script verifica a configuração do Cursor/VSCode para análise completa da workspace.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    """Executa testes de verificação da análise Python."""
    workspace_root = Path(__file__).parent.parent
    print(f"🔍 Testando análise Python na workspace: {workspace_root}")

    # 1. Verificar se o interpretador Python está correto
    print("\n1. Verificando interpretador Python...")
    venv_python = workspace_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        print(f"✅ Interpretador encontrado: {venv_python}")
        result = subprocess.run(
            [str(venv_python), "--version"], capture_output=True, text=True
        )
        print(f"   Versão: {result.stdout.strip()}")
    else:
        print(f"❌ Interpretador não encontrado: {venv_python}")

    # 2. Verificar configurações do Cursor
    print("\n2. Verificando configurações do Cursor...")
    cursor_settings = workspace_root / ".cursor" / "settings.json"
    vscode_settings = workspace_root / ".vscode" / "settings.json"

    if cursor_settings.exists():
        print(f"✅ Configurações do Cursor encontradas: {cursor_settings}")
    else:
        print(f"❌ Configurações do Cursor não encontradas: {cursor_settings}")

    if vscode_settings.exists():
        print(f"✅ Configurações do VSCode encontradas: {vscode_settings}")
    else:
        print(f"❌ Configurações do VSCode não encontradas: {vscode_settings}")

    # 3. Verificar projetos incluídos na análise
    print("\n3. Verificando projetos da workspace...")
    expected_projects = [
        "flx-core/src",
        "flx-api/src",
        "flx-auth/src",
        "flx-cli/src",
        "flx-grpc/src",
        "flx-ldap/src",
        "flx-meltano/src",
        "flx-observability/src",
        "flx-plugin/src",
        "flx-quality/src",
        "flx-web/src",
        "flx-db-oracle/src",
        "oracledb-core-shared/src",
        "tap-ldap/src",
        "tap-oracle-oic/src",
        "tap-oracle-wms/src",
        "target-ldap/src",
        "target-oracle-oic/src",
        "target-oracle-wms/src",
        "client-a-oud-mig/src",
        "client-b-poc-oic-wms/src",
        "flx-meltano-enterprise-github/src",
        "dbt-ldap/src",
    ]

    found_projects = 0
    for project_path in expected_projects:
        full_path = workspace_root / project_path
        if full_path.exists():
            print(f"✅ {project_path}")
            found_projects += 1
        else:
            print(f"⚠️  {project_path} (não encontrado)")

    print(f"\n📊 Projetos encontrados: {found_projects}/{len(expected_projects)}")

    # 4. Verificar arquivos de configuração de linting
    print("\n4. Verificando configurações de linting...")
    config_files = ["mypy.ini", "pyproject.toml", ".pre-commit-config.yaml"]

    for config_file in config_files:
        config_path = workspace_root / config_file
        if config_path.exists():
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} não encontrado")

    # 5. Testar MyPy em um projeto exemplo
    print("\n5. Testando MyPy...")
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "mypy", "--version"],
            capture_output=True,
            text=True,
            cwd=workspace_root,
        )

        if result.returncode == 0:
            print(f"✅ MyPy instalado: {result.stdout.strip()}")

            # Testar em um arquivo exemplo se existir
            test_file = workspace_root / "flx-core" / "src" / "flx_core" / "__init__.py"
            if test_file.exists():
                result = subprocess.run(
                    [str(venv_python), "-m", "mypy", str(test_file)],
                    capture_output=True,
                    text=True,
                    cwd=workspace_root,
                )

                if result.returncode == 0:
                    print("✅ MyPy executou sem erros críticos")
                else:
                    print(f"⚠️  MyPy encontrou problemas:\n{result.stdout}")
        else:
            print(f"❌ Erro ao executar MyPy: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao testar MyPy: {e}")

    # 6. Testar Ruff
    print("\n6. Testando Ruff...")
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "ruff", "--version"],
            capture_output=True,
            text=True,
            cwd=workspace_root,
        )

        if result.returncode == 0:
            print(f"✅ Ruff instalado: {result.stdout.strip()}")
        else:
            print("❌ Ruff não encontrado")
    except Exception as e:
        print(f"❌ Erro ao testar Ruff: {e}")

    print("\n" + "=" * 50)
    print("🎯 RESUMO DO TESTE DE CONFIGURAÇÃO")
    print("=" * 50)
    print("Para que a análise Python funcione completamente:")
    print("1. Reinicie o Cursor IDE")
    print("2. Aguarde a indexação completa (pode levar alguns minutos)")
    print("3. Abra o painel Problems (Ctrl+Shift+M)")
    print("4. Verifique se os problemas aparecem em tempo real")
    print("\nAtalhos úteis:")
    print("- Ctrl+Shift+E: Focar no painel Problems")
    print("- Alt+F8: Próximo problema")
    print("- Alt+Shift+F8: Problema anterior")
    print("- Ctrl+Shift+R: Refresh IntelliSense")


if __name__ == "__main__":
    main()

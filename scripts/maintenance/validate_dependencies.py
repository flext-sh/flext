#!/usr/bin/env python3
"""
Script para validar se as dependências circulares foram corrigidas.

Este script verifica:
1. Se ainda existem imports diretos do FLX fora do projeto FLX
2. Se os lazy imports estão funcionando corretamente
3. Se os pyproject.toml estão bem configurados
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_direct_flx_imports() -> list[str]:
    """Verifica se ainda existem imports diretos do FLX fora do projeto FLX."""
    issues: list = []

    # Projetos que não devem ter imports diretos do FLX
    projects_to_check = [
        "flx-http-oracle-oic",
        "flx-http-oracle-wms",
        "flx-database-oracle",
        "flx-oracle-oic",
        "flx-oracle-wms",
        "target-oracle-oic",
        "target-oracle-wms",
        "tap-oracle-oic",
        "tap-oracle-wms",
    ]

    for project in projects_to_check:
        project_path = Path(project)
        if not project_path.exists():
            continue

        src_path = project_path / "src"
        if not src_path.exists():
            continue

        for py_file in src_path.rglob("*.py"):
            if "test" in str(py_file) or "example" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # Verifica imports diretos do FLX (exceto lazy_import)
                    if (
                        line.startswith(("from flx.", "import flx."))
                    ) and "lazy_import" not in line:
                        issues.append(
                            f"{py_file}:{line_num} - Import direto do FLX: {line}"
                        )

            except Exception as e:
                issues.append(f"Erro ao analisar {py_file}: {e}")

    return issues


def check_lazy_import_usage() -> list[str]:
    """Verifica se os lazy imports estão sendo usados corretamente."""
    issues: list = []

    projects_to_check = [
        "flx-http-oracle-oic",
        "flx-http-oracle-wms",
        "flx-database-oracle",
        "flx-oracle-oic",
        "flx-oracle-wms",
    ]

    for project in projects_to_check:
        project_path = Path(project)
        if not project_path.exists():
            continue

        src_path = project_path / "src"
        if not src_path.exists():
            continue

        lazy_import_files: list = []
        for py_file in src_path.rglob("*.py"):
            if "test" in str(py_file) or "example" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if "lazy_import" in content:
                    lazy_import_files.append(py_file)

                    # Verifica se o import do lazy_import está presente
                    if "from flx.utils.lazy_import import lazy_import" not in content:
                        issues.append(
                            f"{py_file} - Usa lazy_import mas não importa a função"
                        )

            except Exception as e:
                issues.append(f"Erro ao analisar {py_file}: {e}")

        if lazy_import_files:
            print(
                f"✅ {project}: {len(lazy_import_files)} arquivos usando lazy imports"
            )
            print(f"⚠️  {project}: Nenhum arquivo usando lazy imports")

    return issues


def check_pyproject_dependencies() -> list[str]:
    """Verifica se os pyproject.toml estão bem configurados."""
    issues: list = []

    # Verifica o pyproject.toml principal
    main_pyproject = Path("pyproject.toml")
    if main_pyproject.exists():
        try:
            with open(main_pyproject, encoding="utf-8") as f:
                content = f.read()

            # Verifica se FLX não é opcional no principal
            if 'flx = { path = "flx", develop = true, optional = true }' in content:
                issues.append("pyproject.toml principal - FLX não deve ser opcional")

            # Verifica se subprojetos são opcionais
            required_optional = [
                "flx-database-oracle",
                "flx-http-oracle-oic",
                "flx-http-oracle-wms",
                "flx-oracle-oic",
                "flx-oracle-wms",
            ]

            for project in required_optional:
                if f'{project} = {{ path = "./{project}", develop = true }}' in content:
                    issues.append(
                        f"pyproject.toml principal - {project} deve ser opcional"
                    )

        except Exception as e:
            issues.append(f"Erro ao analisar pyproject.toml principal: {e}")

    # Verifica pyproject.toml dos subprojetos
    subprojects = [
        "flx-http-oracle-oic",
        "flx-oracle-oic",
        "flx-ldap",
    ]

    for project in subprojects:
        pyproject_path = Path(project) / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, encoding="utf-8") as f:
                    content = f.read()

                # Verifica se dependências do FLX são opcionais
                if 'flx = { path = "../flx", develop = true }' in content:
                    issues.append(
                        f"{project}/pyproject.toml - Dependência do FLX deve ser opcional"
                    )

            except Exception as e:
                issues.append(f"Erro ao analisar {project}/pyproject.toml: {e}")

    return issues


def test_import_flx_utils() -> list[str]:
    """Testa se o módulo lazy_import pode ser importado."""
    issues: list = []

    try:
        # Adiciona o caminho do FLX ao sys.path temporariamente
        flx_src_path = Path("flx/src")
        if flx_src_path.exists():
            sys.path.insert(0, str(flx_src_path))

        # Tenta importar o lazy_import
        from flx.utils.lazy_import import LazyImport, lazy_import

        # Testa funcionalidade básica
        test_lazy = lazy_import("os", "path")
        if not isinstance(test_lazy, LazyImport):
            issues.append("lazy_import não retorna instância LazyImport")

        print("✅ Módulo lazy_import funciona corretamente")

    except ImportError as e:
        issues.append(f"Não foi possível importar lazy_import: {e}")
    except Exception as e:
        issues.append(f"Erro ao testar lazy_import: {e}")
    finally:
        # Remove o caminho do sys.path
        if str(flx_src_path) in sys.path:
            sys.path.remove(str(flx_src_path))

    return issues


def main() -> None:
    """Função principal."""
    print("🔍 Validando correção de dependências circulares...")

    all_issues: list = []

    print("\n1. Verificando imports diretos do FLX...")
    direct_import_issues = check_direct_flx_imports()
    all_issues.extend(direct_import_issues)

    if direct_import_issues:
        print(f"❌ {len(direct_import_issues)} imports diretos encontrados")
        for issue in direct_import_issues[:5]:  # Mostra apenas os primeiros 5
            print(f"  - {issue}")
        if len(direct_import_issues) > 5:
            print(f"  ... e mais {len(direct_import_issues) - 5} problemas")
        print("✅ Nenhum import direto do FLX encontrado")

    print("\n2. Verificando uso de lazy imports...")
    lazy_import_issues = check_lazy_import_usage()
    all_issues.extend(lazy_import_issues)

    if lazy_import_issues:
        print(f"❌ {len(lazy_import_issues)} problemas com lazy imports")
        for issue in lazy_import_issues:
            print(f"  - {issue}")
        print("✅ Lazy imports configurados corretamente")

    print("\n3. Verificando configuração dos pyproject.toml...")
    pyproject_issues = check_pyproject_dependencies()
    all_issues.extend(pyproject_issues)

    if pyproject_issues:
        print(f"❌ {len(pyproject_issues)} problemas nos pyproject.toml")
        for issue in pyproject_issues:
            print(f"  - {issue}")
        print("✅ pyproject.toml configurados corretamente")

    print("\n4. Testando funcionalidade do lazy_import...")
    lazy_test_issues = test_import_flx_utils()
    all_issues.extend(lazy_test_issues)

    if lazy_test_issues:
        print(f"❌ {len(lazy_test_issues)} problemas com lazy_import")
        for issue in lazy_test_issues:
            print(f"  - {issue}")

    # Resultado final
    print(f"\n{'=' * 60}")
    if all_issues:
        print(f"❌ VALIDAÇÃO FALHOU: {len(all_issues)} problemas encontrados")
        print("\n🔧 Problemas que precisam ser corrigidos:")
        for issue in all_issues:
            print(f"  - {issue}")
        sys.exit(1)
        print("✅ VALIDAÇÃO PASSOU: Dependências circulares corrigidas com sucesso!")
        print("\n🎉 Benefícios alcançados:")
        print("  - Imports diretos do FLX eliminados")
        print("  - Lazy imports implementados corretamente")
        print("  - Dependências opcionais configuradas")
        print("  - Compatibilidade com workspace mantida")
        print("  - Possibilidade de usar subprojetos independentemente")


if __name__ == "__main__":
    main()

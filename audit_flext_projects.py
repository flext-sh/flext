#!/usr/bin/env python3
"""Audit completo e honesto de todos os projetos FLEXT.
Sem inventar nada - apenas contar e verificar fatos reais.
"""

import json
import subprocess
from pathlib import Path
from typing import Any


def count_lines_in_directory(directory: Path, pattern: str = "*.py") -> int:
    """Conta linhas reais de código Python em um diretório."""
    try:
        cmd = ["find", str(directory), "-name", pattern, "-type", "f", "-exec", "wc", "-l", "{}", "+"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            if lines and "total" in lines[-1]:
                return int(lines[-1].split()[0])
        return 0
    except (subprocess.SubprocessError, ValueError, IndexError):
        return 0


def check_pyproject_toml(project_path: Path) -> dict[str, Any]:
    """Verifica se tem pyproject.toml e extrai info básica."""
    pyproject_file = project_path / "pyproject.toml"
    info = {
        "has_pyproject": pyproject_file.exists(),
        "version": "unknown",
        "dependencies": [],
        "flext_core_dependency": False
    }

    if pyproject_file.exists():
        try:
            content = pyproject_file.read_text()
            if "flext-core" in content:
                info["flext_core_dependency"] = True
        except Exception:
            pass

    return info


def check_directory_structure(project_path: Path) -> dict[str, bool]:
    """Verifica estrutura básica de diretórios."""
    return {
        "has_src": (project_path / "src").exists(),
        "has_tests": (project_path / "tests").exists(),
        "has_docs": (project_path / "docs").exists(),
        "has_examples": (project_path / "examples").exists(),
        "has_makefile": (project_path / "Makefile").exists(),
        "has_readme": (project_path / "README.md").exists(),
    }


def has_actual_python_code(project_path: Path) -> bool:
    """Verifica se tem código Python real (não apenas __init__.py vazios)."""
    src_dir = project_path / "src"
    if not src_dir.exists():
        return False

    # Conta arquivos Python com mais de 10 linhas
    python_files = list(src_dir.rglob("*.py"))
    substantial_files = 0

    for py_file in python_files:
        try:
            if py_file.stat().st_size > 200:  # Mais que 200 bytes
                substantial_files += 1
        except OSError:
            continue

    return substantial_files > 1  # Mais que só __init__.py


def audit_single_project(project_path: Path) -> dict[str, Any]:
    """Faz audit de um único projeto FLEXT."""
    project_name = project_path.name

    # Contagem de linhas
    src_lines = count_lines_in_directory(project_path / "src")
    test_lines = count_lines_in_directory(project_path / "tests")

    # Verificações estruturais
    pyproject_info = check_pyproject_toml(project_path)
    structure = check_directory_structure(project_path)
    has_code = has_actual_python_code(project_path)

    # Status geral
    if src_lines == 0:
        status = "EMPTY"
    elif src_lines < 100:
        status = "MINIMAL"
    elif src_lines < 1000:
        status = "BASIC"
    elif src_lines < 5000:
        status = "SUBSTANTIAL"
    else:
        status = "LARGE"

    return {
        "name": project_name,
        "status": status,
        "src_lines": src_lines,
        "test_lines": test_lines,
        "total_lines": src_lines + test_lines,
        "has_actual_code": has_code,
        "pyproject_info": pyproject_info,
        "structure": structure,
        "test_coverage_estimate": "HIGH" if test_lines > src_lines * 0.5 else "LOW" if test_lines > 0 else "NONE"
    }


def main():
    """Executa audit completo de todos os projetos FLEXT."""
    workspace_path = Path("/home/marlonsc/flext")

    # Encontra todos os projetos flext-*
    flext_projects = sorted([
        p for p in workspace_path.iterdir()
        if p.is_dir() and p.name.startswith("flext-")
    ])

    print("🔍 AUDIT COMPLETO E HONESTO - PROJETOS FLEXT")
    print("=" * 60)
    print(f"Total de projetos encontrados: {len(flext_projects)}")
    print()

    results = []
    total_src_lines = 0
    total_test_lines = 0

    # Categorias
    empty_projects = []
    minimal_projects = []
    basic_projects = []
    substantial_projects = []
    large_projects = []

    for project_path in flext_projects:
        result = audit_single_project(project_path)
        results.append(result)

        total_src_lines += result["src_lines"]
        total_test_lines += result["test_lines"]

        # Categoriza
        if result["status"] == "EMPTY":
            empty_projects.append(result)
        elif result["status"] == "MINIMAL":
            minimal_projects.append(result)
        elif result["status"] == "BASIC":
            basic_projects.append(result)
        elif result["status"] == "SUBSTANTIAL":
            substantial_projects.append(result)
        elif result["status"] == "LARGE":
            large_projects.append(result)

    # Relatório detalhado
    print("📊 RELATÓRIO POR PROJETO")
    print("-" * 60)
    for result in results:
        deps_info = "✅ flext-core" if result["pyproject_info"]["flext_core_dependency"] else "❌ no flext-core"
        code_info = "✅ código real" if result["has_actual_code"] else "❌ vazio/minimal"

        print(f"{result['name']:<25} | {result['status']:<12} | "
              f"Src: {result['src_lines']:>5} | Test: {result['test_lines']:>5} | "
              f"{deps_info} | {code_info}")

    print()
    print("📈 RESUMO ESTATÍSTICO")
    print("-" * 60)
    print(f"Total de linhas de código fonte: {total_src_lines:,}")
    print(f"Total de linhas de teste: {total_test_lines:,}")
    print(f"Total de linhas: {total_src_lines + total_test_lines:,}")
    print()

    print("🏷️ PROJETOS POR CATEGORIA")
    print("-" * 60)
    print(f"EMPTY (0 linhas): {len(empty_projects)} projetos")
    for p in empty_projects:
        print(f"  - {p['name']}")

    print(f"MINIMAL (1-99 linhas): {len(minimal_projects)} projetos")
    for p in minimal_projects:
        print(f"  - {p['name']} ({p['src_lines']} linhas)")

    print(f"BASIC (100-999 linhas): {len(basic_projects)} projetos")
    for p in basic_projects:
        print(f"  - {p['name']} ({p['src_lines']} linhas)")

    print(f"SUBSTANTIAL (1000-4999 linhas): {len(substantial_projects)} projetos")
    for p in substantial_projects:
        print(f"  - {p['name']} ({p['src_lines']} linhas)")

    print(f"LARGE (5000+ linhas): {len(large_projects)} projetos")
    for p in large_projects:
        print(f"  - {p['name']} ({p['src_lines']} linhas)")

    print()
    print("🔗 DEPENDÊNCIAS DO FLEXT-CORE")
    print("-" * 60)
    with_core = [p for p in results if p["pyproject_info"]["flext_core_dependency"]]
    without_core = [p for p in results if not p["pyproject_info"]["flext_core_dependency"]]

    print(f"Projetos que dependem do flext-core: {len(with_core)}")
    print(f"Projetos independentes: {len(without_core)}")

    print()
    print("⚠️ PROBLEMAS CRÍTICOS IDENTIFICADOS")
    print("-" * 60)

    projects_without_tests = [p for p in results if p["test_lines"] == 0]
    projects_without_code = [p for p in results if not p["has_actual_code"]]

    print(f"Projetos sem testes: {len(projects_without_tests)}")
    for p in projects_without_tests:
        print(f"  - {p['name']}")

    print(f"Projetos sem código real: {len(projects_without_code)}")
    for p in projects_without_code:
        print(f"  - {p['name']}")

    # Salva resultados em JSON para análise posterior
    with open("/home/marlonsc/flext/audit_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_projects": len(flext_projects),
                "total_src_lines": total_src_lines,
                "total_test_lines": total_test_lines,
                "empty_projects": len(empty_projects),
                "minimal_projects": len(minimal_projects),
                "basic_projects": len(basic_projects),
                "substantial_projects": len(substantial_projects),
                "large_projects": len(large_projects),
                "projects_with_flext_core": len(with_core),
                "projects_without_tests": len(projects_without_tests),
                "projects_without_code": len(projects_without_code)
            },
            "projects": results
        }, f, indent=2)

    print()
    print("💾 Resultados salvos em: audit_results.json")
    print()
    print("🎯 ESTIMATIVA REALISTA DE TRABALHO")
    print("-" * 60)

    functional_projects = len([p for p in results if p["src_lines"] > 100 and p["has_actual_code"]])
    coverage_percentage = (functional_projects / len(flext_projects)) * 100

    print(f"Projetos funcionais: {functional_projects}/{len(flext_projects)} ({coverage_percentage:.1f}%)")
    print("Trabalho restante para 100% coverage:")
    print(f"  - Implementar {len(projects_without_code)} projetos vazios")
    print(f"  - Adicionar testes para {len(projects_without_tests)} projetos")
    print(f"  - Integrar {len(without_core)} projetos ao flext-core")


if __name__ == "__main__":
    main()

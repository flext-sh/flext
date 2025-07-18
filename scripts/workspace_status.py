#!/usr/bin/env python3
"""
Script para mostrar status geral do workspace FLEXT.

Dashboard rápido usando flext_tools.
"""

import sys
from pathlib import Path

# Adiciona scripts ao path para importar flext_tools
sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import (
    Colors,
    ConflictAnalyzer,
    DependencyDiscovery,
    PoetryValidator,
    cached,
    print_colored,
)


def main():
    """Mostra status geral do workspace."""
    print_colored("📊 FLEXT Workspace Status", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    workspace_path = Path.cwd()

    # Detecta projetos
    projects = sorted(
        [
            p.parent
            for p in workspace_path.rglob("pyproject.toml")
            if not any(
                skip in str(p) for skip in ["archive", "backup", "node_modules", ".git"]
            )
        ],
    )

    if not projects:
        print_colored("❌ Nenhum projeto Python encontrado!", Colors.RED)
        return 1

    print_colored(f"📁 Workspace: {workspace_path.name}", Colors.CYAN)
    print_colored(f"📦 Projetos encontrados: {len(projects)}", Colors.CYAN)

    # Quick validation
    print_colored("\n🔍 Status Rápido:", Colors.BLUE)

    # Cache para performance
    @cached(namespace="status", ttl=300)
    def get_quick_status():
        validator = PoetryValidator()
        analyzer = ConflictAnalyzer()
        discovery = DependencyDiscovery()

        # Validação rápida
        validations = {}
        for project in projects[:10]:  # Apenas top 10 para status rápido
            validation = validator.validate_project(project)
            validations[project.name] = validation

        # Conflitos
        conflicts = analyzer.analyze_workspace_conflicts(workspace_path)

        # Sample de dependências faltantes (3 projetos)
        missing_sample = 0
        for project in projects[:3]:
            missing = discovery.discover_project_dependencies(project)
            missing_sample += sum(len(deps) for deps in missing.values())

        return validations, conflicts, missing_sample

    validations, conflicts, missing_sample = get_quick_status()

    # Status da validação
    valid_count = sum(1 for v in validations.values() if v["valid"])
    invalid_count = len(validations) - valid_count

    if invalid_count == 0:
        print_colored("  ✅ Poetry: Todos os projetos válidos", Colors.GREEN)
    else:
        print_colored(
            f"  ⚠️ Poetry: {invalid_count} projetos com problemas", Colors.YELLOW,
        )

    # Status de conflitos
    conflict_count = conflicts["stats"]["packages_with_conflicts"]
    if conflict_count == 0:
        print_colored("  ✅ Conflitos: Nenhum encontrado", Colors.GREEN)
    else:
        print_colored(f"  ⚠️ Conflitos: {conflict_count} pacotes", Colors.YELLOW)

    # Sample de dependências
    if missing_sample == 0:
        print_colored("  ✅ Dependências: Sample OK", Colors.GREEN)
    else:
        print_colored(
            f"  ⚠️ Dependências: ~{missing_sample} podem estar faltantes", Colors.YELLOW,
        )

    # Lista de projetos
    print_colored("\n📋 Projetos no workspace:", Colors.BLUE)

    for i, project in enumerate(projects):
        if i < 10:  # Top 10
            status_icon = (
                "✅" if validations.get(project.name, {}).get("valid", False) else "❓"
            )
            print(f"  {status_icon} {project.name}")
        elif i == 10:
            print(f"  ... e mais {len(projects) - 10} projetos")
            break

    # Top conflitos
    if conflicts["version_conflicts"]:
        print_colored("\n⚠️ Top 3 Conflitos:", Colors.YELLOW)
        for i, (package, data) in enumerate(
            list(conflicts["version_conflicts"].items())[:3],
        ):
            print(f"  {i + 1}. {package}: {len(data['projects'])} projetos")

    # Estatísticas gerais
    print_colored("\n📊 Estatísticas:", Colors.BLUE)
    stats = conflicts["stats"]
    print(f"  • Projetos: {len(projects)}")
    print(f"  • Pacotes únicos: {stats['unique_packages']}")
    print(f"  • Total dependências: {stats['total_dependencies']}")

    # Comandos úteis
    print_colored("\n🛠️ Comandos úteis:", Colors.CYAN)
    print("  • python quality_gateway.py        - Quality gateway completo")
    print("  • python sync_dependencies.py      - Sincronização completa")
    print("  • python discover_missing_deps.py  - Dependências faltantes")
    print("  • python analyze_who_blocks_updates.py - Análise de conflitos")
    print("  • python validate_poetry_projects.py   - Validação Poetry")

    # Cache stats
    if "-v" in sys.argv:
        stats = get_quick_status.cache_stats()
        print_colored(f"\n📊 Cache: {stats['hit_rate']}% hit rate", Colors.CYAN)

    return 0


if __name__ == "__main__":
    sys.exit(main())

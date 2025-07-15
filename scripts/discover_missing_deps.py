#!/usr/bin/env python3
"""
Script refatorado para descobrir dependências faltantes usando flext_tools.

Agora muito mais simples e reutilizável.
"""

import sys
from pathlib import Path

# Adiciona scripts ao path para importar flext_tools
sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import (
    Colors,
    DependencyDiscovery,
    PoetryOperations,
    cached,
    print_colored,
)


def main():
    """Descobre e adiciona dependências faltantes."""
    print_colored("🔍 Descobrindo dependências faltantes...\n", Colors.BLUE)

    # Inicializa descoberta
    discovery = DependencyDiscovery()

    # Detecta projetos no workspace - CORRIGIDO para evitar busca recursiva pesada
    workspace_path = Path.cwd()
    if workspace_path.name.startswith("flext-"):
        # Se estamos dentro de um projeto, analisa apenas este
        projects = (
            [workspace_path] if (workspace_path / "pyproject.toml").exists() else []
        )
    else:
        # Se estamos no workspace, busca projetos de primeiro nível apenas
        projects = sorted(
            [
                p
                for p in workspace_path.iterdir()
                if p.is_dir()
                and (p / "pyproject.toml").exists()
                and not any(
                    skip in p.name
                    for skip in [
                        "archive",
                        "backup",
                        "node_modules",
                        ".git",
                        ".venv",
                        "cookiecutter",
                    ]
                )
            ]
        )

    if not projects:
        print_colored("❌ Nenhum projeto Python encontrado!", Colors.RED)
        return 1

    print_colored(f"📁 Encontrados {len(projects)} projetos\n", Colors.CYAN)

    # Cache para performance
    @cached(namespace="discovery", ttl=300)
    def discover_project(project_path: Path):
        return discovery.discover_project_dependencies(
            project_path, include_dev=True, include_test=True
        )

    # Analisa cada projeto
    total_missing = 0
    projects_with_missing = []

    for project in projects:
        print_colored(f"🔍 Analisando {project.name}...", Colors.CYAN)

        missing_deps = discover_project(project)

        # Conta total
        project_total = sum(len(deps) for deps in missing_deps.values())

        if project_total > 0:
            total_missing += project_total
            projects_with_missing.append((project, missing_deps))
            print_colored(f"  ⚠️ {project_total} dependências faltantes", Colors.YELLOW)
        else:
            print_colored("  ✅ Todas as dependências declaradas", Colors.GREEN)

    # Resumo
    print_colored("\n📊 Resumo:", Colors.BLUE)
    print_colored(f"  Total de dependências faltantes: {total_missing}", Colors.CYAN)
    print_colored(
        f"  Projetos afetados: {len(projects_with_missing)}/{len(projects)}",
        Colors.CYAN,
    )

    if not projects_with_missing:
        print_colored(
            "\n✨ Todos os projetos estão com dependências completas!", Colors.GREEN
        )
        return 0

    # Pergunta se quer adicionar
    print_colored("\n💡 Deseja adicionar as dependências faltantes?", Colors.YELLOW)
    print_colored("   (Use --dry-run para simular)", Colors.CYAN)

    dry_run = "--dry-run" in sys.argv
    auto = "--auto" in sys.argv

    if not auto and not dry_run:
        response = input("\nAdicionar dependências? (s/N): ")
        if response.lower() not in {"s", "sim", "y", "yes"}:
            print_colored("\n❌ Operação cancelada", Colors.YELLOW)
            return 0

    # Adiciona dependências
    poetry_ops = PoetryOperations(dry_run=dry_run)

    for project, missing_deps in projects_with_missing:
        print_colored(f"\n📦 Processando {project.name}...", Colors.BLUE)

        added = poetry_ops.add_dependencies(
            project, missing_deps, auto_confirm=auto or dry_run
        )

        # Mostra resultado
        total_added = sum(len(deps) for deps in added.values())
        if total_added > 0:
            action = "seriam adicionadas" if dry_run else "adicionadas"
            print_colored(f"  ✅ {total_added} dependências {action}", Colors.GREEN)
        else:
            print_colored("  ⚠️ Nenhuma dependência adicionada", Colors.YELLOW)

    # Mostra cache stats se verboso
    if "-v" in sys.argv or "--verbose" in sys.argv:
        stats = discover_project.cache_stats()
        print_colored(
            f"\n📊 Cache: {stats['hits']} hits, {stats['misses']} misses ({stats['hit_rate']}%)",
            Colors.CYAN,
        )

    print_colored("\n✨ Concluído!", Colors.GREEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())

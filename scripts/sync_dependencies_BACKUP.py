#!/usr/bin/env python3
"""
Script principal refatorado para sincronização de dependências.

Agora usa flext_tools para operações modulares e eficientes.
"""

import sys
from pathlib import Path

# Adiciona scripts ao path para importar flext_tools
sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import (
    Colors,
    ConflictAnalyzer,
    DependencyDiscovery,
    PoetryOperations,
    PoetryValidator,
    cached,
    print_colored,
)


def main():
    """Sincronização completa de dependências do workspace."""
    print_colored("🔄 Sincronização de dependências FLEXT", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    # Configurações de linha de comando
    dry_run = "--dry-run" in sys.argv
    auto = "--auto" in sys.argv
    validate_only = "--validate" in sys.argv
    conflicts_only = "--conflicts" in sys.argv

    if dry_run:
        print_colored("⚠️ Modo DRY-RUN: Nenhuma modificação será feita", Colors.YELLOW)

    # Workspace path
    workspace_path = Path.cwd().parent  # /home/marlonsc/flext

    # Detecta projetos
    projects = sorted(
        [
            p.parent
            for p in workspace_path.rglob("pyproject.toml")
            if not any(
                skip in str(p)
                for skip in [
                    "archive",
                    "backup",
                    "node_modules",
                    ".git",
                    ".venv",
                    "cookiecutter",
                ]
            )
        ],
    )

    if not projects:
        print_colored("❌ Nenhum projeto Python encontrado!", Colors.RED)
        return 1

    print_colored(f"📁 Encontrados {len(projects)} projetos\n", Colors.CYAN)

    # 1. VALIDAÇÃO DE PROJETOS POETRY
    print_colored("1️⃣ Validando configurações Poetry...", Colors.BLUE)
    validator = PoetryValidator()

    @cached(namespace="validation", ttl=300)
    def validate_workspace():
        return validator.validate_workspace(workspace_path)

    validations = validate_workspace()

    # Conta projetos válidos/inválidos
    valid_count = sum(1 for v in validations.values() if v["valid"])
    invalid_count = len(validations) - valid_count

    print_colored(f"  ✅ Projetos válidos: {valid_count}", Colors.GREEN)
    if invalid_count > 0:
        print_colored(f"  ❌ Projetos inválidos: {invalid_count}", Colors.RED)

        # Mostra erros críticos
        for project, validation in validations.items():
            if not validation["valid"]:
                print_colored(f"    • {project}:", Colors.RED)
                for error in validation["errors"]:
                    print(f"      - {error}")

    if validate_only:
        return 0 if invalid_count == 0 else 1

    # 2. ANÁLISE DE CONFLITOS
    print_colored("\n2️⃣ Analisando conflitos de versão...", Colors.BLUE)
    analyzer = ConflictAnalyzer()

    @cached(namespace="conflicts", ttl=600)
    def get_conflicts():
        return analyzer.analyze_workspace_conflicts(workspace_path)

    conflicts = get_conflicts()
    stats = conflicts["stats"]

    print_colored(
        f"  📊 {stats['packages_with_conflicts']} pacotes com conflitos", Colors.CYAN,
    )
    print_colored(
        f"  🚫 {stats['blocking_packages']} pacotes bloqueadores", Colors.CYAN,
    )

    # Mostra top 5 conflitos
    if conflicts["version_conflicts"]:
        print_colored("\n  ⚠️ Top 5 conflitos:", Colors.YELLOW)
        for i, (package, data) in enumerate(
            list(conflicts["version_conflicts"].items())[:5],
        ):
            print(f"    {i + 1}. {package}: {len(data['projects'])} projetos")

    if conflicts_only:
        # Gera relatório de conflitos
        if "--report" in sys.argv:
            report_path = Path("conflict_report.md")
            report = analyzer.generate_conflict_report(conflicts)
            with Path(report_path).open("w", encoding="utf-8") as f:
                f.write(report)
            print_colored(f"\n📄 Relatório salvo em: {report_path}", Colors.GREEN)
        return 0

    # 3. DESCOBERTA DE DEPENDÊNCIAS FALTANTES
    print_colored("\n3️⃣ Descobrindo dependências faltantes...", Colors.BLUE)
    discovery = DependencyDiscovery()

    @cached(namespace="discovery", ttl=300)
    def discover_project_deps(project_path: Path):
        return discovery.discover_project_dependencies(
            project_path, include_dev=True, include_test=True,
        )

    all_missing = {}
    total_missing = 0

    for project in projects:
        missing = discover_project_deps(project)
        project_total = sum(len(deps) for deps in missing.values())

        if project_total > 0:
            all_missing[project] = missing
            total_missing += project_total
            print_colored(
                f"  • {project.name}: {project_total} faltantes", Colors.YELLOW,
            )
        else:
            print_colored(f"  • {project.name}: ✅ completo", Colors.GREEN)

    print_colored(
        f"\n  📊 Total: {total_missing} dependências faltantes em {len(all_missing)} projetos",
        Colors.CYAN,
    )

    # 4. ADIÇÃO DE DEPENDÊNCIAS
    if all_missing and not dry_run:
        print_colored("\n4️⃣ Adicionando dependências faltantes...", Colors.BLUE)

        if not auto:
            response = input("\nDeseja adicionar as dependências faltantes? (s/N): ")
            if response.lower() not in {"s", "sim", "y", "yes"}:
                print_colored("❌ Operação cancelada", Colors.YELLOW)
                return 0

        poetry_ops = PoetryOperations(dry_run=False)

        added_summary = {"runtime": 0, "test": 0, "dev": 0}

        for project, missing_deps in all_missing.items():
            print_colored(f"\n  📦 Processando {project.name}...", Colors.CYAN)

            added = poetry_ops.add_dependencies(
                project, missing_deps, auto_confirm=auto,
            )

            # Atualiza contadores
            for category, deps in added.items():
                added_summary[category] += len(deps)

        # Resumo final
        total_added = sum(added_summary.values())
        print_colored(f"\n  ✅ {total_added} dependências adicionadas:", Colors.GREEN)
        for category, count in added_summary.items():
            if count > 0:
                print(f"    • {category}: {count}")

    elif all_missing and dry_run:
        print_colored(
            "\n4️⃣ Simulação: dependências que seriam adicionadas", Colors.YELLOW,
        )
        for project, missing_deps in all_missing.items():
            project_total = sum(len(deps) for deps in missing_deps.values())
            print(f"  • {project.name}: {project_total} dependências")

    # 5. RESOLUÇÃO DE CONFLITOS (se solicitado)
    if conflicts["suggested_resolutions"] and "--resolve" in sys.argv:
        print_colored("\n5️⃣ Aplicando resoluções de conflitos...", Colors.BLUE)

        if not auto and not dry_run:
            print_colored(
                "⚠️ Isto pode alterar versões de dependências existentes!", Colors.YELLOW,
            )
            response = input("Deseja continuar? (s/N): ")
            if response.lower() not in {"s", "sim", "y", "yes"}:
                print_colored("❌ Resolução de conflitos cancelada", Colors.YELLOW)
                return 0

        poetry_ops = PoetryOperations(dry_run=dry_run)
        resolved_count = 0

        for project in projects:
            project_resolutions = {}

            # Filtra resoluções aplicáveis a este projeto
            for package, resolution in conflicts["suggested_resolutions"].items():
                # Verifica se projeto tem esse pacote
                if package in conflicts.get("version_conflicts", {}):
                    project_data = conflicts["version_conflicts"][package]["projects"]
                    if project.name in project_data:
                        project_resolutions[package] = resolution

            if project_resolutions:
                success = poetry_ops.update_dependency_versions(
                    project, project_resolutions,
                )
                if success:
                    resolved_count += len(project_resolutions)
                    print_colored(
                        f"  ✅ {project.name}: {len(project_resolutions)} resoluções aplicadas",
                        Colors.GREEN,
                    )

        action = "seriam aplicadas" if dry_run else "aplicadas"
        print_colored(
            f"\n  📊 Total: {resolved_count} resoluções {action}", Colors.CYAN,
        )

    # Estatísticas finais
    print_colored("\n✨ Sincronização concluída!", Colors.GREEN)

    if "-v" in sys.argv or "--verbose" in sys.argv:
        print_colored("\n📊 Estatísticas de cache:", Colors.CYAN)
        for func_name, func in [
            ("validation", validate_workspace),
            ("conflicts", get_conflicts),
            ("discovery", discover_project_deps),
        ]:
            if hasattr(func, "cache_stats"):
                stats = func.cache_stats()
                print(f"  • {func_name}: {stats['hit_rate']}% hit rate")

    # Dicas finais
    print_colored("\n💡 Opções disponíveis:", Colors.CYAN)
    print("  • --dry-run: Simula operações sem modificar")
    print("  • --auto: Confirma automaticamente")
    print("  • --validate: Apenas valida projetos")
    print("  • --conflicts: Apenas analisa conflitos")
    print("  • --resolve: Aplica resoluções de conflitos")
    print("  • --report: Gera relatório de conflitos")
    print("  • -v: Mostra estatísticas detalhadas")

    return 0


if __name__ == "__main__":
    sys.exit(main())

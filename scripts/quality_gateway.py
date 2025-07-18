#!/usr/bin/env python3
"""
Script refatorado para quality gateway usando flext_tools.

Combina validação Poetry, análise de conflitos e descoberta de dependências.
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
    """Quality gateway completo para o workspace."""
    print_colored("🛡️ FLEXT Quality Gateway", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    # Configurações
    strict_mode = "--strict" in sys.argv
    fix_mode = "--fix" in sys.argv

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

    print_colored(f"📁 Analisando {len(projects)} projetos\n", Colors.CYAN)

    # Contadores de qualidade
    quality_score = 0
    max_score = 0
    issues_found = []

    # 1. VALIDAÇÃO POETRY
    print_colored("1️⃣ Validação Poetry", Colors.BLUE)
    validator = PoetryValidator()

    @cached(namespace="validation", ttl=300)
    def validate_workspace():
        return validator.validate_workspace(workspace_path)

    validations = validate_workspace()

    valid_count = sum(1 for v in validations.values() if v["valid"])
    invalid_count = len(validations) - valid_count

    max_score += 30  # 30 pontos para validação
    if invalid_count == 0:
        quality_score += 30
        print_colored(
            f"  ✅ Todos os {len(validations)} projetos são válidos (+30 pontos)",
            Colors.GREEN,
        )
    else:
        partial_score = int(30 * (valid_count / len(validations)))
        quality_score += partial_score
        print_colored(
            f"  ⚠️ {valid_count}/{len(validations)} projetos válidos (+{partial_score} pontos)",
            Colors.YELLOW,
        )

        issues_found.append(f"Poetry: {invalid_count} projetos inválidos")

        # Mostra erros críticos
        for project, validation in validations.items():
            if not validation["valid"]:
                print_colored(
                    f"    ❌ {project}: {len(validation['errors'])} erros", Colors.RED,
                )

    # 2. ANÁLISE DE CONFLITOS
    print_colored("\n2️⃣ Análise de Conflitos", Colors.BLUE)
    analyzer = ConflictAnalyzer()

    @cached(namespace="conflicts", ttl=600)
    def get_conflicts():
        return analyzer.analyze_workspace_conflicts(workspace_path)

    conflicts = get_conflicts()
    stats = conflicts["stats"]

    max_score += 25  # 25 pontos para conflitos
    conflict_count = stats["packages_with_conflicts"]

    if conflict_count == 0:
        quality_score += 25
        print_colored(
            "  ✅ Nenhum conflito de versão encontrado (+25 pontos)", Colors.GREEN,
        )
    else:
        # Desconta pontos baseado no número de conflitos
        deduction = min(25, conflict_count * 2)
        partial_score = 25 - deduction
        quality_score += partial_score
        print_colored(
            f"  ⚠️ {conflict_count} pacotes com conflitos (+{partial_score} pontos)",
            Colors.YELLOW,
        )

        issues_found.append(f"Conflitos: {conflict_count} pacotes")

        # Mostra top 3 conflitos
        top_conflicts = list(conflicts["version_conflicts"].items())[:3]
        for package, data in top_conflicts:
            print_colored(
                f"    ⚠️ {package}: {len(data['projects'])} projetos", Colors.YELLOW,
            )

    # 3. DEPENDÊNCIAS FALTANTES
    print_colored("\n3️⃣ Dependências Faltantes", Colors.BLUE)
    discovery = DependencyDiscovery()

    @cached(namespace="discovery", ttl=300)
    def discover_project_deps(project_path: Path):
        return discovery.discover_project_dependencies(
            project_path, include_dev=True, include_test=True,
        )

    total_missing = 0
    projects_with_missing = 0

    for project in projects:
        missing = discover_project_deps(project)
        project_total = sum(len(deps) for deps in missing.values())

        if project_total > 0:
            total_missing += project_total
            projects_with_missing += 1

    max_score += 25  # 25 pontos para dependências
    if total_missing == 0:
        quality_score += 25
        print_colored(
            "  ✅ Todas as dependências estão declaradas (+25 pontos)", Colors.GREEN,
        )
    else:
        # Desconta pontos baseado no número de dependências faltantes
        deduction = min(25, total_missing)
        partial_score = 25 - deduction
        quality_score += partial_score
        print_colored(
            f"  ⚠️ {total_missing} dependências faltantes em {projects_with_missing} projetos (+{partial_score} pontos)",
            Colors.YELLOW,
        )

        issues_found.append(f"Dependências: {total_missing} faltantes")

    # 4. ESTRUTURA DE ARQUIVOS
    print_colored("\n4️⃣ Estrutura de Arquivos", Colors.BLUE)

    structure_score = 0
    max_structure = 20

    # Verifica estruturas básicas
    checks = [
        ("Makefile na raiz", workspace_path / "Makefile"),
        ("pyproject.toml na raiz", workspace_path / "pyproject.toml"),
        ("README.md na raiz", workspace_path / "README.md"),
        (".gitignore na raiz", workspace_path / ".gitignore"),
    ]

    for check_name, path in checks:
        if path.exists():
            structure_score += 5
            print_colored(f"  ✅ {check_name}", Colors.GREEN)
        else:
            print_colored(f"  ❌ {check_name}", Colors.RED)
            issues_found.append(f"Estrutura: {check_name} ausente")

    quality_score += structure_score
    max_score += max_structure

    # RESULTADO FINAL
    print_colored("\n📊 RESULTADO DO QUALITY GATEWAY", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    percentage = (quality_score / max_score) * 100

    print(f"Pontuação: {quality_score}/{max_score} ({percentage:.1f}%)")

    # Determina status baseado na pontuação
    if percentage >= 90:
        status = "EXCELLENT"
        color = Colors.GREEN
        icon = "🏆"
    elif percentage >= 75:
        status = "GOOD"
        color = Colors.GREEN
        icon = "✅"
    elif percentage >= 60:
        status = "FAIR"
        color = Colors.YELLOW
        icon = "⚠️"
    else:
        status = "POOR"
        color = Colors.RED
        icon = "❌"

    print_colored(f"\nStatus: {icon} {status}", color)

    # Lista problemas encontrados
    if issues_found:
        print_colored("\n🔍 Problemas Encontrados:", Colors.YELLOW)
        for issue in issues_found:
            print(f"  • {issue}")

    # Recomendações
    print_colored("\n💡 Recomendações:", Colors.CYAN)

    if invalid_count > 0:
        print(
            "  • Execute 'python validate_poetry_projects.py' para ver detalhes dos erros Poetry",
        )

    if conflict_count > 0:
        print(
            "  • Execute 'python analyze_who_blocks_updates.py --suggest' para ver resoluções",
        )

    if total_missing > 0:
        print(
            "  • Execute 'python discover_missing_deps.py --dry-run' para ver dependências faltantes",
        )

    if fix_mode:
        print_colored(
            "\n🔧 Modo de correção automática não implementado ainda", Colors.YELLOW,
        )
        print("  • Use os scripts individuais para correções específicas")

    # Mostra cache stats se verboso
    if "-v" in sys.argv:
        print_colored("\n📊 Estatísticas de Cache:", Colors.CYAN)
        for func_name, func in [
            ("validation", validate_workspace),
            ("conflicts", get_conflicts),
            ("discovery", discover_project_deps),
        ]:
            if hasattr(func, "cache_stats"):
                stats = func.cache_stats()
                print(f"  • {func_name}: {stats['hit_rate']}% hit rate")

    # Opções disponíveis
    print_colored("\n💡 Opções:", Colors.CYAN)
    print("  • --strict: Modo rigoroso (falha com qualquer problema)")
    print("  • --fix: Modo de correção automática (futuro)")
    print("  • -v: Estatísticas detalhadas")

    # Status de saída
    if strict_mode and percentage < 100:
        print_colored(
            f"\n❌ FALHOU no modo rigoroso ({percentage:.1f}% < 100%)", Colors.RED,
        )
        return 1
    if percentage < 60:
        print_colored(
            f"\n❌ Qualidade insuficiente ({percentage:.1f}% < 60%)", Colors.RED,
        )
        return 1
    print_colored("\n✅ Quality gateway aprovado!", Colors.GREEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())

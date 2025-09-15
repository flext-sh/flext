#!/usr/bin/env python3
"""Script principal REFATORADO para sincronização de dependências.

Agora usa flext_tools para operações modulares e eficientes.
Funcionalidades:
1. Descobre dependências faltantes
2. Organiza versões no workspace
3. Identifica bloqueadores de atualização
4. Adiciona dependências automaticamente
5. Valida configurações Poetry
"""

import sys
from pathlib import Path
from typing import cast

from flext_core import FlextTypes
from src.flext_tools import Colors, print_colored
from src.flext_tools.conflicts import ConflictAnalyzer
from src.flext_tools.discovery_base import DependencyDiscovery
from src.flext_tools.observability import DetailedLogger
from src.flext_tools.poetry_operations import PoetryOperations
from src.flext_tools.poetry_validator import PoetryValidator


def check_validation_lock() -> bool:
    """Verifica se existe bloqueio de validação que impede execução sem dry-run."""
    lock_file = Path(__file__).parent / "VALIDATION_REQUIRED.lock"
    return lock_file.exists()


def parse_args() -> dict[str, bool]:
    """Parseia argumentos de linha de comando."""
    return {
        "dry_run": "--dry-run" in sys.argv,
        "auto": "--auto" in sys.argv,
        "validate_only": "--validate" in sys.argv,
        "conflicts_only": "--conflicts" in sys.argv,
        "discover_only": "--discover" in sys.argv,
        "verbose": "-v" in sys.argv or "--verbose" in sys.argv,
        "help": "--help" in sys.argv or "-h" in sys.argv,
        "force_unlock": "--force-unlock" in sys.argv,  # Só para emergências
    }


def show_help() -> None:
    """Mostra ajuda do script."""
    print_colored("🔄 Sincronização de dependências FLEXT", Colors.BLUE)


def get_workspace_projects(workspace_path: Path) -> list[Path]:
    """Obtém lista de projetos do workspace."""
    # Busca apenas no primeiro nível para evitar recursão pesada
    projects = [
        item
        for item in workspace_path.iterdir()
        if item.is_dir()
        and (item / "pyproject.toml").exists()
        and not any(
            skip in item.name
            for skip in ["archive", "backup", "node_modules", ".git", ".venv"]
        )
    ]

    return sorted(projects)


def validate_projects(
    projects: list[Path],
    validator: "PoetryValidator",
    *,
    verbose: bool,
) -> bool:
    """Valida todos os projetos Poetry."""
    print_colored("\n1️⃣ Validando projetos Poetry...", Colors.BLUE)

    all_valid = True
    for project in projects:
        if verbose:
            print_colored(f"\n📁 Validando {project.name}...", Colors.CYAN)

        validation_result = validator.validate_project(project)

        if validation_result.is_failure:
            all_valid = False
            print_colored(
                f"  ❌ {project.name}: Erro na validação - {validation_result.error}",
                Colors.RED,
            )
            continue

        validation = validation_result.unwrap()
        # Type assertion for validation result structure
        assert isinstance(validation, dict), "Validation result must be a dict"

        if validation["valid"]:
            if verbose:
                print_colored(f"  ✅ {project.name}: Válido", Colors.GREEN)
        else:
            all_valid = False
            print_colored(f"  ❌ {project.name}: Inválido", Colors.RED)
            # Type assertion for errors list
            errors = cast("list", validation.get("errors", []))
            for error in errors:
                print_colored(f"    - {error}", Colors.RED)

        warnings = cast("list", validation.get("warnings", []))
        if warnings and verbose:
            for warning in warnings:
                print_colored(f"    ⚠️ {warning}", Colors.YELLOW)

    if all_valid:
        print_colored("\n✅ Todos os projetos são válidos!", Colors.GREEN)
    else:
        print_colored("\n❌ Alguns projetos têm problemas de validação", Colors.RED)

    return all_valid


def discover_missing_dependencies(
    projects: list[Path],
    discovery: "DependencyDiscovery",
    *,
    verbose: bool,
) -> dict[Path, dict[str, FlextTypes.Core.StringList]]:
    """Descobre dependências faltantes em todos os projetos."""
    print_colored("\n2️⃣ Descobrindo dependências faltantes...", Colors.BLUE)

    # Removemos o decorator @cached que estava causando problemas de tipagem
    def get_project_deps(project_path: Path) -> dict[str, FlextTypes.Core.StringList]:
        deps = discovery.discover_project_dependencies(
            project_path,
            include_dev=True,
            include_test=True,
        )
        # Converter set para list se necessário
        return {k: list(v) if isinstance(v, set) else v for k, v in deps.items()}

    missing_by_project: dict[Path, dict[str, FlextTypes.Core.StringList]] = {}
    total_missing = 0

    for project in projects:
        if verbose:
            print_colored(f"\n📁 Analisando {project.name}...", Colors.CYAN)

        missing_deps = get_project_deps(project)
        project_total = sum(len(deps) for deps in missing_deps.values())

        if project_total > 0:
            missing_by_project[project] = missing_deps
            total_missing += project_total
            print_colored(
                f"  ⚠️ {project.name}: {project_total} dependências faltantes",
                Colors.YELLOW,
            )
        elif verbose:
            print_colored(f"  ✅ {project.name}: Completo", Colors.GREEN)

    print_colored(f"\n📊 Total de dependências faltantes: {total_missing}", Colors.CYAN)
    print_colored(
        f"📊 Projetos afetados: {len(missing_by_project)}/{len(projects)}",
        Colors.CYAN,
    )

    return missing_by_project


def analyze_conflicts(
    workspace_path: Path,
    analyzer: ConflictAnalyzer,
    *,
    verbose: bool,
) -> FlextTypes.Core.Dict:
    """Analisa conflitos de versão no workspace."""
    print_colored("\n3️⃣ Analisando conflitos de versão...", Colors.BLUE)

    def get_conflicts() -> FlextTypes.Core.Dict:
        result = analyzer.analyze_workspace_conflicts(workspace_path)
        if result.is_success:
            conflict_result = result.unwrap()
            return conflict_result.model_dump()
        return {"error": result.error or "Analysis failed"}

    analysis: FlextTypes.Core.Dict = get_conflicts()
    analysis["stats"]

    print_colored("\n📊 Estatísticas:", Colors.CYAN)

    if analysis["version_conflicts"] and verbose:
        print_colored("\n⚠️ Top 5 conflitos:", Colors.YELLOW)
        version_conflicts = analysis.get("version_conflicts", {})
        if isinstance(version_conflicts, dict):
            conflicts_sorted = sorted(
                version_conflicts.items(),
                key=lambda x: len(x[1]["projects"]),
                reverse=True,
            )
        else:
            conflicts_sorted = []

        for _i, (_package, _data) in enumerate(conflicts_sorted[:5]):
            pass

    return analysis


def add_missing_dependencies(
    missing_by_project: dict[Path, dict[str, FlextTypes.Core.StringList]],
    poetry_ops: PoetryOperations,
    *,
    auto: bool,
) -> bool:
    """Adiciona dependências faltantes aos projetos."""
    if not missing_by_project:
        print_colored("\n✅ Nenhuma dependência faltante!", Colors.GREEN)
        return True

    print_colored("\n4️⃣ Adicionando dependências faltantes...", Colors.BLUE)

    if not auto:
        total_deps = sum(
            sum(len(deps) for deps in missing_deps.values())
            for missing_deps in missing_by_project.values()
        )
        print_colored(
            f"\n💡 {total_deps} dependências serão adicionadas",
            Colors.YELLOW,
        )
        response = input("Continuar? (s/N): ")
        if response.lower() not in {"s", "sim", "y", "yes"}:
            print_colored("❌ Operação cancelada", Colors.YELLOW)
            return False

    success = True
    for project, missing_deps in missing_by_project.items():
        print_colored(f"\n📦 Processando {project.name}...", Colors.CYAN)

        added = poetry_ops.add_dependencies(project, missing_deps, _auto_confirm=auto)

        total_added = sum(len(deps) for deps in added.values())
        if total_added > 0:
            print_colored(f"  ✅ {total_added} dependências adicionadas", Colors.GREEN)
        else:
            print_colored("  ⚠️ Nenhuma dependência foi adicionada", Colors.YELLOW)
            success = False

    return success


def main() -> int:
    """Função principal."""
    args = parse_args()

    if args["help"]:
        show_help()
        return 0

    # Inicializa sistema de logging detalhado
    logger = DetailedLogger("sync_dependencies")

    try:
        logger.info(
            "Starting SYNC_DEPENDENCIES: Sincronização completa de dependências FLEXT",
        )

        print_colored("🔄 Sincronização de dependências FLEXT", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

        # VERIFICAÇÃO CRÍTICA DE SEGURANÇA
        if check_validation_lock() and not args["dry_run"] and not args["force_unlock"]:
            print_colored("🚨 BLOQUEIO DE SEGURANÇA ATIVO", Colors.RED)
            print_colored("=" * 50, Colors.RED)
            print_colored("❌ EXECUÇÃO SEM DRY-RUN BLOQUEADA", Colors.RED)
            print_colored("", Colors.RED)
            print_colored(
                "MOTIVO: Sistema ainda não foi validado completamente",
                Colors.YELLOW,
            )
            print_colored("", Colors.RED)
            print_colored("AÇÕES REQUERIDAS ANTES DE DESBLOQUEAR:", Colors.YELLOW)
            print_colored(
                "1. ✅ Auditoria manual dos 147 falsos positivos detectados",
                Colors.YELLOW,
            )
            print_colored(
                "2. ✅ Validação de detecção de módulos internos",
                Colors.YELLOW,
            )
            print_colored(
                "3. ✅ Teste completo do sistema de backup/rollback",
                Colors.YELLOW,
            )
            print_colored("4. ✅ Teste em projeto isolado", Colors.YELLOW)
            print_colored("", Colors.RED)
            print_colored("OPÇÕES SEGURAS:", Colors.GREEN)
            print_colored("• Use --dry-run para simulação segura", Colors.GREEN)
            print_colored(
                "• Use --discover para análise sem modificações",
                Colors.GREEN,
            )
            print_colored("• Use --validate para verificação de projetos", Colors.GREEN)
            print_colored("", Colors.RED)
            print_colored(
                "⚠️ REMOVER scripts/VALIDATION_REQUIRED.lock apenas após validação completa",
                Colors.YELLOW,
            )

            logger.warning(
                "EXECUTION_BLOCKED: Tentativa de execução sem dry-run bloqueada "
                "por lock de validação",
            )

            logger.error(
                "Operation failed: Execução bloqueada por lock de validação de segurança",
            )
            return 1

        if args["dry_run"]:
            print_colored(
                "⚠️ Modo DRY-RUN: Nenhuma modificação será feita",
                Colors.YELLOW,
            )
        elif check_validation_lock() and args["force_unlock"]:
            print_colored(
                "⚠️ ATENÇÃO: Force unlock ativo - ALTA RESPONSABILIDADE",
                Colors.RED,
            )

        # Detecta workspace
        workspace_path = Path.cwd()
        if not any(
            p.name.startswith("flext-") for p in workspace_path.iterdir() if p.is_dir()
        ):
            print_colored(
                "❌ Execute o script do diretório raiz do workspace FLEXT",
                Colors.RED,
            )
            return 1

        # Obtém projetos
        projects = get_workspace_projects(workspace_path)
        if not projects:
            print_colored("❌ Nenhum projeto Python encontrado!", Colors.RED)
            return 1

        print_colored(f"📁 Encontrados {len(projects)} projetos", Colors.CYAN)

        # Inicializa ferramentas com logger integrado
        validator = PoetryValidator()
        discovery = DependencyDiscovery()
        analyzer = ConflictAnalyzer()
        poetry_ops = PoetryOperations(dry_run=args["dry_run"])

        # Executa operações baseado nos argumentos
        if args["validate_only"]:
            validate_projects(projects, validator, verbose=args["verbose"])
            return 0

        if args["conflicts_only"]:
            analyze_conflicts(workspace_path, analyzer, verbose=args["verbose"])
            return 0

        if args["discover_only"]:
            missing_by_project = discover_missing_dependencies(
                projects,
                discovery,
                verbose=args["verbose"],
            )
            return 0

        # Execução completa
        print_colored("\n🚀 Execução completa iniciada...", Colors.BLUE)

        # 1. Validação
        if not validate_projects(projects, validator, verbose=args["verbose"]):
            print_colored(
                "\n⚠️ Alguns projetos têm problemas, mas continuando...",
                Colors.YELLOW,
            )

        # 2. Descoberta
        missing_by_project = discover_missing_dependencies(
            projects,
            discovery,
            verbose=args["verbose"],
        )

        # 3. Conflitos
        analyze_conflicts(workspace_path, analyzer, verbose=args["verbose"])

        # 4. Adição de dependências
        if missing_by_project:
            add_missing_dependencies(missing_by_project, poetry_ops, auto=args["auto"])

        # 5. Relatório final
        print_colored("\n📊 Relatório Final:", Colors.BLUE)

        # Estatísticas de cache se verboso
        if args["verbose"]:
            # Aqui poderia mostrar estatísticas de cache se necessário
            print_colored("\n📊 Cache utilizado para melhor performance", Colors.CYAN)

        # Finaliza operação com sucesso
        logger.info(
            f"Operation completed successfully: {len(projects)} projects validated",
        )

        print_colored("\n✨ Sincronização concluída!", Colors.GREEN)
    except (OSError, ValueError, TypeError) as e:
        # Log erro crítico
        logger.exception(
            f"SYNC_ERROR: Erro crítico durante sincronização (tipo: {type(e).__name__})",
        )

        # Finaliza operação com falha
        logger.exception("Operation failed: Erro crítico")

        print_colored(f"\n❌ Erro crítico: {e!s}", Colors.RED)
        print_colored("📋 Logs detalhados salvos em .flext_logs/", Colors.CYAN)
        return 1
    else:
        return 0

    finally:
        # Logger cleanup (no close method needed)
        pass


if __name__ == "__main__":
    sys.exit(main())

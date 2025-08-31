#!/usr/bin/env python3
"""MyPy Analyzer Script - PEP 518 Compliant.

Script centralizado para análise MyPy em workspace multi-projeto.
Segue PEP 518 (pyproject.toml), PEP 420 (namespace packages) e melhores práticas.

Usage:
    python scripts/mypy_analyzer.py --workspace     # Analisa workspace
    python scripts/mypy_analyzer.py --all-projects  # Analisa todos projetos
    python scripts/mypy_analyzer.py --comprehensive # Análise completa
    python scripts/mypy_analyzer.py --project=name  # Analisa projeto específico
"""

from __future__ import annotations

import argparse
import operator
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from mypy import api as mypy_api


def _run_mypy_api(args: list[str]) -> tuple[int, str, str]:
    """Run MyPy using its Python API and return (exit_code, stdout, stderr)."""
    try:
        stdout, stderr, exit_status = mypy_api.run(args)
        return int(exit_status), stdout, stderr
    except Exception as e:
        return 1, "", f"MyPy API execution failed: {e}"


def parse_mypy_errors(output: str) -> list[dict[str, object]]:
    """Parse MyPy output to extract structured error information."""
    errors = []

    # Regex para capturar erros MyPy
    error_pattern = r"([^:]+):(\d+): error: (.+?) \[([^\]]+)\]"

    for line in output.split("\n"):
        match = re.match(error_pattern, line)
        if match:
            file_path, line_num, message, error_code = match.groups()
            errors.append(
                {
                    "file": file_path.strip(),
                    "line": int(line_num),
                    "message": message.strip(),
                    "error_code": error_code.strip(),
                    "project": get_project_from_path(file_path),
                },
            )

    return errors


def get_project_from_path(file_path: str) -> str:
    """Extract project name from file path."""
    path_parts = Path(file_path).parts

    # Se está em um subdiretório de projeto
    for part in path_parts:
        if part.startswith(("flext-", "client-a-", "client-b-", "flexcore")):
            return part

    # Se está no workspace raiz
    return "workspace"


def analyze_project_with_stats(
    project_path: Path,
) -> tuple[int, list[dict[str, object]]]:
    """Analisa projeto específico e retorna estatísticas detalhadas."""
    exit_code, stdout, stderr = _run_mypy_api([str(project_path)])

    errors = parse_mypy_errors(stdout + stderr)

    if stdout and not errors:  # Se há output mas não são erros
        pass
    if stderr and "error:" not in stderr:  # Se há stderr mas não são erros
        pass

    return exit_code, errors


def analyze_workspace_with_stats() -> tuple[int, list[dict[str, object]]]:
    """Analisa workspace e retorna estatísticas detalhadas."""
    workspace_root = Path(__file__).parent.parent

    # Verificar quais diretórios existem para análise
    dirs_to_analyze = []
    for dir_name in ["src", "tests", "scripts", "examples"]:
        dir_path = workspace_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            dirs_to_analyze.append(dir_name)

    if not dirs_to_analyze:
        return 1, []

    # Build absolute paths for analysis to avoid cwd dependency
    abs_args = [str(workspace_root / d) for d in dirs_to_analyze]
    exit_code, stdout, stderr = _run_mypy_api(abs_args)

    errors = parse_mypy_errors(stdout + stderr)

    if stdout and not errors:  # Se há output mas não são erros
        pass
    if stderr and "error:" not in stderr:  # Se há stderr mas não são erros
        pass

    return exit_code, errors


def analyze_workspace() -> int:
    """Analisa o workspace principal seguindo PEP 518."""
    workspace_root = Path(__file__).parent.parent

    # Verificar quais diretórios existem para análise
    dirs_to_analyze = []
    for dir_name in ["src", "tests", "scripts", "examples"]:
        dir_path = workspace_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            dirs_to_analyze.append(dir_name)

    if not dirs_to_analyze:
        return 1

    exit_code, stdout, stderr = _run_mypy_api(dirs_to_analyze)

    if stdout:
        pass
    if stderr:
        pass

    if exit_code == 0:
        pass

    return exit_code


def get_python_projects() -> list[Path]:
    """Encontra todos os projetos Python com pyproject.toml."""
    workspace_root = Path(__file__).parent.parent
    projects: list[Path] = []

    # Projetos definidos no Makefile (seguindo padrão existente)
    project_patterns = ["flext-*", "client-a-*", "client-b-*", "flexcore"]

    for pattern in project_patterns:
        projects.extend(
            project_dir
            for project_dir in workspace_root.glob(pattern)
            if (
                project_dir.is_dir()
                and (project_dir / "pyproject.toml").exists()
                and (project_dir / "src").exists()
            )
        )

    return sorted(projects)


def analyze_project(project_path: Path) -> int:
    """Analisa projeto específico com seu pyproject.toml."""
    exit_code, stdout, stderr = _run_mypy_api([str(project_path)])

    if stdout:
        pass
    if stderr:
        pass

    return exit_code


def analyze_all_projects() -> int:
    """Analisa todos os projetos individuais."""
    projects = get_python_projects()
    if not projects:
        return 0

    total_errors = 0
    success_count = 0

    for project in projects:
        exit_code = analyze_project(project)

        if exit_code == 0:
            success_count += 1
        else:
            total_errors += 1

    return total_errors


def analyze_comprehensive() -> int:
    """Análise completa: workspace + todos os projetos."""
    workspace_errors = analyze_workspace()

    project_errors = analyze_all_projects()

    total_errors = workspace_errors + project_errors

    if total_errors == 0:
        pass

    return total_errors


def analyze_specific_project(project_name: str) -> int:
    """Analisa projeto específico por nome."""
    workspace_root = Path(__file__).parent.parent
    project_path = workspace_root / project_name

    if not project_path.exists():
        return 1

    if not (project_path / "pyproject.toml").exists():
        return 1

    return analyze_project(project_path)


def stats_by_project() -> int:
    """Mostra estatísticas de erros MyPy por projeto."""
    projects = get_python_projects()
    if not projects:
        return 0

    all_errors = []
    project_stats = {}

    # Analisar workspace primeiro
    _, workspace_errors = analyze_workspace_with_stats()
    all_errors.extend(workspace_errors)
    workspace_count = len(workspace_errors)
    project_stats["workspace"] = workspace_count

    # Analisar cada projeto
    for project in projects:
        _, project_errors = analyze_project_with_stats(project)
        all_errors.extend(project_errors)
        error_count = len(project_errors)
        project_stats[project.name] = error_count

    # Estatísticas resumidas
    total_errors = len(all_errors)
    len(project_stats)

    # Ordenar projetos por número de erros (decrescente)
    sorted_projects = sorted(
        project_stats.items(),
        key=operator.itemgetter(1),
        reverse=True,
    )

    for _project_name, error_count in sorted_projects:
        percentage = (error_count / total_errors * 100) if total_errors > 0 else 0
        bar_length = int(percentage / 5)  # Escala de 0-20 caracteres
        "█" * bar_length + "░" * (20 - bar_length)

    return total_errors


def stats_by_error_type() -> int:
    """Mostra estatísticas de erros MyPy por tipo."""
    # Analisar workspace
    _, workspace_errors = analyze_workspace_with_stats()
    all_errors = workspace_errors.copy()

    # Analisar todos os projetos
    projects = get_python_projects()
    for project in projects:
        _, project_errors = analyze_project_with_stats(project)
        all_errors.extend(project_errors)

    if not all_errors:
        return 0

    # Contar erros por tipo
    error_type_counts = Counter(error["error_code"] for error in all_errors)

    # Contar erros por projeto para cada tipo
    error_by_project_type: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int),
    )
    for error in all_errors:
        error_by_project_type[str(error["error_code"])][str(error["project"])] += 1

    total_errors = len(all_errors)

    # Ordenar tipos de erro por frequência
    for error_type, count in error_type_counts.most_common():
        percentage = count / total_errors * 100
        bar_length = int(percentage / 2)  # Escala de 0-50 caracteres
        "█" * bar_length + "░" * (max(0, 25 - bar_length))

        # Mostrar distribuição por projeto para este tipo de erro
        project_distribution = error_by_project_type[error_type]
        sorted_projects = sorted(
            project_distribution.items(),
            key=operator.itemgetter(1),
            reverse=True,
        )

        for _project_name, project_count in sorted_projects[:5]:  # Top 5 projetos
            project_count / count * 100

        if len(sorted_projects) > 5:
            len(sorted_projects) - 5

    top_5_errors = error_type_counts.most_common(5)
    for error_type, count in top_5_errors:
        percentage = count / total_errors * 100

    return total_errors


def main() -> int:
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="MyPy Analyzer - PEP 518 Compliant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--workspace",
        action="store_true",
        help="Analyze workspace only",
    )
    group.add_argument(
        "--all-projects",
        action="store_true",
        help="Analyze all individual projects",
    )
    group.add_argument(
        "--comprehensive",
        action="store_true",
        help="Comprehensive analysis (workspace + all projects)",
    )
    group.add_argument("--project", type=str, help="Analyze specific project by name")
    group.add_argument(
        "--stats-by-project",
        action="store_true",
        help="Show error statistics by project",
    )
    group.add_argument(
        "--stats-by-type",
        action="store_true",
        help="Show error statistics by error type",
    )

    args = parser.parse_args()

    if args.workspace:
        return analyze_workspace()
    if args.all_projects:
        return analyze_all_projects()
    if args.comprehensive:
        return analyze_comprehensive()
    if args.project:
        return analyze_specific_project(args.project)
    if args.stats_by_project:
        return stats_by_project()
    if args.stats_by_type:
        return stats_by_error_type()

    return 1


if __name__ == "__main__":
    sys.exit(main())

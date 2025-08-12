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
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Execute command and return exit code, stdout, stderr."""
    # Validate command exists
    if not cmd or not shutil.which(cmd[0]):
        return 1, "", f"Command not found: {cmd[0] if cmd else 'None'}"

    try:
        result = subprocess.run(  # noqa: S603
            cmd,  # Validated: first element checked with shutil.which()
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


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
    print(f"🔍 Analyzing {project_path.name}...")

    exit_code, stdout, stderr = run_command(["mypy", "."], cwd=project_path)

    errors = parse_mypy_errors(stdout + stderr)

    if stdout and not errors:  # Se há output mas não são erros
        print(stdout)
    if stderr and "error:" not in stderr:  # Se há stderr mas não são erros
        print(stderr, file=sys.stderr)

    return exit_code, errors


def analyze_workspace_with_stats() -> tuple[int, list[dict[str, object]]]:
    """Analisa workspace e retorna estatísticas detalhadas."""
    print("🔍 Analyzing workspace with MyPy (PEP 518)...")

    workspace_root = Path(__file__).parent.parent

    # Verificar quais diretórios existem para análise
    dirs_to_analyze = []
    for dir_name in ["src", "tests", "scripts", "examples"]:
        dir_path = workspace_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            dirs_to_analyze.append(dir_name)
            print(f"📁 Found directory: {dir_name}")
        else:
            print(f"⚠️  Directory not found: {dir_name}")

    if not dirs_to_analyze:
        print("❌ No directories found for analysis")
        return 1, []

    exit_code, stdout, stderr = run_command(
        ["mypy", *dirs_to_analyze],
        cwd=workspace_root,
    )

    errors = parse_mypy_errors(stdout + stderr)

    if stdout and not errors:  # Se há output mas não são erros
        print(stdout)
    if stderr and "error:" not in stderr:  # Se há stderr mas não são erros
        print(stderr, file=sys.stderr)

    return exit_code, errors


def analyze_workspace() -> int:
    """Analisa o workspace principal seguindo PEP 518."""
    print("🔍 Analyzing workspace with MyPy (PEP 518)...")

    workspace_root = Path(__file__).parent.parent

    # Verificar quais diretórios existem para análise
    dirs_to_analyze = []
    for dir_name in ["src", "tests", "scripts", "examples"]:
        dir_path = workspace_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            dirs_to_analyze.append(dir_name)
            print(f"📁 Found directory: {dir_name}")
        else:
            print(f"⚠️  Directory not found: {dir_name}")

    if not dirs_to_analyze:
        print("❌ No directories found for analysis")
        return 1

    exit_code, stdout, stderr = run_command(
        ["mypy", *dirs_to_analyze],
        cwd=workspace_root,
    )

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if exit_code == 0:
        print("✅ Workspace analysis completed successfully!")
    else:
        print("❌ Workspace analysis found issues.")

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
    print(f"🔍 Analyzing {project_path.name}...")

    exit_code, stdout, stderr = run_command(["mypy", "."], cwd=project_path)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    return exit_code


def analyze_all_projects() -> int:
    """Analisa todos os projetos individuais."""
    print("🔍 Analyzing all projects...")

    projects = get_python_projects()
    if not projects:
        print("⚠️  No Python projects found with pyproject.toml")
        return 0

    total_errors = 0
    success_count = 0

    for project in projects:
        print(f"\n📦 Project: {project.name}")
        exit_code = analyze_project(project)

        if exit_code == 0:
            success_count += 1
            print(f"✅ {project.name} - OK")
        else:
            total_errors += 1
            print(f"❌ {project.name} - Issues found")

    print(f"\n📊 Summary: {success_count} OK, {total_errors} with issues")
    return total_errors


def analyze_comprehensive() -> int:
    """Análise completa: workspace + todos os projetos."""
    print("🔍 Comprehensive MyPy Analysis")
    print("=" * 50)

    print("\n1️⃣ Workspace Analysis:")
    workspace_errors = analyze_workspace()

    print("\n2️⃣ Individual Projects Analysis:")
    project_errors = analyze_all_projects()

    total_errors = workspace_errors + project_errors

    print("\n" + "=" * 50)
    print(f"🏁 Total Issues: {total_errors}")

    if total_errors == 0:
        print("✅ All analysis completed successfully!")
    else:
        print("❌ Issues found in analysis.")

    return total_errors


def analyze_specific_project(project_name: str) -> int:
    """Analisa projeto específico por nome."""
    workspace_root = Path(__file__).parent.parent
    project_path = workspace_root / project_name

    if not project_path.exists():
        print(f"❌ Project '{project_name}' not found")
        return 1

    if not (project_path / "pyproject.toml").exists():
        print(f"❌ Project '{project_name}' has no pyproject.toml")
        return 1

    return analyze_project(project_path)


def stats_by_project() -> int:
    """Mostra estatísticas de erros MyPy por projeto."""
    print("📊 MyPy Error Statistics by Project")
    print("=" * 50)

    projects = get_python_projects()
    if not projects:
        print("⚠️  No Python projects found with pyproject.toml")
        return 0

    all_errors = []
    project_stats = {}

    # Analisar workspace primeiro
    print("\n🏠 Workspace Analysis:")
    _, workspace_errors = analyze_workspace_with_stats()
    all_errors.extend(workspace_errors)
    workspace_count = len(workspace_errors)
    project_stats["workspace"] = workspace_count

    print(f"   Workspace: {workspace_count} errors")

    # Analisar cada projeto
    print("\n📦 Individual Projects:")
    for project in projects:
        _, project_errors = analyze_project_with_stats(project)
        all_errors.extend(project_errors)
        error_count = len(project_errors)
        project_stats[project.name] = error_count
        print(f"   {project.name}: {error_count} errors")

    # Estatísticas resumidas
    total_errors = len(all_errors)
    total_projects = len(project_stats)

    print("\n" + "=" * 50)
    print("📈 Summary by Project:")
    print("=" * 50)

    # Ordenar projetos por número de erros (decrescente)
    sorted_projects = sorted(
        project_stats.items(),
        key=operator.itemgetter(1),
        reverse=True,
    )

    for project_name, error_count in sorted_projects:
        percentage = (error_count / total_errors * 100) if total_errors > 0 else 0
        bar_length = int(percentage / 5)  # Escala de 0-20 caracteres
        bar = "█" * bar_length + "░" * (20 - bar_length)

        print(f"{project_name:25} {error_count:4d} errors [{bar}] {percentage:5.1f}%")

    print(f"\n🏁 Total: {total_errors} errors across {total_projects} projects")

    return total_errors


def stats_by_error_type() -> int:
    """Mostra estatísticas de erros MyPy por tipo."""
    print("📊 MyPy Error Statistics by Error Type")
    print("=" * 50)

    # Analisar workspace
    print("\n🔍 Collecting errors from all sources...")
    _, workspace_errors = analyze_workspace_with_stats()
    all_errors = workspace_errors.copy()

    # Analisar todos os projetos
    projects = get_python_projects()
    for project in projects:
        _, project_errors = analyze_project_with_stats(project)
        all_errors.extend(project_errors)

    if not all_errors:
        print("✅ No MyPy errors found!")
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

    print(f"\n📈 Found {total_errors} total errors")
    print("\n" + "=" * 80)
    print("📋 Error Types (sorted by frequency):")
    print("=" * 80)

    # Ordenar tipos de erro por frequência
    for error_type, count in error_type_counts.most_common():
        percentage = count / total_errors * 100
        bar_length = int(percentage / 2)  # Escala de 0-50 caracteres
        bar = "█" * bar_length + "░" * (max(0, 25 - bar_length))

        print(f"\n{error_type:30} {count:4d} errors [{bar}] {percentage:5.1f}%")

        # Mostrar distribuição por projeto para este tipo de erro
        project_distribution = error_by_project_type[error_type]
        sorted_projects = sorted(
            project_distribution.items(),
            key=operator.itemgetter(1),
            reverse=True,
        )

        print("  Projects:")
        for project_name, project_count in sorted_projects[:5]:  # Top 5 projetos
            project_percentage = project_count / count * 100
            print(
                f"    {project_name:20} {project_count:3d}"
                f" ({project_percentage:4.1f}%)",
            )

        if len(sorted_projects) > 5:
            remaining = len(sorted_projects) - 5
            print(f"    ... and {remaining} more projects")

    print("\n" + "=" * 80)
    print("🎯 Top Error Types Summary:")
    print("=" * 80)

    top_5_errors = error_type_counts.most_common(5)
    for i, (error_type, count) in enumerate(top_5_errors, 1):
        percentage = count / total_errors * 100
        print(f"{i}. {error_type:25} {count:4d} errors ({percentage:5.1f}%)")

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

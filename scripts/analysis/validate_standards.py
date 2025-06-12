#!/usr/bin/env python3
"""
Validador de Padronização - Verifica se todos os projetos seguem os padrões
"""

import sys
from pathlib import Path

import tomli
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_project_standards(project_path: Path) -> dict:
    """Verifica se um projeto segue os padrões definidos"""
    issues = []
    config_path = project_path / "pyproject.toml"

    if not config_path.exists():
        return {"issues": ["pyproject.toml não encontrado"]}

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
    except Exception as e:
        return {"issues": [f"Erro ao ler pyproject.toml: {e}"]}

    # Verifica build-system
    build_system = config.get("build-system", {})
    if "poetry-core" not in str(build_system.get("requires", [])):
        issues.append("build-system não usa poetry-core")

    # Verifica versão Python
    tool_poetry = config.get("tool", {}).get("poetry", {})
    python_version = tool_poetry.get("dependencies", {}).get("python", "")
    if not python_version.startswith("^3.13"):
        issues.append(f"Python version incorreta: {python_version}")

    # Verifica ferramentas de qualidade
    tool_config = config.get("tool", {})

    required_tools = ["black", "ruff", "mypy", "pytest.ini_options"]
    for tool in required_tools:
        if tool not in tool_config:
            issues.append(f"Ferramenta ausente: {tool}")

    # Verifica ruff target-version
    ruff_config = tool_config.get("ruff", {})
    if ruff_config.get("target-version") != "py312":
        issues.append(
            f"Ruff target-version incorreto: {ruff_config.get('target-version')}"
        )

    # Verifica mypy python_version
    mypy_config = tool_config.get("mypy", {})
    if mypy_config.get("python_version") != "3.13":
        issues.append(
            f"MyPy python_version incorreto: {mypy_config.get('python_version')}"
        )

    return {"issues": issues}


def main():
    """Função principal"""
    workspace_path = Path.cwd()

    console.print(
        Panel.fit(
            "Validator de Padronização PYAUTO\n"
            "Verifica conformidade com padrões PEP8 & Poetry",
            style="bold blue",
        )
    )

    # Encontra projetos
    projects = []
    seen_projects = set()
    for path in workspace_path.rglob("pyproject.toml"):
        if any(
            part.startswith(".")
            and part
            in {".venv", ".mypy_cache", ".pytest_cache", ".standardization_backup"}
            for part in path.parts
        ):
            continue

        # Evita duplicatas baseado no nome do projeto
        project_path = path.parent
        if project_path.name not in seen_projects:
            projects.append(project_path)
            seen_projects.add(project_path.name)

    # Verifica cada projeto
    table = Table(title="Status de Padronização")
    table.add_column("Projeto", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Issues", style="red")

    total_issues = 0

    for project_path in projects:
        result = check_project_standards(project_path)
        issues = result["issues"]

        if issues:
            status = "❌ Não Conforme"
            issues_text = "\n".join(issues[:3])  # Limita a 3 issues
            if len(issues) > 3:
                issues_text += f"\n... e {len(issues) - 3} mais"
            total_issues += len(issues)
        else:
            status = "✅ Conforme"
            issues_text = "-"

        table.add_row(project_path.name, status, issues_text)

    console.print(table)

    if total_issues > 0:
        console.print(f"\n[red]Total de issues encontradas: {total_issues}[/red]")
        console.print(
            "[yellow]Execute 'python standardize_projects.py' para corrigir[/yellow]"
        )
        sys.exit(1)
    else:
        console.print("\n[green]✅ Todos os projetos estão em conformidade![/green]")


if __name__ == "__main__":
    main()

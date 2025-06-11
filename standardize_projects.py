#!/usr/bin/env python3
"""
Script de Padronização PYAUTO - PEP8 & Poetry
Padroniza configurações de todos os projetos Python no workspace
"""

import sys
import shutil
from pathlib import Path
from typing import Dict, List, Any
import tomli
import tomli_w
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()

# Configuração padrão unificada
STANDARD_CONFIG = {
    "build-system": {
        "requires": ["poetry-core>=2.1.3"],
        "build-backend": "poetry.core.masonry.api",
    },
    "tool": {
        "poetry": {
            "dependencies": {
                "python": "^3.13",
            },
        },
        "black": {
            "line-length": 88,
            "target-version": ["py312"],
            "include": r"\.pyi?$",
        },
        "isort": {
            "profile": "black",
            "line_length": 88,
            "multi_line_output": 3,
            "include_trailing_comma": True,
            "force_grid_wrap": 0,
            "use_parentheses": True,
            "ensure_newline_before_comments": True,
        },
        "ruff": {
            "target-version": "py312",
            "line-length": 88,
            "src": ["src", "tests"],
        },
        "ruff.lint": {
            "select": [
                "E",
                "W",
                "F",
                "I",
                "UP",
                "N",
                "B",
                "C4",
                "DTZ",
                "T10",
                "ISC",
                "G",
                "PIE",
                "PT",
                "RET",
                "SIM",
                "ARG",
                "ERA",
                "PGH",
                "PL",
                "TRY",
                "BLE",
                "COM",
            ],
            "ignore": [
                "E501",
                "UP007",
                "BLE001",
                "G004",
                "DTZ007",
                "TRY003",
                "PLR2004",
                "PLR0911",
                "PLR0912",
                "TRY401",
            ],
        },
        "ruff.lint.per-file-ignores": {
            "__init__.py": ["F401"],
            "tests/**/*.py": ["S101", "PLR2004", "TID252", "ARG", "FBT"],
            "scripts/**/*.py": ["T20", "S101", "PLR2004"],
        },
        "mypy": {
            "python_version": "3.13",
            "strict": True,
            "warn_return_any": True,
            "warn_unused_configs": True,
            "warn_redundant_casts": True,
            "warn_unused_ignores": True,
            "show_error_codes": True,
            "pretty": True,
        },
        "pytest.ini_options": {
            "minversion": "8.0",
            "addopts": [
                "--strict-markers",
                "--strict-config",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage",
                "--cov-report=xml",
                "--junitxml=reports/junit.xml",
            ],
            "testpaths": ["tests"],
            "python_files": ["test_*.py", "*_test.py"],
            "python_functions": ["test_*"],
            "python_classes": ["Test*"],
            "markers": [
                "slow: marks tests as slow",
                "integration: marks tests as integration tests",
                "unit: marks tests as unit tests",
            ],
        },
        "coverage.run": {
            "source": ["src"],
            "branch": True,
            "omit": [
                "*/tests/*",
                "*/test_*",
                "*/__main__.py",
                "*/conftest.py",
            ],
        },
        "coverage.report": {
            "exclude_lines": [
                "pragma: no cover",
                "def __repr__",
                "raise AssertionError",
                "raise NotImplementedError",
                "if __name__ == .__main__.:",
                "if TYPE_CHECKING:",
                "@abstractmethod",
            ],
        },
    },
}

# Grupos de dependências padrão para desenvolvimento
STANDARD_DEV_DEPENDENCIES = {
    "pytest": "^8.4.0",
    "pytest-cov": "^6.1.1",
    "pytest-mock": "^3.14.0",
    "pytest-asyncio": "^0.24.0",
    "mypy": "^1.16.0",
    "ruff": "^0.11.13",
    "black": "^25.1.0",
    "isort": "^6.0.1",
    "pre-commit": "^4.2.0",
}


class ProjectStandardizer:
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.projects: List[Path] = []
        self.backup_dir = workspace_path / ".standardization_backup"

    def find_projects(self) -> List[Path]:
        """Encontra todos os projetos com pyproject.toml"""
        projects = []
        seen_projects = set()

        for path in self.workspace_path.rglob("pyproject.toml"):
            # Ignora venv e cache directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in path.parts
            ):
                continue

            # Evita duplicatas baseado no nome do projeto
            project_path = path.parent
            if project_path.name not in seen_projects:
                projects.append(project_path)
                seen_projects.add(project_path.name)

        return projects

    def create_backup(self, project_path: Path):
        """Cria backup do pyproject.toml original"""
        backup_path = self.backup_dir / project_path.name
        backup_path.mkdir(parents=True, exist_ok=True)

        source = project_path / "pyproject.toml"
        target = backup_path / "pyproject.toml"
        shutil.copy2(source, target)

    def load_project_config(self, project_path: Path) -> Dict[str, Any]:
        """Carrega configuração atual do projeto"""
        config_path = project_path / "pyproject.toml"
        with open(config_path, "rb") as f:
            return tomli.load(f)

    def merge_configs(
        self, current: Dict[str, Any], project_path: Path
    ) -> Dict[str, Any]:
        """Mescla configuração atual com padrões"""
        result = current.copy()

        # Atualiza build-system
        result["build-system"] = STANDARD_CONFIG["build-system"]

        # Preserva metadados do projeto Poetry
        if "tool" not in result:
            result["tool"] = {}
        if "poetry" not in result["tool"]:
            result["tool"]["poetry"] = {}

        # Preserva informações específicas do projeto
        poetry_config = result["tool"]["poetry"]

        # Atualiza python version nas dependencies
        if "dependencies" in poetry_config:
            poetry_config["dependencies"]["python"] = "^3.13"

        # Adiciona dependências de desenvolvimento padrão
        if "group" not in result["tool"]["poetry"]:
            result["tool"]["poetry"]["group"] = {}
        if "dev" not in result["tool"]["poetry"]["group"]:
            result["tool"]["poetry"]["group"]["dev"] = {}
        if "dependencies" not in result["tool"]["poetry"]["group"]["dev"]:
            result["tool"]["poetry"]["group"]["dev"]["dependencies"] = {}

        # Mescla dev dependencies
        dev_deps = result["tool"]["poetry"]["group"]["dev"]["dependencies"]
        for dep, version in STANDARD_DEV_DEPENDENCIES.items():
            if dep not in dev_deps:
                dev_deps[dep] = version

        # Aplica configurações padrão de ferramentas
        for tool, config in STANDARD_CONFIG["tool"].items():
            if tool != "poetry":  # Poetry já foi tratado acima
                result["tool"][tool] = config

        # Ajustes específicos por projeto
        if "flx" in str(project_path):
            # FLX precisa de configurações mais rigorosas
            result["tool"]["ruff"]["line-length"] = 120
            result["tool"]["mypy"]["strict"] = True

        return result

    def save_project_config(self, project_path: Path, config: Dict[str, Any]):
        """Salva configuração padronizada"""
        config_path = project_path / "pyproject.toml"
        with open(config_path, "wb") as f:
            tomli_w.dump(config, f)

    def standardize_project(self, project_path: Path) -> bool:
        """Padroniza um projeto específico"""
        try:
            # Cria backup
            self.create_backup(project_path)

            # Carrega e mescla configuração
            current_config = self.load_project_config(project_path)
            standardized_config = self.merge_configs(current_config, project_path)

            # Salva configuração padronizada
            self.save_project_config(project_path, standardized_config)

            return True
        except Exception as e:
            console.print(f"[red]Erro ao padronizar {project_path.name}: {e}[/red]")
            return False

    def run_standardization(self):
        """Executa padronização completa"""
        console.print(Panel.fit("🔧 Iniciando Padronização PYAUTO", style="bold blue"))

        # Encontra projetos
        self.projects = self.find_projects()
        console.print(f"[green]Encontrados {len(self.projects)} projetos[/green]")

        # Cria diretório de backup
        self.backup_dir.mkdir(exist_ok=True)

        # Cria tabela de progresso
        table = Table(title="Projetos a Padronizar")
        table.add_column("Projeto", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Observações")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Padronizando projetos...", total=len(self.projects)
            )

            for project_path in self.projects:
                progress.update(task, description=f"Processando {project_path.name}")

                success = self.standardize_project(project_path)
                status = "✅ Padronizado" if success else "❌ Erro"

                table.add_row(
                    project_path.name,
                    status,
                    "Backup criado" if success else "Verifique logs",
                )

                results.append((project_path.name, success))
                progress.advance(task)

        console.print(table)

        # Sumário final
        successful = sum(1 for _, success in results if success)
        console.print(
            f"\n[green]✅ {successful}/{len(results)} projetos padronizados com sucesso[/green]"
        )
        console.print(f"[yellow]📁 Backups salvos em: {self.backup_dir}[/yellow]")

        return results


def main():
    """Função principal"""
    workspace_path = Path.cwd()

    console.print(
        Panel.fit(
            "PYAUTO Standardization Tool\n"
            "Padroniza configurações PEP8 & Poetry\n"
            "em todos os projetos do workspace",
            style="bold magenta",
        )
    )

    # Confirma execução
    if "--force" not in sys.argv:
        confirm = console.input(
            "\n[yellow]Deseja continuar com a padronização? (y/N): [/yellow]"
        )
        if confirm.lower() != "y":
            console.print("[red]Operação cancelada[/red]")
            return

    # Executa padronização
    standardizer = ProjectStandardizer(workspace_path)
    standardizer.run_standardization()

    # Recomendações pós-padronização
    console.print(
        Panel(
            "🔄 Próximos passos recomendados:\n"
            "1. Execute 'poetry lock --no-update' em cada projeto\n"
            "2. Execute 'poetry install' para atualizar dependências\n"
            "3. Execute 'ruff check .' para verificar conformidade\n"
            "4. Execute 'mypy .' para verificar tipos\n"
            "5. Execute testes para garantir funcionalidade",
            title="Pós-Padronização",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()

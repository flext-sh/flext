#!/usr/bin/env python3
"""
PyAuto Enterprise Project Standardization System

Padroniza pyproject.toml e .pre-commit-config.yaml em todos os subprojetos
seguindo os padrões enterprise definidos no CLAUDE.md e template oficial.

ZERO TOLERANCE para configurações inconsistentes.
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import toml
import tomli
from rich.console import Console
from rich.table import Table


class ProjectStandardizer:
    """Sistema enterprise de padronização de projetos."""

    def __init__(self, workspace_root: Path = Path.cwd()) -> None:
        self.workspace_root = workspace_root
        self.console = Console()
        self.template_pyproject = workspace_root / "pyproject-template.toml"
        self.backup_dir = workspace_root / "backups" / f"standardization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Load template
        if not self.template_pyproject.exists():
            raise FileNotFoundError(f"Template não encontrado: {self.template_pyproject}")

        with open(self.template_pyproject, "rb") as f:
            self.template_config = tomli.load(f)

    def discover_real_projects(self) -> list[Path]:
        """Descobre todos os subprojetos reais com pyproject.toml."""
        projects = []

        # Definir projetos principais baseado na estrutura conhecida
        known_projects = [
            "flx",
            "tap-ldap",
            "target-ldap",
            "flx-ldap",
            "dbt-ldap",
            "ldap-core-shared",
            "tap-oracle-wms",
            "tap-oracle-oic",
            "target-oracle-wms",
            "target-oracle-oic",
            "flx-oracle-wms",
            "flx-oracle-oic",
            "oracle-oic-ext",
            "flx-database-oracle",
            "flx-http-oracle-oic",
            "flx-http-oracle-wms",
            "flx-adapter-example",
            "flx-meltano-enterprise",
            "client-a-oud-mig",
            "dc-code-analyzer",
            "client-b-poc-oic-wms"
        ]

        for project_name in known_projects:
            project_path = self.workspace_root / project_name
            pyproject_path = project_path / "pyproject.toml"

            if project_path.exists() and project_path.is_dir() and pyproject_path.exists():
                projects.append(project_path)
                self.console.print(f"✓ Projeto encontrado: [green]{project_name}[/green]")
            else:
                self.console.print(f"⚠ Projeto não encontrado ou sem pyproject.toml: [yellow]{project_name}[/yellow]")

        return projects

    def create_backup(self, project_path: Path) -> None:
        """Cria backup completo do projeto antes das modificações."""
        project_name = project_path.name
        project_backup_dir = self.backup_dir / project_name
        project_backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup pyproject.toml
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            shutil.copy2(pyproject_file, project_backup_dir / "pyproject.toml")

        # Backup .pre-commit-config.yaml
        precommit_file = project_path / ".pre-commit-config.yaml"
        if precommit_file.exists():
            shutil.copy2(precommit_file, project_backup_dir / ".pre-commit-config.yaml")

        # Backup poetry.lock se existir
        poetry_lock = project_path / "poetry.lock"
        if poetry_lock.exists():
            shutil.copy2(poetry_lock, project_backup_dir / "poetry.lock")

        self.console.print(f"✓ Backup criado: [blue]{project_backup_dir}[/blue]")

    def get_project_module_name(self, project_name: str) -> str:
        """Converte nome do projeto para nome do módulo Python."""
        # Converter hifens para underscores
        return project_name.replace("-", "_")

    def detect_project_type(self, project_path: Path) -> str:
        """Detecta o tipo do projeto baseado na estrutura."""
        project_name = project_path.name.lower()

        if project_name.startswith("tap-"):
            return "singer_tap"
        if project_name.startswith("target-"):
            return "singer_target"
        if project_name.startswith("flx-"):
            return "flx_adapter"
        if project_name == "flx":
            return "flx_core"
        if project_name.startswith("dbt-"):
            return "dbt_package"
        return "generic"

    def standardize_pyproject_toml(self, project_path: Path) -> bool:
        """Padroniza o pyproject.toml do projeto usando o template enterprise."""
        try:
            pyproject_file = project_path / "pyproject.toml"
            project_name = project_path.name
            project_module = self.get_project_module_name(project_name)
            project_type = self.detect_project_type(project_path)

            # Carregar configuração atual se existir
            current_config = {}
            if pyproject_file.exists():
                with open(pyproject_file, "rb") as f:
                    current_config = tomli.load(f)

            # Criar nova configuração baseada no template
            new_config = self.template_config.copy()

            # Substituir placeholders
            self._replace_placeholders(new_config, project_name, project_module)

            # Preservar dependências específicas do projeto
            self._preserve_project_dependencies(new_config, current_config, project_type)

            # Preservar scripts CLI se existirem
            self._preserve_cli_scripts(new_config, current_config)

            # Escrever nova configuração usando toml
            with open(pyproject_file, "w") as f:
                toml.dump(new_config, f)

            self.console.print(f"✓ pyproject.toml padronizado: [green]{project_name}[/green]")
            return True

        except Exception as e:
            self.console.print(f"✗ Erro ao padronizar pyproject.toml em {project_path.name}: [red]{e}[/red]")
            return False

    def _replace_placeholders(self, config: dict[str, Any], project_name: str, project_module: str) -> None:
        """Substitui placeholders no template."""
        def replace_recursive(obj: dict[str, Any] | list[Any] | str, replacements: dict[str, str]) -> dict[str, Any] | list[Any] | str:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    obj[key] = replace_recursive(value, replacements)
            elif isinstance(obj, list):
                obj = [replace_recursive(item, replacements) for item in obj]
            elif isinstance(obj, str):
                for old, new in replacements.items():
                    obj = obj.replace(old, new)
            return obj

        replacements = {
            "PROJECT_NAME": project_name,
            "PROJECT_MODULE": project_module,
        }

        replace_recursive(config, replacements)

    def _preserve_project_dependencies(self, new_config: dict[str, Any], current_config: dict[str, Any], project_type: str) -> None:
        """Preserva dependências específicas do projeto."""
        if "tool" not in current_config or "poetry" not in current_config["tool"]:
            return

        current_deps = current_config["tool"]["poetry"].get("dependencies", {})

        # Preservar dependências específicas (não core)
        core_deps = {"python", "pydantic", "typing-extensions"}

        for dep_name, dep_spec in current_deps.items():
            if dep_name not in core_deps and dep_name != "python":
                new_config["tool"]["poetry"]["dependencies"][dep_name] = dep_spec

        # Adicionar dependências típicas por tipo de projeto
        if project_type == "singer_tap":
            new_config["tool"]["poetry"]["dependencies"]["singer-sdk"] = "^0.45.0"
        elif project_type == "singer_target":
            new_config["tool"]["poetry"]["dependencies"]["singer-sdk"] = "^0.45.0"
        elif project_type.startswith("flx_"):
            new_config["tool"]["poetry"]["dependencies"]["flx"] = {"path": "../flx", "develop": True}

    def _preserve_cli_scripts(self, new_config: dict[str, Any], current_config: dict[str, Any]) -> None:
        """Preserva scripts CLI existentes."""
        if ("tool" in current_config and
            "poetry" in current_config["tool"] and
            "scripts" in current_config["tool"]["poetry"]):

            scripts = current_config["tool"]["poetry"]["scripts"]
            if scripts:
                new_config["tool"]["poetry"]["scripts"] = scripts

    def create_standard_precommit_config(self, project_path: Path) -> bool:
        """Cria configuração padrão de pre-commit para o projeto."""
        try:
            precommit_file = project_path / ".pre-commit-config.yaml"

            # Configuração padrão enterprise baseada no FLX
            precommit_config = """# Pre-commit configuration - PyAuto Enterprise Standards
# See https://pre-commit.com for more information

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements
      - id: mixed-line-ending

  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.16.0
    hooks:
      - id: mypy
        additional_dependencies: [types-python-dateutil]
        args: [--strict, --ignore-missing-imports]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        args: [-r, src/]
        exclude: tests/

  - repo: https://github.com/python-poetry/poetry
    rev: 1.8.4
    hooks:
      - id: poetry-check
      - id: poetry-lock
        args: [--no-update]
"""

            with open(precommit_file, "w") as f:
                f.write(precommit_config)

            self.console.print(f"✓ .pre-commit-config.yaml criado: [green]{project_path.name}[/green]")
            return True

        except Exception as e:
            self.console.print(f"✗ Erro ao criar .pre-commit-config.yaml em {project_path.name}: [red]{e}[/red]")
            return False

    def install_precommit_hooks(self, project_path: Path) -> bool:
        """Instala os hooks de pre-commit no projeto."""
        try:
            result = subprocess.run(
                ["pre-commit", "install"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.console.print(f"✓ Pre-commit hooks instalados: [green]{project_path.name}[/green]")
                return True
            self.console.print(f"⚠ Aviso ao instalar pre-commit em {project_path.name}: {result.stderr}")
            return False

        except Exception as e:
            self.console.print(f"✗ Erro ao instalar pre-commit em {project_path.name}: [red]{e}[/red]")
            return False

    def validate_project_quality_gates(self, project_path: Path) -> dict[str, bool]:
        """Valida os quality gates do projeto."""
        results = {}

        # Verificar se pyproject.toml é válido
        try:
            with open(project_path / "pyproject.toml", "rb") as f:
                tomli.load(f)
            results["pyproject_valid"] = True
        except Exception:
            results["pyproject_valid"] = False

        # Verificar se poetry check passa
        try:
            result = subprocess.run(
                ["poetry", "check"],
                cwd=project_path,
                capture_output=True,
                timeout=30
            )
            results["poetry_check"] = result.returncode == 0
        except Exception:
            results["poetry_check"] = False

        # Verificar se pre-commit funciona (dry-run)
        try:
            result = subprocess.run(
                ["pre-commit", "run", "--all-files", "--dry-run"],
                cwd=project_path,
                capture_output=True,
                timeout=60
            )
            results["precommit_valid"] = result.returncode == 0
        except Exception:
            results["precommit_valid"] = False

        return results

    def run_standardization(self) -> None:
        """Executa o processo completo de padronização."""
        self.console.print("\n[bold blue]🚀 PyAuto Enterprise Project Standardization[/bold blue]\n")

        # Descobrir projetos
        projects = self.discover_real_projects()

        if not projects:
            self.console.print("[red]Nenhum projeto encontrado![/red]")
            return

        self.console.print(f"\n[green]✓ {len(projects)} projetos descobertos[/green]\n")

        # Processar cada projeto
        results_table = Table(title="Resultados da Padronização")
        results_table.add_column("Projeto", style="cyan")
        results_table.add_column("Backup", style="green")
        results_table.add_column("PyProject", style="yellow")
        results_table.add_column("Pre-commit", style="blue")
        results_table.add_column("Hooks", style="magenta")
        results_table.add_column("Validação", style="white")

        total_success = 0

        for project_path in projects:
            project_name = project_path.name

            self.console.print(f"\n[bold]📦 Processando: {project_name}[/bold]")

            # Criar backup
            self.create_backup(project_path)
            backup_ok = "✓"

            # Padronizar pyproject.toml
            pyproject_ok = "✓" if self.standardize_pyproject_toml(project_path) else "✗"

            # Criar/atualizar pre-commit config
            precommit_ok = "✓" if self.create_standard_precommit_config(project_path) else "✗"

            # Instalar hooks
            hooks_ok = "✓" if self.install_precommit_hooks(project_path) else "⚠"

            # Validar quality gates
            validation = self.validate_project_quality_gates(project_path)
            validation_ok = "✓" if all(validation.values()) else "⚠"

            if pyproject_ok == "✓" and precommit_ok == "✓":
                total_success += 1

            results_table.add_row(
                project_name,
                backup_ok,
                pyproject_ok,
                precommit_ok,
                hooks_ok,
                validation_ok
            )

        # Mostrar resultados
        self.console.print("\n")
        self.console.print(results_table)

        self.console.print(f"\n[bold green]✅ Padronização concluída: {total_success}/{len(projects)} projetos[/bold green]")
        self.console.print(f"[blue]📁 Backups salvos em: {self.backup_dir}[/blue]")


def main() -> None:
    """Função principal."""
    try:
        standardizer = ProjectStandardizer()
        standardizer.run_standardization()

        # Registrar conclusão conforme CLAUDE.md
        with open(".token", "a") as f:
            f.write("STANDARDIZATION-PRECOMMIT-001 COMPLETED\n")

    except KeyboardInterrupt:
        print("\n❌ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        with open(".token", "a") as f:
            f.write(f"STANDARDIZATION-PRECOMMIT-001 FAILED: {e}\n")


if __name__ == "__main__":
    main()

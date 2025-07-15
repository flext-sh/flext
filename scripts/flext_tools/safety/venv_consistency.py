"""Validação de consistência do virtual environment"""

import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from flext_tools.utils import Colors, print_colored


@dataclass
class PackageInfo:
    """Informações sobre um package instalado."""

    name: str
    version: str
    location: str | None = None
    required_by: list[str] | None = None
    dependencies: list[str] | None = None


@dataclass
class VenvConflict:
    """Representa um conflito no virtual environment."""

    type: str  # "version", "missing", "duplicate", "orphan"
    package: str
    details: str
    severity: str  # "critical", "warning", "info"
    affected_projects: list[str]


class VenvConsistencyValidator:
    """Valida consistência do virtual environment compartilhado."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.venv_path = workspace_path / ".venv"
        self.installed_packages: dict[str, PackageInfo] = {}
        self.project_requirements: dict[str, dict[str, str]] = {}
        self.conflicts: list[VenvConflict] = []

    def validate_venv_consistency(self) -> dict[str, list[VenvConflict]]:
        """
        Executa validação completa do venv.

        Returns:
            Dict com categorias de conflitos
        """
        print_colored(
            "🔍 Validando consistência do virtual environment...", Colors.BLUE
        )

        # Verifica se venv existe
        if not self.venv_path.exists():
            print_colored("❌ Virtual environment não encontrado!", Colors.RED)
            return {
                "critical": [
                    VenvConflict(
                        type="missing",
                        package="venv",
                        details="Virtual environment não existe",
                        severity="critical",
                        affected_projects=[],
                    )
                ]
            }

        # Coleta informações do venv
        self._scan_installed_packages()

        # Coleta requisitos dos projetos
        self._scan_project_requirements()

        # Detecta conflitos
        self._detect_conflicts()

        return self._categorize_conflicts()

    def _scan_installed_packages(self):
        """Escaneia packages instalados no venv."""
        print_colored("  📦 Escaneando packages instalados...", Colors.CYAN)

        try:
            # Usa pip list para obter packages instalados
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )

            import json

            packages_data = json.loads(result.stdout)

            for pkg_data in packages_data:
                name = pkg_data["name"].lower().replace("_", "-")
                version = pkg_data["version"]

                self.installed_packages[name] = PackageInfo(name=name, version=version)

            print_colored(
                f"    ✅ {len(self.installed_packages)} packages encontrados",
                Colors.GREEN,
            )

        except Exception as e:
            print_colored(f"    ❌ Erro ao escanear packages: {e}", Colors.RED)

    def _scan_project_requirements(self):
        """Escaneia requisitos de todos os projetos."""
        print_colored("  📋 Escaneando requisitos dos projetos...", Colors.CYAN)

        projects = [
            d
            for d in self.workspace_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        for project_path in projects:
            project_name = project_path.name
            self.project_requirements[project_name] = {}

            # Processa pyproject.toml
            pyproject_path = project_path / "pyproject.toml"
            if pyproject_path.exists():
                try:
                    import tomllib

                    with open(pyproject_path, "rb") as f:
                        data = tomllib.load(f)

                    # PEP 621 dependencies
                    pep621_deps = data.get("project", {}).get("dependencies", [])
                    for dep_spec in pep621_deps:
                        dep_name, dep_version = self._parse_dependency_spec(dep_spec)
                        if dep_name:
                            self.project_requirements[project_name][dep_name] = (
                                dep_version
                            )

                    # Poetry dependencies
                    poetry_deps = (
                        data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                    )
                    for dep_name, dep_spec in poetry_deps.items():
                        if dep_name != "python" and not isinstance(dep_spec, dict):
                            self.project_requirements[project_name][dep_name] = str(
                                dep_spec
                            )
                        elif isinstance(dep_spec, dict) and "version" in dep_spec:
                            self.project_requirements[project_name][dep_name] = (
                                dep_spec["version"]
                            )

                    # Poetry group dependencies
                    groups = data.get("tool", {}).get("poetry", {}).get("group", {})
                    for group_data in groups.values():
                        group_deps = group_data.get("dependencies", {})
                        for dep_name, dep_spec in group_deps.items():
                            if not isinstance(dep_spec, dict):
                                self.project_requirements[project_name][dep_name] = str(
                                    dep_spec
                                )
                            elif "version" in dep_spec:
                                self.project_requirements[project_name][dep_name] = (
                                    dep_spec["version"]
                                )

                except Exception as e:
                    print_colored(
                        f"    ⚠️ Erro ao ler {project_name}: {e}", Colors.YELLOW
                    )

        total_reqs = sum(len(reqs) for reqs in self.project_requirements.values())
        print_colored(
            f"    ✅ {total_reqs} requisitos em {len(projects)} projetos", Colors.GREEN
        )

    def _parse_dependency_spec(self, dep_spec: str) -> tuple[str, str]:
        """
        Parse uma especificação de dependência PEP 621.

        Returns:
            Tuple (nome, versão)
        """
        import re

        # Remove espaços e parênteses
        dep_spec = dep_spec.strip().replace("(", "").replace(")", "")

        # Extrai nome e versão
        match = re.match(r"^([a-zA-Z0-9_-]+)([>=<~!].*)?", dep_spec)
        if match:
            name = match.group(1).lower().replace("_", "-")
            version = match.group(2) or "any"
            return name, version

        return "", ""

    def _detect_conflicts(self):
        """Detecta conflitos entre venv e requisitos dos projetos."""
        print_colored("  🔍 Detectando conflitos...", Colors.CYAN)

        # Agrega requisitos por package
        package_requirements = defaultdict(dict)
        for project_name, requirements in self.project_requirements.items():
            for dep_name, dep_version in requirements.items():
                package_requirements[dep_name][project_name] = dep_version

        conflicts_found = 0

        for package_name, project_versions in package_requirements.items():
            if len(project_versions) <= 1:
                continue  # Não há conflito se apenas 1 projeto usa

            # Verifica se há versões diferentes
            unique_versions = set(project_versions.values())
            if len(unique_versions) > 1:
                # Conflito de versão entre projetos
                self.conflicts.append(
                    VenvConflict(
                        type="version",
                        package=package_name,
                        details=f"Versões diferentes: {dict(project_versions)}",
                        severity="critical"
                        if len(project_versions) > len(self.project_requirements) / 2
                        else "warning",
                        affected_projects=list(project_versions.keys()),
                    )
                )
                conflicts_found += 1

            # Verifica se package está instalado no venv
            normalized_name = package_name.lower().replace("_", "-")
            if normalized_name not in self.installed_packages:
                # Package requerido mas não instalado
                self.conflicts.append(
                    VenvConflict(
                        type="missing",
                        package=package_name,
                        details=f"Requerido por {len(project_versions)} projetos mas não instalado",
                        severity="critical",
                        affected_projects=list(project_versions.keys()),
                    )
                )
                conflicts_found += 1

        # Detecta packages órfãos (instalados mas não requeridos)
        all_required = set()
        for requirements in self.project_requirements.values():
            all_required.update(req.lower().replace("_", "-") for req in requirements)

        orphan_packages = []
        for installed_name in self.installed_packages:
            if installed_name not in all_required:
                # Verifica se não é package do sistema ou desenvolvimento
                if not self._is_system_package(installed_name):
                    orphan_packages.append(installed_name)

        if orphan_packages:
            # Agrupa órfãos em um conflito
            self.conflicts.append(
                VenvConflict(
                    type="orphan",
                    package="multiple",
                    details=f"{len(orphan_packages)} packages órfãos: {orphan_packages[:10]}{'...' if len(orphan_packages) > 10 else ''}",
                    severity="info",
                    affected_projects=[],
                )
            )

        print_colored(
            f"    📊 {conflicts_found} conflitos detectados",
            Colors.YELLOW if conflicts_found > 0 else Colors.GREEN,
        )

    def _is_system_package(self, package_name: str) -> bool:
        """Verifica se é um package de sistema/desenvolvimento."""
        system_packages = {
            "pip",
            "setuptools",
            "wheel",
            "poetry",
            "poetry-core",
            "poetry-plugin-export",
            "virtualenv",
            "distlib",
            "platformdirs",
            "filelock",
            "six",
            "colorama",
            "importlib-metadata",
            "zipp",
            "typing-extensions",
            "packaging",
            "pyparsing",
            "certifi",
            "charset-normalizer",
            "idna",
            "requests",
            "urllib3",
            "tomli",
            "tomllib-w",
        }

        return package_name in system_packages or package_name.startswith("pip-")

    def _categorize_conflicts(self) -> dict[str, list[VenvConflict]]:
        """Categoriza conflitos por severidade."""
        categories = {"critical": [], "warning": [], "info": []}

        for conflict in self.conflicts:
            categories[conflict.severity].append(conflict)

        # Report summary
        total = len(self.conflicts)
        if total > 0:
            print_colored(f"\n📊 Conflitos encontrados: {total}", Colors.YELLOW)
            print_colored(f"  🔴 Críticos: {len(categories['critical'])}", Colors.RED)
            print_colored(f"  🟡 Avisos: {len(categories['warning'])}", Colors.YELLOW)
            print_colored(f"  ℹ️ Info: {len(categories['info'])}", Colors.CYAN)
        else:
            print_colored("\n✅ Nenhum conflito detectado", Colors.GREEN)

        return categories

    def get_venv_summary(self) -> dict[str, any]:
        """Retorna resumo do estado do venv."""
        return {
            "venv_path": str(self.venv_path),
            "venv_exists": self.venv_path.exists(),
            "installed_packages": len(self.installed_packages),
            "projects_scanned": len(self.project_requirements),
            "total_conflicts": len(self.conflicts),
            "python_executable": sys.executable,
        }

    def print_detailed_report(self, categories: dict[str, list[VenvConflict]]):
        """Imprime relatório detalhado dos conflitos."""

        for severity, conflicts in categories.items():
            if not conflicts:
                continue

            color = (
                Colors.RED
                if severity == "critical"
                else (Colors.YELLOW if severity == "warning" else Colors.CYAN)
            )

            severity_label = {
                "critical": "🔴 CRÍTICOS",
                "warning": "🟡 AVISOS",
                "info": "ℹ️ INFORMAÇÕES",
            }.get(severity, severity.upper())

            print_colored(f"\n{severity_label} ({len(conflicts)}):", color)

            for conflict in conflicts[:10]:  # Limite de 10 por categoria
                print_colored(f"  📦 {conflict.package} ({conflict.type}):", color)
                print_colored(f"    {conflict.details}", color)

                if conflict.affected_projects:
                    projects_str = ", ".join(conflict.affected_projects[:5])
                    if len(conflict.affected_projects) > 5:
                        projects_str += f" e mais {len(conflict.affected_projects) - 5}"
                    print_colored(f"    🎯 Projetos afetados: {projects_str}", color)

            if len(conflicts) > 10:
                print_colored(f"    ... e mais {len(conflicts) - 10} conflitos", color)

"""Validação de consistência do virtual environment."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from flext_tools.utils import Colors, print_colored

if TYPE_CHECKING:
    from pathlib import Path

MAX_ORPHAN_DISPLAY = 10
MAX_PROJECTS_DISPLAY = 5
MAX_CONFLICTS_DISPLAY = 10


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

    def __init__(self, workspace_path: Path) -> None:
        """Initialize validator with workspace path."""
        self.workspace_path = workspace_path
        self.venv_path = workspace_path / ".venv"
        self.installed_packages: dict[str, PackageInfo] = {}
        self.project_requirements: dict[str, dict[str, str]] = {}
        self.conflicts: list[VenvConflict] = []

    def validate_venv_consistency(self) -> dict[str, list[VenvConflict]]:
        """Valida consistência do venv compartilhado."""
        print_colored(
            "🔍 Validando consistência do virtual environment...",
            Colors.BLUE,
        )

        # 1. Verifica se venv existe
        if not self._check_venv_exists():
            return {
                "critical": [
                    VenvConflict(
                        type="missing_venv",
                        package="",
                        details="Virtual environment não encontrado",
                        severity="critical",
                        affected_projects=[],
                    ),
                ],
            }

        # 2. Escaneia packages instalados
        self._scan_installed_packages()

        # 3. Coleta requisitos dos projetos
        self._collect_project_requirements()

        # 4. Analisa conflitos
        self._analyze_conflicts()

        # 5. Organiza conflitos por severidade
        conflicts_by_severity = self._organize_conflicts_by_severity()

        # 6. Gera relatório
        self._print_validation_summary(conflicts_by_severity)

        return conflicts_by_severity

    def _check_venv_exists(self) -> bool:
        """Verifica se o virtual environment existe."""
        if not self.venv_path.exists():
            print_colored("❌ Virtual environment não encontrado!", Colors.RED)
            print_colored(f"    Esperado em: {self.venv_path}", Colors.YELLOW)
            return False

        print_colored(
            f"✅ Virtual environment encontrado: {self.venv_path}",
            Colors.GREEN,
        )
        return True

    def _scan_installed_packages(self) -> None:
        """Escaneia packages instalados no venv."""
        print_colored("  📦 Escaneando packages instalados...", Colors.CYAN)

        try:
            # Usa pip list para obter packages instalados
            # Safe: using sys.executable with hardcoded arguments
            result = subprocess.run(  # noqa: S603
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.workspace_path,
            )

            packages_data = json.loads(result.stdout)

            for package_data in packages_data:
                name = package_data["name"].lower()
                version = package_data["version"]

                self.installed_packages[name] = PackageInfo(
                    name=name,
                    version=version,
                )

            print_colored(
                f"    ✅ {len(self.installed_packages)} packages encontrados",
                Colors.GREEN,
            )

        except subprocess.CalledProcessError as e:
            print_colored(f"    ⚠️ Erro ao escanear packages: {e}", Colors.YELLOW)
        except (json.JSONDecodeError, OSError, ValueError) as e:
            print_colored(f"    ⚠️ Erro inesperado: {e}", Colors.YELLOW)

    def _collect_project_requirements(self) -> None:
        """Coleta requisitos de todos os projetos."""
        print_colored("  📋 Coletando requisitos dos projetos...", Colors.CYAN)

        projects = [
            d
            for d in self.workspace_path.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and (d / "pyproject.toml").exists()
        ]

        for project_path in projects:
            project_name = project_path.name

            # Processa pyproject.toml
            pyproject_path = project_path / "pyproject.toml"

            try:
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)

                self.project_requirements[project_name] = {}

                # Dependências principais
                deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                for dep_name, dep_spec in deps.items():
                    if dep_name != "python":
                        name, version = self._parse_dependency_spec(str(dep_spec))
                        self.project_requirements[project_name][name] = version

                # Dependências de desenvolvimento
                dev_deps = (
                    data.get("tool", {})
                    .get("poetry", {})
                    .get("group", {})
                    .get("dev", {})
                    .get("dependencies", {})
                )
                for dep_spec in dev_deps.values():
                    name, version = self._parse_dependency_spec(str(dep_spec))
                    self.project_requirements[project_name][f"{name}[dev]"] = version

            except (
                OSError,
                tomllib.TOMLDecodeError,
                KeyError,
                UnicodeDecodeError,
            ) as e:
                print_colored(
                    f"    ⚠️ Erro ao ler {project_name}: {e}",
                    Colors.YELLOW,
                )

        total_reqs = sum(len(reqs) for reqs in self.project_requirements.values())
        print_colored(
            f"    ✅ {total_reqs} requisitos em {len(projects)} projetos",
            Colors.GREEN,
        )

    def _parse_dependency_spec(self, dep_spec: str | dict[str, Any]) -> tuple[str, str]:
        """Parse uma especificação de dependência PEP 621."""
        if isinstance(dep_spec, dict):
            name = dep_spec.get("name", "unknown")
            version = dep_spec.get("version", "*")
            return name.lower(), str(version)

        # String simples como "package^1.0.0" ou "package"
        if "^" in dep_spec:
            name, version = dep_spec.split("^", 1)
            return name.lower().strip(), f"^{version.strip()}"
        if "==" in dep_spec:
            name, version = dep_spec.split("==", 1)
            return name.lower().strip(), f"=={version.strip()}"
        if ">=" in dep_spec:
            name, version = dep_spec.split(">=", 1)
            return name.lower().strip(), f">={version.strip()}"
        return dep_spec.lower().strip(), "*"

    def _analyze_conflicts(self) -> None:
        """Analisa conflitos entre packages instalados e requisitos."""
        print_colored("  🔍 Analisando conflitos...", Colors.CYAN)

        # Mapeia qual package é requisitado por quais projetos
        package_requesters: dict[str, list[str]] = defaultdict(list)
        package_versions: dict[str, set[str]] = defaultdict(set)

        for project, requirements in self.project_requirements.items():
            for package, version in requirements.items():
                # Remove marcadores como [dev]
                clean_package = package.split("[")[0]
                package_requesters[clean_package].append(project)
                package_versions[clean_package].add(version)

        # 1. Conflitos de versão
        for package, versions in package_versions.items():
            if len(versions) > 1:
                self.conflicts.append(
                    VenvConflict(
                        type="version",
                        package=package,
                        details=f"Versões conflitantes: {', '.join(versions)}",
                        severity="warning",
                        affected_projects=package_requesters[package],
                    ),
                )

        # 2. Packages missing
        for package, requesters in package_requesters.items():
            if package not in self.installed_packages:
                self.conflicts.append(
                    VenvConflict(
                        type="missing",
                        package=package,
                        details="Package requisitado mas não instalado",
                        severity="critical",
                        affected_projects=requesters,
                    ),
                )

        # 3. Packages órfãos
        all_required = set(package_requesters.keys())
        installed_names = set(self.installed_packages.keys())
        orphans = installed_names - all_required

        # Remove packages conhecidos do sistema
        system_packages = {
            "pip",
            "setuptools",
            "wheel",
            "poetry",
            "poetry-core",
            "pkg-resources",
            "pkg_resources",
            "distlib",
            "virtualenv",
        }
        orphans -= system_packages

        for orphan in orphans:
            self.conflicts.append(
                VenvConflict(
                    type="orphan",
                    package=orphan,
                    details="Package instalado mas não requisitado por nenhum projeto",
                    severity="info",
                    affected_projects=[],
                ),
            )

        print_colored(
            f"    ✅ {len(self.conflicts)} conflitos identificados",
            Colors.GREEN,
        )

    def _organize_conflicts_by_severity(self) -> dict[str, list[VenvConflict]]:
        """Organiza conflitos por severidade."""
        organized: dict[str, list[VenvConflict]] = {
            "critical": [],
            "warning": [],
            "info": [],
        }

        for conflict in self.conflicts:
            organized[conflict.severity].append(conflict)

        return organized

    def _print_validation_summary(
        self,
        conflicts_by_severity: dict[str, list[VenvConflict]],
    ) -> None:
        """Imprime resumo da validação."""
        print_colored("\n" + "=" * 60, Colors.CYAN)
        print_colored("📊 RESUMO DA VALIDAÇÃO DE CONSISTÊNCIA", Colors.CYAN)
        print_colored("=" * 60, Colors.CYAN)

        total_installed = len(self.installed_packages)
        total_projects = len(self.project_requirements)
        total_conflicts = len(self.conflicts)

        print_colored(f"📦 Packages instalados: {total_installed}", Colors.BLUE)
        print_colored(f"📂 Projetos escaneados: {total_projects}", Colors.BLUE)
        print_colored(f"⚠️ Conflitos encontrados: {total_conflicts}", Colors.BLUE)

        # Exibe conflitos por severidade
        for severity, conflicts in conflicts_by_severity.items():
            if not conflicts:
                continue

            if severity == "critical":
                icon, color = "🔴", Colors.RED
            elif severity == "warning":
                icon, color = "🟡", Colors.YELLOW
            else:
                icon, color = "[INFO]", Colors.CYAN

            print_colored(
                f"\n{icon} {severity.upper()}: {len(conflicts)} conflitos",
                color,
            )

            for conflict in conflicts[:MAX_CONFLICTS_DISPLAY]:
                print_colored(f"  • {conflict.package}: {conflict.details}", color)

                if conflict.affected_projects:
                    projects_str = ", ".join(
                        conflict.affected_projects[:MAX_PROJECTS_DISPLAY],
                    )
                    if len(conflict.affected_projects) > MAX_PROJECTS_DISPLAY:
                        projects_str += f" e mais {len(conflict.affected_projects) - 5}"
                    print_colored(f"    🎯 Projetos afetados: {projects_str}", color)

            if len(conflicts) > MAX_CONFLICTS_DISPLAY:
                print_colored(f"    ... e mais {len(conflicts) - 10} conflitos", color)

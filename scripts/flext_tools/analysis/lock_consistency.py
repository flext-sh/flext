"""Detecção de inconsistências no poetry.lock entre projetos do workspace"""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from flext_tools.utils import Colors, print_colored


@dataclass
class LockFileEntry:
    """Representa uma entrada no poetry.lock."""

    name: str
    version: str
    hash: str | None = None
    dependencies: dict[str, str] | None = None


@dataclass
class ProjectLockInfo:
    """Informações sobre o poetry.lock de um projeto."""

    project_name: str
    lock_path: Path
    exists: bool
    packages: dict[str, LockFileEntry]
    lock_version: str | None = None
    python_versions: list[str] | None = None


@dataclass
class LockInconsistency:
    """Representa uma inconsistência entre arquivos lock."""

    package: str
    type: str  # "version", "missing", "hash"
    details: dict[str, str]  # project -> version/status
    severity: str  # "critical", "warning", "info"


class LockConsistencyAnalyzer:
    """Analisa consistência entre arquivos poetry.lock no workspace."""

    def __init__(self):
        self.project_locks: dict[str, ProjectLockInfo] = {}
        self.inconsistencies: list[LockInconsistency] = []

    def analyze_workspace(
        self, workspace_path: Path
    ) -> dict[str, list[LockInconsistency]]:
        """
        Analisa todos os poetry.lock no workspace.

        Returns:
            Dict com categorias de inconsistências
        """
        print_colored(
            "🔍 Analisando consistência de poetry.lock no workspace...", Colors.BLUE
        )

        # Descobre todos os projetos
        projects = self._discover_projects(workspace_path)
        print_colored(f"  📁 Encontrados {len(projects)} projetos", Colors.CYAN)

        # Carrega informações de lock de cada projeto
        for project_path in projects:
            self._load_project_lock(project_path)

        # Analisa inconsistências
        self._analyze_inconsistencies()

        # Categoriza resultados
        return self._categorize_inconsistencies()

    def _discover_projects(self, workspace_path: Path) -> list[Path]:
        """Descobre projetos no workspace que têm pyproject.toml."""
        projects = []

        for item in workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                pyproject_path = item / "pyproject.toml"
                if pyproject_path.exists():
                    projects.append(item)

        return sorted(projects)

    def _load_project_lock(self, project_path: Path):
        """Carrega informações do poetry.lock de um projeto."""
        project_name = project_path.name
        lock_path = project_path / "poetry.lock"

        if not lock_path.exists():
            self.project_locks[project_name] = ProjectLockInfo(
                project_name=project_name,
                lock_path=lock_path,
                exists=False,
                packages={},
            )
            return

        try:
            packages = {}
            with open(lock_path, encoding="utf-8") as f:
                data = tomllib.loads(f.read())

            # Extrai informações dos packages
            for package_data in data.get("package", []):
                name = package_data.get("name", "").lower()
                version = package_data.get("version", "")

                # Extrai hash se disponível
                files = package_data.get("files", [])
                hash_value = None
                if files and isinstance(files[0], dict):
                    hash_value = files[0].get("hash", "")

                # Extrai dependências
                dependencies = package_data.get("dependencies", {})

                packages[name] = LockFileEntry(
                    name=name,
                    version=version,
                    hash=hash_value,
                    dependencies=dependencies,
                )

            # Extrai metadados
            metadata = data.get("metadata", {})
            lock_version = metadata.get("lock-version", "")
            python_versions = metadata.get("python-versions", "")

            self.project_locks[project_name] = ProjectLockInfo(
                project_name=project_name,
                lock_path=lock_path,
                exists=True,
                packages=packages,
                lock_version=lock_version,
                python_versions=[python_versions] if python_versions else [],
            )

            print_colored(
                f"    ✅ {project_name}: {len(packages)} packages", Colors.GREEN
            )

        except Exception as e:
            print_colored(
                f"    ❌ {project_name}: Erro ao ler poetry.lock - {e}", Colors.RED
            )
            self.project_locks[project_name] = ProjectLockInfo(
                project_name=project_name,
                lock_path=lock_path,
                exists=False,
                packages={},
            )

    def _analyze_inconsistencies(self):
        """Analisa inconsistências entre os arquivos lock."""
        print_colored("🔍 Detectando inconsistências...", Colors.BLUE)

        # Projetos válidos (com lock files)
        valid_projects = {
            name: info
            for name, info in self.project_locks.items()
            if info.exists and info.packages
        }

        if len(valid_projects) < 2:
            print_colored(
                "  ⚠️ Menos de 2 projetos com poetry.lock válidos", Colors.YELLOW
            )
            return

        # Coleta todos os packages únicos
        all_packages = set()
        for project_info in valid_projects.values():
            all_packages.update(project_info.packages.keys())

        print_colored(
            f"  📦 Analisando {len(all_packages)} packages únicos", Colors.CYAN
        )

        # Analisa cada package
        for package in sorted(all_packages):
            self._analyze_package_consistency(package, valid_projects)

    def _analyze_package_consistency(
        self, package: str, projects: dict[str, ProjectLockInfo]
    ):
        """Analisa consistência de um package específico."""

        # Coleta versões por projeto
        versions = {}
        projects_with_package = []

        for project_name, project_info in projects.items():
            if package in project_info.packages:
                entry = project_info.packages[package]
                versions[project_name] = entry.version
                projects_with_package.append(project_name)

        # Verifica se há versões diferentes
        unique_versions = set(versions.values())

        if len(unique_versions) > 1:
            # Versões diferentes - inconsistência crítica
            self.inconsistencies.append(
                LockInconsistency(
                    package=package,
                    type="version",
                    details=versions,
                    severity="critical"
                    if len(projects_with_package) > len(projects) / 2
                    else "warning",
                )
            )

        # Verifica se package está em poucos projetos mas deveria estar em mais
        if (
            len(projects_with_package) < len(projects) * 0.3
        ):  # Menos de 30% dos projetos
            missing_projects = [
                name for name in projects if name not in projects_with_package
            ]

            if len(missing_projects) > 1:
                details = dict.fromkeys(missing_projects, "missing")
                details.update(versions)

                self.inconsistencies.append(
                    LockInconsistency(
                        package=package,
                        type="missing",
                        details=details,
                        severity="info",
                    )
                )

    def _categorize_inconsistencies(self) -> dict[str, list[LockInconsistency]]:
        """Categoriza inconsistências por tipo e severidade."""
        categories = {"critical": [], "warning": [], "info": []}

        for inconsistency in self.inconsistencies:
            categories[inconsistency.severity].append(inconsistency)

        # Report summary
        total = len(self.inconsistencies)
        if total > 0:
            print_colored(f"\n📊 Inconsistências encontradas: {total}", Colors.YELLOW)
            print_colored(f"  🔴 Críticas: {len(categories['critical'])}", Colors.RED)
            print_colored(f"  🟡 Avisos: {len(categories['warning'])}", Colors.YELLOW)
            print_colored(f"  ℹ️ Info: {len(categories['info'])}", Colors.CYAN)
        else:
            print_colored("\n✅ Nenhuma inconsistência detectada", Colors.GREEN)

        return categories

    def get_workspace_summary(self) -> dict[str, any]:
        """Retorna resumo do estado do workspace."""
        projects_with_lock = sum(1 for p in self.project_locks.values() if p.exists)
        total_projects = len(self.project_locks)

        # Versões Python únicas
        python_versions = set()
        for project_info in self.project_locks.values():
            if project_info.python_versions:
                python_versions.update(project_info.python_versions)

        # Lock versions únicas
        lock_versions = set()
        for project_info in self.project_locks.values():
            if project_info.lock_version:
                lock_versions.add(project_info.lock_version)

        return {
            "total_projects": total_projects,
            "projects_with_lock": projects_with_lock,
            "coverage": projects_with_lock / total_projects
            if total_projects > 0
            else 0,
            "python_versions": sorted(python_versions),
            "lock_versions": sorted(lock_versions),
            "total_inconsistencies": len(self.inconsistencies),
        }

    def print_detailed_report(self, categories: dict[str, list[LockInconsistency]]):
        """Imprime relatório detalhado das inconsistências."""

        for severity, inconsistencies in categories.items():
            if not inconsistencies:
                continue

            color = (
                Colors.RED
                if severity == "critical"
                else (Colors.YELLOW if severity == "warning" else Colors.CYAN)
            )

            severity_label = {
                "critical": "🔴 CRÍTICAS",
                "warning": "🟡 AVISOS",
                "info": "ℹ️ INFORMAÇÕES",
            }.get(severity, severity.upper())

            print_colored(f"\n{severity_label} ({len(inconsistencies)}):", color)

            for inconsistency in inconsistencies[:10]:  # Limite de 10 por categoria
                print_colored(
                    f"  📦 {inconsistency.package} ({inconsistency.type}):", color
                )

                for project, value in sorted(inconsistency.details.items()):
                    status_emoji = "❌" if value == "missing" else "📌"
                    print_colored(f"    {status_emoji} {project}: {value}", color)

            if len(inconsistencies) > 10:
                print_colored(
                    f"    ... e mais {len(inconsistencies) - 10} itens", color
                )

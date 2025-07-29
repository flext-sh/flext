"""Análise de conflitos entre projetos."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, Any

from flext_tools.analysis.lock_consistency import LockConsistencyAnalyzer
from flext_tools.analysis.version import VersionAnalyzer
from flext_tools.utils import Colors, print_colored

if TYPE_CHECKING:
    from pathlib import Path


# Constants
MIN_PROJECTS_FOR_ANALYSIS = 2


class ConflictAnalyzer:
    """Analisa conflitos de dependências entre projetos."""

    def __init__(self) -> None:
        """Initialize conflict analyzer."""
        self.version_analyzer = VersionAnalyzer()

    def analyze_workspace_conflicts(self, workspace_path: Path) -> dict[str, Any]:
        """Analisa conflitos de dependências no workspace."""
        print_colored("🔍 Analisando conflitos de dependências...", Colors.BLUE)

        # Coleta dados de todos os projetos
        projects_data = {}
        for project_path in workspace_path.iterdir():
            if project_path.is_dir() and not project_path.name.startswith("."):
                pyproject_path = project_path / "pyproject.toml"
                if pyproject_path.exists():
                    try:
                        with pyproject_path.open("rb") as f:
                            data = tomllib.load(f)
                        projects_data[project_path.name] = data
                    except (OSError, tomllib.TOMLDecodeError) as e:
                        print_colored(
                            f"  ⚠️ Erro ao ler {project_path.name}: {e}",
                            Colors.YELLOW,
                        )

        if len(projects_data) < MIN_PROJECTS_FOR_ANALYSIS:
            print_colored("  [INFO] Menos de 2 projetos encontrados", Colors.CYAN)
            return {"conflicts": [], "summary": {"total": 0}}

        # Coleta dependências do workspace
        workspace_deps = self._collect_workspace_dependencies(workspace_path)

        # Analisa conflitos de versão
        version_conflicts = self.version_analyzer.analyze_version_conflicts(
            projects_data,
        )

        # Analisa conflitos de lock
        lock_analyzer = self._get_lock_analyzer()
        lock_analyzer.analyze_workspace(workspace_path)

        # Identifica bloqueadores
        blockers = self._identify_update_blockers(workspace_deps)

        # Sugere resoluções - converte formato de conflitos
        conflicts_for_resolution = {}
        for package, conflict_list in version_conflicts.items():
            if conflict_list:
                conflicts_for_resolution[package] = conflict_list[0]

        resolutions = self.version_analyzer.suggest_version_resolution(
            conflicts_for_resolution,
        )

        return {
            "total_projects": len(projects_data),
            "version_conflicts": version_conflicts,
            "update_blockers": blockers,
            "suggested_resolutions": resolutions,
            "stats": self._calculate_stats(workspace_deps, version_conflicts, blockers),
        }

    def _collect_workspace_dependencies(
        self,
        workspace_path: Path,
    ) -> dict[str, dict[str, str]]:
        """Coleta todas as dependências do workspace."""
        dependencies = {}

        # Procura por projetos Python
        for pyproject in workspace_path.rglob("pyproject.toml"):
            # Ignora diretórios especiais
            if any(
                p in pyproject.parts
                for p in ["archive", "backup", "node_modules", ".git"]
            ):
                continue

            project_name = pyproject.parent.name
            deps = self._extract_project_dependencies(pyproject)

            if deps:
                dependencies[project_name] = deps

        return dependencies

    def _extract_project_dependencies(self, pyproject_path: Path) -> dict[str, str]:
        """Extrai dependências de um arquivo pyproject.toml."""
        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            print_colored(f"  ⚠️ Erro ao ler {pyproject_path}: {e}", Colors.YELLOW)
            return {}
        else:
            deps = {}

            # Dependências principais
            main_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for name, spec in main_deps.items():
                if name != "python":
                    version_str = self._extract_version_string(spec)
                    deps[name] = version_str

            # Dependências de grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get("dependencies", {})
                for name, spec in group_deps.items():
                    version_str = self._extract_version_string(spec)
                    deps[f"{name}[{group_name}]"] = version_str

            return deps

    def _extract_version_string(self, spec: str | dict[str, Any]) -> str:
        """Extrai string de versão de uma especificação."""
        if isinstance(spec, str):
            return spec
        if isinstance(spec, dict):
            version = spec.get("version", "*")
            return str(version)
        return "*"

    def _identify_update_blockers(
        self,
        workspace_deps: dict[str, dict[str, str]],
    ) -> dict[str, dict[str, Any]]:
        """Identifica projetos que bloqueiam atualizações."""
        blockers: dict[str, dict[str, Any]] = {}

        # Conta quantas vezes cada constraint aparece
        constraint_usage: dict[str, dict[str, list[str]]] = {}
        for project, deps in workspace_deps.items():
            for package, constraint in deps.items():
                # Remove sufixo de grupo [dev], [test], etc
                base_package = package.split("[")[0]

                if base_package not in constraint_usage:
                    constraint_usage[base_package] = {}

                if constraint not in constraint_usage[base_package]:
                    constraint_usage[base_package][constraint] = []

                constraint_usage[base_package][constraint].append(project)

        # Identifica bloqueadores (projetos com constraints únicas ou restritivas)
        for package, constraints in constraint_usage.items():
            if len(constraints) > 1:
                # Há múltiplas constraints diferentes
                for constraint, projects in constraints.items():
                    if self._is_restrictive_constraint(constraint):
                        if package not in blockers:
                            blockers[package] = {
                                "blocking_projects": [],
                                "constraints": {},
                            }

                        blockers[package]["blocking_projects"].extend(projects)
                        blockers[package]["constraints"][constraint] = projects

        return blockers

    def _is_restrictive_constraint(self, constraint: str) -> bool:
        """Verifica se uma constraint é restritiva."""
        if not constraint or constraint == "*":
            return False

        # Constraints com == são as mais restritivas
        if constraint.startswith("=="):
            return True

        # Constraints com upper bound também são restritivas
        if "<" in constraint:
            return True

        # Caret com versão 0.x é restritiva
        return bool(constraint.startswith("^0."))

    def _calculate_stats(
        self,
        workspace_deps: dict[str, dict[str, str]],
        conflicts: dict[str, Any],
        blockers: dict[str, dict[str, Any]],
    ) -> dict[str, int]:
        """Calcula estatísticas da análise."""
        total_deps = sum(len(deps) for deps in workspace_deps.values())
        unique_packages = set()

        for deps in workspace_deps.values():
            for package in deps:
                base_package = package.split("[")[0]
                unique_packages.add(base_package)

        return {
            "total_dependencies": total_deps,
            "unique_packages": len(unique_packages),
            "packages_with_conflicts": len(conflicts),
            "blocking_packages": len(blockers),
            "affected_projects": len(
                {
                    project
                    for blocker_data in blockers.values()
                    for project in blocker_data["blocking_projects"]
                },
            ),
        }

    def generate_conflict_report(self, analysis: dict[str, Any]) -> str:
        """Gera relatório formatado de conflitos."""
        lines = []
        lines.append("# 📊 Relatório de Conflitos de Dependências\n")

        # Estatísticas gerais
        stats = analysis["stats"]
        lines.extend(
            (
                "## 📈 Estatísticas Gerais\n",
                f"- **Total de projetos**: {analysis['total_projects']}",
                f"- **Total de dependências**: {stats['total_dependencies']}",
                f"- **Pacotes únicos**: {stats['unique_packages']}",
                f"- **Pacotes com conflitos**: {stats['packages_with_conflicts']}",
                f"- **Pacotes bloqueadores**: {stats['blocking_packages']}",
                f"- **Projetos afetados**: {stats['affected_projects']}\n",
            ),
        )

        # Conflitos de versão
        if analysis["version_conflicts"]:
            lines.append("## ⚠️ Conflitos de Versão\n")

            for package, conflict_data in sorted(analysis["version_conflicts"].items()):
                severity = conflict_data.get("severity", "medium")
                icon = "🔴" if severity == "high" else "🟡"

                lines.extend((f"### {icon} {package}\n", "**Projetos e versões:**"))

                for project, version in conflict_data["projects"].items():
                    lines.append(f"- `{project}`: {version}")

                if conflict_data["analysis"]["issues"]:
                    lines.append("\n**Problemas:**")
                    lines.extend(
                        f"- {issue}" for issue in conflict_data["analysis"]["issues"]
                    )

                lines.append("")

        # Bloqueadores de atualização
        if analysis["update_blockers"]:
            lines.append("## 🚫 Bloqueadores de Atualização\n")

            for package, blocker_data in sorted(analysis["update_blockers"].items()):
                lines.extend((f"### {package}\n", "**Projetos bloqueadores:**"))

                for constraint, projects in blocker_data["constraints"].items():
                    lines.append(f"- Constraint `{constraint}`: {', '.join(projects)}")

                lines.append("")

        # Resoluções sugeridas
        if analysis["suggested_resolutions"]:
            lines.append("## 💡 Resoluções Sugeridas\n")

            for package, suggestion in sorted(
                analysis["suggested_resolutions"].items(),
            ):
                lines.append(f"- **{package}**: `{suggestion}`")

        return "\n".join(lines)

    def _get_lock_analyzer(self) -> LockConsistencyAnalyzer:
        """Get lock analyzer instance."""
        return LockConsistencyAnalyzer()

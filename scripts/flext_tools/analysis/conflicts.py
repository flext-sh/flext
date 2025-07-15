"""Análise de conflitos entre projetos"""

import tomllib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from flext_tools.analysis.version import VersionAnalyzer
from flext_tools.utils import Colors, print_colored


class ConflictAnalyzer:
    """Analisa conflitos de dependências entre projetos."""

    def __init__(self):
        self.version_analyzer = VersionAnalyzer()

    def analyze_workspace_conflicts(self, workspace_path: Path) -> dict[str, any]:
        """
        Analisa conflitos de dependências em todo o workspace.

        Args:
            workspace_path: Caminho para o workspace

        Returns:
            Dicionário com análise completa de conflitos
        """
        print_colored("🔍 Analisando conflitos no workspace...", Colors.BLUE)

        # Coleta todas as dependências
        workspace_deps = self._collect_workspace_dependencies(workspace_path)

        # Analisa conflitos de versão
        version_conflicts = self.version_analyzer.analyze_version_conflicts(
            workspace_deps
        )

        # Identifica bloqueadores
        blockers = self._identify_update_blockers(workspace_deps)

        # Sugere resoluções
        resolutions = self.version_analyzer.suggest_version_resolution(
            version_conflicts
        )

        return {
            "total_projects": len(workspace_deps),
            "version_conflicts": version_conflicts,
            "update_blockers": blockers,
            "suggested_resolutions": resolutions,
            "stats": self._calculate_stats(workspace_deps, version_conflicts, blockers),
        }

    def _collect_workspace_dependencies(
        self, workspace_path: Path
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
        """Extrai dependências de um pyproject.toml."""
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

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

        except Exception as e:
            print_colored(f"  ⚠️ Erro ao ler {pyproject_path}: {e}", Colors.YELLOW)
            return {}

    def _extract_version_string(self, spec: any) -> str:
        """Extrai string de versão de uma especificação."""
        if isinstance(spec, str):
            return spec
        if isinstance(spec, dict):
            return spec.get("version", "*")
        return "*"

    def _identify_update_blockers(
        self, workspace_deps: dict[str, dict[str, str]]
    ) -> dict[str, dict]:
        """Identifica projetos que bloqueiam atualizações."""
        blockers = {}

        # Conta quantas vezes cada constraint aparece
        constraint_usage = {}
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
        conflicts: dict[str, any],
        blockers: dict[str, any],
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
                }
            ),
        }

    def generate_conflict_report(self, analysis: dict[str, any]) -> str:
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
            )
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
                analysis["suggested_resolutions"].items()
            ):
                lines.append(f"- **{package}**: `{suggestion}`")

        return "\n".join(lines)

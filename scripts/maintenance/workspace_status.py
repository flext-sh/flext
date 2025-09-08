#!/usr/bin/env python3
"""FLEXT Workspace Status - Dashboard Completo do Workspace.

Script para mostrar status detalhado e saúde geral do workspace FLEXT,
incluindo projetos, dependências, qualidade e métricas de desenvolvimento.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_core import FlextResult

from flext_tools import Colors, ScriptMetadata, print_colored


class WorkspaceStatus:
    """Script para dashboard completo do workspace FLEXT."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="workspace_status",
            description="Dashboard completo do workspace FLEXT com métricas e status",
            category="maintenance",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validar se estamos no workspace FLEXT."""
        workspace_root = Path.cwd()
        flext_projects = [
            p
            for p in workspace_root.iterdir()
            if p.is_dir() and p.name.startswith("flext-")
        ]

        if not flext_projects:
            print_colored("❌ Execute do diretório raiz do workspace FLEXT", Colors.RED)
            return FlextResult[None].fail("Not in FLEXT workspace root")

        return FlextResult[None].ok(None)

    def execute_main_logic(self, **_kwargs: object) -> FlextResult[object]:
        """Executar análise completa do workspace."""
        try:
            workspace_root = Path.cwd()

            print_colored("📊 DASHBOARD DO WORKSPACE FLEXT", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # 1. Análise de projetos
            projects_info = self._analyze_projects(workspace_root)
            self._print_projects_summary(projects_info)

            # 2. Análise de qualidade
            quality_info = self._analyze_quality(workspace_root, projects_info)
            self._print_quality_summary(quality_info)

            # 3. Análise de dependências
            deps_info = self._analyze_dependencies(workspace_root, projects_info)
            self._print_dependencies_summary(deps_info)

            # 4. Health Score
            health_score = self._calculate_health_score(
                projects_info,
                quality_info,
                deps_info,
            )
            self._print_health_score(health_score)

            return FlextResult[object].ok(
                {
                    "projects_info": projects_info,
                    "quality_info": quality_info,
                    "deps_info": deps_info,
                    "health_score": health_score,
                },
            )

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Erro durante análise: {e}", Colors.RED)
            return FlextResult[object].fail(f"Analysis error: {e}")

    def _analyze_projects(self, workspace_root: Path) -> FlextTypes.Core.Dict:
        """Analisar projetos do workspace."""
        projects = {}

        for item in workspace_root.iterdir():
            if item.is_dir() and (item / "pyproject.toml").exists():
                if any(
                    skip in item.name
                    for skip in [".git", ".venv", "node_modules", "__pycache__"]
                ):
                    continue

                projects[item.name] = {
                    "path": item,
                    "has_src": (item / "src").exists(),
                    "has_tests": (item / "tests").exists(),
                    "has_makefile": (item / "Makefile").exists(),
                    "python_files": len(list(item.rglob("*.py"))),
                    "type": self._detect_project_type(item),
                }

        return {
            "projects": projects,
            "total_count": len(projects),
            "framework_count": len(
                [p for p in projects.values() if p["type"] == "framework"],
            ),
            "tap_count": len([p for p in projects.values() if p["type"] == "tap"]),
            "target_count": len(
                [p for p in projects.values() if p["type"] == "target"],
            ),
        }

    def _detect_project_type(self, project_path: Path) -> str:
        """Detectar tipo do projeto."""
        name = project_path.name
        if name.startswith("flext-tap-"):
            return "tap"
        if name.startswith("flext-target-"):
            return "target"
        if name.startswith("flext-dbt-"):
            return "dbt"
        if name.startswith("flext-"):
            return "framework"
        return "enterprise"

    def _analyze_quality(
        self,
        _workspace_root: Path,
        projects_info: FlextTypes.Core.Dict,
    ) -> FlextTypes.Core.Dict:
        """Analisar qualidade do código."""
        quality_data = {
            "total_python_files": 0,
            "projects_with_tests": 0,
            "projects_with_makefiles": 0,
            "lint_issues": 0,
            "type_issues": 0,
        }

        for project_data in projects_info["projects"].values():
            quality_data["total_python_files"] += project_data["python_files"]
            if project_data["has_tests"]:
                quality_data["projects_with_tests"] += 1
            if project_data["has_makefile"]:
                quality_data["projects_with_makefiles"] += 1

        return quality_data

    def _analyze_dependencies(
        self,
        _workspace_root: Path,
        projects_info: FlextTypes.Core.Dict,
    ) -> FlextTypes.Core.Dict:
        """Analisar dependências."""
        deps_data = {
            "projects_with_poetry": 0,
            "total_dependencies": 0,
            "conflicts_detected": 0,
        }

        for project_data in projects_info["projects"].values():
            project_path = project_data["path"]
            if (project_path / "poetry.lock").exists():
                deps_data["projects_with_poetry"] += 1

        return deps_data

    def _calculate_health_score(
        self,
        projects: FlextTypes.Core.Dict,
        quality: FlextTypes.Core.Dict,
        deps: FlextTypes.Core.Dict,
    ) -> FlextTypes.Core.Dict:
        """Calcular health score do workspace."""
        total_projects = projects["total_count"]

        if total_projects == 0:
            return {"score": 0, "grade": "F", "issues": ["Nenhum projeto encontrado"]}

        # Pontuação baseada em várias métricas
        score = 0
        max_score = 100
        issues = []

        # Estrutura dos projetos (30 pontos)
        if projects["total_count"] >= 20:
            score += 15
        elif projects["total_count"] >= 10:
            score += 10
        else:
            score += 5
            issues.append(f"Poucos projetos ({projects['total_count']})")

        # Cobertura de testes (25 pontos)
        test_coverage = quality["projects_with_tests"] / total_projects
        score += int(test_coverage * 25)
        if test_coverage < 0.8:
            issues.append(f"Baixa cobertura de testes ({test_coverage:.1%})")

        # Makefiles padronizados (20 pontos)
        makefile_coverage = quality["projects_with_makefiles"] / total_projects
        score += int(makefile_coverage * 20)
        if makefile_coverage < 0.9:
            issues.append(f"Makefiles faltando ({makefile_coverage:.1%})")

        # Poetry setup (15 pontos)
        poetry_coverage = deps["projects_with_poetry"] / total_projects
        score += int(poetry_coverage * 15)
        if poetry_coverage < 0.8:
            issues.append(f"Poetry não configurado ({poetry_coverage:.1%})")

        # Arquivos Python (10 pontos)
        if quality["total_python_files"] > 1000:
            score += 10
        elif quality["total_python_files"] > 500:
            score += 7
        else:
            score += 4
            issues.append(f"Poucos arquivos Python ({quality['total_python_files']})")

        # Determinar grade
        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": score,
            "grade": grade,
            "issues": issues,
            "max_score": max_score,
        }

    def _print_projects_summary(self, projects_info: FlextTypes.Core.Dict) -> None:
        """Imprimir resumo dos projetos."""
        projects = projects_info["projects"]
        total_count = projects_info["total_count"]

        print_colored(f"\n📁 PROJETOS ENCONTRADOS: {total_count}", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

        # Agrupar por tipo
        by_type: dict[str, FlextTypes.Core.StringList] = {}
        for name, data in projects.items():
            project_type = data["type"]
            if project_type not in by_type:
                by_type[project_type] = []
            by_type[project_type].append(name)

        for project_type, names in by_type.items():
            print_colored(f"\n🔧 {project_type.upper()}: {len(names)}", Colors.CYAN)
            for name in sorted(names):
                data = projects[name]
                "✅" if data["has_tests"] else "⚠️"

    def _print_quality_summary(self, _quality_info: FlextTypes.Core.Dict) -> None:
        """Imprimir resumo da qualidade."""
        print_colored("\n📊 QUALIDADE DO CÓDIGO", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

    def _print_dependencies_summary(self, _deps_info: FlextTypes.Core.Dict) -> None:
        """Imprimir resumo das dependências."""
        print_colored("\n📦 DEPENDÊNCIAS", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

    def _print_health_score(self, health: FlextTypes.Core.Dict) -> None:
        """Imprimir health score."""
        print_colored("\n🏥 HEALTH SCORE DO WORKSPACE", Colors.BLUE)

        # Cor baseada no score
        if health["score"] >= 80:
            score_color = Colors.GREEN
        elif health["score"] >= 60:
            score_color = Colors.YELLOW
        else:
            score_color = Colors.RED

        print_colored(
            f"  Score: {health['score']}/{health['max_score']} (Grade: {health['grade']})",
            score_color,
        )

        if health["issues"]:
            print_colored("\n⚠️ Issues identificadas:", Colors.YELLOW)
            for _issue in health["issues"]:
                pass

        print_colored(
            f"\n{'🎉' if health['score'] >= 80 else '⚠️'} "
            "Workspace Status: "
            f"{'EXCELLENT' if health['score'] >= 90 else 'GOOD' if health['score'] >= 80 else 'NEEDS IMPROVEMENT' if health['score'] >= 60 else 'CRITICAL'}",
            score_color,
        )


def main() -> int:
    """Função principal."""
    script = WorkspaceStatus()
    try:
        result = script.execute_main_logic()
        if result.is_success:
            return 0
        print_colored(f"❌ Erro: {result.error}", Colors.RED)
        return 1
    except Exception as e:
        print_colored(f"❌ Erro inesperado: {e}", Colors.RED)
        return 1
    """Função principal."""
    script = WorkspaceStatus()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())

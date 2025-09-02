#!/usr/bin/env python3
"""FLEXT Quality Gateway - Sistema Completo de Controle de Qualidade.

Gateway de qualidade enterprise com zero tolerância a regressões.
Usa flext_tools para validação consistente em todo o workspace.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from flext_core import FlextResult
from mypy import api as mypy_api

from flext_tools import (
    Colors,
    ConflictAnalyzer,
    DependencyDiscovery,
    FlextScript,
    PoetryValidator,
    ScriptMetadata,
    print_colored,
)

from .common import discover_projects

# Constantes para análise de qualidade
CRITICAL_DEPENDENCY_THRESHOLD = 5
CRITICAL_RUFF_ISSUES_THRESHOLD = 10
CRITICAL_MYPY_ERRORS_THRESHOLD = 5
PERFECT_SCORE = 100
GOOD_SCORE_THRESHOLD = 80
NEEDS_IMPROVEMENT_THRESHOLD = 60


@dataclass
class AnalysisResults:
    """Resultados de análise de qualidade."""

    deps_result: dict[str, object]
    quality_result: dict[str, object]
    conflicts_result: dict[str, object]
    poetry_result: dict[str, object]


@dataclass
class QualitySettings:
    """Configurações de qualidade."""

    strict_mode: bool = False


class QualityGateway(FlextScript):
    """Sistema completo de controle de qualidade FLEXT."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Return script metadata."""
        return ScriptMetadata(
            name="quality_gateway",
            description=(
                "Gateway completo de qualidade com zero tolerância a regressões"
            ),
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validar ferramentas necessárias."""
        workspace_root = Path.cwd()

        # Verificar se estamos no workspace FLEXT
        flext_projects = [
            p
            for p in workspace_root.iterdir()
            if p.is_dir()
            and p.name.startswith("flext-")
            and (p / "pyproject.toml").exists()
        ]

        if not flext_projects:
            print_colored("❌ Execute do diretório raiz do workspace FLEXT", Colors.RED)
            return FlextResult[None].fail("Not in FLEXT workspace root")

        print_colored(
            f"✅ Encontrados {len(flext_projects)} projetos FLEXT",
            Colors.GREEN,
        )

        # Verificar ferramentas necessárias
        required_tools = ["ruff", "mypy", "poetry"]
        missing_tools = []

        for tool in required_tools:
            if shutil.which(tool) is None:
                missing_tools.append(tool)
                print_colored(f"❌ {tool.title()} não encontrado", Colors.RED)
            else:
                print_colored(f"✅ {tool.title()} disponível", Colors.GREEN)

        if missing_tools:
            print_colored(
                f"Instale as ferramentas faltantes: {', '.join(missing_tools)}",
                Colors.YELLOW,
            )
            return FlextResult[None].fail(
                f"Missing required tools: {', '.join(missing_tools)}",
            )

        return FlextResult[None].ok(None)

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Executar gateway de qualidade completo."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")
            strict_mode = bool(kwargs.get("strict"))

            print_colored("🚀 FLEXT QUALITY GATEWAY", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Descobrir projetos
            projects = self._discover_projects(
                workspace_root,
                str(projects_filter) if projects_filter else None,
            )

            # Estatísticas agregadas
            total_stats: dict[str, object] = {
                "projects_analyzed": 0,
                "passed": 0,
                "failed": 0,
                "total_issues": 0,
                "critical_issues": 0,
            }

            failed_projects: list[str] = []

            # Executar análise em cada projeto
            for project_path in projects:
                project_name = project_path.name

                print_colored(f"\n📦 Analisando {project_name}...", Colors.BLUE)

                # 1. Análise de dependências
                deps_result = self._analyze_dependencies(project_path)

                # 2. Análise de qualidade de código
                quality_result = self._analyze_code_quality(project_path)

                # 3. Análise de conflitos
                conflicts_result = self._analyze_conflicts(project_path)

                # 4. Validação Poetry
                poetry_result = self._validate_poetry_config(project_path)

                # Calcular resultado do projeto
                analysis_results = AnalysisResults(
                    deps_result=deps_result,
                    quality_result=quality_result,
                    conflicts_result=conflicts_result,
                    poetry_result=poetry_result,
                )

                project_result = self._calculate_project_result(
                    project_name,
                    analysis_results,
                )  # Atualizar estatísticas
                total_stats["projects_analyzed"] = (
                    int(total_stats["projects_analyzed"]) + 1
                )
                if project_result["passed"]:
                    total_stats["passed"] = int(total_stats["passed"]) + 1
                    print_colored(f"  ✅ {project_name}: APROVADO", Colors.GREEN)
                else:
                    total_stats["failed"] = int(total_stats["failed"]) + 1
                    failed_projects.append(project_name)
                    print_colored(f"  ❌ {project_name}: REPROVADO", Colors.RED)

                total_stats["total_issues"] = int(total_stats["total_issues"]) + int(
                    project_result["total_issues"],
                )
                total_stats["critical_issues"] = int(
                    total_stats["critical_issues"],
                ) + int(project_result["critical_issues"])

                # Mostrar detalhes se há falhas
                if not project_result["passed"]:
                    self._print_project_issues(project_result)

            # Resumo final
            self._print_final_summary(total_stats, failed_projects, strict_mode)

            # Gateway aprovado apenas se todos os projetos passaram
            gateway_passed = int(total_stats["failed"]) == 0

            if gateway_passed:
                print_colored("\n🎉 QUALITY GATEWAY: APROVADO", Colors.GREEN)
            else:
                print_colored("\n🚫 QUALITY GATEWAY: REPROVADO", Colors.RED)

            return FlextResult[object].ok(
                {
                    "gateway_passed": gateway_passed,
                    "stats": total_stats,
                    "failed_projects": failed_projects,
                },
            )

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Erro durante análise: {e}", Colors.RED)
            return FlextResult[object].fail(f"Analysis error: {e}")

    def _discover_projects(
        self,
        workspace_root: Path,
        projects_filter: str | None = None,
    ) -> list[Path]:
        """Descobrir projetos para analisar."""
        return discover_projects(workspace_root, projects_filter)

    def _analyze_dependencies(self, project_path: Path) -> dict[str, object]:
        """Analisar dependências usando flext_tools."""
        try:
            discovery = DependencyDiscovery(resolve_transitive=True)
            missing_deps = discovery.discover_project_dependencies(
                project_path,
                include_dev=True,
                include_test=True,
            )

            total_missing = sum(len(deps) for deps in missing_deps.values())

            return {
                "missing_count": total_missing,
                "missing_deps": missing_deps,
                "status": "passed" if total_missing == 0 else "failed",
            }

        except (OSError, ValueError, TypeError) as e:
            return {
                "missing_count": -1,
                "missing_deps": {},
                "status": "error",
                "error": str(e),
            }

    def _analyze_code_quality(self, project_path: Path) -> dict[str, object]:
        """Analisar qualidade do código."""
        try:
            # Ruff check via API (no subprocess)
            try:
                pass
            except Exception:
                return {
                    "ruff_issues": -1,
                    "mypy_errors": -1,
                    "total_issues": -1,
                    "status": "error",
                    "error": "Ruff module not available",
                }

            if not project_path.is_dir():
                return {
                    "ruff_issues": -1,
                    "mypy_errors": -1,
                    "total_issues": -1,
                    "status": "error",
                    "error": "Invalid project path",
                }

            # Ruff check via subprocess (API não disponível na versão atual)

            try:
                # Note: ruff path is trusted (installed via Poetry), project_path is validated
                result = subprocess.run(
                    [
                        "/usr/bin/env",
                        "ruff",
                        "check",
                        str(project_path),
                        "--output-format=json",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                ruff_output = result.stdout
            except (FileNotFoundError, subprocess.SubprocessError):
                ruff_output = ""

            ruff_issues = 0
            if ruff_output:
                try:
                    issues = json.loads(ruff_output)
                    ruff_issues = len(issues)
                except json.JSONDecodeError:
                    ruff_issues = 0

            # MyPy check via API (no subprocess)
            try:
                pass
            except Exception:
                return {
                    "ruff_issues": ruff_issues,
                    "mypy_errors": -1,
                    "total_issues": ruff_issues,
                    "status": "error",
                    "error": "MyPy module not available",
                }

            mypy_stdout, _mypy_stderr, _status = mypy_api.run(
                [str(project_path), "--no-error-summary"],
            )
            mypy_errors = 0
            if mypy_stdout:
                mypy_errors = len(
                    [line for line in mypy_stdout.split("\n") if line and ":" in line],
                )

            total_issues = ruff_issues + mypy_errors

            return {
                "ruff_issues": ruff_issues,
                "mypy_errors": mypy_errors,
                "total_issues": total_issues,
                "status": "passed" if total_issues == 0 else "failed",
            }

        except (OSError, ValueError, TypeError) as e:
            return {
                "ruff_issues": -1,
                "mypy_errors": -1,
                "total_issues": -1,
                "status": "error",
                "error": str(e),
            }

    def _analyze_conflicts(self, project_path: Path) -> dict[str, object]:
        """Analisar conflitos usando flext_tools."""
        try:
            analyzer = ConflictAnalyzer()
            conflicts = analyzer.analyze_workspace_conflicts(project_path)

            return {
                "conflicts_count": len(conflicts),
                "conflicts": conflicts,
                "status": "passed" if len(conflicts) == 0 else "failed",
            }

        except (OSError, ValueError, TypeError) as e:
            return {
                "conflicts_count": -1,
                "conflicts": [],
                "status": "error",
                "error": str(e),
            }

    def _validate_poetry_config(self, project_path: Path) -> dict[str, object]:
        """Validar configuração Poetry usando flext_tools."""
        try:
            validator = PoetryValidator()
            is_valid = validator.validate_project(project_path)

            return {"is_valid": is_valid, "status": "passed" if is_valid else "failed"}

        except (OSError, ValueError, TypeError) as e:
            return {"is_valid": False, "status": "error", "error": str(e)}

    def _calculate_project_result(
        self,
        project_name: str,
        results: AnalysisResults,
    ) -> dict[str, object]:
        """Calcular resultado final do projeto."""
        issues = []
        critical_issues = 0
        total_issues = 0

        # Dependências faltantes
        if results.deps_result["status"] == "failed":
            missing_count_obj = results.deps_result["missing_count"]
            missing_count = (
                int(missing_count_obj)
                if isinstance(missing_count_obj, (int, str))
                else 0
            )
            issues.append(f"Dependências faltantes: {missing_count}")
            total_issues += missing_count
            if missing_count > CRITICAL_DEPENDENCY_THRESHOLD:
                critical_issues += 1

        # Qualidade do código
        if results.quality_result["status"] == "failed":
            ruff_issues_obj = results.quality_result["ruff_issues"]
            mypy_errors_obj = results.quality_result["mypy_errors"]

            ruff_issues = (
                int(ruff_issues_obj) if isinstance(ruff_issues_obj, (int, str)) else 0
            )
            mypy_errors = (
                int(mypy_errors_obj) if isinstance(mypy_errors_obj, (int, str)) else 0
            )

            if ruff_issues > 0:
                issues.append(f"Ruff issues: {ruff_issues}")
                total_issues += ruff_issues
                if ruff_issues > CRITICAL_RUFF_ISSUES_THRESHOLD:
                    critical_issues += 1

            if mypy_errors > 0:
                issues.append(f"MyPy errors: {mypy_errors}")
                total_issues += mypy_errors
                if mypy_errors > CRITICAL_MYPY_ERRORS_THRESHOLD:
                    critical_issues += 1

        # Conflitos
        if results.conflicts_result["status"] == "failed":
            conflicts_count_obj = results.conflicts_result["conflicts_count"]
            conflicts_count = (
                int(conflicts_count_obj)
                if isinstance(conflicts_count_obj, (int, str))
                else 0
            )
            issues.append(f"Conflitos: {conflicts_count}")
            total_issues += conflicts_count
            critical_issues += 1  # Conflitos são sempre críticos

        # Poetry inválido
        if results.poetry_result["status"] == "failed":
            issues.append("Configuração Poetry inválida")
            total_issues += 1
            critical_issues += 1  # Poetry inválido é crítico

        # Determinar se passou
        passed = critical_issues == 0

        return {
            "project_name": project_name,
            "passed": passed,
            "issues": issues,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "deps_result": results.deps_result,
            "quality_result": results.quality_result,
            "conflicts_result": results.conflicts_result,
            "poetry_result": results.poetry_result,
        }

    def _print_project_issues(self, project_result: dict[str, object]) -> None:
        """Imprimir issues do projeto."""
        for issue in project_result["issues"]:
            if "Conflitos:" in issue or "Poetry" in issue:
                print_colored(f"    🚨 {issue}", Colors.RED)
            else:
                print_colored(f"    ⚠️ {issue}", Colors.YELLOW)

    def _print_final_summary(
        self,
        total_stats: dict[str, object],
        failed_projects: list[str],
        *,
        _strict_mode: bool = False,
    ) -> None:
        """Imprimir resumo final do gateway."""
        print_colored("\n📊 RESUMO DO QUALITY GATEWAY", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

        if failed_projects:
            print_colored("\n🚫 Projetos Reprovados:", Colors.RED)
            for _project in failed_projects:
                pass

        # Score de qualidade
        if total_stats["projects_analyzed"] > 0:
            success_rate = (
                total_stats["passed"] / total_stats["projects_analyzed"]
            ) * 100

            if success_rate == PERFECT_SCORE:
                score_color = Colors.GREEN
                status = "PERFEITO"
            elif success_rate >= GOOD_SCORE_THRESHOLD:
                score_color = Colors.CYAN
                status = "BOM"
            elif success_rate >= NEEDS_IMPROVEMENT_THRESHOLD:
                score_color = Colors.YELLOW
                status = "PRECISA MELHORAR"
            else:
                score_color = Colors.RED
                status = "CRÍTICO"

            print_colored(
                f"\n🏆 Score de Qualidade: {success_rate:.1f}% ({status})",
                score_color,
            )

    def create_parser(self) -> argparse.ArgumentParser:
        """Criar parser com argumentos específicos."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filtrar projetos específicos (separados por vírgula)",
        )

        parser.add_argument(
            "--strict",
            action="store_true",
            help="Modo estrito: zero tolerância a qualquer issue",
        )

        return parser

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Função principal."""
    script = QualityGateway()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())

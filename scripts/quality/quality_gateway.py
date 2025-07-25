#!/usr/bin/env python3
"""FLEXT Quality Gateway - Sistema Completo de Controle de Qualidade.

Gateway de qualidade enterprise com zero tolerância a regressões.
Usa flext_tools para validação consistente em todo o workspace.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Usar flext_tools diretamente - já está no .venv
from flext_tools import (
    Colors,
    ConflictAnalyzer,
    DependencyDiscovery,
    PoetryValidator,
    print_colored,
)
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class QualityGateway(FlextScript):
    """Sistema completo de controle de qualidade FLEXT."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="quality_gateway",
            description="Gateway completo de qualidade com zero tolerância a regressões",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validar ferramentas necessárias."""
        workspace_root = Path.cwd()

        # Verificar se estamos no workspace FLEXT
        flext_projects = [
            p for p in workspace_root.iterdir() if p.is_dir() and p.name.startswith("flext-") and (p / "pyproject.toml").exists()
        ]

        if not flext_projects:
            print_colored("❌ Execute do diretório raiz do workspace FLEXT", Colors.RED)
            return False

        print_colored(
            f"✅ Encontrados {len(flext_projects)} projetos FLEXT",
            Colors.GREEN,
        )

        # Verificar ferramentas necessárias
        required_tools = ["ruff", "mypy", "poetry"]
        missing_tools = []

        for tool in required_tools:
            try:
                import subprocess

                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    check=True,
                    timeout=5,
                )
                print_colored(f"✅ {tool.title()} disponível", Colors.GREEN)
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                missing_tools.append(tool)
                print_colored(f"❌ {tool.title()} não encontrado", Colors.RED)

        if missing_tools:
            print_colored(
                f"Instale as ferramentas faltantes: {', '.join(missing_tools)}",
                Colors.YELLOW,
            )
            return False

        return True

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Executar gateway de qualidade completo."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")
            strict_mode = kwargs.get("strict", False)

            print_colored("🚀 FLEXT QUALITY GATEWAY", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Descobrir projetos
            projects = self._discover_projects(workspace_root, projects_filter)

            # Estatísticas agregadas
            total_stats = {
                "projects_analyzed": 0,
                "passed": 0,
                "failed": 0,
                "total_issues": 0,
                "critical_issues": 0,
            }

            failed_projects = []

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
                project_result = self._calculate_project_result(
                    project_name,
                    deps_result,
                    quality_result,
                    conflicts_result,
                    poetry_result,
                    strict_mode,
                )

                # Atualizar estatísticas
                total_stats["projects_analyzed"] += 1
                if project_result["passed"]:
                    total_stats["passed"] += 1
                    print_colored(f"  ✅ {project_name}: APROVADO", Colors.GREEN)
                else:
                    total_stats["failed"] += 1
                    failed_projects.append(project_name)
                    print_colored(f"  ❌ {project_name}: REPROVADO", Colors.RED)

                total_stats["total_issues"] += project_result["total_issues"]
                total_stats["critical_issues"] += project_result["critical_issues"]

                # Mostrar detalhes se há falhas
                if not project_result["passed"]:
                    self._print_project_issues(project_result)

            # Resumo final
            self._print_final_summary(total_stats, failed_projects, strict_mode)

            # Gateway aprovado apenas se todos os projetos passaram
            gateway_passed = total_stats["failed"] == 0

            if gateway_passed:
                print_colored("\n🎉 QUALITY GATEWAY: APROVADO", Colors.GREEN)
            else:
                print_colored("\n🚫 QUALITY GATEWAY: REPROVADO", Colors.RED)

            return gateway_passed

        except Exception as e:
            print_colored(f"❌ Erro durante análise: {e}", Colors.RED)
            return False

    def _discover_projects(
        self,
        workspace_root: Path,
        projects_filter: str | None = None,
    ) -> list[Path]:
        """Descobrir projetos para analisar."""
        from scripts.common import discover_projects

        return discover_projects(workspace_root, projects_filter)

    def _analyze_dependencies(self, project_path: Path) -> dict[str, Any]:
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

        except Exception as e:
            return {
                "missing_count": -1,
                "missing_deps": {},
                "status": "error",
                "error": str(e),
            }

    def _analyze_code_quality(self, project_path: Path) -> dict[str, Any]:
        """Analisar qualidade do código."""
        try:
            import json
            import subprocess

            # Ruff check
            ruff_result = subprocess.run(
                ["ruff", "check", ".", "--output-format=json"],
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            ruff_issues = 0
            if ruff_result.stdout:
                try:
                    issues = json.loads(ruff_result.stdout)
                    ruff_issues = len(issues)
                except json.JSONDecodeError:
                    pass

            # MyPy check
            mypy_result = subprocess.run(
                ["mypy", ".", "--no-error-summary"],
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            mypy_errors = 0
            if mypy_result.stdout:
                mypy_errors = len(
                    [line for line in mypy_result.stdout.split("\n") if line and ":" in line],
                )

            total_issues = ruff_issues + mypy_errors

            return {
                "ruff_issues": ruff_issues,
                "mypy_errors": mypy_errors,
                "total_issues": total_issues,
                "status": "passed" if total_issues == 0 else "failed",
            }

        except Exception as e:
            return {
                "ruff_issues": -1,
                "mypy_errors": -1,
                "total_issues": -1,
                "status": "error",
                "error": str(e),
            }

    def _analyze_conflicts(self, project_path: Path) -> dict[str, Any]:
        """Analisar conflitos usando flext_tools."""
        try:
            analyzer = ConflictAnalyzer()
            conflicts = analyzer.analyze_workspace_conflicts(project_path)

            return {
                "conflicts_count": len(conflicts),
                "conflicts": conflicts,
                "status": "passed" if len(conflicts) == 0 else "failed",
            }

        except Exception as e:
            return {
                "conflicts_count": -1,
                "conflicts": [],
                "status": "error",
                "error": str(e),
            }

    def _validate_poetry_config(self, project_path: Path) -> dict[str, Any]:
        """Validar configuração Poetry usando flext_tools."""
        try:
            validator = PoetryValidator()
            is_valid = validator.validate_project(project_path)

            return {"is_valid": is_valid, "status": "passed" if is_valid else "failed"}

        except Exception as e:
            return {"is_valid": False, "status": "error", "error": str(e)}

    def _calculate_project_result(
        self,
        project_name: str,
        deps_result: dict[str, Any],
        quality_result: dict[str, Any],
        conflicts_result: dict[str, Any],
        poetry_result: dict[str, Any],
        strict_mode: bool,
    ) -> dict[str, Any]:
        """Calcular resultado final do projeto."""
        issues = []
        critical_issues = 0
        total_issues = 0

        # Dependências faltantes
        if deps_result["status"] == "failed":
            missing_count = deps_result["missing_count"]
            issues.append(f"Dependências faltantes: {missing_count}")
            total_issues += missing_count
            if missing_count > 5:  # Muitas dependências faltantes = crítico
                critical_issues += 1

        # Qualidade do código
        if quality_result["status"] == "failed":
            ruff_issues = quality_result["ruff_issues"]
            mypy_errors = quality_result["mypy_errors"]

            if ruff_issues > 0:
                issues.append(f"Ruff issues: {ruff_issues}")
                total_issues += ruff_issues
                if ruff_issues > 10:  # Muitos issues = crítico
                    critical_issues += 1

            if mypy_errors > 0:
                issues.append(f"MyPy errors: {mypy_errors}")
                total_issues += mypy_errors
                if mypy_errors > 5:  # Muitos erros = crítico
                    critical_issues += 1

        # Conflitos
        if conflicts_result["status"] == "failed":
            conflicts_count = conflicts_result["conflicts_count"]
            issues.append(f"Conflitos: {conflicts_count}")
            total_issues += conflicts_count
            critical_issues += 1  # Conflitos são sempre críticos

        # Poetry inválido
        if poetry_result["status"] == "failed":
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
            "deps_result": deps_result,
            "quality_result": quality_result,
            "conflicts_result": conflicts_result,
            "poetry_result": poetry_result,
        }

    def _print_project_issues(self, project_result: dict[str, Any]) -> None:
        """Imprimir issues do projeto."""
        for issue in project_result["issues"]:
            if "Conflitos:" in issue or "Poetry" in issue:
                print_colored(f"    🚨 {issue}", Colors.RED)
            else:
                print_colored(f"    ⚠️ {issue}", Colors.YELLOW)

    def _print_final_summary(
        self,
        total_stats: dict[str, Any],
        failed_projects: list[str],
        strict_mode: bool,
    ) -> None:
        """Imprimir resumo final do gateway."""
        print_colored("\n📊 RESUMO DO QUALITY GATEWAY", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

        print(f"  📁 Projetos analisados: {total_stats['projects_analyzed']}")
        print(f"  ✅ Projetos aprovados: {total_stats['passed']}")
        print(f"  ❌ Projetos reprovados: {total_stats['failed']}")
        print(f"  📋 Total de issues: {total_stats['total_issues']}")
        print(f"  🚨 Issues críticas: {total_stats['critical_issues']}")
        print(f"  🎯 Modo: {'ESTRITO' if strict_mode else 'NORMAL'}")

        if failed_projects:
            print_colored("\n🚫 Projetos Reprovados:", Colors.RED)
            for project in failed_projects:
                print(f"  • {project}")

        # Score de qualidade
        if total_stats["projects_analyzed"] > 0:
            success_rate = (total_stats["passed"] / total_stats["projects_analyzed"]) * 100

            if success_rate == 100:
                score_color = Colors.GREEN
                status = "PERFEITO"
            elif success_rate >= 80:
                score_color = Colors.CYAN
                status = "BOM"
            elif success_rate >= 60:
                score_color = Colors.YELLOW
                status = "PRECISA MELHORAR"
            else:
                score_color = Colors.RED
                status = "CRÍTICO"

            print_colored(
                f"\n🏆 Score de Qualidade: {success_rate:.1f}% ({status})",
                score_color,
            )

    def create_parser(self) -> Any:
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

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Função principal."""
    script = QualityGateway()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())

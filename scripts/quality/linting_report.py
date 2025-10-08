#!/usr/bin/env python3
"""FLEXT Linting Report - Complete Code Quality Report.

Script to generate detailed code quality reports using Ruff,
MyPy and other linting tools in the FLEXT workspace.
"""

from __future__ import annotations

import argparse
import io
import json
import operator
import shutil
import sys
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import cast

from flext_core import FlextResult, FlextTypes
from mypy import api as mypy_api

from flext_tools import Colors, FlextScript, ScriptMetadata, print_colored

from ..common import discover_projects


class LintingReport(FlextScript):
    """Script para gerar relatórios completos de qualidade de código."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        """Metadados do script.

        Returns:
            ScriptMetadata: Metadados do script.

        """
        return ScriptMetadata(
            name="linting_report",
            description="Relatório de qualidade de código com Ruff, MyPy e métricas",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validar ferramentas necessárias."""
        required_tools = ["ruff", "mypy"]
        missing_tools: FlextTypes.List = []
        for tool in required_tools:
            if shutil.which(tool) is None:
                print_colored(f"❌ {tool.title()} não encontrado", Colors.RED)
                print_colored(f"   Instale com: pip install {tool}", Colors.YELLOW)
                missing_tools.append(tool)
            else:
                print_colored(f"✅ {tool.title()} encontrado", Colors.GREEN)

        if missing_tools:
            return FlextResult[None].fail(
                f"Missing required tools: {', '.join(missing_tools)}",
            )

        return FlextResult[None].ok(None)

    def execute_main_logic(
        self, **kwargs: dict[str, str]
    ) -> FlextResult[dict[str, str]]:
        """Execute main script logic."""
        """Executar análise completa de qualidade."""
        try:
            workspace_root = Path.cwd()
            output_format = kwargs.get("format", "console")
            detailed = bool(kwargs.get("verbose"))
            projects_filter = kwargs.get("projects")

            print_colored("📊 RELATÓRIO DE QUALIDADE DE CÓDIGO", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Descobrir projetos
            projects: list[Path] = self._discover_projects(
                workspace_root,
                str(projects_filter) if projects_filter else None,
            )

            # Análise agregada
            total_stats: FlextTypes.Dict = {
                "projects_analyzed": 0,
                "total_files": 0,
                "ruff_issues": 0,
                "mypy_errors": 0,
                "projects_with_issues": 0,
            }

            project_results: FlextTypes.Dict = {}

            # Analisar cada projeto
            for project_path in projects:
                project_name = project_path.name

                print_colored(f"\n📦 Analisando {project_name}...", Colors.BLUE)

                # Análise Ruff
                ruff_result = self._run_ruff_analysis(project_path)

                # Análise MyPy
                mypy_result = self._run_mypy_analysis(project_path)

                # Estatísticas do projeto
                project_stats = {
                    "python_files": len(list(project_path.rglob("*.py"))),
                    "ruff_issues": ruff_result["total_issues"],
                    "mypy_errors": mypy_result["total_errors"],
                    "has_issues": int(str(ruff_result["total_issues"])) > 0
                    or int(str(mypy_result["total_errors"])) > 0,
                }

                project_results[project_name] = {
                    "stats": project_stats,
                    "ruff": ruff_result,
                    "mypy": mypy_result,
                }

                # Atualizar totais
                current_analyzed = total_stats["projects_analyzed"]
                if isinstance(current_analyzed, (int, str)):
                    total_stats["projects_analyzed"] = int(current_analyzed) + 1
                else:
                    total_stats["projects_analyzed"] = 1
                # Safe int conversion for total_files
                current_total_files = total_stats["total_files"]
                if isinstance(current_total_files, (int, str)):
                    total_stats["total_files"] = int(current_total_files) + int(
                        project_stats["python_files"],
                    )
                else:
                    total_stats["total_files"] = int(project_stats["python_files"])

                # Safe int conversion for ruff_issues
                current_ruff_issues = total_stats["ruff_issues"]
                if isinstance(current_ruff_issues, (int, str)):
                    total_stats["ruff_issues"] = int(current_ruff_issues) + int(
                        project_stats["ruff_issues"],
                    )
                else:
                    total_stats["ruff_issues"] = int(project_stats["ruff_issues"])

                # Safe int conversion for mypy_errors
                current_mypy_errors = total_stats["mypy_errors"]
                if isinstance(current_mypy_errors, (int, str)):
                    total_stats["mypy_errors"] = int(current_mypy_errors) + int(
                        project_stats["mypy_errors"],
                    )
                else:
                    total_stats["mypy_errors"] = int(project_stats["mypy_errors"])
                if project_stats["has_issues"]:
                    current_projects_with_issues = total_stats["projects_with_issues"]
                    if isinstance(current_projects_with_issues, (int, str)):
                        total_stats["projects_with_issues"] = (
                            int(current_projects_with_issues) + 1
                        )
                    else:
                        total_stats["projects_with_issues"] = 1

                # Mostrar resultado do projeto
                self._print_project_summary(
                    project_name,
                    project_stats,
                    _detailed=detailed,
                )

                if detailed:
                    self._print_detailed_issues(ruff_result, mypy_result)

            # Resumo final
            self._print_final_summary(total_stats, project_results)

            # Salvar relatório se solicitado
            if output_format == "json":
                self._save_json_report(total_stats, project_results)
            elif output_format == "html":
                self._save_html_report(total_stats, project_results)

            return FlextResult[object].ok(
                {"total_stats": total_stats, "project_results": project_results},
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

    def _run_ruff_analysis(self, project_path: Path) -> FlextTypes.Dict:
        """Executar análise Ruff."""
        try:
            if not project_path.is_dir():
                return {
                    "total_issues": 0,
                    "by_category": {},
                    "by_file": {},
                    "issues": [],
                }

            # Import ruff at runtime to avoid import-time dependency issues
            ruff_main = None
            try:
                ruff_mod = import_module("ruff.__main__")
                ruff_main = getattr(ruff_mod, "main", None)
            except Exception:
                ruff_main = None

            stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                try:
                    if ruff_main is not None:
                        ruff_main(["check", str(project_path), "--output-format=json"])
                except SystemExit as e:
                    _ = e.code if isinstance(e.code, int) else 1

            issues_by_category: dict[str, int] = defaultdict(int)
            issues_by_file: dict[str, int] = defaultdict(int)
            all_issues: FlextTypes.List = []

            output_text = stdout_buf.getvalue()
            if output_text:
                try:
                    issues = json.loads(output_text)
                    for issue in issues:
                        category = issue.get("code", "Unknown")
                        filename = issue.get("filename", "Unknown")

                        issues_by_category[category] += 1
                        issues_by_file[filename] += 1
                        all_issues.append(issue)
                except json.JSONDecodeError:
                    pass

            return {
                "total_issues": len(all_issues),
                "by_category": dict(issues_by_category),
                "by_file": dict(issues_by_file),
                "issues": all_issues,
            }

        except Exception as e:
            print_colored(f"    ⚠️ Erro no Ruff: {e}", Colors.YELLOW)
            return {"total_issues": 0, "by_category": {}, "by_file": {}, "issues": []}

    def _run_mypy_analysis(self, project_path: Path) -> FlextTypes.Dict:
        """Executar análise MyPy."""
        try:
            if not project_path.is_dir():
                return {"total_errors": 0, "by_type": {}, "by_file": {}, "output": ""}

            stdout_text, _stderr_text, _status = mypy_api.run(
                [str(project_path), "--no-error-summary"],
            )

            errors_by_type: dict[str, int] = defaultdict(int)
            errors_by_file: dict[str, int] = defaultdict(int)
            total_errors = 0

            if stdout_text:
                for line in stdout_text.strip().split("\n"):
                    if line and ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 4:
                            filename = parts[0]
                            error_type = (
                                parts[3].strip() if len(parts) > 3 else "Unknown"
                            )

                            errors_by_file[filename] += 1
                            errors_by_type[error_type] += 1
                            total_errors += 1

            return {
                "total_errors": total_errors,
                "by_type": dict(errors_by_type),
                "by_file": dict(errors_by_file),
                "output": stdout_text,
            }

        except Exception as e:
            print_colored(f"    ⚠️ Erro no MyPy: {e}", Colors.YELLOW)
            return {"total_errors": 0, "by_type": {}, "by_file": {}, "output": ""}

    def _print_project_summary(
        self,
        _project_name: str,
        stats: FlextTypes.Dict,
        *,
        _detailed: bool,
    ) -> None:
        """Imprimir resumo do projeto."""
        ruff_issues = stats["ruff_issues"]
        mypy_errors = stats["mypy_errors"]
        total_issues = (
            int(ruff_issues) + int(mypy_errors)
            if isinstance(ruff_issues, (int, str))
            and isinstance(mypy_errors, (int, str))
            else 0
        )

        if total_issues == 0:
            print_colored(
                f"  ✅ {stats['python_files']} arquivos, sem issues",
                Colors.GREEN,
            )
        else:
            print_colored(
                f"  ⚠️ {stats['python_files']} arquivos, {total_issues} issues",
                Colors.YELLOW,
            )

    def _print_detailed_issues(
        self,
        ruff_result: FlextTypes.Dict,
        mypy_result: FlextTypes.Dict,
    ) -> None:
        """Imprimir issues detalhadas."""
        if ruff_result["by_category"] and isinstance(ruff_result["by_category"], dict):
            print_colored("    📋 Top Ruff Issues:", Colors.CYAN)
            by_category = ruff_result["by_category"]
            if isinstance(by_category, dict):
                for _category, _count in sorted(
                    by_category.items(),
                    key=operator.itemgetter(1),
                    reverse=True,
                )[:5]:
                    pass

        if mypy_result["by_type"] and isinstance(mypy_result["by_type"], dict):
            print_colored("    📋 Top MyPy Errors:", Colors.CYAN)
            by_type = mypy_result["by_type"]
            if isinstance(by_type, dict):
                for _error_type, _count in sorted(
                    by_type.items(),
                    key=operator.itemgetter(1),
                    reverse=True,
                )[:5]:
                    pass

    def _print_final_summary(
        self,
        total_stats: FlextTypes.Dict,
        _project_results: FlextTypes.Dict,
    ) -> None:
        """Imprimir resumo final."""
        print_colored("\n📊 RESUMO FINAL DO LINTING", Colors.BLUE)
        print_colored("=" * 50, Colors.BLUE)

        # Score de qualidade
        if cast("int", total_stats["total_files"]) > 0:
            issues_per_file = (
                cast("int", total_stats["ruff_issues"])
                + cast("int", total_stats["mypy_errors"])
            ) / cast("int", total_stats["total_files"])
            if issues_per_file == 0:
                score_color = Colors.GREEN
                status = "PERFEITO"
            elif issues_per_file <= 0.1:
                score_color = Colors.CYAN
                status = "EXCELENTE"
            elif issues_per_file <= 0.5:
                score_color = Colors.YELLOW
                status = "BOM"
            else:
                score_color = Colors.RED
                status = "PRECISA MELHORAR"

            print_colored(
                f"\n🏆 Score: {issues_per_file:.2f} issues/arquivo ({status})",
                score_color,
            )

    def _save_json_report(
        self,
        total_stats: FlextTypes.Dict,
        project_results: FlextTypes.Dict,
    ) -> None:
        """Salvar relatório em JSON."""
        report_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": total_stats,
            "projects": project_results,
        }

        report_path = Path.cwd() / ".flext_logs" / "linting_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print_colored(f"📄 Relatório JSON: {report_path}", Colors.CYAN)

    def _save_html_report(
        self,
        total_stats: FlextTypes.Dict,
        project_results: FlextTypes.Dict,
    ) -> None:
        """Salvar relatório em formato HTML."""
        report_path = Path("linting_report.html")

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>FLEXT Quality Report</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 20px; }}
      .header {{ background: #f0f0f0; padding: 20px; }}
      .summary {{ background: #e8f4f8; padding: 15px; margin: 10px 0; }}
      .project {{ border-left: 3px solid #ccc; padding: 10px; margin: 10px 0; }}
      .issues {{ color: #d9534f; }}
      .clean {{ color: #5cb85c; }}
    </style>
</head>
<body>
    <div class="header">
      <h1>🎯 FLEXT Quality Report</h1>
      <p>Generated: {total_stats}</p>
    </div>

    <div class="summary">
      <h2>📊 Summary</h2>
      <p>Projects: {total_stats["projects_analyzed"]}</p>
      <p>Python files: {total_stats["total_files"]}</p>
      <p>Projects with issues: {total_stats["projects_with_issues"]}</p>
      <p>Ruff issues: {total_stats["ruff_issues"]}</p>
      <p>MyPy errors: {total_stats["mypy_errors"]}</p>
    </div>

    <h2>📦 Project Details</h2>
    {
            "".join(
                f'<div class="project"><h3>{name}</h3> <p>Issues: '
                f"{cast('int', cast('FlextTypes.Dict', cast('dict', data)['stats'])['ruff_issues']) + cast('int', cast('FlextTypes.Dict', cast('dict', data)['stats'])['mypy_errors'])}"
                f"</p></div>"
                for name, data in project_results.items()
            )
        }
</body>
</html>
      """

        with report_path.open("w", encoding="utf-8") as f:
            f.write(html_content)

        print_colored(f"\n💾 Relatório HTML salvo: {report_path}", Colors.GREEN)

    def create_parser(self) -> argparse.ArgumentParser:
        """Criar parser com argumentos específicos."""
        parser = super().create_parser()

        parser.add_argument(
            "--format",
            choices=["console", "json", "html"],
            default="console",
            help="Formato do output (default: console)",
        )

        parser.add_argument(
            "--projects",
            help="Filtrar projetos específicos (separados por vírgula)",
        )

        return parser

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Função principal."""
    script = LintingReport()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
FLEXT Advanced Quality Gateway - Sistema Completo de Correção Automática
========================================================================

Sistema avançado que:
1. Aplica TODAS as ferramentas automáticas disponíveis sequencialmente
2. Para cada ferramenta, só aceita se não piorar a taxa de erros
3. Cria backup antes de cada etapa
4. Reverte automaticamente em caso de piora
5. Relatório detalhado de cada etapa

Ferramentas aplicadas em ordem:
1. isort - Organização de imports
2. autopep8 - Correções PEP 8 básicas
3. black - Formatação de código
4. ruff check --fix - Linting avançado
5. ruff format - Formatação final

Autor: FLEXT Automation
Versão: 3.0.0 - Advanced
"""

import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
    )
    from rich.table import Table
    from rich.tree import Tree

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


@dataclass
class QualityMetrics:
    """Métricas detalhadas de qualidade de um arquivo."""

    ruff_issues: int = 0
    mypy_issues: int = 0
    bandit_issues: int = 0
    import_issues: int = 0
    format_issues: int = 0
    syntax_errors: int = 0

    @property
    def total_issues(self) -> int:
        """Total de issues."""
        return (
            self.ruff_issues
            + self.mypy_issues
            + self.bandit_issues
            + self.import_issues
            + self.format_issues
            + self.syntax_errors
        )

    @property
    def quality_score(self) -> float:
        """Score de qualidade (0-100)."""
        if self.total_issues == 0:
            return 100.0
        return max(0.0, 100.0 - (self.total_issues * 2))


@dataclass
class ToolResult:
    """Resultado da aplicação de uma ferramenta."""

    tool_name: str
    success: bool
    before_metrics: QualityMetrics
    after_metrics: QualityMetrics
    changes_applied: bool = False
    execution_time: float = 0.0
    error_message: str = ""

    @property
    def improvement(self) -> int:
        """Melhoria em número de issues."""
        return self.before_metrics.total_issues - self.after_metrics.total_issues

    @property
    def regression(self) -> bool:
        """Se houve regressão."""
        return self.after_metrics.total_issues > self.before_metrics.total_issues


class AdvancedQualityChecker:
    """Verificador avançado de qualidade com múltiplas ferramentas."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.python_executable = workspace_root / ".venv" / "bin" / "python"

        # Validar Python
        if not self.python_executable.exists():
            msg = f"Python não encontrado: {self.python_executable}"
            raise RuntimeError(msg)

        # Verificar ferramentas disponíveis
        self.available_tools = self._check_available_tools()

    def _check_available_tools(self) -> dict[str, bool]:
        """Verifica quais ferramentas estão disponíveis."""
        tools = {}

        # Verificar cada ferramenta
        for tool in ["isort", "autopep8", "black", "ruff", "mypy", "bandit"]:
            try:
                result = subprocess.run(
                    [str(self.python_executable), "-m", tool, "--version"],
                    check=False,
                    capture_output=True,
                    timeout=10,
                )
                tools[tool] = result.returncode == 0
            except Exception:
                tools[tool] = False

        return tools

    def count_detailed_metrics(self, file_path: Path) -> QualityMetrics:
        """Conta métricas detalhadas de qualidade."""
        metrics = QualityMetrics()

        # Ruff issues
        try:
            result = subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "ruff",
                    "check",
                    "--output-format=json",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                try:
                    issues = json.loads(result.stdout)
                    metrics.ruff_issues = len(issues)
                except json.JSONDecodeError:
                    metrics.ruff_issues = len(
                        [line for line in result.stdout.split("\n") if line.strip()]
                    )
        except Exception:
            pass

        # MyPy issues
        try:
            result = subprocess.run(
                [str(self.python_executable), "-m", "mypy", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_lines = [
                    line
                    for line in result.stdout.split("\n")
                    if line.strip() and ": error:" in line
                ]
                metrics.mypy_issues = len(error_lines)
        except Exception:
            pass

        # Bandit issues
        try:
            result = subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "bandit",
                    "-f",
                    "json",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                try:
                    report = json.loads(result.stdout)
                    metrics.bandit_issues = len(report.get("results", []))
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # Import issues (usando isort check)
        try:
            result = subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "isort",
                    "--check-only",
                    "--diff",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Conta número de linhas de diff
                diff_lines = [
                    line
                    for line in result.stdout.split("\n")
                    if line.startswith(("+", "-"))
                ]
                metrics.import_issues = len(diff_lines)
        except Exception:
            pass

        # Format issues (usando black check)
        try:
            result = subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "black",
                    "--check",
                    "--diff",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Conta linhas de diff
                diff_lines = [
                    line for line in result.stdout.split("\n") if line.startswith("@@")
                ]
                metrics.format_issues = len(diff_lines)
        except Exception:
            pass

        # Syntax errors
        try:
            with open(file_path, encoding="utf-8") as f:
                compile(f.read(), str(file_path), "exec")
        except SyntaxError:
            metrics.syntax_errors = 1
        except Exception:
            pass

        return metrics

    def apply_isort(self, file_path: Path) -> ToolResult:
        """Aplica isort para organizar imports."""
        if not self.available_tools.get("isort", False):
            return ToolResult(
                tool_name="isort",
                success=False,
                before_metrics=QualityMetrics(),
                after_metrics=QualityMetrics(),
                error_message="isort não disponível",
            )

        start_time = time.time()
        before_metrics = self.count_detailed_metrics(file_path)

        try:
            result = subprocess.run(
                [str(self.python_executable), "-m", "isort", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            after_metrics = self.count_detailed_metrics(file_path)
            execution_time = time.time() - start_time

            return ToolResult(
                tool_name="isort",
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=result.returncode == 0,
                execution_time=execution_time,
            )

        except Exception as e:
            return ToolResult(
                tool_name="isort",
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def apply_autopep8(self, file_path: Path) -> ToolResult:
        """Aplica autopep8 para correções PEP 8."""
        if not self.available_tools.get("autopep8", False):
            return ToolResult(
                tool_name="autopep8",
                success=False,
                before_metrics=QualityMetrics(),
                after_metrics=QualityMetrics(),
                error_message="autopep8 não disponível",
            )

        start_time = time.time()
        before_metrics = self.count_detailed_metrics(file_path)

        try:
            subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "autopep8",
                    "--in-place",
                    "--aggressive",
                    "--aggressive",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            after_metrics = self.count_detailed_metrics(file_path)
            execution_time = time.time() - start_time

            return ToolResult(
                tool_name="autopep8",
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=True,
                execution_time=execution_time,
            )

        except Exception as e:
            return ToolResult(
                tool_name="autopep8",
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def apply_black(self, file_path: Path) -> ToolResult:
        """Aplica black para formatação."""
        if not self.available_tools.get("black", False):
            return ToolResult(
                tool_name="black",
                success=False,
                before_metrics=QualityMetrics(),
                after_metrics=QualityMetrics(),
                error_message="black não disponível",
            )

        start_time = time.time()
        before_metrics = self.count_detailed_metrics(file_path)

        try:
            result = subprocess.run(
                [str(self.python_executable), "-m", "black", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            after_metrics = self.count_detailed_metrics(file_path)
            execution_time = time.time() - start_time

            return ToolResult(
                tool_name="black",
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=result.returncode == 0,
                execution_time=execution_time,
            )

        except Exception as e:
            return ToolResult(
                tool_name="black",
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def apply_ruff_fix(self, file_path: Path) -> ToolResult:
        """Aplica ruff --fix para linting."""
        if not self.available_tools.get("ruff", False):
            return ToolResult(
                tool_name="ruff_fix",
                success=False,
                before_metrics=QualityMetrics(),
                after_metrics=QualityMetrics(),
                error_message="ruff não disponível",
            )

        start_time = time.time()
        before_metrics = self.count_detailed_metrics(file_path)

        try:
            subprocess.run(
                [
                    str(self.python_executable),
                    "-m",
                    "ruff",
                    "check",
                    "--fix",
                    str(file_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            after_metrics = self.count_detailed_metrics(file_path)
            execution_time = time.time() - start_time

            return ToolResult(
                tool_name="ruff_fix",
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=True,
                execution_time=execution_time,
            )

        except Exception as e:
            return ToolResult(
                tool_name="ruff_fix",
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def apply_ruff_format(self, file_path: Path) -> ToolResult:
        """Aplica ruff format para formatação final."""
        if not self.available_tools.get("ruff", False):
            return ToolResult(
                tool_name="ruff_format",
                success=False,
                before_metrics=QualityMetrics(),
                after_metrics=QualityMetrics(),
                error_message="ruff não disponível",
            )

        start_time = time.time()
        before_metrics = self.count_detailed_metrics(file_path)

        try:
            result = subprocess.run(
                [str(self.python_executable), "-m", "ruff", "format", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            after_metrics = self.count_detailed_metrics(file_path)
            execution_time = time.time() - start_time

            return ToolResult(
                tool_name="ruff_format",
                success=True,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=result.returncode == 0,
                execution_time=execution_time,
            )

        except Exception as e:
            return ToolResult(
                tool_name="ruff_format",
                success=False,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def process_file_comprehensively(self, file_path: Path) -> dict[str, Any]:
        """Processa um arquivo aplicando todas as ferramentas sequencialmente."""
        if not file_path.exists():
            return {"success": False, "error": "Arquivo não existe", "tool_results": []}

        self._print(f"🔧 Processamento avançado: {file_path.name}")

        # Backup completo inicial
        backup_path = file_path.with_suffix(file_path.suffix + ".advanced_backup")
        try:
            backup_path.write_text(
                file_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro criando backup: {e}",
                "tool_results": [],
            }

        # Métricas iniciais
        initial_metrics = self.count_detailed_metrics(file_path)
        self._print(
            f"📊 Métricas iniciais: {initial_metrics.total_issues} issues totais"
        )

        # Lista de ferramentas para aplicar em ordem
        tools_to_apply = [
            self.apply_isort,
            self.apply_autopep8,
            self.apply_black,
            self.apply_ruff_fix,
            self.apply_ruff_format,
        ]

        tool_results = []
        current_content = file_path.read_text(encoding="utf-8")

        for tool_func in tools_to_apply:
            # Backup antes desta ferramenta
            tool_backup = tempfile.NamedTemporaryFile(
                encoding="utf-8", mode="w", suffix=".py", delete=False
            )
            tool_backup.write(current_content)
            tool_backup.close()
            tool_backup_path = Path(tool_backup.name)

            try:
                # Aplica a ferramenta
                result = tool_func(file_path)
                tool_results.append(result)

                if result.success:
                    if result.regression:
                        # REGRESSÃO - reverter esta ferramenta
                        self._print(
                            f"❌ {result.tool_name}: REVERTIDO (issues: {result.before_metrics.total_issues} → {result.after_metrics.total_issues})"
                        )
                        file_path.write_text(current_content, encoding="utf-8")
                        result.changes_applied = False
                    else:
                        # SUCESSO - manter mudanças
                        improvement = result.improvement
                        if improvement > 0:
                            self._print(
                                f"✅ {result.tool_name}: {improvement} issues corrigidas em {result.execution_time:.2f}s"
                            )
                        else:
                            self._print(
                                f"✅ {result.tool_name}: Sem regressão em {result.execution_time:.2f}s"
                            )
                        current_content = file_path.read_text(encoding="utf-8")
                else:
                    self._print(f"⚠️ {result.tool_name}: {result.error_message}")

            except Exception as e:
                self._print(f"❌ {tool_func.__name__}: Erro inesperado: {e}")
                # Restaurar estado anterior
                file_path.write_text(current_content, encoding="utf-8")

            finally:
                # Limpar backup temporário
                tool_backup_path.unlink(missing_ok=True)

        # Métricas finais
        final_metrics = self.count_detailed_metrics(file_path)
        total_improvement = initial_metrics.total_issues - final_metrics.total_issues

        # Verificação final de segurança
        if final_metrics.total_issues > initial_metrics.total_issues:
            # REGRESSÃO GERAL - reverter tudo
            self._print("❌ REGRESSÃO GERAL DETECTADA - Revertendo todas as mudanças")
            try:
                file_path.write_text(
                    backup_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
                final_metrics = initial_metrics
                total_improvement = 0
            except Exception:
                pass

        # Limpar backup principal
        backup_path.unlink(missing_ok=True)

        self._print(
            f"📈 Resultado final: {initial_metrics.total_issues} → {final_metrics.total_issues} issues ({total_improvement:+d})"
        )

        return {
            "success": True,
            "file_path": str(file_path),
            "initial_metrics": initial_metrics,
            "final_metrics": final_metrics,
            "total_improvement": total_improvement,
            "tool_results": tool_results,
            "processing_time": sum(r.execution_time for r in tool_results if r.success),
        }

    def process_project_comprehensively(self, project_path: Path) -> dict[str, Any]:
        """Processa um projeto completo com todas as ferramentas."""
        if not project_path.exists():
            return {
                "success": False,
                "error": f"Projeto não encontrado: {project_path}",
            }

        # Encontrar arquivos Python
        python_files = [
            py_file
            for py_file in project_path.rglob("*.py")
            if py_file.is_file()
            and not any(part.startswith(".") for part in py_file.parts)
        ]

        if not python_files:
            return {
                "success": True,
                "message": "Nenhum arquivo Python encontrado",
                "files_processed": 0,
            }

        self._print(
            f"🚀 Processamento avançado de {len(python_files)} arquivos em {project_path.name}"
        )

        results = []
        total_initial_issues = 0
        total_final_issues = 0
        total_files_improved = 0
        total_processing_time = 0.0

        # Progress bar
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Processando arquivos...", total=len(python_files)
                )

                for py_file in python_files:
                    progress.update(task, description=f"Processando {py_file.name}...")
                    result = self.process_file_comprehensively(py_file)
                    results.append(result)

                    if result["success"]:
                        total_initial_issues += result["initial_metrics"].total_issues
                        total_final_issues += result["final_metrics"].total_issues
                        total_processing_time += result["processing_time"]

                        if result["total_improvement"] > 0:
                            total_files_improved += 1

                    progress.advance(task)
        else:
            for i, py_file in enumerate(python_files):
                print(f"[{i + 1}/{len(python_files)}] Processando {py_file.name}...")
                result = self.process_file_comprehensively(py_file)
                results.append(result)

                if result["success"]:
                    total_initial_issues += result["initial_metrics"].total_issues
                    total_final_issues += result["final_metrics"].total_issues
                    total_processing_time += result["processing_time"]

                    if result["total_improvement"] > 0:
                        total_files_improved += 1

        return {
            "success": True,
            "project_name": project_path.name,
            "files_processed": len(python_files),
            "files_improved": total_files_improved,
            "total_initial_issues": total_initial_issues,
            "total_final_issues": total_final_issues,
            "total_improvement": total_initial_issues - total_final_issues,
            "total_processing_time": total_processing_time,
            "results": results,
        }

    def _print(self, message: str) -> None:
        """Print com ou sem Rich."""
        if RICH_AVAILABLE and console:
            console.print(message)
        else:
            print(message)


def generate_detailed_report(result: dict[str, Any]) -> str:
    """Gera relatório detalhado dos resultados."""
    if not result["success"]:
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"

    if "results" in result:  # Resultado de projeto
        report = []
        report.extend(
            (
                f"# Relatório de Processamento Avançado - {result['project_name']}",
                "",
                "## 📊 Resumo Executivo",
                f"- **Arquivos processados**: {result['files_processed']}",
                f"- **Arquivos melhorados**: {result['files_improved']}",
                f"- **Issues iniciais**: {result['total_initial_issues']}",
                f"- **Issues finais**: {result['total_final_issues']}",
                f"- **Melhoria total**: {result['total_improvement']}",
                f"- **Tempo de processamento**: {result['total_processing_time']:.2f}s",
                "",
            )
        )

        # Estatísticas por ferramenta
        tool_stats = {}
        for file_result in result["results"]:
            if file_result["success"]:
                for tool_result in file_result["tool_results"]:
                    tool_name = tool_result.tool_name
                    if tool_name not in tool_stats:
                        tool_stats[tool_name] = {
                            "uses": 0,
                            "improvements": 0,
                            "regressions": 0,
                        }

                    tool_stats[tool_name]["uses"] += 1
                    if tool_result.improvement > 0:
                        tool_stats[tool_name]["improvements"] += 1
                    elif tool_result.regression:
                        tool_stats[tool_name]["regressions"] += 1

        if tool_stats:
            report.append("## 🔧 Estatísticas por Ferramenta")
            for tool_name, stats in tool_stats.items():
                report.extend(
                    (
                        f"### {tool_name}",
                        f"- Usos: {stats['uses']}",
                        f"- Melhorias: {stats['improvements']}",
                        f"- Regressões: {stats['regressions']}",
                        "",
                    )
                )

        return "\n".join(report)

    # Resultado de arquivo único
    report = []
    report.append(f"# Relatório de Arquivo - {Path(result['file_path']).name}")
    report.append("")
    report.append("## 📊 Métricas")
    report.append(f"- **Issues iniciais**: {result['initial_metrics'].total_issues}")
    report.append(f"- **Issues finais**: {result['final_metrics'].total_issues}")
    report.append(f"- **Melhoria**: {result['total_improvement']}")
    report.append(f"- **Tempo**: {result['processing_time']:.2f}s")
    report.append("")

    # Detalhes por ferramenta
    report.append("## 🔧 Detalhes por Ferramenta")
    for tool_result in result["tool_results"]:
        status = "✅" if tool_result.success and not tool_result.regression else "❌"
        improvement = tool_result.improvement
        report.append(f"### {status} {tool_result.tool_name}")
        report.append(f"- Melhoria: {improvement:+d} issues")
        report.append(f"- Tempo: {tool_result.execution_time:.2f}s")
        if tool_result.error_message:
            report.append(f"- Erro: {tool_result.error_message}")
        report.append("")

    return "\n".join(report)


def main() -> None:
    """Função principal avançada."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Advanced Quality Gateway - Sistema Completo de Correção Automática"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("/home/marlonsc/flext"),
        help="Diretório raiz do workspace FLEXT",
    )
    parser.add_argument(
        "--project", type=str, help="Processar apenas um projeto específico"
    )
    parser.add_argument(
        "--file", type=Path, help="Processar apenas um arquivo específico"
    )
    parser.add_argument(
        "--report", type=Path, help="Salvar relatório detalhado em arquivo"
    )
    parser.add_argument(
        "--show-tools", action="store_true", help="Mostrar ferramentas disponíveis"
    )

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"❌ Workspace não encontrado: {args.workspace}")
        sys.exit(1)

    try:
        checker = AdvancedQualityChecker(args.workspace)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Mostrar ferramentas disponíveis
    if args.show_tools:
        if RICH_AVAILABLE:
            table = Table(title="Ferramentas Disponíveis")
            table.add_column("Ferramenta", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Função")

            tools_info = {
                "isort": (
                    "Organização de imports",
                    checker.available_tools.get("isort", False),
                ),
                "autopep8": (
                    "Correções PEP 8",
                    checker.available_tools.get("autopep8", False),
                ),
                "black": (
                    "Formatação de código",
                    checker.available_tools.get("black", False),
                ),
                "ruff": (
                    "Linting avançado",
                    checker.available_tools.get("ruff", False),
                ),
                "mypy": ("Type checking", checker.available_tools.get("mypy", False)),
                "bandit": ("Segurança", checker.available_tools.get("bandit", False)),
            }

            for tool, (description, available) in tools_info.items():
                status = "✅ Disponível" if available else "❌ Não disponível"
                table.add_row(tool, status, description)

            console.print(table)
        else:
            print("Ferramentas Disponíveis:")
            for tool, available in checker.available_tools.items():
                status = "✅" if available else "❌"
                print(f"  {status} {tool}")

        return

    # Processamento de arquivo único
    if args.file:
        if not args.file.exists():
            print(f"❌ Arquivo não encontrado: {args.file}")
            sys.exit(1)

        result = checker.process_file_comprehensively(args.file)

        if result["success"]:
            improvement = result["total_improvement"]
            time_taken = result["processing_time"]
            print(f"✅ {args.file.name} processado em {time_taken:.2f}s")
            print(f"📊 Melhoria: {improvement:+d} issues")
        else:
            print(
                f"❌ {args.file.name} falhou: {result.get('error', 'Erro desconhecido')}"
            )

        # Salvar relatório se solicitado
        if args.report:
            report = generate_detailed_report(result)
            args.report.write_text(report, encoding="utf-8")
            print(f"📄 Relatório salvo em: {args.report}")

        return

    # Processamento de projeto
    if args.project:
        project_path = args.workspace / args.project
        result = checker.process_project_comprehensively(project_path)

        if result["success"]:
            print(f"✅ Projeto {args.project} processado:")
            print(f"  📁 Arquivos: {result['files_processed']}")
            print(f"  🔧 Melhorados: {result['files_improved']}")
            print(
                f"  📊 Issues: {result['total_initial_issues']} → {result['total_final_issues']}"
            )
            print(f"  📈 Melhoria total: {result['total_improvement']}")
            print(f"  ⏱️ Tempo: {result['total_processing_time']:.2f}s")
        else:
            print(
                f"❌ Projeto {args.project} falhou: {result.get('error', 'Erro desconhecido')}"
            )

        # Salvar relatório se solicitado
        if args.report:
            report = generate_detailed_report(result)
            args.report.write_text(report, encoding="utf-8")
            print(f"📄 Relatório salvo em: {args.report}")

        return

    print("ℹ️ Use --file, --project ou --show-tools. Use --help para mais opções.")


if __name__ == "__main__":
    main()

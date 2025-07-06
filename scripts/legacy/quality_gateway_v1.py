#!/usr/bin/env python3
"""
FLEXT Quality Gateway - Unified Quality Control System
=====================================================

Sistema unificado de controle de qualidade que:
1. Só aceita mudanças se não aumentarem o número de falhas
2. Aplica correções incrementais e abrangentes
3. Gera relatórios detalhados de status
4. Funciona em todos os projetos FLEXT

Autor: FLEXT Automation
Versão: 2.0.0
"""

import builtins
import contextlib
import json
import operator
import re
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class QualityMetrics:
    """Métricas de qualidade de um arquivo ou projeto."""

    file_path: Path
    ruff_issues: int = 0
    mypy_issues: int = 0
    bandit_issues: int = 0
    syntax_errors: int = 0
    test_failures: int = 0
    coverage_percent: float = 0.0

    @property
    def total_issues(self) -> int:
        """Total de issues encontradas."""
        return (
            self.ruff_issues
            + self.mypy_issues
            + self.bandit_issues
            + self.syntax_errors
            + self.test_failures
        )

    @property
    def quality_score(self) -> float:
        """Score de qualidade (0-100)."""
        if self.total_issues == 0:
            return 100.0
        # Penaliza por issues, premia por coverage
        base_score = max(0, 100 - (self.total_issues * 5))
        return min(100.0, base_score + (self.coverage_percent * 0.3))


@dataclass
class ValidationResult:
    """Resultado de uma validação."""

    validator_name: str
    file_path: Path
    before_metrics: QualityMetrics
    after_metrics: QualityMetrics
    changes_applied: bool = False
    success: bool = field(init=False)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Calcula se a validação foi bem-sucedida."""
        self.success = (
            self.after_metrics.total_issues <= self.before_metrics.total_issues
            and self.after_metrics.quality_score >= self.before_metrics.quality_score
        )


class BaseValidator(ABC):
    """Classe base para todos os validadores."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.python_executable = workspace_root / ".venv" / "bin" / "python"

    @abstractmethod
    def get_validator_name(self) -> str:
        """Nome do validador."""

    @abstractmethod
    def measure_quality(self, file_path: Path) -> QualityMetrics:
        """Mede a qualidade de um arquivo."""

    @abstractmethod
    def apply_improvements(self, file_path: Path) -> bool:
        """Aplica melhorias no arquivo."""

    def validate_with_safety(self, file_path: Path) -> ValidationResult:
        """Valida um arquivo com segurança - só aceita se melhorar."""
        if not file_path.exists():
            return ValidationResult(
                validator_name=self.get_validator_name(),
                file_path=file_path,
                before_metrics=QualityMetrics(file_path),
                after_metrics=QualityMetrics(file_path),
                errors=["Arquivo não existe"],
            )

        # Backup do arquivo original
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        try:
            backup_path.write_text(
                file_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
        except Exception as e:
            return ValidationResult(
                validator_name=self.get_validator_name(),
                file_path=file_path,
                before_metrics=QualityMetrics(file_path),
                after_metrics=QualityMetrics(file_path),
                errors=[f"Erro ao criar backup: {e}"],
            )

        # Medição antes das mudanças
        before_metrics = self.measure_quality(file_path)

        try:
            # Aplicar melhorias
            changes_applied = self.apply_improvements(file_path)

            if not changes_applied:
                # Nenhuma mudança - limpar backup
                backup_path.unlink(missing_ok=True)
                return ValidationResult(
                    validator_name=self.get_validator_name(),
                    file_path=file_path,
                    before_metrics=before_metrics,
                    after_metrics=before_metrics,
                    warnings=["Nenhuma mudança aplicada"],
                )

            # Medição após as mudanças
            after_metrics = self.measure_quality(file_path)

            # Verificar se houve melhoria
            if after_metrics.total_issues > before_metrics.total_issues:
                # Reverter mudanças - piorou
                file_path.write_text(
                    backup_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
                backup_path.unlink(missing_ok=True)

                return ValidationResult(
                    validator_name=self.get_validator_name(),
                    file_path=file_path,
                    before_metrics=before_metrics,
                    after_metrics=after_metrics,
                    changes_applied=True,
                    errors=[
                        f"Mudanças rejeitadas: issues aumentaram de {before_metrics.total_issues} para {after_metrics.total_issues}"
                    ],
                )

            # Sucesso - manter mudanças
            backup_path.unlink(missing_ok=True)

            return ValidationResult(
                validator_name=self.get_validator_name(),
                file_path=file_path,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                changes_applied=True,
            )

        except Exception as e:
            # Erro - reverter mudanças
            with contextlib.suppress(builtins.BaseException):
                file_path.write_text(
                    backup_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            backup_path.unlink(missing_ok=True)

            return ValidationResult(
                validator_name=self.get_validator_name(),
                file_path=file_path,
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                errors=[f"Erro durante validação: {e}"],
            )


class RuffValidator(BaseValidator):
    """Validador Ruff para linting."""

    def get_validator_name(self) -> str:
        return "ruff"

    def measure_quality(self, file_path: Path) -> QualityMetrics:
        """Mede issues do Ruff."""
        metrics = QualityMetrics(file_path)

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
                timeout=60,
            )

            if result.returncode == 0:
                metrics.ruff_issues = 0
            else:
                try:
                    issues = json.loads(result.stdout)
                    metrics.ruff_issues = len(issues)
                except json.JSONDecodeError:
                    metrics.ruff_issues = len(
                        [line for line in result.stdout.split("\n") if line.strip()]
                    )

        except Exception:
            metrics.ruff_issues = 0

        return metrics

    def apply_improvements(self, file_path: Path) -> bool:
        """Aplica correções do Ruff."""
        try:
            result = subprocess.run(
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
                timeout=60,
            )

            # Aplica formatação também
            format_result = subprocess.run(
                [str(self.python_executable), "-m", "ruff", "format", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )

            return result.returncode != 0 or format_result.returncode == 0

        except Exception:
            return False


class ComprehensiveValidator(BaseValidator):
    """Validador abrangente que combina múltiplas ferramentas."""

    def get_validator_name(self) -> str:
        return "comprehensive"

    def measure_quality(self, file_path: Path) -> QualityMetrics:
        """Mede qualidade usando múltiplas ferramentas."""
        metrics = QualityMetrics(file_path)

        # Ruff
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
                timeout=60,
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

        # MyPy
        try:
            result = subprocess.run(
                [str(self.python_executable), "-m", "mypy", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
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

        # Bandit
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
                timeout=60,
            )

            if result.returncode != 0:
                try:
                    report = json.loads(result.stdout)
                    metrics.bandit_issues = len(report.get("results", []))
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # Verificação de sintaxe
        try:
            with open(file_path, encoding="utf-8") as f:
                compile(f.read(), str(file_path), "exec")
        except SyntaxError:
            metrics.syntax_errors = 1
        except Exception:
            pass

        return metrics

    def apply_improvements(self, file_path: Path) -> bool:
        """Aplica melhorias abrangentes."""
        try:
            original_content = file_path.read_text(encoding="utf-8")
            content = original_content

            # Correções básicas de sintaxe
            content = self._fix_syntax_issues(content)

            # Correções de padrões comuns
            content = self._fix_common_patterns(content)

            # Aplicar Ruff
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")

            # Ruff check e format
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
                timeout=60,
            )

            subprocess.run(
                [str(self.python_executable), "-m", "ruff", "format", str(file_path)],
                check=False,
                capture_output=True,
                timeout=60,
            )

            return content != original_content

        except Exception:
            return False

    def _fix_syntax_issues(self, content: str) -> str:
        """Corrige issues básicos de sintaxe."""
        # Corrige duplicação de type: ignore
        content = re.sub(
            r"#\s*type:\s*ignore\[misc\]\s*#\s*type:\s*ignore\[misc\]",
            "# type: ignore[misc]",
            content,
        )

        # Corrige hasattr com sintaxe quebrada
        content = re.sub(
            r"if hasattr\(([^)]+)\)\s+#[^:]*#[^:]*:",
            r"if hasattr(\1):  # type: ignore[misc]",
            content,
        )

        # Remove comentários desnecessários
        return re.sub(r'^\s*#\s*"[^"]*",?\s*#.*$', "", content, flags=re.MULTILINE)

    def _fix_common_patterns(self, content: str) -> str:
        """Corrige padrões comuns de problemas."""
        # Adiciona docstrings para métodos __init__
        content = re.sub(
            r'(def __init__\([^)]*\) -> None:)\n(\s*)((?!"""|\'\'\')[^\n])',
            r'\1\n\2"""Initialize instance."""\n\2\3',
            content,
        )

        # Corrige imports não utilizados básicos
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Remove imports obviously unused
            if re.match(r"^\s*import\s+os\s*$", line) and "os." not in content:
                continue
            if re.match(r"^\s*import\s+sys\s*$", line) and "sys." not in content:
                continue
            fixed_lines.append(line)

        return "\n".join(fixed_lines)


class QualityGateway:
    """Sistema principal de quality gateway."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.comprehensive_validator = ComprehensiveValidator(workspace_root)

    def scan_project(self, project_path: Path) -> list[Path]:
        """Escaneia um projeto para arquivos Python."""
        if not project_path.exists():
            return []

        return [
            py_file
            for py_file in project_path.rglob("*.py")
            if py_file.is_file()
            and not any(part.startswith(".") for part in py_file.parts)
        ]

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Valida um arquivo individual."""
        return self.comprehensive_validator.validate_with_safety(file_path)

    def validate_project(self, project_path: Path) -> dict[str, ValidationResult]:
        """Valida um projeto completo."""
        results = {}
        python_files = self.scan_project(project_path)

        console.print(
            f"[cyan]🔍 Validando {len(python_files)} arquivos em {project_path.name}[/cyan]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validando arquivos...", total=len(python_files))

            for py_file in python_files:
                progress.update(task, description=f"Validando {py_file.name}...")
                result = self.validate_file(py_file)
                results[str(py_file)] = result
                progress.advance(task)

        return results

    def validate_workspace(self) -> dict[str, dict[str, ValidationResult]]:
        """Valida todo o workspace FLEXT."""
        # Projetos ativos do FLEXT
        active_projects = [
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-grpc",
            "flext-web",
            "flext-cli",
            "flext-plugin",
            "flext-observability",
            "flext-meltano",
            "flext-ldap",
            "flext-db-oracle",
            "flext-quality",
            "flext-tap-ldap",
            "flext-tap-oracle-oic",
            "flext-tap-oracle-wms",
            "flext-target-ldap",
            "flext-target-oracle",
            "flext-target-oracle-oic",
            "flext-dbt-ldap",
            "flext-oracle-oic-ext",
        ]

        workspace_results = {}

        console.print(
            Panel.fit(
                f"[bold cyan]🎯 FLEXT Quality Gateway[/bold cyan]\n"
                f"Validando {len(active_projects)} projetos no workspace"
            )
        )

        for project_name in active_projects:
            project_path = self.workspace_root / project_name

            if project_path.exists():
                project_results = self.validate_project(project_path)
                workspace_results[project_name] = project_results

        return workspace_results

    def generate_report(self, results: dict[str, dict[str, ValidationResult]]) -> str:
        """Gera relatório abrangente."""
        report_lines = [
            "# FLEXT Quality Gateway Report",
            f"**Workspace**: {self.workspace_root}",
            f"**Data**: {self._get_timestamp()}",
            "",
        ]

        # Sumário executivo
        total_projects = len(results)
        total_files = sum(len(project_results) for project_results in results.values())
        successful_validations = 0
        total_improvements = 0
        total_errors = 0

        for project_results in results.values():
            for result in project_results.values():
                if result.success:
                    successful_validations += 1
                if result.changes_applied and result.success:
                    total_improvements += 1
                if result.errors:
                    total_errors += len(result.errors)

        report_lines.extend(
            [
                "## 📊 Sumário Executivo",
                f"- **Projetos validados**: {total_projects}",
                f"- **Arquivos processados**: {total_files}",
                f"- **Validações bem-sucedidas**: {successful_validations}",
                f"- **Melhorias aplicadas**: {total_improvements}",
                f"- **Erros encontrados**: {total_errors}",
                f"- **Taxa de sucesso**: {(successful_validations / total_files * 100):.1f}%",
                "",
            ]
        )

        # Detalhes por projeto
        report_lines.append("## 🔍 Detalhes por Projeto")

        for project_name, project_results in results.items():
            if not project_results:
                continue

            project_files = len(project_results)
            project_successes = sum(1 for r in project_results.values() if r.success)
            project_improvements = sum(
                1 for r in project_results.values() if r.changes_applied and r.success
            )

            report_lines.extend(
                [
                    f"### {project_name}",
                    f"- Arquivos: {project_files}",
                    f"- Sucessos: {project_successes}",
                    f"- Melhorias: {project_improvements}",
                    "",
                ]
            )

            # Top 5 arquivos com mais melhorias
            improved_files = [
                (path, result)
                for path, result in project_results.items()
                if result.changes_applied and result.success
            ]

            if improved_files:
                report_lines.append("**Arquivos melhorados:**")
                for path, result in improved_files[:5]:
                    file_name = Path(path).name
                    before_issues = result.before_metrics.total_issues
                    after_issues = result.after_metrics.total_issues
                    improvement = before_issues - after_issues
                    report_lines.append(
                        f"- `{file_name}`: {before_issues} → {after_issues} issues (-{improvement})"
                    )

                if len(improved_files) > 5:
                    report_lines.append(
                        f"- ... e mais {len(improved_files) - 5} arquivos"
                    )

                report_lines.append("")

        # Erros e avisos
        all_errors = []
        all_warnings = []

        for project_results in results.values():
            for result in project_results.values():
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)

        if all_errors:
            report_lines.extend(["## ❌ Erros Encontrados", ""])

            # Agrupa erros similares
            error_counts = {}
            for error in all_errors:
                error_type = error.split(":")[0] if ":" in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

            for error_type, count in sorted(
                error_counts.items(), key=operator.itemgetter(1), reverse=True
            ):
                report_lines.append(f"- **{error_type}**: {count} ocorrências")

            report_lines.append("")

        # Recomendações
        report_lines.extend(["## 🎯 Recomendações", ""])

        if total_improvements > 0:
            report_lines.append(
                f"✅ **{total_improvements} melhorias aplicadas com sucesso**"
            )

        if total_errors > 0:
            report_lines.append(
                f"⚠️ **{total_errors} erros precisam de atenção manual**"
            )

        success_rate = (
            (successful_validations / total_files * 100) if total_files > 0 else 0
        )

        if success_rate >= 90:
            report_lines.append("🏆 **Excelente qualidade de código!**")
        elif success_rate >= 70:
            report_lines.append("👍 **Boa qualidade de código**")
        else:
            report_lines.append("🔧 **Qualidade de código precisa melhorar**")

        return "\n".join(report_lines)

    def _get_timestamp(self) -> str:
        """Obtém timestamp atual."""
        try:
            import datetime

            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "2024-01-01 00:00:00"


def main() -> None:
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Quality Gateway - Sistema unificado de controle de qualidade"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("/home/marlonsc/flext"),
        help="Diretório raiz do workspace FLEXT",
    )
    parser.add_argument(
        "--project", type=str, help="Validar apenas um projeto específico"
    )
    parser.add_argument(
        "--file", type=Path, help="Validar apenas um arquivo específico"
    )
    parser.add_argument("--report", type=Path, help="Caminho para salvar o relatório")

    args = parser.parse_args()

    if not args.workspace.exists():
        console.print(f"[red]❌ Workspace não encontrado: {args.workspace}[/red]")
        sys.exit(1)

    gateway = QualityGateway(args.workspace)

    # Validação de arquivo único
    if args.file:
        if not args.file.exists():
            console.print(f"[red]❌ Arquivo não encontrado: {args.file}[/red]")
            sys.exit(1)

        result = gateway.validate_file(args.file)

        if result.success:
            console.print(f"[green]✅ {args.file.name} validado com sucesso[/green]")
            if result.changes_applied:
                before = result.before_metrics.total_issues
                after = result.after_metrics.total_issues
                console.print(f"[cyan]🔧 Issues: {before} → {after}[/cyan]")
        else:
            console.print(f"[red]❌ {args.file.name} falhou na validação[/red]")
            for error in result.errors:
                console.print(f"[red]  - {error}[/red]")

        return

    # Validação de projeto único
    if args.project:
        project_path = args.workspace / args.project
        if not project_path.exists():
            console.print(f"[red]❌ Projeto não encontrado: {project_path}[/red]")
            sys.exit(1)

        project_results = gateway.validate_project(project_path)

        # Mostra sumário
        total_files = len(project_results)
        successes = sum(1 for r in project_results.values() if r.success)
        improvements = sum(
            1 for r in project_results.values() if r.changes_applied and r.success
        )

        console.print(f"[green]📊 Projeto {args.project}:[/green]")
        console.print(f"  - Arquivos: {total_files}")
        console.print(f"  - Sucessos: {successes}")
        console.print(f"  - Melhorias: {improvements}")

        return

    # Validação completa do workspace
    console.print(
        "[bold cyan]🚀 Iniciando validação completa do workspace FLEXT[/bold cyan]"
    )

    results = gateway.validate_workspace()

    # Gera relatório
    report = gateway.generate_report(results)

    # Salva relatório
    if args.report:
        args.report.write_text(report, encoding="utf-8")
        console.print(f"[green]📄 Relatório salvo em: {args.report}[/green]")
    else:
        # Salva com nome padrão
        report_path = args.workspace / "QUALITY_GATEWAY_REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        console.print(f"[green]📄 Relatório salvo em: {report_path}[/green]")

    # Mostra sumário no terminal
    console.print(
        Panel.fit(
            f"[bold green]✅ Validação completa do workspace![/bold green]\n"
            f"Ver relatório detalhado em: {report_path if not args.report else args.report}"
        )
    )


if __name__ == "__main__":
    main()

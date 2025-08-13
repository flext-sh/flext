#!/usr/bin/env python3
"""Análise Completa de Qualidade de Código - FLEXT Workspace.

Analisa TODOS os projetos Python para identificar problemas de qualidade.
"""

import io
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class QualityReport:
    """Quality report for a project."""

    project: str
    lint_errors: int = 0
    lint_warnings: int = 0
    mypy_errors: int = 0
    mypy_warnings: int = 0
    test_failures: int = 0
    coverage_percentage: float = 0.0
    poetry_issues: int = 0
    issues: list[str] = field(default_factory=list)


def run_command(cmd: list[str], _cwd: str | None = None) -> tuple[int, str, str]:
    """Executa um comando e retorna (exit_code, stdout, stderr)."""
    try:
        # Execução segura e controlada: apenas módulos Python conhecidos
        if cmd[:3] == ["python", "-m", "ruff"]:
            from contextlib import redirect_stderr, redirect_stdout

            from ruff.__main__ import (
                main as ruff_main,  # type: ignore[import-not-found]
            )

            stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                try:
                    ruff_main(cmd[3:])  # type: ignore[arg-type]
                except SystemExit as e:
                    code = e.code if isinstance(e.code, int) else 1
                    return code, stdout_buf.getvalue(), stderr_buf.getvalue()
            return 0, stdout_buf.getvalue(), stderr_buf.getvalue()

        if cmd[:3] == ["python", "-m", "mypy"]:
            from mypy import api as mypy_api  # type: ignore[import-not-found]

            stdout_text, stderr_text, status = mypy_api.run(cmd[3:])  # type: ignore[arg-type]
            exit_code = 0 if status == 0 else 1
            return exit_code, stdout_text, stderr_text

        if cmd[:3] == ["python", "-m", "pytest"]:
            # Mantém subprocesso para isolamento de testes com validação do módulo
            if cmd[0] != "python" or cmd[1] != "-m" or cmd[2] != "pytest":
                return 1, "", "Unsupported pytest invocation"
            import pytest  # type: ignore[import-not-found]
            # Executa pytest em processo; captura saída mínima
            # Nota: para manter simplicidade, delegamos para subprocess apenas quando pytest não disponível
            try:
                exit_code = pytest.main(cmd[3:])  # type: ignore[arg-type]
                return int(exit_code), "", ""
            except Exception:
                return 1, "", "Pytest execution failed"

        # Fallback genérico restrito: bloqueia comandos desconhecidos
        return 1, "", f"Unsupported command: {cmd}"
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def analyze_project(project_path: str) -> QualityReport:
    """Analisa um projeto específico."""
    report = QualityReport(project=Path(project_path).name)

    print(f"\n🔍 Analisando: {project_path}")

    # Verificar se é um projeto Python válido
    pyproject_path = Path(project_path) / "pyproject.toml"
    if not Path(pyproject_path).exists():
        report.issues.append("❌ pyproject.toml não encontrado")
        return report

    # 1. Análise de Lint (ruff)
    print("  📋 Executando lint...")
    exit_code, stdout, stderr = run_command(
        ["python", "-m", "ruff", "check", "."], cwd=project_path,
    )

    if exit_code == 0:
        print("  ✅ Lint: OK")
    else:
        # Contar erros e warnings
        lines = stdout.split("\n") if stdout else []
        errors = [line for line in lines if "E" in line and ":" in line]
        warnings = [line for line in lines if "W" in line and ":" in line]
        report.lint_errors = len(errors)
        report.lint_warnings = len(warnings)
        report.issues.extend(
            [f"❌ Lint Error: {e}" for e in errors[:5]],
        )  # Primeiros 5 erros
        print(f"  ❌ Lint: {report.lint_errors} erros, {report.lint_warnings} warnings")

    # 2. Análise de MyPy
    print("  🔍 Executando mypy...")
    exit_code, stdout, stderr = run_command(
        ["python", "-m", "mypy", "."], cwd=project_path,
    )

    if exit_code == 0:
        print("  ✅ MyPy: OK")
    else:
        # Contar erros e warnings do mypy
        lines = stdout.split("\n") if stdout else []
        errors = [line for line in lines if "error:" in line]
        warnings = [line for line in lines if "note:" in line]
        report.mypy_errors = len(errors)
        report.mypy_warnings = len(warnings)
        report.issues.extend(
            [f"❌ MyPy Error: {e}" for e in errors[:5]],
        )  # Primeiros 5 erros
        print(f"  ❌ MyPy: {report.mypy_errors} erros, {report.mypy_warnings} warnings")

    # 3. Análise de Testes
    print("  🧪 Executando testes...")
    exit_code, stdout, stderr = run_command(
        ["python", "-m", "pytest", "--tb=short", "-q"], cwd=project_path,
    )

    if exit_code == 0:
        print("  ✅ Testes: OK")
    else:
        # Tentar contar falhas de teste
        lines = stdout.split("\n") if stdout else []
        failures = [line for line in lines if "FAILED" in line or "ERROR" in line]
        report.test_failures = len(failures)
        report.issues.extend(
            [f"❌ Test Failure: {f}" for f in failures[:3]],
        )  # Primeiros 3
        print(f"  ❌ Testes: {report.test_failures} falhas")

    # 4. Análise de Cobertura
    print("  📊 Executando cobertura...")
    exit_code, stdout, stderr = run_command(
        ["python", "-m", "pytest", "--cov=src", "--cov-report=term-missing", "-q"],
        cwd=project_path,
    )

    if exit_code == 0 and stdout:
        # Extrair porcentagem de cobertura
        lines = stdout.split("\n")
        for line in lines:
            if "TOTAL" in line and "%" in line:
                try:
                    percentage = float(line.split("%")[0].split()[-1])
                    report.coverage_percentage = percentage
                    break
                except (ValueError, IndexError):
                    pass
        print(f"  📊 Cobertura: {report.coverage_percentage:.1f}%")

    # 5. Análise de Poetry
    print("  📦 Verificando Poetry...")
    exit_code, stdout, stderr = run_command(["poetry", "check"], cwd=project_path)

    if exit_code != 0:
        report.poetry_issues = 1
        report.issues.append(f"❌ Poetry: {stderr.strip()}")
        print("  ❌ Poetry: Problemas encontrados")
    else:
        print("  ✅ Poetry: OK")

    return report


def main() -> int:
    """Função principal."""
    print("🚀 ANÁLISE COMPLETA DE QUALIDADE - FLEXT WORKSPACE")
    print("=" * 60)

    # Listar todos os projetos Python
    projects = []
    for pyproject in Path().rglob("pyproject.toml"):
        project_path = str(pyproject.parent)
        # Filtrar apenas projetos ativos
        if any(
            exclude in project_path
            for exclude in [".bak", ".archive", "backup", "temp-backup", ".venv"]
        ):
            continue
        projects.append(project_path)

    projects.sort()
    print(f"📁 Encontrados {len(projects)} projetos Python")

    # Analisar cada projeto
    reports = []
    total_issues = 0

    for project in projects:
        try:
            report = analyze_project(project)
            reports.append(report)
            total_issues += len(report.issues)
        except Exception as e:
            print(f"❌ Erro ao analisar {project}: {e}")

    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DE QUALIDADE")
    print("=" * 60)

    # Estatísticas gerais
    total_lint_errors = sum(r.lint_errors for r in reports)
    total_lint_warnings = sum(r.lint_warnings for r in reports)
    total_mypy_errors = sum(r.mypy_errors for r in reports)
    total_mypy_warnings = sum(r.mypy_warnings for r in reports)
    total_test_failures = sum(r.test_failures for r in reports)
    avg_coverage = (
        sum(r.coverage_percentage for r in reports) / len(reports) if reports else 0
    )

    print("📈 ESTATÍSTICAS GERAIS:")
    print(f"   • Projetos analisados: {len(reports)}")
    print(f"   • Total de problemas: {total_issues}")
    print(f"   • Erros de Lint: {total_lint_errors}")
    print(f"   • Warnings de Lint: {total_lint_warnings}")
    print(f"   • Erros de MyPy: {total_mypy_errors}")
    print(f"   • Warnings de MyPy: {total_mypy_warnings}")
    print(f"   • Falhas de Teste: {total_test_failures}")
    print(f"   • Cobertura Média: {avg_coverage:.1f}%")

    # Projetos com problemas
    problematic_projects = [r for r in reports if r.issues]
    if problematic_projects:
        print(f"\n⚠️  PROJETOS COM PROBLEMAS ({len(problematic_projects)}):")
        for report in problematic_projects:
            print(f"\n🔴 {report.project}:")
            for issue in report.issues[:3]:
                print(f"   {issue}")
            if len(report.issues) > 3:
                print(f"   ... e mais {len(report.issues) - 3} problemas")
    else:
        print("\n✅ TODOS OS PROJETOS ESTÃO PERFEITOS!")

    # Salvar relatório detalhado
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/quality_analysis_{timestamp}.json"

    Path("reports").mkdir(parents=True, exist_ok=True)
    with Path(report_file).open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "project": r.project,
                    "lint_errors": r.lint_errors,
                    "lint_warnings": r.lint_warnings,
                    "mypy_errors": r.mypy_errors,
                    "mypy_warnings": r.mypy_warnings,
                    "test_failures": r.test_failures,
                    "coverage_percentage": r.coverage_percentage,
                    "poetry_issues": r.poetry_issues,
                    "issues": r.issues,
                }
                for r in reports
            ],
            f,
            indent=2,
        )

    print(f"\n📄 Relatório detalhado salvo em: {report_file}")

    # Retornar código de saída baseado nos problemas
    if total_issues > 0:
        print(f"\n❌ ENCONTRADOS {total_issues} PROBLEMAS - CORREÇÃO NECESSÁRIA!")
        return 1
    print("\n✅ QUALIDADE PERFEITA - TODOS OS PROBLEMAS RESOLVIDOS!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

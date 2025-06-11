#!/usr/bin/env python3
"""Script para gerar relatório completo de cobertura de testes da aplicação FLX.

Este script analisa todos os módulos FLX e gera um relatório abrangente
de cobertura de testes, incluindo métricas por módulo e recomendações.

Usage:
    python scripts/generate_full_coverage_report.py

Features:
    - Análise de cobertura por módulo
    - Identificação de arquivos sem testes
    - Cálculo de métricas de qualidade
    - Geração de relatório HTML e markdown
    - Recomendações de implementação
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click


def flx_run_coverage_analysis(module_path: Path) -> dict[str, Any]:
    """Execute análise de cobertura para um módulo específico.

    Args:
        module_path: Caminho para o módulo

    Returns:
        Dicionário com métricas de cobertura
    """
    try:
        # Executar pytest com coverage
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(module_path / "tests"),
            f"--cov={module_path / 'src'}",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--tb=no",
            "-q",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=module_path, check=False)

        # Ler relatório JSON se existir
        coverage_file = module_path / "coverage.json"
        if coverage_file.exists():
            with coverage_file.open() as f:
                coverage_data = json.load(f)
            coverage_file.unlink()  # Limpar arquivo temporário

            return {
                "module": module_path.name,
                "coverage_percent": coverage_data.get("totals", {}).get(
                    "percent_covered", 0
                ),
                "lines_covered": coverage_data.get("totals", {}).get(
                    "covered_lines", 0
                ),
                "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                "files_analyzed": len(coverage_data.get("files", {})),
                "has_tests": True,
                "test_output": result.stdout,
                "test_errors": result.stderr,
            }
        return {
            "module": module_path.name,
            "coverage_percent": 0,
            "lines_covered": 0,
            "lines_total": flx_count_source_lines(module_path),
            "files_analyzed": 0,
            "has_tests": (module_path / "tests").exists(),
            "test_output": result.stdout,
            "test_errors": result.stderr,
        }

    except Exception as e:
        return {
            "module": module_path.name,
            "coverage_percent": 0,
            "lines_covered": 0,
            "lines_total": flx_count_source_lines(module_path),
            "files_analyzed": 0,
            "has_tests": False,
            "error": str(e),
        }


def flx_count_source_lines(module_path: Path) -> int:
    """Conta linhas de código fonte no módulo.

    Args:
        module_path: Caminho para o módulo

    Returns:
        Número total de linhas de código
    """
    total_lines = 0
    src_path = module_path / "src"

    if not src_path.exists():
        # Tentar buscar arquivos Python diretamente
        for py_file in module_path.rglob("*.py"):
            if "test" not in str(py_file) and ".venv" not in str(py_file):
                try:
                    with py_file.open() as f:
                        total_lines += len(f.readlines())
                except Exception:
                    pass
    else:
        for py_file in src_path.rglob("*.py"):
            try:
                with py_file.open() as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass

    return total_lines


def flx_find_flx_modules(base_path: Path) -> list[Path]:
    """Encontra todos os módulos FLX no workspace.

    Args:
        base_path: Caminho base do workspace

    Returns:
        Lista de caminhos para módulos FLX
    """
    flx_modules = []

    # Módulos FLX conhecidos
    flx_patterns = ["flx", "flx-*", "*flx*"]

    for pattern in flx_patterns:
        for module_dir in base_path.glob(pattern):
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                # Verificar se tem estrutura de projeto Python
                if (
                    (module_dir / "pyproject.toml").exists()
                    or (module_dir / "setup.py").exists()
                    or (module_dir / "src").exists()
                    or any(module_dir.glob("*.py"))
                ):
                    flx_modules.append(module_dir)

    return sorted(flx_modules)


def flx_generate_summary_report(results: list[dict[str, Any]]) -> str:
    """Gera relatório resumido de cobertura.

    Args:
        results: Lista de resultados de cobertura por módulo

    Returns:
        Relatório em formato markdown
    """
    total_modules = len(results)
    modules_with_tests = sum(1 for r in results if r.get("has_tests", False))
    total_lines = sum(r.get("lines_total", 0) for r in results)
    total_covered = sum(r.get("lines_covered", 0) for r in results)
    avg_coverage = (total_covered / total_lines * 100) if total_lines > 0 else 0

    # Classificar módulos por cobertura
    excellent = [r for r in results if r.get("coverage_percent", 0) >= 80]
    good = [r for r in results if 60 <= r.get("coverage_percent", 0) < 80]
    needs_work = [r for r in results if 30 <= r.get("coverage_percent", 0) < 60]
    critical = [r for r in results if r.get("coverage_percent", 0) < 30]

    report = f"""# 📊 RELATÓRIO DE COBERTURA FLX - {datetime.now().strftime("%d/%m/%Y %H:%M")}

## 📈 RESUMO EXECUTIVO

- **Total de Módulos:** {total_modules}
- **Módulos com Testes:** {modules_with_tests} ({modules_with_tests / total_modules * 100:.1f}%)
- **Cobertura Média:** {avg_coverage:.2f}%
- **Linhas Totais:** {total_lines:,}
- **Linhas Cobertas:** {total_covered:,}

## 🎯 CLASSIFICAÇÃO POR COBERTURA

### ✅ Excelente (≥80%): {len(excellent)} módulos
"""

    for module in excellent:
        report += f"- **{module['module']}**: {module['coverage_percent']:.1f}% ({module['lines_covered']}/{module['lines_total']} linhas)\n"

    report += f"""
### 🟡 Bom (60-79%): {len(good)} módulos
"""

    for module in good:
        report += f"- **{module['module']}**: {module['coverage_percent']:.1f}% ({module['lines_covered']}/{module['lines_total']} linhas)\n"

    report += f"""
### ⚠️ Precisa Melhorar (30-59%): {len(needs_work)} módulos
"""

    for module in needs_work:
        report += f"- **{module['module']}**: {module['coverage_percent']:.1f}% ({module['lines_covered']}/{module['lines_total']} linhas)\n"

    report += f"""
### 🔴 Crítico (<30%): {len(critical)} módulos
"""

    for module in critical:
        status = (
            "Sem testes"
            if not module.get("has_tests", False)
            else f"{module['coverage_percent']:.1f}%"
        )
        report += f"- **{module['module']}**: {status} ({module.get('lines_covered', 0)}/{module['lines_total']} linhas)\n"

    report += """
## 🚀 PRÓXIMAS AÇÕES RECOMENDADAS

### Prioridade Alta (Implementar Imediatamente):
"""

    # Módulos críticos sem testes
    no_tests = [r for r in critical if not r.get("has_tests", False)]
    if no_tests:
        for module in no_tests[:3]:  # Top 3 prioridades
            report += (
                f"1. **{module['module']}**: Implementar estrutura básica de testes\n"
            )

    # Módulos com baixa cobertura mas com testes
    low_coverage = [r for r in critical if r.get("has_tests", False)]
    if low_coverage:
        for module in low_coverage[:2]:  # Top 2 prioridades
            report += f"2. **{module['module']}**: Aumentar cobertura de {module['coverage_percent']:.1f}% para 60%+\n"

    report += """
### Prioridade Média (Próximas 2 semanas):
"""

    for module in needs_work[:3]:  # Top 3 módulos que precisam melhorar
        report += f"- **{module['module']}**: Aumentar cobertura para 80%+\n"

    report += """
### Prioridade Baixa (Manutenção):
"""

    for module in good + excellent:
        if module.get("coverage_percent", 0) < 95:
            report += f"- **{module['module']}**: Manter/melhorar cobertura atual\n"

    return report


def flx_generate_detailed_report(results: list[dict[str, Any]]) -> str:
    """Gera relatório detalhado de cobertura.

    Args:
        results: Lista de resultados de cobertura por módulo

    Returns:
        Relatório detalhado em formato markdown
    """
    report = f"""# 📋 RELATÓRIO DETALHADO DE COBERTURA FLX

Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}

## 📊 ANÁLISE POR MÓDULO

"""

    for module_data in sorted(
        results, key=lambda x: x.get("coverage_percent", 0), reverse=True
    ):
        coverage = module_data.get("coverage_percent", 0)
        has_tests = module_data.get("has_tests", False)

        # Determinar status
        if coverage >= 80:
            status_icon = "✅"
            status_text = "EXCELENTE"
        elif coverage >= 60:
            status_icon = "🟡"
            status_text = "BOM"
        elif coverage >= 30:
            status_icon = "⚠️"
            status_text = "PRECISA MELHORAR"
        else:
            status_icon = "🔴"
            status_text = "CRÍTICO"

        report += f"""### {status_icon} {module_data['module']} - {status_text}

- **Cobertura:** {coverage:.2f}%
- **Linhas Cobertas:** {module_data.get('lines_covered', 0):,} / {module_data.get('lines_total', 0):,}
- **Arquivos Analisados:** {module_data.get('files_analyzed', 0)}
- **Possui Testes:** {'✅ Sim' if has_tests else '❌ Não'}
"""

        if module_data.get("error"):
            report += f"- **Erro:** {module_data['error']}\n"

        if module_data.get("test_errors"):
            report += f"- **Erros de Teste:** {module_data['test_errors'][:200]}...\n"

        # Recomendações específicas
        if not has_tests:
            report += """
**🎯 Ações Recomendadas:**
1. Criar estrutura básica de testes (`tests/` directory)
2. Implementar testes unitários para funções principais
3. Configurar pytest e coverage
4. Estabelecer CI/CD para testes automáticos
"""
        elif coverage < 30:
            report += """
**🎯 Ações Recomendadas:**
1. Identificar funções/classes não testadas
2. Implementar testes para código crítico
3. Adicionar testes de integração
4. Melhorar qualidade dos testes existentes
"""
        elif coverage < 60:
            report += """
**🎯 Ações Recomendadas:**
1. Expandir cobertura para edge cases
2. Adicionar testes de erro/exceção
3. Implementar testes de performance
4. Documentar casos de teste
"""
        elif coverage < 80:
            report += """
**🎯 Ações Recomendadas:**
1. Adicionar testes para casos complexos
2. Implementar testes end-to-end
3. Adicionar testes de stress/load
4. Melhorar assertivas dos testes
"""
        else:
            report += """
**🎯 Manutenção:**
1. Manter cobertura atual
2. Atualizar testes conforme mudanças
3. Adicionar testes para novas features
4. Revisar qualidade dos testes periodicamente
"""

        report += "\n---\n\n"

    return report


@click.command()
@click.option(
    "--workspace",
    default=".",
    help="Caminho para o workspace FLX",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--output",
    default="reports/coverage",
    help="Diretório de saída para relatórios",
    type=click.Path(path_type=Path),
)
@click.option(
    "--format",
    "output_format",
    default="all",
    type=click.Choice(["markdown", "json", "all"]),
    help="Formato de saída do relatório",
)
def main(workspace: Path, output: Path, output_format: str) -> None:
    """Gera relatório completo de cobertura para aplicação FLX."""
    print("🔍 Analisando módulos FLX...")

    # Encontrar módulos FLX
    flx_modules = flx_find_flx_modules(workspace)

    if not flx_modules:
        print("❌ Nenhum módulo FLX encontrado no workspace")
        sys.exit(1)

    print(f"📦 Encontrados {len(flx_modules)} módulos FLX:")
    for module in flx_modules:
        print(f"  - {module.name}")

    # Criar diretório de saída
    output.mkdir(parents=True, exist_ok=True)

    # Analisar cada módulo
    results = []
    for i, module_path in enumerate(flx_modules, 1):
        print(f"📊 Analisando {module_path.name} ({i}/{len(flx_modules)})...")
        result = flx_run_coverage_analysis(module_path)
        results.append(result)

        coverage = result.get("coverage_percent", 0)
        status = (
            "✅"
            if coverage >= 80
            else "🟡" if coverage >= 60 else "⚠️" if coverage >= 30 else "🔴"
        )
        print(f"   {status} {coverage:.1f}% cobertura")

    # Gerar relatórios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_format in {"markdown", "all"}:
        # Relatório resumido
        summary_report = flx_generate_summary_report(results)
        summary_file = output / f"flx_coverage_summary_{timestamp}.md"
        with summary_file.open("w", encoding="utf-8") as f:
            f.write(summary_report)
        print(f"📄 Relatório resumido salvo em: {summary_file}")

        # Relatório detalhado
        detailed_report = flx_generate_detailed_report(results)
        detailed_file = output / f"flx_coverage_detailed_{timestamp}.md"
        with detailed_file.open("w", encoding="utf-8") as f:
            f.write(detailed_report)
        print(f"📋 Relatório detalhado salvo em: {detailed_file}")

    if output_format in {"json", "all"}:
        # Dados em JSON
        json_file = output / f"flx_coverage_data_{timestamp}.json"
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "workspace": str(workspace),
                    "total_modules": len(results),
                    "modules": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"💾 Dados JSON salvos em: {json_file}")

    # Resumo final
    total_coverage = sum(r.get("lines_covered", 0) for r in results)
    total_lines = sum(r.get("lines_total", 0) for r in results)
    avg_coverage = (total_coverage / total_lines * 100) if total_lines > 0 else 0

    print("\n🎯 RESUMO FINAL:")
    print(f"   Cobertura Média: {avg_coverage:.2f}%")
    print(f"   Módulos Analisados: {len(results)}")
    print(
        f"   Módulos com Testes: {sum(1 for r in results if r.get('has_tests', False))}"
    )

    if avg_coverage < 50:
        print(
            "⚠️  ATENÇÃO: Cobertura baixa! Recomenda-se implementação massiva de testes."
        )
    elif avg_coverage < 80:
        print("🟡 Cobertura razoável. Foco em melhorar módulos críticos.")
    else:
        print("✅ Excelente cobertura! Manter qualidade dos testes.")


if __name__ == "__main__":
    main()

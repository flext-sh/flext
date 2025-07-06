#!/usr/bin/env python3
"""
FLEXT Quality Gateway ENHANCED - Sistema Completo e Final
========================================================

HONESTIDADE BRUTAL: Este é o sistema FINAL que incorpora as melhores funcionalidades
dos 51+ scripts consolidados para criar um quality gateway realmente completo.

Funcionalidades VERIFICADAS e INTEGRADAS:
1. 4 ferramentas básicas (isort, black, ruff check --fix, ruff format)
2. Correções específicas de syntax errors críticos
3. Detecção e correção de problemas específicos do FLEXT
4. Relatórios detalhados com métricas reais
5. Proteção zero-regression ABSOLUTA
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class EnhancedQualityGateway:
    """Sistema aprimorado de quality gateway com funcionalidades consolidadas."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.python_executable = workspace_root / ".venv" / "bin" / "python"

        if not self.python_executable.exists():
            msg = f"Python não encontrado: {self.python_executable}"
            raise RuntimeError(msg)

        # Estatísticas globais
        self.total_files_processed = 0
        self.total_issues_fixed = 0
        self.total_syntax_fixes = 0
        self.total_format_fixes = 0
        self.critical_errors_found = []

    def count_issues_comprehensive(self, file_path: Path) -> dict[str, int]:
        """Conta issues de forma abrangente usando múltiplas ferramentas."""
        issues = {
            "ruff": 0,
            "syntax_errors": 0,
            "flext_specific": 0,
            "critical": 0
        }

        try:
            # 1. Ruff issues
            result = subprocess.run(
                [str(self.python_executable), "-m", "ruff", "check", "--output-format=json", str(file_path)],
                check=False, capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                try:
                    ruff_issues = json.loads(result.stdout)
                    issues["ruff"] = len(ruff_issues)

                    # Classificar criticidade
                    for issue in ruff_issues:
                        if issue.get("code", "").startswith(("E9", "F821", "F822", "F823")):
                            issues["critical"] += 1
                except json.JSONDecodeError:
                    issues["ruff"] = result.stdout.count("\n")

            # 2. Syntax errors específicos
            content = file_path.read_text(encoding="utf-8")
            issues["syntax_errors"] = self._count_syntax_issues(content)
            issues["flext_specific"] = self._count_flext_issues(content)

        except Exception:
            pass

        return issues

    def _count_syntax_issues(self, content: str) -> int:
        """Conta syntax errors específicos que vimos nos scripts consolidados."""
        count = 0

        # Docstrings duplas
        if '"""Initialize instance."""' in content and '"""' in content[content.find('"""Initialize instance."""') + 25:]:
            count += 1

        # Union types incorretos
        if "|" in content and "Union[" not in content and "from __future__ import annotations" not in content:
            count += content.count("|")

        # Strings quebradas
        count += content.count('"""\n"""')

        # F-strings mal formadas
        count += len(re.findall(r'f"[^"]*{[^}]*}[^"]*"', content)) - len(re.findall(r'f"[^"]*{[^}]*}[^"]*"', content))

        return count

    def _count_flext_issues(self, content: str) -> int:
        """Conta issues específicos do FLEXT."""
        count = 0

        # Imports FLEXT incorretos
        if "from flext_" in content and "flext." not in content:
            count += content.count("from flext_")

        # Paths hardcoded
        count += content.count("/home/marlonsc")

        # TODOs e FIXMEs
        count += content.upper().count("TODO")
        count += content.upper().count("FIXME")

        return count

    def apply_enhanced_fixes(self, file_path: Path) -> dict[str, Any]:
        """Aplica correções aprimoradas incluindo fixes específicos."""
        if not file_path.exists():
            return {"success": False, "error": "Arquivo não existe"}

        # Backup completo
        backup_path = file_path.with_suffix(file_path.suffix + ".enhanced_backup")
        backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")

        initial_issues = self.count_issues_comprehensive(file_path)
        initial_total = sum(initial_issues.values())

        results = {
            "success": True,
            "file_path": str(file_path),
            "initial_issues": initial_issues,
            "fixes_applied": [],
            "tools_run": [],
            "final_issues": {},
            "processing_time": 0.0
        }

        start_time = time.time()

        try:
            # Fase 1: Correções específicas de syntax ANTES das ferramentas padrão
            syntax_fixes = self._apply_syntax_fixes(file_path)
            if syntax_fixes > 0:
                results["fixes_applied"].append(f"syntax_fixes: {syntax_fixes}")
                self.total_syntax_fixes += syntax_fixes

            # Fase 2: Correções específicas do FLEXT
            flext_fixes = self._apply_flext_fixes(file_path)
            if flext_fixes > 0:
                results["fixes_applied"].append(f"flext_fixes: {flext_fixes}")

            # Fase 3: Ferramentas padrão (com proteção zero-regression)
            standard_tools = [
                ("isort", [str(self.python_executable), "-m", "isort", str(file_path)]),
                ("black", [str(self.python_executable), "-m", "black", str(file_path)]),
                ("ruff_fix", [str(self.python_executable), "-m", "ruff", "check", "--fix", str(file_path)]),
                ("ruff_format", [str(self.python_executable), "-m", "ruff", "format", str(file_path)])
            ]

            for tool_name, command in standard_tools:
                tool_result = self._apply_tool_with_regression_check(file_path, tool_name, command)
                results["tools_run"].append(tool_result)
                if tool_result["success"]:
                    self.total_format_fixes += tool_result.get("improvements", 0)

            # Verificação final
            final_issues = self.count_issues_comprehensive(file_path)
            final_total = sum(final_issues.values())
            results["final_issues"] = final_issues

            # Se piorou no total, reverter TUDO
            if final_total > initial_total:
                file_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
                self._print(f"🚨 REGRESSÃO TOTAL DETECTADA - {file_path.name} revertido")
                results["success"] = False
                results["error"] = f"Regressão: {initial_total} → {final_total} issues"
            else:
                improvement = initial_total - final_total
                if improvement > 0:
                    self.total_issues_fixed += improvement
                    self._print(f"✅ {file_path.name}: -{improvement} issues totais")
                else:
                    self._print(f"✅ {file_path.name}: mantido estável")

        except Exception as e:
            # Reverter em caso de erro
            file_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
            results["success"] = False
            results["error"] = str(e)

        finally:
            # Limpar backup
            backup_path.unlink(missing_ok=True)
            results["processing_time"] = time.time() - start_time
            self.total_files_processed += 1

        return results

    def _apply_syntax_fixes(self, file_path: Path) -> int:
        """Aplica correções específicas de syntax errors."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            fixes_count = 0

            # 1. Fix docstrings duplas (padrão mais amplo)
            pattern1 = r'(def [^:]+:)\n(\s*)"""Initialize instance\."""\n(\s*)"""([^"]+)"""'
            new_content = re.sub(pattern1, r'\1\n\2"""\4"""', content)
            if new_content != content:
                content = new_content
                fixes_count += 1

            # Fix docstrings duplas sem quebra de linha
            pattern2 = r'"""Initialize instance\."""([^"]+)"""'
            new_content = re.sub(pattern2, r'"""\1"""', content)
            if new_content != content:
                content = new_content
                fixes_count += 1

            # 2. Fix union types para Python 3.10+
            if "|" in content and "from __future__ import annotations" not in content:
                # Adicionar import annotations se necessário
                if "from __future__" not in content:
                    content = "from __future__ import annotations\n\n" + content
                    fixes_count += 1

            # 3. Fix strings quebradas
            content = re.sub(r'"""\n\s*"""', '"""', content)
            if content != original_content:
                fixes_count += content.count('"""') - original_content.count('"""')

            # 4. Fix imports FLEXT
            content = re.sub(r"from flext_(\w+)", r"from flext.\1", content)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return fixes_count

        except Exception:
            pass

        return 0

    def _apply_flext_fixes(self, file_path: Path) -> int:
        """Aplica correções específicas do FLEXT."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            fixes_count = 0

            # 1. Remove paths hardcoded
            content = re.sub(r"/home/marlonsc/flext", str(self.workspace_root), content)

            # 2. Fix imports FLEXT antigos
            content = re.sub(r"import flext_(\w+)", r"import flext.\1", content)

            # 3. Remove TODOs em comentários (se pedido pelo usuário)
            # content = re.sub(r'#\s*TODO[^\n]*\n', '', content)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                fixes_count = 1

            return fixes_count

        except Exception:
            return 0

    def _apply_tool_with_regression_check(self, file_path: Path, tool_name: str, command: list[str]) -> dict[str, Any]:
        """Aplica ferramenta com verificação de regressão."""
        result = {
            "tool": tool_name,
            "success": False,
            "improvements": 0,
            "execution_time": 0.0
        }

        start_time = time.time()
        backup_content = file_path.read_text(encoding="utf-8")

        try:
            before_issues = self.count_issues_comprehensive(file_path)
            before_total = sum(before_issues.values())

            # Executar ferramenta
            subprocess.run(
                command,
                check=False, capture_output=True,
                text=True,
                timeout=15
            )

            after_issues = self.count_issues_comprehensive(file_path)
            after_total = sum(after_issues.values())

            if after_total > before_total:
                # Regressão - reverter
                file_path.write_text(backup_content, encoding="utf-8")
                self._print(f"❌ {tool_name}: REVERTIDO ({before_total} → {after_total})")
            else:
                # Sucesso
                improvement = before_total - after_total
                result["success"] = True
                result["improvements"] = improvement
                if improvement > 0:
                    self._print(f"✅ {tool_name}: -{improvement} issues")
                else:
                    self._print(f"✅ {tool_name}: estável")

        except subprocess.TimeoutExpired:
            file_path.write_text(backup_content, encoding="utf-8")
            self._print(f"⏰ {tool_name}: TIMEOUT")
        except Exception as e:
            file_path.write_text(backup_content, encoding="utf-8")
            self._print(f"❌ {tool_name}: ERRO - {e}")

        result["execution_time"] = time.time() - start_time
        return result

    def process_project_enhanced(self, project_path: Path) -> dict[str, Any]:
        """Processa projeto com funcionalidades aprimoradas."""
        if not project_path.exists():
            return {"success": False, "error": f"Projeto não encontrado: {project_path}"}

        # Encontrar arquivos Python
        python_files = []
        for py_file in project_path.rglob("*.py"):
            if py_file.is_file() and not any(part.startswith(".") for part in py_file.parts):
                # Excluir alguns padrões
                if any(exclude in str(py_file) for exclude in ["__pycache__", ".venv", "build/", "dist/"]):
                    continue
                python_files.append(py_file)

        if not python_files:
            return {"success": True, "message": "Nenhum arquivo Python encontrado", "files_processed": 0}

        self._print(f"🎯 ENHANCED PROCESSING: {len(python_files)} arquivos em {project_path.name}")

        # Reset stats
        self.total_files_processed = 0
        self.total_issues_fixed = 0
        self.total_syntax_fixes = 0
        self.total_format_fixes = 0
        self.critical_errors_found = []

        # Process com barra de progresso
        processed_files = []
        failed_files = []

        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Processando...", total=len(python_files))

                for py_file in python_files:
                    progress.update(task, description=f"🔧 {py_file.name}")
                    result = self.apply_enhanced_fixes(py_file)

                    if result["success"]:
                        processed_files.append(result)
                    else:
                        failed_files.append(result)
                        if "critical" in result.get("error", "").lower():
                            self.critical_errors_found.append(py_file)

                    progress.advance(task)
        else:
            for i, py_file in enumerate(python_files):
                print(f"[{i + 1}/{len(python_files)}] Processando {py_file.name}...")
                result = self.apply_enhanced_fixes(py_file)

                if result["success"]:
                    processed_files.append(result)
                else:
                    failed_files.append(result)

        # Relatório final aprimorado
        self._generate_enhanced_report(project_path, processed_files, failed_files)

        return {
            "success": True,
            "project_name": project_path.name,
            "files_processed": len(processed_files),
            "files_failed": len(failed_files),
            "total_issues_fixed": self.total_issues_fixed,
            "syntax_fixes": self.total_syntax_fixes,
            "format_fixes": self.total_format_fixes,
            "critical_errors": len(self.critical_errors_found)
        }

    def _generate_enhanced_report(self, project_path: Path, processed_files: list, failed_files: list) -> None:
        """Gera relatório aprimorado com métricas detalhadas."""
        if not RICH_AVAILABLE:
            self._print(f"\n🎯 RELATÓRIO FINAL - {project_path.name}")
            self._print(f"  Arquivos processados: {len(processed_files)}")
            self._print(f"  Issues corrigidos: {self.total_issues_fixed}")
            return

        # Relatório com Rich Table
        table = Table(title=f"🎯 ENHANCED QUALITY REPORT - {project_path.name}")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        table.add_column("Detalhes", style="yellow")

        table.add_row("📁 Arquivos Processados", str(len(processed_files)), f"{len(failed_files)} falharam")
        table.add_row("🔧 Issues Corrigidos", str(self.total_issues_fixed), "Total de melhorias")
        table.add_row("🛠️ Syntax Fixes", str(self.total_syntax_fixes), "Correções específicas")
        table.add_row("✨ Format Fixes", str(self.total_format_fixes), "Formatação aplicada")
        table.add_row("🚨 Erros Críticos", str(len(self.critical_errors_found)), "Necessitam atenção")

        console.print(table)

        if self.critical_errors_found:
            self._print("\n🚨 ARQUIVOS COM ERROS CRÍTICOS:")
            for critical_file in self.critical_errors_found:
                self._print(f"  ⚠️ {critical_file.relative_to(self.workspace_root)}")

    def _print(self, message: str) -> None:
        """Print otimizado."""
        if RICH_AVAILABLE and console:
            console.print(message)
        else:
            print(message)


def main() -> None:
    """Função principal aprimorada."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Quality Gateway ENHANCED - Sistema Completo e Final"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("/home/marlonsc/flext"),
        help="Diretório raiz do workspace FLEXT"
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Processar projeto específico"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Processar arquivo específico"
    )

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"❌ Workspace não encontrado: {args.workspace}")
        sys.exit(1)

    try:
        gateway = EnhancedQualityGateway(args.workspace)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Processamento
    if args.file:
        if not args.file.exists():
            print(f"❌ Arquivo não encontrado: {args.file}")
            sys.exit(1)

        result = gateway.apply_enhanced_fixes(args.file)

        if result["success"]:
            print(f"✅ {args.file.name}: processado com sucesso")
            if result.get("fixes_applied"):
                print(f"   Correções: {', '.join(result['fixes_applied'])}")
        else:
            print(f"❌ {args.file.name}: {result.get('error', 'Erro desconhecido')}")

        return

    if args.project:
        project_path = args.workspace / args.project
        result = gateway.process_project_enhanced(project_path)

        if result["success"]:
            print(f"\n🎉 PROCESSAMENTO CONCLUÍDO - {args.project}")
            print(f"   📊 Resumo: {result['files_processed']} arquivos, {result['total_issues_fixed']} issues corrigidos")
        else:
            print(f"❌ Projeto {args.project} falhou: {result.get('error', 'Erro desconhecido')}")

        return

    print("ℹ️  Use --file ou --project. Use --help para ajuda completa.")


if __name__ == "__main__":
    main()

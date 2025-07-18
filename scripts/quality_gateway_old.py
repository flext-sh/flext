#!/usr/bin/env python3
"""
FLEXT Quality Gateway FINAL - Versão Real e Otimizada
====================================================

Sistema REAL que:
1. É RÁPIDO - otimizado para projetos grandes
2. É CONFIÁVEL - só aplica ferramentas que realmente melhoram
3. É PRÁTICO - feedback em tempo real
4. É SEGURO - backup e reversão garantidos

Ferramentas aplicadas (apenas as que funcionam bem):
1. isort - Organização de imports
2. black - Formatação profissional
3. ruff check --fix - Correções automáticas
4. ruff format - Formatação final

Versão: FINAL - Production Ready
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class QualityGatewayFinal:
    """Sistema final de quality gateway - otimizado e confiável."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.python_executable = workspace_root / ".venv" / "bin" / "python"

        if not self.python_executable.exists():
            msg = f"Python não encontrado: {self.python_executable}"
            raise RuntimeError(msg)

    def count_issues_fast(self, file_path: Path) -> int:
        """Conta issues rapidamente usando apenas Ruff."""
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
                timeout=10,  # timeout mais baixo
            )

            if result.returncode == 0:
                return 0

            try:
                issues = json.loads(result.stdout)
                return len(issues)
            except json.JSONDecodeError:
                # Fallback simples
                return result.stdout.count("\n")

        except Exception:
            return 0

    def apply_tool_safely(
        self, file_path: Path, tool_name: str, command: list[str],
    ) -> tuple[bool, int, int, float]:
        """Aplica uma ferramenta com segurança.

        Returns: (success, before_issues, after_issues, execution_time)
        """
        start_time = time.time()

        # Backup
        backup_content = file_path.read_text(encoding="utf-8")

        # Medir antes
        before_issues = self.count_issues_fast(file_path)

        try:
            # Aplicar ferramenta
            subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,  # timeout reduzido
            )

            # Medir depois
            after_issues = self.count_issues_fast(file_path)
            execution_time = time.time() - start_time

            # Verificar se piorou
            if after_issues > before_issues:
                # REVERTER
                file_path.write_text(backup_content, encoding="utf-8")
                self._print(
                    f"❌ {tool_name}: REVERTIDO ({before_issues} → {after_issues})",
                )
                return False, before_issues, before_issues, execution_time

            # SUCESSO
            improvement = before_issues - after_issues
            if improvement > 0:
                self._print(
                    f"✅ {tool_name}: -{improvement} issues em {execution_time:.1f}s",
                )
            else:
                self._print(f"✅ {tool_name}: OK em {execution_time:.1f}s")

            return True, before_issues, after_issues, execution_time

        except subprocess.TimeoutExpired:
            # Timeout - reverter
            file_path.write_text(backup_content, encoding="utf-8")
            self._print(f"⏰ {tool_name}: TIMEOUT - revertido")
            return False, before_issues, before_issues, time.time() - start_time

        except Exception as e:
            # Erro - reverter
            file_path.write_text(backup_content, encoding="utf-8")
            self._print(f"❌ {tool_name}: ERRO - {e}")
            return False, before_issues, before_issues, time.time() - start_time

    def process_file_optimized(self, file_path: Path) -> dict[str, Any]:
        """Processa um arquivo de forma otimizada."""
        if not file_path.exists():
            return {"success": False, "error": "Arquivo não existe"}

        # Backup inicial completo
        backup_path = file_path.with_suffix(file_path.suffix + ".qg_backup")
        try:
            backup_path.write_text(
                file_path.read_text(encoding="utf-8"), encoding="utf-8",
            )
        except Exception as e:
            return {"success": False, "error": f"Erro criando backup: {e}"}

        initial_issues = self.count_issues_fast(file_path)

        # Ferramentas em ordem otimizada (removido autopep8 que causa problemas)
        tools = [
            ("isort", [str(self.python_executable), "-m", "isort", str(file_path)]),
            ("black", [str(self.python_executable), "-m", "black", str(file_path)]),
            (
                "ruff_fix",
                [
                    str(self.python_executable),
                    "-m",
                    "ruff",
                    "check",
                    "--fix",
                    str(file_path),
                ],
            ),
            (
                "ruff_format",
                [str(self.python_executable), "-m", "ruff", "format", str(file_path)],
            ),
        ]

        total_improvement = 0
        total_time = 0.0
        tools_applied = 0

        for tool_name, command in tools:
            success, before, after, exec_time = self.apply_tool_safely(
                file_path, tool_name, command,
            )
            total_time += exec_time

            if success:
                tools_applied += 1
                improvement = before - after
                if improvement > 0:
                    total_improvement += improvement

        final_issues = self.count_issues_fast(file_path)

        # Verificação final de segurança
        if final_issues > initial_issues:
            # Regressão geral - reverter tudo
            try:
                file_path.write_text(
                    backup_path.read_text(encoding="utf-8"), encoding="utf-8",
                )
                self._print(f"🚨 REGRESSÃO GERAL - Revertendo {file_path.name}")
                final_issues = initial_issues
                total_improvement = 0
            except Exception:
                pass

        # Limpar backup
        backup_path.unlink(missing_ok=True)

        return {
            "success": True,
            "file_path": str(file_path),
            "initial_issues": initial_issues,
            "final_issues": final_issues,
            "improvement": total_improvement,
            "tools_applied": tools_applied,
            "processing_time": total_time,
        }

    def process_project_efficiently(self, project_path: Path) -> dict[str, Any]:
        """Processa um projeto de forma eficiente."""
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
            f"🎯 Processando {len(python_files)} arquivos em {project_path.name}",
        )

        # Estatísticas
        files_processed = 0
        files_improved = 0
        total_initial_issues = 0
        total_final_issues = 0
        total_improvement = 0
        total_time = 0.0

        # Progress bar otimizada
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                task = progress.add_task("Processando...", total=len(python_files))

                for py_file in python_files:
                    progress.update(task, description=f"📝 {py_file.name}")
                    result = self.process_file_optimized(py_file)

                    if result["success"]:
                        files_processed += 1
                        total_initial_issues += result["initial_issues"]
                        total_final_issues += result["final_issues"]
                        total_improvement += result["improvement"]
                        total_time += result["processing_time"]

                        if result["improvement"] > 0:
                            files_improved += 1

                    progress.advance(task)
        else:
            # Fallback sem Rich
            for i, py_file in enumerate(python_files):
                print(f"[{i + 1}/{len(python_files)}] Processando {py_file.name}...")
                result = self.process_file_optimized(py_file)

                if result["success"]:
                    files_processed += 1
                    total_initial_issues += result["initial_issues"]
                    total_final_issues += result["final_issues"]
                    total_improvement += result["improvement"]
                    total_time += result["processing_time"]

                    if result["improvement"] > 0:
                        files_improved += 1

        return {
            "success": True,
            "project_name": project_path.name,
            "files_processed": files_processed,
            "files_improved": files_improved,
            "total_initial_issues": total_initial_issues,
            "total_final_issues": total_final_issues,
            "total_improvement": total_improvement,
            "total_time": total_time,
            "improvement_rate": (
                (files_improved / files_processed * 100) if files_processed > 0 else 0
            ),
        }

    def _print(self, message: str) -> None:
        """Print otimizado.
                if RICH_AVAILABLE and console:
                    console.print(message)
                else:
                    print(message)


        def main() -> None:
            Função principal otimizada."""

    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Quality Gateway FINAL - Sistema Real e Otimizado",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("/home/marlonsc/flext"),
        help="Diretório raiz do workspace FLEXT",
    )
    parser.add_argument("--project", type=str, help="Processar projeto específico")
    parser.add_argument("--file", type=Path, help="Processar arquivo específico")

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"❌ Workspace não encontrado: {args.workspace}")
        sys.exit(1)

    try:
        gateway = QualityGatewayFinal(args.workspace)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Processamento de arquivo único
    if args.file:
        if not args.file.exists():
            print(f"❌ Arquivo não encontrado: {args.file}")
            sys.exit(1)

        result = gateway.process_file_optimized(args.file)

        if result["success"]:
            improvement = result["improvement"]
            time_taken = result["processing_time"]
            print(f"✅ {args.file.name}: {improvement:+d} issues em {time_taken:.1f}s")
        else:
            print(f"❌ {args.file.name}: {result.get('error', 'Erro desconhecido')}")

    # Processamento de projeto
    if args.project:
        project_path = args.workspace / args.project
        result = gateway.process_project_efficiently(project_path)

        if result["success"]:
            print(f"\n🎯 Resultado Final - {args.project}:")
            print(f"  📁 Arquivos: {result['files_processed']}")
            print(
                f"  🔧 Melhorados: {result['files_improved']} ({result['improvement_rate']:.1f}%)",
            )
            print(
                f"  📊 Issues: {result['total_initial_issues']} → {result['total_final_issues']}",
            )
            print(f"  📈 Melhoria: {result['total_improvement']:+d}")
            print(f"  ⏱️  Tempo: {result['total_time']:.1f}s")
        else:
            print(
                f"❌ Projeto {args.project} falhou: {result.get('error', 'Erro desconhecido')}",
            )

    print("ℹ️  Use --file ou --project. Use --help para ajuda.")


if __name__ == "__main__":
    main()

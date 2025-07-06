#!/usr/bin/env python3
"""
FLEXT Syntax Fixer - Automated Python Syntax Error Correction
============================================================

Sistema automatizado e seguro para correção de erros de sintaxe em Python:
1. Corrige padrões comuns de forma segura
2. Faz backup antes de modificar arquivos
3. Valida cada correção antes de confirmar
4. Gera relatórios detalhados de correções

Autor: FLEXT Quality Team
Versão: 1.0.0
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class SyntaxPattern:
    """Representa um padrão de sintaxe que pode ser corrigido automaticamente."""

    def __init__(self, name: str, description: str, pattern: str, replacement: str, safe: bool = True) -> None:
        self.name = name
        self.description = description
        self.pattern = pattern
        self.replacement = replacement
        self.safe = safe


class SyntaxFixer:
    """Corrige erros de sintaxe Python de forma automatizada e segura."""

    # Padrões de correção segura
    SAFE_PATTERNS = [
        SyntaxPattern(
            "isolated_colons",
            "Remove linhas com apenas dois pontos isolados",
            r"^:\s*$",
            "",
            safe=True
        ),
        SyntaxPattern(
            "classmethod_colon",
            "Remove dois pontos após @classmethod",
            r"@classmethod:\s*$",
            "@classmethod",
            safe=True
        ),
        SyntaxPattern(
            "abstractmethod_colon",
            "Remove dois pontos após @abstractmethod",
            r"@abstractmethod:\s*$",
            "@abstractmethod",
            safe=True
        ),
        SyntaxPattern(
            "docstring_colon",
            "Remove dois pontos ao final de docstrings",
            r'"""([^"]*?)""":(\s*)$',
            r'"""\1"""\2',
            safe=True
        ),
        SyntaxPattern(
            "self_parameter_colon",
            "Corrige self: para self, em parâmetros de função",
            r"\bself:\s*$",
            "self,",
            safe=True
        ),
    ]

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.backup_dir = workspace_root / ".syntax_fixes_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "syntax_errors_before": 0,
            "syntax_errors_after": 0,
            "patterns_applied": {},
        }

    def create_backup(self, file_path: Path) -> Path:
        """Cria backup de um arquivo antes de modificá-lo."""
        backup_path = self.backup_dir / file_path.relative_to(self.workspace_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def test_python_syntax(self, file_path: Path) -> tuple[bool, str]:
        """Testa se um arquivo Python tem sintaxe válida."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                check=False, capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            return result.returncode == 0, result.stderr
        except Exception as e:
            return False, str(e)

    def apply_pattern_to_file(self, file_path: Path, pattern: SyntaxPattern) -> bool:
        """Aplica um padrão de correção a um arquivo."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            import re
            original_content = content

            # Aplica a correção baseada no tipo de padrão
            if pattern.name == "isolated_colons":
                # Remove linhas com apenas dois pontos
                lines = content.split("\n")
                new_lines = [line for line in lines if line.strip() != ":"]
                content = "\n".join(new_lines)
            else:
                # Usa regex para outros padrões
                content = re.sub(pattern.pattern, pattern.replacement, content, flags=re.MULTILINE)

            # Se houve mudança, salva o arquivo
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            console.print(f"[red]Erro ao aplicar padrão {pattern.name} em {file_path}: {e}[/red]")
            return False

    def fix_file(self, file_path: Path) -> dict[str, any]:
        """Corrige um arquivo Python aplicando padrões seguros."""
        result = {
            "file": str(file_path),
            "syntax_valid_before": False,
            "syntax_valid_after": False,
            "patterns_applied": [],
            "backup_created": False,
            "error": None
        }

        try:
            # Testa sintaxe inicial
            syntax_ok_before, _error_before = self.test_python_syntax(file_path)
            result["syntax_valid_before"] = syntax_ok_before

            # Se já está válido, não precisa de correção
            if syntax_ok_before:
                return result

            # Cria backup
            backup_path = self.create_backup(file_path)
            result["backup_created"] = True

            # Aplica padrões seguros
            file_modified = False
            for pattern in self.SAFE_PATTERNS:
                if self.apply_pattern_to_file(file_path, pattern):
                    result["patterns_applied"].append(pattern.name)
                    file_modified = True

                    # Incrementa estatística do padrão
                    if pattern.name not in self.stats["patterns_applied"]:
                        self.stats["patterns_applied"][pattern.name] = 0
                    self.stats["patterns_applied"][pattern.name] += 1

            # Testa sintaxe final
            syntax_ok_after, _error_after = self.test_python_syntax(file_path)
            result["syntax_valid_after"] = syntax_ok_after

            # Se não melhorou, restaura o backup
            if not syntax_ok_after and file_modified:
                shutil.copy2(backup_path, file_path)
                result["patterns_applied"] = []
                console.print(f"[yellow]Restaurado backup para {file_path} - correções não melhoraram sintaxe[/yellow]")

            if file_modified and syntax_ok_after:
                self.stats["files_modified"] += 1

        except Exception as e:
            result["error"] = str(e)
            console.print(f"[red]Erro ao processar {file_path}: {e}[/red]")

        return result

    def find_python_files(self, directory: Path) -> list[Path]:
        """Encontra todos os arquivos Python em um diretório."""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Ignora diretórios de cache e virtuais
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "venv", ".venv"}]

            python_files.extend(Path(root) / file for file in files if file.endswith(".py"))

        return python_files

    def fix_project(self, project_path: Path) -> dict[str, any]:
        """Corrige todos os arquivos Python em um projeto."""
        if not project_path.exists():
            return {"error": f"Projeto não encontrado: {project_path}"}

        console.print(f"[cyan]Processando projeto: {project_path.name}[/cyan]")

        python_files = self.find_python_files(project_path)
        results = []

        # Conta erros de sintaxe inicial
        syntax_errors_before = 0
        for file_path in python_files:
            syntax_ok, _ = self.test_python_syntax(file_path)
            if not syntax_ok:
                syntax_errors_before += 1

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Corrigindo {len(python_files)} arquivos...", total=len(python_files))

            for file_path in python_files:
                result = self.fix_file(file_path)
                results.append(result)
                self.stats["files_processed"] += 1
                progress.advance(task)

        # Conta erros de sintaxe final
        syntax_errors_after = 0
        for file_path in python_files:
            syntax_ok, _ = self.test_python_syntax(file_path)
            if not syntax_ok:
                syntax_errors_after += 1

        return {
            "project": str(project_path),
            "files_processed": len(python_files),
            "syntax_errors_before": syntax_errors_before,
            "syntax_errors_after": syntax_errors_after,
            "files_fixed": len([r for r in results if r["patterns_applied"]]),
            "results": results
        }

    def fix_workspace(self, project_names: list[str] | None = None) -> None:
        """Corrige todos os projetos no workspace ou uma lista específica."""
        console.print(Panel.fit(
            "[bold blue]FLEXT Syntax Fixer[/bold blue]\n"
            "Correção automatizada e segura de erros de sintaxe Python",
            border_style="blue"
        ))

        # Se não especificado, processa todos os projetos
        if not project_names:
            project_names = [
                "flext-core", "flext-auth", "flext-api", "flext-grpc", "flext-web",
                "flext-cli", "flext-plugin", "flext-observability", "flext-meltano",
                "flext-ldap", "flext-quality", "flext-db-oracle"
            ]

        all_results = []

        for project_name in project_names:
            project_path = self.workspace_root / project_name
            if project_path.exists():
                result = self.fix_project(project_path)
                all_results.append(result)

                # Atualiza estatísticas globais
                if "syntax_errors_before" in result:
                    self.stats["syntax_errors_before"] += result["syntax_errors_before"]
                    self.stats["syntax_errors_after"] += result["syntax_errors_after"]

        self.print_summary(all_results)

    def print_summary(self, results: list[dict]) -> None:
        """Imprime resumo das correções aplicadas."""
        console.print("\n[bold green]Resumo das Correções[/bold green]")

        # Tabela de resultados por projeto
        table = Table(title="Resultados por Projeto")
        table.add_column("Projeto", style="cyan")
        table.add_column("Arquivos", justify="right")
        table.add_column("Erros Antes", justify="right", style="red")
        table.add_column("Erros Depois", justify="right", style="yellow")
        table.add_column("Corrigidos", justify="right", style="green")
        table.add_column("Status", style="bold")

        for result in results:
            if "error" in result:
                table.add_row(
                    result.get("project", "?"),
                    "N/A", "N/A", "N/A", "N/A",
                    f"[red]Erro: {result['error']}[/red]"
                )
            else:
                project_name = Path(result["project"]).name
                files_count = str(result["files_processed"])
                errors_before = str(result["syntax_errors_before"])
                errors_after = str(result["syntax_errors_after"])
                files_fixed = str(result["files_fixed"])

                if result["syntax_errors_after"] == 0:
                    status = "[green]✓ Limpo[/green]"
                elif result["syntax_errors_after"] < result["syntax_errors_before"]:
                    status = "[yellow]⚠ Melhorado[/yellow]"
                else:
                    status = "[red]✗ Problemas[/red]"

                table.add_row(project_name, files_count, errors_before, errors_after, files_fixed, status)

        console.print(table)

        # Estatísticas globais
        console.print("\n[bold]Estatísticas Globais:[/bold]")
        console.print(f"Arquivos processados: {self.stats['files_processed']}")
        console.print(f"Arquivos modificados: {self.stats['files_modified']}")
        console.print(f"Erros de sintaxe antes: {self.stats['syntax_errors_before']}")
        console.print(f"Erros de sintaxe depois: {self.stats['syntax_errors_after']}")

        if self.stats["syntax_errors_before"] > 0:
            improvement = ((self.stats["syntax_errors_before"] - self.stats["syntax_errors_after"]) /
                          self.stats["syntax_errors_before"]) * 100
            console.print(f"Melhoria: {improvement:.1f}%")

        # Padrões aplicados
        if self.stats["patterns_applied"]:
            console.print("\n[bold]Padrões Aplicados:[/bold]")
            for pattern, count in self.stats["patterns_applied"].items():
                console.print(f"  {pattern}: {count} vezes")

        console.print(f"\n[bold]Backups salvos em:[/bold] {self.backup_dir}")


def main() -> None:
    """Função principal do script."""
    workspace_root = Path(__file__).parent.parent

    # Parse argumentos simples
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        console.print("""
[bold]FLEXT Syntax Fixer[/bold]

Uso:
  python syntax_fixer.py [projeto1] [projeto2] ...

Exemplos:
  python syntax_fixer.py                    # Corrige todos os projetos
  python syntax_fixer.py flext-core         # Corrige apenas flext-core
  python syntax_fixer.py flext-core flext-auth  # Corrige projetos específicos

O script cria backups automáticos antes de qualquer modificação.
""")
        return

    # Lista de projetos específicos ou None para todos
    projects = sys.argv[1:] if len(sys.argv) > 1 else None

    fixer = SyntaxFixer(workspace_root)
    fixer.fix_workspace(projects)


if __name__ == "__main__":
    main()

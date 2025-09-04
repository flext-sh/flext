#!/usr/bin/env python3
"""FlextResult Type Consistency Auditor.

Audita e verifica consistências de tipos FlextResult em todos os projetos FLEXT
usando flext_tools.quality para máxima confiabilidade e padronização enterprise.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from flext_core import FlextResult

from flext_tools import Colors, FlextScript, ScriptMetadata, print_colored


class FlextResultTypeAuditor(FlextScript):
    """Audit FlextResult type consistency across all FLEXT projects."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="flextresult_type_auditor",
            description="Audit FlextResult type consistency across FLEXT ecosystem",
            category="quality",
            version="1.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate preconditions."""
        if not self._is_git_repository():
            print_colored("❌ Not in a git repository", Colors.RED)
            return FlextResult[None].fail("Not in a git repository")
        return FlextResult[None].ok(None)

    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        return Path(".git").exists()

    def _is_ignored_by_git(self, file_path: str, project_dir: str = ".") -> bool:
        """Verifica se um arquivo está ignorado pelo git usando git check-ignore."""

        def _validate_git_available() -> str:
            git_path = shutil.which("git")
            if not git_path:
                msg = "git executable not found"
                raise FileNotFoundError(msg)
            return git_path

        try:
            git_path = _validate_git_available()

            # Usa git check-ignore para verificar se o arquivo é ignorado
            result = subprocess.run(
                [git_path, "check-ignore", file_path],
                check=False,
                cwd=project_dir,
                capture_output=True,
                text=True,
            )
            # Se o exit code for 0, o arquivo está ignorado
            return result.returncode == 0

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Se git não estiver disponível ou der erro, usa lista básica de exclusões
            ignored_patterns = [
                ".venv",
                "venv",
                "__pycache__",
                ".git",
                ".meltano",
                "node_modules",
                ".pytest_cache",
                ".mypy_cache",
                ".tox",
                "build",
                "dist",
            ]
            return any(pattern in file_path for pattern in ignored_patterns)

    def _find_flext_projects(self) -> list[str]:
        """Encontra todos os projetos flext no workspace usando git submodules."""
        projects = []

        # Adiciona o projeto raiz (workspace principal)
        projects.append(".")

        try:
            result = subprocess.run(
                ["git", "submodule", "status"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    # Extrai o nome do projeto da linha do git submodule status
                    parts = line.split()
                    if len(parts) >= 2:
                        project_name = parts[1]
                        if Path(project_name).is_dir():
                            projects.append(project_name)
            return sorted(projects)
        except subprocess.CalledProcessError:
            # Fallback para método antigo se git submodule falhar
            fallback_projects = [
                item.name
                for item in Path().iterdir()
                if item.is_dir() and item.name.startswith("flext-")
            ]
            return sorted(fallback_projects)

    def _find_python_files(self, project_dir: str) -> list[str]:
        """Encontra todos os arquivos .py no projeto respeitando .gitignore."""
        py_files = []
        project_path = Path(project_dir)

        for root, dirs, files in os.walk(project_path):
            # Remove diretórios ignorados da lista para não percorrer
            dirs[:] = [
                d
                for d in dirs
                if not self._is_ignored_by_git(str(Path(root) / d), project_dir)
            ]

            for file in files:
                if file.endswith(".py"):
                    full_path = str(Path(root) / file)
                    if not self._is_ignored_by_git(full_path, project_dir):
                        py_files.append(full_path)
        return py_files

    def _check_flextresult_inconsistencies(
        self, file_path: str
    ) -> list[dict[str, object]]:
        """Verifica inconsistências de FlextResult em um arquivo."""
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print_colored(f"❌ Erro ao ler {file_path}: {e}", Colors.RED)
            return []

        # Padrões para encontrar declarações de métodos e retornos
        method_pattern = r"def\s+(\w+)\([^)]*\)\s*->\s*FlextResult\[([^\]]+)\]:"
        return_pattern = r"return\s+FlextResult\.(?:success|error)\(\)"

        issues = []
        lines = content.split("\n")

        # Procura por métodos que retornam FlextResult[T] mas fazem return FlextResult.success()
        for i, line in enumerate(lines):
            method_match = re.search(method_pattern, line)
            if method_match:
                method_name = method_match.group(1)
                return_type = method_match.group(2)

                # Se o tipo de retorno não é None, procura returns problemáticos
                if return_type.strip() != "None":
                    # Procura pelo corpo do método
                    for j in range(
                        i + 1, min(i + 50, len(lines))
                    ):  # Até 50 linhas depois
                        if lines[j].strip().startswith("def "):  # Próximo método
                            break
                        if re.search(return_pattern, lines[j]):
                            issues.append({
                                "file": file_path,
                                "line": j + 1,
                                "method": method_name,
                                "declared_type": return_type,
                                "issue": f"Método declara FlextResult[{return_type}] mas retorna FlextResult.success()/error() sem valor",
                            })

        # Procura por outros padrões problemáticos
        for i, line in enumerate(lines):
            # Ignora comentários e strings que contêm padrões de exemplo
            if (
                line.strip().startswith("#")
                or '"""' in line
                or "'" in line
                or '"' in line
            ):
                continue

            if (
                "FlextResult" in line
                and "FlextResult[None]" in line
                and "FlextResult[dict" in line
            ):
                issues.append({
                    "file": file_path,
                    "line": i + 1,
                    "method": "unknown",
                    "declared_type": "mixed",
                    "issue": "Possível inconsistência entre FlextResult[None] e FlextResult[dict]",
                })

        return issues

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute FlextResult type consistency audit."""
        print_colored(
            "🔍 Verificando inconsistências de FlextResult em todos os projetos flext...",
            Colors.CYAN,
        )
        print_colored("=" * 80, Colors.CYAN)

        projects = self._find_flext_projects()
        all_issues = []

        for project in projects:
            project_name = "workspace-raiz" if project == "." else project
            print_colored(f"\n📁 Analisando projeto: {project_name}", Colors.BLUE)

            py_files = self._find_python_files(project)
            project_issues = []

            for file_path in py_files:
                issues = self._check_flextresult_inconsistencies(file_path)
                project_issues.extend(issues)

            if project_issues:
                print_colored(
                    f"   ⚠️  {len(project_issues)} problemas encontrados", Colors.YELLOW
                )
                all_issues.extend(project_issues)
            else:
                print_colored("   ✅ Nenhum problema encontrado", Colors.GREEN)

        print_colored("\n" + "=" * 80, Colors.CYAN)
        print_colored("📊 RESUMO GERAL:", Colors.CYAN)
        print_colored(f"Total de projetos analisados: {len(projects)}", Colors.BLUE)
        print_colored(f"Total de problemas encontrados: {len(all_issues)}", Colors.BLUE)

        if all_issues:
            print_colored("\n🔧 PROBLEMAS DETALHADOS:", Colors.YELLOW)
            current_project = None
            for issue in all_issues:
                project_name = str(issue["file"]).split("/")[0]
                if project_name != current_project:
                    current_project = project_name
                    print_colored(f"\n📁 {project_name}:", Colors.BLUE)

                print_colored(f"   📄 {issue['file']}:{issue['line']}", Colors.WHITE)
                print_colored(f"      Método: {issue['method']}", Colors.WHITE)
                print_colored(
                    f"      Tipo declarado: FlextResult[{issue['declared_type']}]",
                    Colors.WHITE,
                )
                print_colored(f"      Problema: {issue['issue']}", Colors.WHITE)

        exit_code = len(all_issues)
        status_msg = (
            "🎉 Análise concluída!" if exit_code == 0 else "⚠️  Problemas encontrados!"
        )
        color = Colors.GREEN if exit_code == 0 else Colors.YELLOW
        print_colored(f"\n{status_msg}", color)

        return FlextResult[object].ok({"issues_count": exit_code, "issues": all_issues})


def main() -> int:
    """Main entry point."""
    auditor = FlextResultTypeAuditor()
    return auditor.run()


if __name__ == "__main__":
    sys.exit(main())

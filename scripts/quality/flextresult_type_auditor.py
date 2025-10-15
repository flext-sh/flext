# !/usr/bin/env python3
"""FlextCore.Result Type Consistency Auditor.

Audita e verifica consistências de tipos FlextCore.Result em todos os projetos FLEXT
usando flext_tools.quality para máxima confiabilidade e padronização enterprise.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast

from flext_core import FlextCore

from flext_tools import Colors, FlextScript, ScriptMetadata, print_colored


class FlextResultTypeAuditor(FlextScript):
    """Audit FlextCore.Result type consistency across all FLEXT projects."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="flextresult_type_auditor",
            description="Audit FlextCore.Result type consistency across FLEXT ecosystem",
            category="quality",
            version="1.0.0",
        )

    def validate_preconditions(self) -> FlextCore.Result[None]:
        """Validate preconditions."""
        if not self._is_git_repository():
            print_colored("❌ Not in a git repository", Colors.RED)
            return FlextCore.Result[None].fail("Not in a git repository")
        return FlextCore.Result[None].ok(None)

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
            result = FlextCore.Utilities.run_external_command(
                [git_path, "check-ignore", file_path],
                check=False,
                cwd=project_dir,
                capture_output=True,
                text=True,
            )
            # Se o exit code for 0, o arquivo está ignorado
            #  needs to be unwrapped to access CompletedProcess attributes
            return result.value.returncode == 0 if result.is_success else False

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

    def _find_flext_projects(self) -> FlextCore.Types.StringList:
        """Encontra todos os projetos flext no workspace usando git submodules."""
        projects: list[str] = []
        # Adiciona o projeto raiz (workspace principal)
        projects.append(".")

        try:
            result = FlextCore.Utilities.run_external_command(
                ["/usr/bin/git", "submodule", "status"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.value.stdout.strip().split("\n"):
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
        py_files: list[str] = []
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
        self,
        file_path: str,
    ) -> list[dict[str, object]]:
        """Verifica inconsistências de FlextCore.Result em um arquivo."""
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print_colored(f"❌ Erro ao ler {file_path}: {e}", Colors.RED)
            return []

        # Padrões para encontrar declarações de métodos e retornos
        method_pattern = r"def\s+(\w+)\([^)]*\)\s*->\s*FlextCore.Result\[([^\]]+)\]:"
        return_pattern = r"return\s+FlextCore.Result\.(?:Union[success, error])\(\)"

        issues: FlextCore.Types.List = []
        lines = content.split("\n")

        # Procura por métodos que retornam FlextCore.Result[T] mas fazem return FlextCore.Result.success()
        for i, line in enumerate(lines):
            method_match = re.search(method_pattern, line)
            if method_match:
                method_name = method_match.group(1)
                return_type = method_match.group(2)

                # Se o tipo de retorno não é None, procura returns problemáticos
                if return_type.strip() != "None":
                    # Procura pelo corpo do método
                    for j in range(
                        i + 1,
                        min(i + 50, len(lines)),
                    ):  # Até 50 linhas depois
                        if lines[j].strip().startswith("def "):  # Próximo método
                            break
                        if re.search(return_pattern, lines[j]):
                            issues.append(
                                {
                                    "file": file_path,
                                    "line": j + 1,
                                    "method": method_name,
                                    "declared_type": return_type,
                                    "issue": f"Método declara FlextCore.Result[{return_type}] mas retorna FlextCore.Result.success()/error() sem valor",
                                },
                            )

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
                "FlextCore.Result" in line
                and "FlextCore.Result[None]" in line
                and "FlextCore.Result[dict" in line
            ):
                issues.append(
                    {
                        "file": file_path,
                        "line": i + 1,
                        "method": "unknown",
                        "declared_type": "mixed",
                        "issue": "Possível inconsistência entre FlextCore.Result[None] e FlextCore.Result[FlextCore.Types.Dict]",
                    },
                )

        return cast("list[dict[str, object]]", issues)

    def execute_implementation(
        self, **_kwargs: dict[str, str]
    ) -> FlextCore.Result[dict[str, str]]:
        """Execute FlextCore.Result type consistency audit."""
        print_colored(
            "🔍 Verificando inconsistências de FlextCore.Result em todos os projetos flext...",
            Colors.BLUE,
        )
        print_colored("=" * 80, Colors.BLUE)

        projects = self._find_flext_projects()
        all_issues: list[dict[str, object]] = []
        for project in projects:
            project_name = "workspace-raiz" if project == "." else project
            print_colored(f"\n📁 Analisando projeto: {project_name}", Colors.BLUE)

            py_files = self._find_python_files(project)
            project_issues: list[dict[str, object]] = []
            for file_path in py_files:
                issues = self._check_flextresult_inconsistencies(file_path)
                project_issues.extend(issues)

            if project_issues:
                print_colored(
                    f"   ⚠️  {len(project_issues)} problemas encontrados",
                    Colors.YELLOW,
                )
                all_issues.extend(project_issues)
            else:
                print_colored("   ✅ Nenhum problema encontrado", Colors.GREEN)

        print_colored("\n" + "=" * 80, Colors.BLUE)
        print_colored("📊 RESUMO GERAL:", Colors.BLUE)
        print_colored(f"Total de projetos analisados: {len(projects)}", Colors.BLUE)
        print_colored(f"Total de problemas encontrados: {len(all_issues)}", Colors.BLUE)

        if all_issues:
            print_colored("\n🔧 PROBLEMAS DETALHADOS:", Colors.YELLOW)
            current_project = None
            for issue in all_issues:
                issue_dict: dict[str, object] = issue
                project_name = str(issue_dict["file"]).split("/")[0]
                if project_name != current_project:
                    current_project = project_name
                    print_colored(f"\n📁 {project_name}:", Colors.BLUE)

                print_colored(
                    f"   📄 {issue_dict['file']}:{issue_dict['line']}", Colors.BLUE
                )
                print_colored(f"      Método: {issue_dict['method']}", Colors.BLUE)
                print_colored(
                    f"      Tipo declarado: FlextCore.Result[{issue_dict['declared_type']}]",
                    Colors.BLUE,
                )
                print_colored(f"      Problema: {issue_dict['issue']}", Colors.BLUE)

        exit_code = len(all_issues)
        status_msg = (
            "🎉 Análise concluída!" if exit_code == 0 else "⚠️  Problemas encontrados!"
        )
        color = Colors.GREEN if exit_code == 0 else Colors.YELLOW
        print_colored(f"\n{status_msg}", color)

        return FlextCore.Result[dict[str, str]].ok({
            "issues_count": str(exit_code),
            "issues": str(len(all_issues)),
        })


def main() -> int:
    """Main entry point."""
    auditor = FlextResultTypeAuditor()
    result = auditor.run()
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    sys.exit(main())

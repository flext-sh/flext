#!/usr/bin/env python3
"""Script para verificar inconsistências de FlextResult em todos os projetos flext."""

import os
import pathlib
import re
import subprocess


def find_flext_projects():
    """Encontra todos os projetos flext no workspace usando git submodules."""
    projects = []

    # Adiciona o projeto raiz (workspace principal)
    projects.append(".")

    try:
        result = subprocess.run(
            ["git", "submodule", "status"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                # Extrai o nome do projeto da linha do git submodule status
                parts = line.split()
                if len(parts) >= 2:
                    project_name = parts[1]
                    if pathlib.Path(project_name).is_dir():
                        projects.append(project_name)
        return sorted(projects)
    except subprocess.CalledProcessError:
        # Fallback para método antigo se git submodule falhar
        flext_dirs = [
            item
            for item in os.listdir(".")
            if pathlib.Path(item).is_dir() and item.startswith("flext-")
        ]
        projects.extend(flext_dirs)
        return sorted(projects)


def is_ignored_by_git(file_path, project_dir="."):
    """Verifica se um arquivo está ignorado pelo git usando git check-ignore."""
    try:
        # Usa git check-ignore para verificar se o arquivo é ignorado
        result = subprocess.run(
            ["git", "check-ignore", file_path],
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


def find_python_files(project_dir):
    """Encontra todos os arquivos .py no projeto respeitando .gitignore."""
    py_files = []
    for root, dirs, files in os.walk(project_dir):
        # Remove diretórios ignorados da lista para não percorrer
        dirs[:] = [
            d for d in dirs if not is_ignored_by_git(os.path.join(root, d), project_dir)
        ]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                if not is_ignored_by_git(full_path, project_dir):
                    py_files.append(full_path)
    return py_files


def check_flextresult_inconsistencies(file_path):
    """Verifica inconsistências de FlextResult em um arquivo."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
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
                for j in range(i + 1, min(i + 50, len(lines))):  # Até 50 linhas depois
                    if lines[j].strip().startswith("def "):  # Próximo método
                        break
                    if re.search(return_pattern, lines[j]):
                        issues.append(
                            {
                                "file": file_path,
                                "line": j + 1,
                                "method": method_name,
                                "declared_type": return_type,
                                "issue": f"Método declara FlextResult[{return_type}] mas retorna FlextResult.success()/error() sem valor",
                            }
                        )

    # Procura por outros padrões problemáticos
    for i, line in enumerate(lines):
        # Ignora comentários e strings que contêm padrões de exemplo
        if line.strip().startswith("#") or '"""' in line or "'" in line or '"' in line:
            continue

        if "FlextResult" in line:
            # Verifica assignments problemáticos
            if "FlextResult[None]" in line and "FlextResult[dict" in line:
                issues.append(
                    {
                        "file": file_path,
                        "line": i + 1,
                        "method": "unknown",
                        "declared_type": "mixed",
                        "issue": "Possível inconsistência entre FlextResult[None] e FlextResult[dict]",
                    }
                )

    return issues


def main():
    projects = find_flext_projects()
    all_issues = []

    for project in projects:
        project_name = "workspace-raiz" if project == "." else project
        py_files = find_python_files(project)
        project_issues = []

        for file_path in py_files:
            issues = check_flextresult_inconsistencies(file_path)
            project_issues.extend(issues)

        if project_issues:
            all_issues.extend(project_issues)

    if all_issues:
        current_project = None
        for issue in all_issues:
            project_name = issue["file"].split("/")[0]
            if project_name != current_project:
                current_project = project_name

    return len(all_issues)


if __name__ == "__main__":
    exit_code = main()
